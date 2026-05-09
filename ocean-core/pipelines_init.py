"""
CURIOSITY OCEAN
===============
AI Brain of Kloud Cloud with 5 Pipelines:

1. Core Reasoning Pipeline - Text processing & reasoning
2. Vision Pipeline - Image/screenshot processing (future)
3. Audio Pipeline - Speech-to-text (future)
4. Document Pipeline - PDF/DOCX parsing (future)
5. System Pipeline - Health, admin, logs

Created by Ledjan Ahmati
WEB8euroweb GmbH, Germany
https://kloud.cloud
"""

__version__ = "2.0.0"
__author__ = "Ledjan Ahmati"

from .core import (
    CoreReasoningPipeline,
    ReasoningMode,
    get_context_manager,
    get_reasoning_pipeline,
    get_safety_filter,
)
from .system import get_system_pipeline

__all__ = [
    "CoreReasoningPipeline",
    "ReasoningMode",
    "get_reasoning_pipeline",
    "get_context_manager",
    "get_safety_filter",
    "get_system_pipeline",
]

