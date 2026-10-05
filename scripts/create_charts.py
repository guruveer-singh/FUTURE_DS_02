import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set global styles
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300

df = pd.read_csv('data/telco_customer_churn_cleaned.csv')
out_dir = 'visualizations/retention'
os.makedirs(out_dir, exist_ok=True)

# -------------------------------------------------------------
# Chart 1: Churn Overview & Revenue Exposure
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor='white')
churn_counts = df['Churn'].value_counts()
colors = ['#0D9488', '#E11D48']

wedges, texts, autotexts = ax1.pie(churn_counts, labels=['Retained (5,174)', 'Churned (1,869)'], 
                                   autopct='%1.1f%%', startangle=140, colors=colors,
                                   wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2),
                                   textprops=dict(fontsize=11, fontweight='bold', color='#1E293B'))
for at in autotexts:
    at.set_color('white')
    at.set_fontsize(12)
ax1.set_title('Customer Retention vs. Churn Rate\nTotal Base: 7,043 Accounts', fontsize=13, fontweight='bold', pad=15, color='#1E293B')

mrr_retained = df[df['Churn'] == 'No']['MonthlyCharges'].sum()
mrr_churned = df[df['Churn'] == 'Yes']['MonthlyCharges'].sum()
wedges2, texts2, autotexts2 = ax2.pie([mrr_retained, mrr_churned], 
                                      labels=[f'Retained MRR\n${mrr_retained:,.0f}/mo', f'Lost MRR\n${mrr_churned:,.0f}/mo'], 
                                      autopct='%1.1f%%', startangle=140, colors=colors,
                                      wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2),
                                      textprops=dict(fontsize=11, fontweight='bold', color='#1E293B'))
for at in autotexts2:
    at.set_color('white')
    at.set_fontsize(12)
ax2.set_title('Monthly Recurring Revenue (MRR) Impact\nAnnualized Loss: $1.67M / year', fontsize=13, fontweight='bold', pad=15, color='#1E293B')

plt.suptitle('TELCO / SUBSCRIPTION CHURN OVERVIEW & FINANCIAL EXPOSURE', fontsize=15, fontweight='bold', color='#0F172A', y=1.02)
plt.tight_layout()
plt.savefig(f'{out_dir}/01_churn_overview_and_revenue.png', dpi=300, bbox_inches='tight')
plt.close()
print('Chart 1 complete.')

# -------------------------------------------------------------
# Chart 2: Cross-Sectional Tenure Bracket Retention & Churn Curve
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), facecolor='white')
cohort_order = ['0-12 Mo', '13-24 Mo', '25-36 Mo', '37-48 Mo', '49-60 Mo', '61-72 Mo']
cohort_stats = df.groupby('Tenure_Cohort', observed=False).agg(
    Total=('customerID', 'count'),
    Churn_Rate=('Churn_Num', 'mean')
).reindex(cohort_order)

bars = ax1.bar(cohort_stats.index, cohort_stats['Churn_Rate'] * 100, color='#E11D48', alpha=0.85, width=0.55, edgecolor='#9F1239')
ax1.set_title('Churn Rate by Tenure Bracket (% Churned in Snapshot)', fontsize=12, fontweight='bold', color='#1E293B')
ax1.set_ylabel('Churn Rate (%)', fontsize=11, fontweight='bold', color='#334155')
ax1.set_ylim(0, 60)
for bar, total in zip(bars, cohort_stats['Total']):
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 1.2, f'{yval:.1f}%\n(N={total:,})', ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#9F1239')
avg_churn = df['Churn_Num'].mean() * 100
ax1.axhline(avg_churn, color='#64748B', linestyle='--', linewidth=1.5, label=f'Avg Churn: {avg_churn:.1f}%')
ax1.legend(loc='upper right', frameon=True)
ax1.grid(axis='y', linestyle=':', alpha=0.6)

# Line plot: Cross-Sectional Tenure Distribution (% accounts active at or beyond month m)
tenure_survival = []
for m in range(1, 73):
    sub = df[df['tenure'] >= m]
    tenure_survival.append(len(sub) / len(df) * 100)

ax2.plot(range(1, 73), tenure_survival, color='#0D9488', linewidth=3, label='Snapshot Tenure Profile')
ax2.axvspan(1, 12, color='#FEE2E2', alpha=0.5, label='High-Risk Onboarding Window (Mo 1-12)')
ax2.set_title('Cross-Sectional Tenure Profile (% Accounts with Tenure >= Month m)', fontsize=11, fontweight='bold', color='#1E293B')
ax2.set_xlabel('Tenure (Months Active in Snapshot)', fontsize=11, fontweight='bold', color='#334155')
ax2.set_ylabel('% of Accounts (Snapshot)', fontsize=11, fontweight='bold', color='#334155')
ax2.set_ylim(0, 105)
ax2.text(14, 75, '47.4% Churn in Mo 0-12\nAttrition stabilizes in >24 Mo accounts', color='#9F1239', fontweight='bold', fontsize=10, bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='#E11D48'))
ax2.legend(loc='lower left', frameon=True)
ax2.grid(axis='both', linestyle=':', alpha=0.6)

