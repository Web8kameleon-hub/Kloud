"""
Kloud Cloud - Monitoring Middleware  
Real-time performance monitoring and metrics collection
"""
import asyncio
import time
import logging
import json
from typing import Dict, Any, List
from collections import defaultdict, deque
import psutil
import threading

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    Industrial-grade monitoring middleware for Kloud
    Collects real-time metrics, performance data, and system health
    """
    
    def __init__(self, app, metrics_window: int = 300):  # 5 minutes default
        super().__init__(app)
        self.metrics_window = metrics_window
        
        # Metrics storage
        self.request_times = deque(maxlen=1000)  # Last 1000 requests
        self.request_counts = defaultdict(int)
        self.endpoint_metrics = defaultdict(lambda: {
            "count": 0,
            "total_time": 0,
            "avg_time": 0,
            "min_time": float('inf'),
            "max_time": 0,
            "error_count": 0
        })
        
        self.status_codes = defaultdict(int)
        self.error_log = deque(maxlen=100)  # Last 100 errors
        
        # System metrics
        self.system_metrics_history = deque(maxlen=60)  # Last 60 samples (5 min at 5s intervals)
        
        # Start background metric collection
        self._start_system_metrics_collection()
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Main monitoring middleware logic"""
        
        start_time = time.time()
        endpoint = f"{request.method} {request.url.path}"
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate metrics
            processing_time = time.time() - start_time
            
            # Update metrics
            await self._update_metrics(endpoint, processing_time, response.status_code, None)
            
            # Add monitoring headers
            response.headers["X-Processing-Time"] = f"{processing_time:.4f}"
            response.headers["X-Endpoint"] = endpoint
            
            return response
            
        except Exception as e:
            # Handle errors
            processing_time = time.time() - start_time
            error_info = {
                "endpoint": endpoint,
                "error": str(e),
                "processing_time": processing_time,
                "timestamp": time.time()
            }
            
            await self._update_metrics(endpoint, processing_time, 500, error_info)
            
            # Re-raise the exception
            raise e
    
    async def _update_metrics(self, endpoint: str, processing_time: float, status_code: int, error_info: Dict = None):
        """Update internal metrics"""
        
        current_time = time.time()
        
        # Update request times
        self.request_times.append({
            "timestamp": current_time,
            "processing_time": processing_time,
            "endpoint": endpoint,
            "status_code": status_code
        })
        
        # Update endpoint metrics
        endpoint_data = self.endpoint_metrics[endpoint]
        endpoint_data["count"] += 1
        endpoint_data["total_time"] += processing_time
        endpoint_data["avg_time"] = endpoint_data["total_time"] / endpoint_data["count"]
        endpoint_data["min_time"] = min(endpoint_data["min_time"], processing_time)
        endpoint_data["max_time"] = max(endpoint_data["max_time"], processing_time)
        
        if status_code >= 400:
            endpoint_data["error_count"] += 1
        
        # Update status code counts
        self.status_codes[status_code] += 1
        
        # Log errors
        if error_info:
            self.error_log.append(error_info)
            logger.error(f"Request error: {json.dumps(error_info)}")
        
        # Update request counts (cleanup old entries)
        self._cleanup_old_metrics(current_time)
    
    def _cleanup_old_metrics(self, current_time: float):
        """Remove old metrics outside the window"""
        
        cutoff_time = current_time - self.metrics_window
        
        # Clean request times
        while self.request_times and self.request_times[0]["timestamp"] < cutoff_time:
            self.request_times.popleft()
        
        # Clean system metrics history
        while self.system_metrics_history and self.system_metrics_history[0]["timestamp"] < cutoff_time:
            self.system_metrics_history.popleft()
    
    def _start_system_metrics_collection(self):
        """Start background thread for system metrics collection"""
        
        def collect_system_metrics():
            while True:
                try:
                    metrics = self._collect_system_metrics()
                    self.system_metrics_history.append(metrics)
                    
                    # Sleep for 5 seconds
                    time.sleep(5)
                    
                except Exception as e:
                    logger.error(f"Error collecting system metrics: {e}")
                    time.sleep(10)  # Wait longer on error
        
        # Start background thread
        metrics_thread = threading.Thread(target=collect_system_metrics, daemon=True)
        metrics_thread.start()
        logger.info("System metrics collection started")
    
    def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/' if psutil.POSIX else 'C:')
            
            # Network stats (if available)
            network = psutil.net_io_counters() if hasattr(psutil, 'net_io_counters') else None
            
            return {
                "timestamp": time.time(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                },
                "network": {
                    "bytes_sent": network.bytes_sent if network else 0,
                    "bytes_recv": network.bytes_recv if network else 0,
                    "packets_sent": network.packets_sent if network else 0,
                    "packets_recv": network.packets_recv if network else 0
                } if network else None
            }
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {
                "timestamp": time.time(),
                "error": str(e)
            }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        
        current_time = time.time()
        self._cleanup_old_metrics(current_time)
        
        # Calculate request rate
        recent_requests = [req for req in self.request_times if req["timestamp"] > current_time - 60]  # Last minute
        requests_per_minute = len(recent_requests)
        
        # Calculate average response time
        if self.request_times:
            avg_response_time = sum(req["processing_time"] for req in self.request_times) / len(self.request_times)
            min_response_time = min(req["processing_time"] for req in self.request_times)
            max_response_time = max(req["processing_time"] for req in self.request_times)
        else:
            avg_response_time = min_response_time = max_response_time = 0
        
        # Error rate
        total_requests = len(self.request_times)
        error_requests = sum(1 for req in self.request_times if req["status_code"] >= 400)
        error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "timestamp": current_time,
            "requests": {
                "total": total_requests,
                "per_minute": requests_per_minute,
                "error_count": error_requests,
                "error_rate_percent": round(error_rate, 2)
            },
            "response_times": {
                "average": round(avg_response_time, 4),
                "minimum": round(min_response_time, 4),
                "maximum": round(max_response_time, 4)
            },
            "status_codes": dict(self.status_codes),
            "top_endpoints": self._get_top_endpoints()
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics"""
        
        if not self.system_metrics_history:
            return {"error": "No system metrics available"}
        
        latest = self.system_metrics_history[-1]
        
        # Calculate averages over the window
        if len(self.system_metrics_history) > 1:
            cpu_avg = sum(m.get("cpu", {}).get("percent", 0) for m in self.system_metrics_history) / len(self.system_metrics_history)
            memory_avg = sum(m.get("memory", {}).get("percent", 0) for m in self.system_metrics_history) / len(self.system_metrics_history)
        else:
            cpu_avg = latest.get("cpu", {}).get("percent", 0)
            memory_avg = latest.get("memory", {}).get("percent", 0)
        
        return {
            "timestamp": latest["timestamp"],
            "current": latest,
            "averages": {
                "cpu_percent": round(cpu_avg, 2),
                "memory_percent": round(memory_avg, 2),
                "window_minutes": self.metrics_window / 60
            },
            "history_samples": len(self.system_metrics_history)
        }
    
    def _get_top_endpoints(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top endpoints by request count"""
        
        sorted_endpoints = sorted(
            self.endpoint_metrics.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )
        
        return [
            {
                "endpoint": endpoint,
                "count": data["count"],
                "avg_time": round(data["avg_time"], 4),
                "error_count": data["error_count"],
                "error_rate": round((data["error_count"] / data["count"]) * 100, 2) if data["count"] > 0 else 0
            }
            for endpoint, data in sorted_endpoints[:limit]
        ]
    
    def get_recent_errors(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent errors"""
        
        return list(self.error_log)[-limit:]
    
    def reset_metrics(self):
        """Reset all metrics (for testing or manual reset)"""
        
        self.request_times.clear()
        self.request_counts.clear()
        self.endpoint_metrics.clear()
        self.status_codes.clear()
        self.error_log.clear()
        self.system_metrics_history.clear()
        
        logger.info("All metrics have been reset")
    
    def get_health_score(self) -> Dict[str, Any]:
        """Calculate system health score based on metrics"""
        
        try:
            # Get latest system metrics
            if not self.system_metrics_history:
                return {"health_score": 50, "status": "unknown", "message": "No metrics available"}
            
            latest = self.system_metrics_history[-1]
            
            # Calculate health score (0-100)
            cpu_score = max(0, 100 - latest.get("cpu", {}).get("percent", 50))
            memory_score = max(0, 100 - latest.get("memory", {}).get("percent", 50))
            
            # Error rate impact
            perf_metrics = self.get_performance_metrics()
            error_rate = perf_metrics["requests"]["error_rate_percent"]
            error_score = max(0, 100 - error_rate * 2)  # Penalty for errors
            
            # Response time impact
            avg_response = perf_metrics["response_times"]["average"]
            response_score = max(0, 100 - (avg_response * 10))  # Penalty for slow responses
            
            # Weighted average
            health_score = (
                cpu_score * 0.3 +
                memory_score * 0.3 +
                error_score * 0.2 +
                response_score * 0.2
            )
            
            # Determine status
            if health_score >= 90:
                status = "excellent"
            elif health_score >= 75:
                status = "good"
            elif health_score >= 50:
                status = "fair"
            elif health_score >= 25:
                status = "poor"
            else:
                status = "critical"
            
            return {
                "health_score": round(health_score, 1),
                "status": status,
                "components": {
                    "cpu_score": round(cpu_score, 1),
                    "memory_score": round(memory_score, 1),
                    "error_score": round(error_score, 1),
                    "response_score": round(response_score, 1)
                },
                "timestamp": time.time(),
                "business": "Ledjan Ahmati - WEB8euroweb GmbH"
            }
            
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return {
                "health_score": 25,
                "status": "error",
                "message": f"Health calculation failed: {str(e)}",
                "timestamp": time.time()
            }



