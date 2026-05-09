# -*- coding: utf-8 -*-
"""
Mesh Cluster Startup Script
Industrial Launcher for:
 - Distributed Pulse Balancer
 - Kloud Integrated System
 - Mesh HQ Receiver

Business: Ledjan Ahmati - WEB8euroweb GmbH
REAL LAUNCHER â€¢ NO MOCK â€¢ NO RANDOM â€¢ NO PLACEHOLDER
"""

from datetime import datetime
from pathlib import Path
import os
import sys
import signal
import subprocess
import time
from typing import Dict

import psutil

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "apps" / "api"))

try:
    from Kloud.colored_logger import setup_logger
except ImportError:
    # Fallback logger if module not found
    import logging
    def setup_logger(name):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')
        return logging.getLogger(name)

BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
os.makedirs(LOGS_DIR, exist_ok=True)


logger = setup_logger("KloudCluster")


def launch_process(name: str, command: list[str], logfile: Path) -> subprocess.Popen:
    """Start a process and stream stdout/stderr to the provided logfile."""

    logger.info("Launching %s ...", name)
    logfile.parent.mkdir(parents=True, exist_ok=True)
    handle = open(logfile, "a", encoding="utf-8")
    handle.write(f"\n\n=== {datetime.utcnow().isoformat()} START {name} ===\n")

    creation_flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)

    return subprocess.Popen(
        command,
        stdout=handle,
        stderr=handle,
        cwd=BASE_DIR,
        creationflags=creation_flags,
    )


def monitor_processes(processes: Dict[str, subprocess.Popen]) -> None:
    """Continuously print process health and resource usage."""

    try:
        while True:
            logger.info("--- CLUSTER STATUS ---")
            for name, proc in processes.items():
                alive = proc.poll() is None
                cpu_percent = 0.0
                mem_percent = 0.0

                if alive:
                    try:
                        ps_proc = psutil.Process(proc.pid)
                        cpu_percent = ps_proc.cpu_percent() / max(psutil.cpu_count(logical=True) or 1, 1)
                        mem_percent = ps_proc.memory_percent()
                    except psutil.NoSuchProcess:
                        alive = False

                status = "ðŸŸ¢ RUNNING" if alive else "ðŸ”´ STOPPED"
                logger.info(
                    "%s | PID %s | %s | CPU %.1f%% | MEM %.1f%%",
                    f"{name:<25}",
                    proc.pid,
                    status,
                    cpu_percent,
                    mem_percent,
                )
            logger.info("----------------------")
            time.sleep(10)
    except KeyboardInterrupt:
        logger.info("Shutdown signal received.")
        for name, proc in processes.items():
            if proc.poll() is None:
                logger.info("Stopping %s ...", name)
                try:
                    os.kill(proc.pid, signal.SIGTERM)
                except Exception:
                    pass
        logger.info("All processes stopped.")


if __name__ == "__main__":
    balancer_file = BASE_DIR / "distributed_pulse_balancer.py"
    integrated_file = BASE_DIR / "Kloud_integrated_system.py"
    mesh_file = BASE_DIR / "mesh_hq_receiver.py"

    processes: Dict[str, subprocess.Popen] = {}

    processes["Distributed Pulse Balancer"] = launch_process(
        "Distributed Pulse Balancer",
        ["python", str(balancer_file)],
        LOGS_DIR / "balancer_run.log",
    )

    time.sleep(3)

    processes["Kloud Integrated System"] = launch_process(
        "Kloud Integrated System",
        ["python", str(integrated_file)],
        LOGS_DIR / "integrated_run.log",
    )

    time.sleep(2)

    processes["Mesh HQ Receiver"] = launch_process(
        "Mesh HQ Receiver",
        ["python", str(mesh_file)],
        LOGS_DIR / "mesh_run.log",
    )

    logger.info("All cluster services launched successfully.")
    logger.info("Press CTRL+C to stop all.")
    monitor_processes(processes)


