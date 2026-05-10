# -*- coding: utf-8 -*-
"""
[FIX] SERVICE REGISTRY - All 56+ Kloud Microservices
====================================================
Central registry of ALL microservices from docker-compose.microservices.yml

Structure:
 DATABASES & INFRASTRUCTURE (Postgres, Redis, Neo4j, VictoriaMetrics)
 ASI TRINITY (ALBA, ALBI, JONA, ASI)
 CORE ENGINES (Ocean-Core, Alphabet-Layers, LIAM, ALDA)
 14 PERSONAS (Medical, IoT, Security, etc.)
 AGIEM + 7 DATASOURCES (Europe, Americas, Asia, India, Africa, Oceania, Antarctica)
 23 LABORATORIES (City-Named: Elbasan, Tirana, Rome, Athens, etc.)
 SAAS & MARKETPLACE
 SERVICES (Reporting, Excel, Behavioral, Economy, Aviation)
 FRONTEND & API GATEWAY

Version: 2.0.1 - FULL HYBRID REGISTRY
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
import asyncio
import logging

logger = logging.getLogger("service_registry")


@dataclass
class MicroService:
    """A single microservice definition"""

    name: str
    port: int
    description: str
    category: str
    file: str = ""
    region: str = ""
    country: str = ""
    health_endpoint: str = "/health"
    api_docs: str = "/docs"
    capabilities: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    is_core: bool = False
    status: str = "unknown"
    last_check: Optional[datetime] = None


# =============================================================================
# COMPLETE SERVICE REGISTRY - All 56+ Microservices from docker-compose
# =============================================================================

SERVICES: Dict[str, MicroService] = {
    # =========================================================================
    # DATABASES & INFRASTRUCTURE (4 services)
    # =========================================================================
    "postgres": MicroService(
        name="PostgreSQL",
        port=5432,
        description="Primary relational database - klouddb",
        category="database",
        is_core=True,
        capabilities=["sql", "transactions", "persistence", "queries"],
    ),
    "redis": MicroService(
        name="Redis",
        port=6379,
        description="In-memory cache and message broker",
        category="database",
        is_core=True,
        capabilities=["cache", "pubsub", "sessions", "queues"],
    ),
    "neo4j": MicroService(
        name="Neo4j",
        port=7474,
        description="Graph database for knowledge relationships",
        category="database",
        is_core=True,
        capabilities=["graph", "relationships", "cypher", "knowledge_graph"],
    ),
    "victoriametrics": MicroService(
        name="VictoriaMetrics",
        port=8428,
        description="Long-term metrics storage - Prometheus compatible",
        category="monitoring",
        capabilities=["metrics", "timeseries", "prometheus", "retention"],
    ),
    # =========================================================================
    # ASI TRINITY - Core AI (4 services)
    # =========================================================================
    "alba": MicroService(
        name="ALBA",
        port=5555,
        description="Analytical Intelligence - Data collection & signal processing",
        category="asi_trinity",
        is_core=True,
        file="alba_service_5555.py",
        capabilities=["analysis", "patterns", "signals", "data_processing", "eeg"],
    ),
    "albi": MicroService(
        name="ALBI",
        port=6680,
        description="Creative Intelligence - Adaptive learning & analytics",
        category="asi_trinity",
        is_core=True,
        file="albi_service_6680.py",
        capabilities=["creativity", "learning", "analytics", "adaptation"],
    ),
    "jona": MicroService(
        name="JONA",
        port=7777,
        description="Master Coordinator - Sandbox & synthesis",
        category="asi_trinity",
        is_core=True,
        file="jona_server.py",
        capabilities=["orchestration", "sandbox", "synthesis", "coordination"],
    ),
    "asi": MicroService(
        name="ASI",
        port=9094,
        description="Artificial Super Intelligence - Combined Trinity",
        category="asi_trinity",
        is_core=True,
        file="asi_api_server.py",
        capabilities=["superintelligence", "reasoning", "planning", "strategy"],
    ),
    # =========================================================================
    # CORE ENGINES (7 services)
    # =========================================================================
    "ocean-core": MicroService(
        name="Ocean Core",
        port=8030,
        description="Knowledge Engine & Curiosity AI - Central brain",
        category="core",
        is_core=True,
        file="ocean_api.py",
        capabilities=["knowledge", "chat", "curiosity", "personas", "learning"],
    ),
    "clx-i": MicroService(
        name="CLX.I Multi-Model Engine",
        port=4444,
        description="3 CLX models enterprise router - kloud-ocean:v2, llama3.1:8b, gpt-oss:120b (microservice 8031)",
        category="core",
        is_core=True,
        file="clx_i_api.py",
        health_endpoint="/health",
        api_docs="/docs",
        capabilities=[
            "local_ai",
            "multi_model",
            "auto_selection",
            "balanced_mode",
            "deep_analysis",
            "chat",
            "generate",
            "llama3",
            "gpt_oss_120b",
        ],
    ),
    "alphabet-layers": MicroService(
        name="Alphabet Layers",
        port=8061,
        description="61 Mathematical Layers - Greek+Albanian BINARY (CBOR2/MessagePack)",
        category="core",
        is_core=True,
        file="alphabet_layers.py",
        capabilities=["math", "binary", "cbor", "layers", "algebra"],
    ),
    "liam": MicroService(
        name="LIAM",
        port=8062,
        description="Labor Intelligence Array Matrix - Binary Algebra, No Loops",
        category="core",
        is_core=True,
        file="liam_server.py",
        capabilities=["binary_algebra", "arrays", "matrix", "no_loops"],
    ),
    "alda": MicroService(
        name="ALDA",
        port=8063,
        description="Artificial Labor Determined Array - Deterministic Scheduling",
        category="core",
        is_core=True,
        file="alda_server.py",
        capabilities=["scheduling", "deterministic", "labor", "orchestration"],
    ),
    "alba-idle": MicroService(
        name="ALBA Idle",
        port=8031,
        description="Technical Status Chat - System monitoring interface",
        category="core",
        file="alba_idle_chat.py",
        capabilities=["status", "monitoring", "chat", "diagnostics"],
    ),
    "blerina": MicroService(
        name="Blerina",
        port=8035,
        description="Document Intelligence & Narrative Engine",
        category="core",
        file="blerina_reformatter.py",
        capabilities=["documents", "narrative", "intelligence", "youtube"],
    ),
    # =========================================================================
    # 14 PERSONAS - Specialist Modules (Single Container :9200)
    # =========================================================================
    "personas": MicroService(
        name="Personas Engine",
        port=9200,
        description="14 Specialist Personas - Medical, IoT, Security, Architecture, etc.",
        category="personas",
        is_core=True,
        file="personas_api.py",
        capabilities=[
            "medical_science",
            "lora_iot",
            "security",
            "systems_architecture",
            "natural_science",
            "industrial_process",
            "agi_analyst",
            "business_analyst",
            "smart_human",
            "academic",
            "media",
            "culture",
            "hobby",
            "entertainment",
        ],
    ),
    # =========================================================================
    # AGIEM + 8 DATA SOURCE CONTAINERS (Per Continent)
    # =========================================================================
    "agiem": MicroService(
        name="AGIEM",
        port=9300,
        description="AGI Ecosystem Manager - Connected to all data sources",
        category="agiem",
        is_core=True,
        file="agiem_core.py",
        capabilities=["ecosystem", "manager", "agi", "coordination", "scaling"],
    ),
    "datasource-europe": MicroService(
        name="DataSource Europe",
        port=9301,
        description="European & Eastern European data sources",
        category="datasource",
        region="europe",
        capabilities=["eurostat", "ecb", "balkans", "eu_open_data"],
    ),
    "datasource-americas": MicroService(
        name="DataSource Americas",
        port=9302,
        description="North, Central, South America + Caribbean data",
        category="datasource",
        region="americas",
        capabilities=["us_census", "fred", "brazil", "canada"],
    ),
    "datasource-asia-china": MicroService(
        name="DataSource Asia & China",
        port=9303,
        description="China, Japan, Korea, Southeast Asia data",
        category="datasource",
        region="asia",
        capabilities=["china_nbs", "japan_stat", "kostat", "asean"],
    ),
    "datasource-india-south-asia": MicroService(
        name="DataSource India & South Asia",
        port=9304,
        description="India, Pakistan, Bangladesh, Sri Lanka data",
        category="datasource",
        region="india",
        capabilities=["india_data", "rbi", "pakistan", "south_asia"],
    ),
    "datasource-africa-middle-east": MicroService(
        name="DataSource Africa & Middle East",
        port=9305,
        description="African + Arab World data sources",
        category="datasource",
        region="africa",
        capabilities=["afdb", "saudi", "uae", "nigeria", "south_africa"],
    ),
    "datasource-oceania-pacific": MicroService(
        name="DataSource Oceania & Pacific",
        port=9306,
        description="Australia, New Zealand, Pacific Islands data",
        category="datasource",
        region="oceania",
        capabilities=["abs_australia", "stats_nz", "pacific_spc"],
    ),
    "datasource-central-asia": MicroService(
        name="DataSource Central Asia",
        port=9307,
        description="Kazakhstan, Uzbekistan, Caucasus data",
        category="datasource",
        region="central_asia",
        capabilities=["kazstat", "uzstat", "georgia", "armenia"],
    ),
    # =========================================================================
    # 23 LABORATORIES - City-Named Research Labs (9101-9123)
    # =========================================================================
    # ALBANIA LABS (7)
    "lab-elbasan": MicroService(
        name="Elbasan AI Lab",
        port=9101,
        description="Artificial Intelligence & Machine Learning",
        category="laboratory",
        region="balkans",
        country="albania",
        capabilities=["ai", "ml", "research", "development"],
    ),
    "lab-tirana": MicroService(
        name="Tirana Medical Lab",
        port=9102,
        description="Medical Research & Bioscience",
        category="laboratory",
        region="balkans",
        country="albania",
        capabilities=["medical", "bioscience", "health", "research"],
    ),
    "lab-durres": MicroService(
        name="Durrs IoT Lab",
        port=9103,
        description="Internet of Things & Sensor Networks",
        category="laboratory",
        region="balkans",
        country="albania",
        capabilities=["iot", "sensors", "networks", "smart_devices"],
    ),
    "lab-vlore": MicroService(
        name="Vlor Environmental Lab",
        port=9104,
        description="Environmental Monitoring & Ecology",
        category="laboratory",
        region="balkans",
        country="albania",
        capabilities=["environment", "ecology", "monitoring", "climate"],
    ),
    "lab-shkoder": MicroService(
        name="Shkodr Marine Lab",
        port=9105,
        description="Marine Biology & Oceanography",
        category="laboratory",
        region="balkans",
        country="albania",
        capabilities=["marine", "oceanography", "biology", "aquatic"],
    ),
    "lab-korce": MicroService(
        name="Kora Agricultural Lab",
        port=9106,
        description="Agricultural Sciences & Crop Analysis",
        category="laboratory",
        region="balkans",
        country="albania",
        capabilities=["agriculture", "crops", "soil", "farming"],
    ),
    "lab-saranda": MicroService(
        name="Sarand Underwater Lab",
        port=9107,
        description="Underwater Exploration & Deep Sea Research",
        category="laboratory",
        region="balkans",
        country="albania",
        capabilities=["underwater", "deep_sea", "exploration", "diving"],
    ),
    # KOSOVO LAB (1)
    "lab-prishtina": MicroService(
        name="Prishtina Security Lab",
        port=9108,
        description="Cybersecurity & Network Protection",
        category="laboratory",
        region="balkans",
        country="kosovo",
        capabilities=["cybersecurity", "network", "protection", "defense"],
    ),
    # NORTH MACEDONIA LAB (1)
    "lab-kostur": MicroService(
        name="Kostur Energy Lab",
        port=9109,
        description="Renewable Energy & Power Systems",
        category="laboratory",
        region="balkans",
        country="north_macedonia",
        capabilities=["energy", "renewable", "power", "solar"],
    ),
    # GREECE LAB (1)
    "lab-athens": MicroService(
        name="Athens Classical Lab",
        port=9110,
        description="Classical Studies & Historical Research",
        category="laboratory",
        region="europe",
        country="greece",
        capabilities=["classical", "history", "archaeology", "research"],
    ),
    # ITALY LAB (1)
    "lab-rome": MicroService(
        name="Rome Architecture Lab",
        port=9111,
        description="Architectural Engineering & Design",
        category="laboratory",
        region="europe",
        country="italy",
        capabilities=["architecture", "engineering", "design", "building"],
    ),
    # SWITZERLAND LAB (1)
    "lab-zurich": MicroService(
        name="Zurich Finance Lab",
        port=9112,
        description="Financial Analysis & Blockchain",
        category="laboratory",
        region="europe",
        country="switzerland",
        capabilities=["finance", "blockchain", "banking", "crypto"],
    ),
    # SERBIA LAB (1)
    "lab-beograd": MicroService(
        name="Beograd Industrial Lab",
        port=9113,
        description="Industrial Process Optimization",
        category="laboratory",
        region="balkans",
        country="serbia",
        capabilities=["industrial", "optimization", "manufacturing", "processes"],
    ),
    # BULGARIA LAB (1)
    "lab-sofia": MicroService(
        name="Sofia Chemistry Lab",
        port=9114,
        description="Chemical Research & Material Science",
        category="laboratory",
        region="europe",
        country="bulgaria",
        capabilities=["chemistry", "materials", "compounds", "research"],
    ),
    # CROATIA LAB (1)
    "lab-zagreb": MicroService(
        name="Zagreb Biotech Lab",
        port=9115,
        description="Biotechnology & Genetic Engineering",
        category="laboratory",
        region="balkans",
        country="croatia",
        capabilities=["biotech", "genetics", "dna", "engineering"],
    ),
    # SLOVENIA LAB (1)
    "lab-ljubljana": MicroService(
        name="Ljubljana Quantum Lab",
        port=9116,
        description="Quantum Computing & Physics",
        category="laboratory",
        region="europe",
        country="slovenia",
        capabilities=["quantum", "computing", "physics", "research"],
    ),
    # AUSTRIA LAB (1)
    "lab-vienna": MicroService(
        name="Vienna Neuroscience Lab",
        port=9117,
        description="Neuroscience & Brain Research",
        category="laboratory",
        region="europe",
        country="austria",
        capabilities=["neuroscience", "brain", "cognition", "research"],
    ),
    # CZECH REPUBLIC LAB (1)
    "lab-prague": MicroService(
        name="Prague Robotics Lab",
        port=9118,
        description="Robotics & Automation Systems",
        category="laboratory",
        region="europe",
        country="czech",
        capabilities=["robotics", "automation", "systems", "ai"],
    ),
    # HUNGARY LAB (1)
    "lab-budapest": MicroService(
        name="Budapest Data Lab",
        port=9119,
        description="Big Data Analytics & Visualization",
        category="laboratory",
        region="europe",
        country="hungary",
        capabilities=["big_data", "analytics", "visualization", "processing"],
    ),
    # ROMANIA LAB (1)
    "lab-bucharest": MicroService(
        name="Bucharest Nanotechnology Lab",
        port=9120,
        description="Nanotechnology & Nanomaterials",
        category="laboratory",
        region="europe",
        country="romania",
        capabilities=["nanotechnology", "nanomaterials", "research", "science"],
    ),
    # TURKEY LAB (1)
    "lab-istanbul": MicroService(
        name="Istanbul Trade Lab",
        port=9121,
        description="International Trade & Logistics",
        category="laboratory",
        region="middle_east",
        country="turkey",
        capabilities=["trade", "logistics", "international", "commerce"],
    ),
    # EGYPT LAB (1)
    "lab-cairo": MicroService(
        name="Cairo Archeology Lab",
        port=9122,
        description="Archeological Research & Preservation",
        category="laboratory",
        region="africa",
        country="egypt",
        capabilities=["archeology", "preservation", "history", "artifacts"],
    ),
    # PALESTINE LAB (1)
    "lab-jerusalem": MicroService(
        name="Jerusalem Heritage Lab",
        port=9123,
        description="Cultural Heritage & Restoration",
        category="laboratory",
        region="middle_east",
        country="palestine",
        capabilities=["heritage", "restoration", "culture", "preservation"],
    ),
    # =========================================================================
    # SAAS & MARKETPLACE
    # =========================================================================
    "saas-api": MicroService(
        name="SaaS API",
        port=8040,
        description="SaaS Production API - Commercial endpoints",
        category="saas",
        is_core=True,
        file="saas_api.py",
        capabilities=["saas", "production", "api", "commercial"],
    ),
    "marketplace": MicroService(
        name="Marketplace",
        port=8004,
        description="API Keys, Billing, Stripe Integration",
        category="saas",
        file="marketplace_api.py",
        capabilities=["billing", "subscriptions", "api_keys", "stripe"],
    ),
    # =========================================================================
    # SERVICES (Reporting, Excel, Behavioral, Economy, Aviation)
    # =========================================================================
    "reporting": MicroService(
        name="Reporting Service",
        port=8001,
        description="Excel, PowerPoint, Dashboard Reports",
        category="services",
        file="reporting_api.py",
        capabilities=["excel", "powerpoint", "reports", "exports"],
    ),
    "excel": MicroService(
        name="Excel Microservice",
        port=8002,
        description="Excel File Processing & Generation",
        category="services",
        file="services/excel",
        capabilities=["excel", "spreadsheets", "imports", "exports"],
    ),
    "behavioral": MicroService(
        name="Behavioral Science",
        port=8003,
        description="Mood, Habits, Focus Analytics",
        category="services",
        file="behavioral_science_api.py",
        capabilities=["mood", "habits", "focus", "behavior"],
    ),
    "economy": MicroService(
        name="Economy Engine",
        port=9093,
        description="Credits, Usage, Billing Economy",
        category="services",
        file="economy_api_server.py",
        capabilities=["credits", "usage", "billing", "economy"],
    ),
    "aviation": MicroService(
        name="Aviation Weather",
        port=8080,
        description="Aviation Weather Data - METAR, TAF, NOTAM",
        category="services",
        file="services/aviation-weather",
        capabilities=["metar", "taf", "aviation", "weather", "notam"],
    ),
    # =========================================================================
    # FRONTEND & API GATEWAY
    # =========================================================================
    "api": MicroService(
        name="Backend API",
        port=8000,
        description="Main REST API - Entry point for frontend",
        category="gateway",
        is_core=True,
        file="apps/api/main.py",
        capabilities=["rest", "authentication", "authorization", "crud"],
    ),
    "web": MicroService(
        name="Web Frontend",
        port=3000,
        description="Next.js 16 Dashboard - User interface",
        category="frontend",
        is_core=True,
        file="apps/web",
        capabilities=["dashboard", "ui", "visualization", "modules"],
    ),
    # =========================================================================
    # NEURO & BRAIN SCIENCE
    "neurosonix": MicroService(
        name="NeuroSonix",
        port=8006,
        description="Industrial Neuroscience - EEG, brain analysis",
        category="neuroscience",
        file="neurosonix_industrial_api.py",
        capabilities=["eeg", "brain_analysis", "cognitive", "neuro"],
    ),
    "brain": MicroService(
        name="Brain Engine",
        port=8015,
        description="Neural processing and brain simulations",
        category="neuroscience",
        file="apps/api/brain_engine.py",
        capabilities=["neural_network", "simulation", "processing"],
    ),
    "brainsync": MicroService(
        name="BrainSync",
        port=8025,
        description="Brain state synchronization",
        category="neuroscience",
        file="backend/neuro/brainsync_engine.py",
        capabilities=["synchronization", "coherence", "brainwaves"],
    ),
    "hps": MicroService(
        name="HPS Engine",
        port=8022,
        description="Human Performance System - Cognitive optimization",
        category="neuroscience",
        file="apps/api/neuro/hps_engine.py",
        capabilities=["performance", "optimization", "cognitive"],
    ),
    # -----------------------------
    # BEHAVIORAL & WELLNESS
    # -----------------------------
    "behavioral": MicroService(
        name="Behavioral Science",
        port=8003,
        description="Mood, habits, focus analytics",
        category="wellness",
        file="behavioral_science_api.py",
        capabilities=["mood", "habits", "focus", "behavior"],
    ),
    "mood": MicroService(
        name="Mood Engine",
        port=8023,
        description="Mood tracking and analysis",
        category="wellness",
        file="backend/neuro/moodboard_engine.py",
        capabilities=["mood_tracking", "emotions", "sentiment"],
    ),
    "energy": MicroService(
        name="Energy Engine",
        port=8024,
        description="Energy levels and vitality tracking",
        category="wellness",
        file="backend/neuro/energy_engine.py",
        capabilities=["energy", "vitality", "fatigue"],
    ),
    "coach": MicroService(
        name="Coaching Engine",
        port=8020,
        description="AI coaching and guidance",
        category="wellness",
        file="apps/api/modules/coaching_engine.py",
        capabilities=["coaching", "guidance", "recommendations"],
    ),
    # -----------------------------
    # BIOMETRICS
    # -----------------------------
    "biometric": MicroService(
        name="Biometric API",
        port=8009,
        description="Biometric data analysis",
        category="biometric",
        file="hybrid_biometric_api.py",
        capabilities=["biometrics", "heart_rate", "hrv", "stress"],
    ),
    # -----------------------------
    # CYCLE & TIME
    # -----------------------------
    "cycle": MicroService(
        name="Cycle Engine",
        port=8005,
        description="Advanced cycle alignments - Circadian, ultradian",
        category="cycles",
        file="cycle_engine.py",
        capabilities=["cycles", "circadian", "ultradian", "alignment"],
    ),
    # -----------------------------
    # KNOWLEDGE & CURIOSITY
    # -----------------------------
    "curiosity": MicroService(
        name="Curiosity Ocean",
        port=8011,
        description="Knowledge discovery and exploration",
        category="knowledge",
        file="services/curiosity_ocean",
        capabilities=["discovery", "exploration", "questions"],
    ),
    "knowledge": MicroService(
        name="Knowledge Index",
        port=8012,
        description="Search and indexing service",
        category="knowledge",
        file="services/knowledge_index",
        capabilities=["search", "indexing", "retrieval"],
    ),
    "agi": MicroService(
        name="Internal AGI",
        port=8014,
        description="Advanced General Intelligence",
        category="ai_advanced",
        file="services/internal_agi",
        capabilities=["agi", "reasoning", "learning", "adaptation"],
    ),
    # -----------------------------
    # ANALYTICS & DATA
    # -----------------------------
    "analytics": MicroService(
        name="Advanced Analytics",
        port=8007,
        description="Data science and analytics",
        category="analytics",
        file="advanced_analytics_api.py",
        capabilities=["analytics", "data_science", "ml", "statistics"],
    ),
    # -----------------------------
    # BUSINESS & SAAS
    # -----------------------------
    "saas": MicroService(
        name="SaaS Engine",
        port=8008,
        description="SaaS signal processing",
        category="business",
        file="saas_services_orchestrator.py",
        capabilities=["saas", "signals", "processing"],
    ),
    "marketplace": MicroService(
        name="Marketplace",
        port=8004,
        description="API keys, billing, subscriptions",
        category="business",
        file="marketplace_api.py",
        capabilities=["billing", "subscriptions", "api_keys", "stripe"],
    ),
    "economy": MicroService(
        name="Economy",
        port=9093,
        description="Credits, usage, billing",
        category="business",
        file="economy_api_server.py",
        capabilities=["credits", "usage", "billing", "economy"],
    ),
    # -----------------------------
    # REPORTING & DOCS
    # -----------------------------
    "reporting": MicroService(
        name="Reporting",
        port=8001,
        description="Excel, PowerPoint, dashboard reports",
        category="reporting",
        file="reporting_api.py",
        capabilities=["excel", "powerpoint", "reports", "exports"],
    ),
    "excel": MicroService(
        name="Excel Microservice",
        port=8002,
        description="Excel file processing",
        category="reporting",
        file="services/excel",
        capabilities=["excel", "spreadsheets", "imports", "exports"],
    ),
    # -----------------------------
    # USER & AUTH
    # -----------------------------
    "userdata": MicroService(
        name="User Data API",
        port=8010,
        description="User management and data",
        category="auth",
        file="user_data_api.py",
        capabilities=["users", "profiles", "data", "management"],
    ),
    # -----------------------------
    # INTEGRATIONS
    # -----------------------------
    "slack": MicroService(
        name="Slack Integration",
        port=8016,
        description="Slack bot and notifications",
        category="integrations",
        file="slack_integration_service.py",
        capabilities=["slack", "notifications", "bot", "messaging"],
    ),
    "youtube": MicroService(
        name="YouTube Insights",
        port=8018,
        description="YouTube data analysis",
        category="integrations",
        file="youtube_insight_engine.py",
        capabilities=["youtube", "video", "analytics"],
    ),
    # -----------------------------
    # TELEMETRY & MONITORING
    # -----------------------------
    "agiem": MicroService(
        name="AGIEM Telemetry",
        port=8017,
        description="Agent telemetry and monitoring",
        category="monitoring",
        file="agiem_telemetry_service.py",
        capabilities=["telemetry", "agents", "monitoring"],
    ),
    # -----------------------------
    # NETWORK & MESH
    # -----------------------------
    "mesh": MicroService(
        name="Mesh Network",
        port=8019,
        description="Distributed mesh networking",
        category="network",
        file="backend/mesh/server.py",
        capabilities=["mesh", "p2p", "distributed"],
    ),
    "balancer": MicroService(
        name="Load Balancer",
        port=3334,
        description="Request load balancing",
        category="network",
        file="balancer_nodes_3334.py",
        capabilities=["load_balancing", "routing", "health_checks"],
    ),
    # -----------------------------
    # SPECIALIZED
    # -----------------------------
    "aviation": MicroService(
        name="Aviation Weather",
        port=8080,
        description="Aviation weather data",
        category="specialized",
        file="services/aviation-weather",
        capabilities=["metar", "taf", "aviation", "weather"],
    ),
    "concept": MicroService(
        name="Concept Gap",
        port=8021,
        description="Concept gap analysis",
        category="specialized",
        file="services/concept_gap/service.py",
        capabilities=["concepts", "gaps", "analysis"],
    ),
    "liam": MicroService(
        name="LIAM Server",
        port=7788,
        description="LIAM language model server",
        category="ai_core",
        file="liam_server.py",
        capabilities=["language", "model", "inference"],
    ),
    "alda": MicroService(
        name="ALDA Server",
        port=7790,
        description="ALDA data aggregation",
        category="ai_core",
        file="alda_server.py",
        capabilities=["aggregation", "data", "processing"],
    ),
}


class ServiceRegistry:
    """Central registry for all microservices"""

    def __init__(self):
        self.services = SERVICES
        self._http_client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=5.0)
        return self._http_client

    def get_all_services(self) -> Dict[str, MicroService]:
        return self.services

    def get_service(self, name: str) -> Optional[MicroService]:
        return self.services.get(name.lower())

    def get_by_category(self, category: str) -> List[MicroService]:
        return [s for s in self.services.values() if s.category == category]

    def get_by_capability(self, capability: str) -> List[MicroService]:
        return [s for s in self.services.values() if capability in s.capabilities]

    def get_core_services(self) -> List[MicroService]:
        return [s for s in self.services.values() if s.is_core]

    def get_categories(self) -> List[str]:
        return list(set(s.category for s in self.services.values()))

    def search(self, query: str) -> List[MicroService]:
        """Search services by name, description, or capabilities"""
        query = query.lower()
        results = []
        for svc in self.services.values():
            if query in svc.name.lower() or query in svc.description.lower() or any(query in c for c in svc.capabilities):
                results.append(svc)
        return results

    async def check_health(self, service_name: str) -> Dict[str, Any]:
        """Check health of a specific service"""
        svc = self.get_service(service_name)
        if not svc:
            return {"status": "unknown", "error": "Service not found"}

        try:
            client = await self._get_client()
            url = f"http://localhost:{svc.port}{svc.health_endpoint}"
            resp = await client.get(url)
            svc.status = "healthy" if resp.status_code == 200 else "unhealthy"
            svc.last_check = datetime.now()
            return {"status": svc.status, "port": svc.port, "response_code": resp.status_code}
        except Exception as e:
            svc.status = "offline"
            svc.last_check = datetime.now()
            return {"status": "offline", "error": str(e)}

    async def check_all_health(self) -> Dict[str, str]:
        """Check health of all services"""
        results = {}
        tasks = []
        for name in self.services.keys():
            tasks.append(self.check_health(name))

        health_results = await asyncio.gather(*tasks, return_exceptions=True)
        for name, result in zip(self.services.keys(), health_results):
            if isinstance(result, Exception):
                results[name] = "error"
            else:
                results[name] = result.get("status", "unknown")

        return results

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all services"""
        categories = {}
        for svc in self.services.values():
            if svc.category not in categories:
                categories[svc.category] = []
            categories[svc.category].append(svc.name)

        return {
            "total_services": len(self.services),
            "core_services": len([s for s in self.services.values() if s.is_core]),
            "categories": categories,
            "port_range": f"{min(s.port for s in self.services.values())}-{max(s.port for s in self.services.values())}",
        }

    def to_chat_context(self) -> str:
        """Generate context string for chat AI"""
        lines = ["KLOUD MICROSERVICES REGISTRY:", ""]

        for category in sorted(self.get_categories()):
            services = self.get_by_category(category)
            lines.append(f"[PKG] {category.upper()}:")
            for svc in services:
                caps = ", ".join(svc.capabilities[:3])
                lines.append(f"  - {svc.name} (:{svc.port}): {svc.description} [{caps}]")
            lines.append("")

        return "\n".join(lines)


# Global instance
_registry: Optional[ServiceRegistry] = None


def get_service_registry() -> ServiceRegistry:
    global _registry
    if _registry is None:
        _registry = ServiceRegistry()
    return _registry


# For direct testing
if __name__ == "__main__":
    reg = get_service_registry()
    summary = reg.get_summary()
    print(f"Total Services: {summary['total_services']}")
    print(f"Core Services: {summary['core_services']}")
    print(f"Categories: {list(summary['categories'].keys())}")
    print("\nChat Context:")
    print(reg.to_chat_context()[:2000])
