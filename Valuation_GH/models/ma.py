from models.globals import results

# ============================================================
# 1) M&A analysis
# ============================================================

def accretion_dilution(enterprise_value_target):

    global results

    print("\n--- ACCRETION / DILUTION ANALYSIS ---")

    # -----------------------------
    # TARGET CAPITAL STRUCTURE
    # -----------------------------
    debt_target = float(input("Insert TARGET Debt: "))
    cash_target = float(input("Insert TARGET Cash: "))
    shares_target = float(input("Insert TARGET Shares Outstanding: "))
    market_price = float(input("Insert TARGET Current Market Price: "))

    # Equity Value from EV
    equity_value_target = enterprise_value_target - (debt_target - cash_target)
    fair_value_per_share = equity_value_target / shares_target

    # Premium massimo sostenibile
    premium_max_pct = fair_value_per_share / market_price - 1

    print(f"\nFair Value per Share (from EV): {fair_value_per_share:.2f}")
    print(f"Maximum Sustainable Premium: {premium_max_pct*100:.2f}%")

    # Offer price
    offer_price = float(input("\nInsert OFFER PRICE per share: "))
    equity_value_offer = offer_price * shares_target

    # Equity value at market price
    equity_value_market = market_price * shares_target

    # Premium totale in €
    premium = equity_value_offer - equity_value_market

    # Premium percentuale
    premium_pct = offer_price / market_price - 1

    # -----------------------------
    # BUYER INPUTS
    # -----------------------------
    ni_buyer = float(input("\nInsert BUYER Net Income: "))
    shares_buyer = float(input("Insert BUYER Shares Outstanding: "))
    debt_buyer = float(input("Insert BUYER Net Debt: "))
    ebitda_buyer = float(input("Insert BUYER EBITDA: "))

    results["ebitda_buyer"]=ebitda_buyer
    results["shares_buyer"]=shares_buyer
    results["debt_buyer"]=debt_buyer
    results["ni_buyer"]=ni_buyer

    # -----------------------------
    # TARGET INPUTS (operativi)
    # -----------------------------
    ni_target = float(input("\nInsert TARGET Net Income: "))
    ebitda_target = float(input("Insert TARGET EBITDA: "))

    results["ebitda_target"]=ebitda_target
    results["ni_target"]=ni_target



    # -----------------------------
    # DEAL FINANCING
    # -----------------------------
    print("\n--- DEAL FINANCING ---")
    debt_financing = float(input("Insert NEW DEBT used to finance the deal: "))
    interest_rate = float(input("Insert INTEREST RATE on new debt (e.g. 0.06): "))
    new_shares = float(input("Insert NEW SHARES issued (0 if none): "))

    # -----------------------------
    # SYNERGIES
    # -----------------------------
    synergies = float(input("\nInsert TOTAL SYNERGIES after tax: "))

    # -----------------------------
    # EPS PRE-DEAL
    # -----------------------------
    eps_pre = ni_buyer / shares_buyer

    # -----------------------------
    # NET INCOME POST-DEAL
    # -----------------------------
    new_interest = debt_financing * interest_rate
    ni_post = ni_buyer + ni_target + synergies - new_interest
    shares_post = shares_buyer + new_shares

    eps_post = ni_post / shares_post
    accretion_pct = eps_post / eps_pre - 1

    # -----------------------------
    # LEVERAGE PRO-FORMA
    # -----------------------------
    net_debt_post = debt_buyer + debt_financing + debt_target - cash_target
    ebitda_post = ebitda_buyer + ebitda_target + synergies
    leverage_post = net_debt_post / ebitda_post

    # -----------------------------
    # IMPLIED DEAL MULTIPLES
    # -----------------------------
    ev_offer = equity_value_offer + debt_target - cash_target
    ev_ebitda_implied = ev_offer / ebitda_target if ebitda_target != 0 else None
    pe_implied = equity_value_offer / ni_target if ni_target != 0 else None

    # -----------------------------
    # OUTPUT
    # -----------------------------
    print("\n--- RESULTS ---")
    print(f"Fair Value per Share: {fair_value_per_share:.2f}")
    print(f"Offer Price: {offer_price:.2f}")
    print(f"Premium Paid (%): {premium_pct*100:.2f}%")
    print(f"Premium Paid (€): {premium:,.2f}")
    print(f"Maximum Sustainable Premium: {premium_max_pct*100:.2f}%")

    print(f"\nEPS pre-deal: {eps_pre:.4f}")
    print(f"EPS post-deal: {eps_post:.4f}")
    print(f"Accretion / Dilution: {accretion_pct*100:.2f}%")

    print(f"\nPro-forma Leverage: {leverage_post:.2f}x")

    print("\n--- IMPLIED DEAL MULTIPLES ---")
    print(f"Implied EV/EBITDA: {ev_ebitda_implied:.2f}x" if ev_ebitda_implied else "Implied EV/EBITDA: N/A")
    print(f"Implied P/E: {pe_implied:.2f}x" if pe_implied else "Implied P/E: N/A")

    # -----------------------------
    # SENSITIVITY ANALYSIS
    # -----------------------------
    print("\n--- SENSITIVITY ANALYSIS ---")

    # Synergies sensitivity
    for mult in [0.5, 0.75, 1.0]:
        sy = synergies * mult
        eps_post_s = (ni_buyer + ni_target + sy - new_interest) / shares_post
        acc = eps_post_s / eps_pre - 1
        print(f"Synergies {int(mult*100)}% -> Accretion: {acc*100:.2f}%")

    # Interest rate sensitivity
    for r in [interest_rate - 0.01, interest_rate, interest_rate + 0.01]:
        ni_post_r = ni_buyer + ni_target + synergies - (debt_financing * r)
        eps_post_r = ni_post_r / shares_post
        acc_r = eps_post_r / eps_pre - 1
        print(f"Interest rate {r*100:.1f}% -> Accretion: {acc_r*100:.2f}%")

    # -----------------------------
    # SAVE RESULTS
    # -----------------------------
    results.update({
        "enterprise_value_dcf": enterprise_value_target,
        "offer_price": offer_price,
        "enterprise_value_offer": ev_offer,
        "equity_value_offer": equity_value_offer,
        "equity_value_market": equity_value_market,
        "premium": premium,
        "premium_pct": premium_pct,
        "fair_value": fair_value_per_share,
        "premium_max_pct": premium_max_pct,
        "premium_paid_pct": premium_pct,
        "eps_pre": eps_pre,
        "eps_post": eps_post,
        "accretion_pct": accretion_pct,
        "leverage_post": leverage_post,
        "ev_ebitda_implied": ev_ebitda_implied,
        "pe_implied": pe_implied
    })

    return {
        "enterprise_value_dcf": enterprise_value_target,
        "enterprise_value_offer": ev_offer,
        "equity_value_offer": equity_value_offer,
        "equity_value_market": equity_value_market,
        "premium_paid_total": premium,
        "fair_value": fair_value_per_share,
        "premium_max_pct": premium_max_pct,
        "premium_paid_pct": premium_pct,
        "eps_pre": eps_pre,
        "eps_post": eps_post,
        "accretion_pct": accretion_pct,
        "leverage_post": leverage_post,
        "ev_ebitda_implied": ev_ebitda_implied,
        "pe_implied": pe_implied
    }

