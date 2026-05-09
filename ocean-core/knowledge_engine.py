"""
KNOWLEDGE ENGINE
================
Aggregates data from ALL sources and formulates intelligent responses

Features:
- Multi-source aggregation with weighting
- Context linking (connections between labs, agents, metrics)
- "Curiosity threads" - exploration pathways
- Response formulation (rational, professional, proud of accuracy)
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger("ocean_knowledge_engine")


@dataclass
class CuriosityThread:
    """A curiosity thread - exploration pathway"""
    topic: str
    initial_question: str
    related_topics: List[str]
    continue_suggestions: List[str]
    sources_used: List[str]


@dataclass
class KnowledgeResponse:
    """Structured response from knowledge engine"""
    query: str
    intent: str
    main_response: str
    key_findings: List[Dict[str, Any]]
    sources_cited: Dict[str, Any]  # internal sources only
    curiosity_threads: List[CuriosityThread]
    confidence_score: float  # 0.0 - 1.0
    processing_time_ms: float
    timestamp: str


class SourceAggregator:
    """Aggregates data from multiple sources"""
    
    def __init__(self, data_sources_manager, external_apis_manager=None):
        self.data_sources = data_sources_manager
        self.external_apis = None  # Disabled - internal sources only
    
    async def aggregate_by_intent(self, intent: str, required_sources: List[str], 
                                  entities: Dict[str, List[str]]) -> Dict[str, Any]:
        """Aggregate data based on intent and required sources"""
        
        logger.info(f"📊 Aggregating sources: {required_sources}")
        
        aggregated_data = {
            "timestamp": datetime.now().isoformat(),
            "intent": intent,
            "internal_data": {},
            "external_data": {}
        }
        
        # Parallel queries to internal sources
        internal_tasks = []
        internal_source_names = []
        
        if "location_labs" in required_sources:
            internal_tasks.append(self.data_sources.location_labs.get_all_labs_data())
            internal_source_names.append("location_labs")
        
        if "laboratories" in required_sources or "location_labs" in required_sources:
            try:
                internal_tasks.append(self.data_sources.get_all_laboratories())
                internal_source_names.append("laboratories")
            except:
                pass
        
        if "agent_telemetry" in required_sources:
            internal_tasks.append(self.data_sources.agent_telemetry.get_all_agents_data())
            internal_source_names.append("agent_telemetry")
        
        if "cycle_data" in required_sources:
            internal_tasks.append(self.data_sources.cycle_data.get_cycle_data())
            internal_source_names.append("cycle_data")
        
        if "system_metrics" in required_sources:
            # TODO: Add system metrics
            pass
        
        if "excel_data" in required_sources:
            internal_tasks.append(self.data_sources.excel_data.get_excel_data())
            internal_source_names.append("excel_data")
        
        # Execute internal queries in parallel
        if internal_tasks:
            internal_results = await asyncio.gather(*internal_tasks, return_exceptions=True)
            
            for source_name, result in zip(internal_source_names, internal_results):
                if isinstance(result, Exception):
                    logger.error(f"Error fetching {source_name}: {result}")
                    aggregated_data["internal_data"][source_name] = {"error": str(result)}
                else:
                    aggregated_data["internal_data"][source_name] = result
        
        # External sources - DISABLED (internal only)
        # All queries now use ONLY internal Kloud data sources
        aggregated_data["external_sources_to_query"] = []
        
        return aggregated_data


class ResponseFormulator:
    """Formulates intelligent responses"""
    
    @staticmethod
    def format_response(query: str, intent: str, aggregated_data: Dict[str, Any],
                       external_data: Dict[str, Any], source_weights: Dict[str, float]) -> KnowledgeResponse:
        """Formulate response from aggregated data"""
        
        logger.info("📝 Formulating response...")
        
        # Extract key findings from internal data
        key_findings = ResponseFormulator._extract_findings(
            query, intent, aggregated_data, source_weights
        )
        
        # Build main response text
        main_response = ResponseFormulator._build_main_response(
            query, intent, key_findings, aggregated_data, external_data
        )
        
        # Create curiosity threads
        curiosity_threads = ResponseFormulator._create_curiosity_threads(
            query, intent, key_findings
        )
        
        # Calculate confidence
        confidence = ResponseFormulator._calculate_confidence(
            key_findings, len(aggregated_data.get("internal_data", {}))
        )
        
        # Source attribution - INTERNAL ONLY
        sources_cited = {
            "internal": list(aggregated_data.get("internal_data", {}).keys()),
            "external": []  # Disabled - using only internal Kloud sources
        }
        
        return KnowledgeResponse(
            query=query,
            intent=intent,
            main_response=main_response,
            key_findings=key_findings,
            sources_cited=sources_cited,
            curiosity_threads=curiosity_threads,
            confidence_score=confidence,
            processing_time_ms=0,  # Will be set by caller
            timestamp=datetime.now().isoformat()
        )
    
    @staticmethod
    def _extract_findings(query: str, intent: str, aggregated_data: Dict[str, Any],
                         source_weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """Extract key findings from aggregated data"""
        
        findings = []
        internal_data = aggregated_data.get("internal_data", {})
        
        # 23 Specialized Laboratories findings
        if "laboratories" in internal_data:
            lab_data = internal_data["laboratories"]
            if isinstance(lab_data, dict) and "total_labs" in lab_data:
                findings.append({
                    "type": "laboratory",
                    "title": "Specialized Laboratory Network",
                    "value": f"{lab_data['total_labs']} specialized laboratories across 23 domains",
                    "description": "AI, Medical, IoT, Marine, Environmental, Agricultural, Underwater, Security, Energy, Academic, Architecture, Finance, Industrial, Chemistry, Biotech, Quantum, Neuroscience, Robotics, Data, Nanotechnology, Trade, Archeology, Heritage",
                    "source": "laboratory_network",
                    "weight": source_weights.get("laboratories", 0.8)
                })
        
        # Location Labs findings
        if "location_labs" in internal_data:
            labs_data = internal_data["location_labs"]
            if "total_labs" in labs_data:
                findings.append({
                    "type": "laboratory",
                    "title": "Geographic Laboratory Network",
                    "value": f"{labs_data['total_labs']} active laboratories",
                    "source": "location_labs",
                    "weight": source_weights.get("location_labs", 0.5)
                })
        
        # Agent Telemetry findings
        if "agent_telemetry" in internal_data:
            agent_data = internal_data["agent_telemetry"]
            if "agents" in agent_data:
                agents = agent_data["agents"]
                findings.append({
                    "type": "agents",
                    "title": "Agent Status",
                    "value": f"{len(agents)} agents operational",
                    "agents_detail": list(agents.keys()),
                    "source": "agent_telemetry",
                    "weight": source_weights.get("agent_telemetry", 0.5)
                })
        
        # Sort by weight (importance)
        findings.sort(key=lambda f: f.get("weight", 0), reverse=True)
        
        return findings
    
    @staticmethod
    def _build_main_response(query: str, intent: str, key_findings: List[Dict[str, Any]],
                            aggregated_data: Dict[str, Any], 
                            external_data: Dict[str, Any]) -> str:
        """Build main response text"""
        
        response_parts = []
        
        # Opening based on intent
        if intent == "laboratory":
            response_parts.append("🔬 Laboratory Analysis Report")
        elif intent == "agent":
            response_parts.append("🤖 Agent Intelligence Summary")
        elif intent == "technical":
            response_parts.append("⚙️ Technical Infrastructure Status")
        elif intent == "business":
            response_parts.append("📊 Business Intelligence Report")
        elif intent == "system":
            response_parts.append("🖥️ System Health Report")
        else:
            response_parts.append("📚 Knowledge Response")
        
        response_parts.append("")
        
        # Add key findings
        if key_findings:
            response_parts.append("Key Findings:")
            for i, finding in enumerate(key_findings[:5], 1):  # Top 5
                response_parts.append(f"{i}. {finding.get('title', 'Finding')}: {finding.get('value', 'N/A')}")
            response_parts.append("")
        
        # Add source attribution
        internal_sources = aggregated_data.get("internal_data", {}).keys()
        if internal_sources:
            response_parts.append(f"Sources: {', '.join(internal_sources)}")
        
        # Professional sign-off
        response_parts.append("")
        response_parts.append("💭 Continue exploring:")
        
        return "\n".join(response_parts)
    
    @staticmethod
    def _create_curiosity_threads(query: str, intent: str,
                                 key_findings: List[Dict[str, Any]]) -> List[CuriosityThread]:
        """Create curiosity threads for exploration"""
        
        threads = []
        
        # Based on intent, create exploration paths
        if intent == "laboratory":
            threads.append(CuriosityThread(
                topic="Laboratory Networks",
                initial_question=query,
                related_topics=["Geographic distribution", "Lab specialization", "Data quality"],
                continue_suggestions=[
                    "What domains are most active?",
                    "Which locations have highest quality data?",
                    "How are labs interconnected?"
                ],
                sources_used=["location_labs"]
            ))
        
        elif intent == "agent":
            threads.append(CuriosityThread(
                topic="Agent Intelligence",
                initial_question=query,
                related_topics=["Agent decisions", "Confidence scores", "Task execution"],
                continue_suggestions=[
                    "What are the top agent decisions?",
                    "Which agent has highest confidence?",
                    "What anomalies were detected?"
                ],
                sources_used=["agent_telemetry"]
            ))
        
        elif intent == "technical":
            threads.append(CuriosityThread(
                topic="Technical Infrastructure",
                initial_question=query,
                related_topics=["Performance", "Reliability", "Scalability"],
                continue_suggestions=[
                    "What are current latency metrics?",
                    "Are there any error spikes?",
                    "How's resource utilization?"
                ],
                sources_used=["system_metrics"]
            ))
        
        return threads
    
    @staticmethod
    def _calculate_confidence(key_findings: List[Dict[str, Any]], 
                             source_count: int) -> float:
        """Calculate confidence score for response"""
        
        # More sources + more findings = higher confidence
        base_confidence = min(0.5 + (source_count * 0.1), 0.95)
        finding_boost = min(len(key_findings) * 0.05, 0.3)
        
        confidence = min(base_confidence + finding_boost, 1.0)
        
        return round(confidence, 2)


class KnowledgeEngine:
    """Central knowledge engine - orchestrates everything"""
    
    def __init__(self, data_sources_manager, external_apis_manager):
        self.data_sources = data_sources_manager
        self.external_apis = external_apis_manager
        self.aggregator = SourceAggregator(data_sources_manager, external_apis_manager)
        self.formulator = ResponseFormulator()
        self.initialized = False
    
    async def initialize(self):
        """Initialize knowledge engine"""
        try:
            # Data sources are already initialized in __init__, just mark ready
            self.initialized = True
            logger.info("✅ Knowledge Engine initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Knowledge Engine initialization failed: {e}")
            return False
    
    async def answer_query(self, query: str, processed_query) -> KnowledgeResponse:
        """Generate answer for processed query"""
        
        import time
        start_time = time.time()
        
        logger.info(f"🧠 Generating answer for: {query}")
        
        # 1. Aggregate internal data
        aggregated_data = await self.aggregator.aggregate_by_intent(
            processed_query.intent.value,
            processed_query.required_sources,
            processed_query.entities
        )
        
        # 2. Query external sources if needed
        external_data = {}
        external_sources = [s for s in processed_query.required_sources 
                           if s in ["wikipedia", "arxiv", "pubmed", "github"]]
        
        if external_sources:
            # Search all external sources
            external_results = await self.external_apis.search_all(query, limit=3)
            external_data = external_results
        
        # 3. Formulate response
        response = self.formulator.format_response(
            query,
            processed_query.intent.value,
            aggregated_data,
            external_data,
            processed_query.source_weights
        )
        
        # 4. Calculate processing time
        end_time = time.time()
        response.processing_time_ms = round((end_time - start_time) * 1000, 2)
        
        logger.info(f"✅ Answer generated in {response.processing_time_ms}ms, confidence: {response.confidence_score}")
        
        return response


# Global singleton
_knowledge_engine: Optional[KnowledgeEngine] = None


async def get_knowledge_engine(data_sources_manager, external_apis_manager) -> KnowledgeEngine:
    """Get or create global knowledge engine"""
    global _knowledge_engine
    
    if _knowledge_engine is None:
        _knowledge_engine = KnowledgeEngine(data_sources_manager, external_apis_manager)
        await _knowledge_engine.initialize()
    
    return _knowledge_engine

