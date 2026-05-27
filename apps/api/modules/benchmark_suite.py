from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(tags=["benchmark-suite"])

Scenario = Literal[
    "intra_node",
    "cross_node",
    "edge_cloud",
    "burst",
    "sustained",
    "chaos",
]


class BenchmarkRequest(BaseModel):
    test_name: Scenario
    messages: int = Field(default=100, ge=10, le=200000)
    target_url: str
    timeout_ms: int = Field(default=3000, ge=100, le=60000)
    method: Literal["GET", "POST"] = "GET"
    chaos_delay_ms: int = Field(default=0, ge=0, le=2000)


class BenchmarkResult(BaseModel):
    test_name: str
    messages: int
    p50_ms: float
    p95_ms: float
    p99_ms: float
    throughput_msg_sec: float
    errors: int
    timestamp: str


class BenchmarkThresholds(BaseModel):
    p50_ms_max: float | None = Field(default=None, ge=0.0)
    p95_ms_max: float | None = Field(default=None, ge=0.0)
    p99_ms_max: float | None = Field(default=None, ge=0.0)
    error_count_max: int | None = Field(default=None, ge=0)
    throughput_min: float | None = Field(default=None, ge=0.0)


class BenchmarkEvaluateRequest(BaseModel):
    result: BenchmarkResult
    thresholds: BenchmarkThresholds


def _percentile(sorted_values: List[float], p: float) -> float:
    if not sorted_values:
        return 0.0
    k = (len(sorted_values) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    if f == c:
        return sorted_values[f]
    d0 = sorted_values[f] * (c - k)
    d1 = sorted_values[c] * (k - f)
    return d0 + d1


def evaluate_thresholds(
    result: BenchmarkResult, thresholds: BenchmarkThresholds
) -> Dict[str, Any]:
    failures: List[str] = []
    if thresholds.p50_ms_max is not None and result.p50_ms > thresholds.p50_ms_max:
        failures.append(f"p50_ms>{thresholds.p50_ms_max}")
    if thresholds.p95_ms_max is not None and result.p95_ms > thresholds.p95_ms_max:
        failures.append(f"p95_ms>{thresholds.p95_ms_max}")
    if thresholds.p99_ms_max is not None and result.p99_ms > thresholds.p99_ms_max:
        failures.append(f"p99_ms>{thresholds.p99_ms_max}")
    if (
        thresholds.error_count_max is not None
        and result.errors > thresholds.error_count_max
    ):
        failures.append(f"errors>{thresholds.error_count_max}")
    if (
        thresholds.throughput_min is not None
        and result.throughput_msg_sec < thresholds.throughput_min
    ):
        failures.append(f"throughput<{thresholds.throughput_min}")
    return {
        "passed": len(failures) == 0,
        "failures": failures,
    }


@router.post("/v1/benchmarks/run")
async def run_benchmark(payload: BenchmarkRequest):
    latencies_ms: List[float] = []
    errors = 0
    started = time.perf_counter()

    timeout = payload.timeout_ms / 1000.0
    async with httpx.AsyncClient(timeout=timeout) as client:
        for _ in range(payload.messages):
            tick = time.perf_counter()
            try:
                if payload.chaos_delay_ms > 0 and payload.test_name == "chaos":
                    await _sleep_ms(payload.chaos_delay_ms)

                if payload.method == "GET":
                    response = await client.get(payload.target_url)
                else:
                    response = await client.post(
                        payload.target_url, json={"benchmark": True}
                    )

                if response.status_code >= 400:
                    errors += 1
            except Exception:
                errors += 1
            finally:
                latencies_ms.append((time.perf_counter() - tick) * 1000.0)

    elapsed = max(time.perf_counter() - started, 0.000001)
    sorted_latencies = sorted(latencies_ms)

    result = BenchmarkResult(
        test_name=payload.test_name,
        messages=payload.messages,
        p50_ms=round(_percentile(sorted_latencies, 0.50), 3),
        p95_ms=round(_percentile(sorted_latencies, 0.95), 3),
        p99_ms=round(_percentile(sorted_latencies, 0.99), 3),
        throughput_msg_sec=round(payload.messages / elapsed, 3),
        errors=errors,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    return {"ok": True, "result": result.model_dump()}


@router.get("/v1/benchmarks/targets")
def benchmark_targets() -> Dict[str, Any]:
    return {
        "ok": True,
        "targets": {
            "intra_node": {
                "default": "http://127.0.0.1:8000/health",
                "notes": "Run locally against same-node API",
            },
            "cross_node": {
                "default": "http://127.0.0.1:5555/health",
                "notes": "Set to another node in same PoP",
            },
            "edge_cloud": {
                "default": "http://127.0.0.1:8000/health",
                "notes": "Set to cloud ingress endpoint",
            },
        },
    }


@router.post("/v1/benchmarks/evaluate")
def benchmark_evaluate(payload: BenchmarkEvaluateRequest) -> Dict[str, Any]:
    evaluation = evaluate_thresholds(payload.result, payload.thresholds)
    return {
        "ok": True,
        "evaluation": evaluation,
        "result": payload.result.model_dump(),
    }


async def _sleep_ms(delay_ms: int) -> None:
    if delay_ms <= 0:
        return
    # Real wait used only when chaos scenario is explicitly requested.
    await asyncio.sleep(delay_ms / 1000.0)
