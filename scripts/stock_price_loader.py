import os
import time
import pandas as pd
import yfinance as yf

INPUT_FILE = "data/raw/companies.csv"
OUTPUT_FILE = "data/raw/stock_prices.csv"

companies = pd.read_csv(INPUT_FILE)

all_data = []

for symbol in companies["Symbol"]:

    ticker = symbol + ".NS"

    try:

        print(f"Downloading {ticker}")

        df = yf.download(
            ticker,
            period="5y",
            progress=False,
            auto_adjust=False
        )

        if df.empty:
            continue

        df = df.reset_index()

        # Fix MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df["Symbol"] = symbol

        all_data.append(df)

        time.sleep(0.3)

    except Exception as e:

        print(f"Error downloading {symbol}: {e}")

if all_data:

    final_df = pd.concat(all_data, ignore_index=True)

    os.makedirs("data/raw", exist_ok=True)

    final_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nDownload Complete")
    print(final_df.head())
    print("\nShape:", final_df.shape)

else:

    print("No data downloaded.")