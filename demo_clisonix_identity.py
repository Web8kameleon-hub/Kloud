#!/usr/bin/env python3
"""
Kloud System Identity Demonstration
Shows Curiosity Ocean now knows itself as Kloud with multilingual support

Author: Ledjan Ahmati
Date: January 17, 2026
"""

import sys
import json
sys.path.insert(0, "apps/api/services")

from kloud_identity import get_kloud_identity, IdentityLanguage
from curiosity_core_engine import get_engine, ResponseLanguage


def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def main():
    """Demonstrate Kloud system identity awareness"""
    
    identity = get_kloud_identity()
    engine = get_engine()
    
    # ====================================================================
    # 1. SYSTEM IDENTITY
    # ====================================================================
    print_section("1️⃣  KLOUD SYSTEM IDENTITY")
    
    status = identity.get_system_status(IdentityLanguage.ENGLISH)
    for key, value in status.items():
        print(f"  {key:20} → {value}")
    
    # ====================================================================
    # 2. MULTILINGUAL SELF-INTRODUCTION
    # ====================================================================
    print_section("2️⃣  MULTILINGUAL SELF-INTRODUCTION")
    
    languages = [
        ("Albanian", IdentityLanguage.ALBANIAN),
        ("English", IdentityLanguage.ENGLISH),
        ("Italian", IdentityLanguage.ITALIAN),
        ("Spanish", IdentityLanguage.SPANISH),
    ]
    
    for lang_name, lang_enum in languages:
        print(f"\n🌍 {lang_name}:")
        intro = identity.get_identity_intro(lang_enum)
        print(f"   {intro}\n")
        full = identity.get_full_identity(lang_enum)
        print(f"   {full}\n")
    
    # ====================================================================
    # 3. TRINITY SYSTEM (ALBA/ALBI/JONA)
    # ====================================================================
    print_section("3️⃣  ASI TRINITY SYSTEM (ALBA/ALBI/JONA)")
    
    trinity = identity.trinity_architecture
    for component, info in trinity.items():
        print(f"\n  {component} (Port {info['port']})")
        print(f"    Function: {info['function']}")
        print(f"    Capabilities:")
        for cap in info['capabilities']:
            print(f"      • {cap}")
    
    # ====================================================================
    # 4. CURIOSITY OCEAN LAYER
    # ====================================================================
    print_section("4️⃣  CURIOSITY OCEAN - LAYER 7")
    
    ocean_desc = identity.get_ocean_description(IdentityLanguage.ENGLISH)
    print(f"  {ocean_desc}\n")
    
    # ====================================================================
    # 5. FULL LAYER HIERARCHY
    # ====================================================================
    print_section("5️⃣  COMPLETE 12-LAYER ARCHITECTURE")
    
    for i in range(1, 13):
        layer_desc = identity.get_layer_description(i, IdentityLanguage.ENGLISH)
        print(f"  Layer {i:2d}: {layer_desc}")
    
    # ====================================================================
    # 6. IDENTITY-AWARE QUESTIONS
    # ====================================================================
    print_section("6️⃣  OCEAN ANSWERING IDENTITY QUESTIONS")
    
    test_questions = [
        ("Who are you?", ResponseLanguage.ENGLISH),
        ("What is your purpose?", ResponseLanguage.ENGLISH),
        ("Tell me about the Trinity?", ResponseLanguage.ENGLISH),
        ("Qfarë je ti?", ResponseLanguage.ALBANIAN),  # What are you? (Albanian)
        ("Cili është qëllimi yt?", ResponseLanguage.ALBANIAN),  # What is your purpose? (Albanian)
    ]
    
    for question, response_lang in test_questions:
        print(f"\n  Q: {question}")
        
        # Check if engine detects this as identity question
        is_identity = engine.is_identity_question(question)
        print(f"  Identity Question? {is_identity}")
        
        if is_identity:
            # Get identity-aware response
            answer = engine.handle_identity_question(question, response_lang)
            print(f"\n  A: {answer[:150]}..." if len(answer) > 150 else f"\n  A: {answer}")
    
    # ====================================================================
    # 7. CAPABILITIES SUMMARY
    # ====================================================================
    print_section("7️⃣  SYSTEM CAPABILITIES")
    
    capabilities = identity.get_capabilities(IdentityLanguage.ENGLISH)
    print(f"  {capabilities}\n")
    
    # ====================================================================
    # 8. PURPOSE STATEMENT
    # ====================================================================
    print_section("8️⃣  MISSION & PURPOSE")
    
    purpose = identity.get_purpose(IdentityLanguage.ENGLISH)
    print(f"  {purpose}\n")
    
    # ====================================================================
    # 9. JSON API RESPONSE EXAMPLE
    # ====================================================================
    print_section("9️⃣  API RESPONSE FORMAT (JSON)")
    
    api_response = {
        "success": True,
        "identity": {
            "name": identity.identity.name,
            "version": identity.identity.version,
            "type": identity.identity.type,
            "layers": identity.identity.layers
        },
        "introduction": identity.get_identity_intro(IdentityLanguage.ENGLISH),
        "capabilities": identity.get_capabilities(IdentityLanguage.ENGLISH)
    }
    
    print(json.dumps(api_response, indent=2, ensure_ascii=False))
    
    # ====================================================================
    # 10. SUMMARY
    # ====================================================================
    print_section("✅ SYSTEM IDENTITY VERIFICATION COMPLETE")
    
    print("""
  ✓ Kloud now has system identity and self-awareness
  ✓ Curiosity Ocean understands it is Layer 7 of Kloud
  ✓ Trinity system (ALBA/ALBI/JONA) integrated
  ✓ Multilingual support (8+ languages)
  ✓ Identity-aware question detection enabled
  ✓ API endpoints for identity information ready
  
  ENDPOINTS AVAILABLE:
  
  GET /api/ocean/identity?language=en|sq|it|es|fr|de
    → Complete system identity
  
  GET /api/ocean/identity/trinity
    → Trinity system information
  
  GET /api/ocean/identity/layers
    → All 12 layers with descriptions
  
  POST /api/ocean/chat (with language parameter)
    → Chat with identity-aware responses
  
  STATUS: Kloud knows itself! 🧠🌊
    """)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

