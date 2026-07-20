import sqlite3
import pandas as pd

from src.analytics.radar import RadarChartEngine


DB_PATH = "nifty100.db"

print("=" * 60)
print("RADAR CHART ENGINE")
print("=" * 60)

# ------------------------------------------
# Connect Database
# ------------------------------------------

conn = sqlite3.connect(DB_PATH)

print("\nLoading Financial Ratios...")

financial_df = pd.read_sql(

    "SELECT * FROM financial_ratios",

    conn

)

print("Rows :", len(financial_df))
print("Columns :", len(financial_df.columns))

# ------------------------------------------
# Run Radar Chart Engine
# ------------------------------------------

engine = RadarChartEngine(

    financial_df

)

engine.run()

# ------------------------------------------
# Summary
# ------------------------------------------

print("\nRadar Chart Generation Completed")

print("-" * 60)

print("Total Companies :", len(financial_df))

print(
    "Output Folder : reports/radar_charts"
)

# ------------------------------------------
# Close Database
# ------------------------------------------

conn.close()

print("\nDatabase Connection Closed")

print("\nSprint 3 - Day 19 Completed Successfully")

print("=" * 60)