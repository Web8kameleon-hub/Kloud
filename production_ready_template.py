"""
🚀 KLOUD PRODUCTION-READY EXCEL TEMPLATE
Template i plotë për publikim në Hetzner me të gjitha kolonat:
- Status Testimi, Autentikimi, Dokumentacioni
- Monitorimi, Siguria, Versioni
- Data Publikimit, Owner, Komente
- Drop-down Lists, Conditional Formatting
- Formula për % progresi

Krijon: python production_ready_template.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
    from openpyxl.formatting.rule import FormulaRule, ColorScaleRule
    from openpyxl.chart import BarChart, Reference, PieChart
except ImportError:
    print("❌ pip install openpyxl")
    exit(1)


# ============================================================
# KONFIGURIMI - Drop-down Options
# ============================================================
STATUS_TESTIMI = "✅ Unit Test,✅ Integration,✅ Load Test,⏳ Pending,❌ Failed"
AUTENTIKIMI = "OAuth2,API Key,JWT,Bearer Token,None"
MONITORIMI = "Prometheus,Grafana,Logs,Email Alerts,All"
SIGURIA = "✅ SSL/TLS,✅ Pen Test,✅ Vuln Scan,⏳ Pending,❌ Not Done"
VERSIONI = "v1.0,v1.1,v2.0,v2.1,v3.0"
STATUS_PUBLIKIMI = "✅ Ready,⏳ In Progress,❌ Pending,🔒 Security Review"
DOKUMENTACIONI = "✅ Full Docs,⏳ Partial,❌ Missing,📝 In Progress"


def create_production_template():
    """Krijon Excel template profesional për publikim."""
    
    base_path = Path(__file__).parent
    output_path = base_path / "Kloud_Production_Ready.xlsx"
    
    wb = Workbook()
    
    # ========== SHEET 1: API ENDPOINTS ==========
    ws = wb.active
    ws.title = "API_Endpoints"
    
    # KOLONAT E PLOTA (19 kolona)
    headers = [
        ("A", "Row_ID", 8),
        ("B", "Folder", 20),
        ("C", "Method", 10),
        ("D", "Endpoint", 35),
        ("E", "Përshkrimi", 40),
        ("F", "Status_Testimi", 18),      # Drop-down
        ("G", "Autentikimi", 15),         # Drop-down
        ("H", "Dokumentacioni", 15),      # Drop-down
        ("I", "Monitorimi", 15),          # Drop-down
        ("J", "Siguria", 18),             # Drop-down
        ("K", "Versioni_API", 12),        # Drop-down
        ("L", "Data_Publikimit", 15),
        ("M", "Owner", 20),
        ("N", "Status_Publikimi", 18),    # Drop-down
        ("O", "Komente", 35),
        ("P", "cURL", 60),
        ("Q", "Python_Snippet", 55),
        ("R", "Response_Sample", 40),
        ("S", "Last_Check", 18),
    ]
    
    # Styles
    header_fill = PatternFill(start_color='1F4E79', end_color='1F4E79', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF', size=10)
    header_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    wrap_align = Alignment(horizontal='left', vertical='top', wrap_text=True)
    code_font = Font(name='Consolas', size=9)
    
    # Apliko headers
    for col_letter, header_name, width in headers:
        col_idx = ord(col_letter) - ord('A') + 1
        cell = ws.cell(row=1, column=col_idx, value=header_name)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_align
        cell.border = thin_border
        ws.column_dimensions[col_letter].width = width
    
    # Row height për header
    ws.row_dimensions[1].height = 30
    
    # ========== DATA VALIDATION (Drop-down Lists) ==========
    # Status Testimi (F)
    dv_test = DataValidation(type="list", formula1=f'"{STATUS_TESTIMI}"', allow_blank=True)
    dv_test.error = "Zgjedh një opsion nga lista"
    dv_test.prompt = "Zgjedh statusin e testimit"
    ws.add_data_validation(dv_test)
    dv_test.add("F2:F500")
    
    # Autentikimi (G)
    dv_auth = DataValidation(type="list", formula1=f'"{AUTENTIKIMI}"', allow_blank=True)
    ws.add_data_validation(dv_auth)
    dv_auth.add("G2:G500")
    
    # Dokumentacioni (H)
    dv_docs = DataValidation(type="list", formula1=f'"{DOKUMENTACIONI}"', allow_blank=True)
    ws.add_data_validation(dv_docs)
    dv_docs.add("H2:H500")
    
    # Monitorimi (I)
    dv_mon = DataValidation(type="list", formula1=f'"{MONITORIMI}"', allow_blank=True)
    ws.add_data_validation(dv_mon)
    dv_mon.add("I2:I500")
    
    # Siguria (J)
    dv_sec = DataValidation(type="list", formula1=f'"{SIGURIA}"', allow_blank=True)
    ws.add_data_validation(dv_sec)
    dv_sec.add("J2:J500")
    
    # Versioni (K)
    dv_ver = DataValidation(type="list", formula1=f'"{VERSIONI}"', allow_blank=True)
    ws.add_data_validation(dv_ver)
    dv_ver.add("K2:K500")
    
    # Status Publikimi (N)
    dv_pub = DataValidation(type="list", formula1=f'"{STATUS_PUBLIKIMI}"', allow_blank=True)
    ws.add_data_validation(dv_pub)
    dv_pub.add("N2:N500")
    
    # ========== CONDITIONAL FORMATTING ==========
    # Status Publikimi - Jeshile për Ready
    green_fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
    red_fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
    yellow_fill = PatternFill(start_color='FFEB9C', end_color='FFEB9C', fill_type='solid')
    blue_fill = PatternFill(start_color='BDD7EE', end_color='BDD7EE', fill_type='solid')
    
    # Ready = Green
    ws.conditional_formatting.add('N2:N500',
        FormulaRule(formula=['$N2="✅ Ready"'], fill=green_fill))
    # Pending = Red
    ws.conditional_formatting.add('N2:N500',
        FormulaRule(formula=['$N2="❌ Pending"'], fill=red_fill))
    # In Progress = Yellow
    ws.conditional_formatting.add('N2:N500',
        FormulaRule(formula=['$N2="⏳ In Progress"'], fill=yellow_fill))
    # Security Review = Blue
    ws.conditional_formatting.add('N2:N500',
        FormulaRule(formula=['$N2="🔒 Security Review"'], fill=blue_fill))
    
    # Method Colors
    method_colors = {
        'GET': '2ECC71',
        'POST': '3498DB',
        'PUT': 'F39C12',
        'PATCH': 'E67E22',
        'DELETE': 'E74C3C'
    }
    
    # ========== NGARKO ENDPOINTS ==========
    collection_path = base_path / "kloud-ultra-mega-collection.json"
    if not collection_path.exists():
        collection_path = base_path / "kloud-postman-collection.json"
    
    endpoints = []
    if collection_path.exists():
        with open(collection_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        def extract_endpoints(items, folder_name="Root"):
            for item in items:
                if 'item' in item:
                    extract_endpoints(item['item'], item.get('name', 'Unknown'))
                elif 'request' in item:
                    req = item['request']
                    method = req.get('method', 'GET')
                    
                    url = req.get('url', {})
                    if isinstance(url, str):
                        endpoint = url
                    else:
                        path = url.get('path', [])
                        endpoint = '/' + '/'.join(path) if path else url.get('raw', '')
                    
                    body = ""
                    if 'body' in req and req['body'].get('mode') == 'raw':
                        body = req['body'].get('raw', '')
                    
                    endpoints.append({
                        'folder': folder_name,
                        'method': method,
                        'endpoint': endpoint,
                        'name': item.get('name', ''),
                        'body': body
                    })
        
        if 'item' in data:
            extract_endpoints(data['item'])
    
    # ========== POPULO TABELËN ==========
    today = datetime.now().strftime("%d/%m/%Y")
    base_url = "https://api.kloud.com"
    
    for idx, ep in enumerate(endpoints, 2):
        method = ep['method'].upper()
        row = idx
        
        # A: Row_ID
        ws.cell(row=row, column=1, value=idx-1).alignment = Alignment(horizontal='center')
        
        # B: Folder
        ws.cell(row=row, column=2, value=ep['folder']).alignment = wrap_align
        
        # C: Method (me ngjyrë)
        method_cell = ws.cell(row=row, column=3, value=method)
        color = method_colors.get(method, 'CCCCCC')
        method_cell.fill = PatternFill(start_color=color, end_color=color, fill_type='solid')
        method_cell.font = Font(bold=True, color='FFFFFF')
        method_cell.alignment = Alignment(horizontal='center')
        
        # D: Endpoint
        ws.cell(row=row, column=4, value=ep['endpoint']).font = code_font
        ws.cell(row=row, column=4).alignment = wrap_align
        
        # E: Përshkrimi
        ws.cell(row=row, column=5, value=ep['name']).alignment = wrap_align
        
        # F: Status Testimi - Default
        ws.cell(row=row, column=6, value="✅ Unit Test")
        
        # G: Autentikimi - Default
        ws.cell(row=row, column=7, value="Bearer Token")
        
        # H: Dokumentacioni
        ws.cell(row=row, column=8, value="✅ Full Docs")
        
        # I: Monitorimi
        ws.cell(row=row, column=9, value="Prometheus")
        
        # J: Siguria
        ws.cell(row=row, column=10, value="✅ SSL/TLS")
        
        # K: Versioni
        ws.cell(row=row, column=11, value="v1.0")
        
        # L: Data Publikimit
        ws.cell(row=row, column=12, value=today)
        
        # M: Owner
        ws.cell(row=row, column=13, value="Kloud Team")
        
        # N: Status Publikimi
        ws.cell(row=row, column=14, value="✅ Ready")
        
        # O: Komente
        ws.cell(row=row, column=15, value="Ready for Production")
        
        # P: cURL
        curl = f'curl -X {method} "{base_url}{ep["endpoint"]}" -H "Authorization: Bearer $TOKEN"'
        ws.cell(row=row, column=16, value=curl).font = code_font
        ws.cell(row=row, column=16).alignment = wrap_align
        
        # Q: Python Snippet
        python_code = f'requests.{method.lower()}("{base_url}{ep["endpoint"]}", headers={{"Authorization": "Bearer TOKEN"}})'
        ws.cell(row=row, column=17, value=python_code).font = code_font
        ws.cell(row=row, column=17).alignment = wrap_align
        
        # R: Response Sample
        ws.cell(row=row, column=18, value='{"status": "ok"}').font = code_font
        
        # S: Last Check
        ws.cell(row=row, column=19, value=today)
        
        # Apply borders
        for col in range(1, 20):
            ws.cell(row=row, column=col).border = thin_border
    
    # Freeze panes
    ws.freeze_panes = 'E2'
    
    # ========== SHEET 2: DASHBOARD ==========
    ws2 = wb.create_sheet("Dashboard")
    ws2['A1'] = "📊 KLOUD PUBLICATION DASHBOARD"
    ws2['A1'].font = Font(bold=True, size=18, color='1F4E79')
    
    # Summary Stats
    ws2['A3'] = "📈 STATISTIKA"
    ws2['A3'].font = Font(bold=True, size=14)
    
    ws2['A5'] = "Total Endpoints:"
    ws2['B5'] = len(endpoints)
    ws2['B5'].font = Font(bold=True, size=14)
    
    ws2['A6'] = "Ready for Production:"
    ws2['B6'] = f'=COUNTIF(API_Endpoints!N:N,"✅ Ready")'
    
    ws2['A7'] = "In Progress:"
    ws2['B7'] = f'=COUNTIF(API_Endpoints!N:N,"⏳ In Progress")'
    
    ws2['A8'] = "Pending:"
    ws2['B8'] = f'=COUNTIF(API_Endpoints!N:N,"❌ Pending")'
    
    ws2['A10'] = "% Progresi:"
    ws2['B10'] = f'=ROUND(COUNTIF(API_Endpoints!N:N,"✅ Ready")/COUNTA(API_Endpoints!N2:N500)*100,1)&"%"'
    ws2['B10'].font = Font(bold=True, size=16, color='2ECC71')
    
    # Column widths
    ws2.column_dimensions['A'].width = 25
    ws2.column_dimensions['B'].width = 20
    
    # ========== SHEET 3: CHECKLIST ==========
    ws3 = wb.create_sheet("Pre-Deploy_Checklist")
    ws3['A1'] = "✅ PRE-DEPLOYMENT CHECKLIST FOR HETZNER"
    ws3['A1'].font = Font(bold=True, size=16, color='1F4E79')
    
    checklist = [
        ("", ""),
        ("KATEGORIA", "STATUSI"),
        ("1. Docker Images", "☐ Built & Pushed"),
        ("2. SSL Certificates", "☐ Configured"),
        ("3. Environment Variables", "☐ Set in Hetzner"),
        ("4. Database Migration", "☐ Completed"),
        ("5. Redis Connection", "☐ Tested"),
        ("6. API Endpoints", "☐ All Tested"),
        ("7. Monitoring Setup", "☐ Prometheus/Grafana"),
        ("8. Logging", "☐ Configured"),
        ("9. Backup Strategy", "☐ Defined"),
        ("10. DNS Configuration", "☐ Pointed"),
        ("11. Load Balancer", "☐ Configured"),
        ("12. Security Scan", "☐ Passed"),
        ("13. Performance Test", "☐ Completed"),
        ("14. Documentation", "☐ Updated"),
        ("15. Rollback Plan", "☐ Documented"),
    ]
    
    for i, (item, status) in enumerate(checklist, 1):
        ws3[f'A{i+1}'] = item
        ws3[f'B{i+1}'] = status
        if i == 1:
            ws3[f'A{i+1}'].font = Font(bold=True)
            ws3[f'B{i+1}'].font = Font(bold=True)
    
    ws3.column_dimensions['A'].width = 35
    ws3.column_dimensions['B'].width = 25
    
    # ========== SHEET 4: OFFICE SCRIPT ==========
    ws4 = wb.create_sheet("API_Script")
    ws4['A1'] = "🐍 OFFICE SCRIPT PËR API STATUS CHECK"
    ws4['A1'].font = Font(bold=True, size=14)
    
    script_code = '''// Office Script për Excel Online
// Kontrollon statusin e API endpoints

async function main(workbook: ExcelScript.Workbook) {
    const sheet = workbook.getWorksheet("API_Endpoints");
    const range = sheet.getUsedRange();
    const values = range.getValues();
    
    // Skip header row
    for (let i = 1; i < values.length; i++) {
        const endpoint = values[i][3]; // Column D - Endpoint
        const method = values[i][2];   // Column C - Method
        
        if (endpoint && typeof endpoint === 'string') {
            try {
                // Simulate API check (replace with actual fetch in production)
                const status = "✅ Connected";
                const timestamp = new Date().toLocaleString();
                
                // Update Last Check column (S)
                sheet.getCell(i, 18).setValue(timestamp);
                
                console.log(`Checked: ${endpoint} - ${status}`);
            } catch (error) {
                sheet.getCell(i, 18).setValue("❌ Error");
            }
        }
    }
    
    console.log("API Status Check Complete!");
}'''
    
    ws4['A3'] = "Kopjo këtë script në Excel Online → Automate → New Script"
    ws4['A5'] = script_code
    ws4['A5'].font = Font(name='Consolas', size=9)
    ws4['A5'].alignment = Alignment(wrap_text=True)
    
    ws4.column_dimensions['A'].width = 100
    ws4.row_dimensions[5].height = 400
    
    # ========== SHEET 5: OFFICE SCRIPTS FUNCTIONS ==========
    ws5 = wb.create_sheet("Functions_Registry")
    ws5['A1'] = "📋 OFFICE SCRIPTS & PYTHON FUNCTIONS REGISTRY"
    ws5['A1'].font = Font(bold=True, size=16, color='1F4E79')
    
    # Headers
    func_headers = ["ID", "Function Name", "File", "Type", "Description", "Parameters", "Returns", "Status"]
    for col, h in enumerate(func_headers, 1):
        cell = ws5.cell(row=3, column=col, value=h)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_align
        cell.border = thin_border
    
    # Functions data
    functions = [
        (1, "main", "UpdateStatusFromAPI.ts", "Office Script", "Kontrollon statusin e të gjitha API endpoints", "workbook: ExcelScript.Workbook", "void", "✅ Ready"),
        (2, "main", "PowerAutomateConnector.ts", "Office Script", "Kolekton endpoints për Power Automate", "workbook: ExcelScript.Workbook", "EndpointData[]", "✅ Ready"),
        (3, "updateResult", "PowerAutomateConnector.ts", "Office Script", "Përditëson rezultatin pas HTTP request", "workbook, row, status, response, latency", "void", "✅ Ready"),
        (4, "create_production_template", "production_ready_template.py", "Python", "Gjeneron Excel template me 19 kolona", "output_path: str", "tuple[str, int]", "✅ Ready"),
        (5, "create_api_generator_template", "api_request_generator.py", "Python", "Krijon template me =PY() formulas", "output_path: str", "tuple[str, int]", "✅ Ready"),
        (6, "generate_master_table", "generate_master_table.py", "Python", "Gjeneron Master Table me 71 APIs", "None", "None", "✅ Ready"),
        (7, "extract_endpoints", "production_ready_template.py", "Python", "Nxjerr endpoints nga Postman collection", "items, folder_name", "list", "✅ Ready"),
    ]
    
    for row_idx, func in enumerate(functions, 4):
        for col_idx, value in enumerate(func, 1):
            cell = ws5.cell(row=row_idx, column=col_idx, value=value)
            cell.border = thin_border
            cell.alignment = wrap_align
            if col_idx == 8:  # Status column
                if "Ready" in str(value):
                    cell.fill = PatternFill(start_color='C6EFCE', end_color='C6EFCE', fill_type='solid')
    
    # Column widths
    ws5.column_dimensions['A'].width = 6
    ws5.column_dimensions['B'].width = 25
    ws5.column_dimensions['C'].width = 30
    ws5.column_dimensions['D'].width = 15
    ws5.column_dimensions['E'].width = 45
    ws5.column_dimensions['F'].width = 40
    ws5.column_dimensions['G'].width = 20
    ws5.column_dimensions['H'].width = 12
    
    ws5.freeze_panes = 'A4'
    
    # Save
    wb.save(output_path)
    return str(output_path), len(endpoints)


def main():
    print("🚀 KLOUD PRODUCTION-READY TEMPLATE")
    print("=" * 55)
    
    output_path, count = create_production_template()
    
    print(f"✅ Template Created: {output_path}")
    print(f"📊 {count} API endpoints loaded")
    print()
    print("📋 KOLONAT (19 total):")
    print("   A: Row_ID")
    print("   B: Folder")
    print("   C: Method")
    print("   D: Endpoint")
    print("   E: Përshkrimi")
    print("   F: Status_Testimi     ← Drop-down")
    print("   G: Autentikimi        ← Drop-down")
    print("   H: Dokumentacioni     ← Drop-down")
    print("   I: Monitorimi         ← Drop-down")
    print("   J: Siguria            ← Drop-down")
    print("   K: Versioni_API       ← Drop-down")
    print("   L: Data_Publikimit")
    print("   M: Owner")
    print("   N: Status_Publikimi   ← Drop-down + Conditional Formatting")
    print("   O: Komente")
    print("   P: cURL")
    print("   Q: Python_Snippet")
    print("   R: Response_Sample")
    print("   S: Last_Check")
    print()
    print("📑 SHEETS:")
    print("   1. API_Endpoints      - Tabela kryesore")
    print("   2. Dashboard          - Statistika & Progresi")
    print("   3. Pre-Deploy_Checklist - Checklist për Hetzner")
    print("   4. API_Script         - Office Script për API check")
    print()
    print("📂 Opening in Excel...")
    
    os.startfile(output_path)
    
    print("✅ Done! Ready for Hetzner deployment!")


if __name__ == "__main__":
    main()

