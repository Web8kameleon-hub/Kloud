# Architecture Wiring & Deep Analysis (Kloud)

> Qëllimi: të dokumentojë wiring-in real të projektit Kloud në mënyrë që shërbimet të jenë **funksionale** end-to-end dhe të minimizohet rreziku i “breakage” nga mospërputhje ports/env/startup.

---

## 1) Hartë e përgjithshme (End-to-End)

### 1.1 Rrjedha kryesore (dominant path)

**Frontend (apps/web) → Main API (apps/api) → Agents/Engines → Storage + Observability**

1. **Frontend** (Next.js) e komunikon **server-side API** përmes `API_INTERNAL_URL=http://kloud-api:8000`.
2. **Main API** (FastAPI, port `8000`) vepron si:
   - gateway (routing i kërkesave),
   - auth/billing/usage orchestration (varësisht endpoint-it),
   - proxy/thirrje drejt agjentëve/serviseve të brendshme.
3. **Agents/Engines** (p.sh. Alba `5555`, Albi `6680`, Jona `7777`, ASI/AGIEM, Orchestrator `9999`, etj.) kryejnë fazat e pipeline.
4. **Storage** (PostgreSQL/Redis/Neo4j/MinIO + shërbime kërkimi si Elasticsearch/Weaviate sipas stack-it të dokumentuar më sipër) mban të dhëna.
5. **Observability**: shërbimet ekspozojnë `health`/`metrics` që merren nga Prometheus/Grafana/VictoriaMetrics; logs/trace nga Loki/Tempo.

### 1.2 Rrjedha dytësore (Research/Cycle Engine)

**Cycle Engine + Telemetry Router + Research Data Ecosystem**

- Diagrami “CYCLE” tregon:
  - Interval trigger → Cycle Engine → Alba (collection) → Albi (analysis/doc generation) → Jona (ethical oversight) → dokument gjenerim → broadcast telemetry.
- Kjo rrjedhë është e pavarur nga pipeline EEG/audio dhe shërben për “research cycles” + document generation.

---

## 2) Kontratat e shërbimeve (Ports / Health / Metrics / Naming)

### 2.1 Konventat e përgjithshme në repo

- Çdo service në `docker-compose*.yml` ka:
  - **`healthcheck`** (zakonisht `GET /health` ose `curl` kundër portit të vet),
  - **`ports:`** për ekspozim (në host),
  - environment variables për routing të brendshëm (p.sh. `CLX_HOST`, `REDIS_URL`, `ALBA_URL`, `STIGMA_NODEDB_URL`).

### 2.2 Shërbimet kryesore (sipas `docker-compose.yml`)

#### Frontend

- **Service:** `web`
- **Port container:** `3000`
- **Port host:** `3001`
- **Konfigurim kritike:**
  - `API_INTERNAL_URL=http://kloud-api:8000`
  - `NEXT_PUBLIC_API_BASE=/api`
  - `STIGMA_NODEDB_URL=http://kloud-nodedb-control-plane:9090/api/v1/stigma/write`

#### Main API (gateway)

- **Service:** `api`
- **Port container/host:** `8000:8000`
- **Health:** `GET http://localhost:8000/health`
- **Konfigurime kritike:**
  - `DATABASE_URL=postgresql://kloud:kloud@postgres:5432/klouddb`
  - `REDIS_URL=redis://redis:6379/0`
  - ngarkohet `.env` për auth/billing/keys.

#### Alba / Albi / Jona

- **Alba** (`alba_api_server.py` / service `alba`)
  - `5555:5555`
  - health `GET /health`
  - `REDIS_URL` i njëjtë për caching/state.
- **Albi** (`albi_service_6680.py` / service `albi`)
  - `6680:6680`
  - health `GET /health`
- **Jona** (`jona_service_7777.py` / service `jona`)
  - `7777:7777`
  - health `GET /health`

#### Orchestrator / AI Global Node

- **Service `ai-global-9999`**
  - `9999:9999`
  - health `GET /health`

#### Storage/infra (minimum i domosdoshëm për funksion)

- **PostgreSQL**
  - `5432:5432`
  - health `pg_isready`
- **Redis**
  - `6379:6379`
  - health `redis-cli ping`
- **Neo4j**
  - `7474:7474` (HTTP), `7687:7687` (Bolt)
  - health `wget` kundër `:7474`
- **MinIO**
  - `9000:9000`, `9001:9001`
  - health `GET /minio/health/live`

#### LLM backend

- **CLX (Ollama)**
  - `11434:11434`
  - health `ollama list`
- **clx-i (router)**
  - `4444:4444`
  - health `GET /health`

#### Observability

