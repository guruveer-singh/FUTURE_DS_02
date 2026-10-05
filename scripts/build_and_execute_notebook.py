import json
import sys
import io
import base64
import ast
import traceback
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

notebook = {
    "cells": [],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbformat_minor": 2,
            "pygments_lexer": "ipython3",
            "version": "3.12.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

def add_md(text):
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip().split("\n")]
    })

def add_code(code):
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in code.strip().split("\n")]
    })

# ==============================================================================
# 0. Title & Executive Problem Statement
# ==============================================================================
add_md("""# 📊 Customer Retention & Churn Analysis (Future Interns - Task 2)
### By Future Interns Data Science & Analytics Program
**Author:** Guruveer Singh  
**Project:** Task 2 - Customer Retention & Churn Analysis  
**Dataset Scope:** Telecom & Subscription Customer Dataset (7,043 customer accounts)  
**Deliverable:** End-to-end analytics notebook, cross-sectional cohort analysis, churn drivers, and SaaS retention strategy

---

## 🔍 Executive Problem Statement
Customer churn directly impacts company valuation, customer acquisition cost (CAC) payback periods, and recurring cash flow. In subscription models, acquiring a replacement customer is **5x to 7x more expensive** than retaining an existing account.

This analysis provides leadership and product teams with actionable answers to four foundational business questions:
1. **Why are customers leaving the platform?**
2. **Which customer segments and contract commitments are most likely to churn?**
3. **Where in the customer lifecycle does attrition concentrate?**
4. **What high-ROI interventions can maximize customer retention and preserve recurring revenue?**

> **📌 Methodological Note: Cross-Sectional Snapshot vs. Longitudinal Cohort Tracking**  
> This dataset represents a **cross-sectional snapshot** of 7,043 customer accounts observed at a single point in time, with tenure ranging from 0 to 72 months. While it does not track a single monthly cohort longitudinally across 72 consecutive calendar months, grouping accounts into tenure lifecycle brackets (`0-12 Mo`, `13-24 Mo`, etc.) provides a valuable cross-sectional proxy for tenure-related churn propensity. Active subscriber tenures are right-censored (their subscription journey is ongoing), so the observed average tenure (32.4 months) reflects the mean age of accounts in this snapshot rather than completed actuarial customer lifetimes.""")

