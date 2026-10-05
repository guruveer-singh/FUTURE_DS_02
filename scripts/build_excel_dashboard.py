import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference, Series

df = pd.read_csv('data/telco_customer_churn_cleaned.csv')

wb = openpyxl.Workbook()
# remove default sheet
wb.remove(wb.active)

# Color Palette
NAVY_HEADER = '0F172A'       # Dark Slate / Navy
BLUE_ACCENT = '2563EB'       # Royal Blue
TEAL_ACCENT = '0D9488'       # Teal
RED_ALERT = 'E11D48'         # Crimson Red
CARD_BG = 'F8FAFC'           # Light Gray / Off-white
BORDER_COLOR = 'CBD5E1'      # Slate 300
HEADER_BG = '1E293B'         # Slate 800
ZEBRA_BG = 'F1F5F9'          # Slate 100

thin_border = Border(
    left=Side(style='thin', color=BORDER_COLOR),
    right=Side(style='thin', color=BORDER_COLOR),
    top=Side(style='thin', color=BORDER_COLOR),
    bottom=Side(style='thin', color=BORDER_COLOR)
)

card_border = Border(
    left=Side(style='medium', color='94A3B8'),
    right=Side(style='medium', color='94A3B8'),
    top=Side(style='medium', color='94A3B8'),
    bottom=Side(style='medium', color='94A3B8')
)

# ==============================================================================
# TAB 1: EXECUTIVE DASHBOARD
# ==============================================================================
ws_dash = wb.create_sheet(title='Executive Dashboard')
ws_dash.views.sheetView[0].showGridLines = True

# Title Banner (Rows 1-3, Cols A-N)
ws_dash.merge_cells('A1:N2')
banner = ws_dash['A1']
banner.value = "🎯 EXECUTIVE CUSTOMER RETENTION & CHURN DASHBOARD"
banner.font = Font(name='Segoe UI', size=16, bold=True, color='FFFFFF')
banner.fill = PatternFill(start_color=HEADER_BG, end_color=HEADER_BG, fill_type='solid')
banner.alignment = Alignment(horizontal='center', vertical='center')

ws_dash.merge_cells('A3:N3')
sub_banner = ws_dash['A3']
sub_banner.value = "SaaS & Subscription Retention Analytics | Dataset: 7,043 Active/Churned Customer Accounts | Monthly Run-rate: $456.1K MRR"
sub_banner.font = Font(name='Segoe UI', size=10, italic=True, color='E2E8F0')
sub_banner.fill = PatternFill(start_color='334155', end_color='334155', fill_type='solid')
sub_banner.alignment = Alignment(horizontal='center', vertical='center')

# KPI CARDS (Row 5 to 7)
# KPI 1: Total Customer Base (B5:C7)
# KPI 2: Overall Churn Rate (E5:F7)
# KPI 3: Monthly Revenue Lost (MRR) (H5:I7)
# KPI 4: 1-Year Retention Rate (K5:L7)
# KPI 5: Avg Customer Lifetime (tenure) (M5:N7)

def create_kpi_card(ws, start_col, start_row, end_col, end_row, title, value, subtext, val_color='1E293B'):
    # Header
    ws.merge_cells(start_row=start_row, start_column=start_col, end_row=start_row, end_column=end_col)
    c_title = ws.cell(row=start_row, column=start_col)
    c_title.value = title
    c_title.font = Font(name='Segoe UI', size=9, bold=True, color='475569')
    c_title.alignment = Alignment(horizontal='center', vertical='center')
    c_title.fill = PatternFill(start_color=CARD_BG, end_color=CARD_BG, fill_type='solid')
    
    # Value
    ws.merge_cells(start_row=start_row+1, start_column=start_col, end_row=start_row+1, end_column=end_col)
    c_val = ws.cell(row=start_row+1, column=start_col)
    c_val.value = value
    c_val.font = Font(name='Segoe UI', size=18, bold=True, color=val_color)
    c_val.alignment = Alignment(horizontal='center', vertical='center')
    c_val.fill = PatternFill(start_color=CARD_BG, end_color=CARD_BG, fill_type='solid')
    
    # Subtext
    ws.merge_cells(start_row=start_row+2, start_column=start_col, end_row=start_row+2, end_column=end_col)
    c_sub = ws.cell(row=start_row+2, column=start_col)
    c_sub.value = subtext
    c_sub.font = Font(name='Segoe UI', size=8, italic=True, color='64748B')
    c_sub.alignment = Alignment(horizontal='center', vertical='center')
    c_sub.fill = PatternFill(start_color=CARD_BG, end_color=CARD_BG, fill_type='solid')
    
    for r in range(start_row, end_row+1):
        for c in range(start_col, end_col+1):
            ws.cell(row=r, column=c).border = thin_border

