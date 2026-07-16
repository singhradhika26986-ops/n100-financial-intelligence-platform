import sqlite3
import pandas as pd

from src.analytics.ratios import RatioCalculator
from src.analytics.cagr import CAGRCalculator
from src.analytics.cashflow_kpis import CashFlowKPI
from src.analytics.capital_allocation import CapitalAllocation


DB_PATH = "nifty100.db"

conn = sqlite3.connect(DB_PATH)

print("Loading financial statements...")
# Load tables from database

balance_sheet = pd.read_sql(
    "SELECT * FROM balance_sheet",
    conn
)

income_statement = pd.read_sql(
    "SELECT * FROM income_statement",
    conn
)

cash_flow = pd.read_sql(
    "SELECT * FROM cash_flow",
    conn
)

print("Balance Sheet :", balance_sheet.shape)
print("Income Statement :", income_statement.shape)
print("Cash Flow :", cash_flow.shape)
# Merge Financial Statements

financial_df = balance_sheet.merge(
    income_statement,
    on=["symbol", "report_date"],
    how="inner"
)

financial_df = financial_df.merge(
    cash_flow,
    on=["symbol", "report_date"],
    how="inner"
)

print("Merged Shape :", financial_df.shape)
print(financial_df.head())
# Rename columns for Ratio Engine

financial_df = financial_df.rename(
    columns={
        "revenue": "revenue",
        "ebit": "ebit",
        "total_assets": "total_assets",
        "total_debt": "total_debt",
        "shareholders_equity": "shareholders_equity",
        "operating_cash_flow": "operating_cash_flow",
        "capital_expenditure": "capital_expenditure"
    }
)

# Net Profit
financial_df["net_profit"] = financial_df["ebit"]

# Operating Profit
financial_df["operating_profit"] = financial_df["ebit"]

# Capital Employed
financial_df["capital_employed"] = (
    financial_df["shareholders_equity"]
    + financial_df["total_debt"]
)

print("\nColumns Ready For Ratio Engine\n")
print(financial_df.columns.tolist())
# ===========================
# Ratio Engine
# ===========================

ratio_engine = RatioCalculator(financial_df)

financial_df = ratio_engine.run()

print("\nRatio Engine Completed")
print(financial_df.head())
# ===========================
# CAGR Engine
# ===========================

# Dummy start/end values for initial testing
financial_df["revenue_start"] = financial_df["revenue"] * 0.80
financial_df["revenue_end"] = financial_df["revenue"]

financial_df["pat_start"] = financial_df["net_profit"] * 0.80
financial_df["pat_end"] = financial_df["net_profit"]

financial_df["eps_start"] = financial_df["eps"] * 0.80
financial_df["eps_end"] = financial_df["eps"]

financial_df["years"] = 5

cagr_engine = CAGRCalculator(financial_df)

financial_df = cagr_engine.run()

print("\nCAGR Engine Completed")
print(
    financial_df[
        [
            "Revenue CAGR",
            "PAT CAGR",
            "EPS CAGR"
        ]
    ].head()
)
# ===========================
# Cash Flow KPI Engine
# ===========================

cashflow_engine = CashFlowKPI(financial_df)

financial_df = cashflow_engine.run()

print("\nCash Flow KPI Completed")

print(
    financial_df[
        [
            "Free Cash Flow",
            "OCF Margin",
            "Cash Conversion Ratio"
        ]
    ].head()
)
# ===========================
# Capital Allocation Engine
# ===========================

capital_engine = CapitalAllocation(financial_df)

financial_df = capital_engine.run()

print("\nCapital Allocation Completed")

print(financial_df.columns.tolist())
# ===========================
# Save Financial Ratios
# ===========================

print("\nSaving financial ratios to SQLite...")

financial_df.to_sql(
    "financial_ratios",
    conn,
    if_exists="replace",
    index=False
)

print("financial_ratios table saved successfully.")

rows = pd.read_sql(
    "SELECT COUNT(*) AS total_rows FROM financial_ratios",
    conn
)

print(rows)

print(pd.read_sql(
    """
    SELECT
        symbol,
        report_date,
        ROE,
        ROA,
        ROCE,
        NPM,
        OPM,
        `Revenue CAGR`,
        `Free Cash Flow`
    FROM financial_ratios
    LIMIT 5
    """,
    conn
))

conn.close()

print("\nSprint 2 Completed Successfully")