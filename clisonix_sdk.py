"""
Kloud Cloud SDK – Python Client
Part of UltraWebThinking / Euroweb
"""

import asyncio
from typing import Any, Dict, Optional
import requests
from pathlib import Path


class KloudClient:
    """Synchronous Kloud API client"""

    def __init__(
        self,
        base_url: str = "https://kameleon.life",
        token: Optional[str] = None,
        timeout: int = 30,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.refresh_token: Optional[str] = None
        self.api_key: Optional[str] = None
        self.timeout = timeout
        self.session = requests.Session()

    def _headers(self, json_content: bool = True) -> Dict[str, str]:
        headers = {"User-Agent": "Kloud-Python-SDK/1.0"}
        if json_content:
            headers["Accept"] = "application/json"
            headers["Content-Type"] = "application/json"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def set_token(self, token: str) -> None:
        """Set or update the authentication token"""
        self.token = token

    def set_api_key(self, api_key: str) -> None:
        """Set or update the API key"""
        self.api_key = api_key

    # ==================== Authentication ====================

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """POST /auth/login – Authenticate with email & password"""
        payload = {"email": email, "password": password}
        r = self.session.post(
            f"{self.base_url}/auth/login",
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        data = r.json()

        # Store tokens
        self.token = data.get("token")
        self.refresh_token = data.get("refresh_token")
        if api_key := data.get("api_key"):
            self.api_key = api_key

        return data

    def refresh(self) -> Dict[str, Any]:
        """POST /auth/refresh – Refresh the JWT token"""
        if not self.refresh_token:
            raise RuntimeError("No refresh_token stored. Call login() first.")

        payload = {"refresh_token": self.refresh_token}
        r = self.session.post(
            f"{self.base_url}/auth/refresh",
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        data = r.json()

        # Update token
        self.token = data.get("token")
        return data

    def create_api_key(self, label: str) -> Dict[str, Any]:
        """POST /auth/api-key – Create a new API key"""
        if not self.token:
            raise RuntimeError("Authentication required. Call login() first.")

        payload = {"label": label}
        r = self.session.post(
            f"{self.base_url}/auth/api-key",
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        data = r.json()

        # Store the API key
        if api_key := data.get("api_key"):
            self.api_key = api_key

        return data

    # ==================== Health & Status ====================

    def health(self) -> Dict[str, Any]:
        """GET /health – System health check"""
        r = self.session.get(
            f"{self.base_url}/health", headers=self._headers(), timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    def status(self) -> Dict[str, Any]:
        """GET /status – Full system status"""
        r = self.session.get(
            f"{self.base_url}/status", headers=self._headers(), timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    def system_status(self) -> Dict[str, Any]:
        """GET /api/system-status – System status proxy"""
        r = self.session.get(
            f"{self.base_url}/api/system-status",
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def db_ping(self) -> Dict[str, Any]:
        """GET /db/ping – Database connectivity test"""
        r = self.session.get(
            f"{self.base_url}/db/ping", headers=self._headers(), timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    def redis_ping(self) -> Dict[str, Any]:
        """GET /redis/ping – Redis connectivity test"""
        r = self.session.get(
            f"{self.base_url}/redis/ping", headers=self._headers(), timeout=self.timeout
        )
        r.raise_for_status()
        return r.json()

    # ==================== Ask & Neural Symphony ====================

    def ask(
        self, question: str, context: Optional[str] = None, include_details: bool = True
    ) -> Dict[str, Any]:
        """POST /api/ask – Query the AI assistant"""
        payload = {
            "question": question,
            "context": context,
            "include_details": include_details,
        }
        r = self.session.post(
            f"{self.base_url}/api/ask",
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def neural_symphony(self, save_to: Optional[str] = None) -> bytes:
        """GET /neural-symphony – Generate EEG alpha wave audio"""
        headers = self._headers(json_content=False)
        headers["Accept"] = "audio/wav"
        r = self.session.get(
            f"{self.base_url}/neural-symphony", headers=headers, timeout=self.timeout
        )
        r.raise_for_status()

        if save_to:
            Path(save_to).write_bytes(r.content)

        return r.content

    # ==================== Uploads & Processing ====================

    def upload_eeg(self, file_path: str) -> Dict[str, Any]:
        """POST /api/uploads/eeg/process – Process EEG file"""
        with open(file_path, "rb") as f:
            files = {"file": f}
            r = self.session.post(
                f"{self.base_url}/api/uploads/eeg/process",
                files=files,
                headers={
                    k: v
                    for k, v in self._headers(json_content=False).items()
                    if k != "Content-Type"
                },
                timeout=self.timeout,
            )
        r.raise_for_status()
        return r.json()

    def upload_audio(self, file_path: str) -> Dict[str, Any]:
        """POST /api/uploads/audio/process – Process audio file"""
        with open(file_path, "rb") as f:
            files = {"file": f}
            r = self.session.post(
                f"{self.base_url}/api/uploads/audio/process",
                files=files,
                headers={
                    k: v
                    for k, v in self._headers(json_content=False).items()
                    if k != "Content-Type"
                },
                timeout=self.timeout,
            )
        r.raise_for_status()
        return r.json()

    # ==================== Brain Engine ====================

    def brain_youtube_insight(self, video_id: str) -> Dict[str, Any]:
        """GET /brain/youtube/insight – YouTube video analysis"""
        r = self.session.get(
            f"{self.base_url}/brain/youtube/insight",
            params={"video_id": video_id},
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def brain_energy_check(self, file_path: str) -> Dict[str, Any]:
        """POST /brain/energy/check – Daily energy analysis"""
        with open(file_path, "rb") as f:
            files = {"file": f}
            r = self.session.post(
                f"{self.base_url}/brain/energy/check",
                files=files,
                headers={
                    k: v
                    for k, v in self._headers(json_content=False).items()
                    if k != "Content-Type"
                },
                timeout=self.timeout,
            )
        r.raise_for_status()
        return r.json()

    def brain_harmony(self, file_path: str) -> Dict[str, Any]:
        """POST /brain/harmony – Harmonic structure analysis"""
        with open(file_path, "rb") as f:
            files = {"file": f}
            r = self.session.post(
                f"{self.base_url}/brain/harmony",
                files=files,
                headers={
                    k: v
                    for k, v in self._headers(json_content=False).items()
                    if k != "Content-Type"
                },
                timeout=self.timeout,
            )
        r.raise_for_status()
        return r.json()

    def brain_cortex_map(self) -> Dict[str, Any]:
        """GET /brain/cortex-map – Neural architecture map"""
        r = self.session.get(
            f"{self.base_url}/brain/cortex-map",
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def brain_temperature(self) -> Dict[str, Any]:
        """GET /brain/temperature – Module thermal stress"""
        r = self.session.get(
            f"{self.base_url}/brain/temperature",
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def brain_restart(self) -> Dict[str, Any]:
        """POST /brain/restart – Safely restart cognitive modules"""
        r = self.session.post(
            f"{self.base_url}/brain/restart",
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    # ==================== ALBA Data Collection ====================

    def alba_status(self) -> Dict[str, Any]:
        """GET /api/alba/status – ALBA module status"""
        r = self.session.get(
            f"{self.base_url}/api/alba/status",
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def alba_streams_start(
        self,
        stream_id: str,
        sampling_rate_hz: int = 256,
        channels: Optional[list] = None,
        description: Optional[str] = None,
        metadata: Optional[dict] = None,
    ) -> Dict[str, Any]:
        """POST /api/alba/streams/start – Start data stream"""
        payload = {
            "stream_id": stream_id,
            "sampling_rate_hz": sampling_rate_hz,
            "channels": channels or ["C3", "C4"],
            "description": description,
            "metadata": metadata or {},
        }
        r = self.session.post(
            f"{self.base_url}/api/alba/streams/start",
            json=payload,
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def alba_streams_stop(self, stream_id: str) -> Dict[str, Any]:
        """POST /api/alba/streams/{stream_id}/stop – Stop data stream"""
        r = self.session.post(
            f"{self.base_url}/api/alba/streams/{stream_id}/stop",
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def alba_streams_list(self) -> Dict[str, Any]:
        """GET /api/alba/streams – List active streams"""
        r = self.session.get(
            f"{self.base_url}/api/alba/streams",
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def alba_streams_data(self, stream_id: str, limit: int = 100) -> Dict[str, Any]:
        """GET /api/alba/streams/{stream_id}/data – Get stream data"""
        r = self.session.get(
            f"{self.base_url}/api/alba/streams/{stream_id}/data",
            params={"limit": limit},
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def alba_metrics(self) -> Dict[str, Any]:
        """GET /api/alba/metrics – Collection metrics"""
        r = self.session.get(
            f"{self.base_url}/api/alba/metrics",
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def alba_health(self) -> Dict[str, Any]:
        """GET /api/alba/health – ALBA health check"""
        r = self.session.get(
            f"{self.base_url}/api/alba/health",
            headers=self._headers(),
            timeout=self.timeout,
        )
        r.raise_for_status()
        return r.json()

    def close(self) -> None:
        """Close the session"""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# ==================== Example Usage ====================

if __name__ == "__main__":
    client = KloudClient(base_url="https://api.kloud.com")

    try:
        # 1. Login
        login_data = client.login("user@example.com", "password")
        print(f"✓ Logged in. Token: {login_data['token'][:20]}...")
        print(f"✓ Refresh token: {login_data['refresh_token'][:20]}...")

        # 2. Check health
        health = client.health()
        print(f"✓ Health: {health['status']}")

        # 3. Ask a question
        answer = client.ask("Çfarë është Kloud?", "neuro-audio platform")
        print(f"✓ Answer: {answer['answer'][:100]}...")

        # 4. Refresh token (optional)
        refreshed = client.refresh()
        print(f"✓ Token refreshed: {refreshed['token'][:20]}...")

        # 5. Create API key
        api_key_response = client.create_api_key("my-server-integration")
        print(f"✓ API Key created: {api_key_response['api_key'][:20]}...")

    except Exception as e:
        print(f"✗ Error: {e}")
    finally:
        client.close()
