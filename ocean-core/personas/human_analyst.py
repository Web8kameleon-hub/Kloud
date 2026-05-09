from typing import Dict, Any
import random


class HumanAnalyst:
    name = "Human Analyst"
    domain = "human"
    
    # Real knowledge base for general questions
    GREETINGS = {
        "hello": "👋 Hello! Welcome to Curiosity Ocean. I'm here to help you explore any topic. What would you like to learn about today?",
        "hi": "👋 Hi there! Great to see you. Feel free to ask me anything - from science to philosophy, technology to art.",
        "hey": "👋 Hey! Ready to dive into the ocean of knowledge? What's on your mind?",
        "pershendetje": "👋 Përshëndetje! Mirësevini në Oqeanin e Kuriozitetit. Si mund t'ju ndihmoj sot?",
        "tungjatjeta": "👋 Tungjatjeta! Jam këtu për t'ju ndihmuar të eksploroni çdo temë. Çfarë dëshironi të mësoni?",
        "miredita": "👋 Mirëdita! Si mund t'ju ndihmoj sot?",
        "cfare mund": "👋 Unë jam Curiosity Ocean - një sistem inteligjent që mund t'ju ndihmoj me:\n\n🧠 **Neuroshkencë** - Si funksionon truri\n🤖 **Inteligjencë Artificiale** - AI, machine learning\n🔬 **Shkencë** - Fizikë, kimi, biologji\n💡 **Filozofi** - Pyetje të thella\n📊 **Biznesi** - Strategji, KPI\n🔒 **Siguri** - Cybersecurity\n\nPyetni çfarëdo dhe do t'ju ndihmoj!",
    }
    
    # Self-description
    ABOUT_ME = """🌊 **Unë jam Curiosity Ocean** - Motori i Njohurive të Pafundme!

**Çfarë jam unë:**
Jam një sistem inteligjent i ndërtuar nga Kloud që kombinon 14 Persona Specialistësh për t'ju dhënë përgjigje të sakta dhe të detajuara.

**14 Personat e mia:**
1. 🧠 **Neuroscience Expert** - Truri dhe mendja
2. 🤖 **AI Specialist** - Inteligjencë artificiale
3. 📊 **Data Analyst** - Analiza e të dhënave
4. 🔧 **Systems Engineer** - Arkitektura e sistemeve
5. 🔒 **Security Expert** - Siguria kibernetike
6. 🏥 **Medical Advisor** - Këshilla mjekësore
7. 💪 **Wellness Coach** - Shëndet dhe mirëqenie
8. 🎨 **Creative Director** - Kreativitet dhe art
9. ⚡ **Performance Optimizer** - Optimizim performancash
10. 🔬 **Research Scientist** - Shkencë dhe hulumtim
11. 💼 **Business Strategist** - Strategji biznesi
12. ✍️ **Technical Writer** - Dokumentacion teknik
13. 🎯 **UX Specialist** - Eksperiencë përdoruesi
14. ⚖️ **Ethics Advisor** - Etikë dhe morale

**Burimet e mia:**
- 23 laboratorë të specializuar
- Të dhëna real-time nga sistemet Kloud
- Njohuri të gjera në shumë fusha

Pyetni çdo gjë - jam këtu për ju!"""
    
    KNOWLEDGE = {
        "consciousness": """🧠 **Consciousness** is one of the deepest mysteries in science and philosophy.

**What is it?**
Consciousness is the subjective experience of being aware - the "what it's like" to be you. It includes:
- **Awareness** of your surroundings, thoughts, and feelings
- **Self-awareness** - knowing that you exist
- **Qualia** - the subjective quality of experiences (like the redness of red)

**Scientific Perspectives:**
- **Neuroscience**: Consciousness emerges from complex neural activity, particularly in the cerebral cortex
- **Integrated Information Theory (IIT)**: Consciousness = integrated information (Phi)
- **Global Workspace Theory**: Consciousness is a "broadcast" system in the brain

**The Hard Problem:**
Why does physical brain activity give rise to subjective experience? This remains unsolved.

**Key Brain Areas:**
- Prefrontal cortex (self-awareness)
- Thalamus (sensory integration)
- Claustrum (potential consciousness hub)""",
        
        "ai": """🤖 **Artificial Intelligence (AI)** refers to computer systems designed to perform tasks that typically require human intelligence.

**Types of AI:**
- **Narrow AI**: Specialized for specific tasks (like ChatGPT, image recognition)
- **General AI (AGI)**: Human-level intelligence across all domains (not yet achieved)
- **Super AI (ASI)**: Surpasses human intelligence (theoretical)

**How Modern AI Works:**
- **Machine Learning**: Systems learn patterns from data
- **Deep Learning**: Neural networks with many layers
- **Transformers**: Architecture behind modern language models (attention mechanism)

**Current Capabilities:**
✅ Language understanding and generation
✅ Image and video analysis
✅ Code generation
✅ Scientific discovery assistance

**Limitations:**
❌ No true understanding (pattern matching)
❌ Hallucinations (confident false information)
❌ No common sense reasoning
❌ No consciousness or feelings""",

        "brain": """🧠 **The Human Brain** is the most complex object in the known universe.

**Key Facts:**
- ~86 billion neurons
- ~100 trillion synaptic connections
- Uses ~20% of body's energy (only 2% of body weight)
- Processes information at ~120 m/s

**Major Regions:**
- **Cerebral Cortex**: Higher thinking, language, consciousness
- **Hippocampus**: Memory formation
- **Amygdala**: Emotions, especially fear
- **Cerebellum**: Motor coordination
- **Brainstem**: Vital functions (breathing, heartbeat)

**Brain Waves:**
- **Delta (0.5-4 Hz)**: Deep sleep
- **Theta (4-8 Hz)**: Meditation, drowsiness
- **Alpha (8-12 Hz)**: Relaxed, calm
- **Beta (12-30 Hz)**: Active thinking
- **Gamma (30-100 Hz)**: Higher cognition

**Neuroplasticity:**
The brain can reorganize itself throughout life, forming new neural connections.""",

        "quantum": """⚛️ **Quantum Computing** is a revolutionary technology that uses quantum mechanics to process information.

**Key Concepts:**
- **Qubits**: Unlike classical bits (0 or 1), qubits can be both 0 AND 1 simultaneously (superposition)
- **Entanglement**: Qubits can be connected so measuring one instantly affects the other
- **Interference**: Quantum states can amplify correct answers and cancel wrong ones

**Why It Matters:**
- Solve problems impossible for classical computers
- Drug discovery and molecular simulation
- Cryptography (breaking and making secure codes)
- Optimization problems (logistics, finance)

**Current State (2026):**
- IBM, Google, IonQ leading development
- 1000+ qubit processors exist
- Still in "NISQ" era (Noisy Intermediate-Scale Quantum)
- Practical applications emerging in chemistry, finance

**Limitations:**
- Requires extreme cooling (-273°C)
- Highly error-prone
- Not faster for all problems""",

        "neural network": """🕸️ **Neural Networks** are computing systems inspired by the human brain.

**How They Work:**
1. **Input Layer**: Receives data (images, text, numbers)
2. **Hidden Layers**: Process and transform data
3. **Output Layer**: Produces result (classification, prediction)

**Key Concepts:**
- **Neurons**: Basic units that receive inputs, apply weights, and produce output
- **Weights**: Parameters that determine connection strength
- **Activation Functions**: Introduce non-linearity (ReLU, Sigmoid)
- **Backpropagation**: Algorithm to adjust weights based on errors

**Types of Neural Networks:**
- **CNN** (Convolutional): Images, video
- **RNN** (Recurrent): Sequences, time series
- **Transformers**: Language, attention-based
- **GAN** (Generative Adversarial): Create new content

**Training Process:**
1. Forward pass: Data flows through network
2. Calculate loss: Compare output to expected
3. Backpropagate: Calculate gradients
4. Update weights: Gradient descent""",

        "machine learning": """📊 **Machine Learning** is a subset of AI where systems learn from data.

**Types of Learning:**
1. **Supervised Learning**: Learn from labeled examples
   - Classification (spam/not spam)
   - Regression (predict prices)

2. **Unsupervised Learning**: Find patterns in unlabeled data
   - Clustering (group similar items)
   - Dimensionality reduction

3. **Reinforcement Learning**: Learn from rewards/penalties
   - Game playing (AlphaGo)
   - Robotics

**Common Algorithms:**
- Linear/Logistic Regression
- Decision Trees / Random Forests
- Support Vector Machines (SVM)
- K-Nearest Neighbors (KNN)
- Neural Networks / Deep Learning

**The ML Pipeline:**
1. Collect and clean data
2. Feature engineering
3. Split into train/test sets
4. Train model
5. Evaluate and tune
6. Deploy and monitor""",

        "kloud": """🌐 **Kloud** is an advanced technology ecosystem.

**Core Components:**
- **Curiosity Ocean**: Knowledge aggregation engine (that's me!)
- **ALBA**: Adaptive Learning & Behavioral Analysis
- **ALBI**: Advanced Learning & Biological Intelligence
- **ASI Trinity**: Superintelligent coordination system
- **Cycle Engine**: Production and process management

**23 Specialized Laboratories:**
Including AI, Medical, IoT, Marine, Environmental, Agricultural, Underwater, Security, Energy, Academic, Finance, Industrial, Quantum, Neuroscience, Robotics, and more.

**Key Features:**
- Real-time data processing
- 14 expert personas for specialized queries
- Internal data sources only (no external APIs)
- Multi-domain knowledge integration""",
    }

    def answer(self, q: str, data: Dict[str, Any]) -> str:
        q_lower = q.lower().strip()
        
        # Check for self-description questions
        if any(phrase in q_lower for phrase in [
            "about you", "who are you", "what are you", "yourself",
            "kush je", "cfare je", "per veten", "your self"
        ]):
            return self.ABOUT_ME
        
        # Check for capability questions
        if any(phrase in q_lower for phrase in [
            "what can you", "cfare mund", "si mund", "how can you", 
            "help me", "ndihmo", "me ndihm"
        ]):
            return self.GREETINGS.get("cfare mund", self._generate_helpful_response(q, data))
        
        # Check for greetings first
        for greeting, response in self.GREETINGS.items():
            if greeting in q_lower or q_lower == greeting:
                return response
        
        # Check for knowledge topics
        for topic, knowledge in self.KNOWLEDGE.items():
            if topic in q_lower:
                return knowledge
        
        # Check for question patterns
        if any(word in q_lower for word in ["what is", "çfarë është", "explain", "shpjego", "tell me about"]):
            return self._generate_exploratory_response(q, data)
        
        # Default helpful response
        return self._generate_helpful_response(q, data)
    
    def _generate_exploratory_response(self, q: str, data: Dict[str, Any]) -> str:
        """Generate an exploratory response for unknown topics."""
        labs_count = len(data.get("laboratories", {}).get("laboratories", []))
        
        return f"""🔍 **Exploring your question:** "{q}"

I'm analyzing this through multiple knowledge domains. Here's what I can tell you:

**Approach:**
1. Breaking down the concept into core components
2. Connecting to related fields of knowledge
3. Identifying practical applications

**Available Resources:**
- 🔬 {labs_count} specialized laboratories for deep analysis
- 🧠 14 expert personas across different domains
- 📊 Real-time data from internal systems

**To get more specific answers, try asking about:**
- Scientific concepts (physics, biology, chemistry)
- Technology (AI, programming, systems)
- Philosophy (consciousness, ethics, meaning)
- Practical skills (learning, creativity, problem-solving)

What aspect would you like to explore deeper?"""

    def _generate_helpful_response(self, q: str, data: Dict[str, Any]) -> str:
        """Generate a helpful response for general queries."""
        suggestions = [
            "What is consciousness?",
            "How does AI work?",
            "Explain brain waves",
            "What is quantum computing?",
            "How do neural networks learn?",
        ]
        
        return f"""🌊 **I received your message:** "{q}"

I'm your Human Analyst, here to make complex topics accessible and understandable.

**I can help you with:**
- 🧠 Neuroscience and brain function
- 🤖 Artificial Intelligence and technology
- 🔬 Scientific concepts and theories
- 💡 Philosophy and deep questions
- 📚 Learning and knowledge acquisition

**Try asking something like:**
{chr(10).join(f"• {s}" for s in random.sample(suggestions, 3))}

What would you like to explore?"""


