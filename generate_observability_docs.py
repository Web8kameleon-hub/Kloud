"""
Kloud Cloud Observability Documentation Generator
Converts Markdown documentation to PDF and HTML for distribution

Requirements:
    pip install markdown2 pdfkit weasyprint beautifulsoup4
    
For PDF generation:
    Option 1: wkhtmltopdf (https://wkhtmltopdf.org/downloads.html)
    Option 2: WeasyPrint (pip install weasyprint)

Usage:
    python generate_observability_docs.py --format pdf
    python generate_observability_docs.py --format html
    python generate_observability_docs.py --format all
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import argparse

try:
    import markdown2
except ImportError:
    print("Installing required packages...")
    os.system("pip install markdown2 beautifulsoup4")
    import markdown2

from bs4 import BeautifulSoup


class ObservabilityDocsGenerator:
    """Generate PDF and HTML exports from observability markdown docs"""
    
    def __init__(self, docs_dir: str = "docs/observability"):
        self.docs_dir = Path(docs_dir)
        self.output_dir = self.docs_dir / "exports"
        self.output_dir.mkdir(exist_ok=True)
        
        # Document order for PDF generation
        self.doc_order = [
            "README.md",
            "architecture.md",
            "metrics-overview.md",
            "prometheus-metrics.md",
            "tsdb-analysis.md",
            "cardinality-engineering.md",
            "alerts.md",
            "anomalies-report.md"
        ]
        
    def get_css_styles(self) -> str:
        """Return CSS styling for HTML/PDF output"""
        return """
        <style>
        @page {
            size: A4;
            margin: 2cm;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #fff;
        }
        
        h1 {
            color: #1a1a1a;
            border-bottom: 3px solid #0066cc;
            padding-bottom: 10px;
            margin-top: 40px;
            font-size: 2.5em;
        }
        
        h2 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 8px;
            margin-top: 30px;
            font-size: 2em;
        }
        
        h3 {
            color: #34495e;
            margin-top: 25px;
            font-size: 1.5em;
        }
        
        h4 {
            color: #555;
            margin-top: 20px;
            font-size: 1.2em;
        }
        
        code {
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', Consolas, Monaco, monospace;
            font-size: 0.9em;
            color: #e74c3c;
        }
        
        pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #0066cc;
        }
        
        pre code {
            background: transparent;
            color: #f8f8f2;
            padding: 0;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        th {
            background: #0066cc;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }
        
        tr:nth-child(even) {
            background: #f9f9f9;
        }
        
        tr:hover {
            background: #f0f0f0;
        }
        
        blockquote {
            border-left: 4px solid #0066cc;
            padding-left: 20px;
            margin: 20px 0;
            color: #555;
            font-style: italic;
            background: #f9f9f9;
            padding: 15px 20px;
        }
        
        img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 20px auto;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-radius: 5px;
        }
        
        ul, ol {
            margin: 15px 0;
            padding-left: 30px;
        }
        
        li {
            margin: 8px 0;
        }
        
        a {
            color: #0066cc;
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-bottom 0.2s;
        }
        
        a:hover {
            border-bottom: 1px solid #0066cc;
        }
        
        hr {
            border: none;
            border-top: 2px solid #eee;
            margin: 40px 0;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: linear-gradient(135deg, #0066cc 0%, #3498db 100%);
            color: white;
            border-radius: 10px;
        }
        
        .header h1 {
            color: white;
            border: none;
            margin: 0;
        }
        
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        
        .footer {
            text-align: center;
            margin-top: 60px;
            padding: 20px;
            border-top: 2px solid #eee;
            color: #777;
            font-size: 0.9em;
        }
        
        .toc {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin: 30px 0;
            border-left: 4px solid #0066cc;
        }
        
        .toc h2 {
            margin-top: 0;
            color: #0066cc;
            border: none;
        }
        
        .toc ul {
            list-style: none;
            padding-left: 0;
        }
        
        .toc li {
            padding: 5px 0;
        }
        
        .page-break {
            page-break-after: always;
        }
        
        @media print {
            body {
                max-width: 100%;
            }
            
            a {
                color: #000;
                text-decoration: none;
            }
            
            .no-print {
                display: none;
            }
        }
        </style>
        """
    
    def read_markdown_file(self, filename: str) -> tuple[str, str]:
        """Read markdown file and return (title, content)"""
        file_path = self.docs_dir / filename
        
        if not file_path.exists():
            print(f"Warning: {filename} not found")
            return "", ""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title from first H1
        lines = content.split('\n')
        title = "Untitled"
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        return title, content
    
    def markdown_to_html(self, markdown_content: str) -> str:
        """Convert markdown to HTML"""
        extras = [
            'fenced-code-blocks',
            'tables',
            'header-ids',
            'task_list',
            'strike',
            'code-friendly',
            'footnotes'
        ]
        
        html = markdown2.markdown(markdown_content, extras=extras)
        return html
    
    def generate_table_of_contents(self) -> str:
        """Generate table of contents"""
        toc_html = '<div class="toc"><h2>📚 Table of Contents</h2><ul>'
        
        for i, filename in enumerate(self.doc_order, 1):
            title, _ = self.read_markdown_file(filename)
            if title:
                # Remove emoji and extra formatting
                clean_title = title.split('—')[0].strip()
                toc_html += f'<li>{i}. <a href="#{self._anchor(clean_title)}">{clean_title}</a></li>'
        
        toc_html += '</ul></div>'
        return toc_html
    
    def _anchor(self, text: str) -> str:
        """Generate HTML anchor from text"""
        return text.lower().replace(' ', '-').replace(':', '').replace('—', '')
    
    def generate_html(self, output_file: str = "observability-docs.html"):
        """Generate complete HTML documentation"""
        print("📄 Generating HTML documentation...")
        
        html_parts = []
        
        # Header
        html_parts.append("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Kloud Cloud — Observability Documentation</title>
        """)
        
        html_parts.append(self.get_css_styles())
        html_parts.append("</head><body>")
        
        # Cover page
        html_parts.append(f"""
        <div class="header">
            <h1>Kloud Cloud</h1>
            <p style="font-size: 1.5em; margin-top: 10px;">Observability Suite</p>
            <p>Enterprise Monitoring • TSDB Analysis • Performance Telemetry</p>
            <p style="margin-top: 20px; font-size: 0.9em;">Generated: {datetime.now().strftime('%B %d, %Y')}</p>
        </div>
        """)
        
        # Table of contents
        html_parts.append(self.generate_table_of_contents())
        
        # Process each document
        for i, filename in enumerate(self.doc_order):
            title, markdown_content = self.read_markdown_file(filename)
            
            if not markdown_content:
                continue
            
            print(f"  Processing {filename}... ({title})")
            
            # Add page break before each section (except first)
            if i > 0:
                html_parts.append('<div class="page-break"></div>')
            
            # Add section anchor
            clean_title = title.split('—')[0].strip()
            html_parts.append(f'<div id="{self._anchor(clean_title)}">')
            
            # Convert markdown to HTML
            html_content = self.markdown_to_html(markdown_content)
            html_parts.append(html_content)
            html_parts.append('</div>')
        
        # Footer
        html_parts.append(f"""
        <div class="footer">
            <p><strong>Kloud Cloud Observability Documentation</strong></p>
            <p>Generated: {datetime.now().strftime('%B %d, %Y at %H:%M UTC')}</p>
            <p>Version 1.0.0 | Maintained by Kloud SRE Team</p>
        </div>
        """)
        
        html_parts.append("</body></html>")
        
        # Write to file
        output_path = self.output_dir / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_parts))
        
        print(f"✅ HTML generated: {output_path}")
        return output_path
    
    def generate_pdf(self, output_file: str = "observability-docs.pdf"):
        """Generate PDF from HTML"""
        print("📕 Generating PDF documentation...")
        
        # First generate HTML
        html_path = self.generate_html("temp-for-pdf.html")
        pdf_path = self.output_dir / output_file
        
        # Try WeasyPrint first (better quality)
        try:
            from weasyprint import HTML
            print("  Using WeasyPrint for PDF generation...")
            HTML(filename=str(html_path)).write_pdf(str(pdf_path))
            print(f"✅ PDF generated: {pdf_path}")
            
            # Clean up temp HTML
            html_path.unlink()
            return pdf_path
            
        except (ImportError, OSError) as e:
            print(f"  WeasyPrint not available: {type(e).__name__}")
            
        # Try pdfkit as fallback
        try:
            import pdfkit
            print("  Using wkhtmltopdf for PDF generation...")
            pdfkit.from_file(str(html_path), str(pdf_path))
            print(f"✅ PDF generated: {pdf_path}")
            
            # Clean up temp HTML
            html_path.unlink()
            return pdf_path
            
        except (ImportError, OSError, Exception) as e:
            print(f"  pdfkit not available: {type(e).__name__}")
            print("\n⚠️  PDF generation requires external dependencies:")
            print("  Option 1: Install GTK libraries for WeasyPrint (complex on Windows)")
            print("  Option 2: Install wkhtmltopdf from https://wkhtmltopdf.org/downloads.html")
            print(f"\n✅ HTML file available at: {html_path}")
            print("   You can open this in a browser and print to PDF (Ctrl+P → Save as PDF)")
            return None
    
    def generate_all(self):
        """Generate both HTML and PDF"""
        html_path = self.generate_html()
        pdf_path = self.generate_pdf()
        
        print("\n" + "=" * 60)
        print("📦 Documentation Export Complete")
        print("=" * 60)
        print(f"HTML: {html_path}")
        if pdf_path:
            print(f"PDF:  {pdf_path}")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Generate Kloud Observability Documentation')
    parser.add_argument(
        '--format',
        choices=['html', 'pdf', 'all'],
        default='all',
        help='Output format (default: all)'
    )
    parser.add_argument(
        '--docs-dir',
        default='docs/observability',
        help='Path to documentation directory'
    )
    
    args = parser.parse_args()
    
    generator = ObservabilityDocsGenerator(args.docs_dir)
    
    if args.format == 'html':
        generator.generate_html()
    elif args.format == 'pdf':
        generator.generate_pdf()
    else:
        generator.generate_all()


if __name__ == "__main__":
    main()


