import sqlite3
import pandas as pd

from src.reports.peer_report import PeerComparisonReport


DB_PATH = "nifty100.db"

print("=" * 60)
print("PEER COMPARISON REPORT")
print("=" * 60)

# ------------------------------------------
# Connect Database
# ------------------------------------------

conn = sqlite3.connect(DB_PATH)

print("\nLoading Peer Ranking Data...")

try:

    peer_df = pd.read_sql(

        "SELECT * FROM peer_ranking",

        conn

    )

except Exception:

    print("peer_ranking table not found.")
    conn.close()
    raise

print("Rows :", len(peer_df))
print("Columns :", len(peer_df.columns))

# ------------------------------------------
# Run Report Generator
# ------------------------------------------

report = PeerComparisonReport(

    peer_df

)

report.run()

# ------------------------------------------
# Summary
# ------------------------------------------

print("\nPeer Comparison Reports Generated Successfully")

print("-" * 60)

print("Total Companies :", len(peer_df))

print("Output Folder : reports/peer_reports")

# ------------------------------------------
# Close Database
# ------------------------------------------

conn.close()

print("\nDatabase Connection Closed")

print("\nSprint 3 - Day 20 Completed Successfully")

print("=" * 60)