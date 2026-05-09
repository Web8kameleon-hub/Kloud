"""
LOCATION LABS ENGINE - Distributed Geographic Research Processing
===================================================================
Isolated engine for location-based laboratory cycles across cities.
Operates independently like Ocean Central Hub - NOT in main.py.

ALL 23 LABORATORIES - Connected to ocean-core/laboratories.py
===================================================================
Albania (7): Elbasan, Tirana, Durrës, Vlorë, Shkodër, Korçë, Sarandë
Kosovo (1): Prishtina
North Macedonia (1): Kostur
Greece (1): Athens
Italy (1): Rome
Switzerland (1): Zurich
Serbia (1): Beograd
Bulgaria (1): Sofia
Croatia (1): Zagreb
Slovenia (1): Ljubljana
Austria (1): Vienna
Czech Republic (1): Prague
Hungary (1): Budapest
Romania (1): Bucharest
Turkey (1): Istanbul
Egypt (1): Cairo
Palestine (1): Jerusalem

Author: Ledjan Ahmati
License: Closed Source
Version: 2.0.0 - Full 23 Labs Integration
"""

import asyncio
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, cast

# Add ocean-core to path for laboratories integration
OCEAN_CORE_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "ocean-core")
if OCEAN_CORE_PATH not in sys.path:
    sys.path.insert(0, OCEAN_CORE_PATH)

# Import LaboratoryNetwork from ocean-core for unified data
try:
    from laboratories import (  # type: ignore[import-not-found]
        LaboratoryNetwork,
        get_laboratory_network,
    )
    LABORATORIES_INTEGRATED = True
except ImportError:
    LABORATORIES_INTEGRATED = False
    LaboratoryNetwork = None  # type: ignore

logger = logging.getLogger("location_labs_engine")

# ============================================================================
# ENUMS & TYPES
# ============================================================================

class LocationRegion(str, Enum):
    """Geographic regions with laboratories - ALL 23 LABS"""
    # Albania (7)
    ELBASAN = "elbasan"
    TIRANA = "tirana"
    DURRES = "durres"
    VLORE = "vlore"
    SHKODER = "shkoder"
    KORCE = "korce"
    SARANDA = "saranda"
    # Kosovo (1)
    PRISHTINA = "prishtina"
    # North Macedonia (1)
    KOSTUR = "kostur"
    # Greece (1)
    ATHENS = "athens"
    # Italy (1)
    ROME = "rome"
    # Switzerland (1)
    ZURICH = "zurich"
    # Serbia (1)
    BEOGRAD = "beograd"
    # Bulgaria (1)
    SOFIA = "sofia"
    # Croatia (1)
    ZAGREB = "zagreb"
    # Slovenia (1)
    LJUBLJANA = "ljubljana"
    # Austria (1)
    VIENNA = "vienna"
    # Czech Republic (1)
    PRAGUE = "prague"
    # Hungary (1)
    BUDAPEST = "budapest"
    # Romania (1)
    BUCHAREST = "bucharest"
    # Turkey (1)
    ISTANBUL = "istanbul"
    # Egypt (1)
    CAIRO = "cairo"
    # Palestine (1)
    JERUSALEM = "jerusalem"


class LabDomain(str, Enum):
    """Lab domain types by location - ALL 23 TYPES"""
    # Core domains
    UNIVERSITY = "university"
    MEDICAL = "medical"
    RESEARCH = "research"
    MARINE = "marine"
    AGRICULTURAL = "agricultural"
    ECOLOGICAL = "ecological"
    TECH = "tech"
    # Extended domains (11 new)
    CYBERSECURITY = "cybersecurity"
    ENERGY = "energy"
    CLASSICAL = "classical"
    ARCHITECTURE = "architecture"
    FINANCE = "finance"
    INDUSTRIAL = "industrial"
    CHEMISTRY = "chemistry"
    BIOTECH = "biotech"
    QUANTUM = "quantum"
    NEUROSCIENCE = "neuroscience"
    ROBOTICS = "robotics"
    DATA = "data"
    NANOTECHNOLOGY = "nanotechnology"
    TRADE = "trade"
    ARCHEOLOGY = "archeology"
    HERITAGE = "heritage"
    UNDERWATER = "underwater"
    IOT = "iot"


class LabDataType(str, Enum):
    """Types of data produced by location labs"""
    EXPERIMENTAL = "experimental"
    OBSERVATIONAL = "observational"
    SENSOR = "sensor"
    CLINICAL = "clinical"
    ENVIRONMENTAL = "environmental"


