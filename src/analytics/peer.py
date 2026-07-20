import pandas as pd
import numpy as np
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class PeerRankingEngine:

    """
    Peer Ranking Engine
    Sprint 3 - Day 18
    """

    def __init__(self, dataframe):

        self.df = dataframe.copy()

        logging.info("Peer Ranking Engine Started")

    # ==========================================
    # Percentile Ranking
    # ==========================================

    def percentile_rank(self, column, ascending=False):

        if column not in self.df.columns:

            logging.warning(f"{column} not found")

            return

        self.df[column + " Percentile"] = (

            self.df[column]

            .rank(

                pct=True,

                ascending=ascending

            )

            * 100

        )

    # ==========================================
    # Ranking Columns
    # ==========================================

    def calculate_percentiles(self):

        metrics = [

            "ROE",
            "ROCE",
            "NPM",
            "Revenue CAGR",
            "PAT CAGR",
            "Free Cash Flow",
            "Cash Conversion Ratio",
            "ICR"

        ]

        reverse_metrics = [

            "D/E"

        ]

        for metric in metrics:

            self.percentile_rank(metric)

        for metric in reverse_metrics:

            self.percentile_rank(
                metric,
                ascending=True
            )

        logging.info("Percentile Ranking Completed")

            # ==========================================
    # Composite Peer Score
    # ==========================================

    def calculate_peer_score(self):

        percentile_columns = [

            "ROE Percentile",
            "ROCE Percentile",
            "NPM Percentile",
            "Revenue CAGR Percentile",
            "PAT CAGR Percentile",
            "Free Cash Flow Percentile",
            "Cash Conversion Ratio Percentile",
            "ICR Percentile",
            "D/E Percentile"

        ]

        available_columns = [

            col for col in percentile_columns

            if col in self.df.columns

        ]

        self.df["Peer Score"] = (

            self.df[available_columns]

            .mean(axis=1)

        )

        logging.info("Peer Score Calculated")

    # ==========================================
    # Sector Ranking
    # ==========================================

    def sector_rank(self):

        if "Sector" not in self.df.columns:

            logging.warning(
                "Sector column not found"
            )

            return

        self.df["Sector Rank"] = (

            self.df.groupby("Sector")["Peer Score"]

            .rank(

                ascending=False,

                method="dense"

            )

        )

        logging.info("Sector Ranking Completed")

    # ==========================================
    # Overall Ranking
    # ==========================================

    def overall_rank(self):

        self.df["Overall Rank"] = (

            self.df["Peer Score"]

            .rank(

                ascending=False,

                method="dense"

            )

        )

        logging.info("Overall Ranking Completed")

    # ==========================================
    # Rating Labels
    # ==========================================

    def assign_rating(self):

        def rating(score):

            if score >= 90:
                return "★★★★★"

            elif score >= 80:
                return "★★★★☆"

            elif score >= 70:
                return "★★★☆☆"

            elif score >= 60:
                return "★★☆☆☆"

            else:
                return "★☆☆☆☆"

        self.df["Peer Rating"] = (

            self.df["Peer Score"]

            .apply(rating)

        )

        logging.info("Peer Ratings Assigned")

            # ==========================================
    # Export to SQLite
    # ==========================================

    def save_to_database(self, connection):

        self.df.to_sql(
            "peer_ranking",
            connection,
            if_exists="replace",
            index=False
        )

        logging.info("Peer Ranking Saved To SQLite")

    # ==========================================
    # Main Run
    # ==========================================

    def run(self):

        # Step 1 : Percentile Ranking
        self.calculate_percentiles()

        # Step 2 : Composite Peer Score
        self.calculate_peer_score()

        # Step 3 : Sector Ranking
        self.sector_rank()

        # Step 4 : Overall Ranking
        self.overall_rank()

        # Step 5 : Rating
        self.assign_rating()

        # Step 6 : Sort Results
        self.df = self.df.sort_values(
            by="Peer Score",
            ascending=False
        ).reset_index(drop=True)

        logging.info(
            "Peer Ranking Engine Completed Successfully"
        )

        return self.df