import numpy as np
import pandas as pd
import yfinance as yf

ticker=input("insert the ticker that you want to study: ")
time=input("insert the time: ")

data=yf.download(ticker,period=time)
prices=data["Close"].values.squeeze()
x=np.diff(np.log(prices))   # log-returns

def arma(x, phi_0, phi_1, theta_1):
    T = len(x)
    eps = np.zeros(T)
    eps[0] = 0.0
    for t in range(1, T):
        eps[t] = x[t] - phi_0 - phi_1*x[t-1] - theta_1*eps[t-1]
    return eps

def ssq(x, phi_0, phi_1, theta_1):
    eps = arma(x, phi_0, phi_1, theta_1)
    return np.sum(eps**2)

def cls(x, phi_0_grid, phi_1_grid, theta_1_grid):
    best_phi_0 = None
    best_phi_1 = None
    best_theta_1 = None
    best_ssq = np.inf

    for phi_0 in phi_0_grid:
        for phi_1 in phi_1_grid:
            for theta_1 in theta_1_grid:
                ssq_val = ssq(x, phi_0, phi_1, theta_1)
                if ssq_val < best_ssq:
                    best_ssq = ssq_val
                    best_phi_0 = phi_0
                    best_phi_1 = phi_1
                    best_theta_1 = theta_1

    return best_phi_0, best_phi_1, best_theta_1, best_ssq

phi_0_intervall = np.linspace(-1.0, 1.0, 20)
phi_1_intervall = np.linspace(-1.0, 1.0, 20)
theta_1_intervall = np.linspace(-1.0, 1.0, 20)

phi_0, phi_1, theta_1, ssq_min = cls(x, phi_0_intervall, phi_1_intervall, theta_1_intervall)

print("phi_0 =", phi_0)
print("phi_1 =", phi_1)
print("theta_1 =", theta_1)
print("ssq =", ssq_min)
