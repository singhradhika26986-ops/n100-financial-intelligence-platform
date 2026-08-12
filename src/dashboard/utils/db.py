import sqlite3
from pathlib import Path

import pandas as pd


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[3]
DATABASE_PATH = BASE_DIR / "nifty100.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():
    """
    Create and return a SQLite database connection.
    """
    return sqlite3.connect(DATABASE_PATH)


# =========================================================
# GENERIC QUERY EXECUTION
# =========================================================

def execute_query(query, params=None):
    """
    Execute SQL query and return the result as a DataFrame.
    """

    conn = get_connection()

    try:
        if params is None:
            df = pd.read_sql_query(
                query,
                conn,
            )
        else:
            df = pd.read_sql_query(
                query,
                conn,
                params=params,
            )

        return df

    finally:
        conn.close()


# =========================================================
# DATABASE TEST
# =========================================================

def test_connection():
    """
    Test whether the SQLite database connection works.
    """

    try:
        conn = get_connection()

        conn.execute("SELECT 1")

        conn.close()

        return True

    except Exception:
        return False


# =========================================================
# COMPANY DATA
# =========================================================

def get_companies():
    """
    Return all companies.
    """

    query = """
    SELECT
        company_name,
        industry,
        symbol,
        series,
        isin_code
    FROM companies
    ORDER BY company_name
    """

    return execute_query(query)


def get_symbols():
    """
    Return all available stock symbols.
    """

    query = """
    SELECT DISTINCT
        symbol
    FROM companies
    ORDER BY symbol
    """

    return execute_query(query)


def get_industries():
    """
    Return all available industries.
    """

    query = """
    SELECT DISTINCT
        industry
    FROM companies
    WHERE industry IS NOT NULL
    ORDER BY industry
    """

    return execute_query(query)


def get_available_years():
    """
    Return all available financial years.
    """

    query = """
    SELECT DISTINCT
        years
    FROM financial_ratios
    WHERE years IS NOT NULL
    ORDER BY years DESC
    """

    return execute_query(query)


# =========================================================
# COMPANY PROFILE
# =========================================================

def get_company_profile(symbol):
    """
    Return company profile for a stock symbol.
    """

    query = """
    SELECT
        company_name,
        industry,
        symbol,
        series,
        isin_code
    FROM companies
    WHERE symbol = ?
    """

    return execute_query(
        query,
        (symbol,),
    )


# =========================================================
# FINANCIAL RATIOS
# =========================================================

def get_financial_ratios(symbol):
    """
    Return financial ratios for a company.
    """

    query = """
    SELECT *
    FROM financial_ratios
    WHERE symbol = ?
    ORDER BY report_date ASC
    """

    return execute_query(
        query,
        (symbol,),
    )


# =========================================================
# BALANCE SHEET
# =========================================================

def get_balance_sheet(symbol):
    """
    Return balance sheet data for a company.
    """

    query = """
    SELECT *
    FROM balance_sheet
    WHERE symbol = ?
    ORDER BY report_date DESC
    """

    return execute_query(
        query,
        (symbol,),
    )


# =========================================================
# INCOME STATEMENT
# =========================================================

def get_income_statement(symbol):
    """
    Return income statement data for a company.
    """

    query = """
    SELECT *
    FROM income_statement
    WHERE symbol = ?
    ORDER BY report_date DESC
    """

    return execute_query(
        query,
        (symbol,),
    )


# =========================================================
# CASH FLOW
# =========================================================

def get_cash_flow(symbol):
    """
    Return cash flow statement for a company.
    """

    query = """
    SELECT *
    FROM cash_flow
    WHERE symbol = ?
    ORDER BY report_date DESC
    """

    return execute_query(
        query,
        (symbol,),
    )


# =========================================================
# SECTOR DATA
# =========================================================

def get_sector_data(industry):
    """
    Return companies belonging to a specific industry.
    """

    query = """
    SELECT
        company_name,
        industry,
        symbol,
        series,
        isin_code
    FROM companies
    WHERE industry = ?
    ORDER BY company_name
    """

    return execute_query(
        query,
        (industry,),
    )


def get_peer_data(industry):
    """
    Return peer companies from the same industry.
    """

    return get_sector_data(industry)


# =========================================================
# STOCK PRICE HISTORY
# =========================================================

def get_stock_prices(symbol):
    """
    Return historical stock prices.
    """

    query = """
    SELECT
        trade_date,
        open,
        high,
        low,
        close,
        adj_close,
        volume
    FROM stock_prices
    WHERE symbol = ?
    ORDER BY trade_date DESC
    """

    return execute_query(
        query,
        (symbol,),
    )


