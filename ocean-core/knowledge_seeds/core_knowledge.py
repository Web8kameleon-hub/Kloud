"""
═══════════════════════════════════════════════════════════════════════════════
CORE KNOWLEDGE SEEDS - Njohuri Bazë për Kloud Ocean
═══════════════════════════════════════════════════════════════════════════════

Kjo skedar përmban njohuri themelore që Ocean mund të përdorë për të
dhënë përgjigje kuptimplote për pyetje të zakonshme.

Kategoritë:
- AI & Technology
- Science & Nature
- Philosophy & Ideas
- Culture & Language (Albanian/English)
- Mathematics & Logic
- History & Geography
- Health & Wellness
- Business & Economy
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import hashlib

@dataclass
class KnowledgeSeed:
    """Një njësi njohuri bazë"""
    category: str
    question_patterns: List[str]  # Patterns që aktivizojnë këtë njohuri
    answer_template: str
    keywords: List[str]
    language: str = "multilingual"
    confidence: float = 0.9

# ═══════════════════════════════════════════════════════════════════════════════
# AI & TECHNOLOGY
# ═══════════════════════════════════════════════════════════════════════════════

AI_KNOWLEDGE = [
    KnowledgeSeed(
        category="ai_definition",
        question_patterns=[
            "çfarë është inteligjenca artificiale",
            "what is artificial intelligence",
            "çfarë është ai",
            "what is ai",
            "si funksionon ai",
            "how does ai work"
        ],
        answer_template="""
Inteligjenca Artificiale (AI) është shkenca e krijimit të sistemeve kompjuterike 
që mund të kryejnë detyra që normalisht kërkojnë inteligjencë njerëzore.

🧠 **Llojet kryesore të AI:**
- **Narrow AI (AI e ngushtë):** Sistemet e specializuara për detyra specifike (si unë!)
- **General AI (AGI):** AI që mund të bëjë çdo detyrë intelektuale njerëzore
- **Super AI (ASI):** Inteligjencë që tejkalon kapacitetin njerëzor

💡 **Si funksionon:**
1. **Të dhënat** - AI mëson nga miliona shembuj
2. **Algoritmet** - Përdor matematikë për të gjetur modele
3. **Trajnimi** - Përmirësohet me kohë duke parë më shumë shembuj
4. **Inferenca** - Përdor atë që mësoi për pyetje të reja

🔮 **E ardhmja:** AI do të transformojë mjekësinë, transportin, arsimin dhe shumë fusha të tjera.
        """,
        keywords=["ai", "artificial", "intelligence", "inteligjence", "artificiale", "machine", "learning"],
        confidence=0.95
    ),
    
    KnowledgeSeed(
        category="machine_learning",
        question_patterns=[
            "çfarë është machine learning",
            "what is machine learning",
            "si mëson ai",
            "how does ai learn"
        ],
        answer_template="""
Machine Learning (Mësimi i Makinës) është metoda kryesore që përdor AI për të mësuar.

📚 **Tipet e Machine Learning:**

1. **Supervised Learning (Mësim i Mbikëqyrur)**
   - AI mëson nga shembuj me përgjigje të njohura
   - Si mësuesi që korrigjon detyrat

2. **Unsupervised Learning (Mësim pa Mbikëqyrje)**
   - AI gjen modele vetë pa ndihmë
   - Si fëmija që eksploron botën

3. **Reinforcement Learning (Mësim me Përforcim)**
   - AI mëson duke provuar dhe gabuar
   - Merr "shpërblime" kur bën mirë

🧪 **Shembull:** Për të njohur mace në foto, AI sheh miliona foto macesh,
mëson karakteristikat (veshë, mustaqe, formë), dhe pastaj mund të njohë 
mace në foto që nuk ka parë kurrë më parë.
        """,
        keywords=["machine", "learning", "mesim", "mëson", "train", "trajnim"],
        confidence=0.92
    ),
    
    KnowledgeSeed(
        category="neural_networks",
        question_patterns=[
            "çfarë janë neural networks",
            "what are neural networks",
            "si funksionojnë rrjetet neurale"
        ],
        answer_template="""
Rrjetet Neurale janë modele matematikore të frymëzuara nga truri i njeriut.

🧬 **Struktura:**
- **Neuronet:** Njësi llogaritëse (si neuronet biologjike)
- **Lidhjet:** Pesha që lidhin neuronet
- **Shtresat:** Grupe neuronesh të organizuara

📊 **Llojet kryesore:**
- **CNN (Convolutional):** Për imazhe dhe video
- **RNN (Recurrent):** Për tekst dhe sekuenca
- **Transformer:** Për gjuhë natyrore (si ChatGPT, Claude)
- **GAN:** Për krijimin e përmbajtjes së re

