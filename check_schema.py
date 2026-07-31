import sqlite3

conn = sqlite3.connect("nifty100.db")

tables = [
    "companies",
    "financial_ratios",
    "balance_sheet",
    "income_statement",
    "cash_flow",
]

for table in tables:
    print("\n" + "=" * 60)
    print(table)
    print("=" * 60)

    cursor = conn.execute(f"PRAGMA table_info({table});")

    for row in cursor.fetchall():
        print(row)

print("\n" + "=" * 60)
print("SAMPLE DATA - financial_ratios")
print("=" * 60)

cursor = conn.execute("SELECT * FROM financial_ratios LIMIT 1")

print([col[0] for col in cursor.description])
print(cursor.fetchone())

conn.close()