import pandas as pd
import numpy as np
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class RatioCalculator:
    """
    Financial Ratio Calculation Engine
    Bluestock Sprint 2
    """

    def __init__(self, dataframe):

        self.df = dataframe.copy()

        logging.info("Ratio Engine Started")

    def safe_divide(self, numerator, denominator):

        denominator = denominator.replace(0, np.nan)

        return numerator / denominator

    def round_values(self):

        numeric_cols = self.df.select_dtypes(include="number").columns

        self.df[numeric_cols] = self.df[numeric_cols].round(2)

        return self.df
    def calculate_profitability_ratios(self):

        # Return on Equity (ROE)
        if {"net_profit", "shareholders_equity"}.issubset(self.df.columns):
            self.df["ROE"] = (
                self.safe_divide(
                    self.df["net_profit"],
                    self.df["shareholders_equity"]
                ) * 100
            )

        # Return on Assets (ROA)
        if {"net_profit", "total_assets"}.issubset(self.df.columns):
            self.df["ROA"] = (
                self.safe_divide(
                    self.df["net_profit"],
                    self.df["total_assets"]
                ) * 100
            )

        # Return on Capital Employed (ROCE)
        if {"ebit", "capital_employed"}.issubset(self.df.columns):
            self.df["ROCE"] = (
                self.safe_divide(
                    self.df["ebit"],
                    self.df["capital_employed"]
                ) * 100
            )

        # Net Profit Margin
        if {"net_profit", "revenue"}.issubset(self.df.columns):
            self.df["NPM"] = (
                self.safe_divide(
                    self.df["net_profit"],
                    self.df["revenue"]
                ) * 100
            )

        # Operating Profit Margin
        if {"operating_profit", "revenue"}.issubset(self.df.columns):
            self.df["OPM"] = (
                self.safe_divide(
                    self.df["operating_profit"],
                    self.df["revenue"]
                ) * 100
            )

        logging.info("Profitability Ratios Calculated")

        return self.df
    
    def calculate_leverage_ratios(self):

        # Debt to Equity
        if {"total_debt", "shareholders_equity"}.issubset(self.df.columns):
            self.df["D/E"] = self.safe_divide(
                self.df["total_debt"],
                self.df["shareholders_equity"]
            )

        # Interest Coverage Ratio
        if {"ebit", "interest_expense"}.issubset(self.df.columns):
            self.df["ICR"] = self.safe_divide(
                self.df["ebit"],
                self.df["interest_expense"]
            )

        logging.info("Leverage Ratios Calculated")

        return self.df


    def calculate_efficiency_ratios(self):

        # Asset Turnover Ratio
        if {"revenue", "total_assets"}.issubset(self.df.columns):
            self.df["Asset Turnover"] = self.safe_divide(
                self.df["revenue"],
                self.df["total_assets"]
            )

        logging.info("Efficiency Ratios Calculated")

        return self.df
    
    def run(self):

        self.calculate_profitability_ratios()
        self.calculate_leverage_ratios()
        self.calculate_efficiency_ratios()

        return self.round_values()