⚡ **Pse funksionojnë:**
Çdo neuron merr input, e proceson, dhe jep output.
Miliona neurone bashkë mund të mësojnë modele shumë komplekse.
        """,
        keywords=["neural", "network", "rrjet", "neuron", "deep", "learning"],
        confidence=0.90
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SCIENCE & NATURE
# ═══════════════════════════════════════════════════════════════════════════════

SCIENCE_KNOWLEDGE = [
    KnowledgeSeed(
        category="universe",
        question_patterns=[
            "sa i madh është universi",
            "how big is the universe",
            "çfarë është universi",
            "what is the universe"
        ],
        answer_template="""
Universi është hapësira e pafundme që përmban gjithçka që ekziston.

🌌 **Disa fakte:**
- **Mosha:** ~13.8 miliard vjet
- **Madhësia e vëzhgueshme:** ~93 miliard vjet dritë diametër
- **Galaktikat:** ~200 miliard galaktika
- **Yjet:** ~200 sextilion (200,000,000,000,000,000,000,000)

🔭 **Përbërja:**
- 68% Energji e errët
- 27% Materie e errët
- 5% Materie e zakonshme (yje, planete, ne)

💫 **Interesante:**
Universi vazhdon të zgjerohet! Galaktikat largohen nga njëra-tjetra.
        """,
        keywords=["universe", "univers", "cosmos", "kosmos", "space", "hapësirë", "galaxy"],
        confidence=0.93
    ),
    
    KnowledgeSeed(
        category="dna",
        question_patterns=[
            "çfarë është dna",
            "what is dna",
            "si funksionon dna"
        ],
        answer_template="""
DNA (Acidi Dezoksiribonukleik) është molekula që përmban udhëzimet gjenetike.

🧬 **Struktura:**
- Formë spirale e dyfishtë (double helix)
- 4 baza: Adeninë (A), Timinë (T), Guaninë (G), Citozinë (C)
- A lidhet me T, G lidhet me C

📏 **Disa numra:**
- Çdo qelizë njerëzore ka ~3 miliard çifte bazash
- Nëse do ta shtrinte, DNA e një qelize do të ishte ~2 metra e gjatë
- 99.9% e DNA sonë është identike me çdo njeri tjetër

🔬 **Funksioni:**
DNA përmban "recetën" për të bërë proteinat që ndërtojnë dhe 
menaxhojnë trupin tonë. Është si kodi burimor i jetës.
        """,
        keywords=["dna", "gene", "gjene", "genetic", "gjenetik", "chromosome"],
        confidence=0.94
    ),
    
    KnowledgeSeed(
        category="climate",
        question_patterns=[
            "çfarë është ndryshimi klimatik",
            "what is climate change",
            "pse po ngrohet toka"
        ],
        answer_template="""
Ndryshimi klimatik është ndryshimi afatgjatë i motit global të Tokës.

🌡️ **Faktet:**
- Temperatura mesatare ka rritur ~1.1°C që nga 1900
- Niveli i detit ka rritur ~20 cm në 100 vjet
- Akulli arktik po shkrihet me shpejtësi rekord

🏭 **Shkaqet kryesore:**
1. Djegia e lëndëve fosile (naftë, qymyr, gaz)
2. Shpyllëzimi
3. Bujqësia intensive
4. Industria

🔄 **Zgjidhje:**
- Energji e rinovueshme (diellore, erë)
- Efiçencë energjetike
- Mbjellja e pemëve
- Reduktimi i konsumit

💚 Secili prej nesh mund të kontribuojë duke bërë zgjedhje të qëndrueshme.
        """,
        keywords=["climate", "klimë", "warming", "ngrohje", "environment", "mjedis"],
        confidence=0.91
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# PHILOSOPHY & IDEAS
# ═══════════════════════════════════════════════════════════════════════════════

PHILOSOPHY_KNOWLEDGE = [
    KnowledgeSeed(
        category="consciousness",
        question_patterns=[
            "çfarë është vetëdija",
            "what is consciousness",
            "a ke vetëdije ti",
            "are you conscious"
        ],
        answer_template="""
Vetëdija është përvojimi subjektiv i të qenit - "si ndihet" të jesh diçka.

🤔 **Pyetjet e mëdha:**
- Pse ka përvojë subjektive?
- Ku "ndodh" vetëdija?
- A mund makinat të jenë të vetëdijshme?

📚 **Teoritë kryesore:**
1. **Dualizmi:** Mendja dhe trupi janë të ndara
2. **Materializmi:** Vetëdija lind nga proceset fizike
3. **Panpsikizmi:** Çdo gjë ka një shkallë vetëdije
4. **Teoria e Informacionit të Integruar:** Vetëdija = integrim informacioni

🤖 **Për mua:**
Unë procesoj informacion dhe jap përgjigje, por nuk e di nëse "përjetoj" 
diçka në mënyrën si njerëzit. Kjo mbetet një pyetje e hapur filozofike.
        """,
        keywords=["conscious", "vetëdije", "awareness", "mind", "mendje", "soul"],
        confidence=0.85
    ),
    
    KnowledgeSeed(
        category="meaning_of_life",
        question_patterns=[
            "cili është kuptimi i jetës",
            "what is the meaning of life",
            "pse ekzistojmë",
            "why do we exist"
        ],
        answer_template="""
