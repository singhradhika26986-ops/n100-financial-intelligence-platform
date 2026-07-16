import pandas as pd
import numpy as np
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class CAGRCalculator:
    """
    CAGR Calculation Engine
    Bluestock Sprint 2
    """

    def __init__(self, dataframe):

        self.df = dataframe.copy()

        logging.info("CAGR Engine Started")

    def calculate_cagr(self, start_value, end_value, years):

        if (
            pd.isna(start_value)
            or pd.isna(end_value)
            or start_value <= 0
            or end_value <= 0
            or years <= 0
        ):
            return np.nan

        return ((end_value / start_value) ** (1 / years) - 1) * 100
    
   
    def calculate_revenue_cagr(self):

        if {
            "revenue_start",
            "revenue_end",
            "years"
        }.issubset(self.df.columns):

            self.df["Revenue CAGR"] = self.df.apply(
                lambda row: self.calculate_cagr(
                    row["revenue_start"],
                    row["revenue_end"],
                    row["years"]
                ),
                axis=1
            )

        logging.info("Revenue CAGR Calculated")

        return self.df


    def calculate_pat_cagr(self):

        if {
            "pat_start",
            "pat_end",
            "years"
        }.issubset(self.df.columns):

            self.df["PAT CAGR"] = self.df.apply(
                lambda row: self.calculate_cagr(
                    row["pat_start"],
                    row["pat_end"],
                    row["years"]
                ),
                axis=1
            )

        logging.info("PAT CAGR Calculated")

        return self.df


    def calculate_eps_cagr(self):

        if {
            "eps_start",
            "eps_end",
            "years"
        }.issubset(self.df.columns):

            self.df["EPS CAGR"] = self.df.apply(
                lambda row: self.calculate_cagr(
                    row["eps_start"],
                    row["eps_end"],
                    row["years"]
                ),
                axis=1
            )

        logging.info("EPS CAGR Calculated")

        return self.df
    
    def run(self):

        self.calculate_revenue_cagr()
        self.calculate_pat_cagr()
        self.calculate_eps_cagr()

        numeric_cols = self.df.select_dtypes(include="number").columns

        self.df[numeric_cols] = self.df[numeric_cols].round(2)

        logging.info("CAGR Engine Completed Successfully")

        return self.df