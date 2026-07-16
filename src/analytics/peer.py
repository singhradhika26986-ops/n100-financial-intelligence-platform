import pandas as pd
import numpy as np
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class PeerComparison:

    """
    Peer Comparison Engine
    Bluestock Sprint 2
    """

    def __init__(self, dataframe):

        self.df = dataframe.copy()

        logging.info("Peer Comparison Engine Started")

    def calculate_peer_average(self, column):

        if column not in self.df.columns:
            return np.nan

        return self.df[column].mean()


    def calculate_peer_median(self, column):

        if column not in self.df.columns:
            return np.nan

        return self.df[column].median()
    
    def calculate_peer_rank(self, column):

        if column in self.df.columns:

            self.df[f"{column}_Rank"] = (
                self.df[column]
                .rank(ascending=False, method="dense")
            )

        logging.info(f"{column} Ranking Calculated")

        return self.df


    def calculate_above_average(self, column):

        if column in self.df.columns:

            avg = self.df[column].mean()

            self.df[f"{column}_Above_Average"] = (
                self.df[column] > avg
            )

        logging.info(f"{column} Above Average Flag Created")

        return self.df


    def run(self):

        metrics = [
            "ROE",
            "ROCE",
            "Revenue CAGR",
            "PAT CAGR",
            "EPS CAGR",
            "Free Cash Flow"
        ]

        for metric in metrics:

            if metric in self.df.columns:

                self.calculate_peer_rank(metric)
                self.calculate_above_average(metric)

        logging.info("Peer Comparison Engine Completed Successfully")

        return self.df