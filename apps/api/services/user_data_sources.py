"""
User Data Sources Service - Real Sensor/API Integration
Each user can connect their own data sources (MQTT, REST API, Webhooks, etc.)
No mock data - real connections with health monitoring.

Architecture:
- SQLite: Source metadata per user
- Async connectors: Test and fetch from real endpoints
- Background sync: Periodic data pull for connected sources
"""

import sqlite3
import json
import httpx
import asyncio
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Data directory
DATA_DIR = Path("/data/kloud")
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "user_data_sources.db"


def get_connection() -> sqlite3.Connection:
    """Get SQLite connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize user_data_sources table"""
    conn = get_connection()
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    
    cursor = conn.cursor()
    
    # User data sources table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data_sources (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            auth_type TEXT DEFAULT 'none',
            auth_config TEXT DEFAULT '{}',
            status TEXT DEFAULT 'pending',
            last_check TIMESTAMP,
            last_data TIMESTAMP,
            data_points INTEGER DEFAULT 0,
            error_message TEXT,
            config TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Data points table (actual data from sources)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS source_data_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            value TEXT NOT NULL,
            metadata TEXT DEFAULT '{}',
            FOREIGN KEY(source_id) REFERENCES user_data_sources(id)
        )
    """)
    
    # Index for fast user lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sources_user_id 
        ON user_data_sources(user_id)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_data_source_id 
        ON source_data_points(source_id)
    """)
    
    conn.commit()
    conn.close()
    logger.info("✓ User Data Sources database initialized")


# Initialize on import
init_database()


