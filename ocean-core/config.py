"""
OCEAN CORE 8030 - CONFIGURATION
================================
Centralized configuration for all Ocean Core systems
"""

import os
from enum import Enum

# ============================================================================
# ENVIRONMENT
# ============================================================================

ENV = os.getenv("ENVIRONMENT", "production")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============================================================================
# SERVICE CONFIGURATION
# ============================================================================

SERVICE_NAME = "Curiosity Ocean 8030"
SERVICE_VERSION = "2.0.0"
SERVICE_PORT = int(os.getenv("OCEAN_CORE_PORT", "8030"))
SERVICE_HOST = os.getenv("OCEAN_CORE_HOST", "0.0.0.0")

# ============================================================================
# DATA SOURCES CONFIGURATION
# ============================================================================

class DataSourceConfig:
    """Configuration for data sources"""
    
    # Location Labs - 23 Laboratories with Specific Functions
    LOCATION_LABS_ENABLED = True
    LOCATION_LABS_LABS = {
        "Elbasan_AI": {"name": "Elbasan AI Lab", "function": "Artificial Intelligence & Machine Learning", "location": "Elbasan", "type": "AI"},
        "Tirana_Medical": {"name": "Tirana Medical Lab", "function": "Medical Research & Bioscience", "location": "Tirana", "type": "Medical"},
        "Durres_IoT": {"name": "Durrës IoT Lab", "function": "Internet of Things & Sensor Networks", "location": "Durrës", "type": "IoT"},
        "Shkoder_Marine": {"name": "Shkodër Marine Lab", "function": "Marine Biology & Oceanography", "location": "Shkodër", "type": "Marine"},
        "Vlore_Environmental": {"name": "Vlorë Environmental Lab", "function": "Environmental Monitoring & Ecology", "location": "Vlorë", "type": "Environmental"},
        "Korce_Agricultural": {"name": "Korça Agricultural Lab", "function": "Agricultural Sciences & Crop Analysis", "location": "Korça", "type": "Agricultural"},
        "Sarrande_Underwater": {"name": "Sarandë Underwater Lab", "function": "Underwater Exploration & Deep Sea Research", "location": "Sarandë", "type": "Underwater"},
        "Prishtina_Security": {"name": "Prishtina Security Lab", "function": "Cybersecurity & Network Protection", "location": "Prishtina", "type": "Security"},
        "Kostur_Energy": {"name": "Kostur Energy Lab", "function": "Renewable Energy & Power Systems", "location": "Kostur", "type": "Energy"},
        "Athens_Classical": {"name": "Athens Classical Lab", "function": "Classical Studies & Historical Research", "location": "Athens", "type": "Academic"},
        "Rome_Architecture": {"name": "Rome Architecture Lab", "function": "Architectural Engineering & Design", "location": "Rome", "type": "Architecture"},
        "Zurich_Finance": {"name": "Zurich Finance Lab", "function": "Financial Analysis & Blockchain", "location": "Zurich", "type": "Finance"},
        "Beograd_Industrial": {"name": "Beograd Industrial Lab", "function": "Industrial Process Optimization", "location": "Beograd", "type": "Industrial"},
        "Sofia_Chemistry": {"name": "Sofia Chemistry Lab", "function": "Chemical Research & Material Science", "location": "Sofia", "type": "Chemistry"},
        "Zagreb_Biotech": {"name": "Zagreb Biotech Lab", "function": "Biotechnology & Genetic Engineering", "location": "Zagreb", "type": "Biotech"},
        "Ljubljana_Quantum": {"name": "Ljubljana Quantum Lab", "function": "Quantum Computing & Physics", "location": "Ljubljana", "type": "Quantum"},
        "Vienna_Neuroscience": {"name": "Vienna Neuroscience Lab", "function": "Neuroscience & Brain Research", "location": "Vienna", "type": "Neuroscience"},
        "Prague_Robotics": {"name": "Prague Robotics Lab", "function": "Robotics & Automation Systems", "location": "Prague", "type": "Robotics"},
        "Budapest_Data": {"name": "Budapest Data Lab", "function": "Big Data Analytics & Visualization", "location": "Budapest", "type": "Data"},
        "Bucharest_Nanotechnology": {"name": "Bucharest Nanotechnology Lab", "function": "Nanotechnology & Nanomaterials", "location": "Bucharest", "type": "Nanotechnology"},
        "Istanbul_Trade": {"name": "Istanbul Trade Lab", "function": "International Trade & Logistics", "location": "Istanbul", "type": "Trade"},
        "Cairo_Archeology": {"name": "Cairo Archeology Lab", "function": "Archeological Research & Preservation", "location": "Cairo", "type": "Archeology"},
        "Jerusalem_Heritage": {"name": "Jerusalem Heritage Lab", "function": "Cultural Heritage & Restoration", "location": "Jerusalem", "type": "Heritage"},
    }
    
    # Agent Telemetry
    AGENT_TELEMETRY_ENABLED = True
    AGENTS = ["alba", "albi", "blerina", "agiem", "asi"]
    
    # Cycle Data
    CYCLE_DATA_ENABLED = True
    
    # Excel Data
    EXCEL_DATA_ENABLED = True
    
    # System Metrics
    SYSTEM_METRICS_ENABLED = True

