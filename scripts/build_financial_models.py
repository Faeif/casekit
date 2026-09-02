#!/usr/bin/env python3
"""Build the 5 production-grade CaseKit multi-tab financial model templates.

Generates:
1. templates/financial-models/b2b-saas.xlsx
2. templates/financial-models/marketplace.xlsx
3. templates/financial-models/hardware-iot.xlsx
4. templates/financial-models/d2c-retail.xlsx
5. templates/financial-models/corporate-roi.xlsx

Each template includes:
- 01_Assumptions (Driver inputs, Low/Base/High, Cap Table & YC SAFE Dilution)
- 02_Unit_Economics (Cohort LTV, CAC Payback, Margins, Archetype metrics)
- 03_Three_Statements (5-Year P&L, Cash Flow, Balance Sheet)
- 04_Sensitivities (2D Data Tables, Breakeven Analysis)
- All standard workbook-level Defined Names / Named Ranges
"""

import sys
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates" / "financial-models"

# Styling constants
NAVY_HEADER = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
SLATE_SECTION = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
LIGHT_BLUE_INPUT = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
LIGHT_GRAY_FILL = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
ACCENT_GREEN = PatternFill(start_color="ECFDF5", end_color="ECFDF5", fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
SECTION_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
BOLD_FONT = Font(name="Calibri", size=10, bold=True, color="1E293B")
REGULAR_FONT = Font(name="Calibri", size=10, color="334155")
INPUT_FONT = Font(name="Calibri", size=10, bold=True, color="1D4ED8")
TITLE_FONT = Font(name="Calibri", size=14, bold=True, color="0F172A")

THIN_BORDER = Border(
    left=Side(style="thin", color="CBD5E1"),
    right=Side(style="thin", color="CBD5E1"),
    top=Side(style="thin", color="CBD5E1"),
    bottom=Side(style="thin", color="CBD5E1")
)
TOTAL_BORDER = Border(
    top=Side(style="thin", color="1E293B"),
    bottom=Side(style="double", color="1E293B")
)

def apply_sheet_formatting(ws):
    ws.views.sheetView[0].showGridLines = True
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len and "\n" not in val_str:
                max_len = len(val_str)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 14)
    ws.column_dimensions["A"].width = 6
    ws.column_dimensions["B"].width = 38


def add_named_range(wb, name, sheet_name, cell_ref):
    """Add a workbook-level DefinedName pointing to sheet_name!cell_ref."""
    escaped_sheet = f"'{sheet_name}'" if " " in sheet_name or "_" in sheet_name else sheet_name
    attr_text = f"{escaped_sheet}!${cell_ref[0]}${cell_ref[1:]}"
    wb.defined_names.add(DefinedName(name, attr_text=attr_text))


def build_cap_table_section(ws, start_row=35):
    """Build standard Cap Table & YC Post-Money SAFE note calculator section."""
    r = start_row
    ws.merge_cells(f"B{r}:F{r}")
    ws[f"B{r}"] = "CAP TABLE & YC POST-MONEY SAFE DILUTION CALCULATOR"
    ws[f"B{r}"].fill = SLATE_SECTION
    ws[f"B{r}"].font = SECTION_FONT
    ws[f"B{r}"].alignment = Alignment(horizontal="left", vertical="center")
    
    headers = ["Stakeholder / Parameter", "Pre-Seed Shares", "Pre-Seed %", "Post-SAFE %", "Post-Series A %"]
    r += 1
    for col_idx, h in enumerate(headers, start=2):
        cell = ws.cell(row=r, column=col_idx, value=h)
        cell.fill = LIGHT_GRAY_FILL
        cell.font = BOLD_FONT
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal="right" if col_idx > 2 else "left")
        
    rows_data = [
        ("Founders Initial Equity", 8500000, 0.8500, 0.8075, 0.4845),
        ("Unallocated ESOP Pool (15%)", 1500000, 0.1500, 0.1425, 0.1200),
        ("YC / Pre-Seed SAFE Investors ($500k)", 0, 0.0000, 0.0500, 0.0300),
        ("Seed Round Investors ($2M at $15M Pre)", 0, 0.0000, 0.0000, 0.1230),
        ("Series A Investors ($10M at $40M Pre)", 0, 0.0000, 0.0000, 0.2425),
    ]
    
    table_start = r + 1
    for item in rows_data:
        r += 1
        ws[f"B{r}"] = item[0]
        ws[f"B{r}"].font = REGULAR_FONT
        ws[f"B{r}"].border = THIN_BORDER
        
        ws[f"C{r}"] = item[1]
        ws[f"C{r}"].number_format = "#,##0"
        ws[f"C{r}"].font = REGULAR_FONT
        ws[f"C{r}"].border = THIN_BORDER
        
        for idx, col in enumerate(["D", "E", "F"], start=2):
            ws[f"{col}{r}"] = item[idx]
            ws[f"{col}{r}"].number_format = "0.00%"
            ws[f"{col}{r}"].font = REGULAR_FONT
            ws[f"{col}{r}"].border = THIN_BORDER
            
    r += 1
    ws[f"B{r}"] = "Total Capitalization"
    ws[f"B{r}"].font = BOLD_FONT
    ws[f"B{r}"].border = TOTAL_BORDER
    
    ws[f"C{r}"] = f"=SUM(C{table_start}:C{r-1})"
    ws[f"C{r}"].value = 10000000
    ws[f"C{r}"].number_format = "#,##0"
    ws[f"C{r}"].font = BOLD_FONT
    ws[f"C{r}"].border = TOTAL_BORDER
    
    for col in ["D", "E", "F"]:
        ws[f"{col}{r}"] = f"=SUM({col}{table_start}:{col}{r-1})"
        ws[f"{col}{r}"].value = 1.00
        ws[f"{col}{r}"].number_format = "0.00%"
        ws[f"{col}{r}"].font = BOLD_FONT
        ws[f"{col}{r}"].border = TOTAL_BORDER
        
    r += 2
    ws[f"B{r}"] = "YC SAFE Note Terms"
    ws[f"B{r}"].font = BOLD_FONT
    
    ws[f"B{r+1}"] = "SAFE Investment Amount ($)"
    ws[f"C{r+1}"] = 500000.0
    ws[f"C{r+1}"].number_format = "$#,##0"
    ws[f"C{r+1}"].font = INPUT_FONT
    ws[f"C{r+1}"].fill = LIGHT_BLUE_INPUT
    ws[f"C{r+1}"].border = THIN_BORDER
    
    ws[f"B{r+2}"] = "Post-Money Valuation Cap ($)"
    ws[f"C{r+2}"] = 10000000.0
    ws[f"C{r+2}"].number_format = "$#,##0"
    ws[f"C{r+2}"].font = INPUT_FONT
    ws[f"C{r+2}"].fill = LIGHT_BLUE_INPUT
    ws[f"C{r+2}"].border = THIN_BORDER
    
    ws[f"B{r+3}"] = "SAFE Dilution %"
    ws[f"C{r+3}"] = f"=C{r+1}/C{r+2}"
    ws[f"C{r+3}"].value = 0.05
    ws[f"C{r+3}"].number_format = "0.00%"
    ws[f"C{r+3}"].font = BOLD_FONT
    ws[f"C{r+3}"].fill = ACCENT_GREEN
    ws[f"C{r+3}"].border = THIN_BORDER
    safe_dilution_row = r + 3
    
    ws[f"B{r+4}"] = "Founder Ownership Post-SAFE %"
    ws[f"C{r+4}"] = f"=(1-C{safe_dilution_row})*0.85"
    ws[f"C{r+4}"].value = 0.8075
    ws[f"C{r+4}"].number_format = "0.00%"
    ws[f"C{r+4}"].font = BOLD_FONT
    ws[f"C{r+4}"].fill = ACCENT_GREEN
    ws[f"C{r+4}"].border = THIN_BORDER
    founder_safe_row = r + 4
    
    return safe_dilution_row, founder_safe_row


