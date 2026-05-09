# -*- coding: utf-8 -*-
"""
🧠 REAL LEARNING ENGINE
=======================
Mëson nga burime REALE - jo fake teach/mock!

Burime të vërteta:
1. Git history - kush kontribuoi, commits, authors
2. File contents - kod, komente, docstrings
3. Package info - pyproject.toml, setup.py
4. README files - dokumentacion
5. API responses - të dhëna reale
6. Environment - variables, configs

Author: Kloud Team
"""

import os
import re
import json
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path


@dataclass
class RealKnowledge:
    """Dije e vërtetë e nxjerrë nga burime reale"""
    topic: str
    value: Any
    source: str  # file path, git, api, etc.
    confidence: float
    extracted_at: datetime = field(default_factory=datetime.now)
    evidence: str = ""  # proof/citation


class RealLearningEngine:
    """
    Mëson nga burime REALE - asnjë mock!
    """
    
    def __init__(self, project_root: str = None):
        # Auto-detect project root - works in Docker (/app) and Windows
        if project_root is None:
            if Path("/app").exists() and Path("/app/ocean_api.py").exists():
                project_root = "/app"
            else:
                # Windows/Linux local development - go up from curiosity_algebra folder
                project_root = str(Path(__file__).parent.parent.parent)
        self.project_root = Path(project_root)
        self.knowledge: Dict[str, RealKnowledge] = {}
        self._learn_from_all_sources()
    
    def _learn_from_all_sources(self):
        """Mëso nga të gjitha burimet"""
        self._learn_from_git()
        self._learn_from_files()
        self._learn_from_packages()
        self._learn_from_readme()
        self._learn_from_code()
        self._learn_from_data_points()  # Skano të gjitha data sources
        self._learn_from_docker()
    
    def _learn_from_git(self):
        """Mëso nga Git history"""
        try:
            # Get all authors
            result = subprocess.run(
                ['git', 'log', '--format=%an', '--all'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                authors = list(set(result.stdout.strip().split('\n')))
                authors = [a for a in authors if a]  # Remove empty
                
                if authors:
                    self.knowledge['project_authors'] = RealKnowledge(
                        topic='project_authors',
                        value=authors,
                        source='git log',
                        confidence=1.0,
                        evidence=f"git log --format=%an --all"
                    )
                    
                    # Primary author (most commits)
                    author_counts = {}
                    for author in result.stdout.strip().split('\n'):
                        if author:
                            author_counts[author] = author_counts.get(author, 0) + 1
                    
                    if author_counts:
                        primary = max(author_counts, key=author_counts.get)
                        self.knowledge['primary_author'] = RealKnowledge(
                            topic='primary_author',
                            value=primary,
                            source='git log',
                            confidence=1.0,
                            evidence=f"{author_counts[primary]} commits"
                        )
            
            # Get first commit date
            result = subprocess.run(
                ['git', 'log', '--reverse', '--format=%ci', '-1'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout.strip():
                self.knowledge['project_started'] = RealKnowledge(
                    topic='project_started',
                    value=result.stdout.strip()[:10],  # Just date
                    source='git log',
                    confidence=1.0,
                    evidence='git log --reverse -1'
                )
            
            # Get total commits
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.knowledge['total_commits'] = RealKnowledge(
                    topic='total_commits',
                    value=int(result.stdout.strip()),
                    source='git',
                    confidence=1.0,
                    evidence='git rev-list --count HEAD'
                )
            
            # Get current branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                self.knowledge['current_branch'] = RealKnowledge(
                    topic='current_branch',
                    value=result.stdout.strip(),
                    source='git',
                    confidence=1.0,
                    evidence='git branch --show-current'
                )
                
        except Exception as e:
            pass  # Git not available
    
    def _learn_from_files(self):
        """Mëso nga struktura e skedarëve"""
        try:
            # Count files by type
            file_counts = {}
            total_lines = 0
            
            for ext in ['.py', '.ts', '.js', '.html', '.css', '.json', '.md', '.yaml', '.yml']:
                count = 0
                for f in self.project_root.rglob(f'*{ext}'):
                    if '.git' not in str(f) and 'node_modules' not in str(f):
                        count += 1
                        try:
                            total_lines += len(f.read_text(errors='ignore').split('\n'))
                        except:
                            pass
                if count > 0:
                    file_counts[ext] = count
            
            self.knowledge['file_counts'] = RealKnowledge(
                topic='file_counts',
                value=file_counts,
                source='filesystem',
                confidence=1.0,
                evidence=f"Scanned {self.project_root}"
            )
            
            self.knowledge['total_lines'] = RealKnowledge(
                topic='total_lines',
                value=total_lines,
                source='filesystem',
                confidence=0.95,
                evidence='Line count of source files'
            )
            
            # Count directories
            dirs = [d for d in self.project_root.iterdir() if d.is_dir() and not d.name.startswith('.')]
            self.knowledge['main_modules'] = RealKnowledge(
                topic='main_modules',
                value=[d.name for d in dirs],
                source='filesystem',
                confidence=1.0,
                evidence=str(self.project_root)
            )
            
        except Exception as e:
            pass
    
    def _learn_from_packages(self):
        """Mëso nga package files"""
        try:
            # pyproject.toml
            pyproject = self.project_root / 'pyproject.toml'
            if pyproject.exists():
                content = pyproject.read_text()
                
                # Project name
                match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    self.knowledge['project_name'] = RealKnowledge(
                        topic='project_name',
                        value=match.group(1),
                        source='pyproject.toml',
                        confidence=1.0,
                        evidence='name = ...'
                    )
                
                # Version
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    self.knowledge['project_version'] = RealKnowledge(
                        topic='project_version',
                        value=match.group(1),
                        source='pyproject.toml',
                        confidence=1.0,
                        evidence='version = ...'
                    )
                
                # Authors
                match = re.search(r'authors\s*=\s*\[(.*?)\]', content, re.DOTALL)
                if match:
                    authors_str = match.group(1)
                    authors = re.findall(r'["\']([^"\']+)["\']', authors_str)
                    if authors:
                        self.knowledge['package_authors'] = RealKnowledge(
                            topic='package_authors',
                            value=authors,
                            source='pyproject.toml',
                            confidence=1.0,
                            evidence='authors = [...]'
                        )
            
            # package.json
            pkg_json = self.project_root / 'package.json'
            if pkg_json.exists():
                data = json.loads(pkg_json.read_text())
                
                if 'name' in data:
                    self.knowledge['npm_name'] = RealKnowledge(
                        topic='npm_name',
                        value=data['name'],
                        source='package.json',
                        confidence=1.0,
                        evidence='name: ...'
                    )
                
                if 'version' in data:
                    self.knowledge['npm_version'] = RealKnowledge(
                        topic='npm_version',
                        value=data['version'],
                        source='package.json',
                        confidence=1.0,
                        evidence='version: ...'
                    )
                
                if 'author' in data:
                    self.knowledge['npm_author'] = RealKnowledge(
                        topic='npm_author',
                        value=data['author'],
                        source='package.json',
                        confidence=1.0,
                        evidence='author: ...'
                    )
                    
        except Exception as e:
            pass
    
    def _learn_from_readme(self):
        """Mëso nga README files"""
        try:
            for readme_name in ['README.md', 'README.txt', 'README']:
                readme = self.project_root / readme_name
                if readme.exists():
                    content = readme.read_text(errors='ignore')
                    
                    # Extract title
                    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                    if match:
                        self.knowledge['readme_title'] = RealKnowledge(
                            topic='readme_title',
                            value=match.group(1).strip(),
                            source=readme_name,
                            confidence=1.0,
                            evidence='# Title'
                        )
                    
                    # Extract description (first paragraph after title)
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if line.startswith('# '):
                            # Find next non-empty line
                            for j in range(i+1, min(i+10, len(lines))):
                                if lines[j].strip() and not lines[j].startswith('#'):
                                    self.knowledge['project_description'] = RealKnowledge(
                                        topic='project_description',
                                        value=lines[j].strip(),
                                        source=readme_name,
                                        confidence=0.9,
                                        evidence='README paragraph'
                                    )
                                    break
                            break
                    break
                    
        except Exception as e:
            pass
    
    def _learn_from_code(self):
        """Mëso nga kodi - docstrings, comments"""
        try:
            # Find main module docstrings
            for init_file in self.project_root.rglob('__init__.py'):
                if '.git' in str(init_file) or 'node_modules' in str(init_file):
                    continue
                
                content = init_file.read_text(errors='ignore')
                
                # Extract docstring
                match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                if match:
                    docstring = match.group(1).strip()
                    module_name = init_file.parent.name
                    
                    # Extract version from docstring
                    ver_match = re.search(r'Version:\s*([^\n]+)', docstring)
                    if ver_match:
                        self.knowledge[f'{module_name}_version'] = RealKnowledge(
                            topic=f'{module_name}_version',
                            value=ver_match.group(1).strip(),
                            source=str(init_file.relative_to(self.project_root)),
                            confidence=1.0,
                            evidence='Version: ...'
                        )
                    
                    # Extract author from docstring
                    auth_match = re.search(r'Author:\s*([^\n]+)', docstring)
                    if auth_match:
                        self.knowledge[f'{module_name}_author'] = RealKnowledge(
                            topic=f'{module_name}_author',
                            value=auth_match.group(1).strip(),
                            source=str(init_file.relative_to(self.project_root)),
                            confidence=1.0,
                            evidence='Author: ...'
                        )
                        
        except Exception as e:
            pass
    
    def _learn_from_docker(self):
        """Mëso nga Docker files"""
        try:
            for dockerfile in self.project_root.rglob('Dockerfile*'):
                if '.git' in str(dockerfile):
                    continue
                
                content = dockerfile.read_text(errors='ignore')
                
                # Base image
                match = re.search(r'^FROM\s+([^\s]+)', content, re.MULTILINE)
                if match:
                    key = f'docker_base_{dockerfile.name}'
                    self.knowledge[key] = RealKnowledge(
                        topic=key,
                        value=match.group(1),
                        source=dockerfile.name,
                        confidence=1.0,
                        evidence='FROM ...'
                    )
                
                # Exposed ports
                ports = re.findall(r'EXPOSE\s+(\d+)', content)
                if ports:
                    self.knowledge['exposed_ports'] = RealKnowledge(
                        topic='exposed_ports',
                        value=[int(p) for p in ports],
                        source='Dockerfile',
                        confidence=1.0,
                        evidence='EXPOSE ...'
                    )
                    
        except Exception as e:
            pass
    
    def _learn_from_data_points(self):
        """
        🔢 Skano të gjitha DATA POINTS në projekt
        APIs, IoT, LoRa, Nodes, Mesh, Monitoring, Balancers, etc.
        """
        try:
            data_points = {
                'apis': {'patterns': ['api', 'endpoint', 'router'], 'count': 0, 'files': []},
                'iot_sensors': {'patterns': ['iot', 'sensor', 'lora', 'lorawan', 'zigbee'], 'count': 0, 'files': []},
                'nodes_mesh': {'patterns': ['node', 'mesh', 'cluster', 'peer'], 'count': 0, 'files': []},
                'monitoring': {'patterns': ['prometheus', 'grafana', 'loki', 'victoria', 'datadog', 'metrics'], 'count': 0, 'files': []},
                'balancers': {'patterns': ['balancer', 'load_balance', 'proxy', 'haproxy', 'nginx'], 'count': 0, 'files': []},
                'databases': {'patterns': ['redis', 'postgres', 'mongo', 'sqlite', 'database', 'db_'], 'count': 0, 'files': []},
                'docker_k8s': {'patterns': ['docker', 'kubernetes', 'k8s', 'container', 'pod'], 'count': 0, 'files': []},
                'managers': {'patterns': ['manager', 'orchestrator', 'coordinator', 'scheduler'], 'count': 0, 'files': []},
                'services': {'patterns': ['service', 'daemon', 'worker', 'handler'], 'count': 0, 'files': []},
                'protocols': {'patterns': ['protocol', 'cbp', 'mqtt', 'websocket', 'grpc', 'http'], 'count': 0, 'files': []},
            }
            
            urls_found = set()
            total_matches = 0
            
            for py_file in self.project_root.rglob('*.py'):
                if '.git' in str(py_file) or '__pycache__' in str(py_file):
                    continue
                
                try:
                    content = py_file.read_text(errors='ignore').lower()
                    rel_path = str(py_file.relative_to(self.project_root))
                    
                    for category, info in data_points.items():
                        for pattern in info['patterns']:
                            if pattern in content:
                                info['count'] += 1
                                if rel_path not in info['files']:
                                    info['files'].append(rel_path)
                                total_matches += 1
                                break
                    
                    # Extract URLs
                    urls = re.findall(r'https?://[^\s\'"<>]+', content)
                    urls_found.update(urls)
                    
                except Exception:
                    pass
            
            # Store as knowledge
            summary = {cat: {'count': info['count'], 'files': len(info['files'])} 
                      for cat, info in data_points.items() if info['count'] > 0}
            
            self.knowledge['data_points'] = RealKnowledge(
                topic='data_points',
                value=summary,
                source='filesystem scan',
                confidence=1.0,
                evidence=f'Scanned {self.project_root}'
            )
            
            self.knowledge['total_data_points'] = RealKnowledge(
                topic='total_data_points',
                value=total_matches,
                source='filesystem',
                confidence=1.0,
                evidence='Pattern matching across all .py files'
            )
            
            self.knowledge['external_urls'] = RealKnowledge(
                topic='external_urls',
                value=list(urls_found)[:100],  # Limit to 100
                source='filesystem',
                confidence=0.9,
                evidence=f'Found {len(urls_found)} unique URLs'
            )
            
            # Category specific knowledge
            for category, info in data_points.items():
                if info['count'] > 0:
                    self.knowledge[f'dp_{category}'] = RealKnowledge(
                        topic=f'data_points_{category}',
                        value={'count': info['count'], 'files': info['files'][:20]},
                        source='filesystem',
                        confidence=1.0,
                        evidence=f"Pattern: {', '.join(info['patterns'])}"
                    )
                    
        except Exception as e:
            pass
    
    def query(self, question: str) -> Dict[str, Any]:
        """Përgjigju pyetjes me dije reale"""
        question_lower = question.lower()
        
        # Map questions to knowledge
        answer = None
        source = None
        confidence = 0.0
        evidence = ""
        
        # Who created/made/built this?
        if any(w in question_lower for w in ['kush', 'who', 'krijoi', 'created', 'made', 'author', 'built']):
            # Check multiple sources
            for key in ['primary_author', 'package_authors', 'npm_author', 'curiosity_algebra_author']:
                if key in self.knowledge:
                    k = self.knowledge[key]
                    answer = k.value
                    source = k.source
                    confidence = k.confidence
                    evidence = k.evidence
                    break
        
        # Version?
        elif any(w in question_lower for w in ['version', 'versioni']):
            for key in ['project_version', 'npm_version', 'curiosity_algebra_version']:
                if key in self.knowledge:
                    k = self.knowledge[key]
                    answer = k.value
                    source = k.source
                    confidence = k.confidence
                    evidence = k.evidence
                    break
        
        # When started?
        elif any(w in question_lower for w in ['when', 'kur', 'started', 'filloi', 'date']):
            if 'project_started' in self.knowledge:
                k = self.knowledge['project_started']
                answer = k.value
                source = k.source
                confidence = k.confidence
                evidence = k.evidence
        
        # How many commits?
        elif any(w in question_lower for w in ['commit', 'commits']):
            if 'total_commits' in self.knowledge:
                k = self.knowledge['total_commits']
                answer = f"{k.value} commits"
                source = k.source
                confidence = k.confidence
                evidence = k.evidence
        
        # How many files/lines?
        elif any(w in question_lower for w in ['file', 'files', 'skedar']):
            if 'file_counts' in self.knowledge:
                k = self.knowledge['file_counts']
                answer = k.value
                source = k.source
                confidence = k.confidence
                evidence = k.evidence
        
        elif any(w in question_lower for w in ['line', 'lines', 'rresht']):
            if 'total_lines' in self.knowledge:
                k = self.knowledge['total_lines']
                answer = f"{k.value:,} lines of code"
                source = k.source
                confidence = k.confidence
                evidence = k.evidence
        
        # Modules?
        elif any(w in question_lower for w in ['module', 'modules', 'component']):
            if 'main_modules' in self.knowledge:
                k = self.knowledge['main_modules']
                answer = k.value
                source = k.source
                confidence = k.confidence
                evidence = k.evidence
        
        # What is this project?
        elif any(w in question_lower for w in ['what is', 'cfare', 'about', 'description']):
            for key in ['project_description', 'readme_title', 'project_name']:
                if key in self.knowledge:
                    k = self.knowledge[key]
                    answer = k.value
                    source = k.source
                    confidence = k.confidence
                    evidence = k.evidence
                    break
        
        # Branch?
        elif any(w in question_lower for w in ['branch', 'dega']):
            if 'current_branch' in self.knowledge:
                k = self.knowledge['current_branch']
                answer = k.value
                source = k.source
                confidence = k.confidence
                evidence = k.evidence
        
        if answer:
            return {
                "success": True,
                "answer": answer,
                "source": source,
                "confidence": confidence,
                "evidence": evidence,
                "is_real": True,
                "is_mock": False
            }
        else:
            return {
                "success": False,
                "answer": None,
                "message": "No real knowledge found for this question",
                "available_topics": list(self.knowledge.keys()),
                "is_real": True,
                "is_mock": False
            }
    
    def get_all_knowledge(self) -> Dict[str, Any]:
        """Kthe gjithë dijet reale"""
        return {
            "total": len(self.knowledge),
            "knowledge": {
                k: {
                    "value": v.value,
                    "source": v.source,
                    "confidence": v.confidence,
                    "evidence": v.evidence,
                    "extracted_at": v.extracted_at.isoformat()
                }
                for k, v in self.knowledge.items()
            }
        }
    
    def refresh(self):
        """Rimëso nga burimet"""
        self.knowledge.clear()
        self._learn_from_all_sources()


# Global instance
_real_learning: Optional[RealLearningEngine] = None


def get_real_learning() -> RealLearningEngine:
    """Get global real learning engine"""
    global _real_learning
    if _real_learning is None:
        _real_learning = RealLearningEngine()
    return _real_learning


def get_real_learning_engine() -> RealLearningEngine:
    """Alias for get_real_learning"""
    return get_real_learning()

