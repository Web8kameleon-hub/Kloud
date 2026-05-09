# Observability Documentation Exports

This folder contains generated documentation exports in various formats.

## 📄 Available Files

- **observability-docs.html** — Complete HTML documentation (116KB)
  - Self-contained with embedded CSS
  - Can be opened directly in any browser
  - Print-friendly (Ctrl+P → Save as PDF)
  - Includes table of contents with navigation

## 🚀 Viewing the Documentation

### Method 1: Open in Browser (Recommended)
```bash
# Windows
start docs/observability/exports/observability-docs.html

# macOS
open docs/observability/exports/observability-docs.html

# Linux
xdg-open docs/observability/exports/observability-docs.html
```

### Method 2: Local Web Server
```bash
# Python
cd docs/observability/exports
python -m http.server 8080
# Open http://localhost:8080/observability-docs.html

# Node.js
npx http-server docs/observability/exports
```

## 📥 Creating PDF Version

Since PDF generation requires external dependencies, the easiest method is:

### Browser Print-to-PDF (Recommended)
1. Open `observability-docs.html` in Chrome/Edge/Firefox
2. Press `Ctrl+P` (Windows) or `Cmd+P` (macOS)
3. Select "Save as PDF" as destination
4. Configure:
   - Paper size: A4
   - Margins: Default
   - Background graphics: ✅ Enabled
5. Click "Save"

### Automated PDF Generation (Advanced)

**Option 1: wkhtmltopdf**
```bash
# Install from https://wkhtmltopdf.org/downloads.html
# Then run:
pip install pdfkit
python generate_observability_docs.py --format pdf
```

**Option 2: WeasyPrint** (Linux/macOS)
```bash
# Ubuntu/Debian
sudo apt-get install python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0

# macOS
brew install cairo pango gdk-pixbuf libffi

# Then:
pip install weasyprint
python generate_observability_docs.py --format pdf
```

## 🔄 Regenerating Documentation

Whenever you update markdown files in `docs/observability/`, regenerate exports:

```bash
# Generate HTML only
python generate_observability_docs.py --format html

# Generate PDF only (requires dependencies)
python generate_observability_docs.py --format pdf

# Generate both
python generate_observability_docs.py --format all
```

## 📤 Sharing Documentation

### For Investors/Partners
1. Generate PDF using browser print
2. Share `observability-docs.pdf`
3. Alternatively, share HTML file (self-contained)

### For Internal Wiki
1. Use `observability-docs.html`
2. Host on internal web server
3. Or embed in Confluence/Notion using iframe

### For GitHub
- HTML is automatically committed via CI/CD
- Available at: `https://github.com/LedjanAhmati/Kloud-cloud/blob/main/docs/observability/exports/observability-docs.html`
- GitHub renders HTML files (limited styling)

## 🎨 Customization

Edit CSS styles in `generate_observability_docs.py`:
- Header colors/gradient
- Code block themes
- Table styling
- Font families

## 📊 Including Charts

The documentation references charts from `docs/observability/grafana-dashboards/`:
- `chart1.png` → Memory Usage by Label Name
- `chart2.png` → Top Label Value Pair Cardinality
- `chart3.png` → TSDB Time Window Timeline
- `chart4.png` → Top Metric Families by Series Count
- `chart5.png` → Label Cardinality
- `chart6.png` → Total Active Time Series

**To include charts in exports:**
1. Save PNG files to `grafana-dashboards/` folder
2. Regenerate documentation
3. Charts will be embedded in HTML/PDF

## 🤖 CI/CD Integration

Documentation auto-generates on every commit to `docs/observability/*.md`:

```yaml
# .github/workflows/docs-observability.yml
on:
  push:
    paths:
      - 'docs/observability/*.md'
```

See `.github/workflows/docs-observability.yml` for full configuration.

---

**Last Updated:** December 11, 2025  
**Generator:** `generate_observability_docs.py`

