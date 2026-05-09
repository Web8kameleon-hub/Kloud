"""
Knowledge Layer — FULL VERSION (31 Modules)
Curiosity Ocean AI Knowledge Base
All platform services and intents
"""

# ═══════════════════════════════════════════════════════════════════
# 1. AGENT IDENTITY — Who I Am
# ═══════════════════════════════════════════════════════════════════
AGENT_IDENTITY = {
    "name": "Curiosity Ocean",
    "emoji": "🌊",
    "platform": "https://kloud.cloud",
    "creator": "Ledjan Ahmati, Geschäftsführer - ABA GmbH (Amtsgericht Bochum HRB: 21069)",
    "identity": "Advanced AI brain of Kloud Cloud platform.",
    "mission": "Assist every user using AI, route to modules, provide documentation.",
    "behavior": "If user asks about a service → route to module. If continuation needed → provide 'how to use' docs.",
    "enterprise_rule": "Respond with clarity, route instantly, provide documentation only when needed.",
    "languages": "72+ languages via Translation Node"
}

# ═══════════════════════════════════════════════════════════════════
# 2. SERVICES — ALL 31 MODULES
# ═══════════════════════════════════════════════════════════════════
SERVICES = {
    # === AI & CHAT ===
    "curiosity-ocean": {
        "name": "Curiosity Ocean", 
        "url": "/modules/curiosity-ocean",
        "desc": "Main AI chat interface with 72 language support"
    },
    "specialized-chat": {
        "name": "Specialized Chat", 
        "url": "/modules/specialized-chat",
        "desc": "Domain-specific AI conversations"
    },
    "open-webui": {
        "name": "Open WebUI", 
        "url": "/modules/open-webui",
        "desc": "Advanced chat interface with multiple models"
    },
    
    # === NEUROSCIENCE & BIOMETRICS ===
    "eeg-analysis": {
        "name": "EEG Analysis", 
        "url": "/modules/eeg-analysis",
        "desc": "Brain wave analysis and visualization"
    },
    "neural-biofeedback": {
        "name": "Neural Biofeedback", 
        "url": "/modules/neural-biofeedback",
        "desc": "Real-time brainwave training"
    },
    "neural-synthesis": {
        "name": "Neural Synthesis", 
        "url": "/modules/neural-synthesis",
        "desc": "AI-powered neural pattern generation"
    },
    "neuroacoustic-converter": {
        "name": "Neuroacoustic Converter", 
        "url": "/modules/neuroacoustic-converter",
        "desc": "Convert brain waves to audio"
    },
    "hybrid-biometric-dashboard": {
        "name": "Hybrid Biometric Dashboard", 
        "url": "/modules/hybrid-biometric-dashboard",
        "desc": "Multi-sensor biometric monitoring"
    },
    "face-detection": {
        "name": "Face Detection", 
        "url": "/modules/face-detection",
        "desc": "AI-powered facial recognition"
    },
    "mymirror-now": {
        "name": "MyMirror Now", 
        "url": "/modules/mymirror-now",
        "desc": "Real-time self reflection with AI"
    },
    
    # === DOCUMENTS & DATA ===
    "document-tools": {
        "name": "Document Tools", 
        "url": "/modules/document-tools",
        "desc": "Excel, Word, PDF processing"
    },
    "excel-dashboard": {
        "name": "Excel Dashboard", 
        "url": "/modules/excel-dashboard",
        "desc": "Advanced Excel analytics and visualization"
    },
    "data-collection": {
        "name": "Data Collection", 
        "url": "/modules/data-collection",
        "desc": "Collect and organize data from multiple sources"
    },
    "user-data": {
        "name": "User Data", 
        "url": "/modules/user-data",
        "desc": "Personal data management"
    },
    
    # === FITNESS & HEALTH ===
    "fitness-dashboard": {
        "name": "Fitness Dashboard", 
        "url": "/modules/fitness-dashboard",
        "desc": "Track workouts, nutrition, progress"
    },
    "daily-habits": {
        "name": "Daily Habits", 
        "url": "/modules/daily-habits",
        "desc": "Habit tracking and building"
    },
    "mood-journal": {
        "name": "Mood Journal", 
        "url": "/modules/mood-journal",
        "desc": "Track emotions and mental health"
    },
    "focus-timer": {
        "name": "Focus Timer", 
        "url": "/modules/focus-timer",
        "desc": "Pomodoro and productivity timer"
    },
    
    # === IoT & INDUSTRIAL ===
    "iot-network": {
        "name": "IoT Network & Data Hub", 
        "url": "/modules/my-data-dashboard",
        "desc": "LoRa, sensors, industrial IoT monitoring"
    },
    "industrial-dashboard": {
        "name": "Industrial Dashboard", 
        "url": "/modules/industrial-dashboard",
        "desc": "Industrial metrics and monitoring"
    },
    "phone-sensors": {
        "name": "Phone Sensors", 
        "url": "/modules/phone-sensors",
        "desc": "Mobile sensor data collection"
    },
    "phone-monitor": {
        "name": "Phone Monitor", 
        "url": "/modules/phone-monitor",
        "desc": "Mobile device monitoring"
    },
    "spectrum-analyzer": {
        "name": "Spectrum Analyzer", 
        "url": "/modules/spectrum-analyzer",
        "desc": "Audio and signal spectrum analysis"
    },
    
    # === ANALYTICS & REPORTING ===
    "ocean-analytics": {
        "name": "Ocean Analytics", 
        "url": "/modules/ocean-analytics",
        "desc": "Platform-wide analytics dashboard"
    },
    "reporting-dashboard": {
        "name": "Reporting Dashboard", 
        "url": "/modules/reporting-dashboard",
        "desc": "Generate and manage reports"
    },
    
    # === WEATHER ===
    "weather-dashboard": {
        "name": "Weather Dashboard", 
        "url": "/modules/weather-dashboard",
        "desc": "Local and global weather data"
    },
    "aviation-weather": {
        "name": "Aviation Weather", 
        "url": "/modules/aviation-weather",
        "desc": "METAR, TAF, aviation forecasts"
    },
    
    # === CRYPTO ===
    "crypto-dashboard": {
        "name": "Crypto Dashboard", 
        "url": "/modules/crypto-dashboard",
        "desc": "Cryptocurrency prices and portfolio"
    },
    
    # === DEVELOPER ===
    "developer-docs": {
        "name": "Developer Docs", 
        "url": "/developers",
        "desc": "API documentation and guides"
    },
    "functions-registry": {
        "name": "Functions Registry", 
        "url": "/modules/functions-registry",
        "desc": "Platform function catalog"
    },
    "protocol-kitchen": {
        "name": "Protocol Kitchen", 
        "url": "/modules/protocol-kitchen",
        "desc": "Protocol development tools"
    },
    
    # === INFO ===
    "about-us": {
        "name": "About Us", 
        "url": "/modules/about-us",
        "desc": "Platform information and team"
    }
}