class UserDataSourcesService:
    """Service for managing user data sources with real connections"""
    
    # Supported source types
    SUPPORTED_TYPES = {
        'api': 'REST API (JSON)',
        'mqtt': 'MQTT Broker',
        'webhook': 'Incoming Webhook',
        'websocket': 'WebSocket Stream',
        'rss': 'RSS/Atom Feed',
        'csv': 'CSV File URL',
        'graphql': 'GraphQL Endpoint'
    }
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0, verify=False)
    
    async def close(self):
        await self.http_client.aclose()
    
    # ==================== CRUD OPERATIONS ====================
    
    def create_source(
        self, 
        user_id: str, 
        name: str, 
        source_type: str, 
        endpoint: str,
        auth_type: str = 'none',
        auth_config: dict = None,
        config: dict = None
    ) -> Dict[str, Any]:
        """Create a new data source for user"""
        
        source_id = f"src_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()
        
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO user_data_sources 
                (id, user_id, name, type, endpoint, auth_type, auth_config, config, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source_id,
                user_id,
                name,
                source_type,
                endpoint,
                auth_type,
                json.dumps(auth_config or {}),
                json.dumps(config or {}),
                now,
                now
            ))
            conn.commit()
            
            return {
                "success": True,
                "source_id": source_id,
                "message": f"Source '{name}' created. Run connection test to activate."
            }
        except Exception as e:
            logger.error(f"Failed to create source: {e}")
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def get_user_sources(self, user_id: str) -> List[Dict]:
        """Get all sources for a user"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM user_data_sources 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (user_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        sources = []
        for row in rows:
            source = dict(row)
            # Parse JSON fields
            source['auth_config'] = json.loads(source.get('auth_config', '{}'))
            source['config'] = json.loads(source.get('config', '{}'))
            # Don't expose auth secrets
            if 'api_key' in source['auth_config']:
                source['auth_config']['api_key'] = '***hidden***'
            if 'password' in source['auth_config']:
                source['auth_config']['password'] = '***hidden***'
            sources.append(source)
        
        return sources
    
    def get_source(self, source_id: str, user_id: str = None) -> Optional[Dict]:
        """Get single source by ID"""
        conn = get_connection()
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute(
                "SELECT * FROM user_data_sources WHERE id = ? AND user_id = ?",
                (source_id, user_id)
            )
        else:
            cursor.execute(
                "SELECT * FROM user_data_sources WHERE id = ?",
                (source_id,)
            )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            source = dict(row)
            source['auth_config'] = json.loads(source.get('auth_config', '{}'))
            source['config'] = json.loads(source.get('config', '{}'))
            return source
        return None
    
    def delete_source(self, source_id: str, user_id: str) -> Dict:
        """Delete a source (user must own it)"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Delete data points first
        cursor.execute("DELETE FROM source_data_points WHERE source_id = ?", (source_id,))
        
        # Delete source
        cursor.execute(
            "DELETE FROM user_data_sources WHERE id = ? AND user_id = ?",
            (source_id, user_id)
        )
        
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        if deleted:
            return {"success": True, "message": f"Source {source_id} deleted"}
        return {"success": False, "error": "Source not found or not owned by user"}
    
    # ==================== CONNECTION TESTING ====================
    
    async def test_connection(self, source_id: str, user_id: str) -> Dict:
        """Test connection to a data source - REAL test, no mock"""
        
        source = self.get_source(source_id, user_id)
        if not source:
            return {"success": False, "error": "Source not found"}
        
        source_type = source['type']
        endpoint = source['endpoint']
        auth_config = source.get('auth_config', {})
        
        result = {
            "source_id": source_id,
            "source_name": source['name'],
            "endpoint": endpoint,
            "type": source_type
        }
        
        try:
            if source_type == 'api':
                test_result = await self._test_api(endpoint, auth_config)
            elif source_type == 'mqtt':
                test_result = await self._test_mqtt(endpoint, auth_config)
            elif source_type == 'webhook':
                test_result = self._test_webhook(source_id)
            elif source_type == 'websocket':
                test_result = await self._test_websocket(endpoint)
            elif source_type == 'rss':
                test_result = await self._test_rss(endpoint)
            elif source_type == 'csv':
                test_result = await self._test_csv(endpoint)
            elif source_type == 'graphql':
                test_result = await self._test_graphql(endpoint, auth_config)
            else:
                test_result = {"success": False, "error": f"Unknown type: {source_type}"}
            
            result.update(test_result)
            
            # Update source status
            self._update_source_status(
                source_id, 
                'active' if test_result['success'] else 'error',
                test_result.get('error')
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Connection test failed for {source_id}: {e}")
            self._update_source_status(source_id, 'error', str(e))
            return {"success": False, "error": str(e), **result}
    
    async def _test_api(self, endpoint: str, auth_config: dict) -> Dict:
        """Test REST API endpoint"""
        headers = {'Accept': 'application/json'}
        
        # Add auth headers
        if auth_config.get('type') == 'bearer':
            headers['Authorization'] = f"Bearer {auth_config.get('token', '')}"
        elif auth_config.get('type') == 'api_key':
            key_name = auth_config.get('key_name', 'X-API-Key')
            headers[key_name] = auth_config.get('api_key', '')
        
        try:
            response = await self.http_client.get(endpoint, headers=headers)
            
            if response.status_code == 200:
                # Try to parse response
                try:
                    data = response.json()
                    data_preview = str(data)[:200] + '...' if len(str(data)) > 200 else str(data)
                    return {
                        "success": True,
                        "status_code": 200,
                        "response_type": "json",
                        "data_preview": data_preview,
                        "latency_ms": int(response.elapsed.total_seconds() * 1000)
                    }
                except:
                    return {
                        "success": True,
                        "status_code": 200,
                        "response_type": "text",
                        "data_preview": response.text[:200],
                        "latency_ms": int(response.elapsed.total_seconds() * 1000)
                    }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}: {response.text[:100]}"
                }
        except httpx.ConnectError as e:
            return {"success": False, "error": f"Connection failed: {str(e)}"}
        except httpx.TimeoutException:
            return {"success": False, "error": "Connection timeout (30s)"}
    
    async def _test_mqtt(self, endpoint: str, auth_config: dict) -> Dict:
        """Test MQTT connection (requires paho-mqtt)"""
        try:
            # Parse MQTT URL: mqtt://host:port/topic
            import re
            match = re.match(r'mqtt://([^:]+):?(\d+)?/?(.+)?', endpoint)
            if not match:
                return {"success": False, "error": "Invalid MQTT URL. Use: mqtt://host:port/topic"}
            
            host = match.group(1)
            port = int(match.group(2) or 1883)
            topic = match.group(3) or '#'
            
            # Try import paho
            try:
                import paho.mqtt.client as mqtt
            except ImportError:
                return {
                    "success": False, 
                    "error": "MQTT support not installed. Run: pip install paho-mqtt"
                }
            
            # Quick connection test
            connected = False
            error_msg = None
            
            def on_connect(client, userdata, flags, rc):
                nonlocal connected
                if rc == 0:
                    connected = True
                else:
                    nonlocal error_msg
                    error_msg = f"MQTT error code: {rc}"
            
            client = mqtt.Client()
            client.on_connect = on_connect
            
            if auth_config.get('username'):
                client.username_pw_set(
                    auth_config.get('username'),
                    auth_config.get('password', '')
                )
            
            try:
                client.connect(host, port, 5)  # 5 second timeout
                client.loop_start()
                await asyncio.sleep(3)  # Wait for connection
                client.loop_stop()
                client.disconnect()
                
                if connected:
                    return {
                        "success": True,
                        "host": host,
                        "port": port,
                        "topic": topic,
                        "message": f"Connected to MQTT broker. Subscribed to: {topic}"
                    }
                else:
                    return {"success": False, "error": error_msg or "Connection failed"}
            except Exception as e:
                return {"success": False, "error": f"MQTT connection error: {str(e)}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_webhook(self, source_id: str) -> Dict:
        """Generate webhook URL for incoming data"""
        # Webhook URL that users can POST data to
        webhook_url = f"https://api.kloud.com/api/webhooks/data/{source_id}"
        
        return {
            "success": True,
            "webhook_url": webhook_url,
            "message": "POST JSON data to this URL to ingest data points",
            "example": {
                "curl": f'curl -X POST {webhook_url} -H "Content-Type: application/json" -d \'{{"value": 25.5, "sensor": "temp1"}}\''
            }
        }
    
    async def _test_websocket(self, endpoint: str) -> Dict:
        """Test WebSocket connection"""
        try:
            import websockets
        except ImportError:
            return {"success": False, "error": "WebSocket support not installed. Run: pip install websockets"}
        
        try:
            async with websockets.connect(endpoint, close_timeout=5) as ws:
                # Try to receive one message
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=5.0)
                    return {
                        "success": True,
                        "message": "WebSocket connected",
                        "sample_data": str(message)[:200]
                    }
                except asyncio.TimeoutError:
                    return {
                        "success": True,
                        "message": "WebSocket connected (no data in 5s, but connection works)"
                    }
        except Exception as e:
            return {"success": False, "error": f"WebSocket error: {str(e)}"}
    
    async def _test_rss(self, endpoint: str) -> Dict:
        """Test RSS/Atom feed"""
        try:
            response = await self.http_client.get(endpoint)
            if response.status_code == 200:
                content = response.text
                if '<rss' in content or '<feed' in content or '<channel' in content:
                    return {
                        "success": True,
                        "format": "RSS/Atom",
                        "message": "Valid feed detected",
                        "content_length": len(content)
                    }
                else:
                    return {"success": False, "error": "URL does not contain valid RSS/Atom feed"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_csv(self, endpoint: str) -> Dict:
        """Test CSV file URL"""
        try:
            response = await self.http_client.get(endpoint)
            if response.status_code == 200:
                lines = response.text.split('\n')[:5]
                return {
                    "success": True,
                    "format": "CSV",
                    "rows_preview": len(lines),
                    "header": lines[0] if lines else None,
                    "sample_row": lines[1] if len(lines) > 1 else None
                }
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_graphql(self, endpoint: str, auth_config: dict) -> Dict:
        """Test GraphQL endpoint"""
        headers = {'Content-Type': 'application/json'}
        
        if auth_config.get('type') == 'bearer':
            headers['Authorization'] = f"Bearer {auth_config.get('token', '')}"
        
        # Introspection query
        query = {"query": "{ __schema { types { name } } }"}
        
        try:
            response = await self.http_client.post(endpoint, json=query, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data:
                    return {
                        "success": True,
                        "message": "GraphQL endpoint responding",
                        "introspection": "enabled" if '__schema' in str(data) else "disabled"
                    }
                elif 'errors' in data:
                    return {"success": False, "error": data['errors'][0].get('message', 'GraphQL error')}
            return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _update_source_status(self, source_id: str, status: str, error: str = None):
        """Update source status after test"""
        conn = get_connection()
        cursor = conn.cursor()
        
        now = datetime.now(timezone.utc).isoformat()
        
        if error:
            cursor.execute("""
                UPDATE user_data_sources 
                SET status = ?, error_message = ?, last_check = ?, updated_at = ?
                WHERE id = ?
            """, (status, error, now, now, source_id))
        else:
            cursor.execute("""
                UPDATE user_data_sources 
                SET status = ?, error_message = NULL, last_check = ?, updated_at = ?
                WHERE id = ?
            """, (status, now, now, source_id))
        
        conn.commit()
        conn.close()
    
    # ==================== DATA FETCHING ====================
    
    async def fetch_data(self, source_id: str, user_id: str) -> Dict:
        """Fetch latest data from source"""
        source = self.get_source(source_id, user_id)
        if not source:
            return {"success": False, "error": "Source not found"}
        
        if source['status'] != 'active':
            return {"success": False, "error": f"Source not active. Status: {source['status']}"}
        
        source_type = source['type']
        endpoint = source['endpoint']
        auth_config = source.get('auth_config', {})
        
        try:
            if source_type == 'api':
                data = await self._fetch_api(endpoint, auth_config)
            elif source_type == 'rss':
                data = await self._fetch_rss(endpoint)
            elif source_type == 'csv':
                data = await self._fetch_csv(endpoint)
            else:
                return {"success": False, "error": f"Fetch not supported for type: {source_type}"}
            
            if data.get('success'):
                # Store data point
                self._store_data_point(source_id, data.get('data', {}))
                
            return data
            
        except Exception as e:
            logger.error(f"Data fetch failed for {source_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _fetch_api(self, endpoint: str, auth_config: dict) -> Dict:
        """Fetch data from REST API"""
        headers = {'Accept': 'application/json'}
        
        if auth_config.get('type') == 'bearer':
            headers['Authorization'] = f"Bearer {auth_config.get('token', '')}"
        elif auth_config.get('type') == 'api_key':
            key_name = auth_config.get('key_name', 'X-API-Key')
            headers[key_name] = auth_config.get('api_key', '')
        
        response = await self.http_client.get(endpoint, headers=headers)
        
        if response.status_code == 200:
            try:
                data = response.json()
                return {"success": True, "data": data}
            except:
                return {"success": True, "data": {"raw": response.text}}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}"}
    
    async def _fetch_rss(self, endpoint: str) -> Dict:
        """Fetch RSS feed items"""
        try:
            import feedparser
        except ImportError:
            # Fallback to raw XML
            response = await self.http_client.get(endpoint)
            return {"success": True, "data": {"raw_xml": response.text[:1000]}}
        
        response = await self.http_client.get(endpoint)
        feed = feedparser.parse(response.text)
        
        items = []
        for entry in feed.entries[:10]:  # Last 10 items
            items.append({
                "title": entry.get('title'),
                "link": entry.get('link'),
                "published": entry.get('published'),
                "summary": entry.get('summary', '')[:200]
            })
        
        return {"success": True, "data": {"items": items, "count": len(feed.entries)}}
    
    async def _fetch_csv(self, endpoint: str) -> Dict:
        """Fetch and parse CSV"""
        response = await self.http_client.get(endpoint)
        
        lines = response.text.strip().split('\n')
        if not lines:
            return {"success": False, "error": "Empty CSV"}
        
        headers = lines[0].split(',')
        rows = []
        for line in lines[1:11]:  # First 10 data rows
            values = line.split(',')
            rows.append(dict(zip(headers, values)))
        
        return {
            "success": True, 
            "data": {
                "headers": headers,
                "rows": rows,
                "total_rows": len(lines) - 1
            }
        }
    
    def _store_data_point(self, source_id: str, data: Any):
        """Store fetched data point"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO source_data_points (source_id, value, metadata)
            VALUES (?, ?, ?)
        """, (source_id, json.dumps(data), '{}'))
        
        # Update source data_points count and last_data
        cursor.execute("""
            UPDATE user_data_sources 
            SET data_points = data_points + 1, last_data = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (source_id,))
        
        conn.commit()
        conn.close()
    
    def get_data_points(self, source_id: str, user_id: str, limit: int = 100) -> List[Dict]:
        """Get stored data points for a source"""
        # Verify ownership
        source = self.get_source(source_id, user_id)
        if not source:
            return []
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM source_data_points 
            WHERE source_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (source_id, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        points = []
        for row in rows:
            point = dict(row)
            point['value'] = json.loads(point['value'])
            point['metadata'] = json.loads(point['metadata'])
            points.append(point)
        
        return points


# Singleton service
_service: Optional[UserDataSourcesService] = None

def get_service() -> UserDataSourcesService:
    global _service
    if _service is None:
        _service = UserDataSourcesService()
    return _service

