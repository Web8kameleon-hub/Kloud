"""
KLOUD AUTO REGISTRY
======================
Skanon dhe përditëson automatikisht të gjitha funksionet në sistem.
Çdo modul regjistrohet me funksionet e tij për përdorim nga modulet e tjera.

Përdorimi:
    from core.auto_registry import registry, discover_all, get_function
    
    # Zbulo të gjitha funksionet
    discover_all()
    
    # Merr një funksion nga çdo modul
    chat_func = get_function("ocean", "chat")
    result = chat_func(message="Përshëndetje")
"""

import os
import sys
import json
import importlib.util
import inspect
import asyncio
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AutoRegistry")

# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class FunctionInfo:
    """Informacion për një funksion të regjistruar"""
    name: str
    module: str
    service: str
    port: int
    path: str
    signature: str
    docstring: str
    is_async: bool
    parameters: List[Dict[str, Any]]
    return_type: str
    tags: List[str] = field(default_factory=list)
    
@dataclass  
class ServiceInfo:
    """Informacion për një shërbim"""
    name: str
    port: int
    file: str
    status: str  # 'active', 'inactive', 'error'
    functions: List[str] = field(default_factory=list)
    endpoints: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


# =============================================================================
# REGISTRY CORE
# =============================================================================

class AutoRegistry:
    """Regjistri qendror i të gjitha funksioneve dhe shërbimeve"""
    
    def __init__(self):
        self.root = Path(__file__).parent.parent
        self.functions: Dict[str, FunctionInfo] = {}
        self.services: Dict[str, ServiceInfo] = {}
        self.endpoints: Dict[str, Dict[str, Any]] = {}
        self._discovered = False
        self._last_scan = None
        
        # Shërbimet e njohura
        self.known_services = {
            "backend": {"port": 8000, "file": "apps/api/main.py"},
            "ocean": {"port": 8030, "file": "ocean-core/ocean_api.py"},
            "alba": {"port": 5555, "file": "alba_service_5555.py"},
            "albi": {"port": 6680, "file": "albi_service_6680.py"},
            "jona": {"port": 7777, "file": "jona_service_7777.py"},
            "alda": {"port": 7070, "file": "alda_server.py"},
            "liam": {"port": 7575, "file": "liam_server.py"},
            "blerina": {"port": 7680, "file": "blerina_reformatter.py"},
            "agiem": {"port": 8080, "file": "agiem_core.py"},
        }
    
    def discover_all(self, force: bool = False) -> Dict[str, Any]:
        """Zbulo të gjitha funksionet dhe shërbimet"""
        if self._discovered and not force:
            return self.get_summary()
        
        logger.info("🔍 Duke skanuar sistemin për funksione...")
        
        # 1. Skano shërbimet e njohura
        for service_name, info in self.known_services.items():
            self._scan_service(service_name, info)
        
        # 2. Skano core/ directory
        self._scan_core_modules()
        
        # 3. Skano për FastAPI endpoints
        self._scan_fastapi_endpoints()
        
        self._discovered = True
        self._last_scan = datetime.now().isoformat()
        
        logger.info(f"✅ Zbuluar {len(self.functions)} funksione në {len(self.services)} shërbime")
        return self.get_summary()
    
    def _scan_service(self, name: str, info: Dict) -> None:
        """Skano një shërbim të vetëm"""
        file_path = self.root / info["file"]
        
        if not file_path.exists():
            self.services[name] = ServiceInfo(
                name=name,
                port=info["port"],
                file=info["file"],
                status="missing"
            )
            return
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Gjej funksionet
            functions = self._extract_functions(content, name, info)
            
            # Gjej endpoints
            endpoints = self._extract_endpoints(content)
            
            self.services[name] = ServiceInfo(
                name=name,
                port=info["port"],
                file=info["file"],
                status="active",
                functions=[f.name for f in functions],
                endpoints=endpoints
            )
            
            for func in functions:
                key = f"{name}.{func.name}"
                self.functions[key] = func
                
        except Exception as e:
            logger.warning(f"⚠️ Gabim duke skanuar {name}: {e}")
            self.services[name] = ServiceInfo(
                name=name,
                port=info["port"],
                file=info["file"],
                status="error"
            )
    
    def _extract_functions(self, content: str, service: str, info: Dict) -> List[FunctionInfo]:
        """Nxjerr funksionet nga përmbajtja e file-it"""
        functions = []
        lines = content.split('\n')
        
        current_docstring = ""
        
        for i, line in enumerate(lines):
            # Gjej definicionet e funksioneve
            if line.strip().startswith('def ') or line.strip().startswith('async def '):
                is_async = 'async def' in line
                
                # Nxjerr emrin dhe parametrat
                try:
                    if 'def ' in line and '(' in line:
                        start = line.index('def ') + 4
                        end = line.index('(')
                        func_name = line[start:end].strip()
                        
                        # Skip private functions
                        if func_name.startswith('_') and not func_name.startswith('__'):
                            continue
                        
                        # Nxjerr signature
                        sig_end = line.find(':')
                        signature = line[start:sig_end].strip() if sig_end > 0 else func_name
                        
                        # Gjej docstring
                        docstring = ""
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            if next_line.startswith('"""') or next_line.startswith("'''"):
                                docstring = next_line.strip('"\'')
                        
                        functions.append(FunctionInfo(
                            name=func_name,
                            module=Path(info["file"]).stem,
                            service=service,
                            port=info["port"],
                            path=info["file"],
                            signature=signature,
                            docstring=docstring,
                            is_async=is_async,
                            parameters=[],
                            return_type="Any"
                        ))
                except:
                    continue
        
        return functions
    
    def _extract_endpoints(self, content: str) -> List[str]:
        """Nxjerr FastAPI endpoints"""
        endpoints = []
        
        # Patterns për endpoints
        patterns = [
            '@app.get("', '@app.post("', '@app.put("', '@app.delete("',
            '@router.get("', '@router.post("', '@router.put("', '@router.delete("',
            '@app.get(\'', '@app.post(\'', '@app.put(\'', '@app.delete(\'',
        ]
        
        for line in content.split('\n'):
            line = line.strip()
            for pattern in patterns:
                if pattern in line:
                    # Nxjerr path-in
                    try:
                        start = line.index(pattern) + len(pattern)
                        end = line.index('"', start) if '"' in line[start:] else line.index("'", start)
                        path = line[start:end]
                        method = pattern.split('.')[1].split('(')[0].upper()
                        endpoints.append(f"{method} {path}")
                    except:
                        continue
        
        return endpoints
    
    def _scan_core_modules(self) -> None:
        """Skano modulet core/"""
        core_dir = self.root / "core"
        if not core_dir.exists():
            return
        
        for py_file in core_dir.rglob("*.py"):
            if py_file.name.startswith('_'):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8', errors='ignore')
                rel_path = py_file.relative_to(self.root)
                
                info = {"port": 0, "file": str(rel_path)}
                functions = self._extract_functions(content, "core", info)
                
                for func in functions:
                    key = f"core.{py_file.stem}.{func.name}"
                    self.functions[key] = func
                    
            except Exception as e:
                logger.debug(f"Skip {py_file}: {e}")
    
    def _scan_fastapi_endpoints(self) -> None:
        """Skano të gjitha FastAPI endpoints"""
        for service_name, service_info in self.services.items():
            if service_info.status != "active":
                continue
            
            for endpoint in service_info.endpoints:
                parts = endpoint.split(' ')
                if len(parts) == 2:
                    method, path = parts
                    key = f"{service_name}:{path}"
                    self.endpoints[key] = {
                        "service": service_name,
                        "port": service_info.port,
                        "method": method,
                        "path": path,
                        "url": f"http://localhost:{service_info.port}{path}"
                    }
    
    def get_function(self, service: str, name: str) -> Optional[FunctionInfo]:
        """Merr informacion për një funksion"""
        key = f"{service}.{name}"
        return self.functions.get(key)
    
    def get_service(self, name: str) -> Optional[ServiceInfo]:
        """Merr informacion për një shërbim"""
        return self.services.get(name)
    
    def get_endpoint(self, service: str, path: str) -> Optional[Dict]:
        """Merr informacion për një endpoint"""
        key = f"{service}:{path}"
        return self.endpoints.get(key)
    
    def search(self, query: str) -> Dict[str, List]:
        """Kërko funksione dhe endpoints"""
        query = query.lower()
        results = {
            "functions": [],
            "endpoints": [],
            "services": []
        }
        
        for key, func in self.functions.items():
            if query in key.lower() or query in func.docstring.lower():
                results["functions"].append(asdict(func))
        
        for key, endpoint in self.endpoints.items():
            if query in key.lower():
                results["endpoints"].append(endpoint)
        
        for name, service in self.services.items():
            if query in name.lower():
                results["services"].append(asdict(service))
        
        return results
    
    def get_summary(self) -> Dict[str, Any]:
        """Merr përmbledhje të regjistrit"""
        return {
            "total_functions": len(self.functions),
            "total_services": len(self.services),
            "total_endpoints": len(self.endpoints),
            "last_scan": self._last_scan,
            "services": {
                name: {
                    "port": svc.port,
                    "status": svc.status,
                    "functions_count": len(svc.functions),
                    "endpoints_count": len(svc.endpoints)
                }
                for name, svc in self.services.items()
            }
        }
    
    def export_json(self, filepath: str = None) -> str:
        """Eksporto regjistrin në JSON"""
        if filepath is None:
            filepath = str(self.root / "registry_export.json")
        
        data = {
            "generated": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "services": {k: asdict(v) for k, v in self.services.items()},
            "functions": {k: asdict(v) for k, v in self.functions.items()},
            "endpoints": self.endpoints
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def generate_env_file(self, filepath: str = None) -> str:
        """Gjenero .env file me të gjitha port-et dhe URL-të"""
        if filepath is None:
            filepath = str(self.root / ".env.services")
        
        lines = [
            "# KLOUD SERVICES - Auto-generated by AutoRegistry",
            f"# Generated: {datetime.now().isoformat()}",
            "",
            "# Service Ports",
        ]
        
        for name, svc in self.services.items():
            env_name = name.upper()
            lines.append(f"{env_name}_PORT={svc.port}")
            lines.append(f"{env_name}_URL=http://localhost:{svc.port}")
        
        lines.extend([
            "",
            "# Service Status",
        ])
        
        for name, svc in self.services.items():
            env_name = name.upper()
            lines.append(f"{env_name}_STATUS={svc.status}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        return filepath


# =============================================================================
# GLOBAL INSTANCE & SHORTCUTS
# =============================================================================

# Instanca globale
registry = AutoRegistry()

def discover_all(force: bool = False) -> Dict[str, Any]:
    """Zbulo të gjitha funksionet dhe shërbimet"""
    return registry.discover_all(force)

def get_function(service: str, name: str) -> Optional[FunctionInfo]:
    """Merr informacion për një funksion"""
    if not registry._discovered:
        registry.discover_all()
    return registry.get_function(service, name)

def get_service(name: str) -> Optional[ServiceInfo]:
    """Merr informacion për një shërbim"""
    if not registry._discovered:
        registry.discover_all()
    return registry.get_service(name)

def search(query: str) -> Dict[str, List]:
    """Kërko funksione dhe endpoints"""
    if not registry._discovered:
        registry.discover_all()
    return registry.search(query)

def export() -> str:
    """Eksporto regjistrin"""
    if not registry._discovered:
        registry.discover_all()
    return registry.export_json()

def generate_env() -> str:
    """Gjenero .env file"""
    if not registry._discovered:
        registry.discover_all()
    return registry.generate_env_file()


# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Kloud Auto Registry")
    parser.add_argument("--scan", action="store_true", help="Skano sistemin")
    parser.add_argument("--export", action="store_true", help="Eksporto në JSON")
    parser.add_argument("--env", action="store_true", help="Gjenero .env file")
    parser.add_argument("--search", type=str, help="Kërko funksione")
    parser.add_argument("--summary", action="store_true", help="Trego përmbledhjen")
    
    args = parser.parse_args()
    
    if args.scan or not any([args.export, args.env, args.search, args.summary]):
        summary = discover_all(force=True)
        print("\n" + "="*60)
        print("📊 KLOUD AUTO REGISTRY - SCAN COMPLETE")
        print("="*60)
        print(f"\n🔧 Shërbime: {summary['total_services']}")
        print(f"📦 Funksione: {summary['total_functions']}")
        print(f"🌐 Endpoints: {summary['total_endpoints']}")
        print("\n📋 Shërbimet:")
        for name, info in summary['services'].items():
            status_icon = "✅" if info['status'] == 'active' else "❌"
            print(f"  {status_icon} {name:12} | Port {info['port']:5} | {info['functions_count']} funksione | {info['endpoints_count']} endpoints")
    
    if args.export:
        path = export()
        print(f"\n📄 Eksportuar në: {path}")
    
    if args.env:
        path = generate_env()
        print(f"\n📄 .env gjeneruar në: {path}")
    
    if args.search:
        results = search(args.search)
        print(f"\n🔍 Rezultate për '{args.search}':")
        for key, items in results.items():
            if items:
                print(f"\n  {key.upper()}:")
                for item in items[:10]:
                    if isinstance(item, dict):
                        print(f"    - {item.get('name', item.get('path', str(item)))}")
    
    if args.summary:
        summary = registry.get_summary()
        print(json.dumps(summary, indent=2, ensure_ascii=False))

