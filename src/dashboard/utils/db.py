import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[3]
DATABASE_PATH = BASE_DIR / "nifty100.db"


def get_connection():
    """
    Create SQLite connection.
    """
    return sqlite3.connect(DATABASE_PATH)


def execute_query(query, params=None):
    """
    Execute SQL query and return DataFrame.
    """
    conn = get_connection()

    try:
        if params is None:
            df = pd.read_sql_query(query, conn)
        else:
            df = pd.read_sql_query(
                query,
                conn,
                params=params,
            )

        return df

    finally:
        conn.close()


def test_connection():
    """
    Test database connection.
    """
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        return True

    except Exception:
        return False

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
    Return all available years.
    """
    query = """
    SELECT DISTINCT
        years
    FROM financial_ratios
    WHERE years IS NOT NULL
    ORDER BY years DESC
    """

    return execute_query(query)

def get_company_profile(symbol):
    """
    Return company profile.
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

    return execute_query(query, (symbol,))


def get_financial_ratios(symbol):
    """
    Return financial ratios for a company.
    """
    query = """
    SELECT *
    FROM financial_ratios
    WHERE symbol = ?
    ORDER BY years DESC
    """

    return execute_query(query, (symbol,))


def get_balance_sheet(symbol):
    """
    Return balance sheet.
    """
    query = """
    SELECT *
    FROM balance_sheet
    WHERE symbol = ?
    ORDER BY report_date DESC
    """

    return execute_query(query, (symbol,))

def get_income_statement(symbol):
    """
    Return income statement.
    """
    query = """
    SELECT *
    FROM income_statement
    WHERE symbol = ?
    ORDER BY report_date DESC
    """

    return execute_query(query, (symbol,))


def get_cash_flow(symbol):
    """
    Return cash flow statement.
    """
    query = """
    SELECT *
    FROM cash_flow
    WHERE symbol = ?
    ORDER BY report_date DESC
    """

    return execute_query(query, (symbol,))


def get_sector_data(industry):
    """
    Return companies belonging to a sector.
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

    return execute_query(query, (industry,))


def get_peer_data(industry):
    """
    Return peer companies from the same industry.
    """
    return get_sector_data(industry)

def get_stock_prices(symbol):
    """
    Return stock price history.
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

    return execute_query(query, (symbol,))


def search_company(keyword):
    """
    Search companies by name or symbol.
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

    return execute_query(query, (value, value))


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

def get_sector_summary():
    """
    Company count by industry.
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


def get_top_companies(limit=5):
    """
    Return top companies alphabetically.
    (Temporary until quality score is available.)
    """
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


def get_home_kpis():
    """
    Dashboard KPI summary.
    """
    query = """
    SELECT
        COUNT(*) AS total_companies,
        COUNT(DISTINCT industry) AS total_industries
    FROM companies
    """

    return execute_query(query)

def test_financial_ratios():
    query = """
    SELECT *
    FROM financial_ratios
    LIMIT 5
    """
    return execute_query(query)

def get_screener_data():
    """
    Return data for stock screener.
    """
    query = """
    SELECT
        c.company_name,
        c.symbol,
        c.industry,
        f.ROE,
        f.ROCE,
        f.NPM,
        f.OPM,
        f."D/E" AS debt_equity,
        f.ICR,
        f."Revenue CAGR" AS revenue_cagr,
        f."PAT CAGR" AS pat_cagr,
        f."Free Cash Flow" AS free_cash_flow
    FROM companies c
    JOIN financial_ratios f
        ON c.symbol = f.symbol
    """

    return execute_query(query)
