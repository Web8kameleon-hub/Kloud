"""
MEGA SIGNAL COLLECTOR - Të Gjitha Sinjalet e Kloud.com
==========================================================

Nga Git deri te file më i vogël, çdo paketë, çdo (,) çdo (.) çdo a+b=x

Skanimi i plotë:
- Git: commits, branches, tags, PRs, diffs
- Files: çdo file, çdo linjë, çdo karakter
- Packages: çdo modul, çdo dependency, çdo version
- Algebra: çdo operacion, çdo variabël, çdo ekuacion
- API: çdo endpoint, çdo request, çdo response
- Docker: çdo container, çdo image, çdo port
- Database: çdo tabelë, çdo kolonë, çdo rekord
"""

import os
import re
import json
import glob
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import ast
import importlib.util


class SignalType(Enum):
    """Llojet e sinjaleve"""
    # Git Signals
    GIT_COMMIT = "git.commit"
    GIT_BRANCH = "git.branch"
    GIT_TAG = "git.tag"
    GIT_DIFF = "git.diff"
    GIT_FILE_CHANGE = "git.file_change"
    GIT_AUTHOR = "git.author"
    
    # File Signals
    FILE_CREATED = "file.created"
    FILE_MODIFIED = "file.modified"
    FILE_CONTENT = "file.content"
    FILE_LINE = "file.line"
    FILE_FUNCTION = "file.function"
    FILE_CLASS = "file.class"
    FILE_IMPORT = "file.import"
    FILE_VARIABLE = "file.variable"
    
    # Package Signals
    PACKAGE_INSTALLED = "package.installed"
    PACKAGE_DEPENDENCY = "package.dependency"
    PACKAGE_VERSION = "package.version"
    PACKAGE_MODULE = "package.module"
    
    # API Signals
    API_ENDPOINT = "api.endpoint"
    API_REQUEST = "api.request"
    API_RESPONSE = "api.response"
    API_ERROR = "api.error"
    
    # Docker Signals
    DOCKER_CONTAINER = "docker.container"
    DOCKER_IMAGE = "docker.image"
    DOCKER_PORT = "docker.port"
    DOCKER_NETWORK = "docker.network"
    DOCKER_VOLUME = "docker.volume"
    
    # Algebra Signals
    ALGEBRA_OPERATION = "algebra.operation"
    ALGEBRA_VARIABLE = "algebra.variable"
    ALGEBRA_EQUATION = "algebra.equation"
    ALGEBRA_RESULT = "algebra.result"
    
    # Punctuation Signals (çdo pikë, çdo presje)
    PUNCT_COMMA = "punct.comma"
    PUNCT_DOT = "punct.dot"
    PUNCT_SEMICOLON = "punct.semicolon"
    PUNCT_COLON = "punct.colon"
    PUNCT_BRACKET = "punct.bracket"
    PUNCT_QUOTE = "punct.quote"
    
    # Data Signals
    DATA_JSON = "data.json"
    DATA_YAML = "data.yaml"
    DATA_CSV = "data.csv"
    DATA_SQL = "data.sql"
    
    # System Signals
    SYSTEM_CPU = "system.cpu"
    SYSTEM_MEMORY = "system.memory"
    SYSTEM_DISK = "system.disk"
    SYSTEM_NETWORK = "system.network"


@dataclass
class MegaSignal:
    """Një sinjal i vetëm me të gjitha detajet"""
    id: str
    type: SignalType
    source: str
    value: Any
    path: str = ""
    line: int = 0
    column: int = 0
    context: str = ""
    parent: str = ""
    children: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    hash: str = ""
    
    def __post_init__(self):
        if not self.hash:
            content = f"{self.type.value}:{self.source}:{self.value}:{self.path}:{self.line}"
            self.hash = hashlib.md5(content.encode()).hexdigest()[:12]


