from models.rw import simulate_random_walk,price_call_from_ticker,price_call_from_ticker_gbm_mc

simulate_random_walk(10000,0)

ticker="AAPL"
price_call_from_ticker(ticker,100,0.028,1,1000)

price_call_from_ticker_gbm_mc(ticker,100,0.028,1,1000)