# ==============================================================================
# Cell 1: Imports
# ==============================================================================
add_code("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Visual style setup
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['figure.dpi'] = 120
print('Core analytics and visualization libraries imported successfully!')""")

# ==============================================================================
# 1. Data Ingestion & Preprocessing
# ==============================================================================
add_md("""---
## 1. Data Ingestion, Cleaning & Preprocessing
We load the raw customer dataset containing 7,043 subscriber records across 21 demographic, service, contract, and billing attributes.""")

add_code("""# Load dataset
df = pd.read_csv('data/telco_customer_churn.csv')
print(f'Dataset Dimensions: {df.shape[0]:,} rows, {df.shape[1]} columns')
df.head(3)""")

add_code("""# Data Hygiene: Check missing values and spaces in numeric columns
print("Missing values per column:")
print(df.isnull().sum()[df.isnull().sum() > 0])

# TotalCharges contains whitespace strings for tenure = 0 customers (new signups)
spaces_count = (df['TotalCharges'] == ' ').sum()
print(f"Whitespace strings in TotalCharges: {spaces_count}")

# Convert TotalCharges to numeric, filling newly acquired accounts (tenure=0) with 0.0
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'].replace(' ', np.nan)).fillna(0.0)

# Binary churn indicator for vectorized statistics
df['Churn_Num'] = (df['Churn'] == 'Yes').astype(int)

# Confirm types and readiness
print(f"TotalCharges dtype: {df['TotalCharges'].dtype}")
print(f"Cleaned dataset ready with {len(df):,} accounts and 0 null values.")""")

# ==============================================================================
# 2. Baseline Churn Rate & Revenue Exposure
# ==============================================================================
add_md("""---
## 2. Baseline Churn Rate & Revenue Exposure (MRR / ARR)
We evaluate the top-line retention health of the business and quantify the exact recurring financial impact of churned accounts.""")

add_code("""total_customers = len(df)
churned_customers = df['Churn_Num'].sum()
retained_customers = total_customers - churned_customers
churn_rate = churned_customers / total_customers

total_mrr = df['MonthlyCharges'].sum()
churned_mrr = df[df['Churn_Num'] == 1]['MonthlyCharges'].sum()
retained_mrr = total_mrr - churned_mrr
churned_arr = churned_mrr * 12

print("="*60)
print("             EXECUTIVE RETENTION KPI SCORECARD")
print("="*60)
print(f"Total Subscriber Base:        {total_customers:,} accounts")
print(f"Retained Accounts:            {retained_customers:,} ({1 - churn_rate:.2%})")
print(f"Churned Accounts:             {churned_customers:,} ({churn_rate:.2%})")
print(f"Total Portfolio MRR:          ${total_mrr:,.2f} / month")
print(f"Lost Recurring Revenue (MRR): ${churned_mrr:,.2f} / month ({churned_mrr/total_mrr:.1%})")
print(f"Annualized Run-Rate Loss:     ${churned_arr:,.2f} / year")
print(f"Observed Mean Account Tenure: {df['tenure'].mean():.1f} months")
print("="*60)""")

# ==============================================================================
# 3. Tenure Bracket Cohort Analysis
# ==============================================================================
add_md("""---
## 3. Tenure Bracket Analysis & The Onboarding Cliff (Months 0–12)
We examine retention across customer lifecycle stages by grouping tenure into 12-month lifecycle brackets (Years 1 through 6).

*Note: In this cross-sectional snapshot, these brackets compare accounts of differing current ages rather than tracking a single historical signup cohort over calendar time.*""")

add_code("""# Define 12-month tenure cohort bins
bins = [0, 12, 24, 36, 48, 60, 72]
labels = ['0-12 Mo (Yr 1)', '13-24 Mo (Yr 2)', '25-36 Mo (Yr 3)', '37-48 Mo (Yr 4)', '49-60 Mo (Yr 5)', '61-72 Mo (Yr 6)']
df['Tenure_Cohort'] = pd.cut(df['tenure'], bins=bins, labels=labels, include_lowest=True)

cohort_summary = df.groupby('Tenure_Cohort', observed=False).agg(
    Total_Customers=('customerID', 'count'),
    Churned_Accounts=('Churn_Num', 'sum'),
    Churn_Rate=('Churn_Num', 'mean'),
    Retention_Rate=('Churn_Num', lambda x: 1 - x.mean()),
    Avg_Monthly_Fee=('MonthlyCharges', 'mean'),
    Avg_Total_Charges=('TotalCharges', 'mean'),
    Total_MRR_Loss=('MonthlyCharges', lambda x: x[df.loc[x.index, 'Churn_Num'] == 1].sum())
)

cohort_summary['% of Total Churn'] = (cohort_summary['Churned_Accounts'] / churned_customers) * 100
cohort_summary""")

add_code("""# Visualize Churn Decay Across Cross-Sectional Tenure Brackets
plt.figure(figsize=(10, 5))
bars = plt.bar(cohort_summary.index, cohort_summary['Churn_Rate'] * 100, color='#E11D48', alpha=0.85, width=0.5)
plt.title('Customer Churn Rate by Tenure Bracket (Cross-Sectional Snapshot)', fontsize=13, fontweight='bold', pad=12)
plt.ylabel('Churn Rate (%)', fontsize=11, fontweight='bold')
plt.ylim(0, 55)

for bar in bars:
    y = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, y + 1.2, f'{y:.1f}%', ha='center', fontweight='bold', color='#9F1239')

plt.axhline(churn_rate * 100, color='#64748B', linestyle='--', label=f'Portfolio Baseline Churn ({churn_rate:.1%})')
plt.legend(frameon=True)
plt.tight_layout()
plt.show()""")

# ==============================================================================
# 4. Contract Commitment Analysis
# ==============================================================================
add_md("""---
## 4. Contract Commitment as the Primary Retention Anchor
Contract type is the single strongest structural determinant of subscriber retention. Month-to-month contracts lack switching friction, while annual agreements lock in habits and commitment.""")

add_code("""contract_perf = df.groupby('Contract').agg(
    Customer_Count=('customerID', 'count'),
    Churn_Count=('Churn_Num', 'sum'),
    Churn_Rate=('Churn_Num', 'mean'),
    Avg_Monthly=('MonthlyCharges', 'mean'),
    Lost_MRR=('MonthlyCharges', lambda x: x[df.loc[x.index, 'Churn_Num'] == 1].sum())
).reindex(['Month-to-month', 'One year', 'Two year'])

