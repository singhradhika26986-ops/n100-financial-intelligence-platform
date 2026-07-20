import pandas as pd
import numpy as np
import logging
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class ScreenerEngine:
    """
    Financial Screener Engine
    Sprint 3
    """

    def __init__(self, dataframe, config):

        self.df = dataframe.copy()
        self.config = config

        logging.info("Screener Engine Started")

    # ==================================================
    # APPLY FILTERS
    # ==================================================

    def apply_filters(self):

        for column, value in self.config.items():

            if column not in self.df.columns:
                continue

            # Maximum Filters
            if column in ["D/E", "P/E", "P/B"]:

                self.df = self.df[
                    self.df[column] <= value
                ]

            # Minimum Filters
            else:

                self.df = self.df[
                    self.df[column] >= value
                ]

        logging.info("All Config Filters Applied")

    # ==================================================
    # ADVANCED COMPOSITE SCORE
    # ==================================================

    def calculate_composite_score(self):

        # -------------------------
        # Profitability (35%)
        # -------------------------

        profitability = (

            self.df["ROE"].fillna(0) * 0.15

            +

            self.df["ROCE"].fillna(0) * 0.10

            +

            self.df["NPM"].fillna(0) * 0.10

        )

        # -------------------------
        # Cash Quality (30%)
        # -------------------------

        fcf_score = (

            self.df["Free Cash Flow"]
            .rank(pct=True)
            .fillna(0)
            * 15

        )

        cash_conversion = (

            self.df["Cash Conversion Ratio"]
            .fillna(0)
            * 10

        )

        positive_fcf = (

            (
                self.df["Free Cash Flow"] > 0
            ).astype(int)
            * 5

        )

        cash_quality = (

            fcf_score

            +

            cash_conversion

            +

            positive_fcf

        )

        # -------------------------
        # Growth (20%)
        # -------------------------

        growth = (

            self.df["Revenue CAGR"].fillna(0) * 0.10

            +

            self.df["PAT CAGR"].fillna(0) * 0.10

        )

        # -------------------------
        # Leverage (15%)
        # -------------------------

        leverage = (

            (

                1 /

                self.df["D/E"]
                .replace(0, 0.01)

            )

            * 10

            +

            self.df["ICR"].fillna(0) * 0.05

        )

        # -------------------------
        # Final Composite Score
        # -------------------------

        self.df["Composite Score"] = (

            profitability

            +

            cash_quality

            +

            growth

            +

            leverage

        )

        logging.info("Advanced Composite Score Calculated")

            # ==================================================
    # PRESET SCREENERS
    # ==================================================

    def get_quality_compounder(self):

        config = {
            "ROE": 15,
            "D/E": 1,
            "Revenue CAGR": 10,
            "Free Cash Flow": 0
        }

        engine = ScreenerEngine(
            self.df.copy(),
            config
        )

        return engine.run()

    def get_value_pick(self):

        config = {
            "ROE": 10,
            "D/E": 2,
            "Revenue CAGR": 4,
            "Free Cash Flow": 0
        }

        engine = ScreenerEngine(
            self.df.copy(),
            config
        )

        return engine.run()

    def get_growth_accelerator(self):

        config = {
            "ROE": 12,
            "D/E": 2,
            "Revenue CAGR": 15,
            "Free Cash Flow": 0
        }

        engine = ScreenerEngine(
            self.df.copy(),
            config
        )

        return engine.run()

    def get_dividend_champion(self):

        config = {
            "ROE": 12,
            "D/E": 2,
            "Revenue CAGR": 4,
            "Free Cash Flow": 0
        }

        engine = ScreenerEngine(
            self.df.copy(),
            config
        )

        return engine.run()

    def get_debt_free_bluechip(self):

        config = {
            "ROE": 12,
            "D/E": 0,
            "Revenue CAGR": 4,
            "Free Cash Flow": 0
        }

        engine = ScreenerEngine(
            self.df.copy(),
            config
        )

        return engine.run()

    def get_turnaround_watch(self):

        config = {
            "ROE": 8,
            "D/E": 2,
            "Revenue CAGR": 4,
            "Free Cash Flow": 0
        }

        engine = ScreenerEngine(
            self.df.copy(),
            config
        )

        return engine.run()

    # ==================================================
    # HELPER FUNCTIONS
    # ==================================================

    def winsorize(self, column):

        if column not in self.df.columns:
            return

        lower = self.df[column].quantile(0.10)
        upper = self.df[column].quantile(0.90)

        self.df[column] = self.df[column].clip(
            lower=lower,
            upper=upper
        )

    def apply_winsorization(self):

        columns = [

            "ROE",
            "ROCE",
            "NPM",
            "Revenue CAGR",
            "PAT CAGR",
            "Free Cash Flow",
            "Cash Conversion Ratio",
            "ICR"

        ]

        for col in columns:

            if col in self.df.columns:
                self.winsorize(col)

        logging.info("Winsorization Applied")

    def sector_normalization(self):

        if "Sector" not in self.df.columns:

            logging.warning(
                "Sector column not found. Skipping normalization."
            )

            return

        self.df["Sector Score"] = (

            self.df.groupby("Sector")["Composite Score"]

            .transform(

                lambda x:

                (x - x.mean())

                /

                (x.std() + 1e-9)

            )

        )

        logging.info("Sector Normalization Completed")

            # ==================================================
    # MAIN RUN
    # ==================================================

    def run(self):

        # Step 1 : Apply Filters
        self.apply_filters()

        # Step 2 : Winsorization
        self.apply_winsorization()

        # Step 3 : Composite Score
        self.calculate_composite_score()

        # Step 4 : Sector Normalization
        self.sector_normalization()

        # Step 5 : Sorting
        if "Sector Score" in self.df.columns:

            self.df = self.df.sort_values(
                by="Sector Score",
                ascending=False
            )

        else:

            self.df = self.df.sort_values(
                by="Composite Score",
                ascending=False
            )

        # Step 6 : Reset Index
        self.df = self.df.reset_index(drop=True)

        logging.info("Screener Engine Completed Successfully")

        return self.df