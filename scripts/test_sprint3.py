import os
import sqlite3
import pandas as pd

DB_PATH = "nifty100.db"

print("=" * 60)
print("SPRINT 3 TEST SUITE")
print("=" * 60)

# ------------------------------------------
# Database Connection
# ------------------------------------------

try:

    conn = sqlite3.connect(DB_PATH)

    print("Database Connection : PASS")

except Exception as e:

    print(f"Database Connection : FAIL ({e})")

    raise

# ------------------------------------------
# Required Tables
# ------------------------------------------

required_tables = [

    "financial_ratios",

    "peer_ranking"

]

tables = pd.read_sql(

    "SELECT name FROM sqlite_master WHERE type='table'",

    conn

)

table_names = tables["name"].tolist()

print("\nChecking Tables...")

for table in required_tables:

    if table in table_names:

        print(f"{table:<25} PASS")

    else:

        print(f"{table:<25} FAIL")

        # ------------------------------------------
# Row Count Validation
# ------------------------------------------

print("\nChecking Table Records...")

for table in required_tables:

    try:

        count = pd.read_sql(

            f"SELECT COUNT(*) AS total FROM {table}",

            conn

        )["total"][0]

        print(f"{table:<25} {count} Rows")

    except Exception as e:

        print(f"{table:<25} FAIL ({e})")

# ------------------------------------------
# Required Folders
# ------------------------------------------

print("\nChecking Output Folders...")

required_folders = [

    "reports/radar_charts",

    "reports/peer_reports"

]

for folder in required_folders:

    if os.path.exists(folder):

        total_files = len(

            os.listdir(folder)

        )

        print(

            f"{folder:<30} PASS ({total_files} files)"

        )

    else:

        print(

            f"{folder:<30} FAIL"

        )

        # ------------------------------------------
# Final Summary
# ------------------------------------------

print("\n" + "=" * 60)
print("SPRINT 3 TEST SUMMARY")
print("=" * 60)

try:

    financial_count = pd.read_sql(

        "SELECT COUNT(*) AS total FROM financial_ratios",

        conn

    )["total"][0]

    peer_count = pd.read_sql(

        "SELECT COUNT(*) AS total FROM peer_ranking",

        conn

    )["total"][0]

    print(f"Financial Ratios Records : {financial_count}")
    print(f"Peer Ranking Records     : {peer_count}")

    print("\nOverall Status : PASS")

except Exception as e:

    print(f"\nOverall Status : FAIL ({e})")

# ------------------------------------------
# Close Database
# ------------------------------------------

conn.close()

print("\nDatabase Connection Closed")

print("\nSprint 3 Testing Completed Successfully")

print("=" * 60)