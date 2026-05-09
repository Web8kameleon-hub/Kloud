"""
KLOUD PERSONAS INTERFACE v1.0
================================
Personas për UX / simulation - NUK prekin core learning!

Rregullat:
- MAX 3 aktive në një kohë
- Vetëm read + influence numeric (weights)
- Asnjë persona nuk shkruan direkt në auto_learning_core
- Jo chat, jo history, jo JSON

Author: Ledjan Ahmati / WEB8euroweb GmbH
Status: FROZEN after testing
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class Persona:
    """
    Persona = profil i qëndrueshem për UX.
    NUK modifikon learning core!
    """
    name: str
    traits: Dict[str, float]  # numeric weights vetëm
    description: str = ""
    active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    
    def get_weight(self, trait: str) -> float:
        """Merr peshën e një trait"""
        return self.traits.get(trait, 0.5)
    
    def influence_query(self, base_weights: Dict[str, float]) -> Dict[str, float]:
        """
        Ndikon parametrat e query me traits të personas.
        Vetëm numeric, asnjë side-effect në core!
        """
        influenced = {}
        for key, value in base_weights.items():
            if key in self.traits:
                # Blend: 70% base, 30% persona influence
                influenced[key] = value * 0.7 + self.traits[key] * 0.3
            else:
                influenced[key] = value
        return influenced
    
    def to_dict(self) -> dict:
        """Serialize për storage/API"""
        return {
            "name": self.name,
            "traits": self.traits,
            "description": self.description,
            "active": self.active,
            "created_at": self.created_at.isoformat()
        }


# ============================================================
# ACTIVE PERSONAS (MAX 3)
# ============================================================

ANALYST = Persona(
    name="Analyst",
    traits={
        "logic": 0.95,
        "creativity": 0.4,
        "precision": 0.9,
        "speed": 0.6,
        "exploration": 0.3
    },
    description="Focused on data analysis, patterns, and logical reasoning"
)

CREATIVE = Persona(
    name="Creative", 
    traits={
        "logic": 0.5,
        "creativity": 0.95,
        "precision": 0.6,
        "speed": 0.7,
        "exploration": 0.9
    },
    description="Explores ideas, generates alternatives, thinks laterally"
)

EXECUTOR = Persona(
    name="Executor",
    traits={
        "logic": 0.75,
        "creativity": 0.5,
        "precision": 0.85,
        "speed": 0.9,
        "exploration": 0.4
    },
    description="Gets things done efficiently, practical solutions"
)

# Lista aktive - MAX 3
ACTIVE_PERSONAS: List[Persona] = [ANALYST, CREATIVE, EXECUTOR]


# ============================================================
# STORED PROFILES (read-only, për zgjerim të ardhshëm)
# ============================================================

STORED_PROFILES: Dict[str, Persona] = {
    "researcher": Persona(
        name="Researcher",
        traits={"logic": 0.85, "creativity": 0.7, "precision": 0.8, "speed": 0.5, "exploration": 0.85},
        description="Deep dives into topics",
        active=False
    ),
    "strategist": Persona(
        name="Strategist", 
        traits={"logic": 0.8, "creativity": 0.75, "precision": 0.7, "speed": 0.6, "exploration": 0.7},
        description="Long-term planning and vision",
        active=False
    ),
    "mentor": Persona(
        name="Mentor",
        traits={"logic": 0.7, "creativity": 0.6, "precision": 0.65, "speed": 0.5, "exploration": 0.6},
        description="Teaching and guidance focus",
        active=False
    )
}


# ============================================================
# INTERFACE FUNCTIONS
# ============================================================

def get_active_personas() -> List[Persona]:
    """Kthen listën e personas aktive"""
    return [p for p in ACTIVE_PERSONAS if p.active]


def get_persona_by_name(name: str) -> Optional[Persona]:
    """Gjen persona me emër"""
    for p in ACTIVE_PERSONAS:
        if p.name.lower() == name.lower():
            return p
    return STORED_PROFILES.get(name.lower())


def apply_persona_influence(persona_name: str, base_weights: Dict[str, float]) -> Dict[str, float]:
    """
    Apliko ndikimin e një persona në weights.
    SAFE: nuk prek core, vetëm kthen weights të modifikuar.
    """
    persona = get_persona_by_name(persona_name)
    if persona:
        return persona.influence_query(base_weights)
    return base_weights


def list_all_personas() -> List[dict]:
    """Lista të gjitha personas (aktive + stored)"""
    result = []
    for p in ACTIVE_PERSONAS:
        d = p.to_dict()
        d["status"] = "active"
        result.append(d)
    for name, p in STORED_PROFILES.items():
        d = p.to_dict()
        d["status"] = "stored"
        result.append(d)
    return result


def persona_stats() -> dict:
    """Stats për personas"""
    return {
        "active_count": len([p for p in ACTIVE_PERSONAS if p.active]),
        "stored_count": len(STORED_PROFILES),
        "max_active": 3,
        "personas": [p.name for p in ACTIVE_PERSONAS if p.active]
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🎭 KLOUD PERSONAS INTERFACE v1.0")
    print("=" * 60)
    
    print("\n📊 Active Personas:")
    for p in get_active_personas():
        print(f"  • {p.name}: {p.traits}")
    
    print("\n📦 Stored Profiles:")
    for name, p in STORED_PROFILES.items():
        print(f"  • {p.name}: {p.traits}")
    
    print("\n🔧 Test influence_query:")
    base = {"logic": 0.5, "creativity": 0.5, "speed": 0.5}
    influenced = apply_persona_influence("Analyst", base)
    print(f"  Base: {base}")
    print(f"  With Analyst: {influenced}")
    
    print("\n📈 Stats:")
    print(f"  {persona_stats()}")
    
    print("\n✅ Personas interface OK - nuk prek auto_learning_core!")