create_kpi_card(ws_dash, 1, 5, 3, 7, "TOTAL CUSTOMER BASE", "7,043", "5,174 Retained | 1,869 Churned", '0F172A')
create_kpi_card(ws_dash, 4, 5, 6, 7, "OVERALL CHURN RATE", "26.54%", "Snapshot Rate | Reference <8%", 'E11D48')
create_kpi_card(ws_dash, 7, 5, 9, 7, "MONTHLY MRR LOSS", "$139,131", "Annualized Run-Rate: $1.67M / yr", 'E11D48')
create_kpi_card(ws_dash, 10, 5, 11, 7, "YEAR-1 RETENTION RATE", "52.56%", "47.4% churn in first 12 months", 'D97706')
create_kpi_card(ws_dash, 12, 5, 14, 7, "MEAN OBSERVED TENURE", "32.4 Mos", "Snapshot active base (right-censored)", '0D9488')

# SECTION 1: Summary Tables for Native Charts (Row 9 to 25)
# Table A: Churn by Contract (Cols A to D)
ws_dash.merge_cells('A9:D9')
sec_a = ws_dash['A9']
sec_a.value = "1. CHURN & REVENUE LOSS BY CONTRACT TYPE"
sec_a.font = Font(name='Segoe UI', size=10, bold=True, color='FFFFFF')
sec_a.fill = PatternFill(start_color='1E293B', end_color='1E293B', fill_type='solid')

headers_a = ["Contract Type", "Accounts", "Churn Rate", "Lost MRR"]
for col_idx, h in enumerate(headers_a, start=1):
    c = ws_dash.cell(row=10, column=col_idx, value=h)
    c.font = Font(name='Segoe UI', size=9, bold=True, color='FFFFFF')
    c.fill = PatternFill(start_color='334155', end_color='334155', fill_type='solid')
    c.alignment = Alignment(horizontal='center')
    c.border = thin_border

contract_data = [
    ["Month-to-month", 3875, 0.4271, 120847.10],
    ["One year", 1473, 0.1127, 14118.45],
    ["Two year", 1695, 0.0283, 4165.30]
]
for row_idx, row in enumerate(contract_data, start=11):
    for col_idx, val in enumerate(row, start=1):
        c = ws_dash.cell(row=row_idx, column=col_idx, value=val)
        c.font = Font(name='Segoe UI', size=9)
        c.border = thin_border
        if col_idx == 1:
            c.alignment = Alignment(horizontal='left')
        elif col_idx == 2:
            c.alignment = Alignment(horizontal='right')
            c.number_format = '#,##0'
        elif col_idx == 3:
            c.alignment = Alignment(horizontal='right')
            c.number_format = '0.0%'
            if val > 0.3:
                c.font = Font(name='Segoe UI', size=9, bold=True, color='BE123C')
        elif col_idx == 4:
            c.alignment = Alignment(horizontal='right')
            c.number_format = '$#,##0'

