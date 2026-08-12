import logging
from pathlib import Path

import pandas as pd

from src.dashboard.utils.db import execute_query
from src.reports.tearsheet import CompanyTearsheet


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


BASE_DIR = Path(__file__).resolve().parents[2]

TEARSHEET_DIR = (
    BASE_DIR
    / "reports"
    / "tearsheets"
)

OUTPUT_DIR = (
    BASE_DIR
    / "output"
)

SKIPPED_FILE = (
    OUTPUT_DIR
    / "skipped_tearsheets.csv"
)


def get_companies():

    query = """
    SELECT
        company_name,
        symbol,
        industry
    FROM companies
    ORDER BY company_name
    """

    return execute_query(query)


def get_company_year_count(symbol):

    query = """
    SELECT
        COUNT(DISTINCT report_date)
    FROM financial_ratios
    WHERE symbol = ?
    """

    df = execute_query(
        query,
        (symbol,),
    )

    if df.empty:
        return 0

    value = df.iloc[0, 0]

    if pd.isna(value):
        return 0

    return int(value)


def generate_batch():

    TEARSHEET_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    companies = get_companies()

    if companies.empty:
        raise RuntimeError(
            "No companies found in database."
        )

    logging.info(
        "Companies discovered: %s",
        len(companies),
    )

    skipped = []
    generated = []

    for _, company in companies.iterrows():

        company_name = company["company_name"]
        symbol = company["symbol"]
        industry = company["industry"]

        logging.info(
            "Processing %s (%s)",
            company_name,
            symbol,
        )

        try:

            year_count = get_company_year_count(
                symbol
            )

            if year_count < 3:

                skipped.append(
                    {
                        "company_name": company_name,
                        "symbol": symbol,
                        "industry": industry,
                        "years_available": year_count,
                        "reason": "Less than 3 years of financial data",
                    }
                )

                logging.warning(
                    "SKIPPED %s - only %s years",
                    symbol,
                    year_count,
                )

                continue

            pdf_path = (
                CompanyTearsheet(
                    symbol
                ).build()
            )

            generated.append(
                {
                    "company_name": company_name,
                    "symbol": symbol,
                    "industry": industry,
                    "years_available": year_count,
                    "pdf_path": str(pdf_path),
                }
            )

            logging.info(
                "GENERATED %s",
                pdf_path,
            )

        except Exception as exc:

            skipped.append(
                {
                    "company_name": company_name,
                    "symbol": symbol,
                    "industry": industry,
                    "years_available": None,
                    "reason": f"Generation error: {exc}",
                }
            )

            logging.exception(
                "Failed: %s",
                symbol,
            )

    skipped_df = pd.DataFrame(
        skipped
    )

    skipped_df.to_csv(
        SKIPPED_FILE,
        index=False,
    )

    logging.info(
        "Batch generation completed"
    )

    print()
    print("=" * 60)
    print("BATCH REPORT SUMMARY")
    print("=" * 60)
    print(
        f"Companies discovered : {len(companies)}"
    )
    print(
        f"PDFs generated       : {len(generated)}"
    )
    print(
        f"Companies skipped    : {len(skipped)}"
    )
    print(
        f"Skipped file         : {SKIPPED_FILE}"
    )
    print("=" * 60)

    return generated, skipped


if __name__ == "__main__":

    generate_batch()