# ============================================================
# 2) Contribution analysis
# ============================================================

def contribution_analysis():

    global results
    
    print("\n--- CONTRIBUTION ANALYSIS ---")

    # -----------------------------
    # BUYER INPUTS
    # -----------------------------
    ebitda_buyer = results["ebitda_buyer"]
    ni_buyer =  results["ni_buyer"]
    ev_buyer = float(input("Insert BUYER Enterprise Value: "))

    # -----------------------------
    # TARGET INPUTS
    # -----------------------------
    ebitda_target = results["ebitda_target"]
    ni_target = results["ni_target"]
    ev_target = results["offer_price"]

    # -----------------------------
    # CONTRIBUTION CALCULATIONS
    # -----------------------------
    total_ebitda = ebitda_buyer + ebitda_target
    total_ni = ni_buyer + ni_target
    total_ev = ev_buyer + ev_target

    ebitda_contribution = ebitda_target / total_ebitda
    ni_contribution = ni_target / total_ni
    ev_contribution = ev_target / total_ev

    # -----------------------------
    # MULTIPLI IMPLICITI DEL DEAL
    # -----------------------------
    ev_ebitda_implied = ev_target / ebitda_target if ebitda_target != 0 else None
    pe_implied = ev_target / ni_target if ni_target != 0 else None

    # -----------------------------
    # OUTPUT
    # -----------------------------
    print("\n--- RESULTS ---")
    print(f"EBITDA Contribution (Target): {ebitda_contribution*100:.2f}%")
    print(f"Net Income Contribution (Target): {ni_contribution*100:.2f}%")
    print(f"Enterprise Value Contribution (Target): {ev_contribution*100:.2f}%")

    print("\n--- IMPLIED DEAL MULTIPLES ---")
    if ev_ebitda_implied:
        print(f"Implied EV/EBITDA: {ev_ebitda_implied:.2f}x")
    else:
        print("Implied EV/EBITDA: N/A (EBITDA = 0)")

    if pe_implied:
        print(f"Implied P/E: {pe_implied:.2f}x")
    else:
        print("Implied P/E: N/A (Net Income = 0)")

    # -----------------------------
    # DEAL FAIRNESS CHECK
    # -----------------------------
    print("\n--- DEAL FAIRNESS CHECK ---")

    if ev_contribution > ebitda_contribution * 1.5:
        print(" WARNING: Price paid is significantly higher than EBITDA contribution.")
    elif ev_contribution > ebitda_contribution:
        print(" Price paid is higher than EBITDA contribution.")
    else:
        print(" Price paid is aligned with EBITDA contribution.")

    if ev_contribution > ni_contribution * 1.5:
        print(" WARNING: Price paid is significantly higher than Net Income contribution.")
    elif ev_contribution > ni_contribution:
        print(" Price paid is higher than Net Income contribution.")
    else:
        print(" Price paid is aligned with Net Income contribution.")

    results.update({
    "ebitda_contribution": ebitda_contribution,
    "ni_contribution": ni_contribution,
    "ev_contribution": ev_contribution,
    "ev_ebitda_implied": ev_ebitda_implied,
    "pe_implied": pe_implied
    })

    return {
        "ebitda_contribution": ebitda_contribution,
        "ni_contribution": ni_contribution,
        "ev_contribution": ev_contribution,
        "EV/EBITDA_implied": ev_ebitda_implied,
        "P/E_implied": pe_implied
    }

