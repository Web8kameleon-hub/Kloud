"""
ðŸ“¡ ALBA - Artificial Laboratory Bits Algorithms (REAL DATA COLLECTOR)
=====================================================================
KolektorÃ« real i tÃ« dhÃ«nave qÃ« mbledh informacione nga sistemi Kloud.
Real file scanner, real data processor, real metrics collector.

NO FAKE DATA, NO MOCK, REAL COLLECTION ONLY
"""

import asyncio
import os
import json
import aiofiles
from datetime import datetime
from typing import Dict, List, Any, Generator
from pathlib import Path
import hashlib


class ALBA_RealCollector:
    """
    ðŸ“Š ALBA Real Data Collector qÃ« mbledh tÃ« dhÃ«na reale nga sistemi
    """
    
    def __init__(self, base_dir="C:/Kloud-cloud"):
        self.base_dir = Path(base_dir)
        self.collection_log = self.base_dir / "data" / "alba_collection_log.json"
        self.collected_files = []
        self.real_stats = {
            "files_scanned": 0,
            "data_collected_bytes": 0,
            "collection_sessions": 0
        }
    
    async def scan_real_directories(self) -> List[Dict[str, Any]]:
        """Skanon direktorit reale tÃ« sistemit pÃ«r tÃ« dhÃ«na"""
        real_data = []
        
        # Direktorit qÃ« do tÃ« skanohen
        scan_dirs = [
            self.base_dir / "data",
            self.base_dir / "uploads", 
            self.base_dir / "outputs",
            self.base_dir / "app" / "services",
            self.base_dir / "backend" / "app"
        ]
        
        for scan_dir in scan_dirs:
            if scan_dir.exists():
                async for file_info in self.collect_from_directory(scan_dir):
                    real_data.append(file_info)
                    self.real_stats["files_scanned"] += 1
        
        return real_data
    
    async def collect_from_directory(self, directory: Path) -> Generator[Dict[str, Any], None, None]:
        """Kolekton tÃ« dhÃ«na reale nga njÃ« direktori"""
        try:
            for item in directory.rglob('*'):
                if item.is_file():
                    file_stats = item.stat()
                    
                    # Llogarit hash real tÃ« file-it
                    file_hash = await self.calculate_real_hash(str(item))
                    
                    file_info = {
                        "file_path": str(item),
                        "file_name": item.name,
                        "file_size": file_stats.st_size,
                        "file_extension": item.suffix,
                        "created_time": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                        "modified_time": datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        "file_hash": file_hash,
                        "collected_at": datetime.utcnow().isoformat(),
                        "collection_source": "ALBA_real_scanner"
                    }
                    
                    self.real_stats["data_collected_bytes"] += file_stats.st_size
                    yield file_info
                    
        except Exception as e:
            yield {
                "error": str(e),
                "directory": str(directory),
                "collection_failed": True
            }
    
    async def calculate_real_hash(self, file_path: str) -> str:
        """Llogarit hash real SHA256 tÃ« njÃ« file"""
        try:
            hash_sha256 = hashlib.sha256()
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(8192):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return "hash_failed"
    
    async def collect_real_system_metrics(self) -> Dict[str, Any]:
        """Kolekton metrika reale tÃ« sistemit"""
        import psutil
        
        # CPU real
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory real
        memory = psutil.virtual_memory()
        
        # Disk real
        disk = psutil.disk_usage(str(self.base_dir))
        
        # Process real
        process = psutil.Process()
        
        return {
            "system_metrics": {
                "cpu_usage_percent": cpu_percent,
                "cpu_cores": cpu_count,
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2)
            },
            "process_metrics": {
                "memory_usage_mb": round(process.memory_info().rss / (1024**2), 2),
                "cpu_usage_percent": process.cpu_percent(),
                "open_files": len(process.open_files()),
                "num_threads": process.num_threads()
            },
            "collected_at": datetime.utcnow().isoformat(),
            "collector": "ALBA_real_metrics",
            "real_data_only": True
        }
    
    async def send_to_albi_real(self, collected_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """DÃ«rgon tÃ« dhÃ«na reale tek ALBI pÃ«r pÃ«rpunim"""
        from .albi_real_engine import create_albi_real
        
        albi = await create_albi_real()
        processing_results = []
        
        for data_item in collected_data:
            if "file_path" in data_item and os.path.exists(data_item["file_path"]):
                try:
                    result = await albi.consume_real_file(data_item["file_path"])
                    processing_results.append(result)
                except Exception as e:
                    processing_results.append({
                        "error": str(e),
                        "file": data_item["file_path"]
                    })
        
        # Log koleksionin real
        await self.log_real_collection(len(collected_data), len(processing_results))
        
        return {
            "alba_to_albi_transfer": "completed",
            "data_items_sent": len(collected_data),
            "processing_results": len(processing_results),
            "successful_transfers": len([r for r in processing_results if "status" in r]),
            "transfer_timestamp": datetime.utcnow().isoformat(),
            "real_transfer_only": True
        }
    
    async def log_real_collection(self, collected_count: int, processed_count: int):
        """Log i koleksionit real nÃ« file"""
        log_entry = {
            "session_id": hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()[:16],
            "collected_items": collected_count,
            "processed_items": processed_count,
            "collection_stats": self.real_stats,
            "timestamp": datetime.utcnow().isoformat(),
            "alba_session": True
        }
        
        # Lexo log-un ekzistues
        existing_log = []
        if self.collection_log.exists():
            async with aiofiles.open(self.collection_log, 'r') as f:
                content = await f.read()
                if content.strip():
                    existing_log = json.loads(content)
        
        # Shto session-in e ri
        existing_log.append(log_entry)
        
        # Mbaj vetÃ«m 100 session tÃ« fundit
        if len(existing_log) > 100:
            existing_log = existing_log[-100:]
        
        # Ruaj log-un
        self.collection_log.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(self.collection_log, 'w') as f:
            await f.write(json.dumps(existing_log, indent=2, ensure_ascii=False))
    
    async def get_real_status(self) -> Dict[str, Any]:
        """Kthen statusin real tÃ« ALBA"""
        return {
            "character": "ALBA",
            "status": "active_real_collection",
            "collection_stats": self.real_stats,
            "base_directory": str(self.base_dir),
            "log_file": str(self.collection_log),
            "last_activity": datetime.utcnow().isoformat(),
            "real_data_only": True,
            "no_mock_no_fake": True
        }


# Factory function pÃ«r ALBA real
async def create_alba_real() -> ALBA_RealCollector:
    """Krijon njÃ« instance ALBA qÃ« mbledh tÃ« dhÃ«na reale"""
    alba = ALBA_RealCollector()
    return alba



