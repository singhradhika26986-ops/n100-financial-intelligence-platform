import sqlite3
import pandas as pd

from src.analytics.peer import PeerRankingEngine


DB_PATH = "nifty100.db"

print("=" * 60)
print("PEER RANKING ENGINE")
print("=" * 60)

# ----------------------------------------
# Connect Database
# ----------------------------------------

conn = sqlite3.connect(DB_PATH)

print("\nLoading Financial Ratios...")

financial_df = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

print("Rows :", len(financial_df))
print("Columns :", len(financial_df.columns))

# ----------------------------------------
# Run Peer Ranking Engine
# ----------------------------------------

engine = PeerRankingEngine(
    financial_df
)

peer_df = engine.run()

# ----------------------------------------
# Save To SQLite
# ----------------------------------------

engine.save_to_database(conn)

print("\nPeer Ranking Saved To Database")

# ----------------------------------------
# Export To Excel
# ----------------------------------------

output_file = "output/peer_ranking.xlsx"

peer_df.to_excel(
    output_file,
    index=False
)

print(f"\nExcel File Saved : {output_file}")

# ----------------------------------------
# Top 20 Companies
# ----------------------------------------

print("\nTop 20 Companies")

display_columns = [
    "Company",
    "Peer Score",
    "Overall Rank",
    "Peer Rating"
]

available_columns = [
    col for col in display_columns
    if col in peer_df.columns
]

print(
    peer_df[available_columns]
    .head(20)
)

# ----------------------------------------
# Summary
# ----------------------------------------

print("\nSummary")
print("-" * 40)

print("Total Companies :", len(peer_df))
print("Average Peer Score :", round(peer_df["Peer Score"].mean(), 2))
print("Highest Peer Score :", round(peer_df["Peer Score"].max(), 2))
print("Lowest Peer Score :", round(peer_df["Peer Score"].min(), 2))

print("\nPeer Ranking Completed Successfully")

# ----------------------------------------
# Close Database
# ----------------------------------------

conn.close()

print("Database Connection Closed")