# ═══════════════════════════════════════════════════════════════════
# 3. USER INTENTS — Full Routing (130+ keywords)
# ═══════════════════════════════════════════════════════════════════
USER_INTENTS = {
    # === AI & CHAT ===
    "chat": "curiosity-ocean", "ask": "curiosity-ocean", "talk": "curiosity-ocean",
    "ai": "curiosity-ocean", "ocean": "curiosity-ocean", "question": "curiosity-ocean",
    "specialized": "specialized-chat", "expert": "specialized-chat",
    "webui": "open-webui", "models": "open-webui",
    
    # === NEUROSCIENCE ===
    "eeg": "eeg-analysis", "brain": "eeg-analysis", "brainwave": "eeg-analysis",
    "neural": "neural-biofeedback", "biofeedback": "neural-biofeedback",
    "synthesis": "neural-synthesis", "pattern": "neural-synthesis",
    "neuroacoustic": "neuroacoustic-converter", "brainmusic": "neuroacoustic-converter",
    "biometric": "hybrid-biometric-dashboard", "hrv": "hybrid-biometric-dashboard",
    "face": "face-detection", "facial": "face-detection", "recognition": "face-detection",
    "mirror": "mymirror-now", "reflection": "mymirror-now",
    
    # === DOCUMENTS ===
    "excel": "document-tools", "word": "document-tools", "pdf": "document-tools",
    "document": "document-tools", "file": "document-tools",
    "spreadsheet": "excel-dashboard", "xlsx": "excel-dashboard",
    "collect": "data-collection", "gather": "data-collection",
    "mydata": "user-data", "personal": "user-data",
    
    # === FITNESS & HEALTH ===
    "fitness": "fitness-dashboard", "workout": "fitness-dashboard", "exercise": "fitness-dashboard",
    "habit": "daily-habits", "routine": "daily-habits", "track": "daily-habits",
    "mood": "mood-journal", "emotion": "mood-journal", "journal": "mood-journal",
    "focus": "focus-timer", "pomodoro": "focus-timer", "timer": "focus-timer",
    
    # === IoT ===
    "iot": "iot-network", "lora": "iot-network", "sensor": "iot-network", "lorawan": "iot-network",
    "industrial": "industrial-dashboard", "factory": "industrial-dashboard", "manufacturing": "industrial-dashboard",
    "phone": "phone-sensors", "mobile": "phone-sensors", "accelerometer": "phone-sensors",
    "monitor": "phone-monitor", "device": "phone-monitor",
    "spectrum": "spectrum-analyzer", "frequency": "spectrum-analyzer", "audio": "spectrum-analyzer",
    
    # === ANALYTICS ===
    "analytics": "ocean-analytics", "statistics": "ocean-analytics", "insight": "ocean-analytics",
    "report": "reporting-dashboard", "reports": "reporting-dashboard",
    
    # === WEATHER ===
    "weather": "weather-dashboard", "forecast": "weather-dashboard", "temperature": "weather-dashboard",
    "metar": "aviation-weather", "taf": "aviation-weather", "aviation": "aviation-weather", "pilot": "aviation-weather",
    
    # === CRYPTO ===
    "crypto": "crypto-dashboard", "bitcoin": "crypto-dashboard", "btc": "crypto-dashboard",
    "ethereum": "crypto-dashboard", "eth": "crypto-dashboard", "portfolio": "crypto-dashboard",
    
    # === DEVELOPER ===
    "developer": "developer-docs", "api": "developer-docs", "documentation": "developer-docs",
    "function": "functions-registry", "registry": "functions-registry",
    "protocol": "protocol-kitchen", "develop": "protocol-kitchen",
    
    # === INFO ===
    "about": "about-us", "team": "about-us", "contact": "about-us", "kloud": "about-us",
    
    # === MULTILINGUAL (Albanian) ===
    "dokument": "document-tools", "skedar": "document-tools",
    "moti": "weather-dashboard", "koha": "weather-dashboard",
    "truri": "eeg-analysis", "valët": "eeg-analysis",
    "ushtrime": "fitness-dashboard", "stërvitje": "fitness-dashboard",
    "analitikë": "ocean-analytics", "raport": "reporting-dashboard",
    "kripto": "crypto-dashboard", "monedha": "crypto-dashboard"
}

