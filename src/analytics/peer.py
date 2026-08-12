import logging

import numpy as np
import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


class PeerRankingEngine:
    """
    Peer Ranking Engine

    Features:
    - Column normalization
    - Latest record selection
    - Percentile ranking
    - Composite peer score
    - Sector ranking
    - Overall ranking
    - Peer rating
    - SQLite export
    """

    def __init__(self, dataframe):
        self.df = dataframe.copy()
        self.available_metrics = []

        logging.info("Peer Ranking Engine Started")

    # =====================================================
    # COLUMN NORMALIZATION
    # =====================================================

    def normalize_columns(self):
        """
        Normalize screener/database column names into
        standard names used by the peer engine.
        """

        column_mapping = {
            "debt_equity": "D/E",
            "revenue_cagr": "Revenue CAGR",
            "pat_cagr": "PAT CAGR",
            "free_cash_flow": "Free Cash Flow",
            "cash_conversion_ratio": "Cash Conversion Ratio",
        }

        for source_column, target_column in column_mapping.items():

            if (
                source_column in self.df.columns
                and target_column not in self.df.columns
            ):
                self.df[target_column] = self.df[
                    source_column
                ]

        # Industry is the project's sector field.
        if "Sector" not in self.df.columns:

            if "industry" in self.df.columns:
                self.df["Sector"] = self.df["industry"]

            else:
                self.df["Sector"] = "Unknown"

        logging.info(
            "Column normalization completed"
        )

    # =====================================================
    # LATEST RECORD PER COMPANY
    # =====================================================

    def keep_latest_company_records(self):
        """
        Keep only the latest financial record for each
        company symbol.
        """

        if "symbol" not in self.df.columns:
            return

        if "report_date" in self.df.columns:

            self.df["report_date"] = pd.to_datetime(
                self.df["report_date"],
                errors="coerce",
            )

            self.df = (
                self.df
                .sort_values("report_date")
                .drop_duplicates(
                    subset=["symbol"],
                    keep="last",
                )
                .reset_index(drop=True)
            )

        else:

            self.df = (
                self.df
                .drop_duplicates(
                    subset=["symbol"],
                    keep="last",
                )
                .reset_index(drop=True)
            )

        logging.info(
            "Latest company records selected: %s",
            len(self.df),
        )

    # =====================================================
    # PERCENTILE RANK
    # =====================================================

    def percentile_rank(
        self,
        column,
        ascending=False,
    ):
        """
        Calculate percentile ranking for a metric.
        """

        if column not in self.df.columns:
            return False

        values = pd.to_numeric(
            self.df[column],
            errors="coerce",
        )

        self.df[
            column + " Percentile"
        ] = (
            values
            .rank(
                pct=True,
                ascending=ascending,
                na_option="keep",
            )
            * 100
        )

        return True

    # =====================================================
    # CALCULATE ALL PERCENTILES
    # =====================================================

    def calculate_percentiles(self):
        """
        Calculate percentile scores for all supported
        peer metrics.
        """

        normal_metrics = [
            "ROE",
            "ROCE",
            "NPM",
            "Revenue CAGR",
            "PAT CAGR",
            "Free Cash Flow",
            "Cash Conversion Ratio",
            "ICR",
        ]

        reverse_metrics = [
            "D/E",
        ]

        self.available_metrics = []

        for metric in normal_metrics:

            if self.percentile_rank(metric):
                self.available_metrics.append(metric)

        for metric in reverse_metrics:

            if self.percentile_rank(
                metric,
                ascending=True,
            ):
                self.available_metrics.append(metric)

        logging.info(
            "Percentile Ranking Completed"
        )

        logging.info(
            "Metrics used: %s",
            ", ".join(self.available_metrics),
        )

    # =====================================================
    # COMPOSITE PEER SCORE
    # =====================================================

    def calculate_peer_score(self):
        """
        Calculate the average percentile score.
        """

        percentile_columns = [
            metric + " Percentile"
            for metric in self.available_metrics
        ]

        if not percentile_columns:

            self.df["Peer Score"] = np.nan

            logging.warning(
                "No peer metrics available"
            )

            return

        self.df["Peer Score"] = (
            self.df[percentile_columns]
            .mean(
                axis=1,
                skipna=True,
            )
            .round(2)
        )

        logging.info(
            "Peer Score Calculated"
        )

    # =====================================================
    # SECTOR RANKING
    # =====================================================

    def sector_rank(self):
        """
        Rank companies within their industry/sector.
        """

        if "Sector" not in self.df.columns:
            self.df["Sector"] = "Unknown"

        self.df["Sector"] = (
            self.df["Sector"]
            .fillna("Unknown")
            .astype(str)
        )

        self.df["Sector Rank"] = (
            self.df
            .groupby("Sector")["Peer Score"]
            .rank(
                ascending=False,
                method="dense",
            )
        )

        logging.info(
            "Sector Ranking Completed"
        )

    # =====================================================
    # OVERALL RANKING
    # =====================================================

    def overall_rank(self):
        """
        Rank all companies by Peer Score.
        """

        self.df["Overall Rank"] = (
            self.df["Peer Score"]
            .rank(
                ascending=False,
                method="dense",
            )
        )

        logging.info(
            "Overall Ranking Completed"
        )

    # =====================================================
    # PEER RATING
    # =====================================================

    def assign_rating(self):
        """
        Convert Peer Score into a 5-star rating.
        """

        def rating(score):

            if pd.isna(score):
                return "N/A"

            if score >= 90:
                return "★★★★★"

            if score >= 80:
                return "★★★★☆"

            if score >= 70:
                return "★★★☆☆"

            if score >= 60:
                return "★★☆☆☆"

            return "★☆☆☆☆"

        self.df["Peer Rating"] = (
            self.df["Peer Score"]
            .apply(rating)
        )

        logging.info(
            "Peer Ratings Assigned"
        )

    # =====================================================
    # SAVE TO SQLITE
    # =====================================================

    def save_to_database(self, connection):
        """
        Save peer ranking results to SQLite.
        """

        self.df.to_sql(
            "peer_ranking",
            connection,
            if_exists="replace",
            index=False,
        )

        logging.info(
            "Peer Ranking Saved To SQLite"
        )

    # =====================================================
    # MAIN PIPELINE
    # =====================================================

    def run(self):
        """
        Execute complete peer ranking pipeline.
        """

        # Step 1
        self.normalize_columns()

        # Step 2
        self.keep_latest_company_records()

        # Step 3
        self.calculate_percentiles()

        # Step 4
        self.calculate_peer_score()

        # Step 5
        self.sector_rank()

        # Step 6
        self.overall_rank()

        # Step 7
        self.assign_rating()

        # Step 8
        self.df = (
            self.df
            .sort_values(
                by="Peer Score",
                ascending=False,
                na_position="last",
            )
            .reset_index(drop=True)
        )

        logging.info(
            "Peer Ranking Engine Completed Successfully"
        )

        return self.df