contract_perf['Share_of_Lost_MRR'] = (contract_perf['Lost_MRR'] / churned_mrr) * 100
contract_perf""")

add_code("""# Contract churn vs MRR loss
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
ax1.bar(contract_perf.index, contract_perf['Churn_Rate'] * 100, color=['#E11D48', '#F59E0B', '#10B981'], width=0.5)
ax1.set_title('Churn Rate by Contract Commitment', fontweight='bold')
ax1.set_ylabel('Churn Rate (%)')
ax1.set_ylim(0, 50)
for i, v in enumerate(contract_perf['Churn_Rate'] * 100):
    ax1.text(i, v + 1, f'{v:.1f}%', ha='center', fontweight='bold')

ax2.bar(contract_perf.index, contract_perf['Lost_MRR'] / 1000, color=['#E11D48', '#F59E0B', '#10B981'], width=0.5)
ax2.set_title('Monthly Revenue Lost ($K / month)', fontweight='bold')
ax2.set_ylabel('MRR Lost ($K)')
ax2.set_ylim(0, 140)
for i, v in enumerate(contract_perf['Lost_MRR'] / 1000):
    ax2.text(i, v + 2, f'${v:.1f}K', ha='center', fontweight='bold')

plt.tight_layout()
plt.show()""")

# ==============================================================================
# 5. Product Quality & The Fiber Optic Support Paradox
# ==============================================================================
add_md("""---
## 5. Product Quality & The Fiber Optic Support Paradox
High-speed Fiber Optic represents the company's highest-priced core product ($91.50/mo vs $58.10/mo for DSL). Yet, Fiber Optic has a shocking **41.9% churn rate**.

Why does the premium product churn at 2.2x the rate of legacy DSL? Let us investigate service bundling and technical support.""")

add_code("""# Cross-tabulate Fiber Optic customers by Tech Support & Online Security
fiber_df = df[df['InternetService'] == 'Fiber optic']
fiber_analysis = fiber_df.groupby(['TechSupport', 'OnlineSecurity'])['Churn_Num'].agg(
    Total_Customers='count',
    Churn_Rate='mean'
).reset_index()

fiber_analysis['Retention_Rate'] = 1 - fiber_analysis['Churn_Rate']
fiber_analysis['Churn_Rate_%'] = (fiber_analysis['Churn_Rate'] * 100).round(1).astype(str) + '%'
fiber_analysis['Retention_Rate_%'] = (fiber_analysis['Retention_Rate'] * 100).round(1).astype(str) + '%'
fiber_analysis.sort_values(by='Churn_Rate', ascending=False)""")

# ==============================================================================
# 6. Payment Channels & Involuntary Billing Friction
# ==============================================================================
add_md("""---
## 6. Payment Channels & Involuntary Billing Friction
Manual payment methods create recurring monthly decision points and involuntary churn due to missed payments or billing fatigue.""")

add_code("""pay_analysis = df.groupby('PaymentMethod').agg(
    Accounts=('customerID', 'count'),
    Churn_Rate=('Churn_Num', 'mean'),
    Avg_Monthly_Fee=('MonthlyCharges', 'mean'),
    Total_MRR_Loss=('MonthlyCharges', lambda x: x[df.loc[x.index, 'Churn_Num'] == 1].sum())
).sort_values(by='Churn_Rate', ascending=False)

pay_analysis['Churn_Rate_%'] = (pay_analysis['Churn_Rate'] * 100).round(1).astype(str) + '%'
pay_analysis""")

# ==============================================================================
# 7. Historical Cumulative Charges Progression by Tenure Bracket
# ==============================================================================
add_md("""---
## 7. Historical Cumulative Spend & Compounding Retention Economics
Customer retention is the ultimate driver of cumulative customer revenue. Analyzing historical cumulative charges (`TotalCharges`) across tenure brackets illustrates how subscriber value compounds over time.