# Table B: Churn by Tenure Bracket (Cols F to I)
ws_dash.merge_cells('F9:I9')
sec_b = ws_dash['F9']
sec_b.value = "2. TENURE BRACKET CHURN DECAY (SNAPSHOT)"
sec_b.font = Font(name='Segoe UI', size=10, bold=True, color='FFFFFF')
sec_b.fill = PatternFill(start_color='1E293B', end_color='1E293B', fill_type='solid')

headers_b = ["Tenure Bracket", "Customers", "Churn Rate", "Avg Spend ($)"]
for col_idx, h in enumerate(headers_b, start=6):
    c = ws_dash.cell(row=10, column=col_idx, value=h)
    c.font = Font(name='Segoe UI', size=9, bold=True, color='FFFFFF')
    c.fill = PatternFill(start_color='334155', end_color='334155', fill_type='solid')
    c.alignment = Alignment(horizontal='center')
    c.border = thin_border

cohort_data = [
    ["0-12 Months", 2186, 0.4744, 275.23],
    ["13-24 Months", 1024, 0.2871, 1126.26],
    ["25-36 Months", 832, 0.2163, 1990.20],
    ["37-48 Months", 762, 0.1903, 2827.47],
    ["49-60 Months", 832, 0.1442, 3848.13],
    ["61-72 Months", 1407, 0.0661, 5180.67]
]
for row_idx, row in enumerate(cohort_data, start=11):
    for col_idx, val in enumerate(row, start=6):
        c = ws_dash.cell(row=row_idx, column=col_idx, value=val)
        c.font = Font(name='Segoe UI', size=9)
        c.border = thin_border
        if col_idx == 6:
            c.alignment = Alignment(horizontal='left')
        elif col_idx == 7:
            c.alignment = Alignment(horizontal='right')
            c.number_format = '#,##0'
        elif col_idx == 8:
            c.alignment = Alignment(horizontal='right')
            c.number_format = '0.0%'
            if val > 0.3:
                c.font = Font(name='Segoe UI', size=9, bold=True, color='BE123C')
        elif col_idx == 9:
            c.alignment = Alignment(horizontal='right')
            c.number_format = '$#,##0'

# Table C: Payment Method Friction (Cols K to N)
ws_dash.merge_cells('K9:N9')
sec_c = ws_dash['K9']
sec_c.value = "3. PAYMENT METHOD FRICTION & CHURN"
sec_c.font = Font(name='Segoe UI', size=10, bold=True, color='FFFFFF')
sec_c.fill = PatternFill(start_color='1E293B', end_color='1E293B', fill_type='solid')

headers_c = ["Payment Method", "Customers", "Churn Rate", "Billing Type"]
for col_idx, h in enumerate(headers_c, start=11):
    c = ws_dash.cell(row=10, column=col_idx, value=h)
    c.font = Font(name='Segoe UI', size=9, bold=True, color='FFFFFF')
    c.fill = PatternFill(start_color='334155', end_color='334155', fill_type='solid')
    c.alignment = Alignment(horizontal='center')
    c.border = thin_border

pay_data = [
    ["Electronic check", 2365, 0.4529, "Manual (High Risk)"],
    ["Mailed check", 1612, 0.1911, "Manual"],
    ["Bank transfer (auto)", 1544, 0.1671, "Automated (Sticky)"],
    ["Credit card (auto)", 1522, 0.1524, "Automated (Sticky)"]
]
for row_idx, row in enumerate(pay_data, start=11):
    for col_idx, val in enumerate(row, start=11):
        c = ws_dash.cell(row=row_idx, column=col_idx, value=val)
        c.font = Font(name='Segoe UI', size=9)
        c.border = thin_border
        if col_idx == 11 or col_idx == 14:
            c.alignment = Alignment(horizontal='left')
        elif col_idx == 12:
            c.alignment = Alignment(horizontal='right')
            c.number_format = '#,##0'
        elif col_idx == 13:
            c.alignment = Alignment(horizontal='right')
            c.number_format = '0.0%'
            if val > 0.3:
                c.font = Font(name='Segoe UI', size=9, bold=True, color='BE123C')