# ============================================================
# 3) Summury
# ============================================================

def deal_summary(results):
    print("\n==================== DEAL SUMMARY ====================")

    # ----------------------------------------------------
    # 1) VALUTAZIONE (DCF)
    # ----------------------------------------------------
    print("\n--- VALUATION ---")
    print(f"Enterprise Value (DCF): {results['enterprise_value']:.2f}")
    print(f"Equity Value (DCF): {results['equity_value']:.2f}")
    print(f"Fair Value per Share: {results['fair_value']:.2f}")

    # ----------------------------------------------------
    # 2) OFFER PRICE & PREMIUM
    # ----------------------------------------------------
    print("\n--- OFFER & PREMIUM ---")
    print(f"Offer Price per Share: {results['offer_price']:.2f}")
    print(f"Premium Paid: {results['premium_pct']*100:.2f}%")
    print(f"Maximum Sustainable Premium: {results['premium_max_pct']*100:.2f}%")

    # ----------------------------------------------------
    # 3) RISK METRICS (BETA, KE, WACC)
    # ----------------------------------------------------
    print("\n--- RISK METRICS ---")
    print(f"Beta (static): {results['beta']:.3f}")

    # --- R² (gestione caso comparables) ---
    r2 = results.get("r2")
    if r2 is None:
        print("R²: N/A")
    else:
        print(f"R²: {r2:.3f}")

    print(f"Ke (CAPM): {results['ke']*100:.2f}%")
    print(f"WACC: {results['wacc']*100:.2f}%")

    # ----------------------------------------------------
    # 4) ACCRETION / DILUTION
    # ----------------------------------------------------
    print("\n--- ACCRETION / DILUTION ---")
    print(f"EPS pre-deal: {results['eps_pre']:.4f}")
    print(f"EPS post-deal: {results['eps_post']:.4f}")
    print(f"Accretion/Dilution: {results['accretion_pct']*100:.2f}%")

    # ----------------------------------------------------
    # 5) LEVERAGE
    # ----------------------------------------------------
    print("\n--- LEVERAGE ---")
    print(f"Pro-forma Net Debt / EBITDA: {results['leverage_post']:.2f}x")

    # ----------------------------------------------------
    # 6) IMPLIED DEAL MULTIPLES
    # ----------------------------------------------------
    print("\n--- IMPLIED DEAL MULTIPLES ---")
    print(f"Implied EV/EBITDA: {results['ev_ebitda_implied']:.2f}x")
    print(f"Implied P/E: {results['pe_implied']:.2f}x")

    # ----------------------------------------------------
    # 7) CONTRIBUTION ANALYSIS
    # ----------------------------------------------------
    print("\n--- CONTRIBUTION ANALYSIS ---")
    print(f"EBITDA Contribution: {results['ebitda_contribution']*100:.2f}%")
    print(f"Net Income Contribution: {results['ni_contribution']*100:.2f}%")
    print(f"Enterprise Value Contribution: {results['ev_contribution']*100:.2f}%")

    # ----------------------------------------------------
    # 8) FAIRNESS CHECK
    # ----------------------------------------------------
    print("\n--- DEAL FAIRNESS ---")
    if results['ev_contribution'] > results['ebitda_contribution'] * 1.5:
        print(" Deal overpriced vs EBITDA contribution.")
    else:
        print(" Price aligned with EBITDA contribution.")

    if results['ev_contribution'] > results['ni_contribution'] * 1.5:
        print(" Deal overpriced vs Net Income contribution.")
    else:
        print(" Price aligned with Net Income contribution.")

    # ----------------------------------------------------
    # 9) SENSITIVITY WACC / KE → EV
    # ----------------------------------------------------
    print("\n--- SENSITIVITY WACC / Ke → EV & Equity ---")
    print(results["sensitivity_table"])

    # ----------------------------------------------------
    # 10) BETA CHARTS (PATHS)
    # ----------------------------------------------------
    print("\n--- BETA CHARTS ---")

    if results.get("beta_regression_path"):
        print(f"Regression Beta Chart saved at: {results['beta_regression_path']}")
    else:
        print("Regression Beta Chart: N/A")

    if results.get("rolling_beta_path"):
        print(f"Rolling Beta Chart saved at: {results['rolling_beta_path']}")
    else:
        print("Rolling Beta Chart: N/A")

    # ----------------------------------------------------
    # 11) COMPARABLES – R² LIST
    # ----------------------------------------------------
    if "r2_list" in results and len(results["r2_list"]) > 0:
        print("\n--- COMPARABLE COMPANIES – R² ---")
        for comp, data in results["r2_list"].items():
            r2_val = data["r2"]
            r2_val = round(r2_val, 3) if r2_val is not None else "N/A"
            print(f"{comp}: R² = {r2_val}")

    print("\n======================================================")