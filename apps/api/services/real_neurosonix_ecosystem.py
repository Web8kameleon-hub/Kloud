"""
ðŸ§ âš¡ REAL Kloud ECOSYSTEM - ALBI + ALBA + JONA
====================================================
Ekosistemi real i Kloud me tÃ« tre karakteret kryesore.
Real data processing, real monitoring, real intelligence growth.

NO FAKE DATA, NO MOCK, REAL ECOSYSTEM ONLY
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path
import aiofiles

from .albi_real_engine import create_albi_real
from .alba_real_collector import create_alba_real  
from .jona_real_monitor import create_jona_real


class KloudRealEcosystem:
    """
    ðŸŒ Real Ecosystem qÃ« integron ALBI, ALBA dhe JONA me tÃ« dhÃ«na reale
    """
    
    def __init__(self, base_dir="C:/Kloud-cloud"):
        self.base_dir = Path(base_dir)
        self.ecosystem_log = self.base_dir / "data" / "ecosystem_real_log.json"
        
        # Character instances (initialized on startup)
        self.albi = None
        self.alba = None 
        self.jona = None
        
        # Ecosystem metrics
        self.ecosystem_stats = {
            "startup_time": None,
            "total_cycles": 0,
            "successful_cycles": 0,
            "data_processed": 0,
            "intelligence_growth": 0,
            "harmony_average": 0
        }
    
    async def initialize_real_ecosystem(self) -> Dict[str, Any]:
        """Inicializon ekosisitemin real me tÃ« tri karakteret"""
        
        try:
            # Initialize ALBI (Intelligence Engine)
            self.albi = await create_albi_real()
            albi_status = await self.albi.get_real_status()
            
            # Initialize ALBA (Data Collector)
            self.alba = await create_alba_real()
            alba_status = await self.alba.get_real_status()
            
            # Initialize JONA (System Monitor)
            self.jona = await create_jona_real()
            jona_status = await self.jona.get_real_status()
            
            # Set startup time
            self.ecosystem_stats["startup_time"] = datetime.utcnow().isoformat()
            
            initialization_result = {
                "ecosystem_status": "initialized_successfully",
                "characters": {
                    "albi": albi_status,
                    "alba": alba_status,
                    "jona": jona_status
                },
                "startup_timestamp": self.ecosystem_stats["startup_time"],
                "real_ecosystem_only": True,
                "no_fake_data": True
            }
            
            await self._log_ecosystem_event("initialization", initialization_result)
            return initialization_result
            
        except Exception as e:
            error_result = {
                "ecosystem_status": "initialization_failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            await self._log_ecosystem_event("initialization_error", error_result)
            return error_result
    
    async def run_real_ecosystem_cycle(self) -> Dict[str, Any]:
        """Ekzekuton njÃ« cikÃ«l tÃ« plotÃ« tÃ« ekosistemit real"""
        
        cycle_start = datetime.utcnow()
        cycle_id = f"cycle_{cycle_start.strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Step 1: JONA monitors system health
            health_report = await self.jona.monitor_real_system_health()
            harmony_score = await self.jona.calculate_real_harmony_score()
            alerts = await self.jona.generate_real_alerts()
            
            # Step 2: ALBA collects real data
            collected_data = await self.alba.scan_real_directories()
            system_metrics = await self.alba.collect_real_system_metrics()
            
            # Step 3: ALBA sends data to ALBI for processing
            transfer_result = await self.alba.send_to_albi_real(collected_data)
            
            # Step 4: ALBI processes and grows intelligence  
            albi_metrics = await self.albi.get_real_metrics()
            
            # Step 5: JONA checks character interactions
            interaction_health = await self.jona.check_albi_alba_interaction()
            
            # Calculate cycle success
            cycle_success = (
                len(alerts) == 0 and
                transfer_result.get("successful_transfers", 0) > 0 and
                harmony_score.get("harmony_score", 0) >= 50
            )
            
            # Update ecosystem stats
            self.ecosystem_stats["total_cycles"] += 1
            if cycle_success:
                self.ecosystem_stats["successful_cycles"] += 1
            
            self.ecosystem_stats["data_processed"] += len(collected_data)
            self.ecosystem_stats["intelligence_growth"] = albi_metrics.get("total_growth", 0)
            
            # Calculate average harmony
            current_harmony = harmony_score.get("harmony_score", 0)
            total_cycles = self.ecosystem_stats["total_cycles"]
            prev_average = self.ecosystem_stats["harmony_average"]
            self.ecosystem_stats["harmony_average"] = (
                (prev_average * (total_cycles - 1) + current_harmony) / total_cycles
            )
            
            cycle_result = {
                "cycle_id": cycle_id,
                "cycle_success": cycle_success,
                "cycle_duration": (datetime.utcnow() - cycle_start).total_seconds(),
                "jona_results": {
                    "health_report": health_report,
                    "harmony_score": harmony_score,
                    "alerts_count": len(alerts),
                    "interaction_health": interaction_health
                },
                "alba_results": {
                    "files_collected": len(collected_data),
                    "system_metrics": system_metrics,
                    "transfer_result": transfer_result
                },
                "albi_results": {
                    "current_metrics": albi_metrics
                },
                "ecosystem_stats": self.ecosystem_stats,
                "timestamp": datetime.utcnow().isoformat(),
                "real_cycle_only": True
            }
            
            # Log the cycle
            await self._log_ecosystem_event("cycle_completed", cycle_result)
            await self.jona.log_real_monitoring_session(health_report, harmony_score, alerts)
            
            return cycle_result
            
        except Exception as e:
            error_result = {
                "cycle_id": cycle_id,
                "cycle_success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
            await self._log_ecosystem_event("cycle_error", error_result)
            return error_result
    
    async def run_continuous_ecosystem(self, duration_minutes: int = 60, cycle_interval: int = 30) -> Dict[str, Any]:
        """Ekzekuton ekosisitemin nÃ« mÃ«nyrÃ« tÃ« vazhdueshme"""
        
        start_time = datetime.utcnow()
        end_time = start_time.timestamp() + (duration_minutes * 60)
        
        continuous_results = {
            "session_start": start_time.isoformat(),
            "planned_duration_minutes": duration_minutes,
            "cycle_interval_seconds": cycle_interval,
            "cycles_completed": [],
            "session_success": True
        }
        
        try:
            # Initialize ecosystem first
            init_result = await self.initialize_real_ecosystem()
            if "error" in init_result:
                continuous_results["session_success"] = False
                continuous_results["initialization_error"] = init_result
                return continuous_results
            
            # Run cycles until duration expires
            while datetime.utcnow().timestamp() < end_time:
                cycle_result = await self.run_real_ecosystem_cycle()
                continuous_results["cycles_completed"].append({
                    "cycle_id": cycle_result.get("cycle_id"),
                    "success": cycle_result.get("cycle_success"),
                    "timestamp": cycle_result.get("timestamp")
                })
                
                # Wait for next cycle
                await asyncio.sleep(cycle_interval)
            
            # Final statistics
            total_cycles = len(continuous_results["cycles_completed"])
            successful_cycles = len([c for c in continuous_results["cycles_completed"] if c["success"]])
            
            continuous_results.update({
                "session_end": datetime.utcnow().isoformat(),
                "actual_duration_minutes": (datetime.utcnow() - start_time).total_seconds() / 60,
                "total_cycles": total_cycles,
                "successful_cycles": successful_cycles,
                "success_rate": (successful_cycles / total_cycles * 100) if total_cycles > 0 else 0,
                "final_ecosystem_stats": self.ecosystem_stats
            })
            
            await self._log_ecosystem_event("continuous_session_completed", continuous_results)
            return continuous_results
            
        except Exception as e:
            continuous_results["session_success"] = False
            continuous_results["error"] = str(e)
            continuous_results["session_end"] = datetime.utcnow().isoformat()
            
            await self._log_ecosystem_event("continuous_session_error", continuous_results)
            return continuous_results
    
    async def get_real_ecosystem_status(self) -> Dict[str, Any]:
        """Kthen statusin e plotÃ« real tÃ« ekosistemit"""
        
        try:
            # Get individual character status
            albi_status = await self.albi.get_real_status() if self.albi else {"status": "not_initialized"}
            alba_status = await self.alba.get_real_status() if self.alba else {"status": "not_initialized"}
            jona_status = await self.jona.get_real_status() if self.jona else {"status": "not_initialized"}
            
            # Overall ecosystem health
            characters_active = sum([
                albi_status.get("status") == "active",
                alba_status.get("status") == "active_real_collection", 
                jona_status.get("status") == "active_real_monitoring"
            ])
            
            ecosystem_health = "optimal" if characters_active == 3 else (
                "partial" if characters_active >= 1 else "inactive"
            )
            
            return {
                "ecosystem_health": ecosystem_health,
                "characters_active": characters_active,
                "character_status": {
                    "albi": albi_status,
                    "alba": alba_status,
                    "jona": jona_status
                },
                "ecosystem_stats": self.ecosystem_stats,
                "status_timestamp": datetime.utcnow().isoformat(),
                "real_status_only": True,
                "no_fake_metrics": True
            }
            
        except Exception as e:
            return {
                "ecosystem_health": "error",
                "error": str(e),
                "status_timestamp": datetime.utcnow().isoformat()
            }
    
    async def _log_ecosystem_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log i event-eve tÃ« ekosistemit"""
        
        log_entry = {
            "event_type": event_type,
            "event_data": event_data,
            "logged_at": datetime.utcnow().isoformat(),
            "ecosystem_logging": True
        }
        
        # Read existing log
        existing_log = []
        if self.ecosystem_log.exists():
            async with aiofiles.open(self.ecosystem_log, 'r') as f:
                content = await f.read()
                if content.strip():
                    existing_log = json.loads(content)
        
        # Add new event
        existing_log.append(log_entry)
        
        # Keep only last 200 events
        if len(existing_log) > 200:
            existing_log = existing_log[-200:]
        
        # Save log
        self.ecosystem_log.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(self.ecosystem_log, 'w') as f:
            await f.write(json.dumps(existing_log, indent=2, ensure_ascii=False))


# Factory function pÃ«r ecosystem real
async def create_real_Kloud_ecosystem() -> KloudRealEcosystem:
    """Krijon ekosisitemin real tÃ« Kloud"""
    ecosystem = KloudRealEcosystem()
    return ecosystem


# Main function pÃ«r testing
async def main():
    """Test i ekosistemit real"""
    print("ðŸ§ âš¡ Starting Real Kloud Ecosystem...")
    
    ecosystem = await create_real_Kloud_ecosystem()
    
    # Run one cycle for testing
    print("ðŸ”„ Running test cycle...")
    cycle_result = await ecosystem.run_real_ecosystem_cycle()
    
    print(f"âœ… Cycle completed: {cycle_result.get('cycle_success')}")
    print(f"ðŸ“Š Files processed: {cycle_result.get('alba_results', {}).get('files_collected', 0)}")
    print(f"ðŸŽ¯ Harmony Score: {cycle_result.get('jona_results', {}).get('harmony_score', {}).get('harmony_score', 0)}")
    
    # Get final status
    status = await ecosystem.get_real_ecosystem_status()
    print(f"ðŸŒ Ecosystem Health: {status.get('ecosystem_health')}")


if __name__ == "__main__":
    asyncio.run(main())



