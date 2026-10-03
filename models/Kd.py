import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import math 

from models.globals import results

# ============================================================
# 1) NEWTHON-RAPHSON METHOD
# ============================================================

def ytm_newton(price, face_value, years, freq=1, coupon_rate=None, coupon_amount=None,
               tol=1e-6, max_iter=100):
    
    global results

    """
    price: prezzo del bond
    face_value: valore nominale rimborsato a scadenza
    years: anni alla scadenza
    freq: numero di cedole per anno (1, 2, 4, 12)
    coupon_rate: tasso cedolare annuale (es. 0.05)
    coupon_amount: importo cedola per periodo (es. 2.5)
    """

    # Numero di periodi totali
    periods = int(years * freq)

    # Determina la cedola periodica
    if coupon_amount is not None:
        coupon = coupon_amount
    elif coupon_rate is not None:
        coupon = (coupon_rate * face_value) / freq
    else:
        raise ValueError("Devi inserire coupon_rate oppure coupon_amount")

    # Guess iniziale
    y = 0.05

    for _ in range(max_iter):
        # Funzione del prezzo
        f = sum([coupon / (1 + y/freq)**t for t in range(1, periods+1)]) \
            + face_value / (1 + y/freq)**periods - price

        # Derivata
        df = sum([-t * coupon / (1 + y/freq)**(t+1) * (1/freq)
                  for t in range(1, periods+1)]) \
             - periods * face_value / (1 + y/freq)**(periods+1) * (1/freq)

        y_new = y - f / df

        if abs(y_new - y) < tol:
            return y_new  # YTM annualizzato

        y = y_new

    return y

# ============================================================
# 2) COST OF DEBT
# ============================================================

def calculate_kd(rf):
    print("\n--- COST OF DEBT (Kd) CALCULATION ---")
    print("1) From financial statements (Interest Expense / Debt)")
    print("2) User-defined Kd")
    print("3) Rating-based Kd (user provides spread)")
    print("4) Newton–Raphson (bond YTM)")

    choice = input("Choose option (1/2/3/4): ")

    # ---------------------------------------------------------
    # 1) From financial statements
    # ---------------------------------------------------------
    if choice == "1":
        interest_expense = float(input("Insert Interest Expense: "))
        debt = float(input("Insert Total Debt: "))
        kd = interest_expense / debt
        print(f"\nKd from financial statements: {kd:.4f}")

        results["kd"]=kd
        
        return kd

    # ---------------------------------------------------------
    # 2) User-defined Kd
    # ---------------------------------------------------------
    elif choice == "2":
        kd = float(input("Insert Kd (decimal): "))
        print(f"\nUser-defined Kd: {kd:.4f}")

        results["kd"]=kd

        return kd

    # ---------------------------------------------------------
    # 3) Rating-based Kd (user provides spread)
    # ---------------------------------------------------------
    elif choice == "3":
        rating = input("Insert credit rating (e.g., BBB, BB+, A-): ").upper()
        spread = float(input("Insert credit spread (decimal): "))

        kd = rf + spread

        print(f"\nRating: {rating}")
        print(f"Spread provided: {spread:.4f}")
        print(f"Risk-free: {rf:.4f}")
        print(f"Rating-based Kd: {kd:.4f}")

        results["kd"]=kd

        return kd

    # ---------------------------------------------------------
    # 4) Newton–Raphson YTM (professional version)
    # ---------------------------------------------------------
    elif choice == "4":
        print("\n--- BOND INPUTS FOR YTM ---")

        price = float(input("Insert bond market price: "))
        face = float(input("Insert face value (nominal): "))
        years = float(input("Insert years to maturity: "))
        freq = int(input("Insert number of coupons per year (1, 2, 4, 12): "))

        print("\nChoose coupon input method:")
        print("1) Annual coupon rate (e.g., 0.05)")
        print("2) Coupon amount per period (e.g., 2.5)")

        c_choice = input("Choose (1/2): ")

        if c_choice == "1":
            coupon_rate = float(input("Insert annual coupon rate (decimal): "))
            coupon_amount = None
        else:
            coupon_amount = float(input("Insert coupon amount per period: "))
            coupon_rate = None

        kd = ytm_newton(
        price=price,
        face_value=face,
        years=years,
        freq=freq,
        coupon_rate=coupon_rate,
        coupon_amount=coupon_amount
        )

        print(f"\nYTM (Kd) from Newton–Raphson: {kd:.4f}")

        results["kd"]=kd
        
        return kd