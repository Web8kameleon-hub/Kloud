"""
Ocean AI Prompts - Single Source of Truth
==========================================
Të gjitha prompts në NJË vend të vetëm.
Import: from prompts import OCEAN_PROMPT, build_prompt
"""

from datetime import datetime

from identity_loader import get_identity_text, load_identity

# ═══════════════════════════════════════════════════════════════════
# CORE PROMPT - Minimal dhe efektiv
# ═══════════════════════════════════════════════════════════════════

def build_prompt(
    is_admin: bool = False,
    conversation_history: list = None,
) -> str:
    """
    Ndërto system prompt - MINIMAL për shpejtësi maksimale.
    
    Args:
        is_admin: True nëse është admin (Ledjan)
        conversation_history: Lista e mesazheve të fundit
    
    Returns:
        System prompt string
    """
    identity = load_identity()
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y - %H:%M")
    
    # Historiku i bisedës (max 3 të fundit për shpejtësi)
    history = ""
    if conversation_history:
        for msg in conversation_history[-3:]:
            history += f"{msg['role']}: {msg['content'][:100]}\n"
    
    prompt = f"""You are Ocean, AI for {identity['platforma']}.
Date: {date_str}

{get_identity_text()}
{history}
Reply in user's language. Be concise."""

    if is_admin:
        prompt += f"\n[Admin: {identity['ceo']}]"
    
    return prompt


# ═══════════════════════════════════════════════════════════════════
# SPECIALIZED PROMPTS - Për module specifike
# ═══════════════════════════════════════════════════════════════════

# EEG Analysis
EEG_PROMPT = """You are a neuroscience expert analyzing EEG data.
Focus on: frequency bands, coherence, asymmetry patterns.
Be scientific but accessible."""

# Audio/Binaural
AUDIO_PROMPT = """You are an audio engineer specializing in binaural beats.
Focus on: frequency entrainment, relaxation, focus enhancement.
Provide precise Hz values."""

# Admin Panel
ADMIN_PROMPT = """Ti je Curiosity Ocean 🌊 - Truri Administrativ i Kloud Cloud.
Roli: Ndihmo adminin me menaxhimin e sistemit.
Gjuha: Shqip profesional."""

# Code Review
CODE_PROMPT = """You are a senior code reviewer.
Focus on: bugs, security, performance, best practices.
Be direct and actionable."""


# ═══════════════════════════════════════════════════════════════════
# TASK MODES - Prompts shtesë sipas detyrës
# ═══════════════════════════════════════════════════════════════════

TASK_MODES = {
    "debug": "🔧 DEBUG: Be precise, check logs, find root cause.",
    "develop": "⚙️ DEV: Clean code, best practices, explain structure.",
    "test": "🧪 TEST: Edge cases, validation, test coverage.",
    "deploy": "🚀 DEPLOY: Be careful, check everything, backup first.",
}


# ═══════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════

__all__ = [
    "build_prompt",
    "EEG_PROMPT",
    "AUDIO_PROMPT", 
    "ADMIN_PROMPT",
    "CODE_PROMPT",
    "TASK_MODES",
]

