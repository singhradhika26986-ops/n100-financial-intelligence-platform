from pathlib import Path

import pandas as pd


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "output" / "analysis_parsed.csv"
OUTPUT_FILE = BASE_DIR / "output" / "pros_cons_generated.csv"


# ============================================================
# HELPERS
# ============================================================

def format_value(value):
    """Format percentage values for display."""
    return f"{value:.2f}%"


def evaluate_metric(metric_type, value):
    """
    Evaluate one financial metric and return
    a classification, pros and cons.
    """

    metric_type = str(metric_type).strip().lower()
    value = float(value)

    pros = []
    cons = []

    # --------------------------------------------------------
    # Compounded Sales Growth
    # --------------------------------------------------------

    if metric_type == "compounded_sales_growth":

        if value >= 15:
            pros.append(
                f"Strong sales growth of {format_value(value)}"
            )

        elif value >= 8:
            pros.append(
                f"Moderate sales growth of {format_value(value)}"
            )

        else:
            cons.append(
                f"Low sales growth of {format_value(value)}"
            )

    # --------------------------------------------------------
    # Compounded Profit Growth
    # --------------------------------------------------------

    elif metric_type == "compounded_profit_growth":

        if value >= 15:
            pros.append(
                f"Strong profit growth of {format_value(value)}"
            )

        elif value >= 8:
            pros.append(
                f"Moderate profit growth of {format_value(value)}"
            )

        else:
            cons.append(
                f"Weak profit growth of {format_value(value)}"
            )

    # --------------------------------------------------------
    # Stock Price CAGR
    # --------------------------------------------------------

    elif metric_type == "stock_price_cagr":

        if value >= 15:
            pros.append(
                f"Strong long-term stock CAGR of {format_value(value)}"
            )

        elif value >= 8:
            pros.append(
                f"Moderate long-term stock CAGR of {format_value(value)}"
            )

        else:
            cons.append(
                f"Low long-term stock CAGR of {format_value(value)}"
            )

    # --------------------------------------------------------
    # ROE
    # --------------------------------------------------------

    elif metric_type == "roe":

        if value >= 20:
            pros.append(
                f"High return on equity of {format_value(value)}"
            )

        elif value >= 12:
            pros.append(
                f"Reasonable return on equity of {format_value(value)}"
            )

        else:
            cons.append(
                f"Low return on equity of {format_value(value)}"
            )

    return pros, cons


# ============================================================
# MAIN GENERATOR
# ============================================================

def generate_pros_cons():

    print("=" * 60)
    print("Pros & Cons Generator")
    print("=" * 60)

    # --------------------------------------------------------
    # Check input file
    # --------------------------------------------------------

    if not INPUT_FILE.exists():

        print(f"Input file not found: {INPUT_FILE}")
        return

    print(f"Reading: {INPUT_FILE}")

    df = pd.read_csv(INPUT_FILE)

    if df.empty:

        print("Input file is empty.")
        return

    required_columns = {
        "company_id",
        "metric_type",
        "period_years",
        "value_pct",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:

        print(
            "Missing columns:",
            ", ".join(sorted(missing_columns)),
        )

        return

    # --------------------------------------------------------
    # Clean data
    # --------------------------------------------------------

    df = df.copy()

    df["company_id"] = pd.to_numeric(
        df["company_id"],
        errors="coerce",
    )

    df["period_years"] = pd.to_numeric(
        df["period_years"],
        errors="coerce",
    )

    df["value_pct"] = pd.to_numeric(
        df["value_pct"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "company_id",
            "metric_type",
            "value_pct",
        ]
    )

    if df.empty:

        print("No valid records available.")
        return

    # --------------------------------------------------------
    # Generate company-level Pros & Cons
    # --------------------------------------------------------

    results = []

    for company_id, company_data in df.groupby(
        "company_id"
    ):

        pros = []
        cons = []

        company_data = company_data.sort_values(
            "metric_type"
        )

        for _, row in company_data.iterrows():

            metric_pros, metric_cons = evaluate_metric(
                row["metric_type"],
                row["value_pct"],
            )

            pros.extend(metric_pros)
            cons.extend(metric_cons)

        # Remove duplicates while preserving order
        pros = list(dict.fromkeys(pros))
        cons = list(dict.fromkeys(cons))

        # ----------------------------------------------------
        # Overall assessment
        # ----------------------------------------------------

        if len(pros) > len(cons):

            assessment = "Positive"

        elif len(cons) > len(pros):

            assessment = "Needs Attention"

        else:

            assessment = "Balanced"

        results.append(
            {
                "company_id": int(company_id),
                "pros": " | ".join(pros)
                if pros
                else "No major strengths identified",
                "cons": " | ".join(cons)
                if cons
                else "No major weaknesses identified",
                "overall_assessment": assessment,
                "metrics_analyzed": len(company_data),
            }
        )

    # --------------------------------------------------------
    # Create output DataFrame
    # --------------------------------------------------------

    result_df = pd.DataFrame(results)

    # Sort by company ID
    result_df = result_df.sort_values(
        "company_id"
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Save output
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    result_df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print()
    print("=" * 60)
    print("Pros & Cons Generation Completed")
    print("=" * 60)

    print(
        f"Companies Processed: {len(result_df)}"
    )

    print(
        f"Records Generated: {len(result_df)}"
    )

    print(
        f"Saved: {OUTPUT_FILE}"
    )

    print("=" * 60)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    generate_pros_cons()