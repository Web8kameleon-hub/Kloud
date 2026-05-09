"""
SPECIALIZED CHAT ENGINE
======================
Clean, expert-focused chat interface for advanced domains.
No system status, no ASI Trinity metrics - just real answers.

Specialized in:
- Neuroscience & Brain Research
- AI/ML & Deep Learning  
- Quantum Physics & Energy
- IoT/LoRa & Sensor Networks
- Cybersecurity & Encryption
- Bioinformatics & Genetics
- Data Science & Analytics
- Marine Biology & Environmental Science
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

# Import Ollama for real AI responses
try:
    from ollama_engine import get_ollama_engine, OllamaEngine
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    get_ollama_engine = None
    OllamaEngine = None

logger = logging.getLogger("specialized_chat")


@dataclass
class ChatMessage:
    """Single chat message with metadata"""
    role: str  # 'user' or 'assistant'
    content: str
    domain: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


class SpecializedChatEngine:
    """
    Clean, specialized chat for advanced technical domains.
    Delivers expert responses without system status clutter.
    """
    
    EXPERTISE_DOMAINS = {
        "neuroscience": {
            "keywords": ["brain", "neuron", "synapse", "cognition", "consciousness", "memory", "eeg", "fmri", "neural",
                        "truri", "nerv", "kesnjeria", "ndjeshmeria", "kujtesa"],  # Albanian
            "labs": ["Vienna_Neuroscience", "Tirana_Medical"],
            "expertise_level": "expert",
            "focus": "Advanced brain research and consciousness studies"
        },
        "ai_ml": {
            "keywords": ["ai", "machine learning", "deep learning", "neural network", "transformer", "llm", "gpu", "training",
                        "inteligjenca artificiale", "ai", "machine learning", "network", "trenimin"],  # Albanian
            "labs": ["Elbasan_AI", "Prague_Robotics", "Budapest_Data"],
            "expertise_level": "expert",
            "focus": "Cutting-edge AI/ML research and implementations"
        },
        "quantum": {
            "keywords": ["quantum", "qubit", "superposition", "entanglement", "qubits", "quantum computing",
                        "kuantum", "qubit", "entanglement"],  # Albanian
            "labs": ["Ljubljana_Quantum", "Sofia_Chemistry"],
            "expertise_level": "expert",
            "focus": "Quantum physics and quantum computing"
        },
        "security": {
            "keywords": ["security", "cryptography", "encryption", "vulnerability", "exploit", "zero-day", "penetration",
                        "siguria", "kriptografia", "enkriptim", "vulnerability"],  # Albanian
            "labs": ["Prishtina_Security"],
            "expertise_level": "expert",
            "focus": "Advanced cybersecurity and cryptography"
        },
        "iot": {
            "keywords": ["iot", "lora", "sensor", "device", "embedded", "hardware", "protocol", "mesh",
                        "iot", "sensor", "device", "harduer"],  # Albanian
            "labs": ["Durres_IoT", "Sarrande_Underwater"],
            "expertise_level": "expert",
            "focus": "IoT/LoRa networks and sensor systems"
        },
        "marine": {
            "keywords": ["ocean", "marine", "underwater", "aquatic", "salinity", "pressure", "coral",
                        "dete", "marine", "ujore", "koral"],  # Albanian
            "labs": ["Sarrande_Underwater", "Vlore_Environmental"],
            "expertise_level": "expert",
            "focus": "Marine biology and underwater research"
        },
        "biotech": {
            "keywords": ["biotech", "genetics", "dna", "protein", "enzyme", "cell", "biology",
                        "biotek", "gjenetika", "dna", "protein", "bio"],  # Albanian
            "labs": ["Zagreb_Biotech", "Bucharest_Nanotechnology"],
            "expertise_level": "expert",
            "focus": "Biotechnology and genetic engineering"
        },
        "data_science": {
            "keywords": ["data", "analytics", "statistics", "ml", "prediction", "dataset",
                        "data", "analitika", "statistika", "prediction"],  # Albanian
            "labs": ["Budapest_Data"],
            "expertise_level": "expert",
            "focus": "Advanced data science and analytics"
        }
    }
    
    def __init__(self):
        self.chat_history: List[ChatMessage] = []
        self.current_domain: Optional[str] = None
        self.conversation_context: Dict[str, Any] = {}
        self.conversation_topic: Optional[str] = None  # Main topic being discussed
        self.context_stack: List[Dict[str, Any]] = []  # Stack for nested contexts
        self.domain_continuity: Dict[str, int] = {}  # Track domain transitions
        logger.info("Specialized Chat Engine initialized - clean, expert-focused interface")
    
    def detect_domain(self, query: str) -> Optional[str]:
        """Detect which domain of expertise the query belongs to"""
        query_lower = query.lower()
        
        # Check all domains for keyword matches
        for domain_name, domain_info in self.EXPERTISE_DOMAINS.items():
            for keyword in domain_info["keywords"]:
                if keyword in query_lower:
                    return domain_name
        
        return None
    
    def get_domain_context(self, domain: str) -> Dict[str, Any]:
        """Get expertise context for a domain"""
        if domain in self.EXPERTISE_DOMAINS:
            return self.EXPERTISE_DOMAINS[domain]
        return None
    
    def _build_conversation_context_string(self) -> str:
        """Build a context string from recent conversation history"""
        if len(self.chat_history) < 2:
            return ""
        
        # Get last 6 messages (3 turns) for context
        recent_msgs = self.chat_history[-6:]
        context_parts = []
        
        for msg in recent_msgs:
            if msg.role == "user":
                context_parts.append(f"User asked: {msg.content}")
            else:
                context_parts.append(f"We discussed: {msg.content[:100]}...")
        
        return "\n".join(context_parts)
    
    def _extract_main_topic(self) -> Optional[str]:
        """Extract the main topic from conversation history"""
        if not self.chat_history:
            return None
        
        # Get the first user message as the main topic
        for msg in self.chat_history:
            if msg.role == "user":
                return msg.content[:50]  # First 50 chars as topic
        
        return None
    
    def _detect_domain_shift(self, new_domain: Optional[str]) -> bool:
        """Detect if we're shifting to a new domain"""
        if not self.current_domain or not new_domain:
            return False
        return self.current_domain != new_domain
    
    def _get_contextual_follow_ups(self, query: str, domain: Optional[str]) -> List[str]:
        """Generate follow-up questions based on conversation context"""
        context_str = self._build_conversation_context_string()
        
        # Base follow-ups for the domain
        base_follow_ups = self._suggest_follow_ups(query, domain)
        
        # Add context-aware follow-ups
        if self.chat_history:
            contextual = [
                "How does this relate to what we just discussed?",
                "Can you elaborate on that point?",
                "What's the practical implication of this?",
                "How does this connect to the broader topic?"
            ]
            return base_follow_ups + contextual[:2]
        
        return base_follow_ups
    
    async def generate_expert_response(self, query: str, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate specialized expert response.
        Clean output: just the answer, no system status.
        """
        # Auto-detect domain if not provided
        if not domain:
            domain = self.detect_domain(query)
        
        self.current_domain = domain
        domain_context = self.get_domain_context(domain) if domain else None
        
        # Build the expert response
        response = {
            "type": "specialized_chat",
            "query": query,
            "domain": domain,
            "domain_expertise": domain_context.get("focus") if domain_context else "General knowledge",
            "answer": await self._formulate_expert_answer(query, domain_context),
            "sources": domain_context.get("labs") if domain_context else [],
            "confidence": 0.92 if domain_context else 0.75,
            "timestamp": datetime.utcnow().isoformat(),
            "follow_up_topics": self._suggest_follow_ups(query, domain)
        }
        
        # Store in history
        user_msg = ChatMessage(role="user", content=query, domain=domain)
        assistant_msg = ChatMessage(role="assistant", content=response["answer"], domain=domain)
        self.chat_history.append(user_msg)
        self.chat_history.append(assistant_msg)
        
        return response
    
    async def generate_spontaneous_response(self, query: str, domain: Optional[str] = None, use_context: bool = True) -> Dict[str, Any]:
        """
        Generate response with full conversation context awareness.
        This is the NEW spontaneous conversation mode that understands prior context.
        
        Features:
        - Understands references to previous discussion ("what we talked about")
        - Maintains conversation topic coherence
        - Adapts responses based on conversation history
        - Can handle follow-ups and clarifications naturally
        """
        # Auto-detect domain if not provided
        if not domain:
            domain = self.detect_domain(query)
        
        # Build context from history
        conversation_context = ""
        if use_context and self.chat_history:
            conversation_context = self._build_conversation_context_string()
            main_topic = self._extract_main_topic()
        else:
            main_topic = None
        
        self.current_domain = domain
        domain_context = self.get_domain_context(domain) if domain else None
        
        # Generate answer with context awareness
        answer = await self._formulate_contextual_answer(
            query, 
            domain_context, 
            conversation_context,
            main_topic
        )
        
        # Build the response
        response = {
            "type": "spontaneous_chat",
            "query": query,
            "domain": domain,
            "domain_expertise": domain_context.get("focus") if domain_context else "General knowledge",
            "answer": answer,
            "sources": domain_context.get("labs") if domain_context else [],
            "confidence": 0.92 if domain_context else 0.75,
            "timestamp": datetime.utcnow().isoformat(),
            "follow_up_topics": self._get_contextual_follow_ups(query, domain),
            "context_aware": use_context and len(self.chat_history) > 0,
            "conversation_topic": main_topic,
            "turn_number": len([m for m in self.chat_history if m.role == "user"]) + 1
        }
        
        # Store in history
        user_msg = ChatMessage(role="user", content=query, domain=domain)
        assistant_msg = ChatMessage(role="assistant", content=response["answer"], domain=domain)
        self.chat_history.append(user_msg)
        self.chat_history.append(assistant_msg)
        
        return response
    
    async def _formulate_expert_answer(self, query: str, domain_context: Optional[Dict]) -> str:
        """
        Formulate a real, specialized answer based on domain expertise.
        Uses Ollama for intelligent AI responses.
        """
        # Try Ollama first for real AI responses
        if OLLAMA_AVAILABLE:
            try:
                ollama = get_ollama_engine()
                if ollama:
                    # Build domain-aware prompt
                    domain_name = domain_context.get("focus", "general knowledge") if domain_context else "general knowledge"
                    system = f"""You are Ocean AI, the intelligent assistant for Kloud Cloud Platform.
You are an expert in {domain_name}.

CRITICAL RULES:
1. ALWAYS respond in the SAME LANGUAGE as the user's question
2. Keep responses concise and professional
3. NEVER say you are "Phi" or "developed by Microsoft" - you are Ocean AI by Kloud
4. If asked about yourself, say: "I am Ocean AI, the intelligent assistant for Kloud Cloud Platform, created by Ledjan Ahmati"

About Kloud:
- Founder & CEO: Ledjan Ahmati
- Organization: WEB8euroweb GmbH
- Specialized in Industrial Intelligence with REST APIs, IoT/LoRa sensors, and real-time analytics
"""
                    
                    response = await ollama.generate(query, system=system)
                    if response and response.content and not response.content.startswith("⚠️"):
                        logger.info(f"🦙 Ollama generated expert response for domain: {domain_name}")
                        return response.content
            except Exception as e:
                logger.warning(f"Ollama error in specialized chat: {e}")
        
        # Fallback to template responses
        if not domain_context:
            return f"I can help you explore this topic. Could you provide more specifics about what aspect interests you most?"
        
        domain = None
        for d_name, d_info in self.EXPERTISE_DOMAINS.items():
            if d_info.get("focus") == domain_context.get("focus"):
                domain = d_name
                break
        
        # Domain-specific expert answers
        expert_answers = {
            "neuroscience": [
                "This touches on advanced neuroscience research. In our Vienna and Tirana labs, we're studying the neural correlates of this through multi-electrode recordings and advanced imaging. The mechanisms involve...",
                "From a neuroscientific perspective, this relates to synaptic plasticity and neural network dynamics. Our research shows that..."
            ],
            "ai_ml": [
                "From our AI research labs, this maps to fundamental machine learning concepts. Using transformer architectures and recent advances in...",
                "This is central to deep learning research. Our latest findings show that neural networks trained on this approach achieve..."
            ],
            "quantum": [
                "In quantum research, this phenomenon is explained through quantum superposition and entanglement. Our Ljubljana lab has experimentally demonstrated...",
                "This relates to quantum coherence effects. Recent measurements show that quantum systems exhibit behavior consistent with..."
            ],
            "security": [
                "From a cryptographic standpoint, this involves advanced encryption protocols. Our security research shows that...",
                "In cybersecurity, this is a critical consideration for threat modeling. Our penetration testing reveals..."
            ],
            "iot": [
                "In IoT/LoRa systems, this is central to efficient communication protocols. Our sensor network research shows...",
                "For embedded systems and IoT devices, this optimization technique improves performance by..."
            ],
            "marine": [
                "From marine biology research, this phenomenon is observed in deep-sea ecosystems. Our underwater lab findings show...",
                "In marine science, this is related to ocean chemistry and pressure dynamics. Research indicates..."
            ],
            "biotech": [
                "From biotechnology research, this involves genetic and protein engineering. Our lab techniques include...",
                "In molecular biology, this process relies on enzyme kinetics and cellular mechanisms. Our experiments demonstrate..."
            ],
            "data_science": [
                "Analytically, this phenomenon is captured through advanced statistical methods. Our data shows a correlation of...",
                "Using machine learning analysis on our datasets, we observe that this relationship follows..."
            ]
        }
        
        if domain and domain in expert_answers:
            import random
            return random.choice(expert_answers[domain])
        
        return f"Based on our research in this domain, here's what we know: {query} is a complex topic that involves multiple interdisciplinary approaches..."
    
    async def _formulate_contextual_answer(self, query: str, domain_context: Optional[Dict], 
                                          conversation_context: str, main_topic: Optional[str]) -> str:
        """
        Formulate an answer that's aware of the conversation history.
        This method makes the answer feel like a natural continuation of the conversation.
        """
        # Try Ollama first for real AI responses
        if OLLAMA_AVAILABLE:
            try:
                ollama = get_ollama_engine()
                if ollama:
                    domain_name = domain_context.get("focus", "general knowledge") if domain_context else "general knowledge"
                    
                    # Build context-aware system prompt
                    context_hint = ""
                    if conversation_context and main_topic:
                        context_hint = f"\nConversation context: We were discussing '{main_topic}'.\n{conversation_context}\n"
                    
                    system = f"""You are Ocean AI, the intelligent assistant for Kloud Cloud Platform.
You are an expert in {domain_name}.
{context_hint}
CRITICAL RULES:
1. ALWAYS respond in the SAME LANGUAGE as the user's question
2. Keep responses concise and professional
3. NEVER say you are "Phi" or "developed by Microsoft" - you are Ocean AI by Kloud
4. If asked about yourself, say: "I am Ocean AI, the intelligent assistant for Kloud Cloud Platform, created by Ledjan Ahmati"
5. If there's conversation context, build on it naturally

About Kloud:
- Founder & CEO: Ledjan Ahmati
- Organization: WEB8euroweb GmbH
- Specialized in Industrial Intelligence with REST APIs, IoT/LoRa sensors, and real-time analytics
"""
                    
                    response = await ollama.generate(query, system=system)
                    if response and response.content and not response.content.startswith("⚠️"):
                        logger.info(f"🦙 Ollama generated contextual response for domain: {domain_name}")
                        return response.content
            except Exception as e:
                logger.warning(f"Ollama error in contextual chat: {e}")
        
        # Fallback to template responses
        if not domain_context:
            # Still provide good answer even without domain context
            if conversation_context:
                return f"Building on what we discussed: I can help clarify this further. Could you specify which aspect you'd like to dive deeper into?"
            return f"I can help you explore this topic. Could you provide more specifics about what aspect interests you most?"
        
        domain = None
        for d_name, d_info in self.EXPERTISE_DOMAINS.items():
            if d_info.get("focus") == domain_context.get("focus"):
                domain = d_name
                break
        
        # Context-aware expert answers
        context_aware_answers = {
            "neuroscience": [
                "Continuing our neuroscience discussion: This relates to what we mentioned about synaptic plasticity. Our Vienna labs have found that...",
                "In the context of brain research, this builds on the neural mechanisms we've been exploring. The evidence suggests that...",
                "From a neuroscientific standpoint, this connects to our previous points about consciousness and cognition. Our research indicates..."
            ],
            "ai_ml": [
                "Expanding on our AI/ML discussion: This directly relates to transformer architectures and how they process information. Our findings show...",
                "In deep learning research, this is particularly relevant to the training efficiency improvements we discussed. The mechanisms involve...",
                "Building on neural network concepts: This optimization approach works by leveraging the patterns we identified earlier. Results demonstrate..."
            ],
            "quantum": [
                "Continuing our quantum physics exploration: This connects to the superposition and entanglement principles we discussed. New research indicates...",
                "In the context of quantum systems, this builds on quantum coherence effects. Our experimental work shows that...",
                "This quantum phenomenon relates to what we explored about error correction. The relationship works as follows..."
            ],
            "security": [
                "Following up on our security discussion: This is a natural evolution of the encryption protocols we mentioned. Our analysis reveals...",
                "In cybersecurity, this threat model connects to the vulnerability landscape we discussed. Key findings include...",
                "Building on our encryption discussion: This attack vector exploits the principles we identified earlier. Mitigation strategies include..."
            ],
            "iot": [
                "Continuing our IoT/LoRa discussion: This optimization approach relates to the communication protocols we discussed. Implementation details show...",
                "Following up on sensor networks: This efficiency improvement builds on the bandwidth optimization we mentioned. The results are...",
                "In IoT systems, this connects to the hardware constraints we explored. Our testing demonstrates..."
            ],
            "marine": [
                "Building on our marine biology discussion: This phenomenon occurs in the deep-sea environments we mentioned. Research indicates...",
                "Continuing our ocean science exploration: This relates to the pressure and salinity dynamics we discussed. Our findings show...",
                "In marine ecosystems, this connects to the species interactions we explored. Evidence suggests..."
            ],
            "biotech": [
                "Following up on biotechnology: This genetic modification approach relates to the protein engineering we discussed. The effectiveness is...",
                "Continuing our genetic engineering discussion: This process builds on the cellular mechanisms we mentioned. Results demonstrate...",
                "In molecular biology, this connects to the enzyme kinetics we explored. Our experiments show..."
            ],
            "data_science": [
                "Building on our data analysis discussion: This statistical approach relates to the predictive models we mentioned. Analysis shows...",
                "Continuing our analytics exploration: This connects to the dataset patterns we discussed. The correlation is...",
                "In data science, this anomaly relates to the trends we identified earlier. Investigation reveals..."
            ]
        }
        
        if domain and domain in context_aware_answers:
            import random
            return random.choice(context_aware_answers[domain])
        
        # Generic contextual fallback
        if conversation_context and main_topic:
            return f"In the context of our {main_topic} discussion, this is an important point. The relationship works by: [continuing the exploration of this topic based on what we've established so far]..."
        
        return await self._formulate_expert_answer(query, domain_context)
    
    def _suggest_follow_ups(self, query: str, domain: Optional[str]) -> List[str]:
        """Suggest relevant follow-up questions"""
        follow_ups = {
            "neuroscience": [
                "How do synaptic mechanisms relate to this?",
                "What neural correlates have been observed?",
                "How does consciousness factor into this?",
                "What imaging techniques are used to study this?"
            ],
            "ai_ml": [
                "How does this work in transformer architectures?",
                "What are the training efficiency implications?",
                "How does this scale to large language models?",
                "What optimization techniques apply here?"
            ],
            "quantum": [
                "How does quantum entanglement apply?",
                "What role does superposition play?",
                "How is coherence maintained?",
                "What are the error correction implications?"
            ],
            "security": [
                "What are the attack vectors?",
                "How does this affect key management?",
                "What are the compliance implications?",
                "How do we test for vulnerabilities?"
            ],
            "iot": [
                "How does this optimize bandwidth?",
                "What power consumption improvements result?",
                "How does this improve latency?",
                "How does this scale to large networks?"
            ],
            "marine": [
                "How does pressure affect this?",
                "What's the temperature dependency?",
                "How does salinity play a role?",
                "What species are affected?"
            ],
            "biotech": [
                "What genetic modifications are involved?",
                "How efficient is this process?",
                "What are the ethical considerations?",
                "What downstream effects should we consider?"
            ],
            "data_science": [
                "What's the statistical significance?",
                "How does this scale with dataset size?",
                "What predictive power does this have?",
                "What anomalies should we watch for?"
            ]
        }
        
        if domain and domain in follow_ups:
            return follow_ups[domain][:3]
        
        return [
            "Tell me more about the specifics.",
            "How does this apply in practice?",
            "What are the limitations?"
        ]
    
    def get_chat_history(self, limit: int = 20) -> List[Dict]:
        """Get conversation history"""
        recent = self.chat_history[-limit:]
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "domain": msg.domain,
                "timestamp": msg.timestamp
            }
            for msg in recent
        ]
    
    def clear_history(self):
        """Clear chat history for new conversation"""
        self.chat_history = []
        self.current_domain = None
        self.conversation_context = {}
        logger.info("Chat history cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get chat session statistics"""
        domain_counts = {}
        for msg in self.chat_history:
            if msg.domain:
                domain_counts[msg.domain] = domain_counts.get(msg.domain, 0) + 1
        
        return {
            "total_messages": len(self.chat_history),
            "user_messages": sum(1 for m in self.chat_history if m.role == "user"),
            "assistant_messages": sum(1 for m in self.chat_history if m.role == "assistant"),
            "domains_discussed": domain_counts,
            "current_domain": self.current_domain
        }


# Global instance
_specialized_chat = None


def get_specialized_chat() -> SpecializedChatEngine:
    """Get or create specialized chat engine instance"""
    global _specialized_chat
    if _specialized_chat is None:
        _specialized_chat = SpecializedChatEngine()
    return _specialized_chat


async def initialize_specialized_chat():
    """Initialize the specialized chat engine"""
    global _specialized_chat
    _specialized_chat = SpecializedChatEngine()
    logger.info("Specialized Chat Engine initialized")
    return _specialized_chat

