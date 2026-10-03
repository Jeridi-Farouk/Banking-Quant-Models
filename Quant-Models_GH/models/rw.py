import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.stats import norm
import yfinance as yf


def simulate_random_walk(
    n_steps: int,
    y0: float = 0.0,
    sigma: float = 1.0,
    random_seed: int | None = None,
    show_plot: bool = True,
    save_plot: bool = True
) -> np.ndarray:
    """
    Simula un random walk discreto e salva il grafico in output/.
    """

    if n_steps <= 0:
        raise ValueError("n_steps deve essere > 0")
    if sigma < 0:
        raise ValueError("sigma deve essere >= 0")

    if random_seed is not None:
        np.random.seed(random_seed)

    # incrementi ~ N(0, sigma^2)
    eps = np.random.normal(loc=0.0, scale=sigma, size=n_steps)

    # path: Y_0, Y_1, ..., Y_n
    path = np.empty(n_steps + 1)
    path[0] = y0
    path[1:] = y0 + np.cumsum(eps)

    # grafico
    plt.figure(figsize=(10, 5))
    plt.plot(path, label="Random Walk")
    plt.title("Random Walk Simulation")
    plt.xlabel("Step")
    plt.ylabel("Value")
    plt.grid(True)
    plt.legend()

    # --- SALVATAGGIO NELLA CARTELLA output/ ---
    if save_plot:
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        filename = os.path.join(output_dir, "random_walk.png")
        plt.savefig(filename, dpi=300)
        print(f"Graph saved here: {filename}")

    if show_plot:
        plt.show()
    else:
        plt.close()

    return path


def price_call_from_ticker(ticker, K, r, T, n, lookback_days=252):
    """
    Pricing di una call Bachelier usando:
    - ticker reale
    - volatilità storica annualizzata
    - ultimo prezzo come S0
    - random walk discreto
    """

    # ============================
    # 1. SCARICO I DATI DEL TICKER
    # ============================
    data = yf.download(ticker, period=f"{lookback_days}d")
    if data.empty:
        raise ValueError("Ticker non valido o dati non disponibili.")

    close_prices = data["Close"]

    # ============================
    # 2. CALCOLO VOLATILITÀ STORICA
    # ============================
    returns = close_prices.pct_change().dropna()
    vol_annual = float(returns.std().values[0] * np.sqrt(252))  # volatilità annualizzata %

    # ============================
    # 3. PREZZO SPOT S0
    # ============================
    S0 =  float(close_prices.iloc[-1].values[0])

    # ============================
    # 4. CONVERSIONE VOL → σ PER STEP
    # ============================
    sigma_T_abs = vol_annual * S0 * np.sqrt(T)  # deviazione assoluta a scadenza
    sigma_step = sigma_T_abs / np.sqrt(n)       # deviazione per step

    # ============================
    # 5. RANDOM WALK BACHELIER
    # ============================
    dt = T / n
    a = (S0 * np.exp(r * T) - S0) / n  # drift risk-neutral

    S = np.zeros(n + 1)
    S[0] = S0

    eps = np.random.normal(0, sigma_step, n)

    for i in range(1, n + 1):
        S[i] = S[i-1] + a + eps[i-1]

    # Parametri finali
    mu = S0 + n * a
    sigma_T = np.sqrt(n) * sigma_step

    # ============================
    # 6. FORMULA BACHELIER
    # ============================
    d = (mu - K) / sigma_T
    call_price = np.exp(-r * T) * ((mu - K) * norm.cdf(d) + sigma_T * norm.pdf(d))

    # ============================
    # 7. STAMPA RISULTATI
    # ============================
    print("\n===== RISULTATI PRICING DA TICKER =====")
    print(f"Ticker:               {ticker}")
    print(f"Prezzo spot S0:       {S0:.4f}")
    print(f"Volatilità annuale:   {vol_annual:.4f}")
    print(f"Deviazione sigma_T:   {sigma_T:.4f}")
    print(f"Media finale mu:      {mu:.4f}")
    print(f"Drift per step a:     {a:.6f}")
    print(f"Call price:           {call_price:.4f}")
    print("========================================\n")

    # ============================
    # 8. SALVATAGGIO OUTPUT
    # ============================
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    results_path = os.path.join(output_dir, f"{ticker}_results.txt")
    with open(results_path, "w") as f:
        f.write("===== RISULTATI PRICING DA TICKER =====\n")
        f.write(f"Ticker:               {ticker}\n")
        f.write(f"Prezzo spot S0:       {S0:.4f}\n")
        f.write(f"Volatilità annuale:   {vol_annual:.4f}\n")
        f.write(f"Deviazione sigma_T:   {sigma_T:.4f}\n")
        f.write(f"Media finale mu:      {mu:.4f}\n")
        f.write(f"Drift per step a:     {a:.6f}\n")
        f.write(f"Call price:           {call_price:.4f}\n")
        f.write("========================================\n")

    print(f"Risultati salvati in: {results_path}")

    # ============================
    # 9. GRAFICO DEL PERCORSO
    # ============================
    plt.figure(figsize=(10,5))
    plt.plot(S, label="Percorso simulato di S")
    plt.axhline(mu, color='red', linestyle='--', label="Media teorica μ")
    plt.title(f"Random Walk del sottostante {ticker}")
    plt.xlabel("Step")
    plt.ylabel("S")
    plt.legend()
    plt.grid(True)

    plot_path = os.path.join(output_dir, f"{ticker}_path.png")
    plt.savefig(plot_path, dpi=300)
    plt.show()

    print(f"Grafico salvato in: {plot_path}")

    return call_price, mu, sigma_T, a


