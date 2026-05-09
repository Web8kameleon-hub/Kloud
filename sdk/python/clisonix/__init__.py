"""
Kloud Cloud Python SDK
==========================

Official Python SDK for Kloud Cloud API - Neural harmonic processing,
EEG analysis, and ASI Trinity integration.

Installation:
    pip install kloud

Quick Start:
    from kloud import Kloud
    
    client = Kloud(api_key="your-api-key")
    
    # Check system health
    health = client.core.health()
    print(f"Status: {health['status']}")
    
    # Get ASI status
    asi = client.asi.status()
    print(f"ASI Active: {asi['asi_active']}")
"""

import os
import time
import json
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from datetime import datetime
import urllib.request
import urllib.error
import urllib.parse

__version__ = "1.0.0"
__author__ = "Kloud Cloud"

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class KloudConfig:
    """SDK Configuration"""
    api_key: str
    base_url: str = "https://api.kloud.com"
    reporting_url: str = "https://reporting.kloud.com"
    excel_url: str = "https://excel.kloud.com"
    timeout: int = 30
    retries: int = 3
    debug: bool = False


# =============================================================================
# EXCEPTIONS
# =============================================================================

class KloudError(Exception):
    """Base exception for Kloud SDK"""
    def __init__(self, message: str, code: str = "UNKNOWN", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(KloudError):
    """Authentication failed"""
    def __init__(self, message: str = "Invalid API key"):
        super().__init__(message, "AUTHENTICATION_FAILED", 401)


class RateLimitError(KloudError):
    """Rate limit exceeded"""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", 429)


class ValidationError(KloudError):
    """Request validation failed"""
    def __init__(self, message: str):
        super().__init__(message, "VALIDATION_ERROR", 400)


class NotFoundError(KloudError):
    """Resource not found"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, "NOT_FOUND", 404)


# =============================================================================
# HTTP CLIENT
# =============================================================================

class HttpClient:
    """HTTP client with retry logic"""
    
    def __init__(self, config: KloudConfig):
        self.config = config
    
    def _request(
        self,
        method: str,
        url: str,
        body: Optional[Dict] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        
        default_headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.config.api_key,
            "User-Agent": f"kloud-python-sdk/{__version__}"
        }
        
        if headers:
            default_headers.update(headers)
        
        data = None
        if body:
            data = json.dumps(body).encode('utf-8')
        
        last_error = None
        
        for attempt in range(self.config.retries):
            try:
                req = urllib.request.Request(
                    url,
                    data=data,
                    headers=default_headers,
                    method=method
                )
                
                with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                    response_data = response.read().decode('utf-8')
                    return json.loads(response_data) if response_data else {}
                    
            except urllib.error.HTTPError as e:
                status_code = e.code
                try:
                    error_body = json.loads(e.read().decode('utf-8'))
                    error_msg = error_body.get('error', {}).get('message', str(e))
                    error_code = error_body.get('error', {}).get('code', 'UNKNOWN')
                except:
                    error_msg = str(e)
                    error_code = 'UNKNOWN'
                
                if status_code == 401:
                    raise AuthenticationError(error_msg)
                elif status_code == 429:
                    raise RateLimitError(error_msg)
                elif status_code == 404:
                    raise NotFoundError(error_msg)
                elif status_code == 400:
                    raise ValidationError(error_msg)
                else:
                    last_error = KloudError(error_msg, error_code, status_code)
                    
            except urllib.error.URLError as e:
                last_error = KloudError(f"Connection error: {e.reason}", "CONNECTION_ERROR", 0)
            except Exception as e:
                last_error = KloudError(str(e), "UNKNOWN", 0)
            
            # Exponential backoff
            if attempt < self.config.retries - 1:
                time.sleep(2 ** attempt)
        
        if last_error:
            raise last_error
        raise KloudError("Request failed after retries")
    
    def get(self, path: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        url = (base_url or self.config.base_url) + path
        return self._request("GET", url)
    
    def post(self, path: str, body: Optional[Dict] = None, base_url: Optional[str] = None) -> Dict[str, Any]:
        url = (base_url or self.config.base_url) + path
        return self._request("POST", url, body)
    
    def put(self, path: str, body: Optional[Dict] = None, base_url: Optional[str] = None) -> Dict[str, Any]:
        url = (base_url or self.config.base_url) + path
        return self._request("PUT", url, body)
    
    def delete(self, path: str, base_url: Optional[str] = None) -> Dict[str, Any]:
        url = (base_url or self.config.base_url) + path
        return self._request("DELETE", url)


# =============================================================================
# API MODULES
# =============================================================================

class CoreAPI:
    """Core API - System health and status endpoints"""
    
    def __init__(self, client: HttpClient):
        self._client = client
    
    def health(self) -> Dict[str, Any]:
        """Get system health status
        
        Returns:
            dict: Health response with status, version, system metrics
        """
        return self._client.get("/health")
    
    def status(self) -> Dict[str, Any]:
        """Get detailed system status
        
        Returns:
            dict: Status response with uptime, memory, dependencies
        """
        return self._client.get("/status")
    
    def ping(self) -> Dict[str, Any]:
        """Simple ping check
        
        Returns:
            dict: {"pong": True, "timestamp": "..."}
        """
        return self._client.get("/ping")


class BrainAPI:
    """Brain API - Neural harmonic processing and analysis"""
    
    def __init__(self, client: HttpClient):
        self._client = client
    
    def analyze_harmonics(
        self,
        frequencies: List[float],
        amplitudes: List[float]
    ) -> Dict[str, Any]:
        """Analyze harmonic patterns
        
        Args:
            frequencies: List of frequencies in Hz
            amplitudes: List of corresponding amplitudes
            
        Returns:
            dict: Harmonic analysis results
        """
        return self._client.post("/brain/harmonics/analyze", {
            "frequencies": frequencies,
            "amplitudes": amplitudes
        })
    
    def get_sync(self) -> Dict[str, Any]:
        """Get brain synchronization metrics
        
        Returns:
            dict: Sync levels for all frequency bands
        """
        return self._client.get("/brain/sync")
    
    def analyze_cortex(
        self,
        pattern_data: List[float],
        analysis_type: str = "quick"
    ) -> Dict[str, Any]:
        """Process cortex patterns
        
        Args:
            pattern_data: Raw pattern data
            analysis_type: "quick", "deep", or "realtime"
            
        Returns:
            dict: Cortex analysis results
        """
        return self._client.post("/brain/cortex/analyze", {
            "pattern_data": pattern_data,
            "analysis_type": analysis_type
        })
    
    def ask(self, question: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Ask the brain AI assistant
        
        Args:
            question: Question to ask
            context: Optional context to help answer
            
        Returns:
            dict: AI response with answer and processing info
        """
        payload = {"question": question}
        if context:
            payload["context"] = context
        return self._client.post("/brain/ask", payload)


class EEGAPI:
    """EEG API - EEG data collection and processing"""
    
    def __init__(self, client: HttpClient):
        self._client = client
    
    def start_session(
        self,
        channels: int = 8,
        sample_rate: int = 256
    ) -> Dict[str, Any]:
        """Start a new EEG recording session
        
        Args:
            channels: Number of EEG channels
            sample_rate: Samples per second
            
        Returns:
            dict: Session info with session_id
        """
        return self._client.post("/eeg/sessions/start", {
            "channels": channels,
            "sample_rate": sample_rate
        })
    
    def stop_session(self, session_id: str) -> Dict[str, Any]:
        """Stop an EEG session
        
        Args:
            session_id: Session ID to stop
            
        Returns:
            dict: Final session info
        """
        return self._client.post(f"/eeg/sessions/{session_id}/stop")
    
    def get_session_data(self, session_id: str) -> List[Dict[str, Any]]:
        """Get session data
        
        Args:
            session_id: Session ID
            
        Returns:
            list: EEG data points
        """
        return self._client.get(f"/eeg/sessions/{session_id}/data")
    
    def analyze_frequencies(self, session_id: str) -> Dict[str, Any]:
        """Analyze frequency bands
        
        Args:
            session_id: Session ID
            
        Returns:
            dict: Frequency band analysis
        """
        return self._client.get(f"/eeg/sessions/{session_id}/frequencies")
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions
        
        Returns:
            list: Active EEG sessions
        """
        return self._client.get("/eeg/sessions")


class ASIAPI:
    """ASI API - ASI Trinity system interface (ALBA, ALBI, JONA)"""
    
    def __init__(self, client: HttpClient):
        self._client = client
    
    def status(self) -> Dict[str, Any]:
        """Get overall ASI status
        
        Returns:
            dict: ASI status with component info
        """
        return self._client.get("/asi/status")
    
    def health(self) -> Dict[str, Any]:
        """Get ASI health
        
        Returns:
            dict: Health status per component
        """
        return self._client.get("/asi/health")
    
    def alba_metrics(self) -> Dict[str, Any]:
        """Get ALBA metrics
        
        Returns:
            dict: Network latency, streams, throughput
        """
        return self._client.get("/asi/alba/metrics")
    
    def albi_metrics(self) -> Dict[str, Any]:
        """Get ALBI metrics
        
        Returns:
            dict: Neural load, patterns, goroutines
        """
        return self._client.get("/asi/albi/metrics")
    
    def jona_metrics(self) -> Dict[str, Any]:
        """Get JONA metrics
        
        Returns:
            dict: Coordination score, tasks, errors
        """
        return self._client.get("/asi/jona/metrics")
    
    def sync(self) -> Dict[str, Any]:
        """Trigger manual sync
        
        Returns:
            dict: Sync result with timestamp
        """
        return self._client.post("/asi/sync")


class BillingAPI:
    """Billing API - Payment and subscription management"""
    
    def __init__(self, client: HttpClient):
        self._client = client
    
    def get_plans(self) -> List[Dict[str, Any]]:
        """Get available plans
        
        Returns:
            list: Available billing plans
        """
        return self._client.get("/billing/plans")
    
    def get_subscription(self) -> Dict[str, Any]:
        """Get current subscription
        
        Returns:
            dict: Current subscription details
        """
        return self._client.get("/billing/subscription")
    
    def create_checkout(self, plan_id: str) -> Dict[str, Any]:
        """Create checkout session
        
        Args:
            plan_id: Plan ID to subscribe to
            
        Returns:
            dict: Checkout URL and session ID
        """
        return self._client.post("/billing/checkout", {"plan_id": plan_id})
    
    def get_usage(self) -> Dict[str, Any]:
        """Get usage statistics
        
        Returns:
            dict: API usage stats
        """
        return self._client.get("/billing/usage")
    
    def cancel(self) -> Dict[str, Any]:
        """Cancel subscription
        
        Returns:
            dict: Cancellation confirmation
        """
        return self._client.post("/billing/subscription/cancel")


class ReportingAPI:
    """Reporting API - Docker and system metrics (Port 8001)"""
    
    def __init__(self, client: HttpClient, config: KloudConfig):
        self._client = client
        self._base_url = config.reporting_url
    
    def docker_containers(self) -> Dict[str, Any]:
        """Get Docker containers
        
        Returns:
            dict: Container list with total and healthy count
        """
        return self._client.get("/api/reporting/docker-containers", self._base_url)
    
    def docker_stats(self) -> Dict[str, Any]:
        """Get Docker stats
        
        Returns:
            dict: Container resource usage stats
        """
        return self._client.get("/api/reporting/docker-stats", self._base_url)
    
    def system_metrics(self) -> Dict[str, Any]:
        """Get system metrics
        
        Returns:
            dict: CPU, memory, disk usage
        """
        return self._client.get("/api/reporting/system-metrics", self._base_url)


class ExcelAPI:
    """Excel API - Excel and reporting operations (Port 8002)"""
    
    def __init__(self, client: HttpClient, config: KloudConfig):
        self._client = client
        self._base_url = config.excel_url
    
    def generate_report(
        self,
        report_type: str,
        date_range: Optional[Dict[str, str]] = None,
        format: str = "xlsx"
    ) -> Dict[str, Any]:
        """Generate Excel report
        
        Args:
            report_type: Type of report to generate
            date_range: Optional date range {"start": "...", "end": "..."}
            format: "xlsx" or "csv"
            
        Returns:
            dict: Download URL and expiration
        """
        payload = {
            "report_type": report_type,
            "format": format
        }
        if date_range:
            payload["date_range"] = date_range
        return self._client.post("/api/excel/generate", payload, self._base_url)
    
    def get_templates(self) -> List[Dict[str, Any]]:
        """Get report templates
        
        Returns:
            list: Available report templates
        """
        return self._client.get("/api/excel/templates", self._base_url)
    
    def regenerate(self) -> Dict[str, Any]:
        """Regenerate Excel data
        
        Returns:
            dict: Regeneration result
        """
        return self._client.post("/api/excel/regenerate", base_url=self._base_url)


# =============================================================================
# MAIN SDK CLASS
# =============================================================================

class Kloud:
    """
    Kloud Cloud SDK
    
    Official Python SDK for Kloud Cloud API - Neural harmonic processing,
    EEG analysis, and ASI Trinity integration.
    
    Example:
        >>> from kloud import Kloud
        >>> 
        >>> client = Kloud(api_key="your-api-key")
        >>> 
        >>> # Check system health
        >>> health = client.core.health()
        >>> print(f"Status: {health['status']}")
        >>> 
        >>> # Analyze brain harmonics
        >>> analysis = client.brain.analyze_harmonics(
        ...     frequencies=[8, 10, 12, 14],
        ...     amplitudes=[0.5, 0.8, 0.6, 0.4]
        ... )
        >>> 
        >>> # Get ASI Trinity status
        >>> asi = client.asi.status()
        >>> print(f"ASI Active: {asi['asi_active']}")
    
    Attributes:
        core: Core API - System health and status
        brain: Brain API - Neural harmonic processing
        eeg: EEG API - Data collection and processing
        asi: ASI API - ASI Trinity interface
        billing: Billing API - Subscription management
        reporting: Reporting API - Docker and metrics (Port 8001)
        excel: Excel API - Report generation (Port 8002)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.kloud.com",
        reporting_url: str = "https://reporting.kloud.com",
        excel_url: str = "https://excel.kloud.com",
        timeout: int = 30,
        retries: int = 3,
        debug: bool = False
    ):
        """
        Initialize Kloud SDK
        
        Args:
            api_key: API key (or set KLOUD_API_KEY environment variable)
            base_url: Base URL for main API
            reporting_url: URL for Reporting microservice
            excel_url: URL for Excel microservice
            timeout: Request timeout in seconds
            retries: Number of retry attempts
            debug: Enable debug logging
        """
        # Get API key from environment if not provided
        api_key = api_key or os.environ.get("KLOUD_API_KEY")
        if not api_key:
            raise ValueError(
                "API key required. Pass api_key parameter or set KLOUD_API_KEY environment variable."
            )
        
        self._config = KloudConfig(
            api_key=api_key,
            base_url=base_url,
            reporting_url=reporting_url,
            excel_url=excel_url,
            timeout=timeout,
            retries=retries,
            debug=debug
        )
        
        self._client = HttpClient(self._config)
        
        # Initialize API modules
        self.core = CoreAPI(self._client)
        self.brain = BrainAPI(self._client)
        self.eeg = EEGAPI(self._client)
        self.asi = ASIAPI(self._client)
        self.billing = BillingAPI(self._client)
        self.reporting = ReportingAPI(self._client, self._config)
        self.excel = ExcelAPI(self._client, self._config)
    
    def is_healthy(self) -> bool:
        """Quick health check
        
        Returns:
            bool: True if system is healthy
        """
        try:
            health = self.core.health()
            return health.get("status") == "healthy"
        except:
            return False
    
    @property
    def version(self) -> str:
        """SDK version"""
        return __version__


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_client(
    api_key: Optional[str] = None,
    **kwargs
) -> Kloud:
    """
    Create a Kloud client
    
    Convenience function to create a client instance.
    
    Args:
        api_key: API key
        **kwargs: Additional config options
        
    Returns:
        Kloud: Client instance
    """
    return Kloud(api_key=api_key, **kwargs)


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI interface for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Kloud Cloud SDK CLI")
    parser.add_argument("--api-key", help="API key")
    parser.add_argument("--health", action="store_true", help="Check health")
    parser.add_argument("--status", action="store_true", help="Get status")
    parser.add_argument("--asi", action="store_true", help="Get ASI status")
    parser.add_argument("--containers", action="store_true", help="Get Docker containers")
    
    args = parser.parse_args()
    
    try:
        client = Kloud(api_key=args.api_key)
        
        if args.health:
            result = client.core.health()
            print(json.dumps(result, indent=2))
        elif args.status:
            result = client.core.status()
            print(json.dumps(result, indent=2))
        elif args.asi:
            result = client.asi.status()
            print(json.dumps(result, indent=2))
        elif args.containers:
            result = client.reporting.docker_containers()
            print(json.dumps(result, indent=2))
        else:
            print(f"Kloud SDK v{__version__}")
            print("Use --help for available commands")
            
    except KloudError as e:
        print(f"Error: {e.message} (code: {e.code})")
        exit(1)


if __name__ == "__main__":
    main()

