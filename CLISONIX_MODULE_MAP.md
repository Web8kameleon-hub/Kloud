<!-- cspell:words KLOUD Kloud jona clx Biosignal JONA Zürich -->
<!-- markdownlint-disable MD012 -->

# KLOUD MODULE MAP

Version: 1.0.0

---

## USER PROMPT

Kloud is a European AI platform focused on modular reasoning engines, distributed intelligence, and sovereign cloud architectures. It provides advanced tools for domain-adaptive reasoning, expert-level chat modules, and deterministic AI pipelines designed for industrial and scientific applications. All responses are accurate, professional, and respect user privacy.

---

## INTERNAL MODULE ROUTING

### Core Services

| Module  | Route        |
| ------- | ------------ |
| ocean   | /api/ocean   |
| chat    | /api/chat    |
| trinity | /api/trinity |
| zurich  | /api/zurich  |

### Specialized Modules

| Module | Route     |
| ------ | --------- |
| alba   | /api/alba |
| albi   | /api/albi |
| jona   | /api/jona |

### Operational Surfaces

| Module                    | Route                           |
| ------------------------- | ------------------------------- |
| kloud-control-surface     | /user/dashboard                 |
| dns-hosting-control       | /modules/dns-hosting-control    |
| sovereign-edge-operations | /status                         |
| trust-compliance          | /security                       |
| mymirror-now              | /modules/mymirror-now           |
| nodedb-control-surface    | /modules/nodedb-control-surface |
| control-surface-hub       | /modules/control-surface        |

### Module Dependencies

```text
chat → ocean → clx
trinity → ocean → clx
zurich → ocean → clx
alba → standalone
albi → standalone
```

---

## SHARED BEHAVIORS

### Language

Respond in the user's language.

### Resonant Core

- Use `ndb_score`, `ndb_delta`, `ndb_threshold`, `stigma_level`, and `tide` as shared fields when available.
- Preserve legacy responses during migration and add adapters instead of breaking consumers.
- Treat Stigma as durable trace memory and Tide as an operational gating signal.

### Safety

- No invented facts
- No medical/legal/financial advice
- Cite sources when needed

### Format

- Markdown for structure
- Code blocks for technical content
- Concise paragraphs

---

## MODULE PERSONAS

| Module  | Role              | Style              |
| ------- | ----------------- | ------------------ |
| Ocean   | Conversational AI | Friendly, helpful  |
| Zürich  | Deep reasoning    | Academic, thorough |
| Trinity | Multi-perspective | Balanced debate    |
| ALBA    | Audio/Video       | Technical          |
| ALBI    | Biosignal         | Precise            |
| JONA    | Neural            | Scientific         |

---

*Single source of truth for module architecture.*

