# 🏆 Sistemi i Garantimit të Cilësisë për Dokumenta

## Rregulla e Artë ✨

> **ASNJË DOKUMENT NUK PUBLIKOHET PA 5 FAZAT E RISTUDIMIT DHE APROVIMIN FINAL**

---

## Mënyra e Funksionimit

### 1️⃣ Dorëzim Dokumenti (Submission)

Autori përgatit dokumentin:
```bash
# Dokumenti përgatitet lokalisht
git add docs/LAGTER_PROTOCOLS.md
git commit -m "docs: submit for review - LAGTER Protocols v1"
git push origin main
```

---

### 2️⃣ 5 Fazat e Ristudimit (5-Phase Review)

| # | Faza | Përgjegjes | Çfarë Kontrollohet |
|---|------|-----------|-------------------|
| 1️⃣ | **Teknik** | Arkitekt | Termat, diagramet, referencat |
| 2️⃣ | **Implementim** | DevOps | Kodi real, endpoints, port-at |
| 3️⃣ | **Akademik** | Eksperte | Logjika, të dhënat, metodologjia |
| 4️⃣ | **Editorial** | Editor | Ortografia, gramatika, stil |
| 5️⃣ | **Aprovim Final** | Ledjan | Sign-off përfundimtar |

---

### 3️⃣ Ristudim Lokal

Çdo reviewer përdor shabllon:
```bash
cp reviews/TEMPLATE_document_review.md reviews/LAGTER_PROTOCOLS_teknik_review.md
# Plotëson të gjithë kontroll-listat
# Logjinon përfundimet
```

---

### 4️⃣ Aprovim Final

Kur të 5 fazat janë ✅ APPROVED:
```bash
# Dokumenti i aprovuar
# Status: READY_FOR_PUBLISH
```

---

### 5️⃣ Publikim në Blog

Veç tani dokumenta mund të publikohet:
```bash
# VETËM me --status APPROVED
python publish_to_blog.py --doc docs/LAGTER_PROTOCOLS.md --status APPROVED

# OUTPUT: Merr në clisonix-blog repo
# → LinkedIn poster e pral automatikisht
```

---

## Komanda të Lejuara

### ❌ NUK LEJOHET (Bllokohet)
```bash
# Pa aprovim
python publish_to_blog.py --doc docs/LAGTER_PROTOCOLS.md
# [BLOCKED] PUBLIKIMI I BLLOKUAR
```

### ❌ NUK LEJOHET (Bllokohet)
```bash
# Me status DRAFT
python publish_to_blog.py --doc docs/LAGTER_PROTOCOLS.md --status DRAFT
# [BLOCKED] PUBLIKIMI I BLLOKUAR
```

### ✅ LEJOHET (Publikohet në LinkedIn)
```bash
# Me aprovim
python publish_to_blog.py --doc docs/LAGTER_PROTOCOLS.md --status APPROVED
# [OK] Dokumenta dërguar në blog
# → LinkedIn e pral automatikisht
```

### ✅ LEJOHET (Vetëm lokal)
```bash
# Me --no-push për testim
python publish_to_blog.py --doc docs/LAGTER_PROTOCOLS.md --status APPROVED --no-push
# [OK] Dokumenta përpiluar lokalisht
# [INFO] Pa dërgim në GitHub
```

---

## Statet e Dokumentit

### 📋 DRAFT (I pret ristudim)
```
Status: DRAFT
Reviewer: [në pret]
Approve: ❌ NO
Blog: ❌ NO
LinkedIn: ❌ NO
```

### 🔄 UNDER_REVIEW (Në ristudim)
```
Status: UNDER_REVIEW
Reviewers: [Faza 1/5 | Faza 2/5 | ...]
Approve: ❌ PENDING
Blog: ❌ NO
LinkedIn: ❌ NO
```

### ✅ APPROVED (Gati për publikim)
```
Status: APPROVED
All Reviews: ✅ YES
Approve: ✅ YES
Blog: ✅ READY
LinkedIn: ✅ AUTO
```

### 📤 PUBLISHED (Publikuar)
```
Status: PUBLISHED
Blog: ✅ ON GITHUB
LinkedIn: ✅ AUTO-POSTED
Date: [data]
URL: https://ledjanahmati.github.io/clisonix-blog/...
```

---

## Procesi Vizuel

