import pandas as pd
import numpy as np
import yfinance as yf

from models.globals import results

# ============================================================
# 1) RISK FREE
# ============================================================

def risk_free():

    global results

    rf=float(input("Enter the risk free value: "))

    results["Risk Free"]=rf

    return rf

# ============================================================
# 2) EQUITY RISK PREMIUM
# ============================================================

def calculate_erp_from_market(rf, years=10):

    global results

    #Downloading
    print(f"\nDownloading market index data for the last {years} years...")

    while True:
        ticker = input("Insert the ticker of the index: ").strip().upper()

        try:
            data = yf.download(ticker, period=f"{years}y")

            # Check if the download returned data
            if data.empty:
                print("Invalid ticker or no data available. Please try again.")
                continue

            # Check if the Close column exists
            if "Close" not in data.columns:
                print("The selected ticker does not contain a 'Close' column. Please try again.")
                continue

            # Daily returns
            data["Returns"] = data["Close"].pct_change()

            # Annualized return (CAGR)
            cumulative_return = (1 + data["Returns"].dropna()).prod()
            annualized_return = cumulative_return ** (1 / years) - 1

            erp = annualized_return - rf

            print(f"\nAnnualized return of {ticker}: {annualized_return:.4f}")
            print(f"Risk-free rate used: {rf:.4f}")
            print(f"Calculated ERP: {erp:.4f}")

            results["ERP"]=erp

            return erp

        except Exception as e:
            print(f"Error while downloading data: {e}")
            print("Please insert a valid ticker.")



