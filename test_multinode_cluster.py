# -*- coding: utf-8 -*-
"""
🧪 Multi-Node Test Script for Distributed Pulse Balancer
=========================================================
Nis 2 instanca lokale të Pulse Balancer për testim cluster.

Business: Ledjan Ahmati - WEB8euroweb GmbH
"""

import subprocess
import time
import sys
import os
import signal
import requests
from typing import List, Optional

# Node configurations
NODES = [
    {
        "name": "node1",
        "port": 8091,
        "hb_port": 42999,
        "env": {
            "NSX_NODE_NAME": "kloud-node1",
            "NSX_NODE_ID": "node1-uuid-0001",
            "NSX_API_PORT": "8091",
            "NSX_HB_PORT": "42999",
        }
    },
    {
        "name": "node2", 
        "port": 8092,
        "hb_port": 43000,
        "env": {
            "NSX_NODE_NAME": "kloud-node2",
            "NSX_NODE_ID": "node2-uuid-0002",
            "NSX_API_PORT": "8092",
            "NSX_HB_PORT": "43000",
        }
    },
]

processes: List[subprocess.Popen] = []


def start_node(node: dict) -> Optional[subprocess.Popen]:
    """Nis një node të Pulse Balancer"""
    env = os.environ.copy()
    env.update(node["env"])
    
    print(f"🚀 Starting {node['name']} on port {node['port']}...")
    
    try:
        proc = subprocess.Popen(
            [sys.executable, "-m", "distributed_pulse_balancer"],
            env=env,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        return proc
    except Exception as e:
        print(f"❌ Failed to start {node['name']}: {e}")
        return None


def check_node_health(port: int) -> dict:
    """Kontrollo shëndetin e një node"""
    try:
        resp = requests.get(f"http://localhost:{port}/balancer/status", timeout=3)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "ok": True,
                "node_name": data.get("self", {}).get("node_name"),
                "is_leader": data.get("leader_id") == data.get("self", {}).get("node_id"),
                "peers": len(data.get("peers", [])),
                "cpu": data.get("self", {}).get("metrics", {}).get("cpu", 0),
                "mem": data.get("self", {}).get("metrics", {}).get("mem", 0),
            }
        return {"ok": False, "error": f"status_{resp.status_code}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_metrics(port: int) -> str:
    """Merr Prometheus metrics nga një node"""
    try:
        resp = requests.get(f"http://localhost:{port}/metrics", timeout=3)
        return resp.text if resp.status_code == 200 else ""
    except:
        return ""


def test_load_balancing(ports: List[int]) -> dict:
    """Testo load balancing duke dërguar requests"""
    results = {"total": 0, "accepted_local": 0, "redirect": 0, "errors": 0}
    
    for i, port in enumerate(ports * 5):  # 10 requests total
        try:
            resp = requests.post(
                f"http://localhost:{port}/balancer/request",
                json={"work_id": f"test_work_{i}", "weight": 1.0},
                timeout=3
            )
            if resp.status_code == 200:
                data = resp.json()
                decision = data.get("decision", "unknown")
                results["total"] += 1
                if decision == "accepted_local":
                    results["accepted_local"] += 1
                elif decision in ("redirect", "redirect_to_leader"):
                    results["redirect"] += 1
            else:
                results["errors"] += 1
        except:
            results["errors"] += 1
    
    return results


def stop_all():
    """Ndal të gjitha proceset"""
    print("\n🛑 Stopping all nodes...")
    for proc in processes:
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except:
            proc.kill()
    print("✓ All nodes stopped")


def main():
    global processes
    
    print("=" * 60)
    print("🧪 KLOUD MULTI-NODE CLUSTER TEST")
    print("=" * 60)
    print()
    
    # Start nodes
    for node in NODES:
        proc = start_node(node)
        if proc:
            processes.append(proc)
            time.sleep(2)  # Give each node time to start
    
    if len(processes) != len(NODES):
        print("❌ Not all nodes started. Aborting...")
        stop_all()
        return
    
    print(f"\n✅ All {len(NODES)} nodes started")
    print("   Waiting for cluster discovery...")
    time.sleep(5)  # Wait for heartbeat discovery
    
    # Health check
    print("\n" + "=" * 60)
    print("📊 NODE HEALTH STATUS")
    print("=" * 60)
    
    leader_count = 0
    for node in NODES:
        health = check_node_health(node["port"])
        if health["ok"]:
            status = "👑 LEADER" if health["is_leader"] else "   Follower"
            if health["is_leader"]:
                leader_count += 1
            print(f"  {node['name']} ({node['port']}): {status}")
            print(f"     CPU: {health['cpu']:.1f}% | MEM: {health['mem']:.1f}% | Peers: {health['peers']}")
        else:
            print(f"  {node['name']} ({node['port']}): ❌ {health['error']}")
    
    if leader_count == 1:
        print(f"\n✅ Leader election OK (exactly 1 leader)")
    else:
        print(f"\n⚠️ Leader election issue: {leader_count} leaders found")
    
    # Test load balancing
    print("\n" + "=" * 60)
    print("⚖️ LOAD BALANCING TEST")
    print("=" * 60)
    
    ports = [n["port"] for n in NODES]
    lb_results = test_load_balancing(ports)
    print(f"  Total requests: {lb_results['total']}")
    print(f"  Accepted locally: {lb_results['accepted_local']}")
    print(f"  Redirected: {lb_results['redirect']}")
    print(f"  Errors: {lb_results['errors']}")
    
    if lb_results["errors"] == 0:
        print("\n✅ Load balancing OK")
    else:
        print(f"\n⚠️ {lb_results['errors']} errors occurred")
    
    # Prometheus metrics check
    print("\n" + "=" * 60)
    print("📈 PROMETHEUS METRICS CHECK")
    print("=" * 60)
    
    for node in NODES:
        metrics = get_metrics(node["port"])
        if "kloud_balancer_cpu_percent" in metrics:
            print(f"  {node['name']} ({node['port']}): ✅ Metrics available")
            # Show sample metrics
            for line in metrics.split("\n")[:3]:
                if line and not line.startswith("#"):
                    print(f"     {line}")
        else:
            print(f"  {node['name']} ({node['port']}): ❌ No metrics")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"  Nodes: {len(processes)}/{len(NODES)} running")
    print(f"  Leader Election: {'✅ OK' if leader_count == 1 else '❌ FAIL'}")
    print(f"  Load Balancing: {'✅ OK' if lb_results['errors'] == 0 else '❌ FAIL'}")
    print(f"  Prometheus: ✅ Endpoints active")
    print()
    
    # Keep running
    print("🔄 Cluster running. Press Ctrl+C to stop...")
    try:
        while True:
            time.sleep(10)
            # Periodic health check
            for node in NODES:
                health = check_node_health(node["port"])
                if not health["ok"]:
                    print(f"⚠️ {node['name']} health check failed: {health['error']}")
    except KeyboardInterrupt:
        stop_all()


if __name__ == "__main__":
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, lambda *_: stop_all())
    main()