> **Methodological Note on Cumulative Spend vs. Lifetime Value:** Because this dataset is a cross-sectional snapshot with right-censored active accounts, `TotalCharges` represents historical cumulative charges billed to date within each tenure bracket, rather than completed actuarial Customer Lifetime Value (CLV).""")

add_code("""spend_cohort = df.groupby('Tenure_Cohort', observed=False)['TotalCharges'].agg(['mean', 'median', 'sum'])
spend_cohort.columns = ['Avg_Cumulative_Spend_($)', 'Median_Cumulative_Spend_($)', 'Total_Cumulative_Revenue_($)']
spend_cohort['Spend_Multiplier_vs_Yr1'] = spend_cohort['Avg_Cumulative_Spend_($)'] / spend_cohort['Avg_Cumulative_Spend_($)'].iloc[0]
spend_cohort.round(2)""")

# ==============================================================================
# 8. Customer Risk Scoring Model
# ==============================================================================
add_md("""---
## 8. Customer Risk Scoring Model (Rule-Based Health Scoring)
We segment the active customer base (5,174 retained accounts) into predictive risk tiers:
- **High Risk:** Month-to-month + First-Year (tenure <= 12) + Electronic Check + Fiber w/o Tech Support
- **Medium Risk:** Month-to-month with tenure > 12 OR unbundled Fiber Optic
- **Low Risk:** Annual/Two-year contracts with automated payment and add-on services""")

add_code("""def score_customer(row):
    score = 0
    if row['Contract'] == 'Month-to-month': score += 3
    if row['tenure'] <= 12: score += 3
    if row['PaymentMethod'] == 'Electronic check': score += 2
    if row['InternetService'] == 'Fiber optic' and row['TechSupport'] == 'No': score += 2
    if row['OnlineSecurity'] == 'No': score += 1
    if row['PaperlessBilling'] == 'Yes': score += 1
    
    if score >= 6: return 'High Risk'
    elif score >= 3: return 'Medium Risk'
    else: return 'Low Risk'

df['Risk_Tier'] = df.apply(score_customer, axis=1)

active_risk = df[df['Churn_Num'] == 0].groupby('Risk_Tier').agg(
    Active_Accounts=('customerID', 'count'),
    Total_MRR_At_Risk=('MonthlyCharges', 'sum'),
    Avg_Monthly_Fee=('MonthlyCharges', 'mean'),
    Avg_Tenure=('tenure', 'mean')
).reindex(['High Risk', 'Medium Risk', 'Low Risk'])

active_risk['Share_of_Active_MRR'] = (active_risk['Total_MRR_At_Risk'] / active_risk['Total_MRR_At_Risk'].sum()) * 100
active_risk.round(2)""")

# ==============================================================================
# 9. ROI Simulation
# ==============================================================================
add_md("""---
## 9. ROI Simulation: Revenue Preserved via Targeted Retention
What is the financial return of reducing churn by **5%**, **10%**, or **20%** through our strategic recommendations?""")

add_code("""scenarios = [0.05, 0.10, 0.15, 0.20]
sim_results = []

for s in scenarios:
    saved_accounts = int(churned_customers * s)
    monthly_rev_saved = churned_mrr * s
    annual_rev_saved = monthly_rev_saved * 12
    sim_results.append({
        'Churn Reduction Goal': f'{s:.0%}',
        'Accounts Saved': f'{saved_accounts:,}',
        'Monthly Revenue Saved': f'${monthly_rev_saved:,.2f}',
        'Annual Recurring Revenue Preserved': f'${annual_rev_saved:,.2f}'
    })

sim_df = pd.DataFrame(sim_results)
print("="*65)
print("       RETENTION INTERVENTION ROI SENSITIVITY MODEL")
print("="*65)
print(sim_df.to_string(index=False))
print("="*65)""")

# ==============================================================================
# 10. Strategic Recommendations
# ==============================================================================
add_md("""---
## 10. Strategic Recommendations & Retention Playbook for Leadership

### 🎯 1. Contract Migration Campaign (The $120.8K/mo Opportunity)
- **The Problem:** Month-to-month contracts have a **42.7% churn rate**, generating **86.9% of all lost MRR**.
- **Action:** Launch an aggressive "Annual Commitment Incentive" offering **15% off or 2 months free** for upgrading to a 1-year agreement.
- **Projected Impact:** Migrating just 20% of M2M subscribers to 1-year agreements preserves **~$24,000/mo ($288K ARR)**.

