# -*- coding: utf-8 -*-
"""Create initial patterns for autolearning"""
import cbor2
from datetime import datetime, timezone

patterns = {
    'patterns': [
        {
            'pattern_id': 'svc_alba',
            'pattern_type': 'service',
            'keywords': ['alba', 'analytical', 'analysis', 'pattern'],
            'regex': r'.*(alba|analytical|analysis|pattern).*',
            'response_template': 'ALBA (port 5555) eshte Analytical Intelligence - per analiza dhe pattern recognition.',
            'times_matched': 0,
            'success_rate': 0.95,
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'pattern_id': 'svc_albi',
            'pattern_type': 'service',
            'keywords': ['albi', 'creative', 'creativity', 'content'],
            'regex': r'.*(albi|creative|creativity|content).*',
            'response_template': 'ALBI (port 6666) eshte Creative Intelligence - per gjenerim dhe ideation.',
            'times_matched': 0,
            'success_rate': 0.95,
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'pattern_id': 'svc_ocean',
            'pattern_type': 'service',
            'keywords': ['ocean', 'knowledge', 'curiosity', 'chat'],
            'regex': r'.*(ocean|knowledge|curiosity|chat).*',
            'response_template': 'Ocean Core (port 8030) eshte Knowledge Engine - truri qendror me 14 persona.',
            'times_matched': 0,
            'success_rate': 0.95,
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'pattern_id': 'svc_asi',
            'pattern_type': 'service',
            'keywords': ['asi', 'superintelligence', 'reasoning', 'strategy'],
            'regex': r'.*(asi|superintelligence|reasoning|strategy).*',
            'response_template': 'ASI (port 9094) eshte Artificial Super Intelligence - per reasoning avancuar.',
            'times_matched': 0,
            'success_rate': 0.95,
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'pattern_id': 'svc_jona',
            'pattern_type': 'service',
            'keywords': ['jona', 'coordinator', 'orchestrator'],
            'regex': r'.*(jona|coordinator|orchestrat).*',
            'response_template': 'JONA (port 7777) eshte Master Coordinator - orkestron te gjitha sherbimet.',
            'times_matched': 0,
            'success_rate': 0.95,
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'pattern_id': 'services_count',
            'pattern_type': 'info',
            'keywords': ['sa sherbime', 'how many services', 'microservices', 'count'],
            'regex': r'.*(sa sherbime|how many services|microservices|count).*',
            'response_template': 'Kloud ka 56 microservices: ALBA, ALBI, ASI, Ocean Core, JONA, dhe shume te tjere.',
            'times_matched': 0,
            'success_rate': 0.95,
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'pattern_id': 'founder',
            'pattern_type': 'company',
            'keywords': ['founder', 'themelues', 'ceo', 'ledjan'],
            'regex': r'.*(founder|themelues|ceo|ledjan).*',
            'response_template': 'Themeluesi dhe CEO i Kloud eshte Ledjan Ahmati.',
            'times_matched': 0,
            'success_rate': 1.0,
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'pattern_id': 'company',
            'pattern_type': 'company',
            'keywords': ['company', 'kompani', 'web8', 'euroweb', 'gmbh'],
            'regex': r'.*(company|kompani|web8|euroweb|gmbh).*',
            'response_template': 'Kloud eshte produkt i WEB8euroweb GmbH. Website: www.kloud.com',
            'times_matched': 0,
            'success_rate': 1.0,
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'pattern_id': 'neuro',
            'pattern_type': 'service',
            'keywords': ['neuro', 'brain', 'eeg', 'cognitive'],
            'regex': r'.*(neuro|brain|eeg|cognitive).*',
            'response_template': 'NeuroSonix (port 8006) ofron Industrial Neuroscience - EEG, brain analysis, cognitive optimization.',
            'times_matched': 0,
            'success_rate': 0.95,
            'created_at': datetime.now(timezone.utc).isoformat()
        },
        {
            'pattern_id': 'cycles',
            'pattern_type': 'service',
            'keywords': ['cycle', 'circadian', 'ultradian', 'rhythm'],
            'regex': r'.*(cycle|circadian|ultradian|rhythm).*',
            'response_template': 'Cycle Engine (port 8005) menaxhon ciklet biologjike - circadian, ultradian, alignment.',
            'times_matched': 0,
            'success_rate': 0.95,
            'created_at': datetime.now(timezone.utc).isoformat()
        }
    ],
    'updated_at': datetime.now(timezone.utc).isoformat(),
    'format': 'cbor2'
}

with open('learned_patterns.cbor', 'wb') as f:
    cbor2.dump(patterns, f)

print(f"Created learned_patterns.cbor with {len(patterns['patterns'])} initial patterns")