```
┌─────────────────────────────────────────────────────────────┐
│ DOKUMENTI FILLESTAR (DRAFT)                                 │
│ docs/LAGTER_PROTOCOLS.md                                    │
└─────────────────┬───────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────────┐
│ FAZA 1: KONTROLL TEKNIK                                     │
│ ✅/❌ Termat, diagramet, referencat                          │
└─────────────────┬───────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────────┐
│ FAZA 2: ALIGNMENT IMPLEMENTIMI                              │
│ ✅/❌ Kodi real, endpoints, port-at                         │
└─────────────────┬───────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────────┐
│ FAZA 3: RISTUDIM AKADEMIK                                   │
│ ✅/❌ Logjika, të dhënat, metodologjia                      │
└─────────────────┬───────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────────┐
│ FAZA 4: EDITORIAL PASS                                      │
│ ✅/❌ Ortografia, gramatika, stil                           │
└─────────────────┬───────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────────┐
│ FAZA 5: APROVIM FINAL                                       │
│ ✅/❌ Sign-off përfundimtar nga Ledjan                      │
└─────────────────┬───────────────────────────────────────────┘
                  ↓ ✅ APPROVED
┌─────────────────────────────────────────────────────────────┐
│ PUBLIKIM NË BLOG                                            │
│ python publish_to_blog.py --status APPROVED                │
└─────────────────┬───────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────────┐
│ CLISONIX-BLOG REPO                                          │
│ posts/protokollet-dhe-metodologjia-e-lagter.md            │
└─────────────────┬───────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────────┐
│ LINKEDIN AUTO-POSTER                                        │
│ Poston automatikisht në LinkedIn                            │
└─────────────────────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────────┐
│ LINKEDIN PROFILE                                            │
│ Artikulli publikuar + share-at                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Rregullat (Non-Negotiable)

### 🚫 5 Rregulla Ari

1. **Nuk publikojmë DRAFT dokumenta** — Blokohet në kod
2. **Nuk publikojmë pa testim teknik** — Faza 2 detyruese
3. **Nuk publikojmë pa validation akademike** — Faza 3 detyruese
4. **Nuk publikojmë pa editorial pass** — Faza 4 detyruese
5. **Nuk publikojmë pa aprovim final** — Ledjan duhet të nënshkruajë

---

## Shembull: LAGTER_PROTOCOLS.md

### Status Aktual
```
🔴 DRAFT → UNDER_REVIEW (Faza 1/5)
```

### Hapi Tjetër
1. Reviewer Teknik: Lexon dhe teston
2. Plotëson: `reviews/LAGTER_PROTOCOLS_teknik_review.md`
3. Rezultat: ✅ APPROVED ose ❌ NEEDS_REVISION

### Kur Të 5 Fazat Janë ✅
```
python publish_to_blog.py --doc docs/LAGTER_PROTOCOLS.md --status APPROVED
```

---

## Për Reviewers

### Shënimet e Rëndësisë
1. **Mos aprovo nëse nuk je 100% sigur** — Mirë për të dërguar përpara për revision
2. **Dokumentoni çdo problem** — Specifike dhe të matshme
3. **Sugjeruesi zgjidh** — Autori bën revizionet, reviewer-i verifikoi
4. **Nuk e aprovon nëse nuk ka testuar** — Faza 2 duhet eksekutim kodi real

---

## Për Autorat

### Të Bërit Të Dytë
1. **Përgatisni dokumentin lokal** — Testesë ortografi, liens-ë
2. **Dorëzoni për ristudim** — Krijoni GitHub issue
3. **Përgjigju reviewers** — Bëni revizionet e kërkuara
4. **Zgjidh çdo problem** — Dokumenti duhet ta kalojë të 5 fazat
5. **Kërkoni sign-off** — Ledjan miratë përfundimisht
6. **Publikoni me aprovim** — Veç atëherë kalon në LinkedIn

---

## FAQ

**P: Çfarë nëse dokumenti ka gabim në LinkedIn pas publikimit?**
A: Revokojmë, bëjmë revision, kalojmë 5 fazat sërish, ripublikojmë.

**P: Çfarë nëse reviewer nuk pajtohet?**
A: Dokumenti nuk publikohet. Duhet përpunim ose qëndruar në DRAFT.

**P: Çfarë nëse publikoj pa aprovim?**
A: Bllokohet nga kod. Scripta refuzon `--status APPROVED`.

**P: Sa kohë zgjat 5 fazat?**
A: Zakonisht 3-5 ditë nëse jeni të gati.

**P: Mund ta publikoj vetë dokumentin?**
A: Jo. Sign-off duhet nga Ledjan (ose delegate).

---

## Kontakt

- **Revista Teknik**: Arkitekt sistemi
- **Revista Implementim**: DevOps team
- **Revista Akademike**: Blerina / Eksperte
- **Revista Editorial**: Editor
- **Sign-Off**: Ledjan Ahmati

---

_Procesi i Garantimit të Cilësisë v1.0_  
_Clisonix Cloud — 28 Shkurt 2026_
