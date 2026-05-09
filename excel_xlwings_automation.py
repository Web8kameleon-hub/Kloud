#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel xlwings Automation - REAL Live Data Updates
Connects to Kloud API and updates Excel dashboards with REAL metrics.
NO MOCK DATA - All values from live API endpoints.

Author: Kloud Automation
Version: 1.0.0
"""

import asyncio
import aiohttp
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# xlwings import with fallback
try:
    import xlwings as xw
    XLWINGS_AVAILABLE = True
except ImportError:
    XLWINGS_AVAILABLE = False
    print("⚠️  xlwings not installed. Run: pip install xlwings")


class ExcelLiveUpdater:
    """
    Updates Excel dashboards with REAL data from Kloud API.
    NO MOCK DATA - All metrics are live from the running system.
    """
    
    def __init__(self, api_base: str = "http://localhost:8000"):
        self.api_base = api_base
        self.session: Optional[aiohttp.ClientSession] = None
        self.update_interval = 5  # seconds
        self.last_update: Optional[datetime] = None
        
    async def _ensure_session(self):
        """Ensure aiohttp session is available."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
    
    async def fetch_real_metrics(self) -> Dict[str, Any]:
        """
        Fetch REAL metrics from all ASI Trinity endpoints.
        NO MOCK DATA - Returns error if API unavailable.
        """
        await self._ensure_session()
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "live_api",
            "alba": None,
            "albi": None,
            "jona": None,
            "system": None,
            "errors": []
        }
        
        endpoints = {
            "system": "/asi/status",
            "alba": "/asi/alba/metrics",
            "albi": "/asi/albi/metrics",
            "jona": "/asi/jona/metrics"
        }
        
        for name, endpoint in endpoints.items():
            try:
                async with self.session.get(
                    f"{self.api_base}{endpoint}",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        metrics[name] = data
                    else:
                        metrics["errors"].append(f"{name}: HTTP {resp.status}")
            except asyncio.TimeoutError:
                metrics["errors"].append(f"{name}: timeout")
            except Exception as e:
                metrics["errors"].append(f"{name}: {str(e)}")
        
        return metrics
    
    def update_dashboard_registry(self, wb: 'xw.Book', metrics: Dict[str, Any]) -> int:
        """Update Dashboard_Registry.xlsx with live metrics."""
        updated = 0
        
        try:
            sheet = wb.sheets[0]  # First sheet
            
            # Find or create header row
            # Update timestamp
            sheet.range("A1").value = "Last Updated"
            sheet.range("B1").value = metrics["timestamp"]
            updated += 1
            
            # System status
            if metrics.get("system"):
                system = metrics["system"]
                sheet.range("A3").value = "System Version"
                sheet.range("B3").value = system.get("version", "N/A")
                sheet.range("A4").value = "Uptime (hours)"
                uptime_s = system.get("system", {}).get("uptime_seconds", 0)
                sheet.range("B4").value = round(uptime_s / 3600, 2) if uptime_s else 0
                updated += 2
            
            # Trinity Health
            row = 6
            for component in ["alba", "albi", "jona"]:
                comp_data = metrics.get(component, {})
                if comp_data:
                    # Get the nested data
                    inner = comp_data.get(f"{component}_network", 
                              comp_data.get(f"{component}_neural",
                                comp_data.get(f"{component}_data", {})))
                    
                    health = inner.get("health", 0) if inner else 0
                    source = inner.get("data_source", "unknown") if inner else "error"
                    
                    sheet.range(f"A{row}").value = f"{component.upper()} Health"
                    sheet.range(f"B{row}").value = f"{round(health * 100, 1)}%"
                    sheet.range(f"C{row}").value = f"Source: {source}"
                    row += 1
                    updated += 1
            
            # Data source indicator
            sheet.range(f"A{row + 1}").value = "Data Source"
            sheet.range(f"B{row + 1}").value = "REAL API - NO MOCK"
            
        except Exception as e:
            print(f"❌ Error updating Dashboard_Registry: {e}")
        
        return updated
    
    def update_python_dashboard(self, wb: 'xw.Book', metrics: Dict[str, Any]) -> int:
        """Update Kloud_Python_Dashboard.xlsx with live metrics."""
        updated = 0
        
        try:
            sheet = wb.sheets[0]
            
            # Update header with timestamp
            sheet.range("A1").value = "Kloud Python Dashboard - LIVE"
            sheet.range("A2").value = f"Updated: {metrics['timestamp']}"
            
            # Trinity metrics table
            headers = ["Component", "Health %", "Status", "Data Source"]
            for col, header in enumerate(headers, 1):
                sheet.range((4, col)).value = header
            
            row = 5
            for component in ["alba", "albi", "jona"]:
                comp_data = metrics.get(component, {})
                if comp_data:
                    inner_key = f"{component}_network" if component == "alba" else \
                               f"{component}_neural" if component == "albi" else \
                               f"{component}_data"
                    inner = comp_data.get(inner_key, {})
                    
                    health = inner.get("health", 0) * 100 if inner else 0
                    operational = inner.get("operational", False) if inner else False
                    source = inner.get("data_source", "error") if inner else "error"
                    
                    sheet.range((row, 1)).value = component.upper()
                    sheet.range((row, 2)).value = round(health, 1)
                    sheet.range((row, 3)).value = "✅ Operational" if operational else "❌ Down"
                    sheet.range((row, 4)).value = source
                    row += 1
                    updated += 1
            
            # Errors section
            if metrics.get("errors"):
                sheet.range(f"A{row + 2}").value = "Errors"
                for i, err in enumerate(metrics["errors"]):
                    sheet.range(f"A{row + 3 + i}").value = f"⚠️ {err}"
                    updated += 1
            
        except Exception as e:
            print(f"❌ Error updating Python Dashboard: {e}")
        
        return updated
    
    async def run_single_update(self, excel_files: List[str] = None) -> Dict[str, Any]:
        """
        Run a single update cycle for all specified Excel files.
        Returns update statistics.
        """
        if not XLWINGS_AVAILABLE:
            return {"error": "xlwings not available", "updated": 0}
        
        # Default files
        if excel_files is None:
            excel_files = [
                "Dashboard_Registry.xlsx",
                "Kloud_Python_Dashboard.xlsx"
            ]
        
        # Fetch REAL metrics
        print("📡 Fetching REAL metrics from API...")
        metrics = await self.fetch_real_metrics()
        
        if metrics.get("errors"):
            print(f"⚠️  Some endpoints had errors: {metrics['errors']}")
        
        results = {
            "timestamp": metrics["timestamp"],
            "files_updated": [],
            "total_cells": 0,
            "errors": metrics.get("errors", [])
        }
        
        base_path = Path(__file__).parent
        
        for filename in excel_files:
            filepath = base_path / filename
            if not filepath.exists():
                results["errors"].append(f"File not found: {filename}")
                continue
            
            try:
                print(f"📊 Opening {filename}...")
                wb = xw.Book(str(filepath))
                
                # Update based on file type
                if "Dashboard_Registry" in filename:
                    cells = self.update_dashboard_registry(wb, metrics)
                elif "Python_Dashboard" in filename:
                    cells = self.update_python_dashboard(wb, metrics)
                else:
                    # Generic update - just timestamp
                    wb.sheets[0].range("A1").value = f"Updated: {metrics['timestamp']}"
                    cells = 1
                
                wb.save()
                print(f"✅ {filename}: {cells} cells updated")
                
                results["files_updated"].append(filename)
                results["total_cells"] += cells
                
            except Exception as e:
                results["errors"].append(f"{filename}: {str(e)}")
                print(f"❌ {filename}: {e}")
        
        self.last_update = datetime.utcnow()
        return results
    
    async def run_continuous(self, excel_files: List[str] = None, interval: int = 5):
        """
        Run continuous updates at specified interval.
        Press Ctrl+C to stop.
        """
        print(f"🚀 Starting continuous Excel updates every {interval}s")
        print("   Press Ctrl+C to stop")
        print("-" * 50)
        
        self.update_interval = interval
        
        try:
            while True:
                result = await self.run_single_update(excel_files)
                print(f"   Updated {result['total_cells']} cells in {len(result['files_updated'])} files")
                
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n⏹️  Stopped by user")
        finally:
            if self.session:
                await self.session.close()
    
    async def close(self):
        """Clean up resources."""
        if self.session and not self.session.closed:
            await self.session.close()


# Command-line interface
async def main():
    """Main entry point for Excel automation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Excel xlwings Automation - REAL Data Only")
    parser.add_argument("--api", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--interval", type=int, default=5, help="Update interval in seconds")
    parser.add_argument("--once", action="store_true", help="Run single update and exit")
    parser.add_argument("--files", nargs="+", help="Excel files to update")
    
    args = parser.parse_args()
    
    updater = ExcelLiveUpdater(api_base=args.api)
    
    try:
        if args.once:
            result = await updater.run_single_update(args.files)
            print(f"\n📈 Update complete: {result}")
        else:
            await updater.run_continuous(args.files, args.interval)
    finally:
        await updater.close()


if __name__ == "__main__":
    print("=" * 60)
    print("  Excel xlwings Automation - REAL DATA ONLY")
    print("  NO MOCK DATA - All metrics from live API")
    print("=" * 60)
    asyncio.run(main())

