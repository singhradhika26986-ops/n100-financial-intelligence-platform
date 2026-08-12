import re
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"

OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_DIR.mkdir(exist_ok=True)


INPUT_FILE = DATA_DIR / "analysis.xlsx"


PATTERN = re.compile(
    r"(\d+)\s*Years?:?\s*([\d.]+)%"
)


TARGET_COLUMNS = [
    "compounded_sales_growth",
    "compounded_profit_growth",
    "stock_price_cagr",
    "roe",
]

def extract_metric(text):
    """
    Extract period and percentage value from text.

    Example:
    '10 Years: 21%'
    -> (10, 21.0)
    """

    if pd.isna(text):
        return None

    text = str(text)

    match = PATTERN.search(text)

    if not match:
        return None

    period = int(match.group(1))
    value = float(match.group(2))

    return period, value


def parse_analysis(df):

    parsed_rows = []

    failed_rows = []

    for _, row in df.iterrows():

        company_id = row.get("company_id")

        for metric in TARGET_COLUMNS:

            value = row.get(metric)

            result = extract_metric(value)

            if result:

                period, pct = result

                parsed_rows.append(
                    {
                        "company_id": company_id,
                        "metric_type": metric,
                        "period_years": period,
                        "value_pct": pct,
                    }
                )

            else:

                failed_rows.append(
                    {
                        "company_id": company_id,
                        "metric_type": metric,
                        "original_text": value,
                    }
                )

    parsed_df = pd.DataFrame(parsed_rows)

    failed_df = pd.DataFrame(failed_rows)

    return parsed_df, failed_df

def main():

    if not INPUT_FILE.exists():
        print(f"Input file not found: {INPUT_FILE}")
        return

    print("Reading analysis.xlsx ...")

    df = pd.read_excel(INPUT_FILE)

    parsed_df, failed_df = parse_analysis(df)

    parsed_file = OUTPUT_DIR / "analysis_parsed.csv"
    failed_file = OUTPUT_DIR / "parse_failures.csv"

    parsed_df.to_csv(
        parsed_file,
        index=False,
    )

    failed_df.to_csv(
        failed_file,
        index=False,
    )

    print("=" * 50)
    print("Parsing Completed")
    print("=" * 50)
    print(f"Parsed Records : {len(parsed_df)}")
    print(f"Failed Records : {len(failed_df)}")
    print(f"Saved : {parsed_file}")
    print(f"Saved : {failed_file}")


if __name__ == "__main__":
    main()