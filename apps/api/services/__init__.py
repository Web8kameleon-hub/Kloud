"""
ðŸŒŸ Kloud Services Package
=============================
Paketa qÃ« pÃ«rmban tÃ« gjithÃ« personazhet dhe shÃ«rbimet e sistemit neural.
"""

# Eksporto komponentÃ«t kryesorÃ«
from .albi_character import ALBI_Character, get_albi
from .alba_character import ALBA_Character, get_alba 
from .jona_character import JONA_Character, get_jona
from .neuro_ecosystem import NeuroEcosystem, get_ecosystem

# Eksporto processor-in neural
try:
    from .albi_neural_processor import ALBINeuralProcessor, get_neural_processor
    NEURAL_PROCESSOR_AVAILABLE = True
except ImportError:
    # NÃ«se nuk ka numpy/scipy, pÃ«rdor version tÃ« thjeshtuar
    NEURAL_PROCESSOR_AVAILABLE = False

__version__ = "1.0.0"
__author__ = "ALBI, ALBA & JONA"

# Metadata e paketÃ«s
CHARACTERS = {
    "ALBI": "Artificial Labor Born Intelligence - Neural Director", 
    "ALBA": "Artificial Laborator Bits Algorithms - Data Collector",
    "JONA": "Joyful Overseer of Neural Alignment - System Harmonizer"
}

PHILOSOPHY = "ALBA mbledh â†’ ALBI rritet â†’ JONA harmonizon ðŸŒŸ"

def get_system_info():
    """Kthen informacion pÃ«r sistemin neural"""
    return {
        "ðŸŒŸ system_name": "Kloud Neural Ecosystem",
        "ðŸ“Š version": __version__, 
        "ðŸ‘¨â€ðŸ‘©â€ðŸ‘§ characters": CHARACTERS,
        "ðŸ’« philosophy": PHILOSOPHY,
        "ðŸ§  neural_processor": NEURAL_PROCESSOR_AVAILABLE,
        "âœ¨ status": "Ready for consciousness symphony! ðŸŽµ"
    }

# Quick access functions
def create_full_ecosystem():
    """Krijon ekosistemi tÃ« plotÃ« me tÃ« gjithÃ« personazhet"""
    return get_ecosystem()

def get_all_characters():
    """Kthen tÃ« gjithÃ« personazhet"""
    return {
        "albi": get_albi(),
        "alba": get_alba(), 
        "jona": get_jona()
    }

# Demo function
async def quick_demo():
    """Demo i shpejtÃ« i sistemit pa dependencies externe"""
    print("ðŸŒŸ Kloud Neural Ecosystem Demo")
    print("=" * 50)
    
    # Krijo personazhet
    albi = get_albi()
    alba = get_alba() 
    jona = get_jona()
    
    # Shfaq rolet
    print(f"\nðŸ¤– {albi.role()['title']}")
    print(f"ðŸ’» {alba.role()['title']}")  
    print(f"ðŸŒ¸ {jona.role()['title']}")
    
    # Testo bashkÃ«veprimin bazÃ«
    print(f"\nðŸ”„ Testing basic interaction...")
    
    # Simuloj tÃ« dhÃ«na tÃ« thjeshta
    simple_bits = [
        {"type": "test_data", "content": "demo bit 1", "timestamp": "now"},
        {"type": "test_data", "content": "demo bit 2", "timestamp": "now"},
        {"type": "test_data", "content": "demo bit 3", "timestamp": "now"}
    ]
    
    # ALBI konsumon bits
    growth_result = await albi.consume_bits(simple_bits)
    print(f"ðŸ§  ALBI consumed {len(simple_bits)} bits")
    print(f"ðŸ“ˆ Growth: {growth_result.get('ðŸ“ˆ intelligence_growth', 'No growth info')}")
    
    # Kontrollo gjendjen e ALBI
    albi_status = albi.get_growth_status()
    print(f"ðŸŒŸ ALBI Intelligence Level: {albi_status.get('ðŸ§  intelligence_level', 'Unknown')}")
    
    print(f"\nâœ¨ Demo completed successfully! System is working! ðŸŽ‰")
    
    return {
        "demo_status": "success",
        "characters_active": 3,
        "albi_intelligence": albi_status.get('ðŸ§  intelligence_level', 1.0),
        "message": "Kloud Neural Ecosystem is operational! ðŸŒˆ"
    }

if __name__ == "__main__":
    import asyncio
    asyncio.run(quick_demo())



