from models.globals import results

# ============================================================
# WEIGHT-AVERAGE-COST OF CAPITAL
# ============================================================

def calculate_wacc(ke, kd):
    global results
    print("\n--- WACC CALCULATION ---")

    # Capital structure
    equity = float(input("Insert Equity Value (E): "))
    debt = float(input("Insert Debt Value (D): "))

    # Tax rate
    tax_rate = float(input("Insert Tax Rate (decimal): "))

    # Weights
    total_capital = equity + debt
    weight_e = equity / total_capital
    weight_d = debt / total_capital

    # WACC formula
    wacc = weight_e * ke + weight_d * kd * (1 - tax_rate)

    print("\n--- RESULTS ---")
    print(f"Equity Weight (E/V): {weight_e:.4f}")
    print(f"Debt Weight (D/V):   {weight_d:.4f}")
    print(f"Ke:                  {ke:.4f}")
    print(f"Kd (after tax):      {kd * (1 - tax_rate):.4f}")
    print(f"\nWACC:                {wacc:.4f}")

    results["wacc"]=wacc

    return wacc