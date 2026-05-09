# -*- coding: utf-8 -*-
"""
🌊 KLOUD CALL OPERATOR
=========================
Mekanizmi që thërret çdo qelizë të brendshme/jashtme.

Call(query, scope) -> Responses[]

Mënyrat e thirrjes:
- Broadcast: "Të gjitha qelizat me rol X, raportoni"
- Targeted: "Qelizat që kanë parë anomali X"
- Cascade: Një qelizë thërret të tjerat e lidhura

Author: Kloud Team
Version: 1.0.0
"""

from __future__ import annotations
import logging
import asyncio
import httpx
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import uuid

from cell_registry import get_cell_registry, Cell, CellRole, CellState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("call_operator")


# =============================================================================
# CALL TYPES
# =============================================================================

class CallScope(Enum):
    """Scope i thirrjes"""
    ALL = "all"                     # Të gjitha qelizat
    ROLE = "role"                   # Sipas rolit
    CLUSTER = "cluster"             # Grup qelizash
    GRAPH_SUBSET = "graph_subset"   # Nën-graf i lidhur
    SINGLE = "single"               # Një qelizë e vetme
    TAGS = "tags"                   # Sipas tag-ave


class CallType(Enum):
    """Lloji i thirrjes"""
    BROADCAST = "broadcast"         # Të gjitha në scope
    TARGETED = "targeted"           # Me kushte specifike
    CASCADE = "cascade"             # Përhapet nga qeliza në qelizë


# =============================================================================
# CALL REQUEST & RESPONSE
# =============================================================================

@dataclass
class CallRequest:
    """Kërkesa për thirrje."""
    call_id: str = field(default_factory=lambda: f"call_{uuid.uuid4().hex[:8]}")
    query: str = ""
    scope: CallScope = CallScope.ALL
    scope_value: Optional[str] = None  # e.g., role name, cell_id
    call_type: CallType = CallType.BROADCAST
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: float = 10.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_id": self.call_id,
            "query": self.query,
            "scope": self.scope.value,
            "scope_value": self.scope_value,
            "call_type": self.call_type.value,
            "parameters": self.parameters,
            "timeout_seconds": self.timeout_seconds,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class CallResponse:
    """Përgjigja nga një qelizë."""
    cell_id: str = ""
    cell_name: str = ""
    success: bool = True
    response: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    latency_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "cell_id": self.cell_id,
            "cell_name": self.cell_name,
            "success": self.success,
            "response": self.response,
            "error": self.error,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp.isoformat()
        }


# =============================================================================
# CALL RESULT
# =============================================================================

@dataclass
class CallResult:
    """Rezultati i plotë i një thirrjeje."""
    call_id: str
    query: str
    scope: str
    total_cells: int = 0
    successful: int = 0
    failed: int = 0
    responses: List[CallResponse] = field(default_factory=list)
    total_latency_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "call_id": self.call_id,
            "query": self.query,
            "scope": self.scope,
            "total_cells": self.total_cells,
            "successful": self.successful,
            "failed": self.failed,
            "responses": [r.to_dict() for r in self.responses],
            "total_latency_ms": self.total_latency_ms,
            "timestamp": self.timestamp.isoformat()
        }


# =============================================================================
# CALL OPERATOR
# =============================================================================

