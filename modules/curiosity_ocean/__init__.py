"""
Curiosity Ocean Module
======================
Core conversational intelligence for Kloud Platform.
Version 6.1.0 - Enterprise AI Governance (4 Critical Layers)

ARCHITECTURE:
├── IRON RULES         → Rregulla të Hekurta (Non-Negotiables)
├── QUANTUM LAYER      → Stabilitet + Determinizëm
├── DDOS LAYER         → Mbrojtje nga abuzimi
└── GOVERNANCE LAYER   → Rregulla, kufij, politika

PURPOSE:
"Të ndihmojë përdoruesit me informacion të saktë, të sigurt dhe të qartë,
brenda kufijve të përcaktuar."
"""

from .master_prompt import (
    # Main prompts
    CURIOSITY_OCEAN_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
    MASTER_PROMPT,
    COMPACT_PROMPT,
    MICRO_PROMPT,
    # New v6.1 layers (4 Critical Layers)
    IRON_RULES,
    QUANTUM_LAYER,
    DDOS_LAYER,
    GOVERNANCE_LAYER,
    KLOUD_INFO,
    MULTILINGUAL_EXAMPLES,
    # Backward compatibility (old layer names)
    DESIRE_LAYER,
    REALISM_LAYER,
    EMOTION_LAYER,
    FEELING_LAYER,
    STABILITY_LAYER,
    FOCUS_LAYER,
    SAFETY_LAYER,
    TECHNICAL_BOUNDARIES_LAYER,
    ADAPTIVE_LAYER,
    CONTEXT_CLEANER_LAYER,
    IDENTITY_LAYER,
    # Functions
    get_prompt,
    get_layer,
)

__all__ = [
    # Main prompts
    "CURIOSITY_OCEAN_SYSTEM_PROMPT",
    "SYSTEM_PROMPT",
    "MASTER_PROMPT",
    "COMPACT_PROMPT",
    "MICRO_PROMPT",
    # New v6.1 layers
    "IRON_RULES",
    "QUANTUM_LAYER",
    "DDOS_LAYER",
    "GOVERNANCE_LAYER",
    "KLOUD_INFO",
    "MULTILINGUAL_EXAMPLES",
    # Backward compatibility
    "DESIRE_LAYER",
    "REALISM_LAYER", 
    "EMOTION_LAYER",
    "FEELING_LAYER",
    "STABILITY_LAYER",
    "FOCUS_LAYER",
    "SAFETY_LAYER",
    "TECHNICAL_BOUNDARIES_LAYER",
    "ADAPTIVE_LAYER",
    "CONTEXT_CLEANER_LAYER",
    "IDENTITY_LAYER",
    # Functions
    "get_prompt",
    "get_layer",
]