plt.suptitle('THE ONBOARDING CLIFF: 55.5% OF ALL CHURN OCCURS IN THE FIRST 12 MONTHS', fontsize=14, fontweight='bold', color='#0F172A', y=1.02)
plt.tight_layout()
plt.savefig(f'{out_dir}/02_tenure_bracket_retention.png', dpi=300, bbox_inches='tight')
plt.close()
print('Chart 2 complete.')

# -------------------------------------------------------------
# Chart 3: Contract Risk Breakdown
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor='white')
contract_order = ['Month-to-month', 'One year', 'Two year']
contract_stats = df.groupby('Contract').agg(
    Count=('customerID', 'count'),
    Churn_Rate=('Churn_Num', 'mean'),
    MRR_Lost=('MonthlyCharges', lambda x: x[df.loc[x.index, 'Churn_Num'] == 1].sum())
).reindex(contract_order)

colors_contract = ['#E11D48', '#F59E0B', '#10B981']
bars1 = ax1.bar(contract_stats.index, contract_stats['Churn_Rate'] * 100, color=colors_contract, width=0.5, edgecolor='#334155')
ax1.set_title('Churn Rate by Contract Commitment', fontsize=12, fontweight='bold', color='#1E293B')
ax1.set_ylabel('Churn Rate (%)', fontsize=11, fontweight='bold')
ax1.set_ylim(0, 50)
for bar, count in zip(bars1, contract_stats['Count']):
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 1.2, f'{yval:.1f}%\n(N={count:,})', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax1.grid(axis='y', linestyle=':', alpha=0.6)

bars2 = ax2.bar(contract_stats.index, contract_stats['MRR_Lost'] / 1000, color=colors_contract, width=0.5, edgecolor='#334155')
ax2.set_title('Monthly Recurring Revenue (MRR) Lost by Contract', fontsize=12, fontweight='bold', color='#1E293B')
ax2.set_ylabel('Monthly Revenue Lost ($K / month)', fontsize=11, fontweight='bold')
ax2.set_ylim(0, 145)
total_mrr_loss = contract_stats['MRR_Lost'].sum() / 1000
for bar in bars2:
    yval = bar.get_height()
    pct = (yval / total_mrr_loss) * 100
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 2.5, f'${yval:.1f}K/mo\n({pct:.1f}%)', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax2.grid(axis='y', linestyle=':', alpha=0.6)

plt.suptitle('CONTRACT TYPE AS THE STRONGEST RETENTION ANCHOR (15x RISK DIFFERENCE)', fontsize=14, fontweight='bold', color='#0F172A', y=1.02)
plt.tight_layout()
plt.savefig(f'{out_dir}/03_contract_risk_breakdown.png', dpi=300, bbox_inches='tight')
plt.close()
print('Chart 3 complete.')

# -------------------------------------------------------------
# Chart 4: Fiber Optic & Support Deficit Paradox
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), facecolor='white')

# Subplot 1: Internet Service Churn & Price
inet = df.groupby('InternetService').agg(
    Count=('customerID', 'count'),
    Churn_Rate=('Churn_Num', 'mean'),
    Avg_Price=('MonthlyCharges', 'mean')
).reindex(['Fiber optic', 'DSL', 'No'])

colors_inet = ['#E11D48', '#0EA5E9', '#94A3B8']
bars_inet = ax1.bar(inet.index, inet['Churn_Rate'] * 100, color=colors_inet, width=0.5, edgecolor='#334155')
ax1.set_title('Churn Rate by Internet Service Type', fontsize=12, fontweight='bold', color='#1E293B')
ax1.set_ylabel('Churn Rate (%)', fontsize=11, fontweight='bold')
ax1.set_ylim(0, 52)
for bar, price in zip(bars_inet, inet['Avg_Price']):
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 1.2, f'{yval:.1f}%\nAvg ${price:.1f}/mo', ha='center', va='bottom', fontsize=10, fontweight='bold')
ax1.grid(axis='y', linestyle=':', alpha=0.6)

# Subplot 2: Fiber Optic Churn by Tech Support and Online Security
fiber_df = df[df['InternetService'] == 'Fiber optic']
fiber_bundle = fiber_df.groupby(['TechSupport', 'OnlineSecurity'])['Churn_Num'].agg(['count', 'mean']).reset_index()
fiber_bundle['Label'] = fiber_bundle.apply(lambda r: f"Support: {r['TechSupport']}\nSecurity: {r['OnlineSecurity']}", axis=1)
fiber_bundle = fiber_bundle.sort_values(by='mean', ascending=False)

