import pandas as pd
from models.globals import results

# ============================================================
# 1) VALUATION
# ============================================================

def valuation_engine_dual(df, row_fcff, row_fcfe, wacc, ke):
    """
    Valuation engine FCFF + FCFE.
    g is ALWAYS taken from results["g"].
    If g is missing, it is requested ONCE and saved.
    """

    global results

    print("\n--- VALUATION ENGINE (FCFF + FCFE) ---")

    # -----------------------------------------
    # 1) Estrarre i flussi dalle RIGHE
    # -----------------------------------------
    fcff = df.loc[row_fcff].values.astype(float)
    fcfe = df.loc[row_fcfe].values.astype(float)
    T = len(fcff)

    # -----------------------------------------
    # 2) Recupero g (senza chiederla mai più)
    # -----------------------------------------
    if "g" in results:
        g = results["g"]
        print(f"\nUsing stored perpetual growth g = {g:.4f}")
    else:
        print("\n--- PERPETUAL GROWTH g (FIRST TIME ONLY) ---")
        gdp = float(input("Insert long-term GDP growth (decimal): "))
        inflation = float(input("Insert long-term inflation (decimal): "))
        sector = float(input("Insert long-term sector growth premium (decimal): "))
        g = gdp + inflation + sector
        results["g"] = g
        print(f"Calculated perpetual growth g = {g:.4f}")

    # -----------------------------------------
    # 3) Forecast
    # -----------------------------------------
    fcff_forecast = fcff[-1] * (1 + g)
    fcfe_forecast = fcfe[-1] * (1 + g)

    # -----------------------------------------
    # 4) Tabella ACT
    # -----------------------------------------
    act_fct = ["ACT"] * T
    table = pd.DataFrame({
        "Year": df.columns,
        "FCFF": fcff,
        "FCFE": fcfe,
        "Type": act_fct
    })
    print("\n--- CASH FLOW TABLE ---")
    print(table)

    # -----------------------------------------
    # 5) PV FCFF
    # -----------------------------------------
    pv_fcff = [fcff[t] / ((1 + wacc) ** (t+1)) for t in range(T)]
    pv_fcff_total = sum(pv_fcff)

    tv_fcff = fcff[-1] * (1 + g) / (wacc - g)
    pv_tv_fcff = tv_fcff / ((1 + wacc) ** T)

    enterprise_value = pv_fcff_total + pv_tv_fcff

    # -----------------------------------------
    # 6) PV FCFE
    # -----------------------------------------
    pv_fcfe = [fcfe[t] / ((1 + ke) ** (t+1)) for t in range(T)]
    pv_fcfe_total = sum(pv_fcfe)

    tv_fcfe = fcfe[-1] * (1 + g) / (ke - g)
    pv_tv_fcfe = tv_fcfe / ((1 + ke) ** T)

    equity_value = pv_fcfe_total + pv_tv_fcfe

    # -----------------------------------------
    # 7) RISULTATI
    # -----------------------------------------
    print("\n--- RESULTS ---")
    print(f"Enterprise Value (FCFF): {enterprise_value:.2f}")
    print(f"Equity Value (FCFE): {equity_value:.2f}")

    results["enterprise_value"] = enterprise_value
    results["equity_value"] = equity_value

    return enterprise_value, equity_value

# ============================================================
# 2) SENSITIVITY ANALYSIS
# ============================================================

def sensitivity_valuation(df, row_fcff, row_fcfe, wacc, ke, delta_list):
    """
    Sensitivity analysis on WACC and Ke.
    g is ALWAYS taken from results["g"].
    """

    global results

    print("\n--- SENSITIVITY ANALYSIS ---")

    # ----------------------------------------------------
    # 1) Primo calcolo base (g già gestita internamente)
    # ----------------------------------------------------
    EV_base, EQ_base = valuation_engine_dual(
        df=df,
        row_fcff=row_fcff,
        row_fcfe=row_fcfe,
        wacc=wacc,
        ke=ke
    )

    g = results["g"]  # g già salvata

    results_s = []

    # ----------------------------------------------------
    # 2) Loop sulle variazioni
    # ----------------------------------------------------
    for d in delta_list:
        new_wacc = wacc + d
        new_ke = ke + d

        EV, EQ = valuation_engine_dual(
            df=df,
            row_fcff=row_fcff,
            row_fcfe=row_fcfe,
            wacc=new_wacc,
            ke=new_ke
        )

        results_s.append({
            "Delta (bps)": round(d * 10000, 3),
            "WACC": round(new_wacc, 3),
            "Ke": round(new_ke, 3),
            "EV": round(EV, 3),
            "EV Δ%": round((EV - EV_base) / EV_base * 100, 3),
            "Equity": round(EQ, 3),
            "Equity Δ%": round((EQ - EQ_base) / EQ_base * 100, 3)
        })

    # ----------------------------------------------------
    # 3) Tabella finale
    # ----------------------------------------------------
    table = pd.DataFrame(results_s)

    print("\n--- SENSITIVITY TABLE ---")
    print(table)


    return table
