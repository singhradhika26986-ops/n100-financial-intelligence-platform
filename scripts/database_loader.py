import sqlite3
import pandas as pd

conn = sqlite3.connect("nifty100.db")

# Load Companies
companies = pd.read_csv("data/raw/companies.csv")

companies.columns = [
    "company_name",
    "industry",
    "symbol",
    "series",
    "isin_code"
]

companies.to_sql(
    "companies",
    conn,
    if_exists="append",
    index=False
)

print("Companies Loaded")

# Load Stock Prices
prices = pd.read_csv("data/raw/stock_prices.csv")

prices = prices.rename(
    columns={
        "Date": "trade_date",
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Adj Close": "adj_close",
        "Volume": "volume",
        "Symbol": "symbol"
    }
)

prices.to_sql(
    "stock_prices",
    conn,
    if_exists="append",
    index=False
)

print("Stock Prices Loaded")

conn.close()

print("Database Load Completed")