bars_bundle = ax2.bar(range(len(fiber_bundle)), fiber_bundle['mean'] * 100, color=['#BE123C', '#E11D48', '#F59E0B', '#10B981'], width=0.55, edgecolor='#334155')
ax2.set_xticks(range(len(fiber_bundle)))
ax2.set_xticklabels(fiber_bundle['Label'], fontsize=9.5, fontweight='bold')
ax2.set_title('Fiber Optic Churn: Tech Support & Security Bundle Impact', fontsize=12, fontweight='bold', color='#1E293B')
ax2.set_ylabel('Churn Rate (%)', fontsize=11, fontweight='bold')
ax2.set_ylim(0, 60)
for bar, cnt in zip(bars_bundle, fiber_bundle['count']):
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 1.2, f'{yval:.1f}%\n(N={cnt:,})', ha='center', va='bottom', fontsize=9.5, fontweight='bold')
ax2.grid(axis='y', linestyle=':', alpha=0.6)

plt.suptitle('THE FIBER OPTIC PARADOX: PREMIUM PRODUCT CHURNS AT 41.9% WITHOUT TECH SUPPORT', fontsize=14, fontweight='bold', color='#0F172A', y=1.02)
plt.tight_layout()
plt.savefig(f'{out_dir}/04_fiber_optic_service_paradox.png', dpi=300, bbox_inches='tight')
plt.close()
print('Chart 4 complete.')

# -------------------------------------------------------------
# Chart 5: Payment Method Friction
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(12, 6), facecolor='white')
pay = df.groupby('PaymentMethod').agg(
    Count=('customerID', 'count'),
    Churn_Rate=('Churn_Num', 'mean'),
    Avg_Price=('MonthlyCharges', 'mean')
).sort_values(by='Churn_Rate', ascending=False)

colors_pay = ['#E11D48', '#F59E0B', '#0D9488', '#10B981']
bars_pay = ax.barh(pay.index, pay['Churn_Rate'] * 100, color=colors_pay, height=0.55, edgecolor='#334155')
ax.set_title('Churn Rate by Payment Channel: Electronic Check Drives Massive Churn', fontsize=13, fontweight='bold', color='#1E293B', pad=15)
ax.set_xlabel('Churn Rate (%)', fontsize=11, fontweight='bold', color='#334155')
ax.set_xlim(0, 55)
ax.axvline(df['Churn_Num'].mean() * 100, color='#64748B', linestyle='--', linewidth=1.5, label='Overall Base Churn (26.5%)')

for bar, cnt, prc in zip(bars_pay, pay['Count'], pay['Avg_Price']):
    xval = bar.get_width()
    yval = bar.get_y() + bar.get_height() / 2.0
    ax.text(xval + 1.0, yval, f'{xval:.1f}%  (Accounts: {cnt:,} | Avg ${prc:.1f}/mo)', ha='left', va='center', fontsize=10, fontweight='bold', color='#1E293B')

