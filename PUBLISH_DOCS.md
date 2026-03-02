# 📰 Publikimi i Dokumentave në Blog

Sistemi i publikimit merr dokumenta nga `clisonix-cloud` repo dhe i dërgon në `clisonix-blog` GitHub repo.
Publisheri automatikisht poston në LinkedIn.

## Dokumenta Kryesore për Publikim

| Dokument | Status | Komanda |
|----------|--------|---------|
| `LAGTER_PROTOCOLS.md` | ✅ Publikuar | `python publish_to_blog.py --doc docs/LAGTER_PROTOCOLS.md` |
| `NANOGRIDATA_SYSTEM_ARCHITECTURE.md` | 📋 I pret | `python publish_to_blog.py --doc NANOGRIDATA_SYSTEM_ARCHITECTURE.md` |
| `COMPLETE_SYSTEM_GUIDE.md` | 📋 I pret | `python publish_to_blog.py --doc COMPLETE_SYSTEM_GUIDE.md` |
| `CLISONIX_ARCHITECTURE_BASELINE_2025.md` | 📋 I pret | `python publish_to_blog.py --doc CLISONIX_ARCHITECTURE_BASELINE_2025.md` |
| `LAGTER_LAB.md` | 📋 I pret | `python publish_to_blog.py --doc docs/LAGTER_LAB.md` |
| `LAGTER_LAWS.md` | 📋 I pret | `python publish_to_blog.py --doc docs/LAGTER_LAWS.md` |

## Pipeline

```
clisonix-cloud/ repo
       ↓
LAGTER_PROTOCOLS.md
       ↓
publish_to_blog.py
       ↓
clisonix-blog/ repo (GitHub)
       ↓
linkedin_auto_poster.py
       ↓
LinkedIn (automatikisht)
```

## Mënyra e Publikimit

### 1️⃣ Publikim Local (Test)
```bash
python publish_to_blog.py --doc docs/LAGTER_PROTOCOLS.md --no-push
```

### 2️⃣ Publikim në GitHub (me Push)
```bash
python publish_to_blog.py --doc docs/LAGTER_PROTOCOLS.md
```

### 3️⃣ Me Custom Titull
```bash
python publish_to_blog.py --doc NANOGRIDATA_SYSTEM_ARCHITECTURE.md --title "NanoGrid Data Gateway - Production Architecture"
```

## Output

Përgatitet:
- ✅ Frontmatter metadata (title, tags, author, published date)
- ✅ Description (auto-extracted)
- ✅ Tags (auto-generated nga keywords)
- ✅ Source link (pointer tek original repo)
- ✅ File slug (auto-generated)
- ✅ publications.json tracking

Publikohet në:
```
clisonix-blog/posts/lagter-protocols-operational-methodology.md
```

LinkedIn publisher merr nga këtu automatikisht ✅
