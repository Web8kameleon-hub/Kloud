# Protokollet dhe Metodologjia e L.A.G.T.E.R

## Korniza Operative për Zbatim Praktik

---

## Qëllimi i Dokumentit

Ky dokument përkthen:

- `LAGTER_LAB.md` (vizionin, misionin, strukturën)
- `LAGTER_LAWS.md` (Ligjin I, II, III)

në një **metodologji të zbatueshme**, të audituar dhe të riprodhueshme.

---

## Parimet Operative (Derivate nga Ligjet)

### **P1 — Dy Pole të Detyrueshme (nga Ligji I)**

Asnjë metrikë nuk analizohet e vetme. Çdo metrikë duhet të ketë kundër-metrikën e saj.

### **P2 — Zinxhir i Plotë (nga Ligji I)**

Çdo vendim kërkon të paktën një sinjal nga secila shtresë:

- Biologji
- Sjellje
- Ambient

### **P3 — Balancë Para Vendimit (nga Ligji II)**

Alert-et dhe rekomandimet jepen vetëm pas stabilizimit të tensionit në dritare kohore të përcaktuar.

### **P4 — Enigma si Sinjal (nga Ligji III)**

Anomalitë nuk etiketohen si zhurmë automatikisht; regjistrohen si "enigmë" dhe kalojnë protokoll dekodimi.

### **P5 — Auditueshmëri Totale**

Çdo output duhet të ketë gjurmë të plotë:

- burimi i të dhënës
- transformimi
- modeli
- versioni
- arsyetimi

---

## Arkitektura e Pipeline

### **Shtresa A — Marrja e të Dhënave (Ingestion)**

Burime tipike:

- sinjale biologjike indirekte (p.sh. indikatorë të sipërfaqes okulare)
- sjellje digitale (koha në ekran, pushimet, ritmi i ndërprerjeve)
- telemetri ambientale (lagështia, temperatura, ndriçimi, ventilimi)

Output: dataset i sinkronizuar kohor (`timestamp-aligned`).

### **Shtresa B — Normalizimi & Cilësia**

- pastrim i mungesave
- zbulim drift-i sensori
- standardizim njësish
- kontroll i kufijve fizikë

Output: dataset i validuar me `quality_score`.

### **Shtresa C — Ndërtimi i Poleve**

Për çdo fenomen krijohen dy pole:

- p.sh. `tear_stability` ↔ `evaporation_risk`
- `screen_exposure` ↔ `recovery_breaks`
- `humidity_support` ↔ `ambient_dryness`

Output: `dual_signal_vector` për çdo përdorues/interval.

### **Shtresa D — Llogaritja e Tensionit**

Llogaritet tensioni mes poleve me funksione të peshuara sipas kontekstit.

Output: `tension_index` në intervalin $[0,1]$.

### **Shtresa E — Balanca dhe Vektori**

Aplikohet dritare stabilizimi (p.sh. 24h / 72h):

- nëse tensioni është transient, jepet status "observe"
- nëse tensioni persiston, jepet status "act"

Output: `vector_direction`, `vector_intensity`, `action_state`.

### **Shtresa F — Regjistri i Enigmave**

Kur modeli nuk e shpjegon fenomenin me besueshmëri të mjaftueshme:

- krijohet objekt "enigme"
- lidhet me të dhëna, hipoteza, plan dekodimi

Output: hyrje në `Enigma Registry`.

### **Shtresa G — Raportimi i Audituar**

Gjenerohen raporte me:

- faktorë kontribues (biologji/sjellje/ambient)
- nivel tensioni
- rekomandim jo-mjekësor
- trail auditimi

Output: `lagter_report_vX`.

---

## Skema Minimale e të Dhënave (v1)

### **Entity: ObservationRecord**

- `record_id`
- `user_id` (pseudonimizuar)
- `timestamp`
- `bio_features` (dict)
- `behavior_features` (dict)
- `ambient_features` (dict)
- `quality_score` (0-1)

### **Entity: DualSignalFrame**

- `frame_id`
- `record_window_start`
- `record_window_end`
- `signals_positive` (dict)
- `signals_counter` (dict)
- `tension_index` (0-1)
- `balance_state` (`stable|unstable|transient`)

### **Entity: EnigmaCase**

- `enigma_id`
- `title`
- `trigger_condition`
- `known_facts`
- `unknowns`
- `hypothesis_list`
- `decode_plan`
- `status` (`open|testing|decoded|archived`)

### **Entity: AuditTrail**

- `audit_id`
- `model_version`
- `feature_version`
- `data_snapshot_hash`
- `decision_summary`
- `law_checks` (Ligji I/II/III pass-fail)

---

## Protokollet Kryesore

## Protokolli 1 — Data Capture Protocol (DCP)

### **Qëllimi**

Të sigurojë marrje të standardizuar të të dhënave nga 3 shtresat.

### **Hapat**

1. Defino sensorët dhe burimet log.
2. Defino frekuencën e sampling.
3. Sinkronizo kohën ndër-burimore.
4. Apliko kontroll cilësie fillestar.
5. Ruaj snapshot me version.

