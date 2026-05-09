#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏗️ SCALABILITY MODULE RUNNER
=============================
Ekzekuton modulin e skalabilitetit për zbulim dhe integrim të të dhënave të hapura.

Ky script:
- Inicializon motorin e skalabilitetit
- Zbulon burime të reja të të dhënave
- Ushqen sistemin inteligjent
- Gjeneron përmbajtje të re
"""

import asyncio
import sys
import os
from pathlib import Path

# Shton root directory në path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from open_data_scalability import get_scalability_engine, discover_and_feed_system

async def main():
    """Funksioni kryesor"""
    print("🚀 Filloj Scalability Module Runner...")
    print("=" * 50)

    try:
        # Kontrollon për cycle engine
        cycle_engine = None
        try:
            from cycle_engine import CycleEngine
            cycle_engine = CycleEngine()
            print("✅ Cycle Engine gjetur dhe inicializuar")
        except ImportError:
            print("⚠️ Cycle Engine nuk është i disponueshëm - vazhdojmë pa të")

        # Merr motorin e skalabilitetit
        scalability_engine = await get_scalability_engine(cycle_engine)

        print("🔍 Filloj zbulimin e burimeve të të dhënave...")
        print("-" * 40)

        # Zbulon burime të reja
        domains_to_search = [
            ".edu", ".ac.uk", ".ac.de", ".gov", ".org",
            "cern.ch", "nasa.gov", "who.int", "un.org"
        ]

        new_sources = await scalability_engine.discover_data_sources(domains_to_search)

        if new_sources:
            print(f"✅ Zbuluar {len(new_sources)} burime të reja!")
            print("\n📋 Burime të reja:")
            for source in new_sources[:5]:  # Shfaq 5 të parat
                print(f"  • {source.name} ({source.url}) - {source.source_type.value}")

            if len(new_sources) > 5:
                print(f"  ... dhe {len(new_sources) - 5} të tjera")

            print("\n🚀 Ushqej sistemin inteligjent...")
            print("-" * 40)

            # Ushqen sistemin
            results = await scalability_engine.feed_intelligent_modules(new_sources)

            print("📊 REZULTATET E PRODHIMIT:")
            print("=" * 50)

            total_generated = 0
            for content_type, items in results.items():
                count = len(items)
                total_generated += count
                print(f"📄 {content_type.replace('_', ' ').title()}: {count}")

                # Shfaq disa shembuj
                if items and count > 0:
                    sample = items[0]
                    if 'title' in sample:
                        print(f"   💡 Shembull: {sample['title'][:60]}...")
                    elif 'cycle_id' in sample:
                        print(f"   🔄 Cycle: {sample['cycle_id']}")
                    print()

            print(f"🎯 TOTAL GJENERUAR: {total_generated} elementë të rinj")
            print()

            # Merr metrikat
            metrics = await scalability_engine.get_metrics()
            print("📈 METRIKA TË SISTEMIT:")
            print("-" * 30)
            print(f"🔍 Burime totale zbuluar: {metrics.total_sources_discovered}")
            print(f"✅ Burime aktive: {metrics.active_sources}")
            print(f"💾 Të dhëna të ingestuara: {metrics.data_ingested_gb:.2f} GB")
            print(f"🔄 Cycles të gjeneruar: {metrics.cycles_generated}")
            print(f"📚 Kërkime të prodhuar: {metrics.research_papers_generated}")
            print(f"🎮 Simulime të ekzekutuara: {metrics.simulations_run}")
            print(f"🛡️ Kontrolle sigurie JONA: {metrics.jona_reviews}")
            if metrics.safety_violations > 0:
                print(f"⚠️ Shkelje sigurie: {metrics.safety_violations}")

        else:
            print("ℹ️ Nuk u zbuluan burime të reja këtë herë")
            print("💡 Provo të shtosh domain-e të tjera ose kontrollo lidhjen internet")

        print("\n✅ Procesi përfundoi me sukses!")
        print("🔄 Sistemi është gati për cikle të ardhshme")

    except KeyboardInterrupt:
        print("\n⏹️ Procesi u ndërpre nga përdoruesi")
    except Exception as e:
        print(f"\n❌ Gabim gjatë ekzekutimit: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)</content>
<parameter name="filePath">c:\Users\pc\Kloud-cloud\run_scalability.py