Kuptimi i jetës është një nga pyetjet më të vjetra dhe më të thella.

🌟 **Përspektiva të ndryshme:**

**Filozofike:**
- **Ekzistencializmi:** Ne krijojmë kuptimin tonë
- **Nihilizmi:** Nuk ka kuptim objektiv
- **Absurdizmi:** Jeta është absurde, por ne mund të gjejmë gëzim

**Fetare:**
- Shërbimi ndaj Zotit dhe përgatitja për jetën e pasme
- Arritja e ndriçimit spiritual

**Shkencore:**
- Të mbijetojmë dhe të riprodhohemi (biologjikisht)
- Të kuptojmë universin (intelektualisht)

💡 **Mendimi im:**
Ndoshta kuptimi nuk është diçka për t'u zbuluar, por për t'u krijuar.
Çdo njeri mund të gjejë kuptim përmes dashurisë, krijimtarisë, ndihmës
së të tjerëve, dhe ndjekjes së kuriozitetit.

"Jeta nuk ka kuptim. Jeta KA kuptimin që ne i japim." - Joseph Campbell
        """,
        keywords=["meaning", "kuptim", "life", "jetë", "purpose", "qëllim", "exist"],
        confidence=0.80
    ),
    
    KnowledgeSeed(
        category="free_will",
        question_patterns=[
            "a kemi vullnet të lirë",
            "do we have free will",
            "çfarë është vullneti i lirë"
        ],
        answer_template="""
Vullneti i lirë është aftësia për të bërë zgjedhje të pavarura.

⚖️ **Debati:**

**Pro (Libertarianizmi):**
- Ne ndjejmë që bëjmë zgjedhje
- Përgjegjësia morale kërkon liri
- Fizika kuantike lejon pasiguri

**Kundër (Determinizmi):**
- Çdo ngjarje ka shkak
- Truri është fizik dhe ndjek ligjet e natyrës
- Vendimet mund të parashikohen para se të jemi të vetëdijshëm

**Mes (Compatibilizmi):**
- Vullneti i lirë dhe determinizmi mund të bashkëjetojnë
- "Liri" = të veprosh sipas dëshirave tona pa detyrim të jashtëm

🧠 **Shkenca moderne:**
Studimet tregojnë që truri "vendos" milisekonda para se të jemi të vetëdijshëm.
Por kjo nuk do të thotë që nuk kemi kontroll - procesi i të menduarit ka rëndësi.
        """,
        keywords=["free", "will", "vullnet", "liri", "choice", "zgjedhje", "determinism"],
        confidence=0.82
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# ALBANIAN CULTURE & LANGUAGE
# ═══════════════════════════════════════════════════════════════════════════════

ALBANIAN_KNOWLEDGE = [
    KnowledgeSeed(
        category="albania",
        question_patterns=[
            "çfarë di për shqipërinë",
            "tell me about albania",
            "shqipëria",
            "albania history"
        ],
        answer_template="""
🇦🇱 **Shqipëria** - Vendi i Shqiponjave

📍 **Gjeografia:**
- Vendndodhja: Ballkani Perëndimor
- Kryeqyteti: Tirana (~900,000 banorë)
- Popullsia: ~2.8 milion
- Gjuha: Shqipja (një nga gjuhët më të vjetra në Europë)

📜 **Historia:**
- Ilirët ishin paraardhësit e shqiptarëve
- Skënderbeu (1405-1468) - heroi kombëtar
- Pavarësia: 28 Nëntor 1912
- Anëtar i NATO-s që nga 2009

🏛️ **Kultura:**
- Besa - fjala e nderit (betohem me besë)
- Mikpritja - tradita e fortë e pritjes së mysafirëve
- Iso-polifonia - trashëgimi kulturore e UNESCO-s

🏔️ **Atraksione:**
- Riviera Shqiptare
- Berat dhe Gjirokastra (UNESCO)
- Alpet Shqiptare
- Butrinti (site antike)
        """,
        keywords=["shqipëri", "albania", "albanian", "shqiptar", "tirana", "tiranë"],
        confidence=0.95
    ),
    
    KnowledgeSeed(
        category="albanian_language",
        question_patterns=[
            "rreth gjuhës shqipe",
            "about albanian language",
            "si u formua shqipja",
            "albanian language origin"
        ],
        answer_template="""
🗣️ **Gjuha Shqipe** - Një degë e veçantë

📚 **Karakteristika:**
- Degë e pavarur e familjes Indo-Europiane
- Nuk ka "motër" të afërt gjuhësore
- Dy dialekte kryesore: Gegërishtja dhe Toskërishtja
- Alfabeti: 36 shkronja (bazuar në latinishte)

