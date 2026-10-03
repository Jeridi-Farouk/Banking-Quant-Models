import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
import statsmodels.api as sm

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

print("\n==============================")
print("      INPUT FINANCIAL DATA")
print("==============================\n")

# Business line names
business_lines = input("Insert business line names (comma separated): ")
business_lines = [n.strip() for n in business_lines.split(",")]

# Inputs
ii = np.array([float(x) for x in input("Insert Interest Income per BL: ").split(",")])
ie = np.array([float(x) for x in input("Insert Interest Expenses per BL: ").split(",")])
nf = np.array([float(x) for x in input("Insert Net Fee per BL: ").split(",")])
oi = np.array([float(x) for x in input("Insert Other Income per BL: ").split(",")])
wd = np.array([float(x) for x in input("Insert Write-Downs per BL: ").split(",")])
oe = np.array([float(x) for x in input("Insert Operating Expenses per BL: ").split(",")])

# PBT
pbt = ii + ie + nf + oi + wd + oe

# Taxes
tax_percentage = float(input("Insert Tax Percentage: "))
taxes = pbt * tax_percentage

# Net Income
ni = pbt - taxes

# P&L table
df_pl = pd.DataFrame({
    "Business Line": business_lines,
    "Interest Income": ii,
    "Interest Expenses": ie,
    "Net Fee": nf,
    "Other Income": oi,
    "Write-Downs": wd,
    "Operating Expenses": oe,
    "PBT": pbt,
    "Taxes": taxes,
    "Net Income": ni
})

print("\n==============================")
print("        PROFIT & LOSS TABLE")
print("==============================\n")
print(df_pl.to_string(index=False))

print("\n==============================")
print("       RISK & CAPITAL DATA")
print("==============================\n")

# RWA & Balance Sheet
rwa = np.array([float(x) for x in input("Insert RWA per BL: ").split(",")])
bs = np.array([float(x) for x in input("Insert Balance Sheet Value per BL: ").split(",")])

rwca = bs * rwa
tcr = float(input("Insert Total Capital Ratio (TCR): "))
capital_allocated = rwca * tcr

# Capitale totale economico per BL: BS + capitale allocato
total_capital_current_bl = bs + capital_allocated
total_capital_current = np.sum(total_capital_current_bl)

df_capital = pd.DataFrame({
    "Business Line": business_lines,
    "Balance Sheet (BS)": bs,
    "RWA": rwa,
    "RWA Capital Absorption": rwca,
    "Capital Allocated (Regulatory)": capital_allocated,
    "Total Capital (BS + Allocated)": total_capital_current_bl
})

print("\n==============================")
print("       CAPITAL ALLOCATION TABLE")
print("==============================\n")
print(df_capital.to_string(index=False))

print("\n==============================")
print("       MARKET DATA & BETA")
print("==============================\n")

ticker = input("Insert Asset Ticker: ")
period = input("Insert Period (e.g. 5y): ")
index_ticker = input("Insert Index Ticker: ")

pricing_asset = yf.download(ticker, period=period)["Close"].values.squeeze()
pricing_index = yf.download(index_ticker, period=period)["Close"].values.squeeze()

asset_returns = np.diff(pricing_asset) / pricing_asset[:-1]
index_returns = np.diff(pricing_index) / pricing_index[:-1]

X = sm.add_constant(index_returns)
model = sm.OLS(asset_returns, X).fit()

beta = model.params[1]
alpha = model.params[0]

print(f"Alpha: {alpha:.6f}")
print(f"Beta: {beta:.6f}")
print(f"R-squared: {model.rsquared:.4f}")

index_returns_mean = (1 + index_returns.mean())**252 - 1
rf = float(input("Insert Risk-Free Rate: "))
erp = index_returns_mean - rf
ke = rf + beta * erp
coe = capital_allocated * ke

roarac = (ni - coe) / capital_allocated

df_risk = pd.DataFrame({
    "Business Line": business_lines,
    "Capital Allocated": capital_allocated,
    "Cost of Equity (COE)": coe,
    "ROARAC": roarac
})

print("\n==============================")
print("       ROARAC TABLE")
print("==============================\n")
print(df_risk.to_string(index=False))

# ROARAC totale corrente (tempo t)
roarac_total_current = (np.sum(ni) - np.sum(capital_allocated * ke)) / np.sum(capital_allocated)
print("\nTotal ROARAC (current):", roarac_total_current)

print("\n==============================")
print("       STRESS TEST RESULTS")
print("==============================\n")

wd_collection = np.array([float(x) for x in input("Insert Write-Down Collection per BL: ").split(",")])

