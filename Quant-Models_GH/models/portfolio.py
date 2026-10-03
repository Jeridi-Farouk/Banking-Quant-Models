import yfinance as yf
import pandas as pd

# -----------------------------
# 1) TICKER LIST (metti la tua)
# -----------------------------
tickers = [
"MMM","AOS","ABT","ABBV","ACN","ATVI","ADM","ADBE","ADP","AAP","AES","AFL","A","APD","AKAM","ALK","ALB","ARE","ALGN","ALLE","LNT","ALL","GOOGL","GOOG","MO","AMZN","AMCR","AEE","AAL","AEP","AXP","AIG","AMT","AWK","AMP","ABC","AME","AMGN","APH","ADI","ANSS","AON","APA","AAPL","AMAT","APTV","ANET","AJG","AIZ","T","ATO","ADSK","AZO","AVB","AVY","BKR","BALL","BAC","BBWI","BAX","BDX","BRK.B","BBY","BIO","TECH","BIIB","BLK","BK","BA","BKNG","BWA","BXP","BSX","BMY","AVGO","BR","BRO","BF.B","BG","CHRW","CDNS","CZR","CPB","COF","CAH","KMX","CCL","CARR","CTLT","CAT","CBOE","CBRE","CDW","CE","CNC","CNP","CDAY","CF","CRL","SCHW","CHD","CI","CINF","CTAS","CSCO","C","CFG","CLX","CME","CMS","KO","CTSH","CL","CMCSA","CMA","CAG","COP","ED","STZ","CEG","COO","CPRT","GLW","CTVA","CSGP","COST","CRWS","CSX","CMI","CVS","DHR","DRI","DVA","DE","DAL","XRAY","DVN","DXCM","FANG","DLR","DFS","DIS","DG","DLTR","D","DPZ","DOV","DOW","DTE","DUK","DD","DXC","EMN","ETN","EBAY","ECL","EIX","EW","EA","ELV","LLY","EMR","ENPH","ETR","EOG","EPAM","EQT","EFX","EQIX","EQR","ESS","EL","ETSY","EVRG","ES","EXC","EXPE","EXPD","EXR","XOM","FFIV","FDS","FICO","FAST","FRT","FDX","FITB","FSLR","FE","FMC","F","FTNT","FTV","FOXA","FOX","BEN","FCX","GRMN","IT","GE","GEHC","GEN","GNRC","GD","GIS","GM","GPC","GILD","GPN","GL","GS","HAL","HIG","HAS","HCA","PEAK","HSIC","HSY","HES","HPE","HLT","HOLX","HD","HON","HRL","HST","HWM","HPQ","HUM","HBAN","HII","IBM","IEX","IDXX","ITW","ILMN","INCY","IR","INTC","ICE","IFF","IP","IPG","INTU","ISRG","IVZ","IQV","IRM","JBHT","JBL","JKHY","J","JNJ","JCI","JPM","JNPR","K","KVUE","KDP","KEY","KEYS","KMB","KIM","KMI","KLAC","KHC","KR","LHX","LH","LRCX","LW","LVS","LDOS","LEN","LIN","LYV","LKQ","LMT","L","LOW","LUMN","LYB","MTB","MRO","MPC","MKTX","MAR","MMC","MLM","MAS","MA","MTCH","MKC","MCD","MCK","MDT","MRK","META","MET","MTD","MGM","MCHP","MU","MSFT","MAA","MRNA","MHK","MOH","TAP","MDLZ","MPWR","MNST","MCO","MS","MOS","MSI","MSCI","NDAQ","NTAP","NFLX","NWL","NEM","NWSA","NWS","NEE","NKE","NI","NDSN","NSC","NTRS","NOC","NCLH","NOV","NRG","NUE","NVDA","NVR","NXPI","ORLY","OXY","ODFL","OMC","ON","OKE","ORCL","OGN","OTIS","PCAR","PKG","PANW","PARA","PH","PAYX","PAYC","PYPL","PNR","PEP","PFE","PCG","PM","PSX","PNW","PXD","PNC","POOL","PPG","PPL","PFG","PG","PGR","PLD","PRU","PEG","PTC","PSA","PHM","PVH","QRVO","QCOM","PWR","DGX","RL","RJF","RTX","O","REG","REGN","RF","RSG","RMD","RHI","ROK","ROL","ROP","ROST","RCL","SPGI","CRM","SBAC","SLB","STX","SEE","SRE","NOW","SHW","SPG","SWKS","SJM","SNA","SOLV","SO","LUV","SWK","SBUX","STT","STE","SYK","SIVB","SYF","SNPS","SYY","TMUS","TROW","TTWO","TPR","TRGP","TREX","TYL","TSCO","TT","TDG","TRV","TRMB","TFC","TSLA","TXN","TXT","TMO","TJX","TSN","USB","UDR","ULTA","UNP","UAL","UPS","URI","UNH","UHS","VLO","VTR","VRSN","VRSK","VZ","VRTX","VTRS","VICI","V","VMC","WRB","GWW","WBD","WBA","WMT","WAT","WEC","WFC","WELL","WST","WDC","WU","WRK","WY","WHR","WMB","WTW","WYNN","XEL","XYL","YUM","ZBRA","ZBH","ZION","ZTS"
]

import yfinance as yf
import numpy as np
import pandas as pd

# -----------------------------
# 1) INDICE S&P500
# -----------------------------
sp500 = yf.download("^GSPC", start="2021-01-01")["Close"].dropna()

# Rendimenti giornalieri dell'indice → array
sp500_returns = sp500.pct_change().dropna().to_numpy()

# Media giornaliera dell'indice (SCALARE)
sp500_mean = np.mean(sp500_returns)

print("Rendimento medio S&P500 (giornaliero):", sp500_mean)

# -----------------------------
# 2) TICKER
# -----------------------------
data = yf.download(tickers, start="2021-01-01")["Close"]

# Elimina colonne con NaN
data = data.dropna(axis=1, how="any")

# Rendimenti giornalieri dei ticker
returns = data.pct_change().dropna()

# Media giornaliera per ogni ticker → Series
mean_returns = returns.mean()

# Versione vettoriale (array) dei rendimenti medi
mean_vec = mean_returns.to_numpy()

# -----------------------------
# 3) FILTRO: TICKER CHE BATTONO L'INDICE
# -----------------------------
mask = mean_vec >= sp500_mean

# Ticker selezionati (come lista)
selected_tickers = mean_returns.index[mask]

# Rendimenti medi selezionati (come Series)
selected = mean_returns[mask]

print("\nTicker che battono l'indice:")
print(selected)

print("\nNumero ticker selezionati:", len(selected_tickers))
print("\nLista ticker selezionati:")
print(list(selected_tickers))