@dataclass
class LocationLabResult:
    """Result from a location-based lab execution"""
    lab_id: str
    location: LocationRegion
    domain: LabDomain
    data_type: LabDataType
    collection_timestamp: str
    processing_time_ms: float
    data_quality_score: float  # 0-1
    sample_count: int
    artifacts_generated: int
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'lab_id': self.lab_id,
            'location': self.location.value,
            'domain': self.domain.value,
            'data_type': self.data_type.value,
            'collection_timestamp': self.collection_timestamp,
            'processing_time_ms': self.processing_time_ms,
            'data_quality_score': self.data_quality_score,
            'sample_count': self.sample_count,
            'artifacts_generated': self.artifacts_generated,
            'errors': self.errors,
            'metadata': self.metadata
        }


# ============================================================================
# LOCATION LAB DEFINITIONS
# ============================================================================

@dataclass
class LocationLabConfig:
    """Configuration for a location laboratory"""
    location: LocationRegion
    domain: LabDomain
    country: str
    source_api: str
    cycle_interval_minutes: int
    data_types: List[LabDataType]
    description: str


LOCATION_LABS_CONFIG: Dict[LocationRegion, LocationLabConfig] = {
    # ALBANIA
    LocationRegion.ELBASAN: LocationLabConfig(
        location=LocationRegion.ELBASAN,
        domain=LabDomain.UNIVERSITY,
        country="Albania",
        source_api="elbasan.university.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.EXPERIMENTAL, LabDataType.OBSERVATIONAL],
        description="Elbasan University Laboratory - Physics & Biology Research"
    ),
    LocationRegion.TIRANA: LocationLabConfig(
        location=LocationRegion.TIRANA,
        domain=LabDomain.MEDICAL,
        country="Albania",
        source_api="tirana.medical.center",
        cycle_interval_minutes=30,
        data_types=[LabDataType.CLINICAL, LabDataType.SENSOR],
        description="Tirana Medical Center - Clinical & Biomedical Research"
    ),
    LocationRegion.DURRES: LocationLabConfig(
        location=LocationRegion.DURRES,
        domain=LabDomain.RESEARCH,
        country="Albania",
        source_api="durres.research.institute",
        cycle_interval_minutes=30,
        data_types=[LabDataType.EXPERIMENTAL, LabDataType.SENSOR],
        description="Durrës Research Institute - General Research & Development"
    ),
    LocationRegion.VLORE: LocationLabConfig(
        location=LocationRegion.VLORE,
        domain=LabDomain.MARINE,
        country="Albania",
        source_api="vlore.marine.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.OBSERVATIONAL, LabDataType.ENVIRONMENTAL],
        description="Vlorë Marine Laboratory - Marine Biology & Oceanography"
    ),
    LocationRegion.SHKODER: LocationLabConfig(
        location=LocationRegion.SHKODER,
        domain=LabDomain.UNIVERSITY,
        country="Albania",
        source_api="shkoder.university.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.EXPERIMENTAL, LabDataType.OBSERVATIONAL],
        description="Shkodër University - Environmental & Ecological Studies"
    ),
    LocationRegion.KORCE: LocationLabConfig(
        location=LocationRegion.KORCE,
        domain=LabDomain.AGRICULTURAL,
        country="Albania",
        source_api="korce.agricultural.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.OBSERVATIONAL, LabDataType.ENVIRONMENTAL],
        description="Korçë Agricultural Lab - Agricultural Science & Soil Studies"
    ),
    LocationRegion.SARANDA: LocationLabConfig(
        location=LocationRegion.SARANDA,
        domain=LabDomain.ECOLOGICAL,
        country="Albania",
        source_api="saranda.ecological.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.OBSERVATIONAL, LabDataType.ENVIRONMENTAL],
        description="Sarandë Ecological Lab - Biodiversity & Ecosystem Monitoring"
    ),
    # KOSOVO
    LocationRegion.PRISHTINA: LocationLabConfig(
        location=LocationRegion.PRISHTINA,
        domain=LabDomain.MEDICAL,
        country="Kosovo",
        source_api="prishtina.university.hospital",
        cycle_interval_minutes=30,
        data_types=[LabDataType.CLINICAL, LabDataType.SENSOR],
        description="Prishtina University Hospital - Medical & Healthcare Research"
    ),
    # NORTH MACEDONIA
    LocationRegion.KOSTUR: LocationLabConfig(
        location=LocationRegion.KOSTUR,
        domain=LabDomain.MEDICAL,
        country="North Macedonia",
        source_api="kostur.medical.center",
        cycle_interval_minutes=30,
        data_types=[LabDataType.CLINICAL, LabDataType.SENSOR],
        description="Kostur Medical Center - Clinical Research & Medicine"
    ),
    # GREECE
    LocationRegion.ATHENS: LocationLabConfig(
        location=LocationRegion.ATHENS,
        domain=LabDomain.RESEARCH,
        country="Greece",
        source_api="athens.national.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.EXPERIMENTAL, LabDataType.SENSOR],
        description="Athens National Lab - Multidisciplinary Research"
    ),
    # ITALY
    LocationRegion.ROME: LocationLabConfig(
        location=LocationRegion.ROME,
        domain=LabDomain.RESEARCH,
        country="Italy",
        source_api="rome.research.center",
        cycle_interval_minutes=30,
        data_types=[LabDataType.EXPERIMENTAL, LabDataType.OBSERVATIONAL],
        description="Rome Research Center - European Research Hub"
    ),
    # SWITZERLAND
    LocationRegion.ZURICH: LocationLabConfig(
        location=LocationRegion.ZURICH,
        domain=LabDomain.FINANCE,
        country="Switzerland",
        source_api="zurich.finance.university",
        cycle_interval_minutes=30,
        data_types=[LabDataType.EXPERIMENTAL, LabDataType.SENSOR],
        description="Zurich Finance Lab - Financial Analysis & Blockchain"
    ),
    # SERBIA
    LocationRegion.BEOGRAD: LocationLabConfig(
        location=LocationRegion.BEOGRAD,
        domain=LabDomain.INDUSTRIAL,
        country="Serbia",
        source_api="beograd.industrial.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.EXPERIMENTAL, LabDataType.SENSOR],
        description="Beograd Industrial Lab - Industrial Process Optimization"
    ),
    # BULGARIA
    LocationRegion.SOFIA: LocationLabConfig(
        location=LocationRegion.SOFIA,
        domain=LabDomain.CHEMISTRY,
        country="Bulgaria",
        source_api="sofia.chemistry.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.EXPERIMENTAL, LabDataType.OBSERVATIONAL],
        description="Sofia Chemistry Lab - Chemical Research & Material Science"
    ),
    # CROATIA
    LocationRegion.ZAGREB: LocationLabConfig(
        location=LocationRegion.ZAGREB,
        domain=LabDomain.BIOTECH,
        country="Croatia",
        source_api="zagreb.biotech.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.EXPERIMENTAL, LabDataType.CLINICAL],
        description="Zagreb Biotech Lab - Biotechnology & Genetic Engineering"
    ),
    # SLOVENIA
    LocationRegion.LJUBLJANA: LocationLabConfig(
        location=LocationRegion.LJUBLJANA,
        domain=LabDomain.QUANTUM,
        country="Slovenia",
        source_api="ljubljana.quantum.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.EXPERIMENTAL, LabDataType.SENSOR],
        description="Ljubljana Quantum Lab - Quantum Computing & Physics"
    ),
    # AUSTRIA
    LocationRegion.VIENNA: LocationLabConfig(
        location=LocationRegion.VIENNA,
        domain=LabDomain.NEUROSCIENCE,
        country="Austria",
        source_api="vienna.neuroscience.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.CLINICAL, LabDataType.SENSOR],
        description="Vienna Neuroscience Lab - Brain Research & Cognitive Science"
    ),
    # CZECH REPUBLIC
    LocationRegion.PRAGUE: LocationLabConfig(
        location=LocationRegion.PRAGUE,
        domain=LabDomain.ROBOTICS,
        country="Czech Republic",
        source_api="prague.robotics.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.EXPERIMENTAL, LabDataType.SENSOR],
        description="Prague Robotics Lab - Robotics & Automation Systems"
    ),
    # HUNGARY
    LocationRegion.BUDAPEST: LocationLabConfig(
        location=LocationRegion.BUDAPEST,
        domain=LabDomain.DATA,
        country="Hungary",
        source_api="budapest.data.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.OBSERVATIONAL, LabDataType.SENSOR],
        description="Budapest Data Lab - Big Data Analytics & Visualization"
    ),
    # ROMANIA
    LocationRegion.BUCHAREST: LocationLabConfig(
        location=LocationRegion.BUCHAREST,
        domain=LabDomain.NANOTECHNOLOGY,
        country="Romania",
        source_api="bucharest.nanotechnology.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.EXPERIMENTAL, LabDataType.SENSOR],
        description="Bucharest Nanotechnology Lab - Nanomaterials & Research"
    ),
    # TURKEY
    LocationRegion.ISTANBUL: LocationLabConfig(
        location=LocationRegion.ISTANBUL,
        domain=LabDomain.TRADE,
        country="Turkey",
        source_api="istanbul.trade.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.OBSERVATIONAL, LabDataType.SENSOR],
        description="Istanbul Trade Lab - International Trade & Logistics"
    ),
    # EGYPT
    LocationRegion.CAIRO: LocationLabConfig(
        location=LocationRegion.CAIRO,
        domain=LabDomain.ARCHEOLOGY,
        country="Egypt",
        source_api="cairo.archeology.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.OBSERVATIONAL, LabDataType.ENVIRONMENTAL],
        description="Cairo Archeology Lab - Archeological Research & Preservation"
    ),
    # PALESTINE
    LocationRegion.JERUSALEM: LocationLabConfig(
        location=LocationRegion.JERUSALEM,
        domain=LabDomain.HERITAGE,
        country="Palestine",
        source_api="jerusalem.heritage.lab",
        cycle_interval_minutes=30,
        data_types=[LabDataType.OBSERVATIONAL, LabDataType.ENVIRONMENTAL],
        description="Jerusalem Heritage Lab - Cultural Heritage & Restoration"
    ),
}