class CallOperator:
    """
    📞 CALL OPERATOR
    
    Thërret qelizat e sistemit dhe mbledh përgjigjet.
    """
    
    def __init__(self):
        self.registry = get_cell_registry()
        self.call_history: List[CallResult] = []
        self.max_history = 100
        logger.info("📞 Call Operator initialized")
    
    # =========================================================================
    # MAIN CALL METHOD
    # =========================================================================
    
    async def call(self, request: CallRequest) -> CallResult:
        """
        Thirr qelizat sipas kërkesës.
        
        Call(query, scope) -> Responses[]
        """
        start_time = datetime.now(timezone.utc)
        
        # Gjej qelizat e targetuara
        cells = self._resolve_scope(request.scope, request.scope_value)
        
        # Thirr çdo qelizë
        responses: List[CallResponse] = []
        
        for cell in cells:
            response = await self._call_cell(cell, request)
            responses.append(response)
        
        # Llogarit statistikat
        total_latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        successful = len([r for r in responses if r.success])
        
        result = CallResult(
            call_id=request.call_id,
            query=request.query,
            scope=request.scope.value,
            total_cells=len(cells),
            successful=successful,
            failed=len(cells) - successful,
            responses=responses,
            total_latency_ms=total_latency
        )
        
        # Ruaj në histori
        self.call_history.append(result)
        if len(self.call_history) > self.max_history:
            self.call_history = self.call_history[-self.max_history:]
        
        logger.info(f"📞 Call {request.call_id}: {successful}/{len(cells)} successful in {total_latency:.2f}ms")
        
        return result
    
    def call_sync(self, query: str, scope: str = "all", scope_value: Optional[str] = None) -> CallResult:
        """
        Thirrje sinkrone (për përdorim të thjeshtë).
        """
        request = CallRequest(
            query=query,
            scope=CallScope(scope) if scope else CallScope.ALL,
            scope_value=scope_value
        )
        
        return asyncio.run(self.call(request))
    
    # =========================================================================
    # SCOPE RESOLUTION
    # =========================================================================
    
    def _resolve_scope(self, scope: CallScope, scope_value: Optional[str]) -> List[Cell]:
        """Gjen qelizat sipas scope-it."""
        
        if scope == CallScope.ALL:
            return self.registry.list_all()
        
        elif scope == CallScope.SINGLE:
            cell = self.registry.get(scope_value)
            return [cell] if cell else []
        
        elif scope == CallScope.ROLE:
            try:
                role = CellRole(scope_value)
                return self.registry.query_by_role(role)
            except ValueError:
                return []
        
        elif scope == CallScope.TAGS:
            tags = scope_value.split(",") if scope_value else []
            return self.registry.query(tags=tags)
        
        elif scope == CallScope.GRAPH_SUBSET:
            # Merr qelizat e lidhura me qelizën e specifikuar
            if scope_value:
                return self.registry.query_linked(scope_value)
            return []
        
        elif scope == CallScope.CLUSTER:
            # Merr qelizat me tag "cluster:X"
            cluster_tag = f"cluster:{scope_value}" if scope_value else None
            if cluster_tag:
                return self.registry.query(tags=[cluster_tag])
            return []
        
        return []
    
    # =========================================================================
    # CELL CALLING
    # =========================================================================
    
    async def _call_cell(self, cell: Cell, request: CallRequest) -> CallResponse:
        """Thirr një qelizë individuale."""
        start_time = datetime.now(timezone.utc)
        
        # Nëse qeliza ka handler custom
        if cell.on_call:
            try:
                result = cell.on_call(request.query, request.parameters)
                latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                return CallResponse(
                    cell_id=cell.cell_id,
                    cell_name=cell.name,
                    success=True,
                    response=result,
                    latency_ms=latency
                )
            except Exception as e:
                return CallResponse(
                    cell_id=cell.cell_id,
                    cell_name=cell.name,
                    success=False,
                    error=str(e)
                )
        
        # Nëse ka endpoint HTTP
        if cell.endpoint and cell.endpoint.startswith("http"):
            return await self._call_http(cell, request)
        
        # Nuk mund të thirret
        return CallResponse(
            cell_id=cell.cell_id,
            cell_name=cell.name,
            success=False,
            error="Cell has no call handler or HTTP endpoint"
        )
    
    async def _call_http(self, cell: Cell, request: CallRequest) -> CallResponse:
        """Thirr qelizë përmes HTTP."""
        start_time = datetime.now(timezone.utc)
        
        try:
            async with httpx.AsyncClient(timeout=request.timeout_seconds) as client:
                # Vendos URL-në e thirrjes
                url = cell.endpoint.rstrip("/")
                
                # Për query të veçanta, thirr endpoints të ndryshme
                if request.query == "health" or request.query == "report-status":
                    endpoint = cell.health_url or "/health"
                    url = f"{url}{endpoint}"
                    response = await client.get(url)
                elif request.query == "status":
                    url = f"{url}/status"
                    response = await client.get(url)
                elif request.query == "metrics":
                    url = f"{url}/metrics"
                    response = await client.get(url)
                else:
                    # POST me query dhe parametra
                    url = f"{url}/api/call"
                    response = await client.post(url, json={
                        "query": request.query,
                        "parameters": request.parameters
                    })
                
                latency = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                    except:
                        data = {"raw": response.text}
                    
                    return CallResponse(
                        cell_id=cell.cell_id,
                        cell_name=cell.name,
                        success=True,
                        response=data,
                        latency_ms=latency
                    )
                else:
                    return CallResponse(
                        cell_id=cell.cell_id,
                        cell_name=cell.name,
                        success=False,
                        error=f"HTTP {response.status_code}",
                        latency_ms=latency
                    )
        
        except httpx.TimeoutException:
            return CallResponse(
                cell_id=cell.cell_id,
                cell_name=cell.name,
                success=False,
                error="Timeout"
            )
        except Exception as e:
            return CallResponse(
                cell_id=cell.cell_id,
                cell_name=cell.name,
                success=False,
                error=str(e)
            )
    
    # =========================================================================
    # CONVENIENCE METHODS
    # =========================================================================
    
    async def broadcast(self, query: str, parameters: Optional[Dict] = None) -> CallResult:
        """Broadcast tek të gjitha qelizat."""
        request = CallRequest(
            query=query,
            scope=CallScope.ALL,
            call_type=CallType.BROADCAST,
            parameters=parameters or {}
        )
        return await self.call(request)
    
    async def call_role(self, role: str, query: str, parameters: Optional[Dict] = None) -> CallResult:
        """Thirr qelizat me një rol specifik."""
        request = CallRequest(
            query=query,
            scope=CallScope.ROLE,
            scope_value=role,
            parameters=parameters or {}
        )
        return await self.call(request)
    
    async def call_single(self, cell_id: str, query: str, parameters: Optional[Dict] = None) -> CallResult:
        """Thirr një qelizë të vetme."""
        request = CallRequest(
            query=query,
            scope=CallScope.SINGLE,
            scope_value=cell_id,
            parameters=parameters or {}
        )
        return await self.call(request)
    
    async def call_health_check(self) -> CallResult:
        """Thirr health check për të gjitha qelizat HTTP."""
        http_cells = [c for c in self.registry.list_all() 
                      if c.endpoint and c.endpoint.startswith("http")]
        
        responses = []
        for cell in http_cells:
            request = CallRequest(query="health")
            response = await self._call_http(cell, request)
            responses.append(response)
        
        successful = len([r for r in responses if r.success])
        
        return CallResult(
            call_id=f"health_{uuid.uuid4().hex[:8]}",
            query="health",
            scope="http_cells",
            total_cells=len(http_cells),
            successful=successful,
            failed=len(http_cells) - successful,
            responses=responses
        )
    
    # =========================================================================
    # CASCADE CALLING
    # =========================================================================
    
    async def cascade(self, start_cell_id: str, query: str, 
                      max_depth: int = 3, parameters: Optional[Dict] = None) -> CallResult:
        """
        Thirrje kaskadë - fillon nga një qelizë dhe përhapet tek të lidhurat.
        """
        visited = set()
        all_responses = []
        
        async def visit(cell_id: str, depth: int):
            if depth > max_depth or cell_id in visited:
                return
            
            visited.add(cell_id)
            cell = self.registry.get(cell_id)
            
            if not cell:
                return
            
            # Thirr qelizën
            request = CallRequest(query=query, parameters=parameters or {})
            response = await self._call_cell(cell, request)
            all_responses.append(response)
            
            # Vazhdo tek të lidhurat
            for linked_id in cell.links:
                await visit(linked_id, depth + 1)
        
        await visit(start_cell_id, 0)
        
        successful = len([r for r in all_responses if r.success])
        
        return CallResult(
            call_id=f"cascade_{uuid.uuid4().hex[:8]}",
            query=query,
            scope=f"cascade from {start_cell_id}",
            total_cells=len(all_responses),
            successful=successful,
            failed=len(all_responses) - successful,
            responses=all_responses
        )
    
    # =========================================================================
    # HISTORY
    # =========================================================================
    
    def get_history(self, limit: int = 10) -> List[CallResult]:
        """Merr historinë e thirrjeve."""
        return self.call_history[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Statistika të thirrjeve."""
        if not self.call_history:
            return {"total_calls": 0}
        
        total = len(self.call_history)
        total_cells = sum(r.total_cells for r in self.call_history)
        total_successful = sum(r.successful for r in self.call_history)
        avg_latency = sum(r.total_latency_ms for r in self.call_history) / total
        
        return {
            "total_calls": total,
            "total_cells_called": total_cells,
            "total_successful": total_successful,
            "total_failed": total_cells - total_successful,
            "success_rate": round(total_successful / total_cells * 100, 2) if total_cells > 0 else 0,
            "average_latency_ms": round(avg_latency, 2)
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_operator_instance: Optional[CallOperator] = None

def get_call_operator() -> CallOperator:
    """Get or create the Call Operator singleton."""
    global _operator_instance
    if _operator_instance is None:
        _operator_instance = CallOperator()
    return _operator_instance


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    operator = get_call_operator()
    
    print("=== Call Operator Test ===")
    print(f"Registry has {len(operator.registry.cells)} cells")
    
    # Test health check (requires running services)
    async def test():
        print("\nCalling health check...")
        result = await operator.call_health_check()
        print(f"Health check: {result.successful}/{result.total_cells} healthy")
        
        for r in result.responses:
            status = "✅" if r.success else "❌"
            print(f"  {status} {r.cell_name}: {r.error or 'OK'}")
        
        # Stats
        print(f"\nStats: {operator.get_stats()}")
    
    asyncio.run(test())

