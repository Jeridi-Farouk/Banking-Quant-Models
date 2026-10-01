
#### Library ####

import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from models.globals import results

#### Risk Free ####

from models.Risk_free_erp import risk_free

rf = risk_free()

#### ERP ####

from models.Risk_free_erp import calculate_erp_from_market

erp = calculate_erp_from_market(rf)

#### Beta ####

from models.Beta import calculate_beta

beta, r2 = calculate_beta()

#### ke ####

from models.Ke import calculate_ke

ke = calculate_ke(rf,erp,beta)

#### Kd ####

from models.Kd import calculate_kd

kd = calculate_kd(rf)

#### WACC ####

from models.wacc import calculate_wacc

wacc = calculate_wacc(ke,kd)

#### READ THE CF ####

df = pd.read_excel("input/flussi.xlsx",sheet_name="FLUSSI",index_col=0)

print(df)

#### Enterprise/Equity valuation ####

from models.Valuation import valuation_engine_dual,sensitivity_valuation

ev , eq_v  = valuation_engine_dual(df,"FCFF","FCFE",wacc,ke)

delta_list = [-0.01,-0.005,-0.001,0,0.001,0.005,0.01]

sensitivity_valuation(df,"FCFF","FCFE",wacc,ke,delta_list)

#### M&A analysis ####

from models.ma import accretion_dilution,contribution_analysis,deal_summary

accretion_dilution(ev)
contribution_analysis()

from models.globals import results

deal_summary(results)




from models.pdf import generate_pdf

generate_pdf()