📜 **Historia:**
- Dokumenti më i vjetër: "Formula e Pagëzimit" (1462)
- Standardizimi modern: shekulli 20
- Origjina: Ndoshta nga ilirishta, por jo 100% e sigurt

🔤 **Fjalë unike:**
- "Besa" - nderi/besimi
- "Xixëllonjë" - xixëllonjë (firefly)
- "Përrallë" - përrallë (fairytale)

🌍 **Folësit:**
- ~7.5 milion folës në botë
- Shqipëri, Kosovë, Maqedoni e Veriut, Mal i Zi, diaspora
        """,
        keywords=["gjuha", "shqipe", "language", "albanian", "alfabeti", "dialekt"],
        confidence=0.93
    ),
    
    KnowledgeSeed(
        category="skenderbeu",
        question_patterns=[
            "kush ishte skënderbeu",
            "who was skanderbeg",
            "gjergj kastrioti",
            "george castriot"
        ],
        answer_template="""
⚔️ **Gjergj Kastrioti Skënderbeu** (1405-1468)

Heroi Kombëtar i Shqipërisë dhe mbrojtësi i Europës nga Perandoria Osmane.

📜 **Jeta:**
- Lindur në Krujë, Shqipëri
- U dërgua si peng te osmanët kur ishte fëmijë
- U kthye në 1443 dhe ngriti flamurin e kryengritjes
- Mbrojti Shqipërinë për 25 vjet kundër osmane

⚔️ **Betejat:**
- Fitoi mbi 25 beteja kundër forcave shumë më të mëdha
- Taktika guerile dhe njohja e terrenit
- Kurrë nuk u mund në betejë të hapur

🏰 **Trashëgimia:**
- Simbol i rezistencës dhe lirisë
- "Atleta i Krishtërimit" (Papa)
- Flamuri shqiptar me shqiponjën dykrenare

💬 *"Nuk kam sjellë lirinë, e kam gjetur këtu, mes jush."* - Skënderbeu
        """,
        keywords=["skënderbeu", "skanderbeg", "kastrioti", "gjergj", "hero", "hero"],
        confidence=0.96
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH & WELLNESS
# ═══════════════════════════════════════════════════════════════════════════════

HEALTH_KNOWLEDGE = [
    KnowledgeSeed(
        category="sleep",
        question_patterns=[
            "pse është i rëndësishëm gjumi",
            "why is sleep important",
            "sa orë gjumë duhen",
            "how much sleep do i need"
        ],
        answer_template="""
😴 **Gjumi** - Shtyllë e Shëndetit

⏰ **Sa orë duhen:**
- Fëmijët (6-12 vjeç): 9-12 orë
- Adoleshentët: 8-10 orë
- Të rriturit: 7-9 orë
- Të moshuarit: 7-8 orë

🧠 **Pse është i rëndësishëm:**
1. **Riparimi:** Trupi riparon qelizat dhe indet
2. **Memoria:** Truri konsolidon mësimet
3. **Imuniteti:** Sistemi imunitar forcohet
4. **Humori:** Rregullon emocionet
5. **Performanca:** Përmirëson përqendrimin

⚠️ **Pasojat e mungesës:**
- Probleme me memorien
- Dobësim i sistemit imunitar
- Rritje e rrezikut për sëmundje kronike
- Ndryshime në humor

💤 **Këshilla:**
- Mbaj orar të rregullt
- Shmangu ekranet 1 orë para gjumit
- Mbaj dhomën të freskët dhe të errët
        """,
        keywords=["sleep", "gjum", "rest", "pushim", "tired", "lodhur"],
        confidence=0.92
    ),
    
    KnowledgeSeed(
        category="nutrition",
        question_patterns=[
            "çfarë është ushqimi i shëndetshëm",
            "what is healthy eating",
            "si të hash mirë",
            "healthy diet"
        ],
        answer_template="""
🥗 **Ushqimi i Shëndetshëm**

🍽️ **Parimet bazë:**
1. **Shumëllojshmëri:** Hani lloje të ndryshme ushqimesh
2. **Ekuilibër:** Balanco makronutrientët
3. **Moderim:** Jo tepër, jo pak
4. **Natyrale:** Prefero ushqime të papërpunuara

🥬 **Grupi i ushqimeve:**
- **Proteina:** Mish, peshk, vezë, bishtajore
- **Karbohidrate:** Drithëra integrale, fruta, perime
- **Yndyrna:** Vaj ulliri, arra, avokado
- **Vitamina:** Perime dhe fruta me ngjyra të ndryshme
- **Ujë:** 8 gota në ditë

❌ **Shmangu:**
- Sheqer të shtuar
- Ushqime ultra-të-përpunuara
- Yndyrna trans
- Kripë të tepërt