- **Prometheus**: `9090:9090`
- **Grafana**: `3001:3000`
- **VictoriaMetrics**: `8428:8428`
- **Loki**: `3102:3100`
- **Tempo**: `3200:3200`

> Shënim: Dokumenti i arkitekturës (ARCHITECTURE_SUMMARY.md) thekson që eksportues të DB/Redis mund të ekzistojnë dhe që shërbimet ekspozojnë `/metrics` për Prometheus/VictoriaMetrics.

---

## 3) Wiring aktual (si vendosen lidhjet në praktikë)

### 3.1 Docker Compose: “Single Source of Wiring”

Në këtë repo, wiring-i final shfaqet në:

- `docker-compose.yml`
- `docker-compose.backend-4*.yml`, `docker-compose.compute*.yml`, `docker-compose.edge.yml`, etj.

Që projekti të jetë funksional, **endpoint naming dhe env var** duhet të përputhen me hostnames e Docker network (p.sh. `kloud-api`, `redis`, `postgres`, `kloud-clx`).

### 3.2 Kompozime të rëndësishme

#### A) Full stack (docker-compose.yml)

Përfshin:

- postgres, redis, neo4j, minio
- clx + clx-i
- api (8000), web (3001)
- alba/albi/jona + engines të tjera
- observability stack
- shumë microservices shtesë

**Arsyetim wiring:**

- API varet nga postgres+redis (me `depends_on` + `condition: service_healthy`).
- Agents varet nga redis dhe nga CLX (kur kërkon LLM).

#### B) Backend-only (docker-compose.backend-4*.yml)

Heq shumicën e frontend/extra; lë vetëm bazën që u duhet agjentëve dhe gateway.

#### C) Hybrid / Compute / Edge

- `compute` shton node-role logjikë (p.sh. `NODE_ROLE=compute`).
- `edge` ka ports/healthcheck për një set të ndryshëm nyjash.

---

## 4) Pikat e riskut që e prishin funksionalitetin (Top failure modes)

### 4.1 Mospërputhje Ports (container vs host)

Shpesh gabimi është se frontend/consumer përdor port host ndërsa service komunikon me port **container** në brendësi të rrjetit docker.

- Në Docker network, target është **emri i service** dhe **porti container**.
- P.sh. `http://kloud-api:8000` (jo `localhost:8000`).

### 4.2 Mospërputhje environment variables

Shembuj nga repo që duhen të jenë të sakta:

- `API_INTERNAL_URL` (web) → duhet të jetë `http://kloud-api:8000`.
- `DATABASE_URL`, `REDIS_URL` (api) → duhet të referojnë `postgres` dhe `redis` (emrat docker).
- `CLX_HOST`, `CLX_URL`, `OLLAMA_HOST` → duhet të referojnë `kloud-clx:11434`.
- `STIGMA_NODEDB_URL` → `http://kloud-nodedb-control-plane:9090/api/v1/stigma/write`

### 4.3 Startup order: depends_on vs reality

`depends_on: condition: service_healthy` ndihmon, por prapë ka race conditions kur:

- service shfaqet “healthy” para se të ketë ngarkuar resources (model/keys/DB migrations),
- healthcheck është “light” dhe nuk garanton readiness për endpoint specifike.

Prandaj: për shërbimet e rënda (API, agents me LLM), duhet **readiness gating** shtesë (p.sh. test call ndaj endpoint-it kryesor ose test query DB).

### 4.4 Endpoint mismatch (path differences)

Në search u panë disa `health`/`status` dhe `/metrics` emra. Risk tipik:

- disa service përdorin `GET /health`, të tjerë `/status`.
- gateway pret `/metrics` standard, por service nuk e ekspozon.

### 4.5 “Split-brain wiring” midis docker-compose file-ve

Ka disa compose variants (`backend-4`, `compute`, `edge`, `75-services`). Nëse env var i një service ndryshon mes variantëve, funksionaliteti prishet.

**Shembull praktik:**

- `albi` ka port container `6680` në një file dhe mapping ndryshe në variant tjetër; gjithashtu `healthcheck` mund të jetë për `/health` por API path mund të ndryshojë.

### 4.6 Security/runtime mismatch

- Ka `api_keys.json` që montohet si volume në disa service.
- Nëse file mungon/është i gabuar → endpointet dështojnë edhe pse service është “up”.

---

## 5) Architecture Stabilization: rules-of-boundaries + checklist

### 5.1 Rules of boundaries (mos e lejo të përzihet domeni)

1. **Gateway rule (Main API):**
   - Main API thërret agjentët vetëm për “use-cases” biznesi.
   - Nuk duhet të mbajë logjikë heavy LLM/EEG; atë e kanë agjentët.