# Add Native Excel Bar Charts below tables!
# Chart 1: Contract Churn Rate
chart_contract = BarChart()
chart_contract.type = "col"
chart_contract.style = 10
chart_contract.title = "Churn Rate by Contract Type"
chart_contract.y_axis.title = "Churn %"
chart_contract.x_axis.title = "Contract"
chart_contract.y_axis.number_format = '0%'
chart_contract.legend = None
chart_contract.width = 15
chart_contract.height = 9

data_ref1 = Reference(ws_dash, min_col=3, min_row=10, max_row=13)
cats_ref1 = Reference(ws_dash, min_col=1, min_row=11, max_row=13)
chart_contract.add_data(data_ref1, titles_from_data=True)
chart_contract.set_categories(cats_ref1)
ws_dash.add_chart(chart_contract, "A18")

# Chart 2: Cohort Churn Decay
chart_cohort = BarChart()
chart_cohort.type = "col"
chart_cohort.style = 11
chart_cohort.title = "Churn Decay Across Tenure Brackets (Snapshot)"
chart_cohort.y_axis.title = "Churn %"
chart_cohort.x_axis.title = "Tenure Bracket"
chart_cohort.y_axis.number_format = '0%'
chart_cohort.legend = None
chart_cohort.width = 17
chart_cohort.height = 9

data_ref2 = Reference(ws_dash, min_col=8, min_row=10, max_row=16)
cats_ref2 = Reference(ws_dash, min_col=6, min_row=11, max_row=16)
chart_cohort.add_data(data_ref2, titles_from_data=True)
chart_cohort.set_categories(cats_ref2)
ws_dash.add_chart(chart_cohort, "F18")

# Chart 3: Payment Method Churn
chart_pay = BarChart()
chart_pay.type = "bar"
chart_pay.style = 13
chart_pay.title = "Churn Rate by Payment Channel"
chart_pay.x_axis.title = "Churn %"
chart_pay.y_axis.title = "Channel"
chart_pay.x_axis.number_format = '0%'
chart_pay.legend = None
chart_pay.width = 16
chart_pay.height = 9

data_ref3 = Reference(ws_dash, min_col=13, min_row=10, max_row=14)
cats_ref3 = Reference(ws_dash, min_col=11, min_row=11, max_row=14)
chart_pay.add_data(data_ref3, titles_from_data=True)
chart_pay.set_categories(cats_ref3)
ws_dash.add_chart(chart_pay, "K18")

# Strategic Takeaways Box (Row 36 to 48)
ws_dash.merge_cells('A36:N36')
takeaway_title = ws_dash['A36']
takeaway_title.value = "🚀 EXECUTIVE RETENTION PLAYBOOK & STRATEGIC RECOMMENDATIONS"
takeaway_title.font = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
takeaway_title.fill = PatternFill(start_color='0F172A', end_color='0F172A', fill_type='solid')

takeaways = [
    ("1. Convert Month-to-Month into Annual Contracts (The $120.8K/mo MRR Opportunity):",
     "Month-to-month contracts exhibit an alarming 42.7% churn rate and represent 86.9% of all lost revenue. Implement a 15-20% discount on annual commitments or offer 2 months free to migrate high-risk accounts. Moving just 20% of M2M users to 1-year contracts saves ~$24,000/mo ($288K/yr)."),
    
    ("2. Tackle the 'First 12 Months' Onboarding Cliff (47.4% First-Year Churn):",
     "Over 55.5% of churn occurs within the first 12 months. Introduce a structured Day 1-90 customer onboarding cadence with proactive digital touchpoints, automated health scoring, and milestone rewards at Month 6 and Month 12."),
    
    ("3. Resolve the Fiber Optic Paradox via Mandatory Support Bundling:",
     "Fiber optic users churn at 41.9% ($91.50/mo), but fiber customers WITH Tech Support churn at only 22.6% (a 54% reduction!). Bundle basic 24/7 tech support and online security directly into fiber tier pricing instead of treating them as unbundled add-ons."),
    
    ("4. Phase Out Electronic Check Billing in Favor of Automated Payment Incentives:",
     "Customers paying via Electronic Check churn at 45.3% vs. 15.2% for Auto-Credit Card and 16.7% for Auto-Bank Transfer. Provide a $5/month recurring statement credit for enrolling in Auto-Pay to immediately slash involuntary churn.")
]