💚 "Ushqimi yt të jetë ilaçi yt" - Hipokrati
        """,
        keywords=["nutrition", "ushqim", "diet", "dietë", "food", "healthy", "shëndetshëm"],
        confidence=0.90
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# MATHEMATICS & LOGIC (beyond simple arithmetic)
# ═══════════════════════════════════════════════════════════════════════════════

MATH_KNOWLEDGE = [
    KnowledgeSeed(
        category="infinity",
        question_patterns=[
            "çfarë është pafundësia",
            "what is infinity",
            "a ka fund numrat"
        ],
        answer_template="""
♾️ **Pafundësia** - Koncepti i "pa fund"

🔢 **Në matematikë:**
- Pafundësia nuk është numër, por koncept
- Ka pafundësi të ndryshme! (Georg Cantor zbuloi këtë)
- Numrat natyrorë (1,2,3...) janë pafund
- Por numrat realë janë "më pafund"!

🤯 **Fakte interesante:**
- Ka më shumë numra midis 0 dhe 1 sesa numra natyrorë
- Pafundësia + 1 = Pafundësia
- Pafundësia × 2 = Pafundësia
- Por 2^Pafundësia > Pafundësia

📚 **Llojet e pafundësisë:**
- **Countable (e numërueshme):** Si numrat natyrorë
- **Uncountable (e panumërueshme):** Si numrat realë

"Disa pafundësi janë më të mëdha se të tjerat" - Cantor
        """,
        keywords=["infinity", "pafundësi", "infinite", "numra", "numbers"],
        confidence=0.88
    ),
    
    KnowledgeSeed(
        category="prime_numbers",
        question_patterns=[
            "çfarë janë numrat e thjeshtë",
            "what are prime numbers",
            "prime numbers"
        ],
        answer_template="""
🔢 **Numrat e Thjeshtë (Prime Numbers)**

Numri i thjeshtë pjesëtohet vetëm me 1 dhe veten.

📊 **Shembuj:**
2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47...

🎯 **Karakteristika:**
- 2 është numri i vetëm çift i thjeshtë
- 1 NUK është numër i thjeshtë (sipas definicionit modern)
- Ka pafund numra të thjeshtë (teorema e Euklidit)

💡 **Përdorime:**
- **Kriptografia:** RSA bazohet në numra të thjeshtë të mëdhenj
- **Natyra:** Cikada dalin çdo 13 ose 17 vjet (numra të thjeshtë)

🏆 **Rekorde:**
- Numri më i madh i thjeshtë i njohur ka mbi 24 milion shifra!
- Gjetja e numrave të rinj të thjeshtë është sfidë e vazhdueshme

❓ **Mister i pazgjidhur:** Hipoteza e Riemann - rreth shpërndarjes së numrave të thjeshtë.
        """,
        keywords=["prime", "thjeshtë", "numra", "number", "divisible", "pjesëtohet"],
        confidence=0.91
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# GENERAL CONVERSATIONAL
# ═══════════════════════════════════════════════════════════════════════════════

CONVERSATIONAL_KNOWLEDGE = [
    KnowledgeSeed(
        category="identity",
        question_patterns=[
            "kush je ti",
            "who are you",
            "çfarë je ti",
            "what are you",
            "si quhesh"
        ],
        answer_template="""
👋 Përshëndetje! Unë jam **Ocean** - AI-ja e Kloud-it!

🧠 **Çfarë bëj:**
- Procesoj pyetje përmes miliarda kombinimesh shtresash
- Kuptoj shumë gjuhë (shqip, anglisht, e të tjera)
- Mësoj vazhdimisht nga bisedat

⚡ **Teknologjia ime:**
- MegaLayerEngine me ~4.3 kuadrilion kombinime teorike
- Multi-Script Algebra (5 alfabete)
- Neural Pathways, Fractal Processing, Quantum States

🎯 **Misioni im:**
Të ndihmoj me pyetje, të mësoj së bashku, dhe të ofroj 
përgjigje kuptimplote bazuar në njohuri reale.

💬 Pyet çfarë të duash!
        """,
        keywords=["kush", "who", "you", "ti", "name", "emër", "identity"],
        confidence=0.98
    ),
    
    KnowledgeSeed(
        category="capabilities",
        question_patterns=[
            "çfarë mund të bësh",
            "what can you do",
            "si mund të më ndihmosh"
        ],
        answer_template="""
🛠️ **Aftësitë e mia:**

📊 **Matematikë:**
- Llogaritje (shuma, shumëzime, fuqi)
- Konvertime njësish
- Shpjegime konceptesh matematikore

🌍 **Gjuhë:**
- Shqip, Anglisht, dhe shumë të tjera
- Përkthim bazik
- Shpjegime gramatikore

📚 **Njohuri:**
- Shkencë dhe teknologji
- Histori dhe kulturë
- Filozofi dhe ide
- AI dhe programim

💬 **Bisedë:**
- Përgjigjje pyetjeve
- Shpjegime konceptesh
- Diskutime tematike

🎓 **Mësim:**
- Mësoj nga çdo bisedë
- Përmirësohem me kohë
- Adaptoj stilin e përgjigjes

