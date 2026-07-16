import pandas as pd
import numpy as np
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class ScreenerEngine:

    """
    Financial Screener Engine
    Bluestock Sprint 2
    """

    def __init__(self, dataframe):

        self.df = dataframe.copy()

        logging.info("Screener Engine Started")

    def filter_by_roe(self, minimum_roe):

        if "ROE" in self.df.columns:

            self.df = self.df[
                self.df["ROE"] >= minimum_roe
            ]

        logging.info("ROE Filter Applied")

        return self.df


    def filter_by_de(self, maximum_de):

        if "D/E" in self.df.columns:

            self.df = self.df[
                self.df["D/E"] <= maximum_de
            ]

        logging.info("Debt to Equity Filter Applied")

        return self.df
    
    def filter_by_revenue_cagr(self, minimum_cagr):

        if "Revenue CAGR" in self.df.columns:

            self.df = self.df[
                self.df["Revenue CAGR"] >= minimum_cagr
            ]

        logging.info("Revenue CAGR Filter Applied")

        return self.df


    def filter_by_free_cash_flow(self):

        if "Free Cash Flow" in self.df.columns:

            self.df = self.df[
                self.df["Free Cash Flow"] > 0
            ]

        logging.info("Free Cash Flow Filter Applied")

        return self.df
    
    def run(
        self,
        minimum_roe=15,
        maximum_de=1.5,
        minimum_revenue_cagr=10
    ):

        self.filter_by_roe(minimum_roe)
        self.filter_by_de(maximum_de)
        self.filter_by_revenue_cagr(minimum_revenue_cagr)
        self.filter_by_free_cash_flow()

        self.df = self.df.sort_values(
            by="ROE",
            ascending=False
        )

        logging.info("Screener Engine Completed Successfully")

        return self.df