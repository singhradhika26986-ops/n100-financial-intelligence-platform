import pandas as pd
import numpy as np
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class CapitalAllocation:
    """
    Capital Allocation Engine
    Bluestock Sprint 2
    """

    def __init__(self, dataframe):

        self.df = dataframe.copy()

        logging.info("Capital Allocation Engine Started")

    def safe_divide(self, numerator, denominator):

        denominator = denominator.replace(0, np.nan)

        return numerator / denominator

    def calculate_dividend_payout(self):
        """
        Dividend data is not available in the current dataset.
        Create the column so the pipeline does not fail.
        """

        self.df["Dividend Payout"] = np.nan

        logging.info("Dividend Payout Calculated")

        return self.df

    def calculate_retention_ratio(self):
        """
        Retention Ratio = 100 - Dividend Payout
        Will remain NaN until dividend data becomes available.
        """

        self.df["Retention Ratio"] = (
            100 - self.df["Dividend Payout"]
        )

        logging.info("Retention Ratio Calculated")

        return self.df

    def calculate_reinvestment_ratio(self):

        if {
            "capital_expenditure",
            "operating_cash_flow"
        }.issubset(self.df.columns):

            self.df["Reinvestment Ratio"] = (
                self.safe_divide(
                    self.df["capital_expenditure"],
                    self.df["operating_cash_flow"]
                ) * 100
            )

        else:

            self.df["Reinvestment Ratio"] = np.nan

        logging.info("Reinvestment Ratio Calculated")

        return self.df

    def run(self):

        self.calculate_dividend_payout()
        self.calculate_retention_ratio()
        self.calculate_reinvestment_ratio()

        numeric_cols = self.df.select_dtypes(include="number").columns

        self.df[numeric_cols] = self.df[numeric_cols].round(2)

        logging.info("Capital Allocation Engine Completed Successfully")

        return self.df