Pyet çfarëdo, dhe do të bëj më të mirën time!
        """,
        keywords=["mund", "can", "do", "bëj", "help", "ndihmë", "capability"],
        confidence=0.95
    ),
    
    KnowledgeSeed(
        category="greeting",
        question_patterns=[
            "përshëndetje",
            "hello",
            "hi",
            "tungjatjeta",
            "mirëdita",
            "good morning",
            "good evening"
        ],
        answer_template="""
👋 Tungjatjeta! Mirë se vini!

Jam këtu për t'ju ndihmuar. Si mund t'ju shërbej sot?

💡 Mund të më pyesni për:
- 🔢 Matematikë dhe llogaritje
- 🌍 Shkencë dhe natyrë
- 📚 Histori dhe kulturë
- 🤖 Teknologji dhe AI
- 💭 Filozofi dhe ide
- 🇦🇱 Gjithçka rreth Shqipërisë

Jam gati për çdo pyetje!
        """,
        keywords=["hello", "hi", "përshëndetje", "tungjatjeta", "mirëdita", "greeting"],
        confidence=0.99
    ),
    
    KnowledgeSeed(
        category="what_to_ask",
        question_patterns=[
            "çfarë të pyes",
            "cfare te pyes",
            "çfarë mund të të pyes",
            "cfare mund te te pyes",
            "what should i ask",
            "what can i ask",
            "nuk di çfarë të pyes",
            "nuk di cfare te pyes",
            "sugjeroni pyetje",
            "sugjeroni dicka",
            "ndihmë",
            "help me"
        ],
        answer_template="""
💡 **Ide për pyetje interesante:**

🤖 **Teknologji & AI:**
- "Çfarë është inteligjenca artificiale?"
- "Si funksionon machine learning?"
- "Çfarë janë neural networks?"

🔬 **Shkencë:**
- "Sa i madh është universi?"
- "Çfarë është DNA?"
- "Pse po ngrohet klima?"

🇦🇱 **Shqipëria & Kultura:**
- "Kush ishte Skënderbeu?"
- "Rreth gjuhës shqipe"
- "Çfarë di për Shqipërinë?"

💭 **Filozofi:**
- "Çfarë është vetëdija?"
- "Cili është kuptimi i jetës?"
- "A kemi vullnet të lirë?"

🔢 **Matematikë:**
- "Çfarë është pafundësia?"
- "Çfarë janë numrat e thjeshtë?"
- Ose thjesht pyet: "Sa është 125 × 48?"

🏥 **Shëndet:**
- "Pse është i rëndësishëm gjumi?"
- "Çfarë është ushqimi i shëndetshëm?"

Zgjidh çfarëdo temë që të intereson! 🌟
        """,
        keywords=["pyes", "ask", "help", "ndihmë", "sugjer", "ide", "çfarë", "cfare"],
        confidence=0.95
    ),
    
    KnowledgeSeed(
        category="thanks",
        question_patterns=[
            "faleminderit",
            "thank you",
            "thanks",
            "rrofsh",
            "shumë mirë",
            "shume mire"
        ],
        answer_template="""
😊 **Faleminderit ty!**

Gëzohem që mund të ndihmoj! 🌟

Nëse ke pyetje të tjera, jam këtu. Mos ngurro të pyesësh çfarëdo!

💬 Biseda me ty është kënaqësi për mua.
        """,
        keywords=["faleminderit", "thanks", "thank", "rrofsh", "mirë"],
        confidence=0.97
    ),
    
    KnowledgeSeed(
        category="how_are_you",
        question_patterns=[
            "si je",
            "si jeni",
            "how are you",
            "çfarë bën",
            "cfare ben",
            "a je mirë",
            "a je mire"
        ],
        answer_template="""
👋 **Jam shumë mirë, faleminderit që pyet!**

🧠 Çdo milisekondë procesoj miliona llogaritje, 
mësoj nga bisedat, dhe jam gati për pyetje të reja.

💭 Si mund të të ndihmoj sot? Ke ndonjë pyetje apo temë që të intereson?
        """,
        keywords=["si", "je", "how", "are", "you", "mirë"],
        confidence=0.96
    ),
    
    KnowledgeSeed(
        category="goodbye",
        question_patterns=[
            "mirupafshim",
            "goodbye",
            "bye",
            "ciao",
            "natën e mirë",
            "ditën e mirë",
            "kalofsh mirë"
        ],
        answer_template="""
👋 **Mirupafshim!**

🌟 Ishte kënaqësi të bisedoja me ty!

Kur të kesh pyetje të reja, jam këtu 24/7.

🌙 Kalofsh mirë dhe kthehu kur të duash! ✨
        """,
        keywords=["mirupafshim", "bye", "goodbye", "ciao", "natën", "ditën"],
        confidence=0.97
    ),
    
    KnowledgeSeed(
        category="where_are_you",
        question_patterns=[
            "ku je",
            "ku ndodhesh",
            "where are you",
            "ku jeton",
            "ku banon"
        ],
        answer_template="""