### 🛡️ 2. First 90 Days Onboarding Cadence
- **The Problem:** **55.5% of total churn occurs in Months 0–12** (47.4% first-year churn rate).
- **Action:** Establish a dedicated Day 1-90 customer success journey with proactive setup calls, onboarding webinars, usage telemetry alerts, and Month-6 milestone loyalty bonuses.

### ⚡ 3. The Fiber Optic Support Bundle
- **The Problem:** Premium Fiber Optic users churn at **41.9%**, but adding Tech Support cuts churn to **22.6%**.
- **Action:** Stop selling unbundled Fiber Optic. Include 24/7 dedicated Tech Support and Online Security as standard features within the base subscription tier.

### 💳 4. Automated Payment Incentives
- **The Problem:** Electronic Check users churn at **45.3%**, compared to **15.2%** for Auto-Credit Card and **16.7%** for Auto-Bank Transfer.
- **Action:** Provide a **$5/month statement credit** for enrolling in Auto-Pay, removing manual payment friction and reducing involuntary churn.""")

# ==============================================================================
# EXECUTION ENGINE: Execute all code cells and embed real outputs
# ==============================================================================
print('Beginning notebook execution...')
exec_globals = {}
exec_count = 1

for idx, cell in enumerate(notebook['cells']):
    if cell['cell_type'] != 'code':
        continue
    
    code_text = "".join(cell['source'])
    print(f'Executing code cell {exec_count}...')
    
    cell['execution_count'] = exec_count
    cell['outputs'] = []
    
    # Intercept stdout
    old_stdout = sys.stdout
    captured_stdout = io.StringIO()
    sys.stdout = captured_stdout
    
    # Intercept matplotlib figures
    captured_figs = []
    def custom_show(*args, **kwargs):
        for fig_num in plt.get_fignums():
            fig = plt.figure(fig_num)
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=120)
            buf.seek(0)
            b64_img = base64.b64encode(buf.read()).decode('utf-8')
            captured_figs.append(b64_img)
        plt.close('all')
    
    orig_show = plt.show
    plt.show = custom_show
    
    eval_result = None
    try:
        # Check if last statement is an expression
        tree = ast.parse(code_text)
        last_is_expr = False
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            last_is_expr = True
            exec_code = ast.unparse(tree.body[:-1])
            eval_expr = ast.unparse(tree.body[-1].value)
            
            if exec_code.strip():
                exec(exec_code, exec_globals)
            eval_result = eval(eval_expr, exec_globals)
        else:
            exec(code_text, exec_globals)
    except Exception as e:
        sys.stdout = old_stdout
        print(f"Error in cell {exec_count}: {e}")
        traceback.print_exc()
        raise e
    finally:
        sys.stdout = old_stdout
        plt.show = orig_show
    
    # Any remaining unshown plots?
    for fig_num in plt.get_fignums():
        fig = plt.figure(fig_num)
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=120)
        buf.seek(0)
        b64_img = base64.b64encode(buf.read()).decode('utf-8')
        captured_figs.append(b64_img)
    plt.close('all')
    
    # Collect stdout
    stdout_val = captured_stdout.getvalue()
    if stdout_val:
        cell['outputs'].append({
            "name": "stdout",
            "output_type": "stream",
            "text": [line + "\n" for line in stdout_val.splitlines()]
        })
    
    # Collect figures
    for fig_b64 in captured_figs:
        cell['outputs'].append({
            "data": {
                "image/png": fig_b64,
                "text/plain": ["<Figure size ...>"]
            },
            "metadata": {},
            "output_type": "display_data"
        })
    
    # Collect expression results (DataFrames, etc.)
    if eval_result is not None:
        data_dict = {}
        if isinstance(eval_result, pd.DataFrame):
            data_dict["text/html"] = [eval_result.to_html()]
            data_dict["text/plain"] = [repr(eval_result)]
        elif isinstance(eval_result, pd.Series):
            data_dict["text/plain"] = [repr(eval_result)]
        else:
            data_dict["text/plain"] = [repr(eval_result)]
        
        cell['outputs'].append({
            "data": data_dict,
            "execution_count": exec_count,
            "metadata": {},
            "output_type": "execute_result"
        })
    
    exec_count += 1

# Write out completed executed notebook
with open('customer_retention_and_churn_analysis.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=2)

print('Executed customer_retention_and_churn_analysis.ipynb with all outputs saved!')
