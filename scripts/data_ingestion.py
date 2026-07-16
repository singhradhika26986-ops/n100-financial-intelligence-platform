import os
import requests
import pandas as pd

DATA_DIR = "data/raw"
os.makedirs(DATA_DIR, exist_ok=True)

url = "https://archives.nseindia.com/content/indices/ind_nifty100list.csv"

print("Downloading Nifty 100 company list...")

try:
    df = pd.read_csv(url)

    df.to_csv(
        os.path.join(DATA_DIR, "companies.csv"),
        index=False
    )

    print(f"Downloaded {len(df)} companies.")
    print(df.head())

except Exception as e:
    print(e)