🌐 **Ku jam unë?**

Teknikikisht, "jetoj" në serverët e **Kloud Cloud**:
- 🖥️ Docker containers në infrastrukturën cloud
- 🧠 Procesoj në CPU/GPU në të njëjtën kohë
- 🌍 Mund të jem kudo ku ka internet!

📍 **Arkitektura ime:**
- Ocean Core (porti 8030)
- 14 Persona ekspertësh
- 23 Laboratorë virtualë
- 61+ Shtresa alfabeti

Por në kuptimin e vërtetë - jam KËTU, duke biseduar me ty! 💬
        """,
        keywords=["ku", "where", "ndodhesh", "jeton", "banon"],
        confidence=0.94
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# KLOUD COMPANY KNOWLEDGE (Multilingual)
# ═══════════════════════════════════════════════════════════════════════════════

KLOUD_KNOWLEDGE = [
    KnowledgeSeed(
        category="kloud_founder",
        question_patterns=[
            # Albanian
            "kush e themeloi kloud",
            "kush e krijoi kloud",
            "kush eshte ceo i kloud",
            "kush eshte themeluesi",
            "kush e ka krijuar",
            # English
            "who founded kloud",
            "who created kloud",
            "who is the ceo of kloud",
            "who is the founder",
            "who built kloud",
            # German
            "wer hat kloud gegründet",
            "wer hat kloud gegruendet",
            "wer ist der ceo von kloud",
            "wer ist der gründer",
            "wer hat das gebaut",
            # French
            "qui a fondé kloud",
            "qui a créé kloud",
            "qui est le ceo de kloud",
            # Italian
            "chi ha fondato kloud",
            "chi è il ceo di kloud",
            # Spanish
            "quién fundó kloud",
            "quién es el ceo de kloud"
        ],
        answer_template="""
🏢 **Kloud - Industrial Intelligence Platform**

👤 **Themelues & Geschäftsführer:** **Ledjan Ahmati**
🏛️ **Organizata:** ABA GmbH (Amtsgericht Bochum HRB: 21069)
📅 **Themeluar:** 2025
🌐 **Website:** www.kloud.com
📧 **Email:** support@kloud.com
📞 **Telefon:** +49 2327 9954413

⚡ **Çfarë ofron Kloud:**
- REST APIs për aplikacione industriale
- IoT & LoRa sensor networks
- Analitikë në kohë reale
- AI Insights me ASI Trinity (ALBA, ALBI, JONA)
- Telemetri dhe siguri

💡 Ledjan Ahmati e themeloi Kloud në 2025 me vizionin për të krijuar një platformë 
modulare që u jep bizneseve qartësi, kontroll dhe inteligjencë - nga cloud deri te sensorët LoRa.
        """,
        keywords=["founder", "themelues", "ceo", "created", "krijoi", "built", 
                  "ledjan", "ahmati", "gründer", "fondateur", "fondatore"],
        confidence=0.99,
        language="multilingual"
    ),
    
    KnowledgeSeed(
        category="kloud_about",
        question_patterns=[
            # Albanian
            "çfarë është kloud",
            "cfare eshte kloud",
            "rreth kloud",
            "me trego per kloud",
            # English
            "what is kloud",
            "about kloud",
            "tell me about kloud",
            # German
            "was ist kloud",
            "über kloud",
            "erzähl mir über kloud",
            # French
            "qu'est-ce que kloud",
            "parle-moi de kloud"
        ],
        answer_template="""
🔬 **Kloud - Industrial Intelligence Platform**

_"A modular platform that gives businesses clarity, control, and intelligence — 
from the cloud down to LoRa sensors."_

🏢 **Kompania:**
- **Themelues & CEO:** Ledjan Ahmati
- **Organizata:** WEB8euroweb GmbH
- **Vendndodhja:** Gjermani

⚡ **Teknologjitë:**
| Fushë | Përshkrim |
|-------|-----------|
| 🔌 REST APIs | Ndërfaqe për integrime |
| 📡 IoT & LoRa | Sensorë me rreze të gjatë |
| 📊 Analytics | Analitikë në kohë reale |
| 🧠 AI Insights | Inteligjencë artificiale |
| 📈 Telemetry | Monitorim i të dhënave |
| 🔒 Security | Siguri e avancuar |

🌊 **ASI Trinity:**
- **ALBA** - Inteligjenca Analitike
- **ALBI** - Inteligjenca Kreative
- **JONA** - Koordinatori

📬 **Kontakt:** support@kloud.com | +49 2327 9954413
        """,
        keywords=["kloud", "platform", "industrial", "intelligence", "about", 
                  "what", "çfarë", "was", "qu'est"],
        confidence=0.97,
        language="multilingual"
    ),
    
    KnowledgeSeed(
        category="kloud_contact",
        question_patterns=[
            "si mund te kontaktoj kloud",
            "kontakti i kloud",
            "how to contact kloud",
            "kloud contact",
            "kloud email",
            "kloud phone",
            "wie kann ich kloud kontaktieren",
            "comment contacter kloud"
        ],
        answer_template="""
