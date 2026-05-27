from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib import request


PRESETS = {
    "intra_node": {
        "scenario": "intra_node",
        "target_path": "/health",
        "messages": 100,
        "timeout_ms": 1000,
        "p50_max": 150.0,
        "p95_max": 250.0,
        "p99_max": 400.0,
        "error_max": 0,
        "throughput_min": None,
        "output": "reports/benchmark-intra_node.json",
    },
    "cross_node": {
        "scenario": "cross_node",
        "target_path": "/health",
        "messages": 100,
        "timeout_ms": 1200,
        "p50_max": 200.0,
        "p95_max": 325.0,
        "p99_max": 500.0,
        "error_max": 0,
        "throughput_min": None,
        "output": "reports/benchmark-cross_node.json",
    },
    "edge_cloud": {
        "scenario": "edge_cloud",
        "target_path": "/health",
        "messages": 100,
        "timeout_ms": 1500,
        "p50_max": 300.0,
        "p95_max": 500.0,
        "p99_max": 700.0,
        "error_max": 0,
        "throughput_min": None,
        "output": "reports/benchmark-edge_cloud.json",
    },
}


def post_json(url: str, payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run benchmark gate against kloud benchmark API"
    )
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--preset", choices=sorted(PRESETS.keys()), default=None)
    parser.add_argument("--target-url", default="")
    parser.add_argument("--scenario", default="")
    parser.add_argument("--messages", type=int, default=None)
    parser.add_argument("--timeout-ms", type=int, default=None)
    parser.add_argument("--p50-max", type=float, default=None)
    parser.add_argument("--p95-max", type=float, default=None)
    parser.add_argument("--p99-max", type=float, default=None)
    parser.add_argument("--error-max", type=int, default=None)
    parser.add_argument("--throughput-min", type=float, default=None)
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    preset = PRESETS.get(args.preset, {})
    scenario = args.scenario or preset.get("scenario") or "intra_node"
    target_url = args.target_url or (
        f"{args.base_url.rstrip('/')}{preset.get('target_path', '/health')}"
    )
    messages = (
        args.messages if args.messages is not None else preset.get("messages", 100)
    )
    timeout_ms = (
        args.timeout_ms
        if args.timeout_ms is not None
        else preset.get("timeout_ms", 1000)
    )
    p50_max = args.p50_max if args.p50_max is not None else preset.get("p50_max")
    p95_max = args.p95_max if args.p95_max is not None else preset.get("p95_max")
    p99_max = args.p99_max if args.p99_max is not None else preset.get("p99_max")
    error_max = (
        args.error_max if args.error_max is not None else preset.get("error_max", 0)
    )
    throughput_min = (
        args.throughput_min
        if args.throughput_min is not None
        else preset.get("throughput_min")
    )
    output = args.output or preset.get("output", "")

    run_payload = {
        "test_name": scenario,
        "messages": messages,
        "target_url": target_url,
        "timeout_ms": timeout_ms,
        "method": "GET",
    }
    thresholds = {
        "p50_ms_max": p50_max,
        "p95_ms_max": p95_max,
        "p99_ms_max": p99_max,
        "error_count_max": error_max,
        "throughput_min": throughput_min,
    }

    run_response = post_json(
        f"{args.base_url.rstrip('/')}/v1/benchmarks/run", run_payload
    )
    result = run_response["result"]
    evaluation_response = post_json(
        f"{args.base_url.rstrip('/')}/v1/benchmarks/evaluate",
        {"result": result, "thresholds": thresholds},
    )
    evaluation = evaluation_response["evaluation"]

    report = {"result": result, "evaluation": evaluation}
    encoded = json.dumps(report, indent=2)
    if output:
        output_path = Path(str(output))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(encoded, encoding="utf-8")
    print(encoded)
    return 0 if evaluation["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
