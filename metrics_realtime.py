import psutil
import datetime
import requests
import json
import os
from typing import Dict, List
import subprocess
import socket

class KloudRealMetrics:
    def __init__(self):
        self.start_time = datetime.datetime.utcnow()
        
    def get_system_metrics(self) -> Dict:
        """Metrika reale tÃ« sistemit pa fake data"""
        try:
            # CPU me procese aktuale
            cpu_per_core = psutil.cpu_percent(percpu=True)
            cpu_processes = len(psutil.pids())
            
            # Memory me breakdown
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk I/O real
            disk_io = psutil.disk_io_counters()
            disk_usage = psutil.disk_usage('/')
            
            # Network me interface specifik
            net_io = psutil.net_io_counters()
            network_interfaces = self.get_network_interfaces()
            
            # Temperatura nÃ«se Ã«shtÃ« e mundur
            temperatures = self.get_temperatures()
            
            # Proceset e Kloud
            Kloud_processes = self.get_Kloud_processes()
            
            return {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "system": {
                    "cpu": {
                        "total_usage_percent": round(psutil.cpu_percent(interval=0.1), 2),
                        "per_core_usage": [round(core, 2) for core in cpu_per_core],
                        "process_count": cpu_processes,
                        "load_avg": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
                    },
                    "memory": {
                        "total_gb": round(memory.total / (1024**3), 2),
                        "used_gb": round(memory.used / (1024**3), 2),
                        "used_percent": round(memory.percent, 2),
                        "available_gb": round(memory.available / (1024**3), 2),
                        "swap_used_percent": round(swap.percent, 2) if swap else 0
                    },
                    "disk": {
                        "total_gb": round(disk_usage.total / (1024**3), 2),
                        "used_gb": round(disk_usage.used / (1024**3), 2),
                        "used_percent": round(disk_usage.percent, 2),
                        "read_mb": round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0,
                        "write_mb": round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0
                    },
                    "network": {
                        "bytes_sent_mb": round(net_io.bytes_sent / (1024**2), 2),
                        "bytes_recv_mb": round(net_io.bytes_recv / (1024**2), 2),
                        "interfaces": network_interfaces
                    },
                    "temperatures": temperatures,
                    "uptime_seconds": round((datetime.datetime.utcnow() - self.start_time).total_seconds(), 2)
                },
                "Kloud": {
                    "process_count": len(Kloud_processes),
                    "processes": Kloud_processes,
                    "alba_status": self.check_alba_status(),
                    "asi_status": self.check_asi_status(),
                    "api_endpoints_active": self.check_api_endpoints()
                },
                "health_score": self.calculate_health_score()
            }
            
        except Exception as e:
            return {
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                "error": f"Metrics collection failed: {str(e)}",
                "health_score": 0
            }

    def get_network_interfaces(self) -> List[Dict]:
        """Kthen statistikat reale tÃ« interface-ve tÃ« rrjetit"""
        interfaces = []
        try:
            for interface, addrs in psutil.net_if_addrs().items():
                stats = psutil.net_if_stats().get(interface)
                io_counters = psutil.net_io_counters(pernic=True).get(interface)
                
                interfaces.append({
                    "interface": interface,
                    "is_up": stats.isup if stats else False,
                    "speed_mbps": stats.speed if stats else 0,
                    "bytes_sent_mb": round(io_counters.bytes_sent / (1024**2), 2) if io_counters else 0,
                    "bytes_recv_mb": round(io_counters.bytes_recv / (1024**2), 2) if io_counters else 0
                })
        except:
            pass
        return interfaces

    def get_temperatures(self) -> Dict:
        """Merr temperaturat e sensorÃ«ve nÃ«se janÃ« tÃ« disponueshme"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                return {
                    "cpu": temps.get('coretemp', [{}])[0].current if 'coretemp' in temps else None,
                    "available_sensors": list(temps.keys())
                }
        except:
            pass
        return {"available_sensors": []}

    def get_Kloud_processes(self) -> List[Dict]:
        """Gjen proceset aktive tÃ« Kloud"""
        Kloud_processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    proc_info = proc.info
                    # Kontrollo nÃ«se Ã«shtÃ« proces Kloud
                    if any(keyword in proc_info['name'].lower() for keyword in 
                          ['python', 'Kloud', 'alba', 'asi', 'fastapi', 'uvicorn']):
                        Kloud_processes.append({
                            "pid": proc_info['pid'],
                            "name": proc_info['name'],
                            "cpu_percent": round(proc_info['cpu_percent'] or 0, 2),
                            "memory_mb": round((proc.memory_info().rss / (1024**2)), 2)
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except:
            pass
        return Kloud_processes

    def check_alba_status(self) -> Dict:
        """Kontrollon statusin real tÃ« ALBA"""
        try:
            # Provon tÃ« lidhet me ALBA endpoint
            response = requests.get('http://localhost:8000/api/alba/status', timeout=2)
            return {
                "status": "active" if response.status_code == 200 else "inactive",
                "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2),
                "last_check": datetime.datetime.utcnow().isoformat() + "Z"
            }
        except:
            return {
                "status": "inactive",
                "response_time_ms": 0,
                "last_check": datetime.datetime.utcnow().isoformat() + "Z"
            }

    def check_asi_status(self) -> Dict:
        """Kontrollon statusin real tÃ« ASI"""
        try:
            response = requests.get('http://localhost:8000/asi/status', timeout=2)
            return {
                "status": "active" if response.status_code == 200 else "inactive",
                "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2)
            }
        except:
            return {"status": "inactive", "response_time_ms": 0}

    def check_api_endpoints(self) -> List[Dict]:
        """Kontrollon tÃ« gjitha endpoint-et e API-t"""
        endpoints = [
            ("/health", "GET"),
            ("/status", "GET"), 
            ("/api/alba/status", "GET"),
            ("/asi/status", "GET"),
            ("/billing/stripe/payment-intent", "POST")
        ]
        
        results = []
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f'http://localhost:8000{endpoint}', timeout=1)
                else:
                    response = requests.post(f'http://localhost:8000{endpoint}', timeout=1)
                
                results.append({
                    "endpoint": endpoint,
                    "method": method,
                    "status": "active" if response.status_code in [200, 201] else "inactive",
                    "response_time_ms": round(response.elapsed.total_seconds() * 1000, 2)
                })
            except:
                results.append({
                    "endpoint": endpoint,
                    "method": method,
                    "status": "inactive",
                    "response_time_ms": 0
                })
        
        return results

    def calculate_health_score(self) -> float:
        """Llogarit score real tÃ« shÃ«ndetit tÃ« sistemit"""
        try:
            score = 100.0
            
            # Zbrit pÃ«r CPU tÃ« lartÃ«
            cpu_usage = psutil.cpu_percent(interval=0.1)
            if cpu_usage > 80:
                score -= 20
            elif cpu_usage > 60:
                score -= 10
                
            # Zbrit pÃ«r memory tÃ« lartÃ«
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                score -= 20
            elif memory.percent > 80:
                score -= 10
                
            # Zbrit pÃ«r disk tÃ« plotÃ«
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                score -= 15
            elif disk.percent > 80:
                score -= 5
                
            # Zbrit pÃ«r API joaktiv
            api_status = self.check_api_endpoints()
            inactive_apis = sum(1 for api in api_status if api['status'] == 'inactive')
            if inactive_apis > 0:
                score -= (inactive_apis * 5)
                
            return max(round(score, 2), 0)
            
        except:
            return 0.0

# âœ… PÃ‹RDORIMI:
if __name__ == "__main__":
    metrics_collector = KloudRealMetrics()
    
    # Merr metrika reale
    real_metrics = metrics_collector.get_system_metrics()
    
    # Printo rezultatet
    print("ðŸš€ Kloud REAL METRICS:")
    print(json.dumps(real_metrics, indent=2))
    
    # Gjendja e shÃ«ndetit
    health = real_metrics['health_score']
    status = "âœ… OPTIMAL" if health > 90 else "âš ï¸ ATTENTION" if health > 70 else "ðŸš¨ CRITICAL"
    print(f"\nðŸ¥ SYSTEM HEALTH: {health}% - {status}")


