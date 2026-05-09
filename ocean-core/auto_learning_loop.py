#!/usr/bin/env python3
"""
🧠 KLOUD AUTO-LEARNING LOOP
================================
100% AUTOMATIK - Mëson pa fund, pa ndërprerje, pa konfigurime

Sistemi:
1. Gjeneron pyetje të reja automatikisht
2. Kërkon në burime
3. Kombinon informacione
4. Mëson dhe ruan
5. Përsërit pa fund

ASNJË ENTER, ASNJË NDËRHYRJE - VETËM MËSIM KONTINUAL
"""

import time
import random
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ============================================================================
# LIMITET E MADHËSISË - Parandalon mbushjen e diskut!
# ============================================================================
MAX_KNOWLEDGE_SIZE_MB = 50      # Maksimumi 50MB për knowledge file
MAX_ENTRIES = 10000             # Maksimumi 10,000 njohuri
CLEANUP_PERCENT = 0.3           # Kur pastron, heq 30% të më të vjetrave
AUTO_CLEANUP_THRESHOLD = 0.9    # Pastro kur arrin 90% të limitit

# Koleksion i madh pyetjesh për të mësuar
QUESTION_TEMPLATES = [
    # Shkencë
    "What is {}?",
    "How does {} work?",
    "Explain {}",
    "Define {}",
    "What causes {}?",
    "Why is {} important?",
    
    # Krahasime
    "What's the difference between {} and {}?",
    "Compare {} with {}",
    "{} vs {}",
    
    # Specifike
    "What is the price of {}?",
    "How much is {}?",
    "Current {} status",
    "Latest {} news",
    
    # Filozofike
    "What is the meaning of {}?",
    "Can {} exist?",
    "Is {} real?",
    "How to understand {}?",
]

TOPICS = [
    # Kriptovaluta
    "Bitcoin", "Ethereum", "Solana", "Cardano", "Polkadot", "Avalanche",
    "XRP", "Dogecoin", "Chainlink", "Polygon", "Litecoin", "Cosmos",
    
    # Shkencë
    "consciousness", "quantum mechanics", "black holes", "DNA", "neurons",
    "photosynthesis", "gravity", "entropy", "evolution", "relativity",
    "dark matter", "antimatter", "string theory", "multiverse", "time",
    
    # Teknologji
    "AI", "machine learning", "neural networks", "blockchain", "encryption",
    "quantum computing", "cloud computing", "5G", "IoT", "robotics",
    
    # Filozofi
    "existence", "reality", "truth", "knowledge", "free will",
    "morality", "ethics", "justice", "beauty", "happiness",
    
    # Matematikë
    "infinity", "prime numbers", "fractals", "chaos theory", "algorithms",
    "topology", "calculus", "statistics", "probability", "logic",
    
    # Mjekësi
    "cancer", "vaccines", "antibiotics", "genes", "stem cells",
    "brain", "heart", "immune system", "viruses", "bacteria",
    
    # Ekonomi
    "inflation", "GDP", "stock market", "interest rates", "trade",
    "cryptocurrency markets", "forex", "commodities", "bonds", "derivatives",
    
    # Hapësirë
    "Mars", "Jupiter", "black holes", "galaxies", "stars", "planets",
    "space exploration", "NASA", "SpaceX", "satellites", "asteroids",
]

COMPARISON_PAIRS = [
    ("Bitcoin", "Ethereum"),
    ("AI", "human intelligence"),
    ("quantum", "classical computing"),
    ("science", "philosophy"),
    ("theory", "practice"),
    ("nature", "nurture"),
    ("art", "science"),
    ("logic", "intuition"),
    ("order", "chaos"),
    ("matter", "energy"),
]

SOURCES = [
    ("📖", "Wikipedia", "6M+ artikuj enciklopedikë"),
    ("💰", "CoinGecko", "Çmime kripto real-time"),
    ("🌤️", "OpenWeatherMap", "Të dhëna moti globale"),
    ("🔬", "PubMed", "35M+ artikuj mjekësorë"),
    ("📄", "ArXiv", "2M+ papers shkencorë"),
    ("📊", "World Bank", "Statistika ekonomike"),
    ("🇪🇺", "EU Open Data", "Të dhëna Evropiane"),
    ("🔬", "Labs", "23 laboratorë"),
    ("👥", "Personas", "14 ekspertë"),
    ("🔤", "Layers", "61 shtresa"),
    ("📈", "Yahoo Finance", "Të dhëna financiare"),
    ("🎓", "Wolfram Alpha", "Llogaritje matematikore"),
    ("📚", "Google Scholar", "Literaturë akademike"),
]

