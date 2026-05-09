"""
brain_analyzer.py
-----------------
Kloud Cognitive Health Analyzer

Kjo njÃ«si analizon dhe vlerÃ«son gjendjen e arkitekturÃ«s kognitive
nÃ« bazÃ« tÃ« metrikave tÃ« performancÃ«s, stabilitetit dhe ngarkesÃ«s neuronale.
"""

from datetime import datetime
import psutil
import random
import math


class BrainAnalyzer:
    """Analizon metrikat e trurit sintetik (Cognitive Health Metrics)."""

    def __init__(self, center_name: str = "Default-Center"):
        self.center_name = center_name
        self.start_time = datetime.utcnow()

    def get_system_metrics(self) -> dict:
        """Lexon metrikat bazÃ« tÃ« sistemit."""
        cpu = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        temp = random.uniform(32.0, 42.0)  # simulim temp. neurale
        load_factor = round(math.sqrt(cpu * memory) / 10, 2)

        return {
            "cpu": cpu,
            "memory": memory,
            "disk": disk,
            "temperature_c": temp,
            "load_factor": load_factor,
        }

    def compute_cognitive_health(self) -> dict:
        """Llogarit njÃ« indeks tÃ« pÃ«rgjithshÃ«m tÃ« 'shÃ«ndetit kognitiv'."""
        metrics = self.get_system_metrics()

        stability = max(0.0, 1.0 - metrics["load_factor"] / 10)
        focus = max(0.0, 1.0 - metrics["memory"] / 100)
        neural_efficiency = (stability + focus) / 2

        health_score = round(neural_efficiency * 100, 2)
        status = "optimal" if health_score > 85 else "stable" if health_score > 60 else "degraded"

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "center": self.center_name,
            "health_score": health_score,
            "status": status,
            "stability": round(stability, 3),
            "focus": round(focus, 3),
            "metrics": metrics,
        }


# ðŸ”§ Shembull pÃ«rdorimi (mund ta testosh me `python brain_analyzer.py`)
if __name__ == "__main__":
    analyzer = BrainAnalyzer(center_name="Zurich-Lab")
    result = analyzer.compute_cognitive_health()
    print("ðŸ§  Cognitive Health Snapshot:")
    print(result)


