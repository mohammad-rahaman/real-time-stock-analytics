import yfinance as yf

def load_stock_data(symbol, period):
    stock = yf.Ticker(symbol)
    return stock.history(period=period)