curr_r = 37
for heading, body in takeaways:
    ws_dash.merge_cells(start_row=curr_r, start_column=1, end_row=curr_r, end_column=14)
    h_cell = ws_dash.cell(row=curr_r, column=1, value=heading)
    h_cell.font = Font(name='Segoe UI', size=9.5, bold=True, color='0F766E')
    h_cell.fill = PatternFill(start_color='F1F5F9', end_color='F1F5F9', fill_type='solid')
    curr_r += 1
    
    ws_dash.merge_cells(start_row=curr_r, start_column=1, end_row=curr_r+1, end_column=14)
    b_cell = ws_dash.cell(row=curr_r, column=1, value=body)
    b_cell.font = Font(name='Segoe UI', size=8.5, color='334155')
    b_cell.alignment = Alignment(wrap_text=True, vertical='center')
    curr_r += 2

# Adjust column widths for Executive Dashboard
col_widths = {'A': 18, 'B': 12, 'C': 12, 'D': 14, 'E': 4, 'F': 16, 'G': 12, 'H': 12, 'I': 14, 'J': 4, 'K': 22, 'L': 12, 'M': 14, 'N': 18}
for col_letter, width in col_widths.items():
    ws_dash.column_dimensions[col_letter].width = width

# ==============================================================================
# TAB 2: COHORT RETENTION TABLE
# ==============================================================================
ws_cohort = wb.create_sheet(title='Cohort Retention Table')
ws_cohort.views.sheetView[0].showGridLines = True

ws_cohort.merge_cells('A1:J2')
c_banner = ws_cohort['A1']
c_banner.value = "📊 DETAILED TENURE BRACKET RETENTION & CHURN MATRIX (SNAPSHOT)"
c_banner.font = Font(name='Segoe UI', size=14, bold=True, color='FFFFFF')
c_banner.fill = PatternFill(start_color=HEADER_BG, end_color=HEADER_BG, fill_type='solid')
c_banner.alignment = Alignment(horizontal='center', vertical='center')

cohort_matrix_headers = [
    "Tenure Cohort", "Total Customers", "Active / Retained", "Churned Accounts",
    "Retention Rate", "Churn Rate", "Avg Monthly Fee", "Total Cumulative Revenue", "Lost MRR", "Risk Status"
]
for col_idx, h in enumerate(cohort_matrix_headers, start=1):
    c = ws_cohort.cell(row=4, column=col_idx, value=h)
    c.font = Font(name='Segoe UI', size=9.5, bold=True, color='FFFFFF')
    c.fill = PatternFill(start_color='1E293B', end_color='1E293B', fill_type='solid')
    c.alignment = Alignment(horizontal='center', vertical='center')
    c.border = thin_border

cohort_matrix_data = [
    ["0-12 Months", 2186, 1149, 1037, 0.5256, 0.4744, 56.10, 601651.90, 68954.25, "Critical (Onboarding Cliff)"],
    ["13-24 Months", 1024, 730, 294, 0.7129, 0.2871, 61.36, 1153287.70, 23081.65, "High (Contract Expiry 1)"],
    ["25-36 Months", 832, 652, 180, 0.7837, 0.2163, 65.58, 1655845.80, 15167.95, "Moderate (Established)"],
    ["37-48 Months", 762, 617, 145, 0.8097, 0.1903, 66.32, 2154534.55, 12294.55, "Moderate (Loyal)"],
    ["49-60 Months", 832, 712, 120, 0.8558, 0.1442, 70.55, 3201646.30, 10581.90, "Low (Highly Retained)"],
    ["61-72 Months", 1407, 1314, 93, 0.9339, 0.0661, 75.95, 7289202.45, 9050.55, "Minimal (VIP Super-Sticky)"]
]

