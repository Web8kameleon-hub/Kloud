# -*- coding: utf-8 -*-
"""
🌊 KLOUD CELL REGISTRY
=========================
Anatomia e organizmës - Çdo modul është një qelizë.

Çdo qelizë ka:
- ID unike
- Rol (sensor, processor, gateway, ui, logic)
- Aftësi (capabilities)
- Gjendje (state)
- Lidhje me qelizat e tjera (links)

Të gjitha qelizat formojnë një graf të gjallë:
G = (Cells, Edges)

Author: Kloud Team
Version: 1.0.0
"""

from __future__ import annotations
import logging
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cell_registry")


# =============================================================================
# CELL TYPES
# =============================================================================

class CellRole(Enum):
    """Rolet e qelizave në sistem"""
    SENSOR = "sensor"           # Mbledh të dhëna
    PROCESSOR = "processor"     # Procedon të dhëna
    GATEWAY = "gateway"         # Ndërmjetëson komunikimin
    UI = "ui"                   # Ndërfaqja e përdoruesit
    LOGIC = "logic"             # Logjikë biznesi
    STORAGE = "storage"         # Ruajtje të dhënash
    AI = "ai"                   # Inteligjencë artificiale
    ORCHESTRATOR = "orchestrator"  # Koordinon të tjerët
    EXTERNAL = "external"       # Shërbim i jashtëm
    API = "api"                 # Endpoint API


class CellState(Enum):
    """Gjendja e qelizës"""
    ACTIVE = "active"           # Punon normalisht
    IDLE = "idle"               # Në pritje
    BUSY = "busy"               # Duke procesuar
    ERROR = "error"             # Gabim
    OFFLINE = "offline"         # Jo aktive
    STARTING = "starting"       # Duke u ndezur
    STOPPING = "stopping"       # Duke u fikur


# =============================================================================
# CELL DATA CLASS
# =============================================================================