# =========================================================
# COMPANY SEARCH
# =========================================================

def search_company(keyword):
    """
    Search companies by company name or stock symbol.
    """

    query = """
    SELECT
        company_name,
        industry,
        symbol,
        series,
        isin_code
    FROM companies
    WHERE company_name LIKE ?
       OR symbol LIKE ?
    ORDER BY company_name
    """

    value = f"%{keyword}%"

    return execute_query(
        query,
        (value, value),
    )


# =========================================================
# DASHBOARD SUMMARY
# =========================================================

def get_dashboard_summary():
    """
    Return dashboard summary statistics.
    """

    query = """
    SELECT
        COUNT(*) AS total_companies,
        COUNT(DISTINCT industry) AS total_industries
    FROM companies
    """

    return execute_query(query)


def get_home_kpis():
    """
    Return home dashboard KPI statistics.
    """

    query = """
    SELECT
        COUNT(*) AS total_companies,
        COUNT(DISTINCT industry) AS total_industries
    FROM companies
    """

    return execute_query(query)


# =========================================================
# SECTOR SUMMARY
# =========================================================

def get_sector_summary():
    """
    Return company count by industry.
    """

    query = """
    SELECT
        industry,
        COUNT(*) AS company_count
    FROM companies
    GROUP BY industry
    ORDER BY company_count DESC
    """

    return execute_query(query)


# =========================================================
# TOP COMPANIES
# =========================================================

def get_top_companies(limit=5):
    """
    Return top companies alphabetically.
    """

    limit = int(limit)

    query = f"""
    SELECT
        company_name,
        symbol,
        industry
    FROM companies
    ORDER BY company_name
    LIMIT {limit}
    """

    return execute_query(query)


# =========================================================
# FINANCIAL RATIO TEST
# =========================================================

def test_financial_ratios():
    """
    Return sample financial ratio records for testing.
    """

    query = """
    SELECT *
    FROM financial_ratios
    LIMIT 5
    """

    return execute_query(query)


# =========================================================
# STOCK SCREENER / PEER ENGINE DATA
# =========================================================

def get_screener_data():
    """
    Return the latest financial record for each company.

    Used by:
        - Stock Screener
        - Peer Comparison
        - Peer Ranking Engine
    """

    query = """
    WITH latest_ratios AS (

        SELECT
            f.*,

            ROW_NUMBER() OVER (
                PARTITION BY f.symbol
                ORDER BY f.report_date DESC
            ) AS row_num

        FROM financial_ratios f
    )

    SELECT
        c.company_name,
        c.symbol,
        c.industry,

        f.report_date,

        f.ROE,
        f.ROCE,
        f.NPM,
        f.OPM,

        f."D/E" AS debt_equity,

        f.ICR,

        f."Revenue CAGR" AS revenue_cagr,

        f."PAT CAGR" AS pat_cagr,

        f."Free Cash Flow" AS free_cash_flow,

        f."Cash Conversion Ratio"
            AS cash_conversion_ratio

    FROM companies c

    INNER JOIN latest_ratios f
        ON c.symbol = f.symbol

    WHERE f.row_num = 1

    ORDER BY c.company_name
    """

    return execute_query(query)

def get_cashflow_intelligence_data():
    """
    Return combined cash-flow and financial-ratio data
    required by the Sprint 5 Cash Flow Intelligence Engine.
    """

    query = """
    WITH latest_ratios AS (

        SELECT
            f.*,

            ROW_NUMBER() OVER (
                PARTITION BY f.symbol
                ORDER BY f.report_date DESC
            ) AS row_num

        FROM financial_ratios f
    )

    SELECT
        c.company_name,
        c.industry,
        c.symbol,

        f.report_date,

        f.revenue,
        f.net_profit,
        f.total_debt,
        f.interest_expense,

        f.operating_cash_flow,
        f.capital_expenditure,
        f.free_cash_flow,

        f."Revenue CAGR" AS revenue_cagr,
        f."PAT CAGR" AS pat_cagr,

        f."OCF Margin" AS ocf_margin,
        f."Cash Conversion Ratio"
            AS cash_conversion_ratio,

        f."Reinvestment Ratio"
            AS reinvestment_ratio,

        cf.free_cash_flow AS cashflow_table_fcf

    FROM companies c

    INNER JOIN latest_ratios f
        ON c.symbol = f.symbol

    LEFT JOIN cash_flow cf
        ON cf.symbol = f.symbol
        AND cf.report_date = f.report_date

    WHERE f.row_num = 1

    ORDER BY c.company_name
    """

    return execute_query(query)