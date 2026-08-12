import logging
from pathlib import Path

import numpy as np
import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


class PatternChangeEngine:
    """
    Sprint 5 - Day 33

    Detect meaningful year-over-year changes in:
    - Revenue
    - Net Profit
    - ROE
    - ROCE
    - NPM
    - OPM
    - Debt / Equity
    - Free Cash Flow
    - Cash Conversion Ratio

    Output:
    output/pattern_changes.csv
    """

    def __init__(self, dataframe, output_dir="output"):

        self.df = dataframe.copy()

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        logging.info(
            "Pattern Change Engine Started"
        )

    # =====================================================
    # PREPARE DATA
    # =====================================================

    def prepare_data(self):

        required = [
            "symbol",
            "report_date",
        ]

        missing = [
            column
            for column in required
            if column not in self.df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing required columns: {missing}"
            )

        self.df["report_date"] = pd.to_datetime(
            self.df["report_date"],
            errors="coerce",
        )

        numeric_columns = [
            "revenue",
            "net_profit",
            "ROE",
            "ROCE",
            "NPM",
            "OPM",
            "D/E",
            "debt_equity",
            "free_cash_flow",
            "Free Cash Flow",
            "Cash Conversion Ratio",
            "cash_conversion_ratio",
        ]

        for column in numeric_columns:

            if column in self.df.columns:

                self.df[column] = pd.to_numeric(
                    self.df[column],
                    errors="coerce",
                )

        self.df = (
            self.df
            .dropna(
                subset=[
                    "symbol",
                    "report_date",
                ]
            )
            .sort_values(
                [
                    "symbol",
                    "report_date",
                ]
            )
            .reset_index(drop=True)
        )

        logging.info(
            "Historical records prepared: %s",
            len(self.df),
        )

    # =====================================================
    # NORMALIZE METRIC NAMES
    # =====================================================

    def normalize_metrics(self):

        if (
            "debt_equity" not in self.df.columns
            and "D/E" in self.df.columns
        ):
            self.df["debt_equity"] = self.df["D/E"]

        if (
            "free_cash_flow" not in self.df.columns
            and "Free Cash Flow" in self.df.columns
        ):
            self.df["free_cash_flow"] = (
                self.df["Free Cash Flow"]
            )

        if (
            "cash_conversion_ratio"
            not in self.df.columns
            and "Cash Conversion Ratio"
            in self.df.columns
        ):
            self.df["cash_conversion_ratio"] = (
                self.df["Cash Conversion Ratio"]
            )

        logging.info(
            "Pattern metric names normalized"
        )

    # =====================================================
    # YEAR-OVER-YEAR CHANGE
    # =====================================================

    def calculate_changes(self):

        metrics = [
            "revenue",
            "net_profit",
            "ROE",
            "ROCE",
            "NPM",
            "OPM",
            "debt_equity",
            "free_cash_flow",
            "cash_conversion_ratio",
        ]

        for metric in metrics:

            if metric not in self.df.columns:
                continue

            previous = (
                self.df
                .groupby("symbol")[metric]
                .shift(1)
            )

            self.df[
                f"{metric}_previous"
            ] = previous

            self.df[
                f"{metric}_change"
            ] = (
                self.df[metric]
                - previous
            )

            self.df[
                f"{metric}_pct_change"
            ] = np.where(
                previous.abs() > 0,
                (
                    (
                        self.df[metric]
                        - previous
                    )
                    / previous.abs()
                )
                * 100,
                np.nan,
            )

        logging.info(
            "Year-over-year changes calculated"
        )

    # =====================================================
    # PATTERN DETECTION
    # =====================================================

    def detect_patterns(self):

        records = []

        latest = (
            self.df
            .groupby("symbol", as_index=False)
            .tail(1)
        )

        for _, row in latest.iterrows():

            company = row.get(
                "company_name",
                row["symbol"],
            )

            symbol = row["symbol"]

            changes = []

            # ---------------------------------------------
            # Revenue
            # ---------------------------------------------

            revenue_change = row.get(
                "revenue_pct_change",
                np.nan,
            )

            if pd.notna(revenue_change):

                if revenue_change <= -10:

                    changes.append(
                        "Revenue Decline"
                    )

                elif revenue_change >= 20:

                    changes.append(
                        "Strong Revenue Growth"
                    )

            # ---------------------------------------------
            # Net Profit
            # ---------------------------------------------

            profit_change = row.get(
                "net_profit_pct_change",
                np.nan,
            )

            if pd.notna(profit_change):

                if profit_change <= -20:

                    changes.append(
                        "Profit Decline"
                    )

                elif profit_change >= 20:

                    changes.append(
                        "Strong Profit Growth"
                    )

            # ---------------------------------------------
            # ROE
            # ---------------------------------------------

            roe_change = row.get(
                "ROE_change",
                np.nan,
            )

            if pd.notna(roe_change):

                if roe_change <= -5:

                    changes.append(
                        "ROE Deterioration"
                    )

                elif roe_change >= 5:

                    changes.append(
                        "ROE Improvement"
                    )

            # ---------------------------------------------
            # ROCE
            # ---------------------------------------------

            roce_change = row.get(
                "ROCE_change",
                np.nan,
            )

            if pd.notna(roce_change):

                if roce_change <= -5:

                    changes.append(
                        "ROCE Deterioration"
                    )

                elif roce_change >= 5:

                    changes.append(
                        "ROCE Improvement"
                    )

            # ---------------------------------------------
            # NPM
            # ---------------------------------------------

            npm_change = row.get(
                "NPM_change",
                np.nan,
            )

            if pd.notna(npm_change):

                if npm_change <= -3:

                    changes.append(
                        "Margin Compression"
                    )

                elif npm_change >= 3:

                    changes.append(
                        "Margin Expansion"
                    )

            # ---------------------------------------------
            # OPM
            # ---------------------------------------------

            opm_change = row.get(
                "OPM_change",
                np.nan,
            )

            if pd.notna(opm_change):

                if opm_change <= -3:

                    changes.append(
                        "Operating Margin Compression"
                    )

                elif opm_change >= 3:

                    changes.append(
                        "Operating Margin Expansion"
                    )

            # ---------------------------------------------
            # Debt / Equity
            # ---------------------------------------------

            debt_change = row.get(
                "debt_equity_change",
                np.nan,
            )

            if pd.notna(debt_change):

                if debt_change >= 0.5:

                    changes.append(
                        "Leverage Increase"
                    )

                elif debt_change <= -0.5:

                    changes.append(
                        "Deleveraging"
                    )

            # ---------------------------------------------
            # Free Cash Flow
            # ---------------------------------------------

            fcf_change = row.get(
                "free_cash_flow_pct_change",
                np.nan,
            )

            current_fcf = row.get(
                "free_cash_flow",
                np.nan,
            )

            previous_fcf = row.get(
                "free_cash_flow_previous",
                np.nan,
            )

            if (
                pd.notna(current_fcf)
                and pd.notna(previous_fcf)
            ):

                if (
                    current_fcf < 0
                    and previous_fcf >= 0
                ):

                    changes.append(
                        "FCF Turned Negative"
                    )

                elif (
                    current_fcf >= 0
                    and previous_fcf < 0
                ):

                    changes.append(
                        "FCF Turned Positive"
                    )

                elif (
                    pd.notna(fcf_change)
                    and fcf_change <= -30
                ):

                    changes.append(
                        "FCF Deterioration"
                    )

            # ---------------------------------------------
            # Cash Conversion
            # ---------------------------------------------

            ccr_change = row.get(
                "cash_conversion_ratio_change",
                np.nan,
            )

            if pd.notna(ccr_change):

                if ccr_change <= -0.25:

                    changes.append(
                        "Cash Conversion Deterioration"
                    )

                elif ccr_change >= 0.25:

                    changes.append(
                        "Cash Conversion Improvement"
                    )

            # ---------------------------------------------
            # Overall Pattern
            # ---------------------------------------------

            if not changes:

                pattern_type = "No Significant Change"

            elif any(
                keyword in change
                for change in changes
                for keyword in [
                    "Decline",
                    "Deterioration",
                    "Compression",
                    "Increase",
                    "Negative",
                ]
            ):

                pattern_type = "Negative"

            else:

                pattern_type = "Positive"

            records.append(
                {
                    "company_name": company,
                    "symbol": symbol,
                    "report_date": row[
                        "report_date"
                    ],
                    "pattern_type": pattern_type,
                    "change_count": len(changes),
                    "pattern_changes": (
                        ", ".join(changes)
                        if changes
                        else "No Significant Change"
                    ),
                }
            )

        self.patterns = pd.DataFrame(
            records
        )

        logging.info(
            "Pattern detection completed: %s companies",
            len(self.patterns),
        )

    # =====================================================
    # EXPORT
    # =====================================================

    def export_results(self):

        output_path = (
            self.output_dir
            / "pattern_changes.csv"
        )

        self.patterns.to_csv(
            output_path,
            index=False,
        )

        logging.info(
            "Saved: %s",
            output_path,
        )

        return self.patterns

    # =====================================================
    # MAIN PIPELINE
    # =====================================================

    def run(self):

        self.prepare_data()

        self.normalize_metrics()

        self.calculate_changes()

        self.detect_patterns()

        result = self.export_results()

        logging.info(
            "Pattern Change Engine "
            "Completed Successfully"
        )

        return result