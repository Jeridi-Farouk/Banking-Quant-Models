import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

ticker=input("insert the ticker that you want to study: ")
time=input("insert the time: ")

data=yf.download(ticker,period=time)
prices=data["Close"].values.squeeze()
print(prices)
x=np.diff(np.log(prices))
print(x)

plt.figure(figsize=(12,6))
plt.plot(x, color="royalblue", linewidth=1)
plt.title(f"{ticker} - Log Returns ({time})", fontsize=16)
plt.xlabel("Date")
plt.ylabel("Log Return")
plt.grid(alpha=0.3)
plt.show()

x_t=x[1:]
x_tm1=x[:-1]

n=len(x_t)

z = np.column_stack([np.ones(n), x_tm1])
print(z)
ztz=np.transpose(z)@z
ztb=np.transpose(z)@x_t
a=ztz[0,0]
b=ztz[0,1]
c=ztz[1,0]
d=ztz[1,1]
e=ztb[0]
f=ztb[1]

pivot=a
multipl=c/pivot
d_new=d-b*multipl
f_new=f-e*multipl
phi_1=f_new/d_new
phi_0=(e-phi_1*b)/a

residui=x_t-(phi_0+phi_1*x_tm1)
print(residui.mean())
print(residui.var())

plt.figure(figsize=(12,6))
plt.plot( residui, color="royalblue", linewidth=2)
plt.show()

n=50
forecast=[]
last_value=x[-1]

for i in range(n):
    next_value=phi_0+phi_1*last_value
    forecast.append(next_value)
    last_value=next_value

plt.figure(figsize=(12,6))

# Serie reale
plt.plot(x, label="Real Data", color="royalblue")

# Serie prevista
plt.plot(range(len(x), len(x)+n), forecast, label="Forecast", color="red")

plt.title("AR(1) Forecast")
plt.legend()
plt.grid(alpha=0.3)
plt.show()
print(forecast)

from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

plt.figure(figsize=(12,5))
plot_acf(x, lags=40)
plt.title("ACF")
plt.show()

plt.figure(figsize=(12,5))
plot_pacf(x, lags=40, method='ywm')
plt.title("PACF")
plt.show()





