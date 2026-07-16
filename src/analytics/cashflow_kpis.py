import pandas as pd
import numpy as np
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class CashFlowKPI:

    """
    Cash Flow KPI Engine
    Bluestock Sprint 2
    """

    def __init__(self, dataframe):

        self.df = dataframe.copy()

        logging.info("Cash Flow KPI Engine Started")

    def safe_divide(self, numerator, denominator):

        denominator = denominator.replace(0, np.nan)

        return numerator / denominator
    
    def calculate_free_cash_flow(self):

        if {
            "operating_cash_flow",
            "capital_expenditure"
        }.issubset(self.df.columns):

            self.df["Free Cash Flow"] = (
                self.df["operating_cash_flow"]
                - self.df["capital_expenditure"]
            )

        logging.info("Free Cash Flow Calculated")

        return self.df


    def calculate_ocf_margin(self):

        if {
            "operating_cash_flow",
            "revenue"
        }.issubset(self.df.columns):

            self.df["OCF Margin"] = (
                self.safe_divide(
                    self.df["operating_cash_flow"],
                    self.df["revenue"]
                ) * 100
            )

        logging.info("OCF Margin Calculated")

        return self.df
    
    def calculate_cash_conversion_ratio(self):

        if {
            "operating_cash_flow",
            "net_profit"
        }.issubset(self.df.columns):

            self.df["Cash Conversion Ratio"] = self.safe_divide(
                self.df["operating_cash_flow"],
                self.df["net_profit"]
            )

        logging.info("Cash Conversion Ratio Calculated")

        return self.df


    def run(self):

        self.calculate_free_cash_flow()
        self.calculate_ocf_margin()
        self.calculate_cash_conversion_ratio()

        numeric_cols = self.df.select_dtypes(include="number").columns

        self.df[numeric_cols] = self.df[numeric_cols].round(2)

        logging.info("Cash Flow KPI Engine Completed Successfully")

        return self.df