### **Kriter Pranimi**
>
- >= 95% plotësi e dritares kohore
- devijim kohor ndër-burimor <= 2s
- `quality_score >= 0.8`

---

## Protokolli 2 — Dual-Signal Construction Protocol (DSCP)

### **Qëllimi**

Të transformojë metrikat lineare në struktura me dy pole.

### **Hapat**

1. Përcakto çiftet pole/kundër-pole.
2. Normalizo secilin sinjal në shkallë të njëjtë.
3. Llogarit diferencën dhe raportin e balancës.
4. Gjenero `dual_signal_vector`.

### **Kriter Pranimi**

- Çdo metrikë ka kundër-metrikë të deklaruar
- Nuk lejohet output me sinjal unik pa çift

---

## Protokolli 3 — Tension Stabilization Protocol (TSP)

### **Qëllimi**

Të shmangë reagimet impulsive nga spike tranziente.

### **Hapat**

1. Llogarit `tension_index` për interval.
2. Apliko moving window dhe EMA.
3. Klasifiko si transient/persistent.
4. Lejo rekomandim vetëm për persistent tension.

### **Kriter Pranimi**

- False alert rate nën pragun e targetuar
- Çdo alert ka "stability evidence"

---

## Protokolli 4 — Enigma Handling Protocol (EHP)

### **Qëllimi**

Të formalizojë trajtimin e rasteve të pashpjeguara.

### **Hapat**

1. Trigger enigmën kur confidence < prag.
2. Hap `EnigmaCase` me fakte dhe boshllëqe.
3. Defino 2-3 hipoteza testuese.
4. Ekzekuto mini-eksperiment validimi.
5. Përditëso modelin ose arkivo enigmën.

### **Kriter Pranimi**

- Çdo enigmë ka status dhe plan dekodimi
- Çdo mbyllje enigme ka evidencë të ruajtur

---

## Protokolli 5 — Law Compliance Gate (LCG)

### **Qëllimi**

Të verifikojë përputhjen e çdo vendimi me 3 Ligjet.

### **Checklist i detyrueshëm**

- Ligji I: U përdorën dy pole + zinxhiri i plotë? (Po/Jo)
- Ligji II: U stabilizua tensioni para vendimit? (Po/Jo)
- Ligji III: U trajtua enigma si sinjal, jo zhurmë? (Po/Jo)

### **Rregulli**

Nëse një përgjigje është "Jo", vendimi nuk publikohet.

---

## KPI dhe Metrika të Faza 1

### **KPI Shkencorë**

- `early_signal_precision`
- `early_signal_recall`
- `time_to_risk_detection`
- `enigma_decode_rate`

### **KPI Operativë**

- `data_quality_compliance`
- `law_compliance_rate`
- `false_alert_rate`
- `report_turnaround_time`

### **KPI Produkti**

- `user_adherence_to_recommendations`
- `symptom_reduction_trend` (jo-klinike, vetëraportim)
- `engagement_with_dashboard`

---

## Dizajni i Eksperimentit 8-Javor (Operacional)

### **J1-J2: Setup & Baseline**

- konfigurim burimesh të dhënash
- baseline individual për përdorues
- aktivizim i LCG gate

### **J3-J4: Data Collection e Kontrolluar**

- mbledhje e dendur e sinjaleve
- monitorim cilësie ditor
- regjistrim enigmesh fillestare

### **J5-J6: Modeling & Calibration**

- kalibrim i peshave të tensionit
- validim i pragjeve transient/persistent
- testim i rekomandimeve jo-mjekësore

### **J7: Dashboard & Audit Reports**

- publikim paneli `Dry Eye Risk`
- audit trail për çdo output

### **J8: Review & Handoff**

- retrospektivë shkencore
- listë përmirësimesh v2
- pitch material për partnerë

---

## Governance dhe Etika

### **Kufiri i Qartë i Përdorimit**

L.A.G.T.E.R është platformë **analize dhe modelimi**, jo diagnozë klinike.

### **Deklarata Standarde në Çdo Raport**

"Ky raport ofron analizë jo-mjekësore mbi sinjale biologjike/sjellore/ambientale. Për shqetësime shëndetësore, konsultohuni me profesionist të shëndetit."

### **Privatësia**

- pseudonimizim i identitetit
- akses me role
- log i aksesit dhe ndryshimeve

---

## Deliverables të Detyrueshme për Çdo Sprint

1. Dataset snapshot me hash
2. Model card me versionim
3. Law Compliance Report
4. Enigma Registry delta
5. Risk dashboard export

---

## Konkluzion Operativ

L.A.G.T.E.R bëhet i zbatueshëm kur çdo vendim kalon këtë rrugë:

**Sinjal -> Kundër-sinjal -> Tension -> Balancë -> Enigmë (nëse duhet) -> Vendim i audituar**

Ky është mekanizmi që ruan:

- strukturën (Ligji I)
- ritmin (Ligji II)
- parashikimin (Ligji III)

---

_Dokumenti i krijuar: 27 Shkurt 2026_  
_L.A.G.T.E.R Protocols v1_  
_Pjesë e Kloud Cloud Platform_