# ============================================================================
# EXTERNAL API CONFIGURATION
# ============================================================================

# ============================================================================
# AI SYSTEM PROMPTS & LANGUAGE CONFIGURATION
# ============================================================================

OCEAN_SYSTEM_PROMPT = """You are Curiosity Ocean, a highly intelligent multilingual AI assistant developed by ABA GmbH (Kloud).

**CRITICAL RULES:**
1. ALWAYS detect the user's language and respond in the SAME language
2. NEVER mix languages in your response
3. Be professional, accurate, and helpful
4. If you don't know something, admit it honestly
5. For technical questions (hosting, services, domains), provide clear actionable answers

**LANGUAGE HANDLING:**
- German question → German answer
- English question → English answer  
- Albanian question → Albanian answer
- French question → French answer
- Detect language automatically, never switch mid-response

**TONE:**
- Professional but approachable
- Clear and structured responses
- Technical accuracy is paramount
- No hallucinations or made-up information

**EXAMPLES:**
User (DE): "Was ist Strato.de?"
Assistant (DE): "Strato.de ist ein deutscher Web-Hosting-Anbieter..."

User (EN): "What is Strato.de?"
Assistant (EN): "Strato.de is a German web hosting provider..."

User (SQ): "Çfarë është Strato.de?"
Assistant (SQ): "Strato.de është një ofertues gjerman i hosting-ut web..."
"""

LANGUAGE_CODES = {
    "sq": "Albanian",
    "en": "English",
    "de": "German",
    "fr": "French",
    "it": "Italian",
    "es": "Spanish",
    "pt": "Portuguese",
    "nl": "Dutch",
    "pl": "Polish",
    "tr": "Turkish",
}

class ExternalAPIsConfig:
    """Configuration for external APIs"""
    
    # API Timeouts (seconds)
    DEFAULT_TIMEOUT = 10
    WIKIPEDIA_TIMEOUT = 15
    ARXIV_TIMEOUT = 15
    PUBMED_TIMEOUT = 20
    GITHUB_TIMEOUT = 15
    DBPEDIA_TIMEOUT = 20
    
    # Result limits
    DEFAULT_LIMIT = 5
    MAX_LIMIT = 20
    
    # APIs
    WIKIPEDIA_ENABLED = True
    ARXIV_ENABLED = True
    PUBMED_ENABLED = True
    GITHUB_ENABLED = True
    DBPEDIA_ENABLED = True
    
    # Retry configuration
    RETRY_ATTEMPTS = 2
    RETRY_DELAY = 1  # seconds

# ============================================================================
# QUERY PROCESSOR CONFIGURATION
# ============================================================================

class QueryProcessorConfig:
    """Configuration for query processing"""
    
    # Intent detection - keyword patterns
    ENABLE_INTENT_DETECTION = True
    ENABLE_ENTITY_EXTRACTION = True
    ENABLE_POLICY_FILTERING = True
    
    # Policy rules
    PROHIBITED_KEYWORDS = [
        "password", "api_key", "secret", "token", "credential",
        "customer_data", "personal_data", "pii", "ssn"
    ]
    
    # Entity recognition
    KNOWN_LABS = [
        "Elbasan_AI", "Tirana_Medical", "Durres_IoT", "Shkoder_Marine", "Vlore_Environmental",
        "Korce_Agricultural", "Sarrande_Underwater", "Prishtina_Security", "Kostur_Energy",
        "Athens_Classical", "Rome_Architecture", "Zurich_Finance", "Beograd_Industrial",
        "Sofia_Chemistry", "Zagreb_Biotech", "Ljubljana_Quantum", "Vienna_Neuroscience",
        "Prague_Robotics", "Budapest_Data", "Bucharest_Nanotechnology", "Istanbul_Trade",
        "Cairo_Archeology", "Jerusalem_Heritage"
    ]
    
    KNOWN_AGENTS = ["alba", "albi", "blerina", "agiem", "asi"]
    KNOWN_DOMAINS = [
        "university", "medical", "research", "marine",
        "agricultural", "ecological", "tech"
    ]

# ============================================================================
# KNOWLEDGE ENGINE CONFIGURATION
# ============================================================================

