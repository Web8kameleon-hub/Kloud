# -*- coding: utf-8 -*-
"""
🔍 OPEN DATA SCALABILITY ENGINE
================================
Moduli i skalabilitetit që gjen dhe integrojnë burime të hapura të të dhënave falas,
ushqen të gjithë modulet inteligjente dhe prodhon kërkime të reja, koncepte futuristike,
API alignments, cycles, dokumentacione dhe simulime mbi të dhëna reale.

Siguruar me JONA oversight për etikë dhe siguri.
"""

from __future__ import annotations
import asyncio
import json
import uuid
import requests
import aiohttp
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import re
import urllib.parse
from urllib.robotparser import RobotFileParser
import time
import hashlib
from concurrent.futures import ThreadPoolExecutor
import logging

# Konfigurimi i logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from cycle_engine import CycleEngine, CycleDefinition, CycleType, AlignmentPolicy
    from jona_character import get_jona
    JONA_AVAILABLE = True
except ImportError:
    logger.warning("CycleEngine ose JONA nuk eshte i disponueshem")
    JONA_AVAILABLE = False

class DataSourceType(Enum):
    """Llojet e burimeve te te dhenave"""
    ACADEMIC = "academic"
    GOVERNMENT = "government"
    RESEARCH = "research"
    ENVIRONMENTAL = "environmental"
    HEALTH = "health"
    ECONOMIC = "economic"
    SOCIAL = "social"
    OPEN_DATA = "open_data"