@dataclass 
class AlgebraExpression:
    """Një shprehje algjebrike"""
    expression: str
    variables: List[str]
    operators: List[str]
    result: Optional[Any] = None
    source_file: str = ""
    line_number: int = 0


class MegaSignalCollector:
    """
    Koleksionuesi Mega i Sinjaleve
    
    Skanon dhe mbledh TË GJITHA sinjalet:
    - Git repository
    - Të gjitha files
    - Të gjitha packages
    - Të gjitha API endpoints
    - Të gjitha Docker containers
    - Të gjitha operacionet algjebrike
    - Çdo pikësim (,.) 
    """
    
    def __init__(self, workspace_path: str = None):
        self.workspace = workspace_path or os.getcwd()
        self.signals: Dict[str, MegaSignal] = {}
        self.signal_graph: Dict[str, List[str]] = {}  # parent -> children
        self.algebra_expressions: List[AlgebraExpression] = []
        self.file_index: Dict[str, Dict] = {}
        self.git_data: Dict[str, Any] = {}
        self.package_data: Dict[str, Any] = {}
        self.api_data: Dict[str, Any] = {}
        self.docker_data: Dict[str, Any] = {}
        self.punctuation_stats: Dict[str, int] = {}
        
        # Counters
        self.stats = {
            "total_signals": 0,
            "git_signals": 0,
            "file_signals": 0,
            "package_signals": 0,
            "api_signals": 0,
            "docker_signals": 0,
            "algebra_signals": 0,
            "punct_signals": 0,
            "files_scanned": 0,
            "lines_scanned": 0,
            "functions_found": 0,
            "classes_found": 0,
            "imports_found": 0,
            "variables_found": 0,
            "commits_found": 0,
            "branches_found": 0,
            "endpoints_found": 0,
            "containers_found": 0,
        }
    
    def add_signal(self, signal: MegaSignal) -> str:
        """Shto një sinjal të ri"""
        self.signals[signal.id] = signal
        self.stats["total_signals"] += 1
        
        # Update graph
        if signal.parent:
            if signal.parent not in self.signal_graph:
                self.signal_graph[signal.parent] = []
            self.signal_graph[signal.parent].append(signal.id)
        
        return signal.id
    
    async def collect_all(self) -> Dict[str, Any]:
        """Mblidh TË GJITHA sinjalet"""
        print("🌊 MEGA SIGNAL COLLECTOR - Fillimi i skanimit të plotë...")
        print(f"📁 Workspace: {self.workspace}")
        
        # 1. Git Signals
        print("\n📊 [1/7] Skanim Git repository...")
        await self.collect_git_signals()
        
        # 2. File Signals
        print("\n📄 [2/7] Skanim të gjitha files...")
        await self.collect_file_signals()
        
        # 3. Package Signals
        print("\n📦 [3/7] Skanim packages dhe dependencies...")
        await self.collect_package_signals()
        
        # 4. API Signals
        print("\n🌐 [4/7] Skanim API endpoints...")
        await self.collect_api_signals()
        
        # 5. Docker Signals
        print("\n🐳 [5/7] Skanim Docker containers...")
        await self.collect_docker_signals()
        
        # 6. Algebra Signals
        print("\n🔢 [6/7] Skanim operacioneve algjebrike...")
        await self.collect_algebra_signals()
        
        # 7. Punctuation Signals
        print("\n✏️ [7/7] Skanim pikësimit (presje, pika)...")
        await self.collect_punctuation_signals()
        
        print(f"\n✅ MEGA SIGNAL COLLECTOR - Kompletuar!")
        print(f"   📊 Total Signals: {self.stats['total_signals']:,}")
        
        return self.get_full_report()
    
    async def collect_git_signals(self):
        """Mblidh sinjalet nga Git"""
        try:
            # Get all commits
            result = subprocess.run(
                ["git", "log", "--oneline", "-100"],
                capture_output=True, text=True, cwd=self.workspace
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(' ', 1)
                        commit_hash = parts[0]
                        message = parts[1] if len(parts) > 1 else ""
                        
                        signal = MegaSignal(
                            id=f"git-commit-{commit_hash}",
                            type=SignalType.GIT_COMMIT,
                            source="git",
                            value={"hash": commit_hash, "message": message},
                            context=message
                        )
                        self.add_signal(signal)
                        self.stats["git_signals"] += 1
                        self.stats["commits_found"] += 1
            
            # Get all branches
            result = subprocess.run(
                ["git", "branch", "-a"],
                capture_output=True, text=True, cwd=self.workspace
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    branch = line.strip().lstrip('* ')
                    if branch:
                        signal = MegaSignal(
                            id=f"git-branch-{branch.replace('/', '-')}",
                            type=SignalType.GIT_BRANCH,
                            source="git",
                            value=branch
                        )
                        self.add_signal(signal)
                        self.stats["git_signals"] += 1
                        self.stats["branches_found"] += 1
            
            # Get all tags
            result = subprocess.run(
                ["git", "tag"],
                capture_output=True, text=True, cwd=self.workspace
            )
            if result.returncode == 0:
                for tag in result.stdout.strip().split('\n'):
                    if tag:
                        signal = MegaSignal(
                            id=f"git-tag-{tag}",
                            type=SignalType.GIT_TAG,
                            source="git",
                            value=tag
                        )
                        self.add_signal(signal)
                        self.stats["git_signals"] += 1
            
            # Get changed files
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, cwd=self.workspace
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        status = line[:2].strip()
                        filepath = line[3:].strip()
                        signal = MegaSignal(
                            id=f"git-change-{hashlib.md5(filepath.encode()).hexdigest()[:8]}",
                            type=SignalType.GIT_FILE_CHANGE,
                            source="git",
                            value={"status": status, "file": filepath},
                            path=filepath
                        )
                        self.add_signal(signal)
                        self.stats["git_signals"] += 1
                        
        except Exception as e:
            print(f"   ⚠️ Git error: {e}")
    
    async def collect_file_signals(self):
        """Mblidh sinjalet nga të gjitha files"""
        # File patterns to scan
        patterns = [
            "**/*.py", "**/*.js", "**/*.ts", "**/*.tsx", "**/*.jsx",
            "**/*.json", "**/*.yaml", "**/*.yml", "**/*.md",
            "**/*.html", "**/*.css", "**/*.sql",
            "**/*.sh", "**/*.ps1", "**/*.bat",
            "**/Dockerfile*", "**/docker-compose*.yml",
            "**/requirements*.txt", "**/package*.json",
            "**/.env*", "**/config*"
        ]
        
        # Exclude patterns
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 
                       'dist', 'build', '.next', '.nuxt', 'coverage', '.pytest_cache'}
        
        all_files = set()
        for pattern in patterns:
            for filepath in glob.glob(os.path.join(self.workspace, pattern), recursive=True):
                # Check if in excluded directory
                path_parts = Path(filepath).parts
                if not any(excl in path_parts for excl in exclude_dirs):
                    all_files.add(filepath)
        
        for filepath in all_files:
            try:
                rel_path = os.path.relpath(filepath, self.workspace)
                stat = os.stat(filepath)
                
                # File signal
                file_signal = MegaSignal(
                    id=f"file-{hashlib.md5(rel_path.encode()).hexdigest()[:10]}",
                    type=SignalType.FILE_CONTENT,
                    source="filesystem",
                    value={
                        "name": os.path.basename(filepath),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                    },
                    path=rel_path,
                    metadata={"extension": os.path.splitext(filepath)[1]}
                )
                self.add_signal(file_signal)
                self.stats["file_signals"] += 1
                self.stats["files_scanned"] += 1
                
                # Read file content for analysis
                if stat.st_size < 1_000_000:  # < 1MB
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.split('\n')
                        self.stats["lines_scanned"] += len(lines)
                        
                        # Analyze Python files
                        if filepath.endswith('.py'):
                            await self._analyze_python_file(filepath, content, file_signal.id)
                        
                        # Analyze JS/TS files
                        elif filepath.endswith(('.js', '.ts', '.tsx', '.jsx')):
                            await self._analyze_js_file(filepath, content, file_signal.id)
                        
                        # Analyze JSON files
                        elif filepath.endswith('.json'):
                            await self._analyze_json_file(filepath, content, file_signal.id)
                            
            except Exception as e:
                pass  # Skip problematic files
    
    async def _analyze_python_file(self, filepath: str, content: str, parent_id: str):
        """Analizo një file Python"""
        try:
            tree = ast.parse(content)
            rel_path = os.path.relpath(filepath, self.workspace)
            
            for node in ast.walk(tree):
                # Functions
                if isinstance(node, ast.FunctionDef):
                    signal = MegaSignal(
                        id=f"func-{hashlib.md5(f'{rel_path}:{node.name}'.encode()).hexdigest()[:10]}",
                        type=SignalType.FILE_FUNCTION,
                        source="python",
                        value=node.name,
                        path=rel_path,
                        line=node.lineno,
                        parent=parent_id,
                        metadata={
                            "args": [arg.arg for arg in node.args.args],
                            "decorators": [self._get_decorator_name(d) for d in node.decorator_list]
                        }
                    )
                    self.add_signal(signal)
                    self.stats["file_signals"] += 1
                    self.stats["functions_found"] += 1
                
                # Classes
                elif isinstance(node, ast.ClassDef):
                    signal = MegaSignal(
                        id=f"class-{hashlib.md5(f'{rel_path}:{node.name}'.encode()).hexdigest()[:10]}",
                        type=SignalType.FILE_CLASS,
                        source="python",
                        value=node.name,
                        path=rel_path,
                        line=node.lineno,
                        parent=parent_id,
                        metadata={
                            "bases": [self._get_name(b) for b in node.bases],
                            "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                        }
                    )
                    self.add_signal(signal)
                    self.stats["file_signals"] += 1
                    self.stats["classes_found"] += 1
                
                # Imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        signal = MegaSignal(
                            id=f"import-{hashlib.md5(f'{rel_path}:{alias.name}'.encode()).hexdigest()[:10]}",
                            type=SignalType.FILE_IMPORT,
                            source="python",
                            value=alias.name,
                            path=rel_path,
                            line=node.lineno,
                            parent=parent_id
                        )
                        self.add_signal(signal)
                        self.stats["file_signals"] += 1
                        self.stats["imports_found"] += 1
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        signal = MegaSignal(
                            id=f"import-{hashlib.md5(f'{rel_path}:{module}.{alias.name}'.encode()).hexdigest()[:10]}",
                            type=SignalType.FILE_IMPORT,
                            source="python",
                            value=f"{module}.{alias.name}",
                            path=rel_path,
                            line=node.lineno,
                            parent=parent_id
                        )
                        self.add_signal(signal)
                        self.stats["file_signals"] += 1
                        self.stats["imports_found"] += 1
                
                # Variables (assignments at module level)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            signal = MegaSignal(
                                id=f"var-{hashlib.md5(f'{rel_path}:{target.id}:{node.lineno}'.encode()).hexdigest()[:10]}",
                                type=SignalType.FILE_VARIABLE,
                                source="python",
                                value=target.id,
                                path=rel_path,
                                line=node.lineno,
                                parent=parent_id
                            )
                            self.add_signal(signal)
                            self.stats["file_signals"] += 1
                            self.stats["variables_found"] += 1
                            
        except SyntaxError:
            pass
        except Exception:
            pass
    
    def _get_decorator_name(self, node) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return "unknown"
    
    def _get_name(self, node) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        return "unknown"
    
    async def _analyze_js_file(self, filepath: str, content: str, parent_id: str):
        """Analizo një file JavaScript/TypeScript"""
        rel_path = os.path.relpath(filepath, self.workspace)
        
        # Find functions
        func_patterns = [
            r'function\s+(\w+)',  # function name()
            r'const\s+(\w+)\s*=\s*(?:async\s*)?\(',  # const name = () or const name = async ()
            r'(\w+)\s*:\s*(?:async\s*)?\(',  # name: () in objects
            r'async\s+(\w+)\s*\(',  # async name()
        ]
        
        for pattern in func_patterns:
            for match in re.finditer(pattern, content):
                func_name = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                
                signal = MegaSignal(
                    id=f"jsfunc-{hashlib.md5(f'{rel_path}:{func_name}:{line_num}'.encode()).hexdigest()[:10]}",
                    type=SignalType.FILE_FUNCTION,
                    source="javascript",
                    value=func_name,
                    path=rel_path,
                    line=line_num,
                    parent=parent_id
                )
                self.add_signal(signal)
                self.stats["file_signals"] += 1
                self.stats["functions_found"] += 1
        
        # Find imports
        import_patterns = [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
        ]
        
        for pattern in import_patterns:
            for match in re.finditer(pattern, content):
                module = match.group(1)
                line_num = content[:match.start()].count('\n') + 1
                
                signal = MegaSignal(
                    id=f"jsimport-{hashlib.md5(f'{rel_path}:{module}'.encode()).hexdigest()[:10]}",
                    type=SignalType.FILE_IMPORT,
                    source="javascript",
                    value=module,
                    path=rel_path,
                    line=line_num,
                    parent=parent_id
                )
                self.add_signal(signal)
                self.stats["file_signals"] += 1
                self.stats["imports_found"] += 1
    
    async def _analyze_json_file(self, filepath: str, content: str, parent_id: str):
        """Analizo një file JSON"""
        try:
            data = json.loads(content)
            rel_path = os.path.relpath(filepath, self.workspace)
            
            def extract_keys(obj, prefix=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        full_key = f"{prefix}.{key}" if prefix else key
                        signal = MegaSignal(
                            id=f"json-{hashlib.md5(f'{rel_path}:{full_key}'.encode()).hexdigest()[:10]}",
                            type=SignalType.DATA_JSON,
                            source="json",
                            value={"key": full_key, "type": type(value).__name__},
                            path=rel_path,
                            parent=parent_id
                        )
                        self.add_signal(signal)
                        self.stats["file_signals"] += 1
                        
                        if isinstance(value, (dict, list)):
                            extract_keys(value, full_key)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj[:10]):  # Limit to first 10 items
                        extract_keys(item, f"{prefix}[{i}]")
            
            extract_keys(data)
        except json.JSONDecodeError:
            pass
    
    async def collect_package_signals(self):
        """Mblidh sinjalet nga packages"""
        # Python requirements
        req_files = glob.glob(os.path.join(self.workspace, "**/requirements*.txt"), recursive=True)
        for req_file in req_files:
            try:
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Parse package==version
                            match = re.match(r'([a-zA-Z0-9_-]+)(?:[=<>!]+(.+))?', line)
                            if match:
                                pkg_name = match.group(1)
                                version = match.group(2) or "latest"
                                
                                signal = MegaSignal(
                                    id=f"pkg-py-{pkg_name}",
                                    type=SignalType.PACKAGE_INSTALLED,
                                    source="pip",
                                    value={"name": pkg_name, "version": version},
                                    path=os.path.relpath(req_file, self.workspace)
                                )
                                self.add_signal(signal)
                                self.stats["package_signals"] += 1
            except Exception:
                pass
        
        # Node.js packages
        pkg_files = glob.glob(os.path.join(self.workspace, "**/package.json"), recursive=True)
        for pkg_file in pkg_files:
            # Skip node_modules
            if 'node_modules' in pkg_file:
                continue
            try:
                with open(pkg_file, 'r') as f:
                    data = json.load(f)
                    
                    # Dependencies
                    for dep_type in ['dependencies', 'devDependencies', 'peerDependencies']:
                        deps = data.get(dep_type, {})
                        for name, version in deps.items():
                            signal = MegaSignal(
                                id=f"pkg-npm-{name}",
                                type=SignalType.PACKAGE_INSTALLED,
                                source="npm",
                                value={"name": name, "version": version, "type": dep_type},
                                path=os.path.relpath(pkg_file, self.workspace)
                            )
                            self.add_signal(signal)
                            self.stats["package_signals"] += 1
            except Exception:
                pass
    
    async def collect_api_signals(self):
        """Mblidh sinjalet nga API endpoints"""
        # Scan Python files for FastAPI/Flask routes
        py_files = glob.glob(os.path.join(self.workspace, "**/*.py"), recursive=True)
        
        route_patterns = [
            r'@app\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'@router\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]',
            r'@bp\.(route|get|post)\s*\(\s*[\'"]([^\'"]+)[\'"]',
        ]
        
        for py_file in py_files:
            if '__pycache__' in py_file or '.venv' in py_file:
                continue
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    for pattern in route_patterns:
                        for match in re.finditer(pattern, content):
                            method = match.group(1).upper()
                            path = match.group(2)
                            line_num = content[:match.start()].count('\n') + 1
                            
                            signal = MegaSignal(
                                id=f"api-{method.lower()}-{hashlib.md5(path.encode()).hexdigest()[:8]}",
                                type=SignalType.API_ENDPOINT,
                                source="fastapi",
                                value={"method": method, "path": path},
                                path=os.path.relpath(py_file, self.workspace),
                                line=line_num
                            )
                            self.add_signal(signal)
                            self.stats["api_signals"] += 1
                            self.stats["endpoints_found"] += 1
            except Exception:
                pass
    
    async def collect_docker_signals(self):
        """Mblidh sinjalet nga Docker"""
        try:
            # Get running containers
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.ID}}|{{.Names}}|{{.Image}}|{{.Ports}}|{{.Status}}"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|')
                        if len(parts) >= 5:
                            container_id, name, image, ports, status = parts[:5]
                            
                            signal = MegaSignal(
                                id=f"docker-{name}",
                                type=SignalType.DOCKER_CONTAINER,
                                source="docker",
                                value={
                                    "id": container_id,
                                    "name": name,
                                    "image": image,
                                    "ports": ports,
                                    "status": status
                                }
                            )
                            self.add_signal(signal)
                            self.stats["docker_signals"] += 1
                            self.stats["containers_found"] += 1
                            
                            # Port signals
                            if ports:
                                for port_mapping in ports.split(','):
                                    port_signal = MegaSignal(
                                        id=f"docker-port-{name}-{hashlib.md5(port_mapping.encode()).hexdigest()[:6]}",
                                        type=SignalType.DOCKER_PORT,
                                        source="docker",
                                        value=port_mapping.strip(),
                                        parent=f"docker-{name}"
                                    )
                                    self.add_signal(port_signal)
                                    self.stats["docker_signals"] += 1
            
            # Get images
            result = subprocess.run(
                ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}|{{.Size}}"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line and '<none>' not in line:
                        parts = line.split('|')
                        if len(parts) >= 2:
                            image, size = parts[:2]
                            
                            signal = MegaSignal(
                                id=f"docker-image-{hashlib.md5(image.encode()).hexdigest()[:8]}",
                                type=SignalType.DOCKER_IMAGE,
                                source="docker",
                                value={"image": image, "size": size}
                            )
                            self.add_signal(signal)
                            self.stats["docker_signals"] += 1
                            
        except Exception as e:
            print(f"   ⚠️ Docker error: {e}")
    
    async def collect_algebra_signals(self):
        """Mblidh sinjalet algjebrike - çdo operacion matematikor"""
        # Scan for mathematical operations
        py_files = glob.glob(os.path.join(self.workspace, "**/*.py"), recursive=True)
        
        # Patterns for algebra operations
        algebra_patterns = [
            (r'(\w+)\s*=\s*(\w+)\s*\+\s*(\w+)', 'addition'),
            (r'(\w+)\s*=\s*(\w+)\s*-\s*(\w+)', 'subtraction'),
            (r'(\w+)\s*=\s*(\w+)\s*\*\s*(\w+)', 'multiplication'),
            (r'(\w+)\s*=\s*(\w+)\s*/\s*(\w+)', 'division'),
            (r'(\w+)\s*=\s*(\w+)\s*\*\*\s*(\w+)', 'power'),
            (r'(\w+)\s*=\s*(\w+)\s*%\s*(\w+)', 'modulo'),
            (r'sum\s*\(([^)]+)\)', 'sum'),
            (r'mean\s*\(([^)]+)\)', 'mean'),
            (r'max\s*\(([^)]+)\)', 'max'),
            (r'min\s*\(([^)]+)\)', 'min'),
            (r'len\s*\(([^)]+)\)', 'length'),
            (r'range\s*\(([^)]+)\)', 'range'),
            (r'abs\s*\(([^)]+)\)', 'absolute'),
            (r'sqrt\s*\(([^)]+)\)', 'sqrt'),
            (r'log\s*\(([^)]+)\)', 'logarithm'),
            (r'sin\s*\(([^)]+)\)', 'sine'),
            (r'cos\s*\(([^)]+)\)', 'cosine'),
        ]
        
        for py_file in py_files:
            if '__pycache__' in py_file or '.venv' in py_file:
                continue
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    rel_path = os.path.relpath(py_file, self.workspace)
                    
                    for pattern, op_type in algebra_patterns:
                        for match in re.finditer(pattern, content):
                            line_num = content[:match.start()].count('\n') + 1
                            expression = match.group(0)
                            
                            signal = MegaSignal(
                                id=f"algebra-{op_type}-{hashlib.md5(f'{rel_path}:{line_num}'.encode()).hexdigest()[:8]}",
                                type=SignalType.ALGEBRA_OPERATION,
                                source="python",
                                value={
                                    "operation": op_type,
                                    "expression": expression[:100]
                                },
                                path=rel_path,
                                line=line_num
                            )
                            self.add_signal(signal)
                            self.stats["algebra_signals"] += 1
                            
                            # Create algebra expression
                            self.algebra_expressions.append(AlgebraExpression(
                                expression=expression,
                                variables=re.findall(r'\b[a-zA-Z_]\w*\b', expression),
                                operators=re.findall(r'[+\-*/=%]', expression),
                                source_file=rel_path,
                                line_number=line_num
                            ))
                            
            except Exception:
                pass
    
    async def collect_punctuation_signals(self):
        """Mblidh statistika për çdo pikësim"""
        punctuation_chars = {
            ',': 'comma',
            '.': 'dot', 
            ';': 'semicolon',
            ':': 'colon',
            '(': 'paren_open',
            ')': 'paren_close',
            '[': 'bracket_open',
            ']': 'bracket_close',
            '{': 'brace_open',
            '}': 'brace_close',
            '"': 'quote_double',
            "'": 'quote_single',
            '=': 'equals',
            '+': 'plus',
            '-': 'minus',
            '*': 'asterisk',
            '/': 'slash',
            '!': 'exclamation',
            '?': 'question',
            '@': 'at',
            '#': 'hash',
            '$': 'dollar',
            '&': 'ampersand',
            '|': 'pipe',
            '<': 'less_than',
            '>': 'greater_than',
        }
        
        total_counts = {name: 0 for name in punctuation_chars.values()}
        
        # Scan all text files
        patterns = ["**/*.py", "**/*.js", "**/*.ts", "**/*.json", "**/*.md"]
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv'}
        
        for pattern in patterns:
            for filepath in glob.glob(os.path.join(self.workspace, pattern), recursive=True):
                path_parts = Path(filepath).parts
                if any(excl in path_parts for excl in exclude_dirs):
                    continue
                    
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        for char, name in punctuation_chars.items():
                            count = content.count(char)
                            total_counts[name] += count
                except Exception:
                    pass
        
        # Create signals for significant punctuation counts
        for name, count in total_counts.items():
            if count > 0:
                signal = MegaSignal(
                    id=f"punct-{name}",
                    type=SignalType.PUNCT_COMMA if name == 'comma' else SignalType.PUNCT_DOT,
                    source="punctuation",
                    value=count,
                    metadata={"character_type": name}
                )
                self.add_signal(signal)
                self.stats["punct_signals"] += 1
        
        self.punctuation_stats = total_counts
    
    def get_full_report(self) -> Dict[str, Any]:
        """Merr raportin e plotë të sinjaleve"""
        return {
            "timestamp": datetime.now().isoformat(),
            "workspace": self.workspace,
            "stats": self.stats,
            "punctuation_stats": self.punctuation_stats,
            "algebra_expressions_count": len(self.algebra_expressions),
            "signal_graph_nodes": len(self.signal_graph),
            "signals_by_type": self._get_signals_by_type(),
            "top_files": self._get_top_files(),
            "summary": {
                "total_signals": self.stats["total_signals"],
                "git": self.stats["git_signals"],
                "files": self.stats["file_signals"],
                "packages": self.stats["package_signals"],
                "apis": self.stats["api_signals"],
                "docker": self.stats["docker_signals"],
                "algebra": self.stats["algebra_signals"],
                "punctuation": self.stats["punct_signals"]
            }
        }
    
    def _get_signals_by_type(self) -> Dict[str, int]:
        """Numëro sinjalet sipas llojit"""
        counts = {}
        for signal in self.signals.values():
            type_name = signal.type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts
    
    def _get_top_files(self) -> List[Dict]:
        """Merr files me më shumë sinjale"""
        file_counts = {}
        for signal in self.signals.values():
            if signal.path:
                file_counts[signal.path] = file_counts.get(signal.path, 0) + 1
        
        sorted_files = sorted(file_counts.items(), key=lambda x: x[1], reverse=True)
        return [{"file": f, "signals": c} for f, c in sorted_files[:20]]
    
    def get_signal(self, signal_id: str) -> Optional[MegaSignal]:
        """Merr një sinjal specifik"""
        return self.signals.get(signal_id)
    
    def query_signals(self, 
                      signal_type: Optional[SignalType] = None,
                      source: Optional[str] = None,
                      path_pattern: Optional[str] = None) -> List[MegaSignal]:
        """Query sinjalet me filtra"""
        results = []
        for signal in self.signals.values():
            if signal_type and signal.type != signal_type:
                continue
            if source and signal.source != source:
                continue
            if path_pattern and not re.search(path_pattern, signal.path or ""):
                continue
            results.append(signal)
        return results
    
    def export_graph(self) -> Dict[str, Any]:
        """Eksporto grafin e sinjaleve"""
        nodes = []
        edges = []
        
        for signal_id, signal in self.signals.items():
            nodes.append({
                "id": signal_id,
                "type": signal.type.value,
                "label": str(signal.value)[:50],
                "source": signal.source
            })
            
            if signal.parent:
                edges.append({
                    "from": signal.parent,
                    "to": signal_id
                })
        
        return {"nodes": nodes, "edges": edges}


# Global instance
_collector: Optional[MegaSignalCollector] = None


def get_mega_collector(workspace: str = None) -> MegaSignalCollector:
    """Get or create the mega signal collector"""
    global _collector
    if _collector is None:
        _collector = MegaSignalCollector(workspace)
    return _collector


async def collect_all_signals(workspace: str = None) -> Dict[str, Any]:
    """Convenience function to collect all signals"""
    collector = get_mega_collector(workspace)
    return await collector.collect_all()