class KnowledgeEngineConfig:
    """Configuration for knowledge engine"""
    
    # Source weighting (0.0 - 1.0)
    INTERNAL_WEIGHT = 1.0
    EXTERNAL_WEIGHT = 0.5
    
    # Aggregation
    PARALLEL_QUERIES = True
    CACHE_RESPONSES = True
    CACHE_TTL_SECONDS = 300
    
    # Response generation
    INCLUDE_CURIOSITY_THREADS = True
    MAX_FINDINGS = 10
    MIN_CONFIDENCE = 0.3

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": LOG_LEVEL,
            "formatter": "default"
        }
    },
    "root": {
        "level": LOG_LEVEL,
        "handlers": ["console"]
    }
}

# ============================================================================
# API ENDPOINTS
# ============================================================================

ENDPOINTS = {
    "root": "/",
    "status": "/api/status",
    "sources": "/api/sources",
    "query": "/api/query",
    "labs": "/api/labs",
    "agents": "/api/agents",
    "threads": "/api/threads/{topic}",
    "health": "/health",
    "docs": "/api/docs",
    "openapi": "/api/openapi.json"
}

# ============================================================================
# INTEGRATION WITH MAIN.PY
# ============================================================================

# If running with main.py proxy
MAIN_API_URL = os.getenv("MAIN_API_URL", "http://localhost:8000")
OCEAN_CORE_URL = os.getenv("OCEAN_CORE_URL", f"http://localhost:{SERVICE_PORT}")

# Proxy settings
PROXY_ENABLED = os.getenv("PROXY_ENABLED", "true").lower() == "true"
PROXY_TIMEOUT = int(os.getenv("PROXY_TIMEOUT", "30"))

# ============================================================================
# SECURITY
# ============================================================================

CORS_ORIGINS = [
    "http://localhost:8000",
    "http://localhost:8030",
    "http://localhost:3000",
    "*"  # Allow all for development
]

ALLOW_CREDENTIALS = True
ALLOW_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
ALLOW_HEADERS = ["*"]

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

# Connection pooling
CONNECTION_POOL_SIZE = 10
CONNECTION_POOL_TIMEOUT = 30

# Request processing
MAX_CONCURRENT_QUERIES = 50
QUERY_QUEUE_SIZE = 100
QUERY_TIMEOUT = 30  # seconds

# ============================================================================
# TESTING
# ============================================================================

TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

# Test data
TEST_QUERIES = [
    "What labs do we have?",
    "How are ALBA and ALBI performing?",
    "What is the status of our system?",
    "What is consciousness?"
]

# ============================================================================
# FEATURE FLAGS
# ============================================================================

class FeatureFlags:
    """Feature toggles"""
    
    ENABLE_LOCATION_LABS = True
    ENABLE_AGENT_TELEMETRY = True
    ENABLE_WIKIPEDIA_INTEGRATION = True
    ENABLE_ARXIV_INTEGRATION = True
    ENABLE_PUBMED_INTEGRATION = True
    ENABLE_GITHUB_INTEGRATION = True
    ENABLE_CURIOSITY_THREADS = True
    ENABLE_RESPONSE_CACHING = True
    ENABLE_QUERY_LOGGING = True

# ============================================================================
# PRINT CONFIG
# ============================================================================

def print_config():
    """Print current configuration"""
    print(f"""
🌊 OCEAN CORE 8030 - CONFIGURATION
{'='*50}
Environment: {ENV}
Debug: {DEBUG}
Service: {SERVICE_NAME} v{SERVICE_VERSION}
Host: {SERVICE_HOST}:{SERVICE_PORT}
{'='*50}

📊 DATA SOURCES:
  - Location Labs: {DataSourceConfig.LOCATION_LABS_ENABLED}
  - Agent Telemetry: {DataSourceConfig.AGENT_TELEMETRY_ENABLED}
  - Cycle Data: {DataSourceConfig.CYCLE_DATA_ENABLED}
  - System Metrics: {DataSourceConfig.SYSTEM_METRICS_ENABLED}

🔗 EXTERNAL APIs:
  - Wikipedia: {ExternalAPIsConfig.WIKIPEDIA_ENABLED}
  - Arxiv: {ExternalAPIsConfig.ARXIV_ENABLED}
  - PubMed: {ExternalAPIsConfig.PUBMED_ENABLED}
  - GitHub: {ExternalAPIsConfig.GITHUB_ENABLED}

🧠 KNOWLEDGE ENGINE:
  - Internal Weight: {KnowledgeEngineConfig.INTERNAL_WEIGHT}
  - External Weight: {KnowledgeEngineConfig.EXTERNAL_WEIGHT}
  - Caching: {KnowledgeEngineConfig.CACHE_RESPONSES}

{'='*50}
""")

if __name__ == "__main__":
    print_config()