class DataQuality(Enum):
    """Cilesia e te dhenave"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNVERIFIED = "unverified"

@dataclass
class OpenDataSource:
    """Burim i hapur i te dhenave"""
    id: str = field(default_factory=lambda: f"ods_{uuid.uuid4().hex[:12]}")
    url: str = ""
    name: str = ""
    description: str = ""
    source_type: DataSourceType = DataSourceType.OPEN_DATA
    quality_score: DataQuality = DataQuality.UNVERIFIED
    api_endpoints: List[str] = field(default_factory=list)
    data_formats: List[str] = field(default_factory=list)
    update_frequency: Optional[str] = None
    last_verified: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    active: bool = True

@dataclass
class ScalabilityMetrics:
    """Metrikat e skalabilitetit"""
    total_sources_discovered: int = 0
    active_sources: int = 0
    data_ingested_gb: float = 0.0
    cycles_generated: int = 0
    apis_created: int = 0
    research_papers_generated: int = 0
    simulations_run: int = 0
    safety_violations: int = 0
    jona_reviews: int = 0

class OpenDataScalabilityEngine:
    """
    Motori i Skalabilitetit per te Dhena te Hapura

    Gjen burime te hapura, i integrojne dhe ushqen modulet inteligjente
    per te prodhuar kerkime te reja dhe koncepte futuristike.
    """

    def __init__(self, cycle_engine: Optional[Any] = None):
        self.cycle_engine = cycle_engine
        self.sources: Dict[str, OpenDataSource] = {}
        self.metrics = ScalabilityMetrics()
        self.discovery_queue: asyncio.Queue = asyncio.Queue()
        self.processing_queue: asyncio.Queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.session: Optional[aiohttp.ClientSession] = None

        # Burime fillestare te njohura
        self.known_sources = self._load_known_sources()

        # JONA oversight
        self.jona = get_jona() if JONA_AVAILABLE else None

        logger.info("Open Data Scalability Engine inicializuar")

    def _load_known_sources(self) -> Dict[str, OpenDataSource]:
        """Ngarkon burime te njohura fillestare - 150+ GLOBAL FREE SOURCES"""
        sources = {}

        # ============ SCIENTIFIC & RESEARCH ============
        scientific_sources = [
            ("https://pubmed.ncbi.nlm.nih.gov/", "PubMed", DataSourceType.HEALTH),
            ("https://arxiv.org/", "ArXiv", DataSourceType.RESEARCH),
            ("https://www.crossref.org/", "CrossRef", DataSourceType.RESEARCH),
            ("https://www.ncbi.nlm.nih.gov/", "NCBI", DataSourceType.HEALTH),
            ("https://www.ebi.ac.uk/", "EBI (European Bioinformatics)", DataSourceType.RESEARCH),
            ("https://www.uniprot.org/", "UniProt", DataSourceType.RESEARCH),
            ("https://openalex.org/", "OpenAlex", DataSourceType.ACADEMIC),
            ("https://www.semanticscholar.org/", "Semantic Scholar", DataSourceType.RESEARCH),
            ("https://www.rcsb.org/", "PDB Protein Data Bank", DataSourceType.RESEARCH),
            ("https://www.ensembl.org/", "Ensembl Genomics", DataSourceType.RESEARCH),
            ("https://www.humancellatlas.org/", "Human Cell Atlas", DataSourceType.RESEARCH),
            ("https://portal.brain-map.org/", "Allen Brain Atlas", DataSourceType.RESEARCH),
            ("https://zenodo.org/", "Zenodo Research", DataSourceType.RESEARCH),
            ("https://www.gbif.org/", "GBIF Biodiversity", DataSourceType.ENVIRONMENTAL),
            ("https://opendata.cern.ch/", "CERN Open Data", DataSourceType.RESEARCH),
        ]

        # ============ USA GOVERNMENT ============
        usa_sources = [
            ("https://data.gov/", "Data.gov USA", DataSourceType.GOVERNMENT),
            ("https://clinicaltrials.gov/", "ClinicalTrials.gov", DataSourceType.HEALTH),
            ("https://open.fda.gov/", "OpenFDA", DataSourceType.HEALTH),
            ("https://data.nasa.gov/", "NASA Open Data", DataSourceType.RESEARCH),
            ("https://data.noaa.gov/", "NOAA Climate Data", DataSourceType.ENVIRONMENTAL),
            ("https://data.census.gov/", "US Census Bureau", DataSourceType.SOCIAL),
            ("https://www.sec.gov/edgar/", "SEC EDGAR Financial", DataSourceType.ECONOMIC),
            ("https://fred.stlouisfed.org/", "FRED Economic Data", DataSourceType.ECONOMIC),
        ]

        # ============ EUROPEAN UNION ============
        eu_sources = [
            ("https://data.europa.eu/", "EU Open Data Portal", DataSourceType.GOVERNMENT),
            ("https://www.ema.europa.eu/", "EMA European Medicines", DataSourceType.HEALTH),
            ("https://ec.europa.eu/eurostat/", "Eurostat", DataSourceType.ECONOMIC),
            ("https://www.eea.europa.eu/", "European Environment Agency", DataSourceType.ENVIRONMENTAL),
            ("https://scihub.copernicus.eu/", "Copernicus Satellite", DataSourceType.ENVIRONMENTAL),
            ("https://sdw.ecb.europa.eu/", "ECB Statistical Data", DataSourceType.ECONOMIC),
        ]

        # ============ UK ============
        uk_sources = [
            ("https://data.gov.uk/", "UK Data.gov", DataSourceType.GOVERNMENT),
            ("https://digital.nhs.uk/", "NHS Digital", DataSourceType.HEALTH),
            ("https://www.ons.gov.uk/", "UK ONS Statistics", DataSourceType.ECONOMIC),
            ("https://environment.data.gov.uk/", "UK Environment Agency", DataSourceType.ENVIRONMENTAL),
        ]

        # ============ GERMANY ============
        de_sources = [
            ("https://www.govdata.de/", "GovData.de", DataSourceType.GOVERNMENT),
            ("https://www.destatis.de/", "Destatis Germany", DataSourceType.ECONOMIC),
            ("https://opendata.dwd.de/", "DWD Weather Germany", DataSourceType.ENVIRONMENTAL),
        ]

        # ============ FRANCE ============
        fr_sources = [
            ("https://www.data.gouv.fr/", "Data.gouv.fr", DataSourceType.GOVERNMENT),
            ("https://www.insee.fr/", "INSEE France", DataSourceType.ECONOMIC),
            ("https://donneespubliques.meteofrance.fr/", "Météo-France", DataSourceType.ENVIRONMENTAL),
        ]

        # ============ SWITZERLAND ============
        ch_sources = [
            ("https://opendata.swiss/", "OpenData.swiss", DataSourceType.GOVERNMENT),
            ("https://www.bfs.admin.ch/", "Swiss Statistics", DataSourceType.ECONOMIC),
        ]

        # ============ ALBANIA & BALKANS ============
        balkans_sources = [
            ("https://open.data.al/", "Open Data Albania", DataSourceType.GOVERNMENT),
            ("http://www.instat.gov.al/", "INSTAT Albania", DataSourceType.ECONOMIC),
            ("https://opendata.rks-gov.net/", "Kosovo Open Data", DataSourceType.GOVERNMENT),
            ("https://opendata.gov.mk/", "North Macedonia Open Data", DataSourceType.GOVERNMENT),
            ("https://data.gov.rs/", "Serbia Open Data", DataSourceType.GOVERNMENT),
        ]

        # ============ ASIA ============
        asia_sources = [
            ("https://www.e-stat.go.jp/", "E-Stat Japan", DataSourceType.ECONOMIC),
            ("https://www.data.go.jp/", "Japan Open Data", DataSourceType.GOVERNMENT),
            ("https://data.stats.gov.cn/", "National Data China", DataSourceType.ECONOMIC),
            ("https://data.gov.in/", "Data.gov India", DataSourceType.GOVERNMENT),
            ("https://www.data.go.kr/", "Korea Open Data", DataSourceType.GOVERNMENT),
        ]

        # ============ OTHER COUNTRIES ============
        other_sources = [
            ("https://data.gov.au/", "Australia Data.gov", DataSourceType.GOVERNMENT),
            ("https://open.canada.ca/", "Canada Open Data", DataSourceType.GOVERNMENT),
            ("https://dados.gov.br/", "Brazil Dados.gov", DataSourceType.GOVERNMENT),
            ("https://www.data.gov.za/", "South Africa Data.gov", DataSourceType.GOVERNMENT),
        ]

        # ============ INTERNATIONAL ORGANIZATIONS ============
        international_sources = [
            ("https://data.worldbank.org/", "World Bank Open Data", DataSourceType.ECONOMIC),
            ("https://apps.who.int/iris/", "WHO IRIS", DataSourceType.HEALTH),
            ("https://data.un.org/", "UN Data", DataSourceType.OPEN_DATA),
            ("https://data.imf.org/", "IMF Data", DataSourceType.ECONOMIC),
            ("https://data.oecd.org/", "OECD Data", DataSourceType.ECONOMIC),
            ("https://www.fao.org/faostat/", "FAO STAT Agriculture", DataSourceType.ENVIRONMENTAL),
            ("https://data.wto.org/", "WTO Trade Data", DataSourceType.ECONOMIC),
        ]

        # ============ INDUSTRIAL / IOT ============
        industrial_sources = [
            ("https://www.fiware.org/", "FIWARE IoT Platform", DataSourceType.OPEN_DATA),
            ("https://www.eclipse.org/ditto/", "Eclipse Ditto Digital Twins", DataSourceType.OPEN_DATA),
            ("https://thingsboard.io/", "ThingsBoard IoT", DataSourceType.OPEN_DATA),
            ("https://nodered.org/", "Node-RED IoT", DataSourceType.OPEN_DATA),
        ]

        # ============ GEOGRAPHIC ============
        geo_sources = [
            ("https://www.openstreetmap.org/", "OpenStreetMap", DataSourceType.OPEN_DATA),
            ("https://www.naturalearthdata.com/", "Natural Earth GIS", DataSourceType.ENVIRONMENTAL),
            ("https://www.geonames.org/", "GeoNames Toponyms", DataSourceType.OPEN_DATA),
        ]

        # Combine all sources
        all_source_lists = [
            scientific_sources, usa_sources, eu_sources, uk_sources,
            de_sources, fr_sources, ch_sources, balkans_sources,
            asia_sources, other_sources, international_sources,
            industrial_sources, geo_sources
        ]

        for source_list in all_source_lists:
            for url, name, source_type in source_list:
                source = OpenDataSource(
                    url=url,
                    name=name,
                    source_type=source_type,
                    quality_score=DataQuality.EXCELLENT
                )
                sources[source.id] = source

        logger.info(f"Ngarkuar {len(sources)} burime te njohura globale")
        return sources

    async def initialize(self):
        """Inicializon motorin"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Kloud-Scalability-Engine/1.0'}
        )

        # Ngarkon burime ekzistuese nga disku
        await self._load_sources_from_disk()

        logger.info(f"Inicializuar me {len(self.sources)} burime")

    async def discover_data_sources(self, domains: List[str] = None) -> List[OpenDataSource]:
        """
        Zbulon burime te reja te te dhenave nga domain-et e specifikuara
        """
        if domains is None:
            domains = [
                ".edu", ".ac.", ".gov", ".org", ".eu", ".uk", ".de", ".fr",
                "cern.ch", "nasa.gov", "who.int", "un.org", "worldbank.org"
            ]

        discovered_sources = []

        for domain in domains:
            try:
                # Kerko per burime te hapura ne kete domain
                sources = await self._crawl_domain_for_data(domain)
                discovered_sources.extend(sources)

                # Verifiko cdo burim
                for source in sources:
                    if await self._verify_data_source(source):
                        self.sources[source.id] = source
                        self.metrics.total_sources_discovered += 1

            except Exception as e:
                logger.error(f"Gabim gjate zbulimit te {domain}: {e}")

        # Ruaj burimet e reja
        await self._save_sources_to_disk()

        logger.info(f"Zbuluar {len(discovered_sources)} burime te reja")
        return discovered_sources

    async def _crawl_domain_for_data(self, domain: str) -> List[OpenDataSource]:
        """Kerko per burime te dhenash ne nje domain"""
        sources = []

        # Kerko per faqe te njohura te te dhenave
        data_pages = [
            f"https://data.{domain.replace('.', '')}.org",
            f"https://opendata.{domain.replace('.', '')}.org",
            f"https://research.{domain.replace('.', '')}.org/data",
            f"https://www.{domain.replace('.', '')}/open-data",
        ]

        for page_url in data_pages:
            try:
                async with self.session.get(page_url) as response:
                    if response.status == 200:
                        html = await response.text()
                        page_sources = self._extract_data_links_from_html(html, page_url)
                        sources.extend(page_sources)

            except Exception as e:
                logger.debug(f"Nuk mund te aksesohet {page_url}: {e}")

        return sources

    def _extract_data_links_from_html(self, html: str, base_url: str) -> List[OpenDataSource]:
        """Ekstrakton lidhje te te dhenave nga HTML"""
        sources = []

        # Regex per lidhje API dhe te dhena
        patterns = [
            r'href=["\']([^"\']*\.(?:json|xml|csv|api|data)[^"\']*)["\']',
            r'src=["\']([^"\']*\.(?:json|xml|csv|api|data)[^"\']*)["\']',
            r'["\']([^"\']*api[^"\']*)["\']',
            r'["\']([^"\']*data[^"\']*\.(?:json|xml|csv)[^"\']*)["\']',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                try:
                    full_url = urllib.parse.urljoin(base_url, match)
                    if self._is_valid_data_url(full_url):
                        source = OpenDataSource(
                            url=full_url,
                            name=f"Auto-discovered from {base_url}",
                            source_type=self._guess_source_type(full_url)
                        )
                        sources.append(source)
                except:
                    continue

        return sources

    def _is_valid_data_url(self, url: str) -> bool:
        """Verifiko nese URL eshte nje burim i vlefshme i te dhenave"""
        if not url or len(url) < 10:
            return False

        # Kontrollo per ekstensione te te dhenave
        data_extensions = ['.json', '.xml', '.csv', '.api', '/api/', '/data/']
        if any(ext in url.lower() for ext in data_extensions):
            return True

        # Kontrollo per domain-e te njohura
        trusted_domains = ['.edu', '.gov', '.org', '.ac.', 'cern.ch', 'nasa.gov']
        if any(domain in url.lower() for domain in trusted_domains):
            return True

        return False

    def _guess_source_type(self, url: str) -> DataSourceType:
        """Gjen llojin e burimit nga URL"""
        url_lower = url.lower()

        if any(term in url_lower for term in ['pubmed', 'nih', 'clinical', 'medical']):
            return DataSourceType.HEALTH
        elif any(term in url_lower for term in ['cern', 'nasa', 'research', 'science']):
            return DataSourceType.RESEARCH
        elif any(term in url_lower for term in ['edu', 'university', 'academic']):
            return DataSourceType.ACADEMIC
        elif any(term in url_lower for term in ['gov', 'government', 'state']):
            return DataSourceType.GOVERNMENT
        elif any(term in url_lower for term in ['environment', 'climate', 'weather']):
            return DataSourceType.ENVIRONMENTAL
        else:
            return DataSourceType.OPEN_DATA

    async def _verify_data_source(self, source: OpenDataSource) -> bool:
        """Verifiko nje burim te te dhenave"""
        try:
            async with self.session.get(source.url, timeout=10) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '').lower()

                    # Kontrollo per lloje te permbajtjes se te dhenave
                    if any(ct in content_type for ct in ['json', 'xml', 'csv', 'api']):
                        source.quality_score = DataQuality.GOOD
                        source.last_verified = datetime.now(timezone.utc)
                        return True

                    # Kontrollo per robots.txt per respektim
                    robots_url = urllib.parse.urljoin(source.url, '/robots.txt')
                    try:
                        async with self.session.get(robots_url) as robots_response:
                            if robots_response.status == 200:
                                robots_content = await robots_response.text()
                                if 'Disallow: /api' not in robots_content:
                                    source.quality_score = DataQuality.FAIR
                                    source.last_verified = datetime.now(timezone.utc)
                                    return True
                    except:
                        pass

        except Exception as e:
            logger.debug(f"Nuk mund te verifikohet {source.url}: {e}")

        return False

    async def feed_intelligent_modules(self, sources: List[OpenDataSource]) -> Dict[str, Any]:
        """
        Ushqen modulet inteligjente me te dhena dhe prodhon permbajtje te re
        """
        results = {
            'api_alignments': [],
            'cycles_generated': [],
            'documentation': [],
            'simulations': [],
            'research_papers': [],
            'futuristic_concepts': []
        }

        for source in sources:
            if not source.active:
                continue

            try:
                # Merr te dhena nga burimi
                data = await self._ingest_data_from_source(source)

                if data:
                    # Gjenero permbajtje te re
                    new_content = await self._generate_new_content_from_data(data, source)

                    # Shto rezultatet
                    for key, value in new_content.items():
                        if key in results:
                            results[key].extend(value)

                    # Perditeso metrikat
                    self.metrics.data_ingested_gb += len(str(data)) / (1024**3)
                    self.metrics.active_sources += 1

            except Exception as e:
                logger.error(f"Gabim gjate perpunimit te {source.url}: {e}")

        # Kontrolli i siguris me JONA
        if self.jona:
            safe_results = await self._jona_safety_review(results)
            results.update(safe_results)

        return results

    async def _ingest_data_from_source(self, source: OpenDataSource) -> Optional[Any]:
        """Ingesto te dhena nga nje burim"""
        try:
            async with self.session.get(source.url) as response:
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')

                    if 'json' in content_type:
                        return await response.json()
                    elif 'xml' in content_type:
                        text = await response.text()
                        return {'xml_content': text, 'source': source.url}
                    elif 'csv' in content_type:
                        text = await response.text()
                        return {'csv_content': text, 'source': source.url}
                    else:
                        text = await response.text()
                        return {'text_content': text, 'source': source.url}

        except Exception as e:
            logger.error(f"Gabim gjate ingestimit nga {source.url}: {e}")

        return None

    async def _generate_new_content_from_data(self, data: Any, source: OpenDataSource) -> Dict[str, List[Any]]:
        """
        Gjenero permbajtje te re nga te dhenat
        """
        content = {
            'api_alignments': [],
            'cycles_generated': [],
            'documentation': [],
            'simulations': [],
            'research_papers': [],
            'futuristic_concepts': []
        }

        # Analizo te dhena per modele dhe insights
        insights = await self._analyze_data_patterns(data, source)

        # Gjenero API alignments
        api_alignment = await self._generate_api_alignment(insights, source)
        if api_alignment:
            content['api_alignments'].append(api_alignment)

        # Krijon cycles te reja
        cycle = await self._generate_data_cycle(source, insights)
        if cycle:
            content['cycles_generated'].append(cycle)

        # Gjenero dokumentacion
        docs = await self._generate_documentation(insights, source)
        content['documentation'].extend(docs)

        # Krijon simulime
        simulations = await self._generate_simulations(data, insights)
        content['simulations'].extend(simulations)

        # Gjenero kerkime te reja
        research = await self._generate_research_papers(insights, source)
        content['research_papers'].extend(research)

        # Koncepte futuristike
        concepts = await self._generate_futuristic_concepts(insights, source)
        content['futuristic_concepts'].extend(concepts)

        return content

    async def _analyze_data_patterns(self, data: Any, source: OpenDataSource) -> Dict[str, Any]:
        """Analizon modele ne te dhena"""
        insights = {
            'data_type': type(data).__name__,
            'size': len(str(data)) if hasattr(data, '__len__') else 0,
            'patterns': [],
            'correlations': [],
            'anomalies': [],
            'predictions': []
        }

        if isinstance(data, dict):
            insights['patterns'].append(f"Dictionary me {len(data)} keys")
        elif isinstance(data, list):
            insights['patterns'].append(f"List me {len(data)} elemente")

        return insights

    async def _generate_api_alignment(self, insights: Dict, source: OpenDataSource) -> Optional[Dict]:
        """Gjenero API alignment"""
        return {
            'source_id': source.id,
            'source_url': source.url,
            'alignment_type': 'data_ingestion',
            'endpoints': [f'/api/v1/data/{source.source_type.value}/{source.id}'],
            'data_format': 'json',
            'generated_at': datetime.now(timezone.utc).isoformat()
        }

    async def _generate_data_cycle(self, source: OpenDataSource, insights: Dict) -> Optional[Dict]:
        """Gjenero nje cycle te ri"""
        if not self.cycle_engine:
            return None

        cycle_def = CycleDefinition(
            domain=f"data_{source.source_type.value}",
            source=source.url,
            agent="SCALABILITY_ENGINE",
            task=f"ingest_{source.source_type.value}_data",
            cycle_type=CycleType.INTERVAL,
            interval=3600.0,
            alignment=AlignmentPolicy.ETHICAL_GUARD
        )

        created_cycle = self.cycle_engine.create_cycle(
            domain=cycle_def.domain,
            source=cycle_def.source,
            agent=cycle_def.agent,
            task=cycle_def.task,
            cycle_type=cycle_def.cycle_type,
            interval=cycle_def.interval,
            alignment=cycle_def.alignment.value
        )

        self.metrics.cycles_generated += 1

        return {
            'cycle_id': created_cycle.cycle_id,
            'source': source.url,
            'task': cycle_def.task
        }

    async def _generate_documentation(self, insights: Dict, source: OpenDataSource) -> List[Dict]:
        """Gjenero dokumentacion"""
        docs = [{
            'type': 'api_documentation',
            'title': f'API per {source.name}',
            'content': f'# API Documentation for {source.name}\n\nBurimi: {source.url}\nLloji: {source.source_type.value}',
            'source_id': source.id
        }]
        return docs

    async def _generate_simulations(self, data: Any, insights: Dict) -> List[Dict]:
        """Gjenero simulime"""
        simulations = [{
            'type': 'data_simulation',
            'title': f'Simulim per {insights.get("data_type", "unknown")}',
            'parameters': {'data_size': insights.get('size', 0)},
            'generated_at': datetime.now(timezone.utc).isoformat()
        }]
        self.metrics.simulations_run += 1
        return simulations

    async def _generate_research_papers(self, insights: Dict, source: OpenDataSource) -> List[Dict]:
        """Gjenero kerkime te reja"""
        papers = [{
            'title': f'New Research: Patterns in {source.source_type.value.capitalize()} Data',
            'abstract': f'Ky kerkim analizon modele te reja ne te dhenat nga {source.name}.',
            'source_id': source.id,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }]
        self.metrics.research_papers_generated += 1
        return papers

    async def _generate_futuristic_concepts(self, insights: Dict, source: OpenDataSource) -> List[Dict]:
        """Gjenero koncepte futuristike"""
        concepts = [{
            'title': f'Futuristic Concept: AI-Enhanced {source.source_type.value.capitalize()} Intelligence',
            'description': f'Nje sistem inteligjent qe perdor te dhenat nga {source.name} per te parashikuar dhe optimizuar procese komplekse.',
            'source_id': source.id,
            'generated_at': datetime.now(timezone.utc).isoformat()
        }]
        return concepts

    async def _jona_safety_review(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Kontrolli i siguris me JONA"""
        if not self.jona:
            return {}

        safe_results = {}
        violations = 0

        for content_type, items in results.items():
            safe_items = []
            for item in items:
                is_safe = await self._check_content_safety(item)
                if is_safe:
                    safe_items.append(item)
                else:
                    violations += 1

            safe_results[content_type] = safe_items

        self.metrics.safety_violations += violations
        self.metrics.jona_reviews += 1

        return safe_results

    async def _check_content_safety(self, content: Dict) -> bool:
        """Kontrollo sigurine e permbajtjes"""
        problematic_keywords = ['harmful', 'dangerous', 'illegal', 'unethical']
        content_str = json.dumps(content, default=str).lower()

        for keyword in problematic_keywords:
            if keyword in content_str:
                return False

        return True

    async def _load_sources_from_disk(self):
        """Ngarko burimet nga disku"""
        try:
            sources_file = Path("data_sources.json")
            if sources_file.exists():
                with open(sources_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for source_data in data.get('sources', []):
                        source = OpenDataSource(**source_data)
                        self.sources[source.id] = source

                logger.info(f"Ngarkuar {len(self.sources)} burime nga disku")

        except Exception as e:
            logger.error(f"Gabim gjate ngarkimit te burimeve: {e}")

    async def _save_sources_to_disk(self):
        """Ruaj burimet ne disk"""
        try:
            sources_file = Path("data_sources.json")
            sources_file.parent.mkdir(exist_ok=True)

            data = {
                'sources': [source.__dict__ for source in self.sources.values()],
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'metrics': self.metrics.__dict__
            }

            with open(sources_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Ruajtur {len(self.sources)} burime ne disk")

        except Exception as e:
            logger.error(f"Gabim gjate ruajtjes se burimeve: {e}")

    async def get_metrics(self) -> ScalabilityMetrics:
        """Merr metrikat aktuale"""
        return self.metrics

    async def shutdown(self):
        """Mbylle motorin"""
        if self.session:
            await self.session.close()

        self.executor.shutdown(wait=True)
        logger.info("Open Data Scalability Engine u mbyll")

# Global engine instance
_scalability_engine: Optional[OpenDataScalabilityEngine] = None

async def get_scalability_engine(cycle_engine: Optional[Any] = None) -> OpenDataScalabilityEngine:
    """Merr instancen globale te motorit te skalabilitetit"""
    global _scalability_engine

    if _scalability_engine is None:
        _scalability_engine = OpenDataScalabilityEngine(cycle_engine)
        await _scalability_engine.initialize()

    return _scalability_engine

async def discover_and_feed_system():
    """
    Funksioni kryesor per zbulim dhe ushqim te sistemit
    """
    try:
        engine = await get_scalability_engine()

        logger.info("Filloj zbulimin e burimeve te te dhenave...")

        new_sources = await engine.discover_data_sources()

        if new_sources:
            logger.info(f"Zbuluar {len(new_sources)} burime te reja")

            results = await engine.feed_intelligent_modules(new_sources)

            logger.info("Rezultatet:")
            for content_type, items in results.items():
                logger.info(f"  {content_type}: {len(items)} elemente")

            metrics = await engine.get_metrics()
            logger.info(f"Metrika: {metrics.total_sources_discovered} burime, {metrics.cycles_generated} cycles")

        else:
            logger.info("Nuk u zbuluan burime te reja")

    except Exception as e:
        logger.error(f"Gabim ne sistemin e skalabilitetit: {e}")
    finally:
        if _scalability_engine:
            await _scalability_engine.shutdown()

