import sqlite3
import pandas as pd
import yfinance as yf
import time

conn = sqlite3.connect("nifty100.db")

companies = pd.read_csv("data/raw/companies.csv")

for symbol in companies["Symbol"]:

    ticker = yf.Ticker(symbol + ".NS")

    print(f"Processing {symbol}")

    try:

        # ---------------- Balance Sheet ----------------

        bs = ticker.balance_sheet.T

        if not bs.empty:

            bs = bs.reset_index().rename(columns={"index": "report_date"})

            bs["symbol"] = symbol

            bs["total_assets"] = bs.get("Total Assets")

            bs["total_debt"] = bs.get("Total Debt")

            bs["shareholders_equity"] = bs.get("Stockholders Equity")

            bs["cash"] = bs.get("Cash And Cash Equivalents")

            bs = bs[
                [
                    "symbol",
                    "report_date",
                    "total_assets",
                    "total_debt",
                    "shareholders_equity",
                    "cash",
                ]
            ]

            bs.to_sql(
                "balance_sheet",
                conn,
                if_exists="append",
                index=False,
            )

        # ---------------- Income Statement ----------------

        fin = ticker.financials.T

        if not fin.empty:

            fin = fin.reset_index().rename(columns={"index": "report_date"})

            fin["symbol"] = symbol

            fin["revenue"] = fin.get("Total Revenue")

            fin["operating_profit"] = fin.get("Operating Income")

            fin["net_profit"] = fin.get("Net Income")

            fin["ebit"] = fin.get("EBIT")

            fin["eps"] = fin.get("Diluted EPS")

            fin["interest_expense"] = fin.get("Interest Expense")

            fin = fin[
                [
                    "symbol",
                    "report_date",
                    "revenue",
                    "operating_profit",
                    "net_profit",
                    "ebit",
                    "eps",
                    "interest_expense",
                ]
            ]

            fin.to_sql(
                "income_statement",
                conn,
                if_exists="append",
                index=False,
            )

        # ---------------- Cash Flow ----------------

        cf = ticker.cashflow.T

        if not cf.empty:

            cf = cf.reset_index().rename(columns={"index": "report_date"})

            cf["symbol"] = symbol

            cf["operating_cash_flow"] = cf.get("Operating Cash Flow")

            cf["capital_expenditure"] = cf.get("Capital Expenditure")

            cf["free_cash_flow"] = cf.get("Free Cash Flow")

            cf = cf[
                [
                    "symbol",
                    "report_date",
                    "operating_cash_flow",
                    "capital_expenditure",
                    "free_cash_flow",
                ]
            ]

            cf.to_sql(
                "cash_flow",
                conn,
                if_exists="append",
                index=False,
            )

        time.sleep(0.5)

    except Exception as e:

        print(symbol, e)

conn.close()

print("\nFinancial Statements Loaded Successfully")