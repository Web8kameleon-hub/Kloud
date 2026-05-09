"""
Kloud Cloud - Security Middleware
Industrial-grade security controls and monitoring
"""
import asyncio
import time
import logging
import uuid
from typing import Dict, Any, List, Set
import hashlib
import json

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Industrial-grade security middleware for Kloud
    Implements IP filtering, request validation, and threat detection
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.blocked_ips: Set[str] = set()
        self.suspicious_ips: Dict[str, Dict[str, Any]] = {}
        self.max_request_size = 100 * 1024 * 1024  # 100MB
        self.rate_limit_window = 60  # seconds
        self.max_requests_per_window = 1000
        
        # Security headers to add to all responses
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", 
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "X-Powered-By": "Kloud-Cloud"
        }
        
        # Dangerous patterns to detect
        self.dangerous_patterns = [
            # SQL Injection patterns
            "union select", "drop table", "delete from", "insert into",
            "update set", "exec(", "execute(",
            
            # XSS patterns
            "<script", "javascript:", "onload=", "onerror=", "onclick=",
            
            # Path traversal
            "../", "..\\", "%2e%2e",
            
            # Command injection
            "; rm ", "; del ", "| rm ", "| del ", "&& rm", "&& del"
        ]
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Main security middleware logic"""
        
        # Get client IP
        client_ip = await self._get_client_ip(request)
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            logger.warning(f"Blocked IP attempted access: {client_ip}")
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Access denied",
                    "message": "Your IP address has been blocked",
                    "timestamp": time.time()
                }
            )
        
        # Rate limiting check
        rate_limit_result = await self._check_rate_limit(client_ip)
        if not rate_limit_result["allowed"]:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": rate_limit_result["message"],
                    "retry_after": rate_limit_result["retry_after"],
                    "timestamp": time.time()
                }
            )
        
        # Request size validation
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            logger.warning(f"Request too large from {client_ip}: {content_length} bytes")
            return JSONResponse(
                status_code=413,
                content={
                    "error": "Request too large",
                    "message": f"Maximum request size is {self.max_request_size / 1024 / 1024:.1f}MB",
                    "timestamp": time.time()
                }
            )
        
        # Security validation
        security_check = await self._validate_request_security(request)
        if not security_check["safe"]:
            await self._handle_security_threat(client_ip, security_check["threat_type"])
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Security validation failed",
                    "message": "Request contains potentially malicious content",
                    "threat_id": security_check["threat_id"],
                    "timestamp": time.time()
                }
            )
        
        # Add request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Process request
        start_time = time.time()
        
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Request processing error for {client_ip}: {e}")
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": request_id,
                    "timestamp": time.time()
                }
            )
        
        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value
        
        # Add request tracking headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{(time.time() - start_time) * 1000:.2f}ms"
        response.headers["X-Client-IP"] = client_ip
        
        # Log request for monitoring
        await self._log_request(request, response, client_ip, time.time() - start_time)
        
        return response
    
    async def _get_client_ip(self, request: Request) -> str:
        """Extract real client IP considering proxies"""
        
        # Check for forwarded headers (from reverse proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP (original client)
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct connection IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    async def _check_rate_limit(self, client_ip: str) -> Dict[str, Any]:
        """Check if client IP is within rate limits"""
        
        current_time = time.time()
        window_start = current_time - self.rate_limit_window
        
        # Clean up old entries
        if client_ip in self.suspicious_ips:
            ip_data = self.suspicious_ips[client_ip]
            ip_data["requests"] = [req_time for req_time in ip_data.get("requests", []) if req_time > window_start]
        else:
            self.suspicious_ips[client_ip] = {"requests": [], "threats": 0}
        
        # Count requests in current window
        request_count = len(self.suspicious_ips[client_ip]["requests"])
        
        if request_count >= self.max_requests_per_window:
            logger.warning(f"Rate limit exceeded for IP: {client_ip} ({request_count} requests)")
            return {
                "allowed": False,
                "message": f"Rate limit exceeded: {self.max_requests_per_window} requests per {self.rate_limit_window} seconds",
                "retry_after": self.rate_limit_window
            }
        
        # Record this request
        self.suspicious_ips[client_ip]["requests"].append(current_time)
        
        return {
            "allowed": True,
            "remaining": self.max_requests_per_window - request_count - 1
        }
    
    async def _validate_request_security(self, request: Request) -> Dict[str, Any]:
        """Validate request for security threats"""
        
        threat_id = str(uuid.uuid4())
        
        # Check URL path
        url_path = str(request.url.path).lower()
        for pattern in self.dangerous_patterns:
            if pattern in url_path:
                return {
                    "safe": False,
                    "threat_type": "malicious_url_pattern",
                    "threat_id": threat_id,
                    "pattern": pattern
                }
        
        # Check query parameters
        query_string = str(request.url.query).lower()
        for pattern in self.dangerous_patterns:
            if pattern in query_string:
                return {
                    "safe": False,
                    "threat_type": "malicious_query_parameter", 
                    "threat_id": threat_id,
                    "pattern": pattern
                }
        
        # Check headers
        for header_name, header_value in request.headers.items():
            header_value_lower = header_value.lower()
            for pattern in self.dangerous_patterns:
                if pattern in header_value_lower:
                    return {
                        "safe": False,
                        "threat_type": "malicious_header",
                        "threat_id": threat_id,
                        "header": header_name,
                        "pattern": pattern
                    }
        
        # Additional checks for specific endpoints
        if request.method in ["POST", "PUT", "PATCH"]:
            # Check Content-Type for suspicious values
            content_type = request.headers.get("content-type", "").lower()
            if "text/html" in content_type or "application/x-" in content_type:
                return {
                    "safe": False,
                    "threat_type": "suspicious_content_type",
                    "threat_id": threat_id,
                    "content_type": content_type
                }
        
        return {
            "safe": True,
            "threat_id": threat_id
        }
    
    async def _handle_security_threat(self, client_ip: str, threat_type: str):
        """Handle detected security threat"""
        
        logger.warning(f"Security threat detected from {client_ip}: {threat_type}")
        
        # Increment threat counter for this IP
        if client_ip in self.suspicious_ips:
            self.suspicious_ips[client_ip]["threats"] = self.suspicious_ips[client_ip].get("threats", 0) + 1
        else:
            self.suspicious_ips[client_ip] = {"requests": [], "threats": 1}
        
        # Block IP if too many threats
        threat_count = self.suspicious_ips[client_ip]["threats"]
        if threat_count >= 5:  # Block after 5 security violations
            self.blocked_ips.add(client_ip)
            logger.error(f"IP blocked due to repeated security threats: {client_ip}")
        
        # Log threat details for analysis
        threat_data = {
            "ip": client_ip,
            "threat_type": threat_type,
            "threat_count": threat_count,
            "timestamp": time.time()
        }
        
        # In production, send to security monitoring system
        logger.error(f"Security threat logged: {json.dumps(threat_data)}")
    
    async def _log_request(self, request: Request, response: Response, client_ip: str, processing_time: float):
        """Log request for monitoring and analysis"""
        
        log_data = {
            "timestamp": time.time(),
            "client_ip": client_ip,
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "processing_time": processing_time,
            "user_agent": request.headers.get("user-agent", ""),
            "request_id": getattr(request.state, "request_id", "unknown")
        }
        
        # Log based on status code
        if response.status_code >= 500:
            logger.error(f"Server error: {json.dumps(log_data)}")
        elif response.status_code >= 400:
            logger.warning(f"Client error: {json.dumps(log_data)}")
        else:
            logger.info(f"Request completed: {request.method} {request.url.path} - {response.status_code} - {processing_time:.3f}s")
    
    def unblock_ip(self, ip: str):
        """Manually unblock an IP address"""
        if ip in self.blocked_ips:
            self.blocked_ips.remove(ip)
            logger.info(f"IP unblocked: {ip}")
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Get current security statistics"""
        return {
            "blocked_ips": len(self.blocked_ips),
            "monitored_ips": len(self.suspicious_ips),
            "total_threats": sum(data.get("threats", 0) for data in self.suspicious_ips.values()),
            "timestamp": time.time()
        }



