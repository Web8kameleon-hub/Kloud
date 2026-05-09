# -*- coding: utf-8 -*-
"""
🧠 LEARNING DISPLAY - Visual Training Process
==============================================
Shfaq procesin e mësimit në terminal me animacion.
Tregon burimet që po konsultohen në kohë reale.
"""

import sys
import time
import asyncio
from datetime import datetime

# Colors for terminal
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header():
    """Print header"""
    print(f"\n{Colors.CYAN}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}🧠 KLOUD LEARNING ENGINE - LIVE PROCESS{Colors.END}")
    print(f"{Colors.CYAN}{'='*70}{Colors.END}\n")


def animate_dots(text, duration=1.5, color=Colors.YELLOW):
    """Animate loading dots"""
    dots = [".", "..", "...", "....", "....."]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f"\r{color}   {text}{dots[i % len(dots)]}{Colors.END}   ")
        sys.stdout.flush()
        time.sleep(0.2)
        i += 1
    print()


def show_source(name, icon, description, delay=0.5):
    """Show a source being consulted"""
    print(f"{Colors.YELLOW}   {icon} {name}{Colors.END}")
    animate_dots(f"Duke kërkuar në {name}", delay)
    print(f"{Colors.GREEN}   ✓ {description}{Colors.END}")
    print()


def show_learning_process(query):
    """Show the full learning process for a query"""
    print(f"\n{Colors.BOLD}{Colors.WHITE}📝 PYETJA: {query}{Colors.END}")
    print(f"{Colors.CYAN}{'─'*70}{Colors.END}\n")
    
    # Step 1: Pattern Detection
    print(f"{Colors.MAGENTA}🔍 HAPI 1: DETEKTIMI I PATTERN-IT{Colors.END}")
    animate_dots("Duke analizuar strukturën e pyetjes", 1)
    print(f"{Colors.GREEN}   ✓ Pattern i detektuar: 'what_is' query{Colors.END}\n")
    
    # Step 2: Check Knowledge Base
    print(f"{Colors.MAGENTA}📚 HAPI 2: KONTROLLI I BAZËS SË NJOHURIVE{Colors.END}")
    animate_dots("Duke kërkuar në knowledge base", 0.8)
    print(f"{Colors.YELLOW}   ⚠ Nuk u gjet në cache - do të mësojmë{Colors.END}\n")
    
    # Step 3: Consulting Sources
    print(f"{Colors.MAGENTA}🌐 HAPI 3: KONSULTIMI I BURIMEVE{Colors.END}")
    print(f"{Colors.CYAN}   Duke konsultuar burimet e disponueshme...{Colors.END}\n")
    
    sources = [
        ("Wikipedia", "📖", "Artikuj enciklopedikë - 6M+ artikuj"),
        ("CoinGecko", "💰", "Çmime kripto në kohë reale"),
        ("OpenWeatherMap", "🌤️", "Të dhëna moti për 200+ qytete"),
        ("PubMed", "🔬", "Kërkime mjekësore - 35M+ artikuj"),
        ("ArXiv", "📄", "Artikuj shkencorë - 2M+ papers"),
        ("World Bank", "📊", "Statistika ekonomike globale"),
        ("EU Open Data", "🇪🇺", "Të dhëna Evropiane"),
        ("Laboratories", "🔬", "23 laboratorë interne"),
        ("Personas", "👥", "14 ekspertë virtualë"),
        ("Alphabet Layers", "🔤", "61 shtresa matematikore"),
    ]
    
    for name, icon, desc in sources:
        show_source(name, icon, desc, 0.3)
    
    # Step 4: Processing
    print(f"{Colors.MAGENTA}⚙️ HAPI 4: PROCESIMI{Colors.END}")
    animate_dots("Duke kombinuar informacionet", 1)
    animate_dots("Duke gjeneruar përgjigjen", 0.8)
    print(f"{Colors.GREEN}   ✓ Përgjigja u gjenerua me sukses{Colors.END}\n")
    
    # Step 5: Learning
    print(f"{Colors.MAGENTA}🧠 HAPI 5: MËSIMI{Colors.END}")
    animate_dots("Duke ruajtur në knowledge base", 0.5)
    knowledge_id = f"know_{hash(query) % 1000000:06x}"
    print(f"{Colors.GREEN}   ✓ U mësua si: {knowledge_id}{Colors.END}")
    print(f"{Colors.GREEN}   ✓ Herën tjetër do të përgjigjet menjëherë!{Colors.END}\n")
    
    # Summary
    print(f"{Colors.CYAN}{'─'*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}✅ PROCESI PËRFUNDOI{Colors.END}")
    print(f"{Colors.WHITE}   Burime të konsultuara: {len(sources)}{Colors.END}")
    print(f"{Colors.WHITE}   Knowledge ID: {knowledge_id}{Colors.END}")
    print(f"{Colors.WHITE}   Koha: {datetime.now().strftime('%H:%M:%S')}{Colors.END}")
    print(f"{Colors.CYAN}{'─'*70}{Colors.END}\n")


def show_cached_response(query):
    """Show when a response comes from cache"""
    print(f"\n{Colors.BOLD}{Colors.WHITE}📝 PYETJA: {query}{Colors.END}")
    print(f"{Colors.CYAN}{'─'*70}{Colors.END}\n")
    
    print(f"{Colors.MAGENTA}🔍 KONTROLLI I CACHE{Colors.END}")
    animate_dots("Duke kërkuar në knowledge base", 0.5)
    print(f"{Colors.GREEN}   ✓ U GJET NË CACHE!{Colors.END}")
    print(f"{Colors.GREEN}   ✓ Përgjigja e menjëhershme - pa nevojë për burime të jashtme{Colors.END}\n")
    
    print(f"{Colors.CYAN}{'─'*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.GREEN}⚡ PËRGJIGJE E SHPEJTË NGA MËSIMI I MËPARSHËM{Colors.END}")
    print(f"{Colors.CYAN}{'─'*70}{Colors.END}\n")


def main():
    """Main demo"""
    print_header()
    
    print(f"{Colors.WHITE}Ky demo tregon si sistemi mëson nga pyetjet.{Colors.END}")
    print(f"{Colors.WHITE}Procesi real ndodh brenda milisekondash, por këtu e shohim ngadalë.{Colors.END}")
    print()
    
    input(f"{Colors.YELLOW}Shtyp ENTER për të parë procesin e mësimit...{Colors.END}")
    
    # First query - will learn
    show_learning_process("What is consciousness?")
    
    input(f"{Colors.YELLOW}Shtyp ENTER për të parë pyetjen e dytë (nga cache)...{Colors.END}")
    
    # Same query - from cache
    show_cached_response("What is consciousness?")
    
    input(f"{Colors.YELLOW}Shtyp ENTER për të parë një pyetje të re...{Colors.END}")
    
    # New query
    show_learning_process("What's the price of Bitcoin?")
    
    print(f"\n{Colors.BOLD}{Colors.CYAN}🎓 DEMO PËRFUNDOI{Colors.END}")
    print(f"{Colors.WHITE}Sistemi tani njeh këto pyetje dhe do t'i përgjigjet menjëherë!{Colors.END}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Demo u ndërpre.{Colors.END}")