delta_pd = np.array([0.01, 0.005, 0.001])
delta_lgd = np.array([0.01, 0.005, 0.001])

wd_stressed_list = [wd_collection * delta_pd[t] * delta_lgd[t] for t in range(len(delta_pd))]
wd_total_scenario = [wd + ws for ws in wd_stressed_list]

pbt_stressed_list = []
taxes_stressed_list = []
ni_stressed_list = []
roarac_stressed_list = []

for i in range(len(delta_pd)):
    wd_s = wd_total_scenario[i]
    pbt_s = ii + ie + nf + oi + wd_s + oe
    taxes_s = pbt_s * tax_percentage
    ni_s = pbt_s - taxes_s
    roarac_s = (ni_s - capital_allocated * ke) / capital_allocated

    pbt_stressed_list.append(pbt_s)
    taxes_stressed_list.append(taxes_s)
    ni_stressed_list.append(ni_s)
    roarac_stressed_list.append(roarac_s)

    print(f"\nScenario {i+1}")
    print("Stressed WD:", wd_s)
    print("PBT stressed:", pbt_s)
    print("NI stressed:", ni_s)
    print("ROARAC stressed:", roarac_s)

# ============================
# OPTIMIZATION: REDISTRIBUTE BS
# ============================

print("\n==============================")
print("       CAPITAL OPTIMIZATION")
print("==============================\n")

# Obiettivo: minimizzare il capitale allocato futuro
def objective(bs_new, rwa, tcr):
    capital_allocated_new = bs_new * rwa * tcr
    return np.sum(capital_allocated_new)

# Vincolo 1: capitale totale economico (BS + capitale allocato) costante
def constraint_total_capital(bs_new):
    capital_allocated_new = bs_new * rwa * tcr
    total_capital_new = np.sum(bs_new + capital_allocated_new)
    return total_capital_new - total_capital_current

# Vincolo 2: ROARAC totale futuro >= ROARAC totale corrente
def constraint_roarac(bs_new, ni, ke, rwa, tcr):
    capital_allocated_new = bs_new * rwa * tcr
    roarac_total_new = (np.sum(ni) - np.sum(capital_allocated_new * ke)) / np.sum(capital_allocated_new)
    return roarac_total_new - roarac_total_current  # deve essere >= 0

constraints = [
    {'type': 'eq',   'fun': constraint_total_capital},
    {'type': 'ineq', 'fun': lambda x: constraint_roarac(x, ni, ke, rwa, tcr)}
]

bounds = [(0, None)] * len(bs)
x0 = bs.copy()

result = minimize(
    objective,
    x0,
    args=(rwa, tcr),
    constraints=constraints,
    bounds=bounds,
    method='SLSQP'
)

bs_optimal = result.x
capital_allocated_optimal = bs_optimal * rwa * tcr
total_capital_optimal_bl = bs_optimal + capital_allocated_optimal

df_opt = pd.DataFrame({
    "Business Line": business_lines,
    "BS Current": bs,
    "BS Optimal": bs_optimal,
    "Capital Allocated Current": capital_allocated,
    "Capital Allocated Optimal": capital_allocated_optimal,
    "Total Capital Optimal": total_capital_optimal_bl
})

print("\n==============================")
print("   OPTIMIZED CAPITAL ALLOCATION")
print("==============================\n")
print(df_opt.to_string(index=False))
print("\nTotal Allocated Capital (Current):", np.sum(capital_allocated))
print("Total Allocated Capital (Optimal):", np.sum(capital_allocated_optimal))

roarac_total_optimal = (np.sum(ni) - np.sum(capital_allocated_optimal * ke)) / np.sum(capital_allocated_optimal)
print("\nTotal ROARAC (current):", roarac_total_current)
print("Total ROARAC (optimal):", roarac_total_optimal)

print("Total Capital (Current):", total_capital_current)
print("Total Capital (Optimal):", np.sum(total_capital_optimal_bl))

# ============================
# PDF EXPORT (ORDERED TABLES)
# ============================

print("\nGenerating PDF report...")

doc = SimpleDocTemplate("Bank_Capital_Report.pdf", pagesize=A4)
elements = []
styles = getSampleStyleSheet()

def add_table(title, df):
    elements.append(Paragraph(f"<b>{title}</b>", styles['Heading2']))
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONT', (0,0), (-1,-1), 'Helvetica', 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

add_table("Profit & Loss Table", df_pl)
add_table("Capital Allocation Table", df_capital)
add_table("ROARAC Table", df_risk)
add_table("Optimized Capital Allocation", df_opt)

doc.build(elements)
print("\nPDF generated: Bank_Capital_Report.pdf")