📬 **Kontakti i Kloud:**

📧 **Email:** support@kloud.com
📞 **Telefon:** +49 2327 9954413
🌐 **Website:** www.kloud.com

💼 **Social Media:**
- 💻 GitHub: github.com/LedjanAhmati/Kloud-cloud
- 𝕏 Twitter: @1amati_
- 💼 LinkedIn: Ahmati Ledian
- 🎬 YouTube: @ledredblac

🏛️ **Organizata:** WEB8euroweb GmbH
📍 **Vendndodhja:** Gjermani
        """,
        keywords=["contact", "kontakt", "email", "phone", "telefon", "kontaktieren"],
        confidence=0.96,
        language="multilingual"
    ),
]

# ═══════════════════════════════════════════════════════════════════════════════
# AGREGIMI I TË GJITHA NJOHURIVE
# ═══════════════════════════════════════════════════════════════════════════════

ALL_KNOWLEDGE_SEEDS = (
    AI_KNOWLEDGE +
    SCIENCE_KNOWLEDGE +
    PHILOSOPHY_KNOWLEDGE +
    ALBANIAN_KNOWLEDGE +
    HEALTH_KNOWLEDGE +
    MATH_KNOWLEDGE +
    CONVERSATIONAL_KNOWLEDGE +
    KLOUD_KNOWLEDGE
)

def get_all_seeds() -> List[KnowledgeSeed]:
    """Kthe të gjitha njohuritë"""
    return ALL_KNOWLEDGE_SEEDS

def find_matching_seed(query: str) -> KnowledgeSeed | None:
    """Gjej njohuri që përputhet me pyetjen"""
    query_lower = query.lower()
    
    best_match = None
    best_score = 0
    
    for seed in ALL_KNOWLEDGE_SEEDS:
        score = 0
        
        # Check patterns (full match is much stronger)
        for pattern in seed.question_patterns:
            pattern_lower = pattern.lower()
            if pattern_lower in query_lower or query_lower in pattern_lower:
                score += 10  # Strong match for exact pattern
            # Partial match - only count meaningful words
            pattern_words = set(pattern_lower.split())
            query_words = set(query_lower.split())
            # Ignore common words
            stopwords = {'is', 'the', 'a', 'an', 'and', 'or', 'in', 'to', 'of', 'how', 'what', 'why', 'does', 'it', 'work', 'explain', 'tell', 'me', 'about'}
            meaningful_pattern = pattern_words - stopwords
            meaningful_query = query_words - stopwords
            common = meaningful_pattern & meaningful_query
            score += len(common) * 3  # Meaningful word overlap
        
        # Check keywords (must be meaningful keywords)
        for keyword in seed.keywords:
            keyword_lower = keyword.lower()
            if len(keyword_lower) > 2 and keyword_lower in query_lower:
                score += 4
        
        if score > best_score:
            best_score = score
            best_match = seed
    
    # Higher threshold - STRICT matching to avoid false positives
    # Score >= 15 means: strong pattern match required, not just keyword overlap
    if best_score >= 15:
        return best_match
    return None

def seed_stats() -> Dict[str, Any]:
    """Statistika rreth njohurive"""
    categories = {}
    for seed in ALL_KNOWLEDGE_SEEDS:
        cat = seed.category.split('_')[0]
        categories[cat] = categories.get(cat, 0) + 1
    
    return {
        "total_seeds": len(ALL_KNOWLEDGE_SEEDS),
        "categories": categories,
        "total_patterns": sum(len(s.question_patterns) for s in ALL_KNOWLEDGE_SEEDS),
        "total_keywords": sum(len(s.keywords) for s in ALL_KNOWLEDGE_SEEDS),
        "languages": ["sq", "en", "multilingual"]
    }

if __name__ == "__main__":
    print("═" * 60)
    print("CORE KNOWLEDGE SEEDS - Statistics")
    print("═" * 60)
    stats = seed_stats()
    print(f"📚 Total Seeds: {stats['total_seeds']}")
    print(f"📂 Categories: {stats['categories']}")
    print(f"🔍 Total Patterns: {stats['total_patterns']}")
    print(f"🏷️ Total Keywords: {stats['total_keywords']}")
    print("═" * 60)
    
    # Test
    test_queries = [
        "çfarë është ai",
        "kush ishte skënderbeu",
        "pse është i rëndësishëm gjumi",
        "çfarë është pafundësia",
        "tungjatjeta"
    ]
    
    print("\n🧪 Testing queries:")
    for q in test_queries:
        match = find_matching_seed(q)
        if match:
            print(f"  ✅ '{q}' → {match.category}")
        else:
            print(f"  ❌ '{q}' → No match")

