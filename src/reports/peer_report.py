import logging
from pathlib import Path

import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


class PeerComparisonReport:
    """
    Peer Comparison Report

    Generates:
    1. Individual company peer reports
    2. Combined peer_comparison.xlsx
    """

    def __init__(self, dataframe):

        self.df = dataframe.copy()

        self.output_folder = (
            Path("reports") / "peer_reports"
        )

        self.output_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.output_file = (
            Path("output")
            / "peer_comparison.xlsx"
        )

        self.output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        logging.info(
            "Peer Comparison Report Started"
        )

    # =====================================================
    # NORMALIZE COLUMNS
    # =====================================================

    def normalize_columns(self):

        mapping = {
            "industry": "Sector",
            "debt_equity": "D/E",
            "revenue_cagr": "Revenue CAGR",
            "pat_cagr": "PAT CAGR",
            "free_cash_flow": "Free Cash Flow",
            "cash_conversion_ratio":
                "Cash Conversion Ratio",
        }

        for source, target in mapping.items():

            if (
                source in self.df.columns
                and target not in self.df.columns
            ):
                self.df[target] = self.df[source]

        # -------------------------------------------------
        # Peer Score
        # -------------------------------------------------

        if "Peer Score" not in self.df.columns:

            score_columns = [
                "ROE",
                "ROCE",
                "NPM",
                "Revenue CAGR",
                "PAT CAGR",
                "Free Cash Flow",
                "Cash Conversion Ratio",
                "ICR",
            ]

            available = [
                column
                for column in score_columns
                if column in self.df.columns
            ]

            if available:

                numeric = self.df[
                    available
                ].apply(
                    pd.to_numeric,
                    errors="coerce",
                )

                percentile = (
                    numeric.rank(
                        pct=True
                    )
                    * 100
                )

                self.df["Peer Score"] = (
                    percentile.mean(
                        axis=1,
                        skipna=True,
                    )
                    .round(2)
                )

            else:

                self.df["Peer Score"] = pd.NA

        # -------------------------------------------------
        # Overall Rank
        # -------------------------------------------------

        if "Overall Rank" not in self.df.columns:

            self.df["Overall Rank"] = (
                self.df["Peer Score"]
                .rank(
                    ascending=False,
                    method="dense",
                )
            )

        # -------------------------------------------------
        # Rating
        # -------------------------------------------------

        if "Rating" not in self.df.columns:

            def get_rating(score):

                if pd.isna(score):
                    return "N/A"

                score = float(score)

                if score >= 90:
                    return "★★★★★"

                if score >= 80:
                    return "★★★★☆"

                if score >= 70:
                    return "★★★☆☆"

                if score >= 60:
                    return "★★☆☆☆"

                return "★☆☆☆☆"

            self.df["Rating"] = (
                self.df["Peer Score"]
                .apply(get_rating)
            )

        logging.info(
            "Peer columns normalized"
        )

    # =====================================================
    # REQUIRED COLUMNS
    # =====================================================

    def get_columns(self):

        columns = [
            "company_name",
            "symbol",
            "Sector",
            "ROE",
            "ROCE",
            "NPM",
            "OPM",
            "D/E",
            "ICR",
            "Revenue CAGR",
            "PAT CAGR",
            "Free Cash Flow",
            "Cash Conversion Ratio",
            "Peer Score",
            "Overall Rank",
            "Rating",
        ]

        return [
            column
            for column in columns
            if column in self.df.columns
        ]

    # =====================================================
    # GENERATE INDIVIDUAL COMPANY REPORT
    # =====================================================

    def generate_company_report(self, row):

        columns = self.get_columns()

        report = pd.DataFrame(
            {
                "Metric": columns,
                "Value": [
                    row.get(
                        column,
                        None,
                    )
                    for column in columns
                ],
            }
        )

        company_name = str(
            row.get(
                "company_name",
                row.get(
                    "symbol",
                    "Unknown",
                ),
            )
        )

        file_name = (
            company_name
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
            + "_Peer_Report.xlsx"
        )

        output_path = (
            self.output_folder
            / file_name
        )

        report.to_excel(
            output_path,
            index=False,
        )

        logging.info(
            "Report Saved: %s",
            file_name,
        )

        return output_path

    # =====================================================
    # GENERATE ALL COMPANY REPORTS
    # =====================================================

    def generate_all_reports(self):

        total = len(self.df)

        logging.info(
            "Generating reports for %s companies...",
            total,
        )

        generated = 0

        for _, row in self.df.iterrows():

            try:

                self.generate_company_report(
                    row
                )

                generated += 1

            except Exception as exc:

                company_name = row.get(
                    "company_name",
                    row.get(
                        "symbol",
                        "Unknown",
                    ),
                )

                logging.warning(
                    "%s : %s",
                    company_name,
                    exc,
                )

        logging.info(
            "Individual peer reports generated: %s/%s",
            generated,
            total,
        )

    # =====================================================
    # GENERATE COMBINED EXCEL
    # =====================================================

    def generate_combined_excel(self):

        columns = self.get_columns()

        comparison = self.df[
            columns
        ].copy()

        # Sort strongest peer score first
        if "Peer Score" in comparison.columns:

            comparison = (
                comparison
                .sort_values(
                    "Peer Score",
                    ascending=False,
                    na_position="last",
                )
                .reset_index(drop=True)
            )

        # Add rank if available
        comparison.to_excel(
            self.output_file,
            index=False,
            sheet_name="Peer Comparison",
        )

        logging.info(
            "Combined peer comparison saved: %s",
            self.output_file,
        )

        return self.output_file

    # =====================================================
    # MAIN RUN
    # =====================================================

    def run(self):

        self.normalize_columns()

        self.generate_all_reports()

        combined_file = (
            self.generate_combined_excel()
        )

        logging.info(
            "Peer Comparison Report Completed Successfully"
        )

        return combined_file