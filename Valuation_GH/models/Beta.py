import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os

from models.globals import results

# ============================================================
# 1) STATIC BETA (REGRESSION)
# ============================================================
def get_beta_from_regression(stock_ticker, index_ticker, years=5):
    # Download data
    stock = yf.download(stock_ticker, period=f"{years}y")["Close"].pct_change().dropna()
    index = yf.download(index_ticker, period=f"{years}y")["Close"].pct_change().dropna()

    df = pd.concat([stock, index], axis=1).dropna()
    df.columns = ["stock", "index"]

    # Regression
    X = sm.add_constant(df["index"])
    model = sm.OLS(df["stock"], X).fit()
    beta = model.params["index"]
    r2 = model.rsquared

    # -----------------------------
    # PLOT REGRESSION
    # -----------------------------
    plt.figure(figsize=(8, 6))
    plt.scatter(df["index"], df["stock"], alpha=0.5, label="Daily returns")
    
    # Regression line
    x_vals = np.linspace(df["index"].min(), df["index"].max(), 100)
    y_vals = model.params["const"] + model.params["index"] * x_vals
    plt.plot(x_vals, y_vals, color="red", label=f"Regression line (β={beta:.3f})")

    plt.title(f"Regression: {stock_ticker} vs {index_ticker}\n"
              f"Beta={beta:.3f}, R²={r2:.3f}")
    plt.xlabel(f"{index_ticker} returns")
    plt.ylabel(f"{stock_ticker} returns")
    plt.legend()

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.join(output_dir, f"beta_regression_{stock_ticker}.png")
    plt.savefig(filename, dpi=300)
    plt.close()

    print(f"Regression image saved in: {filename}")
    print(f"R² of regression: {r2:.4f}")

    return beta, r2,filename


# ============================================================
# 2) ROLLING BETA
# ============================================================
def get_rolling_beta(stock_ticker, index_ticker, years=5, window=252):
    print("\n>>> GENERATING ROLLING BETA (ANALYSIS ONLY) <<<")

    # Download data
    stock = yf.download(stock_ticker, period=f"{years}y")["Close"].pct_change().dropna()
    index = yf.download(index_ticker, period=f"{years}y")["Close"].pct_change().dropna()

    df = pd.concat([stock, index], axis=1).dropna()
    df.columns = ["stock", "index"]

    betas = []

    # Rolling regression
    for i in range(window, len(df)):
        window_df = df.iloc[i-window:i]
        X = sm.add_constant(window_df["index"])
        model = sm.OLS(window_df["stock"], X).fit()
        betas.append(model.params["index"])

    betas = pd.Series(betas, index=df.index[window:])

    # -----------------------------
    # PLOT ROLLING BETA
    # -----------------------------
    plt.figure(figsize=(10, 5))
    plt.plot(betas, label="Rolling Beta", color="blue")
    plt.title(f"Rolling Beta ({window} days) - {stock_ticker}")
    plt.xlabel("Date")
    plt.ylabel("Beta")
    plt.grid(True)
    plt.legend()

    # Create output directory
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    filename_2 = os.path.join(output_dir, f"rolling_beta_{stock_ticker}.png")

    print("Saving rolling beta plot to:", os.path.abspath(filename_2))

    plt.savefig(filename_2, dpi=300)
    plt.close()

    print(f"Rolling beta plot saved in: {filename_2}")

    # IMPORTANTISSIMO:
    # Non ritorniamo nulla, perché il rolling beta NON deve influenzare il modello
    return filename_2



# ============================================================
# 3) MAIN BETA FUNCTION 
# ============================================================
def calculate_beta():
    global results
    print("\n--- BETA CALCULATION ---")
    print("1) Company is listed (market regression)")
    print("2) Company is NOT listed (comparable companies)")

    choice = input("Choose option (1/2): ").strip()

    # ---------------------------------------------------------
    # CASE 1: LISTED COMPANY
    # ---------------------------------------------------------
    if choice == "1":
        stock_ticker = input("Insert the company ticker: ").upper()
        index_ticker = input("Insert the index ticker: ").upper()

        # 1) Beta statico
        beta_value, r2, beta_path = get_beta_from_regression(stock_ticker, index_ticker)
        print(f"\nLevered Beta (static regression): {beta_value:.4f}")
        print(f"R²: {r2:.4f}")

        # 2) Rolling beta
        rolling_path = get_rolling_beta(stock_ticker, index_ticker)

        #SALVIAMO TUTTO NEI RESULTS
        results["beta"] = beta_value
        results["r2"] = r2
        results["beta_regression_path"] = beta_path
        results["rolling_beta_path"] = rolling_path

        #resettiamo la lista comparables
        results["r2_list"] = {}

        return beta_value, r2

    # ---------------------------------------------------------
    # CASE 2: PRIVATE COMPANY (COMPARABLES)
    # ---------------------------------------------------------
    elif choice == "2":
        n = int(input("How many comparable companies? "))

        betas_unlevered = []

        #inizializziamo la lista degli R²
        results["r2_list"] = {}

        for i in range(n):
            print(f"\nComparable {i+1} ------------------")

            comp_ticker = input("Insert comparable stock ticker: ").upper()
            index_ticker = input("Insert index ticker: ").upper()

            # Calcolo beta + R²
            beta_l, r2_l, beta_path = get_beta_from_regression(comp_ticker, index_ticker)
            print(f"Levered Beta: {beta_l:.4f} (R²={r2_l:.4f})")

            # Rolling beta
            rolling_path = get_rolling_beta(comp_ticker, index_ticker)

            #SALVIAMO R² + GRAFICI PER OGNI COMPARABLE
            results["r2_list"][comp_ticker] = {
                "r2": r2_l,
                "beta_path": beta_path,
                "rolling_path": rolling_path
            }

            # Capital structure
            equity = float(input("Insert comparable Equity Value: "))
            debt = float(input("Insert comparable Debt Value: "))

            beta_u = beta_l / (1 + (debt / equity))
            betas_unlevered.append(beta_u)

        # Media unlevered beta
        beta_u_avg = np.mean(betas_unlevered)
        print(f"\nAverage Unlevered Beta: {beta_u_avg:.4f}")

        # Target capital structure
        target_equity = float(input("Insert target company Equity Value: "))
        target_debt = float(input("Insert target company Debt Value: "))

        beta_relevered = beta_u_avg * (1 + (target_debt / target_equity))

        print(f"\nFinal Levered Beta for Target Company: {beta_relevered:.4f}")

        #SALVIAMO NEI RESULTS
        results["beta"] = beta_relevered
        results["r2"] = None  # compatibilità con deal_summary
        results["beta_regression_path"] = None
        results["rolling_beta_path"] = None

        return beta_relevered, None

    else:
        print("Invalid choice. Try again.")
        return calculate_beta()
