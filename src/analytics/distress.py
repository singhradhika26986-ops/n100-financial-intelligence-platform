import logging

import numpy as np
import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


class DistressDetectionEngine:
    """
    Sprint 5 - Day 32

    Multi-factor financial distress detection engine.

    Uses:
    - ROE
    - ROCE
    - NPM
    - OPM
    - Debt / Equity
    - Interest Coverage Ratio
    - Free Cash Flow
    - Cash Conversion Ratio

    Outputs:
    - Distress Score
    - Distress Probability
    - Distress Level
    - Distress Drivers
    """

    def __init__(self, dataframe, output_dir="output"):

        self.df = dataframe.copy()

        self.output_dir = output_dir

        logging.info(
            "Distress Detection Engine Started"
        )

    # =====================================================
    # NUMERIC CONVERSION
    # =====================================================

    def prepare_data(self):

        metrics = [
            "ROE",
            "ROCE",
            "NPM",
            "OPM",
            "debt_equity",
            "ICR",
            "free_cash_flow",
            "cash_conversion_ratio",
        ]

        for column in metrics:

            if column in self.df.columns:

                self.df[column] = pd.to_numeric(
                    self.df[column],
                    errors="coerce",
                )

        logging.info(
            "Distress data prepared"
        )

    # =====================================================
    # DISTRESS SCORE
    # =====================================================

    def calculate_distress_score(self):

        self.df["distress_score"] = 0.0

        # -------------------------------------------------
        # ROE
        # -------------------------------------------------

        if "ROE" in self.df.columns:

            self.df["distress_score"] += np.where(
                self.df["ROE"] < 0,
                15,
                np.where(
                    self.df["ROE"] < 8,
                    8,
                    0,
                ),
            )

        # -------------------------------------------------
        # ROCE
        # -------------------------------------------------

        if "ROCE" in self.df.columns:

            self.df["distress_score"] += np.where(
                self.df["ROCE"] < 0,
                15,
                np.where(
                    self.df["ROCE"] < 10,
                    8,
                    0,
                ),
            )

        # -------------------------------------------------
        # NET PROFIT MARGIN
        # -------------------------------------------------

        if "NPM" in self.df.columns:

            self.df["distress_score"] += np.where(
                self.df["NPM"] < 0,
                15,
                np.where(
                    self.df["NPM"] < 5,
                    8,
                    0,
                ),
            )

        # -------------------------------------------------
        # OPERATING PROFIT MARGIN
        # -------------------------------------------------

        if "OPM" in self.df.columns:

            self.df["distress_score"] += np.where(
                self.df["OPM"] < 0,
                10,
                np.where(
                    self.df["OPM"] < 10,
                    5,
                    0,
                ),
            )

        # -------------------------------------------------
        # DEBT / EQUITY
        # -------------------------------------------------

        if "debt_equity" in self.df.columns:

            self.df["distress_score"] += np.where(
                self.df["debt_equity"] > 2.0,
                15,
                np.where(
                    self.df["debt_equity"] > 1.0,
                    8,
                    0,
                ),
            )

        # -------------------------------------------------
        # INTEREST COVERAGE
        # -------------------------------------------------

        if "ICR" in self.df.columns:

            self.df["distress_score"] += np.where(
                self.df["ICR"] < 1,
                15,
                np.where(
                    self.df["ICR"] < 2,
                    8,
                    0,
                ),
            )

        # -------------------------------------------------
        # FREE CASH FLOW
        # -------------------------------------------------

        if "free_cash_flow" in self.df.columns:

            self.df["distress_score"] += np.where(
                self.df["free_cash_flow"] < 0,
                10,
                0,
            )

        # -------------------------------------------------
        # CASH CONVERSION
        # -------------------------------------------------

        if "cash_conversion_ratio" in self.df.columns:

            self.df["distress_score"] += np.where(
                self.df["cash_conversion_ratio"] < 0.5,
                10,
                0,
            )

        self.df["distress_score"] = (
            self.df["distress_score"]
            .clip(0, 100)
            .round(2)
        )

        logging.info(
            "Distress Score calculated"
        )

    # =====================================================
    # DISTRESS PROBABILITY
    # =====================================================

    def calculate_probability(self):

        self.df["distress_probability"] = (
            self.df["distress_score"] / 100
        ).round(4)

        logging.info(
            "Distress Probability calculated"
        )

    # =====================================================
    # DISTRESS LEVEL
    # =====================================================

    def classify_distress(self):

        def classify(score):

            if pd.isna(score):
                return "Unknown"

            if score >= 60:
                return "Red"

            if score >= 30:
                return "Amber"

            return "Green"

        self.df["distress_level"] = (
            self.df["distress_score"]
            .apply(classify)
        )

        logging.info(
            "Distress classification completed"
        )

    # =====================================================
    # DISTRESS DRIVERS
    # =====================================================

    def identify_drivers(self):

        def get_drivers(row):

            drivers = []

            if (
                pd.notna(row.get("ROE"))
                and row["ROE"] < 8
            ):
                drivers.append("Low ROE")

            if (
                pd.notna(row.get("ROCE"))
                and row["ROCE"] < 10
            ):
                drivers.append("Low ROCE")

            if (
                pd.notna(row.get("NPM"))
                and row["NPM"] < 5
            ):
                drivers.append("Low NPM")

            if (
                pd.notna(row.get("OPM"))
                and row["OPM"] < 10
            ):
                drivers.append("Low OPM")

            if (
                pd.notna(row.get("debt_equity"))
                and row["debt_equity"] > 1
            ):
                drivers.append("High Debt/Equity")

            if (
                pd.notna(row.get("ICR"))
                and row["ICR"] < 2
            ):
                drivers.append("Low Interest Coverage")

            if (
                pd.notna(row.get("free_cash_flow"))
                and row["free_cash_flow"] < 0
            ):
                drivers.append("Negative Free Cash Flow")

            if (
                pd.notna(
                    row.get(
                        "cash_conversion_ratio"
                    )
                )
                and row["cash_conversion_ratio"] < 0.5
            ):
                drivers.append(
                    "Weak Cash Conversion"
                )

            if not drivers:
                return "No major distress driver"

            return ", ".join(drivers)

        self.df["distress_drivers"] = (
            self.df.apply(
                get_drivers,
                axis=1,
            )
        )

        logging.info(
            "Distress Drivers identified"
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def create_summary(self):

        self.summary = {
            "total_companies": len(self.df),
            "green": int(
                (
                    self.df["distress_level"]
                    == "Green"
                ).sum()
            ),
            "amber": int(
                (
                    self.df["distress_level"]
                    == "Amber"
                ).sum()
            ),
            "red": int(
                (
                    self.df["distress_level"]
                    == "Red"
                ).sum()
            ),
        }

        logging.info(
            "Distress Summary: %s",
            self.summary,
        )

    # =====================================================
    # EXPORT
    # =====================================================

    def export_results(self):

        output_columns = [
            "company_name",
            "symbol",
            "industry",
            "ROE",
            "ROCE",
            "NPM",
            "OPM",
            "debt_equity",
            "ICR",
            "free_cash_flow",
            "cash_conversion_ratio",
            "distress_score",
            "distress_probability",
            "distress_level",
            "distress_drivers",
        ]

        available_columns = [
            column
            for column in output_columns
            if column in self.df.columns
        ]

        result = self.df[
            available_columns
        ].copy()

        result = result.sort_values(
            "distress_score",
            ascending=False,
        ).reset_index(
            drop=True
        )

        # Full distress report
        result.to_csv(
            f"{self.output_dir}/distress_report.csv",
            index=False,
        )

        # Alert-only file
        alerts = result[
            result["distress_level"].isin(
                ["Amber", "Red"]
            )
        ].copy()

        alerts.to_csv(
            f"{self.output_dir}/distress_alerts.csv",
            index=False,
        )

        logging.info(
            "Distress report exported"
        )

        logging.info(
            "Distress alerts exported"
        )

        return result

    # =====================================================
    # MAIN PIPELINE
    # =====================================================

    def run(self):

        self.prepare_data()

        self.calculate_distress_score()

        self.calculate_probability()

        self.classify_distress()

        self.identify_drivers()

        self.create_summary()

        result = self.export_results()

        logging.info(
            "Distress Detection Engine "
            "Completed Successfully"
        )

        return result