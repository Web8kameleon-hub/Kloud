#!/usr/bin/env python3
"""
ALDA - Artificial Labor Determined Array
Intelligent Labor Allocation & Determination System

Sistemi për përcaktimin dhe alokimin e punës artificiale
në rrjetin e laboratorëve dhe burimeve të të dhënave.
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import cbor2
import msgpack
from fastapi import FastAPI, Request, Response
import uvicorn
import os
from cors_policy import apply_standard_cors
from fluid_runtime import activate_wwwmmm_fluid

activate_wwwmmm_fluid()

# API Version
API_V1 = "/api/v1"
PORT = int(os.getenv("ALDA_PORT", "8063"))

app = FastAPI(
    title="ALDA - Artificial Labor Determined Array",
    description="Intelligent Labor Allocation & Determination System",
    version="1.0.0",
)

apply_standard_cors(app)


# ═══════════════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════


class LaborPriority(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    BACKGROUND = 1


class LaborType(Enum):
    COMPUTE = "compute"
    ANALYSIS = "analysis"
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"
    LEARNING = "learning"


@dataclass
class LaborTask:
    task_id: str
    labor_type: LaborType
    priority: LaborPriority
    complexity: float  # 0.0 - 1.0
    required_capacity: float
    assigned_lab: Optional[str] = None
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        return {
            "task_id": self.task_id,
            "labor_type": self.labor_type.value,
            "priority": self.priority.value,
            "complexity": self.complexity,
            "required_capacity": self.required_capacity,
            "assigned_lab": self.assigned_lab,
            "status": self.status,
            "created_at": self.created_at,
        }


@dataclass
class LaborCapacity:
    lab_id: str
    total_capacity: float
    used_capacity: float
    efficiency: float  # 0.0 - 1.0
    specializations: List[str]

    @property
    def available_capacity(self) -> float:
        return self.total_capacity - self.used_capacity

    @property
    def utilization(self) -> float:
        return (
            self.used_capacity / self.total_capacity if self.total_capacity > 0 else 0
        )

    def to_dict(self) -> Dict:
        return {
            "lab_id": self.lab_id,
            "total_capacity": self.total_capacity,
            "used_capacity": self.used_capacity,
            "available_capacity": self.available_capacity,
            "utilization": self.utilization,
            "efficiency": self.efficiency,
            "specializations": self.specializations,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ALDA CORE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════


class ALDAEngine:
    """
    Artificial Labor Determined Array Engine

    Përdor matrica për të përcaktuar alokimin optimal të punës
    bazuar në kapacitet, prioritet dhe efikasitet.
    """

    def __init__(self) -> None:
        # 23 Labs from Kloud Network
        self.labs = [
            "Elbasan",
            "Tirana",
            "Durrës",
            "Shkodër",
            "Vlorë",
            "Korçë",
            "Sarandë",
            "Kostur",
            "Preshrink",
            "Rome",
            "Vienna",
            "Athens",
            "Sofia",
            "Istanbul",
            "Ljubljana",
            "Zagreb",
            "Beograd",
            "Budapest",
            "Bucharest",
            "Prague",
            "Jerusalem",
            "Cairo",
            "Zürich",
        ]

        # Initialize capacity matrix: [labs x labor_types]
        self.capacity_matrix = np.random.uniform(0.5, 1.0, (23, 5))
        self.efficiency_vector = np.random.uniform(0.7, 0.95, 23)
        self.utilization_vector = np.random.uniform(0.2, 0.7, 23)

        # Priority weight matrix
        self.priority_weights = np.array(
            [0.1, 0.2, 0.4, 0.7, 1.0]
        )  # BACKGROUND to CRITICAL

        # Task queue
        self.task_queue: List[LaborTask] = []
        self.completed_tasks: List[LaborTask] = []

        # Lab specializations
        self.specializations = {
            "Elbasan": ["compute", "analysis"],
            "Tirana": ["synthesis", "validation"],
            "Zürich": ["learning", "analysis", "compute"],
            "Vienna": ["validation", "synthesis"],
            "Rome": ["compute", "learning"],
            "Athens": ["analysis", "synthesis"],
            "Jerusalem": ["validation", "learning"],
            "Cairo": ["compute", "analysis"],
            "Prague": ["synthesis", "compute"],
            "Budapest": ["learning", "validation"],
        }

    def compute_allocation_matrix(self, tasks: List[LaborTask]) -> np.ndarray:
        """
        Compute optimal allocation matrix.
        No loops - pure matrix operations.

        Returns: allocation_matrix[tasks x labs] with allocation scores
        """
        n_tasks = len(tasks)
        n_labs = len(self.labs)

        if n_tasks == 0:
            return np.zeros((0, n_labs))

        # Build task requirement vector
        task_priorities = np.array([t.priority.value for t in tasks])
        task_capacities = np.array([t.required_capacity for t in tasks])

        # Availability matrix: [labs]
        availability = 1.0 - self.utilization_vector

        # Score matrix: [tasks x labs]
        # Higher score = better match

        # Priority contribution: broadcast task priorities to all labs
        priority_contribution = task_priorities.reshape(-1, 1) * self.priority_weights[
            task_priorities - 1
        ].reshape(-1, 1)

        # Efficiency contribution: broadcast lab efficiency to all tasks
        efficiency_contribution = self.efficiency_vector.reshape(1, -1) * np.ones(
            (n_tasks, 1)
        )

        # Availability contribution
        availability_contribution = availability.reshape(1, -1) * np.ones((n_tasks, 1))

        # Capacity match: how well lab capacity matches task requirement
        capacity_match = 1.0 - np.abs(
            task_capacities.reshape(-1, 1)
            - (1.0 - self.utilization_vector.reshape(1, -1))
        )
        capacity_match = np.clip(capacity_match, 0, 1)

        # Combined allocation score
        allocation_matrix = (
            0.3 * priority_contribution
            + 0.25 * efficiency_contribution
            + 0.25 * availability_contribution
            + 0.2 * capacity_match
        )

        return allocation_matrix

    def determine_assignments(self, allocation_matrix: np.ndarray) -> List[int]:
        """
        Determine optimal lab assignment for each task.
        Uses argmax - no loops.

        Returns: list of lab indices for each task
        """
        if allocation_matrix.size == 0:
            return []

        # Simple greedy: assign each task to best available lab
        assignments = np.argmax(allocation_matrix, axis=1)
        return assignments.tolist()

    def add_task(
        self,
        task_id: str,
        labor_type: str,
        priority: int,
        complexity: float,
        required_capacity: float,
    ) -> LaborTask:
        """Add a new labor task"""
        task = LaborTask(
            task_id=task_id,
            labor_type=LaborType(labor_type),
            priority=LaborPriority(priority),
            complexity=complexity,
            required_capacity=required_capacity,
        )
        self.task_queue.append(task)
        return task

    def process_queue(self) -> List[Dict]:
        """Process all pending tasks and assign to labs"""
        pending = [t for t in self.task_queue if t.status == "pending"]

        if not pending:
            return []

        # Compute allocation
        allocation_matrix = self.compute_allocation_matrix(pending)
        assignments = self.determine_assignments(allocation_matrix)

        results = []
        for task, lab_idx in zip(pending, assignments):
            task.assigned_lab = self.labs[lab_idx]
            task.status = "assigned"

            # Update utilization
            self.utilization_vector[lab_idx] = min(
                1.0, self.utilization_vector[lab_idx] + task.required_capacity * 0.1
            )

            results.append(
                {
                    "task_id": task.task_id,
                    "assigned_lab": task.assigned_lab,
                    "allocation_score": float(
                        allocation_matrix[pending.index(task), lab_idx]
                    ),
                }
            )

        return results

    def get_lab_status(self) -> List[Dict]:
        """Get status of all labs"""
        return [
            {
                "lab": self.labs[i],
                "efficiency": float(self.efficiency_vector[i]),
                "utilization": float(self.utilization_vector[i]),
                "available": float(1.0 - self.utilization_vector[i]),
                "specializations": self.specializations.get(self.labs[i], []),
            }
            for i in range(len(self.labs))
        ]

    def get_network_metrics(self) -> Dict:
        """Get overall network metrics"""
        return {
            "total_labs": len(self.labs),
            "avg_efficiency": float(self.efficiency_vector.mean()),
            "avg_utilization": float(self.utilization_vector.mean()),
            "total_available_capacity": float((1.0 - self.utilization_vector).sum()),
            "pending_tasks": len([t for t in self.task_queue if t.status == "pending"]),
            "assigned_tasks": len(
                [t for t in self.task_queue if t.status == "assigned"]
            ),
            "completed_tasks": len(self.completed_tasks),
        }


# Global engine instance
alda_engine = ALDAEngine()


# ═══════════════════════════════════════════════════════════════════════════════
# BINARY PROTOCOL
# ═══════════════════════════════════════════════════════════════════════════════


def encode_response(data: Dict, fmt: str = "cbor") -> bytes:
    if fmt == "msgpack":
        packed = msgpack.packb(data, use_bin_type=True)
        if isinstance(packed, (bytes, bytearray)):
            return bytes(packed)
        raise TypeError("msgpack.packb returned non-bytes payload")
    return cbor2.dumps(data)


def decode_request(body: bytes, fmt: str = "cbor") -> Dict:
    if fmt == "msgpack":
        return msgpack.unpackb(body, raw=False)
    return cbor2.loads(body)


# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ALDA",
        "timestamp": datetime.now().isoformat(),
    }


@app.get(API_V1 + "/status")
async def api_status():
    return {
        "service": "ALDA - Artificial Labor Determined Array",
        "version": "1.0.0",
        "status": "operational",
        "labs_count": len(alda_engine.labs),
        "timestamp": datetime.now().isoformat(),
    }


@app.get(API_V1 + "/spec")
async def api_spec():
    return app.openapi()


@app.get(API_V1 + "/info")
async def info():
    return {
        "name": "ALDA",
        "full_name": "Artificial Labor Determined Array",
        "version": "1.0.0",
        "description": "Intelligent Labor Allocation & Determination System",
        "features": [
            "Matrix-based labor allocation",
            "Priority-weighted assignments",
            "Efficiency tracking",
            "23-lab network integration",
            "Binary protocol support",
        ],
        "labs_count": len(alda_engine.labs),
        "labor_types": [lt.value for lt in LaborType],
        "timestamp": datetime.now().isoformat(),
    }


@app.get(API_V1 + "/labs")
async def get_labs():
    """Get all labs status"""
    return {
        "labs": alda_engine.get_lab_status(),
        "count": len(alda_engine.labs),
        "timestamp": datetime.now().isoformat(),
    }


@app.get(API_V1 + "/metrics")
async def get_metrics():
    """Get network metrics"""
    metrics = alda_engine.get_network_metrics()
    metrics["timestamp"] = datetime.now().isoformat()
    return metrics


@app.post(API_V1 + "/task")
async def add_task(
    task_id: str,
    labor_type: str = "compute",
    priority: int = 3,
    complexity: float = 0.5,
    required_capacity: float = 0.1,
):
    """Add a new labor task"""
    task = alda_engine.add_task(
        task_id, labor_type, priority, complexity, required_capacity
    )
    return {
        "task": task.to_dict(),
        "message": "Task added to queue",
        "timestamp": datetime.now().isoformat(),
    }


@app.post(API_V1 + "/process")
async def process_queue():
    """Process pending tasks and assign to labs"""
    results = alda_engine.process_queue()
    return {
        "assignments": results,
        "count": len(results),
        "timestamp": datetime.now().isoformat(),
    }


@app.get(API_V1 + "/queue")
async def get_queue():
    """Get current task queue"""
    return {
        "tasks": [t.to_dict() for t in alda_engine.task_queue],
        "pending": len([t for t in alda_engine.task_queue if t.status == "pending"]),
        "assigned": len([t for t in alda_engine.task_queue if t.status == "assigned"]),
        "timestamp": datetime.now().isoformat(),
    }


@app.post(API_V1 + "/bin/allocate")
async def binary_allocate(request: Request):
    """Binary allocation endpoint"""
    body = await request.body()
    content_type = request.headers.get("content-type", "application/cbor")

    fmt = "msgpack" if "msgpack" in content_type else "cbor"
    data = decode_request(body, fmt)

    # Add tasks from binary request
    tasks_data = data.get("tasks", [])
    for t in tasks_data:
        alda_engine.add_task(
            t.get("task_id", f"task_{len(alda_engine.task_queue)}"),
            t.get("labor_type", "compute"),
            t.get("priority", 3),
            t.get("complexity", 0.5),
            t.get("required_capacity", 0.1),
        )

    # Process and return assignments
    results = alda_engine.process_queue()

    response = {
        "assignments": results,
        "count": len(results),
        "timestamp": datetime.now().isoformat(),
    }

    return Response(
        content=encode_response(response, fmt), media_type=f"application/{fmt}"
    )


@app.get(API_V1 + "/allocation/matrix")
async def get_allocation_matrix():
    """Get current allocation matrix for pending tasks"""
    pending = [t for t in alda_engine.task_queue if t.status == "pending"]

    if not pending:
        return {
            "message": "No pending tasks",
            "matrix": [],
            "timestamp": datetime.now().isoformat(),
        }

    matrix = alda_engine.compute_allocation_matrix(pending)

    return {
        "matrix": matrix.tolist(),
        "tasks": [t.task_id for t in pending],
        "labs": alda_engine.labs,
        "shape": list(matrix.shape),
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    print("🤖 ALDA - Artificial Labor Determined Array")
    print("   Intelligent Labor Allocation System")
    print(f"   Port: {PORT}")
    print(f"   Labs: {len(alda_engine.labs)}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