# ============================================================================
# LOCATION LAB PROCESSOR
# ============================================================================

class LocationLabProcessor:
    """Processes data from a specific geographic laboratory"""
    
    def __init__(self, config: LocationLabConfig) -> None:
        self.config: LocationLabConfig = config
        self.lab_id: str = f"loc-lab-{config.location.value}"
        self.execution_count: int = 0
        self.total_processing_time: float = 0.0
        self.last_execution: Optional[datetime] = None
    
    async def process(self) -> LocationLabResult:
        """Process lab data cycle"""
        import time
        from random import randint, random
        
        start_time = time.time()
        collection_timestamp = datetime.utcnow().isoformat()
        
        # Simulate data collection
        await asyncio.sleep(0.1)  # Simulate network/processing
        
        sample_count = randint(50, 500)
        artifacts_generated = randint(1, 10)
        data_quality_score = 0.75 + (0.2 * random())  # 0.75 - 0.95
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        result = LocationLabResult(
            lab_id=self.lab_id,
            location=self.config.location,
            domain=self.config.domain,
            data_type=self.config.data_types[0],  # Primary data type
            collection_timestamp=collection_timestamp,
            processing_time_ms=processing_time_ms,
            data_quality_score=data_quality_score,
            sample_count=sample_count,
            artifacts_generated=artifacts_generated,
            metadata={
                'country': self.config.country,
                'source_api': self.config.source_api,
                'data_types': [dt.value for dt in self.config.data_types]
            }
        )
        
        self.execution_count += 1
        self.total_processing_time += processing_time_ms
        self.last_execution = datetime.utcnow()
        
        logger.info(f"✅ {self.config.location.value} lab processed: {sample_count} samples, "
                   f"{artifacts_generated} artifacts, quality={data_quality_score:.2f}")
        
        return result
    
    def get_stats(self) -> Dict[str, Any]:
        """Get lab statistics"""
        avg_processing_time = (
            self.total_processing_time / self.execution_count 
            if self.execution_count > 0 else 0
        )
        return {
            'lab_id': self.lab_id,
            'location': self.config.location.value,
            'execution_count': self.execution_count,
            'avg_processing_time_ms': avg_processing_time,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'domain': self.config.domain.value,
            'country': self.config.country
        }