2. **Agent purity rule:**
   - Alba: vetëm ingestion + frame generation.
   - Albi: vetëm analytics/pattern recognition.
   - Jona: vetëm orchestration/synthesis & oversight.
   - (ASI/AGIEM: vetëm sistem-level supervision.)

3. **Storage access rule:**
   - Çdo service shkruan/lexon vetëm në storage-t e tij “kontraktual”.
   - Përndryshe rritet coupling dhe prishjet bëhen të vështira.

4. **Observability rule:**
   - Të gjitha shërbimet ekspozojnë standard minimal:
     - `GET /health`
     - `GET /metrics`
     - (opsional) `GET /status` për detaje.

5. **Secret boundary rule:**
   - Secrets vetëm nga `.env` ose volume (p.sh. `api_keys.json`) — jo hardcoded.

### 5.2 Functional Stabilization checklist (minimum për “projekti të punojë”)

#### A) Docker/Infra sanity (para se të testosh logjikën)

- [ ] `docker compose up -d` për variantin e zgjedhur.
- [ ] `postgres` healthy (pg_isready success)
- [ ] `redis` healthy (ping success)
- [ ] `neo4j` healthy
- [ ] `minio` healthy

#### B) LLM routing sanity (CLX)

- [ ] `clx` healthy (ollama list ok)
- [ ] `clx-i` healthy (`GET /health` ok)

#### C) Agent readiness sanity

- [ ] `alba` healthy (`GET /health`)
- [ ] `albi` healthy (`GET /health`)
- [ ] `jona` healthy (`GET /health`)
- [ ] `ai-global-9999` healthy (`GET /health`)

#### D) Gateway/API sanity

- [ ] `api` healthy (`GET /health` ok)
- [ ] `api` mund të flasë me postgres+redis (test query / cache set-get).
- [ ] `api` mund të thërrasë një endpoint agent (p.sh. endpoint minimal route që komunikon me Alba/Albi/Jona).

#### E) Frontend wiring sanity

- [ ] `web` ngarkohet dhe bën request drejt `http://kloud-api:8000` (server-side) pa CORS issues.

#### F) Telemetry/observability sanity

- [ ] `prometheus` up
- [ ] çdo service i targetuar nga scrape i ekspozon `/metrics`.
- [ ] grafana dashboards shfaqin data.

---

## 6) Dokumentim i wiring kontratave (si t’i bëjmë explicit)

Rekomandohet që repo të ketë një dokument “Service Contract Registry” (të paktën në Markdown) me tabelë:

- service name
- port container
- endpoints:
  - health
  - status
  - metrics
- env variables required (lista minimale)

Ndërkohë, ky dokument përdor mapping-in nga `docker-compose.yml` + dokumentet ekzistuese:

- `ARCHITECTURE_SUMMARY.md`
- `CLISONIX_ARCHITECTURE_BASELINE_2025.md`
- `CYCLE_ARCHITECTURE_DIAGRAM.md`
- `CLISONIX_MODULE_MAP.md`

---

## 7) Çfarë duhet të shtohet për ta bërë 100% “functional” (gap analysis)

Nga që u panë në dokumente dhe wiring, pjesët që zakonisht mungojnë kur një projekt është “i madh”:

1. **Readiness gating rigoroz**
   - healthcheck ekziston, por “ready for real work” jo domosdoshmërisht.
2. **Standardizim i `/metrics`**
   - siguro që çdo service e ka.
3. **Uniform endpoint naming** (`/health` vs `/status`)
4. **Kontrata të qarta** për agent-to-agent calls (çfarë dërgon, çfarë pret).
5. **Smoke tests automatikë**
   - 10-20 kërkesa minimale për të verifikuar pipeline end-to-end.

---

## 8) Përfundim

Ky dokument ka nxjerrë një “wiring blueprint” mbi bazën e:

- dokumenteve ekzistuese të arkitekturës,
- `docker-compose.yml` dhe compose variants,
- analizës së endpoint/search për health/metrics dhe routes.

Pika kryesore për sukses operacional është: **konsistencë e ports/env naming + readiness gating + standard metrics endpoints**.

---

## Shtojcë: Komandat e kontrollit (shembull)

> (Shembuj të përgjithshëm; ekzekutimi varet nga stack-u që do të përdorësh)

- Start stack:
  - `docker compose -f docker-compose.yml up -d`
- Shiko status container-e:
  - `docker ps`
- Verifiko health endpoint:
  - (Nga host) `curl http://localhost:8000/health`
  - (Nga një container) `curl http://kloud-api:8000/health`

---

**Dokumenti është shkruar që të shërbejë si “wiring + stabilization playbook” dhe të reduktojë dështimet tipike që vijnë nga mospërputhja e konfigurimeve.**
