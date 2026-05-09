"""
OCEAN ENTERPRISE MODULES
========================
Ultra-lightweight, high-tech enterprise intelligence layer.

10 Modules - Minimal code, Maximum impact:
- identity_kernel: Core personality & self-awareness
- boundary_engine: What Ocean does/doesn't do
- consistency_matrix: Same question = Same answer pattern
- cognitive_verifier: Double-check before responding
- ambiguity_resolver: Ask when unclear
- integrity_firewall: Block manipulation attempts
- tone_governor: Professional tone control
- stress_engine: Logic under pressure
- self_diagnostics: Self-assessment & learning
- behavior_contract: Formal behavior rules

Design Philosophy: <100 lines per module, pure Python, no heavy deps
"""

from .identity_kernel import IdentityKernel, get_identity
from .boundary_engine import BoundaryEngine, get_boundaries
from .consistency_matrix import ConsistencyMatrix, get_consistency
from .cognitive_verifier import CognitiveVerifier, get_verifier
from .ambiguity_resolver import AmbiguityResolver, get_resolver
from .integrity_firewall import IntegrityFirewall, get_firewall
from .tone_governor import ToneGovernor, get_tone
from .stress_engine import StressEngine, get_stress_handler
from .self_diagnostics import SelfDiagnostics, get_diagnostics
from .behavior_contract import BehaviorContract, get_contract
from .enterprise_guard import EnterpriseGuard, get_enterprise_guard

__all__ = [
    "IdentityKernel", "get_identity",
    "BoundaryEngine", "get_boundaries", 
    "ConsistencyMatrix", "get_consistency",
    "CognitiveVerifier", "get_verifier",
    "AmbiguityResolver", "get_resolver",
    "IntegrityFirewall", "get_firewall",
    "ToneGovernor", "get_tone",
    "StressEngine", "get_stress_handler",
    "SelfDiagnostics", "get_diagnostics",
    "BehaviorContract", "get_contract",
    # Unified Guard
    "EnterpriseGuard", "get_enterprise_guard",
]

__version__ = "1.0.0"
__author__ = "Kloud Ocean Team"

