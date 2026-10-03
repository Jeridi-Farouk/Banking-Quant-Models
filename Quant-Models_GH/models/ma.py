import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from scipy.optimize import minimize

ticker=input("insert the ticker that you want to study: ")
time=input("insert the time: ")

data=yf.download(ticker,period=time)
prices=data["Close"].values.squeeze()
print(prices)
x=np.diff(np.log(prices))
mu=np.mean(x)
print(x)

def errors(theta,x,mu):
    theta=np.squeeze(theta)
    theta=float(theta)
    t=len(x)
    e=np.zeros(t)
    for t in range (1,t):
        e[t]=x[t]-mu-theta*e[t-1]
    return e

def loss(theta,x,mu):
    theta=np.squeeze(theta)
    theta=float(theta)
    e=errors(theta,x,mu)
    return np.sum(e**2)

res=minimize(lambda th:loss(th,x,mu),x0=0.0)
theta_hat=res.x[0]

e=errors(theta_hat,x,mu)

plt.figure(figsize=(12,6))
plt.plot( e, color="royalblue", linewidth=2)
plt.show()

forecast=mu+theta_hat*e[-1]
print(forecast)