@dataclass
class Cell:
    """
    Një qelizë në sistem - njësia bazë e organizmës.
    
    Çdo modul, sensor, shërbim, API është një qelizë.
    """
    cell_id: str = field(default_factory=lambda: f"cell_{uuid.uuid4().hex[:8]}")
    name: str = ""
    role: CellRole = CellRole.LOGIC
    state: CellState = CellState.IDLE
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    links: List[str] = field(default_factory=list)  # IDs of connected cells
    endpoint: Optional[str] = None  # URL if it's an API endpoint
    port: Optional[int] = None
    health_url: Optional[str] = None
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: List[str] = field(default_factory=list)
    
    # Callback për kur thirret qeliza
    on_call: Optional[Callable[[str, Dict], Dict]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.cell_id,
            "name": self.name,
            "role": self.role.value,
            "state": self.state.value,
            "capabilities": self.capabilities,
            "metadata": self.metadata,
            "links": self.links,
            "endpoint": self.endpoint,
            "port": self.port,
            "health_url": self.health_url,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "created_at": self.created_at.isoformat(),
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Cell":
        return cls(
            cell_id=data.get("id", f"cell_{uuid.uuid4().hex[:8]}"),
            name=data.get("name", ""),
            role=CellRole(data.get("role", "logic")),
            state=CellState(data.get("state", "idle")),
            capabilities=data.get("capabilities", []),
            metadata=data.get("metadata", {}),
            links=data.get("links", []),
            endpoint=data.get("endpoint"),
            port=data.get("port"),
            health_url=data.get("health_url"),
            tags=data.get("tags", [])
        )
    
    def is_healthy(self, max_age_seconds: int = 60) -> bool:
        """Kontrollo nëse qeliza është e shëndetshme."""
        if self.state in [CellState.ERROR, CellState.OFFLINE]:
            return False
        
        age = (datetime.now(timezone.utc) - self.last_heartbeat).total_seconds()
        return age < max_age_seconds
    
    def heartbeat(self):
        """Përditëso heartbeat."""
        self.last_heartbeat = datetime.now(timezone.utc)
    
    def add_link(self, cell_id: str):
        """Shto lidhje me qelizë tjetër."""
        if cell_id not in self.links:
            self.links.append(cell_id)
    
    def remove_link(self, cell_id: str):
        """Hiq lidhjen me qelizë tjetër."""
        if cell_id in self.links:
            self.links.remove(cell_id)


# =============================================================================
# CELL REGISTRY
# =============================================================================

class CellRegistry:
    """
    🧬 CELL REGISTRY
    
    Regjistri qendror i të gjitha qelizave në sistem.
    Mban gjurmët e kush është kush, çfarë di të bëjë, ku ndodhet.
    """
    
    def __init__(self):
        self.cells: Dict[str, Cell] = {}
        self._register_builtin_cells()
        logger.info(f"🧬 Cell Registry initialized with {len(self.cells)} built-in cells")
    
    def _register_builtin_cells(self):
        """Regjistro qelizat e brendshme të sistemit."""
        builtin_cells = [
            # Core Services
            Cell(
                cell_id="kloud-api",
                name="Kloud Main API",
                role=CellRole.API,
                capabilities=["health", "status", "metrics", "routing"],
                endpoint="http://localhost:8000",
                port=8000,
                health_url="/health",
                tags=["core", "api"]
            ),
            Cell(
                cell_id="ocean-core",
                name="Curiosity Ocean Core",
                role=CellRole.ORCHESTRATOR,
                capabilities=["chat", "query", "personas", "knowledge"],
                endpoint="http://localhost:8030",
                port=8030,
                health_url="/health",
                tags=["core", "ocean", "ai"]
            ),
            # ASI Trinity
            Cell(
                cell_id="asi-engine",
                name="ASI Engine",
                role=CellRole.AI,
                capabilities=["superintelligence", "reasoning", "decision"],
                endpoint="http://localhost:9094",
                port=9094,
                health_url="/health",
                tags=["asi", "ai", "trinity"]
            ),
            Cell(
                cell_id="alba",
                name="ALBA - Emotional AI",
                role=CellRole.AI,
                capabilities=["emotion", "empathy", "creativity"],
                endpoint="http://localhost:5555",
                port=5555,
                health_url="/health",
                tags=["asi", "ai", "trinity", "alba"]
            ),
            Cell(
                cell_id="albi",
                name="ALBI - Brain Interface",
                role=CellRole.AI,
                capabilities=["eeg", "biometrics", "neural"],
                endpoint="http://localhost:6666",
                port=6666,
                health_url="/health",
                tags=["asi", "ai", "trinity", "albi"]
            ),
            # Data Services
            Cell(
                cell_id="reporting",
                name="Reporting Service",
                role=CellRole.PROCESSOR,
                capabilities=["excel", "pptx", "pdf", "reports"],
                endpoint="http://localhost:8001",
                port=8001,
                health_url="/health",
                tags=["reporting", "export"]
            ),
            Cell(
                cell_id="excel-api",
                name="Excel API",
                role=CellRole.PROCESSOR,
                capabilities=["excel", "spreadsheet", "data-export"],
                endpoint="http://localhost:8002",
                port=8002,
                health_url="/health",
                tags=["excel", "export"]
            ),
            Cell(
                cell_id="behavioral",
                name="Behavioral Science API",
                role=CellRole.AI,
                capabilities=["behavior", "analysis", "psychology"],
                endpoint="http://localhost:8003",
                port=8003,
                health_url="/health",
                tags=["behavioral", "ai"]
            ),
            Cell(
                cell_id="marketplace",
                name="Marketplace API",
                role=CellRole.API,
                capabilities=["products", "services", "commerce"],
                endpoint="http://localhost:8004",
                port=8004,
                health_url="/health",
                tags=["marketplace", "commerce"]
            ),
            # External Data
            Cell(
                cell_id="aviation",
                name="Aviation Weather API",
                role=CellRole.EXTERNAL,
                capabilities=["metar", "taf", "weather", "aviation"],
                endpoint="http://localhost:8080",
                port=8080,
                health_url="/health",
                tags=["aviation", "weather", "external"]
            ),
            Cell(
                cell_id="economy",
                name="Economy API",
                role=CellRole.EXTERNAL,
                capabilities=["economy", "indicators", "finance"],
                endpoint="http://localhost:9093",
                port=9093,
                health_url="/health",
                tags=["economy", "finance"]
            ),
            # Infrastructure
            Cell(
                cell_id="redis",
                name="Redis Cache",
                role=CellRole.STORAGE,
                capabilities=["cache", "pubsub", "session"],
                endpoint="redis://localhost:6379",
                port=6379,
                tags=["infrastructure", "cache"]
            ),
            Cell(
                cell_id="postgres",
                name="PostgreSQL Database",
                role=CellRole.STORAGE,
                capabilities=["database", "sql", "persistence"],
                endpoint="postgresql://localhost:5432",
                port=5432,
                tags=["infrastructure", "database"]
            ),
            Cell(
                cell_id="victoriametrics",
                name="VictoriaMetrics",
                role=CellRole.STORAGE,
                capabilities=["metrics", "timeseries", "monitoring"],
                endpoint="http://localhost:8428",
                port=8428,
                tags=["infrastructure", "metrics"]
            ),
            # Frontend
            Cell(
                cell_id="web-frontend",
                name="Web Frontend",
                role=CellRole.UI,
                capabilities=["dashboard", "ui", "visualization"],
                endpoint="http://localhost:3000",
                port=3000,
                tags=["frontend", "ui"]
            ),
        ]
        
        for cell in builtin_cells:
            self.cells[cell.cell_id] = cell
    
    # =========================================================================
    # CRUD OPERATIONS
    # =========================================================================
    
    def register(self, cell: Cell) -> Cell:
        """Regjistro një qelizë të re."""
        self.cells[cell.cell_id] = cell
        logger.info(f"✅ Registered cell: {cell.cell_id} ({cell.name})")
        return cell
    
    def unregister(self, cell_id: str) -> bool:
        """Hiq një qelizë nga regjistri."""
        if cell_id in self.cells:
            del self.cells[cell_id]
            logger.info(f"❌ Unregistered cell: {cell_id}")
            return True
        return False
    
    def get(self, cell_id: str) -> Optional[Cell]:
        """Merr një qelizë sipas ID."""
        return self.cells.get(cell_id)
    
    def update(self, cell_id: str, updates: Dict[str, Any]) -> Optional[Cell]:
        """Përditëso një qelizë."""
        cell = self.cells.get(cell_id)
        if not cell:
            return None
        
        for key, value in updates.items():
            if hasattr(cell, key):
                setattr(cell, key, value)
        
        return cell
    
    def list_all(self) -> List[Cell]:
        """Lista e të gjitha qelizave."""
        return list(self.cells.values())
    
    # =========================================================================
    # QUERY OPERATIONS
    # =========================================================================
    
    def query(self, 
              role: Optional[CellRole] = None,
              state: Optional[CellState] = None,
              tags: Optional[List[str]] = None,
              capability: Optional[str] = None) -> List[Cell]:
        """
        Query qelizat me filtra.
        """
        result = list(self.cells.values())
        
        if role:
            result = [c for c in result if c.role == role]
        
        if state:
            result = [c for c in result if c.state == state]
        
        if tags:
            result = [c for c in result if all(t in c.tags for t in tags)]
        
        if capability:
            result = [c for c in result if capability in c.capabilities]
        
        return result
    
    def query_by_role(self, role: CellRole) -> List[Cell]:
        """Merr qelizat sipas rolit."""
        return [c for c in self.cells.values() if c.role == role]
    
    def query_healthy(self, max_age_seconds: int = 60) -> List[Cell]:
        """Merr vetëm qelizat e shëndetshme."""
        return [c for c in self.cells.values() if c.is_healthy(max_age_seconds)]
    
    def query_unhealthy(self, max_age_seconds: int = 60) -> List[Cell]:
        """Merr qelizat që kanë probleme."""
        return [c for c in self.cells.values() if not c.is_healthy(max_age_seconds)]
    
    def query_by_port(self, port: int) -> Optional[Cell]:
        """Gjej qelizën sipas portit."""
        for cell in self.cells.values():
            if cell.port == port:
                return cell
        return None
    
    def query_linked(self, cell_id: str) -> List[Cell]:
        """Merr të gjitha qelizat e lidhura me një qelizë."""
        cell = self.cells.get(cell_id)
        if not cell:
            return []
        
        return [self.cells[link] for link in cell.links if link in self.cells]
    
    # =========================================================================
    # GRAPH OPERATIONS
    # =========================================================================
    
    def get_graph(self) -> Dict[str, Any]:
        """
        Merr grafin e qelizave.
        G = (Cells, Edges)
        """
        nodes = []
        edges = []
        
        for cell in self.cells.values():
            nodes.append({
                "id": cell.cell_id,
                "name": cell.name,
                "role": cell.role.value,
                "state": cell.state.value
            })
            
            for link in cell.links:
                edges.append({
                    "from": cell.cell_id,
                    "to": link
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }
    
    def add_link(self, from_cell: str, to_cell: str, bidirectional: bool = False):
        """Shto lidhje mes dy qelizave."""
        if from_cell in self.cells and to_cell in self.cells:
            self.cells[from_cell].add_link(to_cell)
            
            if bidirectional:
                self.cells[to_cell].add_link(from_cell)
    
    def remove_link(self, from_cell: str, to_cell: str, bidirectional: bool = False):
        """Hiq lidhjen mes dy qelizave."""
        if from_cell in self.cells:
            self.cells[from_cell].remove_link(to_cell)
        
        if bidirectional and to_cell in self.cells:
            self.cells[to_cell].remove_link(from_cell)
    
    # =========================================================================
    # HEALTH & MONITORING
    # =========================================================================
    
    def heartbeat(self, cell_id: str) -> bool:
        """Përditëso heartbeat-in e një qelize."""
        cell = self.cells.get(cell_id)
        if cell:
            cell.heartbeat()
            return True
        return False
    
    def set_state(self, cell_id: str, state: CellState) -> bool:
        """Ndrysho gjendjen e një qelize."""
        cell = self.cells.get(cell_id)
        if cell:
            cell.state = state
            return True
        return False
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Përmbledhje e shëndetit të të gjitha qelizave."""
        total = len(self.cells)
        healthy = len(self.query_healthy())
        
        by_state = {}
        for cell in self.cells.values():
            s = cell.state.value
            if s not in by_state:
                by_state[s] = 0
            by_state[s] += 1
        
        by_role = {}
        for cell in self.cells.values():
            r = cell.role.value
            if r not in by_role:
                by_role[r] = 0
            by_role[r] += 1
        
        return {
            "total_cells": total,
            "healthy_cells": healthy,
            "unhealthy_cells": total - healthy,
            "health_percentage": round((healthy / total * 100), 2) if total > 0 else 0,
            "by_state": by_state,
            "by_role": by_role
        }
    
    # =========================================================================
    # SERIALIZATION
    # =========================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Eksporto regjistrin në dict."""
        return {
            "cells": [c.to_dict() for c in self.cells.values()],
            "total": len(self.cells)
        }
    
    def to_json(self) -> str:
        """Eksporto regjistrin në JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    def from_json(self, json_str: str):
        """Importo qelizat nga JSON."""
        data = json.loads(json_str)
        for cell_data in data.get("cells", []):
            cell = Cell.from_dict(cell_data)
            self.cells[cell.cell_id] = cell


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_registry_instance: Optional[CellRegistry] = None

def get_cell_registry() -> CellRegistry:
    """Get or create the Cell Registry singleton."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = CellRegistry()
    return _registry_instance


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    registry = get_cell_registry()
    
    print(f"\n=== Cell Registry ===")
    print(f"Total cells: {len(registry.cells)}")
    
    # Lista e qelizave sipas rolit
    print(f"\nBy Role:")
    for role in CellRole:
        cells = registry.query_by_role(role)
        if cells:
            print(f"  {role.value}: {len(cells)}")
    
    # Health summary
    health = registry.get_health_summary()
    print(f"\nHealth Summary: {health}")
    
    # Graph
    graph = registry.get_graph()
    print(f"\nGraph: {graph['total_nodes']} nodes, {graph['total_edges']} edges")
    
    # Export
    print(f"\nAll cells:")
    for cell in registry.list_all():
        print(f"  - {cell.cell_id}: {cell.name} ({cell.role.value})")