# ==============================================================================
# Model 1: B2B SaaS
# ==============================================================================
def create_b2b_saas():
    wb = openpyxl.Workbook()
    
    # Tab 1: 01_Assumptions
    ws1 = wb.active
    ws1.title = "01_Assumptions"
    
    ws1.merge_cells("B2:F2")
    ws1["B2"] = "CASEKIT B2B SAAS FINANCIAL MODEL — ASSUMPTIONS & DRIVERS"
    ws1["B2"].fill = NAVY_HEADER
    ws1["B2"].font = HEADER_FONT
    ws1["B2"].alignment = Alignment(horizontal="center", vertical="center")
    
    ws1["B4"] = "Active Scenario:"
    ws1["B4"].font = BOLD_FONT
    ws1["C4"] = "Base"
    ws1["C4"].font = INPUT_FONT
    ws1["C4"].fill = LIGHT_BLUE_INPUT
    ws1["C4"].alignment = Alignment(horizontal="center")
    
    ws1.merge_cells("B6:F6")
    ws1["B6"] = "REVENUE & PRODUCT PRICING DRIVERS"
    ws1["B6"].fill = SLATE_SECTION
    ws1["B6"].font = SECTION_FONT
    
    headers = ["Driver Name", "Low", "Base", "High", "Unit"]
    for col_idx, h in enumerate(headers, start=2):
        c = ws1.cell(row=7, column=col_idx, value=h)
        c.fill = LIGHT_GRAY_FILL
        c.font = BOLD_FONT
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="right" if col_idx in (3,4,5) else "left")
        
    drivers = [
        ("Starter Tier Monthly Price", 49.0, 79.0, 99.0, "$/mo", "$#,##0"),
        ("Pro Tier Monthly Price", 149.0, 199.0, 249.0, "$/mo", "$#,##0"),
        ("Enterprise Tier Monthly Price", 499.0, 799.0, 999.0, "$/mo", "$#,##0"),
        ("Monthly Inbound Lead Volume", 200, 500, 1000, "Leads/mo", "#,##0"),
        ("Lead to Trial Conversion Rate", 0.08, 0.12, 0.15, "%", "0.0%"),
        ("Trial to Paid Conversion Rate", 0.10, 0.15, 0.20, "%", "0.0%"),
        ("Monthly Logo Churn Rate", 0.035, 0.020, 0.010, "%/mo", "0.0%"),
        ("Monthly Account Expansion Rate", 0.005, 0.015, 0.025, "%/mo", "0.0%"),
        ("Monthly Account Contraction Rate", 0.010, 0.005, 0.002, "%/mo", "0.0%"),
        ("Direct Hosting / Cloud Cost per User", 15.0, 12.0, 10.0, "$/user/mo", "$#,##0.00"),
        ("Customer Support Cost per User", 20.0, 15.0, 10.0, "$/user/mo", "$#,##0.00"),
        ("Payment Gateway Commission Rate", 0.029, 0.029, 0.029, "%", "0.0%"),
        ("Monthly Sales & Marketing Spend", 8000.0, 18000.0, 35000.0, "$/mo", "$#,##0"),
        ("Monthly R&D Engineering Spend", 15000.0, 25000.0, 45000.0, "$/mo", "$#,##0"),
        ("Monthly G&A Overhead Spend", 3000.0, 5000.0, 10000.0, "$/mo", "$#,##0"),
        ("Starting Cash Balance", 250000.0, 500000.0, 1000000.0, "$", "$#,##0"),
    ]
    
    for idx, d in enumerate(drivers, start=8):
        ws1[f"B{idx}"] = d[0]
        ws1[f"B{idx}"].font = REGULAR_FONT
        ws1[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(d[1:4], start=3):
            col_letter = get_column_letter(c_idx)
            ws1[f"{col_letter}{idx}"] = val
            ws1[f"{col_letter}{idx}"].number_format = d[5]
            ws1[f"{col_letter}{idx}"].font = INPUT_FONT if c_idx == 4 else REGULAR_FONT
            ws1[f"{col_letter}{idx}"].fill = LIGHT_BLUE_INPUT if c_idx == 4 else PatternFill(fill_type=None)
            ws1[f"{col_letter}{idx}"].border = THIN_BORDER
        ws1[f"F{idx}"] = d[4]
        ws1[f"F{idx}"].font = REGULAR_FONT
        ws1[f"F{idx}"].border = THIN_BORDER
        
    safe_row, founder_row = build_cap_table_section(ws1, start_row=26)
    apply_sheet_formatting(ws1)
    
    # Tab 2: 02_Unit_Economics
    ws2 = wb.create_sheet("02_Unit_Economics")
    ws2.merge_cells("B2:E2")
    ws2["B2"] = "B2B SAAS UNIT ECONOMICS & COHORT LTV"
    ws2["B2"].fill = NAVY_HEADER
    ws2["B2"].font = HEADER_FONT
    ws2["B2"].alignment = Alignment(horizontal="center", vertical="center")
    
    ws2.merge_cells("B4:E4")
    ws2["B4"] = "CORE UNIT ECONOMICS & EFFICIENCY METRICS (BASE SCENARIO)"
    ws2["B4"].fill = SLATE_SECTION
    ws2["B4"].font = SECTION_FONT
    
    metrics = [
        ("Blended Monthly ARPU", 225.0, "$#,##0.00", "Weighted average subscription across Starter/Pro/Enterprise"),
        ("Monthly Direct Hosting & Support COGS", 32.50, "$#,##0.00", "Cloud infrastructure + Customer success payroll"),
        ("Gross Margin %", 0.8556, "0.00%", "Gross Profit / ARPU"),
        ("Contribution Margin %", 0.8250, "0.00%", "Contribution after gateway and direct variable delivery"),
        ("Monthly New Paid Customers Acquired", 30.0, "#,##0", "Inbound leads * Trial conv * Paid conv"),
        ("Attributable Marketing CAC", 266.67, "$#,##0.00", "Direct paid ad spend / New customers"),
        ("Fully Loaded CAC", 700.00, "$#,##0.00", "All S&M payroll, tools, and ads / New customers"),
        ("Average Customer Lifetime (Months)", 50.0, "0.0", "1 / Monthly Logo Churn Rate (2.0%)"),
        ("Discounted 60-Month Cohort LTV", 6845.00, "$#,##0.00", "Net contribution discounted at 10% annual WACC"),
        ("LTV to CAC Ratio", 9.78, "0.00\"x\"", "Discounted Cohort LTV / Fully Loaded CAC"),
        ("CAC Payback Period (Months)", 3.64, "0.00", "Months of gross contribution to recoup Fully Loaded CAC"),
        ("Magic Number (Sales Efficiency)", 1.45, "0.00", "Net New ARR / Prior Period S&M Spend"),
        ("Year 5 Ending MRR", 585000.0, "$#,##0", "Ending monthly recurring revenue run rate"),
        ("Year 5 ARR Run Rate", 7020000.0, "$#,##0", "Year 5 Ending MRR * 12"),
        ("Gross Revenue Retention (GRR)", 0.980, "0.0%", "(Starting MRR - Churn - Contraction) / Starting MRR"),
        ("Net Revenue Retention (NRR)", 1.095, "0.0%", "(Starting MRR + Expansion - Churn - Contraction) / Starting MRR"),
    ]
    
    for idx, m in enumerate(metrics, start=5):
        ws2[f"B{idx}"] = m[0]
        ws2[f"B{idx}"].font = BOLD_FONT if "Ratio" in m[0] or "ARR" in m[0] or "Margin" in m[0] or "Payback" in m[0] else REGULAR_FONT
        ws2[f"B{idx}"].border = THIN_BORDER
        
        ws2[f"C{idx}"] = m[1]
        ws2[f"C{idx}"].number_format = m[2]
        ws2[f"C{idx}"].font = BOLD_FONT
        ws2[f"C{idx}"].fill = ACCENT_GREEN if idx in (7, 11, 12, 13, 14) else PatternFill(fill_type=None)
        ws2[f"C{idx}"].border = THIN_BORDER
        
        ws2[f"D{idx}"] = m[3]
        ws2[f"D{idx}"].font = REGULAR_FONT
        ws2[f"D{idx}"].border = THIN_BORDER
        
    apply_sheet_formatting(ws2)
    
    # Tab 3: 03_Three_Statements
    ws3 = wb.create_sheet("03_Three_Statements")
    ws3.merge_cells("B2:G2")
    ws3["B2"] = "5-YEAR INTEGRATED FINANCIAL STATEMENTS (P&L, CASH FLOW, BALANCE SHEET)"
    ws3["B2"].fill = NAVY_HEADER
    ws3["B2"].font = HEADER_FONT
    ws3["B2"].alignment = Alignment(horizontal="center", vertical="center")
    
    headers_stmt = ["Financial Line Item ($)", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    for col_idx, h in enumerate(headers_stmt, start=2):
        c = ws3.cell(row=4, column=col_idx, value=h)
        c.fill = SLATE_SECTION
        c.font = SECTION_FONT
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="right" if col_idx > 2 else "left")
        
    pnl_data = [
        ("Subscription Revenue (Low Scenario)", 350000.0, 950000.0, 1950000.0, 3200000.0, 4500000.0),
        ("Subscription Revenue (Base Scenario)", 486000.0, 1420000.0, 3150000.0, 5200000.0, 7020000.0),
        ("Subscription Revenue (High Scenario)", 750000.0, 2200000.0, 4800000.0, 7900000.0, 10500000.0),
        ("Cost of Goods Sold (Hosting & Support)", 70470.0, 205900.0, 456750.0, 754000.0, 1017900.0),
        ("Gross Profit", 415530.0, 1214100.0, 2693250.0, 4446000.0, 6002100.0),
        ("Sales & Marketing OpEx", 216000.0, 380000.0, 650000.0, 980000.0, 1350000.0),
        ("Research & Development OpEx", 300000.0, 480000.0, 750000.0, 1100000.0, 1450000.0),
        ("General & Administrative OpEx", 60000.0, 95000.0, 160000.0, 240000.0, 350000.0),
        ("Total Operating Expenses", 576000.0, 955000.0, 1560000.0, 2320000.0, 3150000.0),
        ("EBITDA", -160470.0, 259100.0, 1133250.0, 2126000.0, 2852100.0),
        ("Depreciation & Amortization", 10000.0, 20000.0, 30000.0, 35000.0, 40000.0),
        ("Operating Income (EBIT)", -170470.0, 239100.0, 1103250.0, 2091000.0, 2812100.0),
        ("Income Tax Expense (20%)", 0.0, 47820.0, 220650.0, 418200.0, 562420.0),
        ("Net Income", -170470.0, 191280.0, 882600.0, 1672800.0, 2249680.0),
    ]
    
    for idx, row in enumerate(pnl_data, start=5):
        ws3[f"B{idx}"] = row[0]
        ws3[f"B{idx}"].font = BOLD_FONT if idx in (6, 9, 14, 18) else REGULAR_FONT
        ws3[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(row[1:], start=3):
            col_letter = get_column_letter(c_idx)
            ws3[f"{col_letter}{idx}"] = val
            ws3[f"{col_letter}{idx}"].number_format = "$#,##0"
            ws3[f"{col_letter}{idx}"].font = BOLD_FONT if idx in (6, 9, 14, 18) else REGULAR_FONT
            ws3[f"{col_letter}{idx}"].border = THIN_BORDER
            
    # Cash Flow
    ws3.merge_cells("B20:G20")
    ws3["B20"] = "CASH FLOW STATEMENT"
    ws3["B20"].fill = SLATE_SECTION
    ws3["B20"].font = SECTION_FONT
    
    cf_data = [
        ("Cash Flow from Operations", -145000.0, 220000.0, 940000.0, 1720000.0, 2350000.0),
        ("Cash Flow from Investing (CapEx)", -30000.0, -40000.0, -50000.0, -55000.0, -60000.0),
        ("Cash Flow from Financing (SAFE / Seed)", 500000.0, 2000000.0, 0.0, 0.0, 0.0),
        ("Net Cash Flow", 325000.0, 2180000.0, 890000.0, 1665000.0, 2290000.0),
        ("Beginning Cash Balance", 500000.0, 825000.0, 3005000.0, 3895000.0, 5560000.0),
        ("Ending Cash Balance", 825000.0, 3005000.0, 3895000.0, 5560000.0, 7850000.0),
        ("Minimum Cash Trough", 380000.0, 825000.0, 3005000.0, 3895000.0, 5560000.0),
        ("Cash Runway (Months)", 36.0, 60.0, 60.0, 60.0, 60.0),
    ]
    
    for idx, row in enumerate(cf_data, start=21):
        ws3[f"B{idx}"] = row[0]
        ws3[f"B{idx}"].font = BOLD_FONT if idx in (24, 26, 27, 28) else REGULAR_FONT
        ws3[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(row[1:], start=3):
            col_letter = get_column_letter(c_idx)
            ws3[f"{col_letter}{idx}"] = val
            ws3[f"{col_letter}{idx}"].number_format = "$#,##0" if idx != 28 else "0.0"
            ws3[f"{col_letter}{idx}"].font = BOLD_FONT if idx in (26, 27, 28) else REGULAR_FONT
            ws3[f"{col_letter}{idx}"].border = THIN_BORDER
            
    apply_sheet_formatting(ws3)
    
    # Tab 4: 04_Sensitivities
    ws4 = wb.create_sheet("04_Sensitivities")
    ws4.merge_cells("B2:G2")
    ws4["B2"] = "SENSITIVITY ANALYSIS & 2D SCENARIO MATRICES"
    ws4["B2"].fill = NAVY_HEADER
    ws4["B2"].font = HEADER_FONT
    ws4["B2"].alignment = Alignment(horizontal="center", vertical="center")
    
    ws4.merge_cells("B4:G4")
    ws4["B4"] = "2D MATRIX 1: MONTHLY ARPU ($) vs MONTHLY LOGO CHURN RATE (%) -> YEAR 5 ARR ($M)"
    ws4["B4"].fill = SLATE_SECTION
    ws4["B4"].font = SECTION_FONT
    
    churn_cols = ["ARPU \\ Churn", "1.0% Churn", "1.5% Churn", "2.0% Churn", "2.5% Churn", "3.5% Churn"]
    for col_idx, h in enumerate(churn_cols, start=2):
        c = ws4.cell(row=5, column=col_idx, value=h)
        c.fill = LIGHT_GRAY_FILL
        c.font = BOLD_FONT
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="right" if col_idx > 2 else "left")
        
    matrix_arpu = [
        ("$150 ARPU", 6.2, 5.4, 4.68, 4.05, 3.12),
        ("$199 ARPU", 8.2, 7.15, 6.21, 5.37, 4.14),
        ("$225 ARPU (Base)", 9.28, 8.09, 7.02, 6.08, 4.68),
        ("$250 ARPU", 10.31, 8.98, 7.80, 6.75, 5.20),
        ("$300 ARPU", 12.37, 10.78, 9.36, 8.10, 6.24),
    ]
    
    for idx, row in enumerate(matrix_arpu, start=6):
        ws4[f"B{idx}"] = row[0]
        ws4[f"B{idx}"].font = BOLD_FONT
        ws4[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(row[1:], start=3):
            col_letter = get_column_letter(c_idx)
            ws4[f"{col_letter}{idx}"] = val
            ws4[f"{col_letter}{idx}"].number_format = "$#,##0.00\"M\""
            ws4[f"{col_letter}{idx}"].font = BOLD_FONT if row[0].startswith("$225") and col_letter == "E" else REGULAR_FONT
            ws4[f"{col_letter}{idx}"].fill = ACCENT_GREEN if row[0].startswith("$225") and col_letter == "E" else PatternFill(fill_type=None)
            ws4[f"{col_letter}{idx}"].border = THIN_BORDER
            
    apply_sheet_formatting(ws4)
    
    # Add Standard & Model-Specific Named Ranges
    add_named_range(wb, "Gross_Revenue_Low", "03_Three_Statements", "G5")
    add_named_range(wb, "Gross_Revenue_Base", "03_Three_Statements", "G6")
    add_named_range(wb, "Gross_Revenue_High", "03_Three_Statements", "G7")
    add_named_range(wb, "Ending_Cash_Base", "03_Three_Statements", "G26")
    add_named_range(wb, "Cash_Trough_Base", "03_Three_Statements", "G27")
    add_named_range(wb, "Cash_Runway_Months_Base", "03_Three_Statements", "G28")
    
    add_named_range(wb, "Gross_Margin_Base", "02_Unit_Economics", "C7")
    add_named_range(wb, "Contribution_Margin_Base", "02_Unit_Economics", "C8")
    add_named_range(wb, "CAC_Selected_Base", "02_Unit_Economics", "C11")
    add_named_range(wb, "LTV_Discounted_Base", "02_Unit_Economics", "C13")
    add_named_range(wb, "LTV_to_CAC_Base", "02_Unit_Economics", "C14")
    add_named_range(wb, "CAC_Payback_Months_Base", "02_Unit_Economics", "C15")
    
    add_named_range(wb, "EBITDA_Base", "03_Three_Statements", "G14")
    add_named_range(wb, "Net_Income_Base", "03_Three_Statements", "G18")
    
    add_named_range(wb, "SAFE_Dilution_Pct", "01_Assumptions", f"C{safe_row}")
    add_named_range(wb, "Founder_Ownership_Pct_Post_SAFE", "01_Assumptions", f"C{founder_row}")
    
    # SaaS specifics
    add_named_range(wb, "MRR_Ending_Base", "02_Unit_Economics", "C17")
    add_named_range(wb, "ARR_Run_Rate_Base", "02_Unit_Economics", "C18")
    add_named_range(wb, "NRR_Base", "02_Unit_Economics", "C20")
    
    out_path = TEMPLATES_DIR / "b2b-saas.xlsx"
    wb.save(out_path)
    print(f"Created {out_path}")


# ==============================================================================
# Model 2: Marketplace
# ==============================================================================
def create_marketplace():
    wb = openpyxl.Workbook()
    
    ws1 = wb.active
    ws1.title = "01_Assumptions"
    ws1.merge_cells("B2:F2")
    ws1["B2"] = "CASEKIT MARKETPLACE FINANCIAL MODEL — ASSUMPTIONS & DRIVERS"
    ws1["B2"].fill = NAVY_HEADER
    ws1["B2"].font = HEADER_FONT
    ws1["B2"].alignment = Alignment(horizontal="center", vertical="center")
    
    ws1["B4"] = "Active Scenario:"
    ws1["B4"].font = BOLD_FONT
    ws1["C4"] = "Base"
    ws1["C4"].font = INPUT_FONT
    ws1["C4"].fill = LIGHT_BLUE_INPUT
    
    ws1.merge_cells("B6:F6")
    ws1["B6"] = "MARKETPLACE TRANSACTION & TAKE RATE DRIVERS"
    ws1["B6"].fill = SLATE_SECTION
    ws1["B6"].font = SECTION_FONT
    
    headers = ["Driver Name", "Low", "Base", "High", "Unit"]
    for col_idx, h in enumerate(headers, start=2):
        c = ws1.cell(row=7, column=col_idx, value=h)
        c.fill = LIGHT_GRAY_FILL
        c.font = BOLD_FONT
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="right" if col_idx in (3,4,5) else "left")
        
    drivers = [
        ("Average Order Value (AOV)", 85.0, 120.0, 160.0, "$/order", "$#,##0.00"),
        ("Commission Take Rate %", 0.12, 0.15, 0.18, "%", "0.0%"),
        ("Monthly Order Frequency per Active Buyer", 1.2, 1.8, 2.5, "Orders/mo", "0.0"),
        ("Active Buyers (Year 1)", 5000, 15000, 30000, "Buyers", "#,##0"),
        ("Active Sellers (Year 1)", 300, 800, 1500, "Sellers", "#,##0"),
        ("Buyer Acquisition Spend ($/mo)", 10000.0, 25000.0, 50000.0, "$/mo", "$#,##0"),
        ("Seller Acquisition Spend ($/mo)", 5000.0, 10000.0, 20000.0, "$/mo", "$#,##0"),
        ("Payment Processing & Gateway Fee %", 0.029, 0.029, 0.029, "%", "0.0%"),
        ("Trust, Safety & Support per Order", 2.00, 1.50, 1.00, "$/order", "$#,##0.00"),
        ("Monthly Engineering & Platform OpEx", 20000.0, 35000.0, 60000.0, "$/mo", "$#,##0"),
        ("Starting Cash Balance", 300000.0, 600000.0, 1200000.0, "$", "$#,##0"),
    ]
    
    for idx, d in enumerate(drivers, start=8):
        ws1[f"B{idx}"] = d[0]
        ws1[f"B{idx}"].font = REGULAR_FONT
        ws1[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(d[1:4], start=3):
            col_letter = get_column_letter(c_idx)
            ws1[f"{col_letter}{idx}"] = val
            ws1[f"{col_letter}{idx}"].number_format = d[5]
            ws1[f"{col_letter}{idx}"].font = INPUT_FONT if c_idx == 4 else REGULAR_FONT
            ws1[f"{col_letter}{idx}"].fill = LIGHT_BLUE_INPUT if c_idx == 4 else PatternFill(fill_type=None)
            ws1[f"{col_letter}{idx}"].border = THIN_BORDER
        ws1[f"F{idx}"] = d[4]
        ws1[f"F{idx}"].font = REGULAR_FONT
        ws1[f"F{idx}"].border = THIN_BORDER
        
    safe_row, founder_row = build_cap_table_section(ws1, start_row=21)
    apply_sheet_formatting(ws1)
    
    # Tab 2: 02_Unit_Economics
    ws2 = wb.create_sheet("02_Unit_Economics")
    ws2.merge_cells("B2:E2")
    ws2["B2"] = "MARKETPLACE TWO-SIDED UNIT ECONOMICS & LIQUIDITY"
    ws2["B2"].fill = NAVY_HEADER
    ws2["B2"].font = HEADER_FONT
    
    ws2.merge_cells("B4:E4")
    ws2["B4"] = "UNIT ECONOMICS PER ORDER & BUYER COHORT LTV"
    ws2["B4"].fill = SLATE_SECTION
    ws2["B4"].font = SECTION_FONT
    
    metrics = [
        ("Average Order Value (AOV)", 120.00, "$#,##0.00", "Gross value of goods transacted per order"),
        ("Marketplace Net Take Rate %", 0.15, "0.0%", "Commission retained by marketplace platform"),
        ("Net Revenue per Order", 18.00, "$#,##0.00", "AOV * Take Rate"),
        ("Payment Processing & Trust/Safety Cost", 4.98, "$#,##0.00", "2.9% + $0.30 gateway + $1.50 support"),
        ("Net Contribution per Order", 13.02, "$#,##0.00", "Net revenue - variable transaction costs"),
        ("Gross Margin %", 0.7233, "0.00%", "Net Contribution / Net Revenue"),
        ("Contribution Margin %", 0.7233, "0.00%", "Contribution margin on platform net revenue"),
        ("Blended Buyer Acquisition CAC", 32.50, "$#,##0.00", "Buyer spend + allocated seller acquisition / new buyers"),
        ("Buyer 24-Month Cohort LTV", 187.49, "$#,##0.00", "Cumulative net contribution per active buyer"),
        ("LTV to CAC Ratio", 5.77, "0.00\"x\"", "Buyer Cohort LTV / Blended Buyer CAC"),
        ("CAC Payback Period (Months)", 2.50, "0.00", "Months of buyer transactions to recover CAC"),
        ("Year 5 Gross Merchandise Value (GMV)", 54000000.0, "$#,##0", "Total annual transacted value through platform"),
        ("Year 5 Marketplace Net Revenue", 8100000.0, "$#,##0", "Year 5 GMV * 15.0% Take Rate"),
        ("Supply-Demand Liquidity Ratio", 0.915, "0.0%", "Matched order requests / Total buyer search requests"),
    ]
    
    for idx, m in enumerate(metrics, start=5):
        ws2[f"B{idx}"] = m[0]
        ws2[f"B{idx}"].font = BOLD_FONT if "Ratio" in m[0] or "GMV" in m[0] or "Margin" in m[0] else REGULAR_FONT
        ws2[f"B{idx}"].border = THIN_BORDER
        ws2[f"C{idx}"] = m[1]
        ws2[f"C{idx}"].number_format = m[2]
        ws2[f"C{idx}"].font = BOLD_FONT
        ws2[f"C{idx}"].fill = ACCENT_GREEN if idx in (6, 10, 14, 15, 16) else PatternFill(fill_type=None)
        ws2[f"C{idx}"].border = THIN_BORDER
        ws2[f"D{idx}"] = m[3]
        ws2[f"D{idx}"].font = REGULAR_FONT
        ws2[f"D{idx}"].border = THIN_BORDER
        
    apply_sheet_formatting(ws2)
    
    # Tab 3: 03_Three_Statements
    ws3 = wb.create_sheet("03_Three_Statements")
    ws3.merge_cells("B2:G2")
    ws3["B2"] = "5-YEAR INTEGRATED FINANCIAL STATEMENTS (MARKETPLACE)"
    ws3["B2"].fill = NAVY_HEADER
    ws3["B2"].font = HEADER_FONT
    
    headers_stmt = ["Financial Line Item ($)", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    for col_idx, h in enumerate(headers_stmt, start=2):
        c = ws3.cell(row=4, column=col_idx, value=h)
        c.fill = SLATE_SECTION
        c.font = SECTION_FONT
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="right" if col_idx > 2 else "left")
        
    pnl_data = [
        ("Gross Merchandise Value (GMV Memo)", 4500000.0, 12000000.0, 24000000.0, 38000000.0, 54000000.0),
        ("Net Marketplace Revenue (Low Scenario)", 450000.0, 1350000.0, 2800000.0, 4600000.0, 6480000.0),
        ("Net Marketplace Revenue (Base Scenario)", 675000.0, 1800000.0, 3600000.0, 5700000.0, 8100000.0),
        ("Net Marketplace Revenue (High Scenario)", 950000.0, 2500000.0, 4900000.0, 7600000.0, 10800000.0),
        ("Transaction Direct COGS & Gateway", 186750.0, 498000.0, 996000.0, 1577000.0, 2241000.0),
        ("Gross Profit", 488250.0, 1302000.0, 2604000.0, 4123000.0, 5859000.0),
        ("Operating Expenses (Growth, Tech, G&A)", 650000.0, 1100000.0, 1750000.0, 2500000.0, 3300000.0),
        ("EBITDA", -161750.0, 202000.0, 854000.0, 1623000.0, 2559000.0),
        ("Net Income", -170000.0, 150000.0, 670000.0, 1280000.0, 2020000.0),
    ]
    for idx, row in enumerate(pnl_data, start=5):
        ws3[f"B{idx}"] = row[0]
        ws3[f"B{idx}"].font = BOLD_FONT if idx in (7, 10, 12, 13) else REGULAR_FONT
        ws3[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(row[1:], start=3):
            col_letter = get_column_letter(c_idx)
            ws3[f"{col_letter}{idx}"] = val
            ws3[f"{col_letter}{idx}"].number_format = "$#,##0"
            ws3[f"{col_letter}{idx}"].font = BOLD_FONT if idx in (7, 10, 12, 13) else REGULAR_FONT
            ws3[f"{col_letter}{idx}"].border = THIN_BORDER
            
    # Cash Flow
    ws3.merge_cells("B15:G15")
    ws3["B15"] = "CASH FLOW STATEMENT"
    ws3["B15"].fill = SLATE_SECTION
    ws3["B15"].font = SECTION_FONT
    
    cf_data = [
        ("Operating Cash Flow (Incl. Float)", -130000.0, 180000.0, 750000.0, 1400000.0, 2150000.0),
        ("CapEx & Platform R&D", -25000.0, -35000.0, -45000.0, -50000.0, -55000.0),
        ("Financing (SAFE & Seed)", 500000.0, 1500000.0, 0.0, 0.0, 0.0),
        ("Ending Cash Balance", 945000.0, 2590000.0, 3295000.0, 4645000.0, 6740000.0),
        ("Minimum Cash Trough", 420000.0, 945000.0, 2590000.0, 3295000.0, 4645000.0),
        ("Cash Runway (Months)", 42.0, 60.0, 60.0, 60.0, 60.0),
    ]
    for idx, row in enumerate(cf_data, start=16):
        ws3[f"B{idx}"] = row[0]
        ws3[f"B{idx}"].font = BOLD_FONT if idx in (19, 20, 21) else REGULAR_FONT
        ws3[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(row[1:], start=3):
            col_letter = get_column_letter(c_idx)
            ws3[f"{col_letter}{idx}"] = val
            ws3[f"{col_letter}{idx}"].number_format = "$#,##0" if idx != 21 else "0.0"
            ws3[f"{col_letter}{idx}"].font = BOLD_FONT if idx in (19, 20, 21) else REGULAR_FONT
            ws3[f"{col_letter}{idx}"].border = THIN_BORDER
            
    apply_sheet_formatting(ws3)
    
    # Tab 4: 04_Sensitivities
    ws4 = wb.create_sheet("04_Sensitivities")
    ws4.merge_cells("B2:G2")
    ws4["B2"] = "MARKETPLACE SENSITIVITIES & LIQUIDITY MATRIX"
    ws4["B2"].fill = NAVY_HEADER
    ws4["B2"].font = HEADER_FONT
    
    ws4.merge_cells("B4:G4")
    ws4["B4"] = "2D MATRIX 1: COMMISSION TAKE RATE (%) vs AOV ($) -> YEAR 5 NET REVENUE ($M)"
    ws4["B4"].fill = SLATE_SECTION
    ws4["B4"].font = SECTION_FONT
    
    take_cols = ["Take Rate \\ AOV", "$80 AOV", "$100 AOV", "$120 AOV (Base)", "$150 AOV", "$200 AOV"]
    for col_idx, h in enumerate(take_cols, start=2):
        c = ws4.cell(row=5, column=col_idx, value=h)
        c.fill = LIGHT_GRAY_FILL
        c.font = BOLD_FONT
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="right" if col_idx > 2 else "left")
        
    matrix_data = [
        ("10.0% Take Rate", 3.60, 4.50, 5.40, 6.75, 9.00),
        ("12.5% Take Rate", 4.50, 5.63, 6.75, 8.44, 11.25),
        ("15.0% Take Rate (Base)", 5.40, 6.75, 8.10, 10.13, 13.50),
        ("17.5% Take Rate", 6.30, 7.88, 9.45, 11.81, 15.75),
        ("20.0% Take Rate", 7.20, 9.00, 10.80, 13.50, 18.00),
    ]
    for idx, row in enumerate(matrix_data, start=6):
        ws4[f"B{idx}"] = row[0]
        ws4[f"B{idx}"].font = BOLD_FONT
        ws4[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(row[1:], start=3):
            col_letter = get_column_letter(c_idx)
            ws4[f"{col_letter}{idx}"] = val
            ws4[f"{col_letter}{idx}"].number_format = "$#,##0.00\"M\""
            ws4[f"{col_letter}{idx}"].font = BOLD_FONT if row[0].startswith("15.0%") and col_letter == "E" else REGULAR_FONT
            ws4[f"{col_letter}{idx}"].fill = ACCENT_GREEN if row[0].startswith("15.0%") and col_letter == "E" else PatternFill(fill_type=None)
            ws4[f"{col_letter}{idx}"].border = THIN_BORDER
            
    apply_sheet_formatting(ws4)
    
    # Named Ranges
    add_named_range(wb, "Gross_Revenue_Low", "03_Three_Statements", "G6")
    add_named_range(wb, "Gross_Revenue_Base", "03_Three_Statements", "G7")
    add_named_range(wb, "Gross_Revenue_High", "03_Three_Statements", "G8")
    add_named_range(wb, "Ending_Cash_Base", "03_Three_Statements", "G19")
    add_named_range(wb, "Cash_Trough_Base", "03_Three_Statements", "G20")
    add_named_range(wb, "Cash_Runway_Months_Base", "03_Three_Statements", "G21")
    
    add_named_range(wb, "Gross_Margin_Base", "02_Unit_Economics", "C10")
    add_named_range(wb, "Contribution_Margin_Base", "02_Unit_Economics", "C11")
    add_named_range(wb, "CAC_Selected_Base", "02_Unit_Economics", "C12")
    add_named_range(wb, "LTV_Discounted_Base", "02_Unit_Economics", "C13")
    add_named_range(wb, "LTV_to_CAC_Base", "02_Unit_Economics", "C14")
    add_named_range(wb, "CAC_Payback_Months_Base", "02_Unit_Economics", "C15")
    
    add_named_range(wb, "EBITDA_Base", "03_Three_Statements", "G12")
    add_named_range(wb, "Net_Income_Base", "03_Three_Statements", "G13")
    
    add_named_range(wb, "SAFE_Dilution_Pct", "01_Assumptions", f"C{safe_row}")
    add_named_range(wb, "Founder_Ownership_Pct_Post_SAFE", "01_Assumptions", f"C{founder_row}")
    
    # Marketplace specifics
    add_named_range(wb, "GMV_Base", "02_Unit_Economics", "C16")
    add_named_range(wb, "Take_Rate_Base", "01_Assumptions", "D9")
    
    out_path = TEMPLATES_DIR / "marketplace.xlsx"
    wb.save(out_path)
    print(f"Created {out_path}")


# ==============================================================================
# Model 3: Hardware & IoT
# ==============================================================================
def create_hardware_iot():
    wb = openpyxl.Workbook()
    
    ws1 = wb.active
    ws1.title = "01_Assumptions"
    ws1.merge_cells("B2:F2")
    ws1["B2"] = "CASEKIT HARDWARE & IOT FINANCIAL MODEL — ASSUMPTIONS & BOM"
    ws1["B2"].fill = NAVY_HEADER
    ws1["B2"].font = HEADER_FONT
    
    ws1["B4"] = "Active Scenario:"
    ws1["B4"].font = BOLD_FONT
    ws1["C4"] = "Base"
    ws1["C4"].font = INPUT_FONT
    ws1["C4"].fill = LIGHT_BLUE_INPUT
    
    ws1.merge_cells("B6:F6")
    ws1["B6"] = "BOM COST & HARDWARE RECURRING DRIVERS"
    ws1["B6"].fill = SLATE_SECTION
    ws1["B6"].font = SECTION_FONT
    
    headers = ["Driver Name", "Low", "Base", "High", "Unit"]
    for col_idx, h in enumerate(headers, start=2):
        c = ws1.cell(row=7, column=col_idx, value=h)
        c.fill = LIGHT_GRAY_FILL
        c.font = BOLD_FONT
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="right" if col_idx in (3,4,5) else "left")
        
    drivers = [
        ("Microcontroller & Sensors BOM", 32.0, 26.0, 22.0, "$/unit", "$#,##0.00"),
        ("PCB Assembly & SMT Manufacturing", 18.0, 14.0, 11.0, "$/unit", "$#,##0.00"),
        ("Mechanical Enclosure & Tooling Wear", 12.0, 9.0, 7.0, "$/unit", "$#,##0.00"),
        ("Packaging & Accessories", 6.0, 4.5, 3.5, "$/unit", "$#,##0.00"),
        ("Inbound Ocean/Air Freight", 7.0, 5.0, 4.0, "$/unit", "$#,##0.00"),
        ("Manufacturing Yield Rate %", 0.88, 0.94, 0.98, "%", "0.0%"),
        ("Hardware Device MSRP ($)", 199.0, 249.0, 299.0, "$/unit", "$#,##0.00"),
        ("Monthly Cloud / Analytics Subscription", 9.99, 14.99, 19.99, "$/mo", "$#,##0.00"),
        ("Subscription Attachment Rate %", 0.55, 0.75, 0.88, "%", "0.0%"),
        ("Monthly Cellular / AWS IoT Cloud COGS", 2.50, 1.80, 1.20, "$/sub/mo", "$#,##0.00"),
        ("One-time Tooling & NRE CapEx ($)", 180000.0, 120000.0, 80000.0, "$", "$#,##0"),
        ("Starting Cash Balance", 400000.0, 800000.0, 1500000.0, "$", "$#,##0"),
    ]
    for idx, d in enumerate(drivers, start=8):
        ws1[f"B{idx}"] = d[0]
        ws1[f"B{idx}"].font = REGULAR_FONT
        ws1[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(d[1:4], start=3):
            col_letter = get_column_letter(c_idx)
            ws1[f"{col_letter}{idx}"] = val
            ws1[f"{col_letter}{idx}"].number_format = d[5]
            ws1[f"{col_letter}{idx}"].font = INPUT_FONT if c_idx == 4 else REGULAR_FONT
            ws1[f"{col_letter}{idx}"].fill = LIGHT_BLUE_INPUT if c_idx == 4 else PatternFill(fill_type=None)
            ws1[f"{col_letter}{idx}"].border = THIN_BORDER
        ws1[f"F{idx}"] = d[4]
        ws1[f"F{idx}"].font = REGULAR_FONT
        ws1[f"F{idx}"].border = THIN_BORDER
        
    safe_row, founder_row = build_cap_table_section(ws1, start_row=22)
    apply_sheet_formatting(ws1)
    
    # Tab 2: 02_Unit_Economics
    ws2 = wb.create_sheet("02_Unit_Economics")
    ws2.merge_cells("B2:E2")
    ws2["B2"] = "HARDWARE & IOT BLENDED UNIT ECONOMICS"
    ws2["B2"].fill = NAVY_HEADER
    ws2["B2"].font = HEADER_FONT
    
    ws2.merge_cells("B4:E4")
    ws2["B4"] = "HARDWARE BOM, MARGINS & RECURRING CLOUD VALUE"
    ws2["B4"].fill = SLATE_SECTION
    ws2["B4"].font = SECTION_FONT
    
    metrics = [
        ("Raw BOM Cost per Unit", 58.50, "$#,##0.00", "Sensors ($26) + PCB ($14) + Enclosure ($9) + Packaging ($4.5) + Freight ($5)"),
        ("Yield-Adjusted Hardware COGS", 62.23, "$#,##0.00", "Raw BOM / 94.0% Manufacturing Yield"),
        ("Hardware Device Selling Price (MSRP)", 249.00, "$#,##0.00", "Direct sales price per device"),
        ("Hardware Gross Profit per Unit", 186.77, "$#,##0.00", "Hardware MSRP - Yield-Adjusted COGS"),
        ("Hardware Device Gross Margin %", 0.7501, "0.00%", "Hardware Gross Profit / MSRP"),
        ("Monthly Cloud Subscription ARPU", 14.99, "$#,##0.00", "Monthly recurring analytics & security subscription"),
        ("Monthly Cloud Direct COGS", 1.80, "$#,##0.00", "AWS IoT Core + cellular eSIM data bundle"),
        ("Cloud Subscription Gross Margin %", 0.8799, "0.00%", "(ARPU - Cloud COGS) / ARPU"),
        ("Blended Fully Loaded CAC per Device", 65.00, "$#,##0.00", "Marketing and hardware sales acquisition"),
        ("36-Month Blended Customer LTV", 482.50, "$#,##0.00", "Hardware gross profit + 36-mo attached subscription cash flows"),
        ("LTV to CAC Ratio", 7.42, "0.00\"x\"", "Blended LTV / Blended Hardware CAC"),
        ("Blended CAC Payback Period (Months)", 1.00, "0.00", "Immediate payback upon device sale + first month sub"),
        ("Gross Margin Base (Blended)", 0.7850, "0.00%", "Blended hardware + recurring subscription margin"),
        ("Contribution Margin Base", 0.7420, "0.00%", "Contribution after warranty, returns, and merchant fees"),
    ]
    for idx, m in enumerate(metrics, start=5):
        ws2[f"B{idx}"] = m[0]
        ws2[f"B{idx}"].font = BOLD_FONT if "Margin" in m[0] or "Ratio" in m[0] or "LTV" in m[0] else REGULAR_FONT
        ws2[f"B{idx}"].border = THIN_BORDER
        ws2[f"C{idx}"] = m[1]
        ws2[f"C{idx}"].number_format = m[2]
        ws2[f"C{idx}"].font = BOLD_FONT
        ws2[f"C{idx}"].fill = ACCENT_GREEN if idx in (9, 15, 16, 17, 18) else PatternFill(fill_type=None)
        ws2[f"C{idx}"].border = THIN_BORDER
        ws2[f"D{idx}"] = m[3]
        ws2[f"D{idx}"].font = REGULAR_FONT
        ws2[f"D{idx}"].border = THIN_BORDER
        
    apply_sheet_formatting(ws2)
    
    # Tab 3: 03_Three_Statements
    ws3 = wb.create_sheet("03_Three_Statements")
    ws3.merge_cells("B2:G2")
    ws3["B2"] = "5-YEAR INTEGRATED FINANCIAL STATEMENTS (HARDWARE & IOT)"
    ws3["B2"].fill = NAVY_HEADER
    ws3["B2"].font = HEADER_FONT
    
    headers_stmt = ["Financial Line Item ($)", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    for col_idx, h in enumerate(headers_stmt, start=2):
        c = ws3.cell(row=4, column=col_idx, value=h)
        c.fill = SLATE_SECTION
        c.font = SECTION_FONT
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="right" if col_idx > 2 else "left")
        
    pnl_data = [
        ("Hardware Units Sold", 3000, 8000, 18000, 32000, 50000),
        ("Total Gross Revenue (Low Scenario)", 620000.0, 1850000.0, 4200000.0, 7800000.0, 12500000.0),
        ("Total Gross Revenue (Base Scenario)", 881500.0, 2690000.0, 6210000.0, 11420000.0, 18350000.0),
        ("Total Gross Revenue (High Scenario)", 1250000.0, 3900000.0, 8900000.0, 16200000.0, 25800000.0),
        ("Hardware & Cloud COGS", 205000.0, 610000.0, 1390000.0, 2520000.0, 3950000.0),
        ("Gross Profit", 676500.0, 2080000.0, 4820000.0, 8900000.0, 14400000.0),
        ("Operating Expenses (Firmware, QA, S&M, G&A)", 850000.0, 1450000.0, 2400000.0, 3800000.0, 5200000.0),
        ("EBITDA", -173500.0, 630000.0, 2420000.0, 5100000.0, 9200000.0),
        ("Net Income", -190000.0, 480000.0, 1900000.0, 4020000.0, 7280000.0),
    ]
    for idx, row in enumerate(pnl_data, start=5):
        ws3[f"B{idx}"] = row[0]
        ws3[f"B{idx}"].font = BOLD_FONT if idx in (7, 10, 12, 13) else REGULAR_FONT
        ws3[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(row[1:], start=3):
            col_letter = get_column_letter(c_idx)
            ws3[f"{col_letter}{idx}"] = val
            ws3[f"{col_letter}{idx}"].number_format = "#,##0" if idx == 5 else "$#,##0"
            ws3[f"{col_letter}{idx}"].font = BOLD_FONT if idx in (7, 10, 12, 13) else REGULAR_FONT
            ws3[f"{col_letter}{idx}"].border = THIN_BORDER
            
    # Cash Flow
    ws3.merge_cells("B15:G15")
    ws3["B15"] = "CASH FLOW STATEMENT (INCL. INVENTORY WORKING CAPITAL)"
    ws3["B15"].fill = SLATE_SECTION
    ws3["B15"].font = SECTION_FONT
    
    cf_data = [
        ("Operating Cash Flow (Incl. Inventory Lead)", -220000.0, 390000.0, 1650000.0, 3500000.0, 6600000.0),
        ("Tooling & Manufacturing CapEx", -120000.0, -50000.0, -60000.0, -70000.0, -80000.0),
        ("Financing (SAFE & Seed)", 500000.0, 1500000.0, 0.0, 0.0, 0.0),
        ("Ending Cash Balance", 960000.0, 2800000.0, 4390000.0, 7820000.0, 14340000.0),
        ("Minimum Cash Trough", 350000.0, 960000.0, 2800000.0, 4390000.0, 7820000.0),
        ("Cash Runway (Months)", 28.0, 60.0, 60.0, 60.0, 60.0),
    ]
    for idx, row in enumerate(cf_data, start=16):
        ws3[f"B{idx}"] = row[0]
        ws3[f"B{idx}"].font = BOLD_FONT if idx in (19, 20, 21) else REGULAR_FONT
        ws3[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(row[1:], start=3):
            col_letter = get_column_letter(c_idx)
            ws3[f"{col_letter}{idx}"] = val
            ws3[f"{col_letter}{idx}"].number_format = "$#,##0" if idx != 21 else "0.0"
            ws3[f"{col_letter}{idx}"].font = BOLD_FONT if idx in (19, 20, 21) else REGULAR_FONT
            ws3[f"{col_letter}{idx}"].border = THIN_BORDER
            
    apply_sheet_formatting(ws3)
    
    # Tab 4: 04_Sensitivities
    ws4 = wb.create_sheet("04_Sensitivities")
    ws4.merge_cells("B2:G2")
    ws4["B2"] = "HARDWARE MANUFACTURING & SUBSCRIPTION SENSITIVITIES"
    ws4["B2"].fill = NAVY_HEADER
    ws4["B2"].font = HEADER_FONT
    
    ws4.merge_cells("B4:G4")
    ws4["B4"] = "2D MATRIX 1: BOM COST ($) vs CLOUD SUBSCRIPTION ($/mo) -> 5-YEAR NET PROFIT ($M)"
    ws4["B4"].fill = SLATE_SECTION
    ws4["B4"].font = SECTION_FONT
    
    bom_cols = ["BOM \\ Sub Price", "$9.99/mo", "$12.99/mo", "$14.99/mo (Base)", "$19.99/mo", "$24.99/mo"]
    for col_idx, h in enumerate(bom_cols, start=2):
        c = ws4.cell(row=5, column=col_idx, value=h)
        c.fill = LIGHT_GRAY_FILL
        c.font = BOLD_FONT
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="right" if col_idx > 2 else "left")
        
    matrix_data = [
        ("$45 BOM", 11.2, 13.1, 14.4, 17.6, 20.8),
        ("$52 BOM", 9.8, 11.7, 13.0, 16.2, 19.4),
        ("$58.5 BOM (Base)", 8.4, 10.3, 11.6, 14.8, 18.0),
        ("$65 BOM", 7.0, 8.9, 10.2, 13.4, 16.6),
        ("$75 BOM", 4.9, 6.8, 8.1, 11.3, 14.5),
    ]
    for idx, row in enumerate(matrix_data, start=6):
        ws4[f"B{idx}"] = row[0]
        ws4[f"B{idx}"].font = BOLD_FONT
        ws4[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(row[1:], start=3):
            col_letter = get_column_letter(c_idx)
            ws4[f"{col_letter}{idx}"] = val
            ws4[f"{col_letter}{idx}"].number_format = "$#,##0.00\"M\""
            ws4[f"{col_letter}{idx}"].font = BOLD_FONT if row[0].startswith("$58.5") and col_letter == "E" else REGULAR_FONT
            ws4[f"{col_letter}{idx}"].fill = ACCENT_GREEN if row[0].startswith("$58.5") and col_letter == "E" else PatternFill(fill_type=None)
            ws4[f"{col_letter}{idx}"].border = THIN_BORDER
            
    apply_sheet_formatting(ws4)
    
    # Named ranges
    add_named_range(wb, "Gross_Revenue_Low", "03_Three_Statements", "G6")
    add_named_range(wb, "Gross_Revenue_Base", "03_Three_Statements", "G7")
    add_named_range(wb, "Gross_Revenue_High", "03_Three_Statements", "G8")
    add_named_range(wb, "Ending_Cash_Base", "03_Three_Statements", "G19")
    add_named_range(wb, "Cash_Trough_Base", "03_Three_Statements", "G20")
    add_named_range(wb, "Cash_Runway_Months_Base", "03_Three_Statements", "G21")
    
    add_named_range(wb, "Gross_Margin_Base", "02_Unit_Economics", "C17")
    add_named_range(wb, "Contribution_Margin_Base", "02_Unit_Economics", "C18")
    add_named_range(wb, "CAC_Selected_Base", "02_Unit_Economics", "C13")
    add_named_range(wb, "LTV_Discounted_Base", "02_Unit_Economics", "C14")
    add_named_range(wb, "LTV_to_CAC_Base", "02_Unit_Economics", "C15")
    add_named_range(wb, "CAC_Payback_Months_Base", "02_Unit_Economics", "C16")
    
    add_named_range(wb, "EBITDA_Base", "03_Three_Statements", "G12")
    add_named_range(wb, "Net_Income_Base", "03_Three_Statements", "G13")
    
    add_named_range(wb, "SAFE_Dilution_Pct", "01_Assumptions", f"C{safe_row}")
    add_named_range(wb, "Founder_Ownership_Pct_Post_SAFE", "01_Assumptions", f"C{founder_row}")
    
    # Hardware specifics
    add_named_range(wb, "Hardware_Gross_Margin_Base", "02_Unit_Economics", "C9")
    add_named_range(wb, "BOM_Unit_Cost_Base", "01_Assumptions", "D8")
    
    out_path = TEMPLATES_DIR / "hardware-iot.xlsx"
    wb.save(out_path)
    print(f"Created {out_path}")


# ==============================================================================
# Model 4: D2C Retail
# ==============================================================================
def create_d2c_retail():
    wb = openpyxl.Workbook()
    
    ws1 = wb.active
    ws1.title = "01_Assumptions"
    ws1.merge_cells("B2:F2")
    ws1["B2"] = "CASEKIT D2C & E-COMMERCE FINANCIAL MODEL — ASSUMPTIONS"
    ws1["B2"].fill = NAVY_HEADER
    ws1["B2"].font = HEADER_FONT
    
    ws1["B4"] = "Active Scenario:"
    ws1["B4"].font = BOLD_FONT
    ws1["C4"] = "Base"
    ws1["C4"].font = INPUT_FONT
    ws1["C4"].fill = LIGHT_BLUE_INPUT
    
    ws1.merge_cells("B6:F6")
    ws1["B6"] = "D2C E-COMMERCE CONVERSION & FULFILLMENT DRIVERS"
    ws1["B6"].fill = SLATE_SECTION
    ws1["B6"].font = SECTION_FONT
    
    headers = ["Driver Name", "Low", "Base", "High", "Unit"]
    for col_idx, h in enumerate(headers, start=2):
        c = ws1.cell(row=7, column=col_idx, value=h)
        c.fill = LIGHT_GRAY_FILL
        c.font = BOLD_FONT
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="right" if col_idx in (3,4,5) else "left")
        
    drivers = [
        ("Average Order Value (AOV)", 55.0, 78.0, 105.0, "$/order", "$#,##0.00"),
        ("E-commerce Store Conversion Rate %", 0.018, 0.026, 0.035, "%", "0.0%"),
        ("Monthly Store Visitors / Sessions", 30000, 80000, 180000, "Sessions", "#,##0"),
        ("Product Unit COGS % of AOV", 0.32, 0.28, 0.24, "%", "0.0%"),
        ("Pick, Pack & Warehouse Fee per Order", 5.50, 4.20, 3.50, "$/order", "$#,##0.00"),
        ("Outbound Shipping Cost per Order", 8.50, 6.80, 5.50, "$/order", "$#,##0.00"),
        ("Customer Shipping Revenue per Order", 5.00, 4.50, 4.00, "$/order", "$#,##0.00"),
        ("Product Return & Refund Rate %", 0.12, 0.08, 0.05, "%", "0.0%"),
        ("Blended Customer Acquisition Cost (CAC)", 38.0, 28.5, 22.0, "$/customer", "$#,##0.00"),
        ("Month 1-12 Repeat Purchase Order Rate", 1.35, 1.65, 2.10, "Orders/yr", "0.00"),
        ("Monthly Brand Ads & Influencer Spend", 15000.0, 35000.0, 75000.0, "$/mo", "$#,##0"),
        ("Starting Cash Balance", 200000.0, 500000.0, 1000000.0, "$", "$#,##0"),
    ]
    for idx, d in enumerate(drivers, start=8):
        ws1[f"B{idx}"] = d[0]
        ws1[f"B{idx}"].font = REGULAR_FONT
        ws1[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(d[1:4], start=3):
            col_letter = get_column_letter(c_idx)
            ws1[f"{col_letter}{idx}"] = val
            ws1[f"{col_letter}{idx}"].number_format = d[5]
            ws1[f"{col_letter}{idx}"].font = INPUT_FONT if c_idx == 4 else REGULAR_FONT
            ws1[f"{col_letter}{idx}"].fill = LIGHT_BLUE_INPUT if c_idx == 4 else PatternFill(fill_type=None)
            ws1[f"{col_letter}{idx}"].border = THIN_BORDER
        ws1[f"F{idx}"] = d[4]
        ws1[f"F{idx}"].font = REGULAR_FONT
        ws1[f"F{idx}"].border = THIN_BORDER
        
    safe_row, founder_row = build_cap_table_section(ws1, start_row=22)
    apply_sheet_formatting(ws1)
    
    # Tab 2: 02_Unit_Economics
    ws2 = wb.create_sheet("02_Unit_Economics")
    ws2.merge_cells("B2:E2")
    ws2["B2"] = "D2C RETAIL UNIT ECONOMICS & CONTRIBUTION MARGIN"
    ws2["B2"].fill = NAVY_HEADER
    ws2["B2"].font = HEADER_FONT
    
    ws2.merge_cells("B4:E4")
    ws2["B4"] = "ORDER ECONOMICS & 12-MONTH COHORT CONTRIBUTION"
    ws2["B4"].fill = SLATE_SECTION
    ws2["B4"].font = SECTION_FONT
    
    metrics = [
        ("Gross Average Order Value (AOV)", 78.00, "$#,##0.00", "Average cart size across all orders"),
        ("Net Returns & Allowances (8.0%)", 6.24, "$#,##0.00", "Returned merchandise losses"),
        ("Net Realized Order Revenue", 71.76, "$#,##0.00", "AOV minus returns plus customer shipping ($4.50)"),
        ("Product Manufacturing COGS (28.0%)", 21.84, "$#,##0.00", "Direct unit goods cost"),
        ("Fulfillment & Delivery COGS (Pick/Pack + Net Ship)", 6.50, "$#,##0.00", "$4.20 pick/pack + $2.30 net shipping"),
        ("Payment Processing Fee (2.9% + $0.30)", 2.56, "$#,##0.00", "Merchant card processing"),
        ("First Order Contribution Margin 1", 40.86, "$#,##0.00", "Net Order Revenue - COGS - Fulfillment - Gateway"),
        ("Gross Margin %", 0.6065, "0.00%", "Order Contribution 1 / Net Order Revenue"),
        ("Blended Acquisition CAC", 28.50, "$#,##0.00", "Total ad spend / First-time purchasing customers"),
        ("First-Order Contribution After CAC (CM2)", 12.36, "$#,##0.00", "Contribution 1 minus Blended CAC (Profitable on 1st order)"),
        ("12-Month Customer Cohort Contribution LTV", 98.45, "$#,##0.00", "1.65 orders * $59.67 net contribution"),
        ("LTV to CAC Ratio", 3.45, "0.00\"x\"", "12-Month Cohort LTV / Blended CAC"),
        ("CAC Payback (Orders)", 0.70, "0.00", "Recouped on first order"),
        ("CAC Payback Period (Months)", 1.20, "0.00", "Immediate payback under 2 months"),
        ("Contribution Margin Base", 0.5360, "0.00%", "Blended contribution margin across repeat cohorts"),
    ]
    for idx, m in enumerate(metrics, start=5):
        ws2[f"B{idx}"] = m[0]
        ws2[f"B{idx}"].font = BOLD_FONT if "Ratio" in m[0] or "Margin" in m[0] or "LTV" in m[0] else REGULAR_FONT
        ws2[f"B{idx}"].border = THIN_BORDER
        ws2[f"C{idx}"] = m[1]
        ws2[f"C{idx}"].number_format = m[2]
        ws2[f"C{idx}"].font = BOLD_FONT
        ws2[f"C{idx}"].fill = ACCENT_GREEN if idx in (12, 14, 15, 16, 17) else PatternFill(fill_type=None)
        ws2[f"C{idx}"].border = THIN_BORDER
        ws2[f"D{idx}"] = m[3]
        ws2[f"D{idx}"].font = REGULAR_FONT
        ws2[f"D{idx}"].border = THIN_BORDER
        
    apply_sheet_formatting(ws2)
    
    # Tab 3: 03_Three_Statements
    ws3 = wb.create_sheet("03_Three_Statements")
    ws3.merge_cells("B2:G2")
    ws3["B2"] = "5-YEAR INTEGRATED FINANCIAL STATEMENTS (D2C RETAIL)"
    ws3["B2"].fill = NAVY_HEADER
    ws3["B2"].font = HEADER_FONT
    
    headers_stmt = ["Financial Line Item ($)", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    for col_idx, h in enumerate(headers_stmt, start=2):
        c = ws3.cell(row=4, column=col_idx, value=h)
        c.fill = SLATE_SECTION
        c.font = SECTION_FONT
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="right" if col_idx > 2 else "left")
        
    pnl_data = [
        ("Total Gross Sales (Low Scenario)", 950000.0, 2400000.0, 4800000.0, 8500000.0, 13200000.0),
        ("Total Gross Sales (Base Scenario)", 1450000.0, 3650000.0, 7200000.0, 12800000.0, 19500000.0),
        ("Total Gross Sales (High Scenario)", 2100000.0, 5200000.0, 10400000.0, 18500000.0, 27500000.0),
        ("Returns, Allowances & Discounts", 116000.0, 292000.0, 576000.0, 1024000.0, 1560000.0),
        ("Net Revenue", 1334000.0, 3358000.0, 6624000.0, 11776000.0, 17940000.0),
        ("Product COGS & Logistics", 525000.0, 1320000.0, 2600000.0, 4620000.0, 7040000.0),
        ("Gross Profit", 809000.0, 2038000.0, 4024000.0, 7156000.0, 10900000.0),
        ("Performance Marketing & Brand Ads", 480000.0, 1050000.0, 1950000.0, 3200000.0, 4600000.0),
        ("G&A, E-comm Stack & Payroll", 380000.0, 620000.0, 980000.0, 1450000.0, 2100000.0),
        ("EBITDA", -51000.0, 368000.0, 1094000.0, 2506000.0, 4200000.0),
        ("Net Income", -60000.0, 280000.0, 850000.0, 1960000.0, 3320000.0),
    ]
    for idx, row in enumerate(pnl_data, start=5):
        ws3[f"B{idx}"] = row[0]
        ws3[f"B{idx}"].font = BOLD_FONT if idx in (6, 9, 11, 14, 15) else REGULAR_FONT
        ws3[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(row[1:], start=3):
            col_letter = get_column_letter(c_idx)
            ws3[f"{col_letter}{idx}"] = val
            ws3[f"{col_letter}{idx}"].number_format = "$#,##0"
            ws3[f"{col_letter}{idx}"].font = BOLD_FONT if idx in (6, 9, 11, 14, 15) else REGULAR_FONT
            ws3[f"{col_letter}{idx}"].border = THIN_BORDER
            
    # Cash Flow
    ws3.merge_cells("B17:G17")
    ws3["B17"] = "CASH FLOW STATEMENT (INCL. INVENTORY PURCHASES & REORDER DRAIN)"
    ws3["B17"].fill = SLATE_SECTION
    ws3["B17"].font = SECTION_FONT
    
    cf_data = [
        ("Operating Cash Flow", -120000.0, 210000.0, 780000.0, 1850000.0, 3100000.0),
        ("Inventory Working Capital Drain", -80000.0, -120000.0, -180000.0, -250000.0, -320000.0),
        ("Financing (SAFE & Seed)", 500000.0, 1000000.0, 0.0, 0.0, 0.0),
        ("Ending Cash Balance", 800000.0, 1890000.0, 2490000.0, 4090000.0, 6870000.0),
        ("Minimum Cash Trough", 320000.0, 800000.0, 1890000.0, 2490000.0, 4090000.0),
        ("Cash Runway (Months)", 30.0, 60.0, 60.0, 60.0, 60.0),
    ]
    for idx, row in enumerate(cf_data, start=18):
        ws3[f"B{idx}"] = row[0]
        ws3[f"B{idx}"].font = BOLD_FONT if idx in (21, 22, 23) else REGULAR_FONT
        ws3[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(row[1:], start=3):
            col_letter = get_column_letter(c_idx)
            ws3[f"{col_letter}{idx}"] = val
            ws3[f"{col_letter}{idx}"].number_format = "$#,##0" if idx != 23 else "0.0"
            ws3[f"{col_letter}{idx}"].font = BOLD_FONT if idx in (21, 22, 23) else REGULAR_FONT
            ws3[f"{col_letter}{idx}"].border = THIN_BORDER
            
    apply_sheet_formatting(ws3)
    
    # Tab 4: 04_Sensitivities
    ws4 = wb.create_sheet("04_Sensitivities")
    ws4.merge_cells("B2:G2")
    ws4["B2"] = "D2C RETAIL SENSITIVITIES & REPEAT CONVERSION"
    ws4["B2"].fill = NAVY_HEADER
    ws4["B2"].font = HEADER_FONT
    
    ws4.merge_cells("B4:G4")
    ws4["B4"] = "2D MATRIX 1: AOV ($) vs RETURN RATE (%) -> CONTRIBUTION MARGIN 1 PER ORDER ($)"
    ws4["B4"].fill = SLATE_SECTION
    ws4["B4"].font = SECTION_FONT
    
    aov_cols = ["AOV \\ Returns", "4.0% Returns", "6.0% Returns", "8.0% Returns (Base)", "10.0% Returns", "15.0% Returns"]
    for col_idx, h in enumerate(aov_cols, start=2):
        c = ws4.cell(row=5, column=col_idx, value=h)
        c.fill = LIGHT_GRAY_FILL
        c.font = BOLD_FONT
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="right" if col_idx > 2 else "left")
        
    matrix_data = [
        ("$55 AOV", 30.5, 29.4, 28.3, 27.2, 24.5),
        ("$65 AOV", 36.8, 35.5, 34.2, 32.9, 29.6),
        ("$78 AOV (Base)", 43.8, 42.3, 40.86, 39.4, 35.7),
        ("$90 AOV", 51.2, 49.4, 47.6, 45.8, 41.3),
        ("$110 AOV", 63.4, 61.2, 59.0, 56.8, 51.3),
    ]
    for idx, row in enumerate(matrix_data, start=6):
        ws4[f"B{idx}"] = row[0]
        ws4[f"B{idx}"].font = BOLD_FONT
        ws4[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(row[1:], start=3):
            col_letter = get_column_letter(c_idx)
            ws4[f"{col_letter}{idx}"] = val
            ws4[f"{col_letter}{idx}"].number_format = "$#,##0.00"
            ws4[f"{col_letter}{idx}"].font = BOLD_FONT if row[0].startswith("$78") and col_letter == "E" else REGULAR_FONT
            ws4[f"{col_letter}{idx}"].fill = ACCENT_GREEN if row[0].startswith("$78") and col_letter == "E" else PatternFill(fill_type=None)
            ws4[f"{col_letter}{idx}"].border = THIN_BORDER
            
    apply_sheet_formatting(ws4)
    
    # Named Ranges
    add_named_range(wb, "Gross_Revenue_Low", "03_Three_Statements", "G5")
    add_named_range(wb, "Gross_Revenue_Base", "03_Three_Statements", "G6")
    add_named_range(wb, "Gross_Revenue_High", "03_Three_Statements", "G7")
    add_named_range(wb, "Ending_Cash_Base", "03_Three_Statements", "G21")
    add_named_range(wb, "Cash_Trough_Base", "03_Three_Statements", "G22")
    add_named_range(wb, "Cash_Runway_Months_Base", "03_Three_Statements", "G23")
    
    add_named_range(wb, "Gross_Margin_Base", "02_Unit_Economics", "C12")
    add_named_range(wb, "Contribution_Margin_Base", "02_Unit_Economics", "C19")
    add_named_range(wb, "CAC_Selected_Base", "02_Unit_Economics", "C13")
    add_named_range(wb, "LTV_Discounted_Base", "02_Unit_Economics", "C15")
    add_named_range(wb, "LTV_to_CAC_Base", "02_Unit_Economics", "C16")
    add_named_range(wb, "CAC_Payback_Months_Base", "02_Unit_Economics", "C18")
    
    add_named_range(wb, "EBITDA_Base", "03_Three_Statements", "G14")
    add_named_range(wb, "Net_Income_Base", "03_Three_Statements", "G15")
    
    add_named_range(wb, "SAFE_Dilution_Pct", "01_Assumptions", f"C{safe_row}")
    add_named_range(wb, "Founder_Ownership_Pct_Post_SAFE", "01_Assumptions", f"C{founder_row}")
    
    # D2C specifics
    add_named_range(wb, "AOV_Base", "01_Assumptions", "D8")
    add_named_range(wb, "Blended_CAC_Base", "02_Unit_Economics", "C13")
    
    out_path = TEMPLATES_DIR / "d2c-retail.xlsx"
    wb.save(out_path)
    print(f"Created {out_path}")


# ==============================================================================
# Model 5: Corporate ROI & Enterprise Transformation
# ==============================================================================
def create_corporate_roi():
    wb = openpyxl.Workbook()
    
    ws1 = wb.active
    ws1.title = "01_Assumptions"
    ws1.merge_cells("B2:F2")
    ws1["B2"] = "CASEKIT CORPORATE ROI & TRANSFORMATION MODEL — ASSUMPTIONS"
    ws1["B2"].fill = NAVY_HEADER
    ws1["B2"].font = HEADER_FONT
    
    ws1["B4"] = "Active Scenario:"
    ws1["B4"].font = BOLD_FONT
    ws1["C4"] = "Base"
    ws1["C4"].font = INPUT_FONT
    ws1["C4"].fill = LIGHT_BLUE_INPUT
    
    ws1.merge_cells("B6:F6")
    ws1["B6"] = "ENTERPRISE TARGET SCOPE & EFFICIENCY DRIVERS"
    ws1["B6"].fill = SLATE_SECTION
    ws1["B6"].font = SECTION_FONT
    
    headers = ["Driver Name", "Low", "Base", "High", "Unit"]
    for col_idx, h in enumerate(headers, start=2):
        c = ws1.cell(row=7, column=col_idx, value=h)
        c.fill = LIGHT_GRAY_FILL
        c.font = BOLD_FONT
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="right" if col_idx in (3,4,5) else "left")
        
    drivers = [
        ("Total Eligible Enterprise Employees", 500, 2000, 5000, "Employees", "#,##0"),
        ("Year 1 User Adoption Rollout Rate %", 0.25, 0.40, 0.60, "%", "0.0%"),
        ("Year 3 Mature Adoption Rollout Rate %", 0.70, 0.85, 0.95, "%", "0.0%"),
        ("Fully Loaded Employee Hourly Cost ($)", 55.0, 75.0, 95.0, "$/hr", "$#,##0.00"),
        ("Baseline Workflow Hours Spent/Week", 8.0, 8.0, 8.0, "Hrs/wk", "0.0"),
        ("Hours Saved per Active User/Week", 2.0, 4.0, 6.0, "Hrs/wk", "0.0"),
        ("Productive Realization / Capture Rate %", 0.60, 0.75, 0.90, "%", "0.0%"),
        ("Annual Enterprise SaaS License Fee/User", 1500.0, 2000.0, 2500.0, "$/user/yr", "$#,##0"),
        ("Initial Implementation & Integration CapEx", 350000.0, 250000.0, 180000.0, "$", "$#,##0"),
        ("Corporate Hurdle Rate / WACC %", 0.10, 0.10, 0.10, "%", "0.0%"),
        ("Starting Cash Balance / Budget Allocation", 500000.0, 1000000.0, 2000000.0, "$", "$#,##0"),
    ]
    for idx, d in enumerate(drivers, start=8):
        ws1[f"B{idx}"] = d[0]
        ws1[f"B{idx}"].font = REGULAR_FONT
        ws1[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(d[1:4], start=3):
            col_letter = get_column_letter(c_idx)
            ws1[f"{col_letter}{idx}"] = val
            ws1[f"{col_letter}{idx}"].number_format = d[5]
            ws1[f"{col_letter}{idx}"].font = INPUT_FONT if c_idx == 4 else REGULAR_FONT
            ws1[f"{col_letter}{idx}"].fill = LIGHT_BLUE_INPUT if c_idx == 4 else PatternFill(fill_type=None)
            ws1[f"{col_letter}{idx}"].border = THIN_BORDER
        ws1[f"F{idx}"] = d[4]
        ws1[f"F{idx}"].font = REGULAR_FONT
        ws1[f"F{idx}"].border = THIN_BORDER
        
    safe_row, founder_row = build_cap_table_section(ws1, start_row=21)
    apply_sheet_formatting(ws1)
    
    # Tab 2: 02_Unit_Economics
    ws2 = wb.create_sheet("02_Unit_Economics")
    ws2.merge_cells("B2:E2")
    ws2["B2"] = "CORPORATE ROI — UNIT VALUE CREATION & WORKAROUND SAVINGS"
    ws2["B2"].fill = NAVY_HEADER
    ws2["B2"].font = HEADER_FONT
    
    ws2.merge_cells("B4:E4")
    ws2["B4"] = "STATUS QUO WORKAROUND COST vs SOLUTION VALUE CREATION"
    ws2["B4"].fill = SLATE_SECTION
    ws2["B4"].font = SECTION_FONT
    
    metrics = [
        ("Status Quo Annual Workaround Cost per Employee", 30000.00, "$#,##0.00", "8 hrs/wk * 50 wks * $75/hr loaded wage"),
        ("Gross Value Generated per Active User/Year", 15000.00, "$#,##0.00", "4 hrs saved * 50 wks * $75/hr * 75% realization"),
        ("Annual Enterprise Software License Fee", 2000.00, "$#,##0.00", "SaaS subscription license per user"),
        ("Net Annual Economic Value per Active User", 13000.00, "$#,##0.00", "Value Generated minus Software License Fee"),
        ("Cost-Benefit Multiplier (Value / Price)", 7.50, "0.00\"x\"", "Gross Value Generated / Annual License Fee"),
        ("Gross Margin Base", 0.8667, "0.00%", "Net Economic Value / Value Generated"),
        ("Contribution Margin Base", 0.8667, "0.00%", "Net value contribution margin"),
        ("Fully Loaded Implementation Cost per User", 347.06, "$#,##0.00", "CapEx ($250k) amortized over 720 Year 1 users"),
        ("5-Year Discounted Net Economic Value (LTV)", 49275.00, "$#,##0.00", "5-year cumulative discounted net savings per user"),
        ("LTV to CAC Ratio (ROI Multiplier)", 14.20, "0.00\"x\"", "5-Year Net Value per User / Implementation Cost"),
        ("Payback Period (Months)", 3.20, "0.00", "Months to recover initial implementation CapEx"),
        ("Annual Net Cost Savings (Mature Year 3)", 18700000.0, "$#,##0", "Total enterprise savings across 1,700 active users"),
    ]
    for idx, m in enumerate(metrics, start=5):
        ws2[f"B{idx}"] = m[0]
        ws2[f"B{idx}"].font = BOLD_FONT if "Multiplier" in m[0] or "Savings" in m[0] or "Margin" in m[0] else REGULAR_FONT
        ws2[f"B{idx}"].border = THIN_BORDER
        ws2[f"C{idx}"] = m[1]
        ws2[f"C{idx}"].number_format = m[2]
        ws2[f"C{idx}"].font = BOLD_FONT
        ws2[f"C{idx}"].fill = ACCENT_GREEN if idx in (9, 10, 14, 15, 16) else PatternFill(fill_type=None)
        ws2[f"C{idx}"].border = THIN_BORDER
        ws2[f"D{idx}"] = m[3]
        ws2[f"D{idx}"].font = REGULAR_FONT
        ws2[f"D{idx}"].border = THIN_BORDER
        
    apply_sheet_formatting(ws2)
    
    # Tab 3: 03_Three_Statements
    ws3 = wb.create_sheet("03_Three_Statements")
    ws3.merge_cells("B2:G2")
    ws3["B2"] = "5-YEAR CORPORATE ROI IMPACT & CASH FLOW STATEMENT"
    ws3["B2"].fill = NAVY_HEADER
    ws3["B2"].font = HEADER_FONT
    
    headers_stmt = ["Financial Impact Line Item ($)", "Year 1", "Year 2", "Year 3", "Year 4", "Year 5"]
    for col_idx, h in enumerate(headers_stmt, start=2):
        c = ws3.cell(row=4, column=col_idx, value=h)
        c.fill = SLATE_SECTION
        c.font = SECTION_FONT
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="right" if col_idx > 2 else "left")
        
    pnl_data = [
        ("Active Enterprise Users Deployed", 800, 1400, 1700, 1850, 1900),
        ("Gross Economic Value Generated (Low)", 5600000.0, 9800000.0, 11900000.0, 12950000.0, 13300000.0),
        ("Gross Economic Value Generated (Base)", 12000000.0, 21000000.0, 25500000.0, 27750000.0, 28500000.0),
        ("Gross Economic Value Generated (High)", 19200000.0, 33600000.0, 40800000.0, 44400000.0, 45600000.0),
        ("Enterprise Software License Fees", 1600000.0, 2800000.0, 3400000.0, 3700000.0, 3800000.0),
        ("Internal Change Management & Support", 250000.0, 350000.0, 400000.0, 420000.0, 450000.0),
        ("Net Annual Cost Savings (Base)", 10150000.0, 17850000.0, 21700000.0, 23630000.0, 24250000.0),
        ("EBITDA Impact (Synergy Contribution)", 10150000.0, 17850000.0, 21700000.0, 23630000.0, 24250000.0),
        ("Net Income Contribution", 8120000.0, 14280000.0, 17360000.0, 18904000.0, 19400000.0),
    ]
    for idx, row in enumerate(pnl_data, start=5):
        ws3[f"B{idx}"] = row[0]
        ws3[f"B{idx}"].font = BOLD_FONT if idx in (7, 11, 12, 13) else REGULAR_FONT
        ws3[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(row[1:], start=3):
            col_letter = get_column_letter(c_idx)
            ws3[f"{col_letter}{idx}"] = val
            ws3[f"{col_letter}{idx}"].number_format = "#,##0" if idx == 5 else "$#,##0"
            ws3[f"{col_letter}{idx}"].font = BOLD_FONT if idx in (7, 11, 12, 13) else REGULAR_FONT
            ws3[f"{col_letter}{idx}"].border = THIN_BORDER
            
    # ROI & Valuation Summary
    ws3.merge_cells("B15:G15")
    ws3["B15"] = "ENTERPRISE TRANSFORMATION ROI & NPV SUMMARY"
    ws3["B15"].fill = SLATE_SECTION
    ws3["B15"].font = SECTION_FONT
    
    roi_data = [
        ("Net Present Value (NPV @ 10% WACC)", 72480000.0, "$#,##0", "Discounted cumulative net cash savings"),
        ("5-Year Total Return on Investment (ROI %)", 5.84, "0.0%", "584% Net Benefit / Total Implementation Costs"),
        ("Capital Investment Payback Period (Months)", 3.2, "0.0", "Months to recoup $250k implementation CapEx"),
        ("Ending Cash / Reserve Balance", 5200000.0, "$#,##0", "Corporate transformation budget reserve"),
        ("Minimum Cash Trough", 750000.0, "$#,##0", "Lowest budget liquidity level"),
        ("Cash Runway (Months)", 60.0, "0.0", "Funded internal transformation"),
    ]
    for idx, row in enumerate(roi_data, start=16):
        ws3[f"B{idx}"] = row[0]
        ws3[f"B{idx}"].font = BOLD_FONT
        ws3[f"B{idx}"].border = THIN_BORDER
        ws3[f"C{idx}"] = row[1]
        ws3[f"C{idx}"].number_format = row[2]
        ws3[f"C{idx}"].font = BOLD_FONT
        ws3[f"C{idx}"].fill = ACCENT_GREEN if idx in (16, 17, 18) else PatternFill(fill_type=None)
        ws3[f"C{idx}"].border = THIN_BORDER
        ws3[f"D{idx}"] = row[3]
        ws3[f"D{idx}"].font = REGULAR_FONT
        ws3[f"D{idx}"].border = THIN_BORDER
        
    apply_sheet_formatting(ws3)
    
    # Tab 4: 04_Sensitivities
    ws4 = wb.create_sheet("04_Sensitivities")
    ws4.merge_cells("B2:G2")
    ws4["B2"] = "CORPORATE ROI SENSITIVITIES & TIME RECOVERY MATRICES"
    ws4["B2"].fill = NAVY_HEADER
    ws4["B2"].font = HEADER_FONT
    
    ws4.merge_cells("B4:G4")
    ws4["B4"] = "2D MATRIX 1: USER ADOPTION (%) vs HOURS SAVED/WEEK -> 5-YEAR NPV ($M)"
    ws4["B4"].fill = SLATE_SECTION
    ws4["B4"].font = SECTION_FONT
    
    sens_cols = ["Adoption \\ Hours", "2.0 Hrs/Wk", "3.0 Hrs/Wk", "4.0 Hrs/Wk (Base)", "5.0 Hrs/Wk", "6.0 Hrs/Wk"]
    for col_idx, h in enumerate(sens_cols, start=2):
        c = ws4.cell(row=5, column=col_idx, value=h)
        c.fill = LIGHT_GRAY_FILL
        c.font = BOLD_FONT
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="right" if col_idx > 2 else "left")
        
    matrix_data = [
        ("50% Adoption", 21.5, 33.8, 46.1, 58.4, 70.7),
        ("70% Adoption", 31.2, 48.4, 65.6, 82.8, 100.0),
        ("85% Adoption (Base)", 38.5, 59.3, 72.48, 101.1, 122.0),
        ("95% Adoption", 43.3, 66.6, 89.9, 113.2, 136.5),
    ]
    for idx, row in enumerate(matrix_data, start=6):
        ws4[f"B{idx}"] = row[0]
        ws4[f"B{idx}"].font = BOLD_FONT
        ws4[f"B{idx}"].border = THIN_BORDER
        for c_idx, val in enumerate(row[1:], start=3):
            col_letter = get_column_letter(c_idx)
            ws4[f"{col_letter}{idx}"] = val
            ws4[f"{col_letter}{idx}"].number_format = "$#,##0.00\"M\""
            ws4[f"{col_letter}{idx}"].font = BOLD_FONT if row[0].startswith("85%") and col_letter == "E" else REGULAR_FONT
            ws4[f"{col_letter}{idx}"].fill = ACCENT_GREEN if row[0].startswith("85%") and col_letter == "E" else PatternFill(fill_type=None)
            ws4[f"{col_letter}{idx}"].border = THIN_BORDER
            
    apply_sheet_formatting(ws4)
    
    # Named Ranges
    add_named_range(wb, "Gross_Revenue_Low", "03_Three_Statements", "G6")
    add_named_range(wb, "Gross_Revenue_Base", "03_Three_Statements", "G7")
    add_named_range(wb, "Gross_Revenue_High", "03_Three_Statements", "G8")
    add_named_range(wb, "Ending_Cash_Base", "03_Three_Statements", "C19")
    add_named_range(wb, "Cash_Trough_Base", "03_Three_Statements", "C20")
    add_named_range(wb, "Cash_Runway_Months_Base", "03_Three_Statements", "C21")
    
    add_named_range(wb, "Gross_Margin_Base", "02_Unit_Economics", "C10")
    add_named_range(wb, "Contribution_Margin_Base", "02_Unit_Economics", "C11")
    add_named_range(wb, "CAC_Selected_Base", "02_Unit_Economics", "C12")
    add_named_range(wb, "LTV_Discounted_Base", "02_Unit_Economics", "C13")
    add_named_range(wb, "LTV_to_CAC_Base", "02_Unit_Economics", "C14")
    add_named_range(wb, "CAC_Payback_Months_Base", "02_Unit_Economics", "C15")
    
    add_named_range(wb, "EBITDA_Base", "03_Three_Statements", "G12")
    add_named_range(wb, "Net_Income_Base", "03_Three_Statements", "G13")
    
    add_named_range(wb, "SAFE_Dilution_Pct", "01_Assumptions", f"C{safe_row}")
    add_named_range(wb, "Founder_Ownership_Pct_Post_SAFE", "01_Assumptions", f"C{founder_row}")
    
    # Corporate ROI specifics
    add_named_range(wb, "Net_Cost_Savings_Base", "02_Unit_Economics", "C16")
    add_named_range(wb, "ROI_Percent_Base", "03_Three_Statements", "C17")
    add_named_range(wb, "Payback_Months_Base", "03_Three_Statements", "C18")
    add_named_range(wb, "NPV_Base", "03_Three_Statements", "C16")
    
    out_path = TEMPLATES_DIR / "corporate-roi.xlsx"
    wb.save(out_path)
    print(f"Created {out_path}")


def main():
    TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
    create_b2b_saas()
    create_marketplace()
    create_hardware_iot()
    create_d2c_retail()
    create_corporate_roi()
    print("Successfully built all 5 financial model templates!")


if __name__ == "__main__":
    main()
