"""
CODE ANALYZER - Code Understanding and Analysis AI Process
===========================================================
Analyzes source code for structure, quality, and insights.

Features:
- Multi-language support (Python, JavaScript, TypeScript, etc.)
- Code structure analysis
- Complexity metrics
- Code smell detection
- Documentation extraction
- Dependency analysis
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class CodeLanguage(Enum):
    """Supported programming languages"""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"
    SQL = "sql"
    HTML = "html"
    CSS = "css"
    JSON = "json"
    YAML = "yaml"
    UNKNOWN = "unknown"


class CodeSmellType(Enum):
    """Types of code smells"""

    LONG_FUNCTION = "long_function"
    DEEP_NESTING = "deep_nesting"
    MAGIC_NUMBERS = "magic_numbers"
    DUPLICATE_CODE = "duplicate_code"
    LONG_PARAMETER_LIST = "long_parameter_list"
    COMMENTED_CODE = "commented_code"
    TODO_FIXME = "todo_fixme"
    MISSING_DOCSTRING = "missing_docstring"
    HARDCODED_VALUES = "hardcoded_values"


@dataclass
class CodeFunction:
    """Extracted function/method"""

    name: str
    line_start: int
    line_end: int
    parameters: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    complexity: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "lines": {"start": self.line_start, "end": self.line_end},
            "parameters": self.parameters,
            "return_type": self.return_type,
            "has_docstring": bool(self.docstring),
            "complexity": self.complexity,
        }


@dataclass
class CodeClass:
    """Extracted class definition"""

    name: str
    line_start: int
    line_end: int
    methods: List[str]
    base_classes: List[str]
    docstring: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "lines": {"start": self.line_start, "end": self.line_end},
            "methods": self.methods,
            "base_classes": self.base_classes,
            "has_docstring": bool(self.docstring),
        }


@dataclass
class CodeSmell:
    """Detected code smell"""

    smell_type: CodeSmellType
    description: str
    line: int
    severity: str  # low, medium, high
    suggestion: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.smell_type.value,
            "description": self.description,
            "line": self.line,
            "severity": self.severity,
            "suggestion": self.suggestion,
        }


@dataclass
class CodeAnalysisResult:
    """Result of code analysis"""

    code_preview: str
    language: str
    lines_total: int
    lines_code: int
    lines_comment: int
    lines_blank: int
    functions: List[CodeFunction]
    classes: List[CodeClass]
    imports: List[str]
    code_smells: List[CodeSmell]
    complexity_score: int
    quality_score: float
    processing_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "language": self.language,
            "lines": {"total": self.lines_total, "code": self.lines_code, "comment": self.lines_comment, "blank": self.lines_blank},
            "functions": [f.to_dict() for f in self.functions],
            "classes": [c.to_dict() for c in self.classes],
            "imports": self.imports,
            "code_smells": [s.to_dict() for s in self.code_smells],
            "complexity_score": self.complexity_score,
            "quality_score": round(self.quality_score, 2),
            "processing_time_ms": round(self.processing_time_ms, 2),
        }


class CodeAnalyzer:
    """
    Code Understanding and Analysis Engine

    Analyzes source code structure, quality, and provides insights
    """

    # Language detection patterns
    LANGUAGE_PATTERNS = {
        CodeLanguage.PYTHON: [
            r"^import\s+\w+",
            r"^from\s+\w+\s+import",
            r"^def\s+\w+\s*\(",
            r"^class\s+\w+",
            r"^if\s+__name__\s*==",
            r":\s*$",
        ],
        CodeLanguage.JAVASCRIPT: [
            r"^const\s+\w+\s*=",
            r"^let\s+\w+\s*=",
            r"^var\s+\w+\s*=",
            r"^function\s+\w+",
            r"=>\s*{",
            r'^import\s+.*from\s+[\'"]',
            r"^export\s+(default\s+)?",
        ],
        CodeLanguage.TYPESCRIPT: [
            r":\s*(string|number|boolean|void|any)\b",
            r"interface\s+\w+",
            r"type\s+\w+\s*=",
            r"<\w+>",
            r'^import\s+.*from\s+[\'"]',
        ],
        CodeLanguage.SQL: [r"^\s*SELECT\s+", r"^\s*INSERT\s+INTO", r"^\s*UPDATE\s+", r"^\s*DELETE\s+FROM", r"^\s*CREATE\s+TABLE"],
        CodeLanguage.HTML: [r"^\s*<!DOCTYPE", r"<html", r"<head>", r"<body>", r"</div>", r"</span>"],
        CodeLanguage.JSON: [r"^\s*\{", r"^\s*\[", r'"\w+":\s*'],
        CodeLanguage.YAML: [r"^\w+:\s*$", r"^\s*-\s+\w+", r"^\s*\w+:\s+\w+"],
    }

    def __init__(self, ollama_host: Optional[str] = None):
        self.ollama_host = ollama_host or "http://kloud-clx:11434"
        self._initialized = False
        logger.info("💻 CodeAnalyzer initialized")

    async def initialize(self):
        """Initialize the analyzer"""
        if self._initialized:
            return
        self._initialized = True
        logger.info("✅ CodeAnalyzer ready")

    async def analyze(self, code: str, language: Optional[str] = None, analyze_smells: bool = True) -> CodeAnalysisResult:
        """
        Analyze source code

        Args:
            code: Source code to analyze
            language: Programming language (auto-detected if None)
            analyze_smells: Whether to detect code smells
        """
        start_time = datetime.now()

        lines = code.split("\n")

        # Detect language
        if language:
            detected_lang = language.lower()
        else:
            detected_lang = self._detect_language(code)

        # Count lines
        lines_total = len(lines)
        lines_blank = sum(1 for l in lines if not l.strip())
        lines_comment = self._count_comments(lines, detected_lang)
        lines_code = lines_total - lines_blank - lines_comment

        # Extract structure
        functions = self._extract_functions(code, detected_lang)
        classes = self._extract_classes(code, detected_lang)
        imports = self._extract_imports(code, detected_lang)

        # Detect code smells
        code_smells = []
        if analyze_smells:
            code_smells = self._detect_smells(code, lines, detected_lang)

        # Calculate metrics
        complexity = self._calculate_complexity(code, functions)
        quality = self._calculate_quality(lines_total, lines_code, lines_comment, functions, classes, code_smells)

        processing_time = (datetime.now() - start_time).total_seconds() * 1000

        return CodeAnalysisResult(
            code_preview=code[:300] + "..." if len(code) > 300 else code,
            language=detected_lang,
            lines_total=lines_total,
            lines_code=lines_code,
            lines_comment=lines_comment,
            lines_blank=lines_blank,
            functions=functions,
            classes=classes,
            imports=imports,
            code_smells=code_smells,
            complexity_score=complexity,
            quality_score=quality,
            processing_time_ms=processing_time,
        )

    def _detect_language(self, code: str) -> str:
        """Detect programming language"""
        scores: Dict[str, int] = {}

        for lang, patterns in self.LANGUAGE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, code, re.MULTILINE | re.IGNORECASE):
                    score += 1
            if score > 0:
                scores[lang.value] = score

        if scores:
            return max(scores, key=scores.get)

        return CodeLanguage.UNKNOWN.value

    def _count_comments(self, lines: List[str], language: str) -> int:
        """Count comment lines"""
        count = 0
        in_multiline = False

        for line in lines:
            stripped = line.strip()

            # Python
            if language == "python":
                if stripped.startswith("#"):
                    count += 1
                elif '"""' in stripped or "'''" in stripped:
                    in_multiline = not in_multiline
                    count += 1
                elif in_multiline:
                    count += 1

            # JavaScript/TypeScript
            elif language in ("javascript", "typescript"):
                if stripped.startswith("//"):
                    count += 1
                elif "/*" in stripped:
                    in_multiline = True
                    count += 1
                elif "*/" in stripped:
                    in_multiline = False
                    count += 1
                elif in_multiline:
                    count += 1

            # SQL
            elif language == "sql":
                if stripped.startswith("--"):
                    count += 1

        return count

    def _extract_functions(self, code: str, language: str) -> List[CodeFunction]:
        """Extract function definitions"""
        functions = []
        lines = code.split("\n")

        if language == "python":
            pattern = r"^(\s*)def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*(\w+))?:"
            for i, line in enumerate(lines):
                match = re.match(pattern, line)
                if match:
                    indent = len(match.group(1))
                    name = match.group(2)
                    params = [p.strip().split(":")[0].strip() for p in match.group(3).split(",") if p.strip()]
                    return_type = match.group(4)

                    # Find end of function
                    end_line = i + 1
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j].startswith(" " * (indent + 1)):
                            if not lines[j].startswith(" " * (indent + 1)):
                                break
                        end_line = j + 1

                    # Check for docstring
                    docstring = None
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line.startswith('"""') or next_line.startswith("'''"):
                            docstring = next_line

                    functions.append(
                        CodeFunction(
                            name=name,
                            line_start=i + 1,
                            line_end=end_line,
                            parameters=params,
                            return_type=return_type,
                            docstring=docstring,
                            complexity=self._function_complexity(lines[i:end_line]),
                        )
                    )

        elif language in ("javascript", "typescript"):
            patterns = [
                r"^(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)",
                r"^(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>",
                r"^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*function",
            ]
            for i, line in enumerate(lines):
                for pattern in patterns:
                    match = re.match(pattern, line.strip())
                    if match:
                        name = match.group(1)
                        functions.append(
                            CodeFunction(
                                name=name,
                                line_start=i + 1,
                                line_end=i + 1,  # Simplified
                                parameters=[],
                                return_type=None,
                                docstring=None,
                                complexity=1,
                            )
                        )
                        break

        return functions

    def _extract_classes(self, code: str, language: str) -> List[CodeClass]:
        """Extract class definitions"""
        classes = []
        lines = code.split("\n")

        if language == "python":
            pattern = r"^class\s+(\w+)(?:\s*\(([^)]*)\))?:"
            for i, line in enumerate(lines):
                match = re.match(pattern, line)
                if match:
                    name = match.group(1)
                    bases = []
                    if match.group(2):
                        bases = [b.strip() for b in match.group(2).split(",")]

                    # Find methods
                    methods = []
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip().startswith("def "):
                            method_match = re.match(r"\s*def\s+(\w+)", lines[j])
                            if method_match:
                                methods.append(method_match.group(1))

                    classes.append(
                        CodeClass(name=name, line_start=i + 1, line_end=i + 1, methods=methods, base_classes=bases, docstring=None)
                    )

        return classes

    def _extract_imports(self, code: str, language: str) -> List[str]:
        """Extract import statements"""
        imports = []

        if language == "python":
            patterns = [r"^import\s+([\w.]+)", r"^from\s+([\w.]+)\s+import"]
            for pattern in patterns:
                imports.extend(re.findall(pattern, code, re.MULTILINE))

        elif language in ("javascript", "typescript"):
            patterns = [r'import\s+.*from\s+[\'"]([^\'"]+)[\'"]', r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)']
            for pattern in patterns:
                imports.extend(re.findall(pattern, code))

        return list(set(imports))

    def _detect_smells(self, code: str, lines: List[str], language: str) -> List[CodeSmell]:
        """Detect code smells"""
        smells = []

        # Long function (>50 lines for now, simplified)
        if language == "python":
            for i, line in enumerate(lines):
                if line.strip().startswith("def "):
                    # Count subsequent indented lines
                    func_lines = 0
                    for j in range(i + 1, len(lines)):
                        if lines[j].strip() and not lines[j][0].isspace():
                            break
                        func_lines += 1

                    if func_lines > 50:
                        smells.append(
                            CodeSmell(
                                smell_type=CodeSmellType.LONG_FUNCTION,
                                description=f"Function has {func_lines} lines",
                                line=i + 1,
                                severity="medium",
                                suggestion="Consider breaking into smaller functions",
                            )
                        )

        # TODO/FIXME comments
        for i, line in enumerate(lines):
            if "TODO" in line or "FIXME" in line or "XXX" in line:
                smells.append(
                    CodeSmell(
                        smell_type=CodeSmellType.TODO_FIXME,
                        description="Contains TODO/FIXME comment",
                        line=i + 1,
                        severity="low",
                        suggestion="Address or track these items",
                    )
                )

        # Magic numbers
        magic_pattern = r'(?<!["\'\w])\b(\d{2,})\b(?!["\'])'
        for i, line in enumerate(lines):
            if re.search(magic_pattern, line):
                if not line.strip().startswith("#") and not line.strip().startswith("//"):
                    smells.append(
                        CodeSmell(
                            smell_type=CodeSmellType.MAGIC_NUMBERS,
                            description="Contains magic numbers",
                            line=i + 1,
                            severity="low",
                            suggestion="Use named constants instead",
                        )
                    )

        # Deep nesting
        for i, line in enumerate(lines):
            indent = len(line) - len(line.lstrip())
            spaces_per_indent = 4 if language == "python" else 2
            nesting_level = indent // spaces_per_indent

            if nesting_level > 4:
                smells.append(
                    CodeSmell(
                        smell_type=CodeSmellType.DEEP_NESTING,
                        description=f"Nesting level: {nesting_level}",
                        line=i + 1,
                        severity="medium",
                        suggestion="Reduce nesting with early returns or extraction",
                    )
                )

        return smells

    def _function_complexity(self, func_lines: List[str]) -> int:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1

        decision_patterns = [
            r"\bif\b",
            r"\belif\b",
            r"\belse\b",
            r"\bfor\b",
            r"\bwhile\b",
            r"\band\b",
            r"\bor\b",
            r"\btry\b",
            r"\bexcept\b",
            r"\bcase\b",
        ]

        code = "\n".join(func_lines)
        for pattern in decision_patterns:
            complexity += len(re.findall(pattern, code))

        return complexity

    def _calculate_complexity(self, code: str, functions: List[CodeFunction]) -> int:
        """Calculate overall code complexity"""
        if not functions:
            return 1

        return sum(f.complexity for f in functions)

    def _calculate_quality(
        self,
        lines_total: int,
        lines_code: int,
        lines_comment: int,
        functions: List[CodeFunction],
        classes: List[CodeClass],
        smells: List[CodeSmell],
    ) -> float:
        """Calculate code quality score (0-100)"""
        score = 100.0

        # Comment ratio (penalize if too low)
        if lines_code > 0:
            comment_ratio = lines_comment / lines_code
            if comment_ratio < 0.1:
                score -= 10

        # Code smells
        for smell in smells:
            if smell.severity == "high":
                score -= 10
            elif smell.severity == "medium":
                score -= 5
            else:
                score -= 2

        # Docstrings
        funcs_with_docs = sum(1 for f in functions if f.docstring)
        if functions:
            doc_ratio = funcs_with_docs / len(functions)
            if doc_ratio < 0.5:
                score -= 10

        # Complexity penalty
        total_complexity = sum(f.complexity for f in functions)
        if total_complexity > 20:
            score -= total_complexity - 20

        return max(0, min(100, score))


# Singleton instance
_code_analyzer: Optional[CodeAnalyzer] = None


def get_code_analyzer() -> CodeAnalyzer:
    """Get or create code analyzer instance"""
    global _code_analyzer
    if _code_analyzer is None:
        _code_analyzer = CodeAnalyzer()
    return _code_analyzer