for row_idx, row in enumerate(cohort_matrix_data, start=5):
    for col_idx, val in enumerate(row, start=1):
        c = ws_cohort.cell(row=row_idx, column=col_idx, value=val)
        c.font = Font(name='Segoe UI', size=9)
        c.border = thin_border
        if col_idx == 1:
            c.alignment = Alignment(horizontal='left')
        elif col_idx in [2, 3, 4]:
            c.alignment = Alignment(horizontal='right')
            c.number_format = '#,##0'
        elif col_idx in [5, 6]:
            c.alignment = Alignment(horizontal='right')
            c.number_format = '0.0%'
        elif col_idx in [7, 8, 9]:
            c.alignment = Alignment(horizontal='right')
            c.number_format = '$#,##0.00'
        elif col_idx == 10:
            c.alignment = Alignment(horizontal='center')
            if "Critical" in val:
                c.fill = PatternFill(start_color='FEE2E2', end_color='FEE2E2', fill_type='solid')
                c.font = Font(name='Segoe UI', size=9, bold=True, color='991B1B')
            elif "High" in val:
                c.fill = PatternFill(start_color='FEF3C7', end_color='FEF3C7', fill_type='solid')
                c.font = Font(name='Segoe UI', size=9, bold=True, color='92400E')
            elif "Minimal" in val or "Low" in val:
                c.fill = PatternFill(start_color='DCFCE7', end_color='DCFCE7', fill_type='solid')
                c.font = Font(name='Segoe UI', size=9, bold=True, color='166534')

# Summary row for Cohorts
ws_cohort.cell(row=11, column=1, value="TOTAL / PORTFOLIO AVERAGE").font = Font(name='Segoe UI', size=9.5, bold=True)
ws_cohort.cell(row=11, column=2, value="=SUM(B5:B10)").number_format = '#,##0'
ws_cohort.cell(row=11, column=3, value="=SUM(C5:C10)").number_format = '#,##0'
ws_cohort.cell(row=11, column=4, value="=SUM(D5:D10)").number_format = '#,##0'
ws_cohort.cell(row=11, column=5, value="=C11/B11").number_format = '0.0%'
ws_cohort.cell(row=11, column=6, value="=D11/B11").number_format = '0.0%'
ws_cohort.cell(row=11, column=7, value="=AVERAGE(G5:G10)").number_format = '$#,##0.00'
ws_cohort.cell(row=11, column=8, value="=SUM(H5:H10)").number_format = '$#,##0.00'
ws_cohort.cell(row=11, column=9, value="=SUM(I5:I10)").number_format = '$#,##0.00'
ws_cohort.cell(row=11, column=10, value="Portfolio Baseline")

for c_i in range(1, 11):
    cell = ws_cohort.cell(row=11, column=c_i)
    cell.font = Font(name='Segoe UI', size=9.5, bold=True)
    cell.border = thin_border
    cell.fill = PatternFill(start_color='E2E8F0', end_color='E2E8F0', fill_type='solid')

# Methodological Footnote
ws_cohort.merge_cells('A13:J13')
fn_cell = ws_cohort['A13']
fn_cell.value = "📌 Methodological Note: Cross-sectional snapshot of 7,043 customer accounts. Active accounts are right-censored; tenure brackets represent account age distribution rather than longitudinal cohort tracking."
fn_cell.font = Font(name='Segoe UI', size=8.5, italic=True, color='475569')
fn_cell.fill = PatternFill(start_color='F8FAFC', end_color='F8FAFC', fill_type='solid')
fn_cell.alignment = Alignment(horizontal='left', vertical='center')

# Auto-width for Cohort sheet
for col in ws_cohort.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws_cohort.column_dimensions[col_letter].width = max(max_len + 3, 14)