import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.stats import norm
import pandas as pd
import os

def price_call_from_ticker_gbm_mc(ticker, K, r, T, n_steps, n_paths=10000, lookback_days=252):
    """
    Pricing di una call con:
    - GBM (lognormale)
    - volatilità da rendimenti logaritmici
    - Monte Carlo (nessuna formula BS)
    """

    # 1. Dati storici
    data = yf.download(ticker, period=f"{lookback_days}d")
    if data.empty:
        raise ValueError("Ticker non valido o dati non disponibili.")
    close_prices = data["Close"]

    # 2. Volatilità da rendimenti logaritmici
    log_ret = np.log(close_prices / close_prices.shift(1)).dropna()
    std_val = log_ret.std()
    if isinstance(std_val, (pd.Series, np.ndarray, list)):
        sigma_annual = float(std_val.values[0] * np.sqrt(252))
    else:
        sigma_annual = float(std_val * np.sqrt(252))

    # 3. Prezzo spot S0
    last_row = close_prices.iloc[-1]
    if isinstance(last_row, (pd.Series, np.ndarray, list)):
        S0 = float(last_row.values[0])
    else:
        S0 = float(last_row)

    # 4. Parametri GBM
    dt = T / n_steps
    sigma = sigma_annual
    mu_rn = r - 0.5 * sigma**2

    # 5. Simulazione Monte Carlo (solo terminale)
    #   Simulo direttamente S_T con lognormale
    Z = np.random.normal(0, 1, n_paths)
    ST = S0 * np.exp(mu_rn * T + sigma * np.sqrt(T) * Z)

    payoff = np.maximum(ST - K, 0)
    call_price_mc = np.exp(-r * T) * payoff.mean()

    # 6. Un percorso singolo per il grafico (random walk lognormale)
    S_path = np.zeros(n_steps + 1)
    S_path[0] = S0
    eps = np.random.normal(0, 1, n_steps)
    for i in range(1, n_steps + 1):
        S_path[i] = S_path[i-1] * np.exp(mu_rn * dt + sigma * np.sqrt(dt) * eps[i-1])

    # 7. Output
    print("\n===== RISULTATI PRICING GBM MONTE CARLO =====")
    print(f"Ticker:               {ticker}")
    print(f"Prezzo spot S0:       {S0:.4f}")
    print(f"Volatilità annuale:   {sigma:.4f}")
    print(f"Call price MC:        {call_price_mc:.4f}")
    print("=============================================\n")

    # 8. Grafico percorso
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(10,5))
    plt.plot(S_path, label="Percorso simulato GBM")
    plt.title(f"Random Walk Lognormale (GBM) - {ticker}")
    plt.xlabel("Step")
    plt.ylabel("S")
    plt.grid(True)
    plt.legend()

    plot_path = os.path.join(output_dir, f"{ticker}_gbm_mc_path.png")
    plt.savefig(plot_path, dpi=300)
    plt.show()

    print(f"Grafico salvato in: {plot_path}")

    return call_price_mc, sigma 