# ============================================================================
# LOCATION LABS ENGINE
# ============================================================================

class LocationLabsEngine:
    """Central engine managing all location-based laboratories"""
    
    def __init__(self) -> None:
        self.labs: Dict[LocationRegion, LocationLabProcessor] = {}
        self.results_cache: Dict[LocationRegion, LocationLabResult] = {}
        self.initialized: bool = False
    
    async def initialize(self) -> None:
        """Initialize all location labs"""
        logger.info("🌍 Initializing Location Labs Engine...")
        
        for location, config in LOCATION_LABS_CONFIG.items():
            processor = LocationLabProcessor(config)
            self.labs[location] = processor
        
        self.initialized = True
        logger.info(f"✅ Location Labs Engine initialized - {len(self.labs)} labs active")
    
    async def process_lab(self, location: LocationRegion) -> LocationLabResult:
        """Process a single lab"""
        if location not in self.labs:
            raise ValueError(f"Location {location.value} not configured")
        
        processor = self.labs[location]
        result = await processor.process()
        self.results_cache[location] = result
        return result
    
    async def process_all_labs(self) -> List[LocationLabResult]:
        """Process all labs in parallel"""
        tasks = [
            self.process_lab(location) 
            for location in self.labs.keys()
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        # Filter out exceptions and cast to correct type
        valid_results: List[LocationLabResult] = [
            cast(LocationLabResult, r) for r in results if not isinstance(r, BaseException)
        ]
        return valid_results
    
    def get_lab_stats(self, location: LocationRegion) -> Optional[Dict[str, Any]]:
        """Get stats for a specific lab"""
        if location not in self.labs:
            return None
        return self.labs[location].get_stats()
    
    def get_all_stats(self) -> List[Dict[str, Any]]:
        """Get stats for all labs"""
        return [lab.get_stats() for lab in self.labs.values()]
    
    def get_last_result(self, location: LocationRegion) -> Optional[LocationLabResult]:
        """Get last result for a location"""
        return self.results_cache.get(location)
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get overall engine status"""
        return {
            "initialized": self.initialized,
            "total_labs": len(self.labs),
            "labs_by_domain": self._count_by_domain(),
            "labs_by_country": self._count_by_country(),
            "cached_results": len(self.results_cache),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _count_by_domain(self) -> Dict[str, int]:
        """Count labs by domain"""
        counts: Dict[str, int] = {}
        for processor in self.labs.values():
            domain = processor.config.domain.value
            counts[domain] = counts.get(domain, 0) + 1
        return counts
    
    def _count_by_country(self) -> Dict[str, int]:
        """Count labs by country"""
        counts: Dict[str, int] = {}
        for processor in self.labs.values():
            country = processor.config.country
            counts[country] = counts.get(country, 0) + 1
        return counts


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_location_engine: Optional[LocationLabsEngine] = None


async def get_location_labs_engine() -> LocationLabsEngine:
    """Get or create global Location Labs Engine"""
    global _location_engine
    if _location_engine is None:
        _location_engine = LocationLabsEngine()
        await _location_engine.initialize()
    return _location_engine


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    "LocationLabsEngine",
    "LocationLabProcessor",
    "LocationLabResult",
    "LocationRegion",
    "LabDomain",
    "LabDataType",
    "get_location_labs_engine",
    "LOCATION_LABS_CONFIG",
    "get_unified_labs_status",
    "sync_with_laboratory_network",
    "LABORATORIES_INTEGRATED"
]


# ============================================================================
# UNIFIED LABORATORY NETWORK INTEGRATION
# ============================================================================

async def get_unified_labs_status() -> Dict[str, Any]:
    """
    Get unified status from both LocationLabsEngine AND LaboratoryNetwork.
    This combines the cycle-processing engine with the laboratory metadata.
    """
    result: Dict[str, Any] = {
        "location_labs_engine": {},
        "laboratory_network": {},
        "unified_count": 0,
        "integration_status": LABORATORIES_INTEGRATED
    }
    
    # Get LocationLabsEngine status
    engine = await get_location_labs_engine()
    result["location_labs_engine"] = engine.get_engine_status()
    
    # Get LaboratoryNetwork status (if integrated)
    if LABORATORIES_INTEGRATED:
        try:
            network = get_laboratory_network()
            result["laboratory_network"] = network.get_network_stats()
            result["unified_count"] = result["location_labs_engine"]["total_labs"]
        except Exception as e:
            result["laboratory_network"] = {"error": str(e)}
    
    return result


async def sync_with_laboratory_network() -> Dict[str, Any]:
    """
    Synchronize LocationLabsEngine signals with LaboratoryNetwork metadata.
    Returns mapping between engine regions and network labs.
    """
    if not LABORATORIES_INTEGRATED:
        return {
            "synced": False,
            "reason": "LaboratoryNetwork not imported",
            "labs": []
        }
    
    engine = await get_location_labs_engine()
    network = get_laboratory_network()
    
    # Map engine regions to network labs
    mapping: List[Dict[str, Any]] = []
    
    region_to_lab_prefix = {
        LocationRegion.ELBASAN: "Elbasan_AI",
        LocationRegion.TIRANA: "Tirana_Medical",
        LocationRegion.DURRES: "Durres_IoT",
        LocationRegion.VLORE: "Vlore_Environmental",
        LocationRegion.SHKODER: "Shkoder_Marine",
        LocationRegion.KORCE: "Korce_Agricultural",
        LocationRegion.SARANDA: "Sarrande_Underwater",
        LocationRegion.PRISHTINA: "Prishtina_Security",
        LocationRegion.KOSTUR: "Kostur_Energy",
        LocationRegion.ATHENS: "Athens_Classical",
        LocationRegion.ROME: "Rome_Architecture",
        LocationRegion.ZURICH: "Zurich_Finance",
        LocationRegion.BEOGRAD: "Beograd_Industrial",
        LocationRegion.SOFIA: "Sofia_Chemistry",
        LocationRegion.ZAGREB: "Zagreb_Biotech",
        LocationRegion.LJUBLJANA: "Ljubljana_Quantum",
        LocationRegion.VIENNA: "Vienna_Neuroscience",
        LocationRegion.PRAGUE: "Prague_Robotics",
        LocationRegion.BUDAPEST: "Budapest_Data",
        LocationRegion.BUCHAREST: "Bucharest_Nanotechnology",
        LocationRegion.ISTANBUL: "Istanbul_Trade",
        LocationRegion.CAIRO: "Cairo_Archeology",
        LocationRegion.JERUSALEM: "Jerusalem_Heritage",
    }
    
    for region, lab_id in region_to_lab_prefix.items():
        engine_stats = engine.get_lab_stats(region)
        network_lab = network.get_lab_by_id(lab_id)
        
        mapping.append({
            "region": region.value,
            "lab_id": lab_id,
            "engine_active": engine_stats is not None,
            "network_lab": network_lab.to_dict() if network_lab else None,
            "synced": engine_stats is not None and network_lab is not None
        })
    
    synced_count = sum(1 for m in mapping if m["synced"])
    
    return {
        "synced": True,
        "total_mappings": len(mapping),
        "synced_labs": synced_count,
        "labs": mapping
    }


# ============================================================================
# ALL 23 LABS QUICK REFERENCE
# ============================================================================

LABS_REFERENCE = """
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ALL 23 KLOUD LABORATORIES                        │
├─────────────────┬───────────────────┬──────────────────────────────────────┤
│ REGION          │ COUNTRY           │ DOMAIN                               │
├─────────────────┼───────────────────┼──────────────────────────────────────┤
│ Elbasan         │ Albania           │ AI & Machine Learning                │
│ Tirana          │ Albania           │ Medical Research                     │
│ Durrës          │ Albania           │ IoT & Sensors                        │
│ Vlorë           │ Albania           │ Environmental                        │
│ Shkodër         │ Albania           │ Marine Biology                       │
│ Korçë           │ Albania           │ Agricultural Sciences                │
│ Sarandë         │ Albania           │ Underwater Exploration               │
│ Prishtina       │ Kosovo            │ Cybersecurity                        │
│ Kostur          │ North Macedonia   │ Renewable Energy                     │
│ Athens          │ Greece            │ Classical Studies                    │
│ Rome            │ Italy             │ Architecture                         │
│ Zurich          │ Switzerland       │ Finance & Blockchain                 │
│ Beograd         │ Serbia            │ Industrial Optimization              │
│ Sofia           │ Bulgaria          │ Chemistry & Materials                │
│ Zagreb          │ Croatia           │ Biotechnology                        │
│ Ljubljana       │ Slovenia          │ Quantum Computing                    │
│ Vienna          │ Austria           │ Neuroscience                         │
│ Prague          │ Czech Republic    │ Robotics                             │
│ Budapest        │ Hungary           │ Big Data Analytics                   │
│ Bucharest       │ Romania           │ Nanotechnology                       │
│ Istanbul        │ Turkey            │ Trade & Logistics                    │
│ Cairo           │ Egypt             │ Archeology                           │
│ Jerusalem       │ Palestine         │ Cultural Heritage                    │
└─────────────────┴───────────────────┴──────────────────────────────────────┘
"""