# ==============================================================================
# TAB 3: CUSTOMER RISK SCORING & ACTION PLAYBOOK
# ==============================================================================
ws_risk = wb.create_sheet(title='Churn Risk Scoring')
ws_risk.views.sheetView[0].showGridLines = True

ws_risk.merge_cells('A1:I2')
r_banner = ws_risk['A1']
r_banner.value = "🔍 CUSTOMER CHURN RISK SCORING & PROACTIVE INTERVENTION PLAYBOOK"
r_banner.font = Font(name='Segoe UI', size=14, bold=True, color='FFFFFF')
r_banner.fill = PatternFill(start_color=HEADER_BG, end_color=HEADER_BG, fill_type='solid')
r_banner.alignment = Alignment(horizontal='center', vertical='center')

risk_headers = ["Risk Tier", "Account Count", "% of Base", "Historical Churn Rate", "Active Accounts at Risk", "MRR at Risk ($/mo)", "Key Profile Characteristics", "Primary Intervention Action"]
for col_idx, h in enumerate(risk_headers, start=1):
    c = ws_risk.cell(row=4, column=col_idx, value=h)
    c.font = Font(name='Segoe UI', size=9.5, bold=True, color='FFFFFF')
    c.fill = PatternFill(start_color='1E293B', end_color='1E293B', fill_type='solid')
    c.alignment = Alignment(horizontal='center', vertical='center')
    c.border = thin_border

# Group by Churn_Risk_Tier
tier_stats = df.groupby('Churn_Risk_Tier').agg(
    Total=('customerID', 'count'),
    Churned=('Churn_Num', 'sum'),
    Churn_Rate=('Churn_Num', 'mean'),
    Active=('Churn_Num', lambda x: (x == 0).sum()),
    Active_MRR=('MonthlyCharges', lambda x: x[df.loc[x.index, 'Churn_Num'] == 0].sum())
).reindex(['High Risk', 'Medium Risk', 'Low Risk'])

risk_playbook_data = [
    ["High Risk", int(tier_stats.loc['High Risk', 'Total']), 
     tier_stats.loc['High Risk', 'Total']/len(df),
     tier_stats.loc['High Risk', 'Churn_Rate'],
     int(tier_stats.loc['High Risk', 'Active']),
     tier_stats.loc['High Risk', 'Active_MRR'],
     "Month-to-month + Tenure <= 12 mo + Electronic check + Fiber w/o support",
     "Immediate CS outreach, Auto-pay $5 discount, Offer 1-year contract lock at 15% discount"],
    
    ["Medium Risk", int(tier_stats.loc['Medium Risk', 'Total']), 
     tier_stats.loc['Medium Risk', 'Total']/len(df),
     tier_stats.loc['Medium Risk', 'Churn_Rate'],
     int(tier_stats.loc['Medium Risk', 'Active']),
     tier_stats.loc['Medium Risk', 'Active_MRR'],
     "Month-to-month with tenure > 12 mo OR unbundled Fiber Optic users",
     "Free Tech Support trial, in-app product onboarding guides, bundle incentives"],
    
    ["Low Risk", int(tier_stats.loc['Low Risk', 'Total']), 
     tier_stats.loc['Low Risk', 'Total']/len(df),
     tier_stats.loc['Low Risk', 'Churn_Rate'],
     int(tier_stats.loc['Low Risk', 'Active']),
     tier_stats.loc['Low Risk', 'Active_MRR'],
     "1-Year or 2-Year Contract + Automated payment + Multiple service add-ons",
     "Loyalty rewards, referral bonuses, upsell to higher bandwidth/enterprise streaming"]
]