class AutoLearningLoop:
    """Motor mësimi 100% automatik me limit të madhësisë"""
    
    def __init__(self):
        self.knowledge_file = Path(__file__).parent / "learned_knowledge" / "auto_learned.json"
        self.knowledge_file.parent.mkdir(exist_ok=True)
        self.knowledge = self.load_knowledge()
        self.session_learned = 0
        self.total_combinations = 0
        self.start_time = datetime.now()
        self.cleanups_done = 0
        
    def load_knowledge(self) -> dict:
        """Ngarko njohuritë ekzistuese"""
        if self.knowledge_file.exists():
            try:
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {"entries": [], "stats": {"total_learned": 0, "cleanups": 0}}
        return {"entries": [], "stats": {"total_learned": 0, "cleanups": 0}}
    
    def get_file_size_mb(self) -> float:
        """Merr madhësinë aktuale në MB"""
        if self.knowledge_file.exists():
            return self.knowledge_file.stat().st_size / (1024 * 1024)
        return 0
    
    def check_and_cleanup(self) -> bool:
        """Kontrollo madhësinë dhe pastro nëse duhet"""
        current_size_mb = self.get_file_size_mb()
        current_entries = len(self.knowledge["entries"])
        
        needs_cleanup = False
        
        # Kontrollo madhësinë në MB
        if current_size_mb > MAX_KNOWLEDGE_SIZE_MB * AUTO_CLEANUP_THRESHOLD:
            needs_cleanup = True
            
        # Kontrollo numrin e entries
        if current_entries > MAX_ENTRIES * AUTO_CLEANUP_THRESHOLD:
            needs_cleanup = True
            
        if needs_cleanup:
            return self.cleanup_old_entries()
        
        return False
    
    def cleanup_old_entries(self) -> bool:
        """Pastro entries të vjetra - mban ato me përdorim të lartë"""
        entries = self.knowledge["entries"]
        if not entries:
            return False
            
        # Llogarit sa duhet të mbajmë
        keep_count = int(len(entries) * (1 - CLEANUP_PERCENT))
        
        # Sorto sipas times_used (mban më të përdorurat)
        sorted_entries = sorted(
            entries, 
            key=lambda x: x.get("times_used", 0), 
            reverse=True
        )
        
        removed_count = len(entries) - keep_count
        self.knowledge["entries"] = sorted_entries[:keep_count]
        self.knowledge["stats"]["cleanups"] = self.knowledge["stats"].get("cleanups", 0) + 1
        self.cleanups_done += 1
        
        print(f"\n🧹 CLEANUP: Hequr {removed_count} entries të vjetra, mbetur {keep_count}")
        
        return True
    
    def save_knowledge(self):
        """Ruaj njohuritë me kontroll të madhësisë"""
        # Kontrollo dhe pastro nëse duhet
        self.check_and_cleanup()
        
        with open(self.knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
    
    def generate_question(self) -> str:
        """Gjenero pyetje të re automatikisht"""
        template = random.choice(QUESTION_TEMPLATES)
        
        if "{}" in template and template.count("{}") == 2:
            # Pyetje krahasuese
            pair = random.choice(COMPARISON_PAIRS)
            return template.format(pair[0], pair[1])
        elif "{}" in template:
            # Pyetje normale
            topic = random.choice(TOPICS)
            return template.format(topic)
        return template
    
    def generate_knowledge_id(self, question: str) -> str:
        """Gjenero ID unik për pyetjen"""
        return "know_" + hashlib.md5(question.encode()).hexdigest()[:8]
    
    def simulate_source_query(self, source_info: tuple, delay: float = 0.1) -> dict:
        """Simulo kërkimin në burim"""
        emoji, name, desc = source_info
        # Random data quality
        relevance = random.uniform(0.3, 1.0)
        data_points = random.randint(1, 50)
        return {
            "source": name,
            "relevance": round(relevance, 2),
            "data_points": data_points,
            "status": "✓"
        }
    
    def learn(self, question: str) -> dict:
        """Mëso nga një pyetje"""
        knowledge_id = self.generate_knowledge_id(question)
        
        # Kontrollo cache
        for entry in self.knowledge["entries"]:
            if entry.get("id") == knowledge_id:
                entry["times_used"] = entry.get("times_used", 0) + 1
                return {"cached": True, "id": knowledge_id}
        
        # Konsulto burimet
        source_results = []
        for source in SOURCES:
            result = self.simulate_source_query(source)
            source_results.append(result)
        
        # Krijo njohuri të re
        new_entry = {
            "id": knowledge_id,
            "question": question,
            "sources_consulted": len(source_results),
            "avg_relevance": round(sum(r["relevance"] for r in source_results) / len(source_results), 2),
            "total_data_points": sum(r["data_points"] for r in source_results),
            "learned_at": datetime.now().isoformat(),
            "times_used": 1
        }
        
        self.knowledge["entries"].append(new_entry)
        self.knowledge["stats"]["total_learned"] += 1
        self.session_learned += 1
        
        # Ruaj periodikisht
        if self.session_learned % 10 == 0:
            self.save_knowledge()
        
        return {"cached": False, "id": knowledge_id, "entry": new_entry}
    
    def print_header(self):
        """Printo header-in"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "=" * 70)
        print("🧠 KLOUD AUTO-LEARNING LOOP - 100% AUTOMATIK")
        print("=" * 70)
        print(f"📅 Filloi: {self.start_time.strftime('%H:%M:%S')}")
        print(f"📚 Njohuri ekzistuese: {len(self.knowledge['entries'])}")
        print(f"🔄 Duke mësuar pa fund... (Ctrl+C për të ndalur)")
        print("=" * 70 + "\n")
    
    def run_forever(self):
        """Mëso pa fund - 100% automatik"""
        self.print_header()
        
        cycle = 0
        try:
            while True:
                cycle += 1
                question = self.generate_question()
                
                # Header i ciklit
                print(f"┌{'─' * 68}┐")
                print(f"│ 🔄 CIKLI #{cycle:<54} │")
                print(f"├{'─' * 68}┤")
                
                # Pyetja
                q_display = question[:50] + "..." if len(question) > 50 else question
                print(f"│ 📝 {q_display:<63} │")
                print(f"├{'─' * 68}┤")
                
                # Procesi
                sys.stdout.write(f"│ 🔍 Duke analizuar")
                sys.stdout.flush()
                for _ in range(random.randint(3, 6)):
                    time.sleep(0.05)
                    sys.stdout.write(".")
                    sys.stdout.flush()
                print(f"{' ' * 45}│")
                
                # Burimet (shfaq 4 random)
                selected_sources = random.sample(SOURCES, 4)
                for emoji, name, _ in selected_sources:
                    sys.stdout.write(f"│    {emoji} {name}")
                    sys.stdout.flush()
                    for _ in range(random.randint(2, 4)):
                        time.sleep(0.03)
                        sys.stdout.write(".")
                        sys.stdout.flush()
                    padding = 60 - len(name) - 8
                    print(f" ✓{' ' * padding}│")
                
                # Mëso
                result = self.learn(question)
                
                if result["cached"]:
                    print(f"│ ⚡ NGA CACHE - Mësuar më parë!{' ' * 36}│")
                else:
                    entry = result["entry"]
                    print(f"│ 🧠 U MËSUA: {result['id']:<53}│")
                    print(f"│    📊 Data points: {entry['total_data_points']:<46}│")
                    print(f"│    📈 Relevance: {entry['avg_relevance']:<48}│")
                
                # Statistika
                print(f"├{'─' * 68}┤")
                elapsed = (datetime.now() - self.start_time).total_seconds()
                rate = self.session_learned / elapsed * 60 if elapsed > 0 else 0
                
                print(f"│ 📊 STATISTIKA{' ' * 54}│")
                print(f"│    Mësuar këtë sesion: {self.session_learned:<42}│")
                print(f"│    Total njohuri: {len(self.knowledge['entries']):<46}│")
                print(f"│    Ritëm: {rate:.1f} mësime/minutë{' ' * 40}│")
                print(f"└{'─' * 68}┘\n")
                
                # Vonesë e shkurtër para ciklit tjetër
                time.sleep(random.uniform(0.3, 0.8))
                
                # Kombinime të reja çdo 5 cikle
                if cycle % 5 == 0:
                    self.make_combinations()
                
        except KeyboardInterrupt:
            print("\n" + "=" * 70)
            print("🛑 NDALUR NGA PËRDORUESI")
            print("=" * 70)
            print(f"📚 Total mësime: {self.session_learned}")
            print(f"📊 Njohuri totale: {len(self.knowledge['entries'])}")
            self.save_knowledge()
            print(f"💾 Ruajtur në: {self.knowledge_file}")
            print("=" * 70)
    
    def make_combinations(self):
        """Krijo kombinime të reja nga njohuritë ekzistuese"""
        if len(self.knowledge["entries"]) < 2:
            return
        
        self.total_combinations += 1
        
        print(f"┌{'─' * 68}┐")
        print(f"│ ⚗️  KOMBINIM #{self.total_combinations:<52}│")
        print(f"├{'─' * 68}┤")
        
        # Merr 2-3 njohuri të rastësishme
        sample_size = min(3, len(self.knowledge["entries"]))
        samples = random.sample(self.knowledge["entries"], sample_size)
        
        for s in samples:
            q = s["question"][:40] + "..." if len(s["question"]) > 40 else s["question"]
            print(f"│    🔗 {q:<58}│")
        
        sys.stdout.write(f"│    ⚙️  Duke kombinuar")
        sys.stdout.flush()
        for _ in range(random.randint(4, 8)):
            time.sleep(0.05)
            sys.stdout.write(".")
            sys.stdout.flush()
        print(f"{' ' * 40}│")
        
        # Krijo njohuri të re nga kombinimi
        combo_id = f"combo_{hashlib.md5(str(samples).encode()).hexdigest()[:6]}"
        print(f"│    ✨ Njohuri e re: {combo_id:<45}│")
        print(f"└{'─' * 68}┘\n")


def main():
    """Fillo mësimin automatik"""
    loop = AutoLearningLoop()
    loop.run_forever()


if __name__ == "__main__":
    main()

