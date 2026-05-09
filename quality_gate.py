#!/usr/bin/env python3
"""
KLOUD QUALITY GATE
======================

Quality control for content before publishing.
Ensures all content meets our standards:
- Real code (not fake imports)
- Real metrics (not "Example: 42")
- Expert-level depth
- Technical accuracy

Author: Ledjan Ahmati (CEO, ABA GmbH)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List


@dataclass
class QualityReport:
    """Report from quality gate validation"""
    passed: bool
    score: float
    word_count: int
    has_real_code: bool
    has_real_metrics: bool
    has_fake_imports: bool
    issues: List[str]
    recommendations: List[str]
    validated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ═══════════════════════════════════════════════════════════════════════════════
# FAKE CODE PATTERNS TO DETECT
# ═══════════════════════════════════════════════════════════════════════════════

FAKE_IMPORT_PATTERNS = [
    # Fake Kloud imports that don't exist
    r"from kloud\.alda import",
    r"from kloud\.liam import",
    r"from kloud\.blerina import",
    r"from kloud_sdk import",
    r"import kloud\.neural",
    r"import kloud\.mesh",
    
    # Fake libraries
    r"from neural_mesh import",
    r"from tide_engine import",
    r"from crdt_layer import",
    r"import WaveSyncProtocol",
    r"from cognitive_load_detector import",
    
    # Overly generic fake imports
    r"from advanced_ai import",
    r"from quantum_neural import",
    r"from enterprise_ml import",
]

FAKE_DATA_PATTERNS = [
    # Placeholder data
    r"\| Example \| 42 \|",
    r"Example:\s*42",
    r"value:\s*42\s*#\s*example",
    r"result\s*=\s*42\s*#",
    
    # Fake metrics
    r"accuracy:\s*99\.9%",
    r"latency:\s*0\.001ms",
    r"uptime:\s*100%",
    
    # Lorem ipsum
    r"lorem ipsum",
    r"foo bar baz",
    r"test data here",
]

REAL_CODE_INDICATORS = [
    # Real imports from our codebase
    r"from alda_core import",
    r"from liam_core import",
    r"from blerina_core import",
    r"from signal_processing_core import",
    
    # Real libraries
    r"import numpy as np",
    r"from scipy import signal",
    r"import mne",
    r"from fastapi import",
    r"import asyncio",
    
    # Real patterns
    r"async def ",
    r"@dataclass",
    r"class \w+:",
    r"def __init__",
]


class QualityGate:
    """
    Quality gate for Kloud content.
    
    Validates:
    1. No fake imports
    2. Real production metrics
    3. Minimum word count
    4. Technical accuracy
    """
    
    MIN_PILLAR_WORDS = 3000
    MIN_BLOG_WORDS = 800
    MIN_QUALITY_SCORE = 0.85
    
    def __init__(self):
        self.fake_import_patterns = [re.compile(p, re.IGNORECASE) for p in FAKE_IMPORT_PATTERNS]
        self.fake_data_patterns = [re.compile(p, re.IGNORECASE) for p in FAKE_DATA_PATTERNS]
        self.real_code_patterns = [re.compile(p) for p in REAL_CODE_INDICATORS]
    
    def validate(self, content: str, content_type: str = "pillar") -> QualityReport:
        """
        Validate content against quality standards.
        
        Args:
            content: The article/content to validate
            content_type: "pillar", "blog", "tutorial", etc.
        
        Returns:
            QualityReport with detailed analysis
        """
        issues = []
        recommendations = []
        
        # 1. Check word count
        word_count = len(content.split())
        min_words = self.MIN_PILLAR_WORDS if content_type == "pillar" else self.MIN_BLOG_WORDS
        
        if word_count < min_words:
            issues.append(f"Word count ({word_count}) below minimum ({min_words})")
            recommendations.append(f"Add more depth - need {min_words - word_count} more words")
        
        # 2. Check for fake imports
        fake_imports_found = self._find_fake_imports(content)
        has_fake_imports = len(fake_imports_found) > 0
        
        if has_fake_imports:
            issues.append(f"Found {len(fake_imports_found)} fake import(s)")
            for fake in fake_imports_found:
                issues.append(f"  - Fake import: {fake}")
            recommendations.append("Replace fake imports with real ones from alda_core.py, liam_core.py, etc.")
        
        # 3. Check for fake data
        fake_data_found = self._find_fake_data(content)
        if fake_data_found:
            issues.append(f"Found {len(fake_data_found)} fake data pattern(s)")
            for fake in fake_data_found:
                issues.append(f"  - Fake data: {fake}")
            recommendations.append("Replace with real production metrics from BLERINA API")
        
        # 4. Check for real code
        real_code_found = self._find_real_code(content)
        has_real_code = len(real_code_found) >= 3  # At least 3 real code patterns
        
        if not has_real_code:
            issues.append("Insufficient real code examples")
            recommendations.append("Include code snippets from actual repository files")
        
        # 5. Check for real metrics
        has_real_metrics = self._has_real_metrics(content)
        
        if not has_real_metrics:
            issues.append("No real production metrics found")
            recommendations.append("Add metrics from BLERINA /health or /analytics endpoints")
        
        # Calculate quality score
        score = self._calculate_score(
            word_count=word_count,
            min_words=min_words,
            has_fake_imports=has_fake_imports,
            has_real_code=has_real_code,
            has_real_metrics=has_real_metrics,
            fake_data_count=len(fake_data_found),
        )
        
        # Determine pass/fail
        passed = (
            score >= self.MIN_QUALITY_SCORE and
            not has_fake_imports and
            has_real_code and
            word_count >= min_words * 0.8  # Allow 20% tolerance
        )
        
        return QualityReport(
            passed=passed,
            score=score,
            word_count=word_count,
            has_real_code=has_real_code,
            has_real_metrics=has_real_metrics,
            has_fake_imports=has_fake_imports,
            issues=issues,
            recommendations=recommendations,
        )
    
    def _find_fake_imports(self, content: str) -> List[str]:
        """Find fake imports in content"""
        found = []
        for pattern in self.fake_import_patterns:
            matches = pattern.findall(content)
            found.extend(matches)
        return found
    
    def _find_fake_data(self, content: str) -> List[str]:
        """Find fake/placeholder data in content"""
        found = []
        for pattern in self.fake_data_patterns:
            matches = pattern.findall(content)
            found.extend(matches)
        return found
    
    def _find_real_code(self, content: str) -> List[str]:
        """Find real code patterns in content"""
        found = []
        for pattern in self.real_code_patterns:
            if pattern.search(content):
                found.append(pattern.pattern)
        return found
    
    def _has_real_metrics(self, content: str) -> bool:
        """Check if content has real metrics (not placeholders)"""
        # Look for specific metric patterns
        real_metric_patterns = [
            r"uptime_seconds:\s*\d+",
            r"processing_time_ms:\s*[\d.]+",
            r"containers:\s*\d+",
            r"accuracy:\s*\d{2}\.\d+%",  # e.g., 92.1%, not 99.9%
            r"latency.*\d+.*ms",
            r"timestamp.*\d{4}-\d{2}-\d{2}",
        ]
        
        for pattern in real_metric_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        
        return False
    
    def _calculate_score(
        self,
        word_count: int,
        min_words: int,
        has_fake_imports: bool,
        has_real_code: bool,
        has_real_metrics: bool,
        fake_data_count: int,
    ) -> float:
        """
        Calculate quality score (0-1).
        
        Weights:
        - Word count: 30%
        - No fake imports: 25%
        - Real code: 25%
        - Real metrics: 20%
        """
        # Word count score (30%)
        word_score = min(1.0, word_count / min_words) * 0.30
        
        # No fake imports (25%) - binary
        fake_import_score = 0.0 if has_fake_imports else 0.25
        
        # Real code (25%)
        real_code_score = 0.25 if has_real_code else 0.0
        
        # Real metrics (20%)
        real_metrics_score = 0.20 if has_real_metrics else 0.0
        
        # Penalty for fake data
        fake_data_penalty = min(0.10, fake_data_count * 0.02)
        
        total = word_score + fake_import_score + real_code_score + real_metrics_score - fake_data_penalty
        
        return max(0, min(1, total))


def validate_article(content: str, content_type: str = "pillar") -> QualityReport:
    """Convenience function to validate an article"""
    gate = QualityGate()
    return gate.validate(content, content_type)


def validate_file(file_path: str, content_type: str = "pillar") -> QualityReport:
    """Validate content from a file"""
    path = Path(file_path)
    if not path.exists():
        return QualityReport(
            passed=False,
            score=0.0,
            word_count=0,
            has_real_code=False,
            has_real_metrics=False,
            has_fake_imports=False,
            issues=[f"File not found: {file_path}"],
            recommendations=["Check file path"],
        )
    
    content = path.read_text(encoding='utf-8')
    return validate_article(content, content_type)


# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Quality Gate - Test")
    print("=" * 50)
    
    # Test with good content
    good_content = """
    # Building EEG Processing Systems
    
    In this article, we explore how to build real EEG processing systems.
    
    ```python
    from alda_core import ArtificialLaborEngine
    from signal_processing_core import SignalProcessor
    import numpy as np
    from scipy import signal
    
    class EEGPipeline:
        def __init__(self):
            self.processor = SignalProcessor()
        
        async def process(self, data: np.ndarray):
            return self.processor.process(data)
    ```
    
    ## Real Production Metrics
    
    From our BLERINA API:
    - uptime_seconds: 3600
    - processing_time_ms: 23.4
    - containers: 60
    - accuracy: 92.1%
    - timestamp: 2026-02-08T19:00:00Z
    
    """ + " word " * 2500  # Pad to meet word count
    
    report = validate_article(good_content)
    print("Good content:")
    print(f"  Passed: {report.passed}")
    print(f"  Score: {report.score:.2f}")
    print(f"  Issues: {len(report.issues)}")
    
    # Test with bad content
    bad_content = """
    # AI Example
    
    ```python
    from kloud.alda import LaborArray
    
    result = 42  # example
    ```
    
    | Example | 42 |
    
    accuracy: 99.9%
    """
    
    report = validate_article(bad_content, "blog")
    print("\nBad content:")
    print(f"  Passed: {report.passed}")
    print(f"  Score: {report.score:.2f}")
    print("  Issues:")
    for issue in report.issues:
        print(f"    - {issue}")