for row_idx, row in enumerate(risk_playbook_data, start=5):
    for col_idx, val in enumerate(row, start=1):
        c = ws_risk.cell(row=row_idx, column=col_idx, value=val)
        c.font = Font(name='Segoe UI', size=9)
        c.border = thin_border
        if col_idx == 1:
            c.alignment = Alignment(horizontal='center')
            if val == "High Risk":
                c.fill = PatternFill(start_color='FEE2E2', end_color='FEE2E2', fill_type='solid')
                c.font = Font(name='Segoe UI', size=9.5, bold=True, color='991B1B')
            elif val == "Medium Risk":
                c.fill = PatternFill(start_color='FEF3C7', end_color='FEF3C7', fill_type='solid')
                c.font = Font(name='Segoe UI', size=9.5, bold=True, color='92400E')
            else:
                c.fill = PatternFill(start_color='DCFCE7', end_color='DCFCE7', fill_type='solid')
                c.font = Font(name='Segoe UI', size=9.5, bold=True, color='166534')
        elif col_idx in [2, 5]:
            c.alignment = Alignment(horizontal='right')
            c.number_format = '#,##0'
        elif col_idx in [3, 4]:
            c.alignment = Alignment(horizontal='right')
            c.number_format = '0.0%'
        elif col_idx == 6:
            c.alignment = Alignment(horizontal='right')
            c.number_format = '$#,##0'
        elif col_idx in [7, 8]:
            c.alignment = Alignment(horizontal='left')

for col in ws_risk.columns:
    max_len = max(len(str(cell.value or '')) for cell in col)
    col_letter = get_column_letter(col[0].column)
    ws_risk.column_dimensions[col_letter].width = max(max_len + 3, 14)

# ==============================================================================
# TAB 4: CLEANED CUSTOMER DATA (7,043 Records)
# ==============================================================================
ws_data = wb.create_sheet(title='Cleaned Customer Data')
ws_data.views.sheetView[0].showGridLines = True

data_cols = [
    'customerID', 'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'tenure', 'Tenure_Cohort',
    'PhoneService', 'MultipleLines', 'InternetService', 'OnlineSecurity', 'OnlineBackup',
    'DeviceProtection', 'TechSupport', 'StreamingTV', 'StreamingMovies', 'Contract',
    'PaperlessBilling', 'PaymentMethod', 'MonthlyCharges', 'TotalCharges', 'Churn', 'Churn_Risk_Tier'
]

# Write headers
for col_idx, col_name in enumerate(data_cols, start=1):
    c = ws_data.cell(row=1, column=col_idx, value=col_name)
    c.font = Font(name='Segoe UI', size=9, bold=True, color='FFFFFF')
    c.fill = PatternFill(start_color='1E293B', end_color='1E293B', fill_type='solid')
    c.alignment = Alignment(horizontal='center')

# Write data rows
for r_idx, row in df[data_cols].iterrows():
    row_num = r_idx + 2
    for c_idx, val in enumerate(row, start=1):
        c = ws_data.cell(row=row_num, column=c_idx, value=val)
        c.font = Font(name='Segoe UI', size=8.5)
        if data_cols[c_idx-1] in ['MonthlyCharges', 'TotalCharges']:
            c.number_format = '$#,##0.00'
            c.alignment = Alignment(horizontal='right')
        elif data_cols[c_idx-1] == 'tenure':
            c.number_format = '#,##0'
            c.alignment = Alignment(horizontal='right')
        elif data_cols[c_idx-1] == 'Churn':
            c.alignment = Alignment(horizontal='center')
            if val == 'Yes':
                c.font = Font(name='Segoe UI', size=8.5, bold=True, color='BE123C')
            else:
                c.font = Font(name='Segoe UI', size=8.5, color='047857')
        else:
            c.alignment = Alignment(horizontal='left')

# Auto-filter on data table
ws_data.auto_filter.ref = f"A1:{get_column_letter(len(data_cols))}{len(df)+1}"

# Set column widths for Data sheet
for col in ws_data.columns:
    col_letter = get_column_letter(col[0].column)
    ws_data.column_dimensions[col_letter].width = 13

# Save workbook
wb.save('Customer_Retention_Dashboard.xlsx')
print('Customer_Retention_Dashboard.xlsx created successfully!')