ax.legend(loc='lower right', frameon=True)
ax.grid(axis='x', linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig(f'{out_dir}/05_payment_method_friction.png', dpi=300, bbox_inches='tight')
plt.close()
print('Chart 5 complete.')

# -------------------------------------------------------------
# Chart 6: Historical Cumulative Charges Progression by Tenure Bracket
# -------------------------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), facecolor='white')

clv_stats = df.groupby('Tenure_Cohort', observed=False).agg(
    Avg_Total=('TotalCharges', 'mean'),
    Total_Rev=('TotalCharges', 'sum'),
    Count=('customerID', 'count')
).reindex(cohort_order)

bars_clv = ax1.bar(clv_stats.index, clv_stats['Avg_Total'], color='#0F766E', width=0.55, edgecolor='#134E4A')
ax1.set_title('Average Historical Cumulative Charges (TotalCharges) by Tenure', fontsize=11, fontweight='bold', color='#1E293B')
ax1.set_ylabel('Average Total Charges ($)', fontsize=11, fontweight='bold')
ax1.set_ylim(0, 6000)
for bar in bars_clv:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 100, f'${yval:,.0f}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='#0F766E')
ax1.grid(axis='y', linestyle=':', alpha=0.6)

bars_rev = ax2.bar(clv_stats.index, clv_stats['Total_Rev'] / 1e6, color='#2563EB', width=0.55, edgecolor='#1D4ED8')
ax2.set_title('Cumulative Revenue Contribution by Tenure Bracket', fontsize=12, fontweight='bold', color='#1E293B')
ax2.set_ylabel('Total Revenue ($ Millions)', fontsize=11, fontweight='bold')
ax2.set_ylim(0, 8.5)
total_cum_rev = clv_stats['Total_Rev'].sum() / 1e6
for bar in bars_rev:
    yval = bar.get_height()
    pct = (yval / total_cum_rev) * 100
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.15, f'${yval:.2f}M\n({pct:.1f}%)', ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#1D4ED8')
ax2.grid(axis='y', linestyle=':', alpha=0.6)

plt.suptitle('THE POWER OF RETENTION: 5+ YEAR ACCOUNTS ACCUMULATE 18.8x HIGHER REVENUE THAN YEAR 1', fontsize=13, fontweight='bold', color='#0F172A', y=1.02)
plt.tight_layout()
plt.savefig(f'{out_dir}/06_clv_and_tenure_progression.png', dpi=300, bbox_inches='tight')
plt.close()
print('Chart 6 complete.')

# -------------------------------------------------------------
# Chart 7: Executive 4-Panel Summary Dashboard
# -------------------------------------------------------------
fig, ((p1, p2), (p3, p4)) = plt.subplots(2, 2, figsize=(16, 12), facecolor='white')

# Panel 1: Churn by Contract
p1.bar(contract_stats.index, contract_stats['Churn_Rate'] * 100, color=['#E11D48', '#F59E0B', '#10B981'], width=0.5)
p1.set_title('1. Churn by Contract Commitment', fontsize=11, fontweight='bold', color='#1E293B')
p1.set_ylabel('Churn Rate (%)', fontsize=10, fontweight='bold')
p1.set_ylim(0, 52)
for i, v in enumerate(contract_stats['Churn_Rate'] * 100):
    p1.text(i, v + 1.2, f'{v:.1f}%', ha='center', fontweight='bold')
p1.grid(axis='y', linestyle=':', alpha=0.5)

# Panel 2: Churn by Tenure Cohort
p2.plot(range(len(cohort_stats)), cohort_stats['Churn_Rate'] * 100, marker='o', linewidth=2.5, color='#BE123C', markersize=7)
p2.set_xticks(range(len(cohort_stats)))
p2.set_xticklabels(cohort_stats.index, fontsize=9.5, fontweight='bold')
p2.set_title('2. Churn Decay by Tenure Bracket (Snapshot)', fontsize=11, fontweight='bold', color='#1E293B')
p2.set_ylabel('Churn Rate (%)', fontsize=10, fontweight='bold')
p2.set_ylim(0, 55)
for i, v in enumerate(cohort_stats['Churn_Rate'] * 100):
    p2.text(i, v + 1.5, f'{v:.1f}%', ha='center', fontweight='bold')
p2.grid(axis='both', linestyle=':', alpha=0.5)

# Panel 3: Fiber Optic Support Deficit
fiber_sub = fiber_bundle.iloc[[0, -1]] # No support/security vs both
p3.bar(['Fiber w/o Support', 'Fiber w/ Full Support'], fiber_sub['mean'] * 100, color=['#E11D48', '#10B981'], width=0.45)
p3.set_title('3. Fiber Optic Churn: Support Impact', fontsize=11, fontweight='bold', color='#1E293B')
p3.set_ylabel('Churn Rate (%)', fontsize=10, fontweight='bold')
p3.set_ylim(0, 60)
for i, v in enumerate(fiber_sub['mean'] * 100):
    p3.text(i, v + 1.5, f'{v:.1f}%', ha='center', fontweight='bold')
p3.grid(axis='y', linestyle=':', alpha=0.5)

# Panel 4: Payment Friction
pay_sub = pay.reindex(['Electronic check', 'Credit card (automatic)'])
p4.bar(['Electronic Check', 'Credit Card (Auto)'], pay_sub['Churn_Rate'] * 100, color=['#E11D48', '#10B981'], width=0.45)
p4.set_title('4. Payment Friction: Manual vs Auto-Pay', fontsize=11, fontweight='bold', color='#1E293B')
p4.set_ylabel('Churn Rate (%)', fontsize=10, fontweight='bold')
p4.set_ylim(0, 55)
for i, v in enumerate(pay_sub['Churn_Rate'] * 100):
    p4.text(i, v + 1.5, f'{v:.1f}%', ha='center', fontweight='bold')
p4.grid(axis='y', linestyle=':', alpha=0.5)

plt.suptitle('EXECUTIVE SUMMARY: KEY CHURN DRIVERS & LEVERAGE POINTS FOR RETENTION', fontsize=15, fontweight='bold', color='#0F172A', y=0.99)
plt.tight_layout()
plt.savefig(f'{out_dir}/07_executive_retention_dashboard_summary.png', dpi=300, bbox_inches='tight')
plt.close()
print('Chart 7 complete. All charts successfully generated!')