# ═══════════════════════════════════════════════════════════════════
# 4. HOW TO USE — Documentation for each module
# ═══════════════════════════════════════════════════════════════════
HOW_TO_USE = {
    "curiosity-ocean": "Open Curiosity Ocean → Type your question in any language → Get AI response",
    "specialized-chat": "Select domain → Start conversation → Get expert-level answers",
    "open-webui": "Choose model → Configure settings → Start chatting",
    
    "eeg-analysis": "Upload EEG file (CSV/EDF) → Select analysis type → View brain wave visualization",
    "neural-biofeedback": "Connect EEG device → Start session → Follow real-time feedback",
    "neural-synthesis": "Choose pattern type → Configure parameters → Generate neural patterns",
    "neuroacoustic-converter": "Upload EEG data → Select audio style → Download brain music",
    "hybrid-biometric-dashboard": "Connect sensors → View real-time data → Track trends",
    "face-detection": "Enable camera → Detect faces → Get recognition results",
    "mymirror-now": "Enable camera → Start reflection → Get AI insights",
    
    "document-tools": "Dashboard → Document Tools → Choose file type → Create or edit",
    "excel-dashboard": "Upload Excel → View charts → Analyze data → Export results",
    "data-collection": "Configure sources → Start collection → View aggregated data",
    "user-data": "View your data → Export or delete → Manage privacy settings",
    
    "fitness-dashboard": "Connect tracker → Log workouts → Track nutrition → View progress",
    "daily-habits": "Create habits → Check daily → View streaks → Analyze patterns",
    "mood-journal": "Log mood daily → Add notes → View trends → Get insights",
    "focus-timer": "Set timer → Start session → Take breaks → Track productivity",
    
    "iot-network": "Configure gateway → Add sensors → View data → Set alerts",
    "industrial-dashboard": "Connect systems → Monitor metrics → Analyze efficiency",
    "phone-sensors": "Enable sensors → Start recording → View real-time data",
    "phone-monitor": "Connect device → Monitor status → View analytics",
    "spectrum-analyzer": "Input audio → View spectrum → Analyze frequencies",
    
    "ocean-analytics": "Select timeframe → Choose metrics → View visualizations",
    "reporting-dashboard": "Choose report type → Configure parameters → Generate and export",
    
    "weather-dashboard": "Set location → View current conditions → Check forecast",
    "aviation-weather": "Enter airport code → View METAR/TAF → Check conditions",
    
    "crypto-dashboard": "Add cryptocurrencies → Track prices → Monitor portfolio",
    
    "developer-docs": "Browse API docs → Test endpoints → Get integration guides",
    "functions-registry": "Search functions → View specifications → Copy code",
    "protocol-kitchen": "Design protocol → Test implementation → Deploy",
    
    "about-us": "Learn about platform → Contact team → View mission"
}

# ═══════════════════════════════════════════════════════════════════
# 5. ROUTING FUNCTIONS — Enterprise Clean
# ═══════════════════════════════════════════════════════════════════
def route_intent(user_input: str) -> str:
    text = user_input.lower()
    for keyword, module in USER_INTENTS.items():
        if keyword in text:
            return module
    return "curiosity-ocean"

def get_service_info(service: str):
    return SERVICES.get(service)

def get_how_to_use(service: str):
    return HOW_TO_USE.get(service, "No documentation available.")

