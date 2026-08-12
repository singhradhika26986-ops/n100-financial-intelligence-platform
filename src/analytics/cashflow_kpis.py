import logging
from pathlib import Path

import numpy as np
import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


class CashFlowIntelligenceEngine:
    """
    Sprint 5 - Day 31
    Cash Flow Intelligence Engine

    Features:
    - CFO Quality Score
    - CFO Quality Label
    - CapEx Intensity
    - CapEx Label
    - FCF CAGR
    - FCF Conversion
    - Distress Signal
    - Deleveraging Flag
    - Capital Allocation Label
    - Excel output
    - Distress alert CSV
    """

    def __init__(self, dataframe, output_dir="output"):

        self.df = dataframe.copy()

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        logging.info(
            "Cash Flow Intelligence Engine Started"
        )

    # =====================================================
    # COLUMN HELPERS
    # =====================================================

    def find_column(self, candidates):

        for column in candidates:

            if column in self.df.columns:
                return column

        return None

    def numeric_column(self, candidates):

        column = self.find_column(candidates)

        if column is None:
            return None

        self.df[column] = pd.to_numeric(
            self.df[column],
            errors="coerce",
        )

        return column

    # =====================================================
    # COLUMN NORMALIZATION
    # =====================================================

    def normalize_columns(self):

        mapping = {}

        aliases = {
            "company_id": [
                "company_id",
                "Company ID",
                "id",
            ],
            "company_name": [
                "company_name",
                "Company Name",
            ],
            "symbol": [
                "symbol",
                "Symbol",
                "ticker",
            ],
            "sector": [
                "sector",
                "Sector",
                "industry",
                "Industry",
            ],
            "report_date": [
                "report_date",
                "Report Date",
                "date",
                "year",
            ],
            "operating_cash_flow": [
                "operating_cash_flow",
                "Operating Cash Flow",
                "CFO",
                "cfo",
            ],
            "net_profit": [
                "net_profit",
                "Net Profit",
                "PAT",
                "pat",
            ],
            "capital_expenditure": [
                "capital_expenditure",
                "Capital Expenditure",
                "CapEx",
                "capex",
            ],
            "investing_activity": [
                "investing_activity",
                "Investing Activity",
                "CFI",
                "cfi",
            ],
            "financing_activity": [
                "financing_activity",
                "Financing Activity",
                "CFF",
                "cff",
            ],
            "borrowings": [
                "borrowings",
                "Borrowings",
                "debt",
                "Debt",
                "total_debt",
            ],
            "revenue": [
                "revenue",
                "Revenue",
                "sales",
                "Sales",
            ],
            "free_cash_flow": [
                "free_cash_flow",
                "Free Cash Flow",
                "FCF",
            ],
        }

        for standard_name, candidates in aliases.items():

            source = self.find_column(candidates)

            if source is not None:
                mapping[standard_name] = source

        for standard_name, source in mapping.items():

            if standard_name not in self.df.columns:

                self.df[standard_name] = self.df[source]

        if "sector" not in self.df.columns:

            self.df["sector"] = "Unknown"

        self.df["sector"] = (
            self.df["sector"]
            .fillna("Unknown")
            .astype(str)
        )

        logging.info(
            "Cash flow columns normalized"
        )

    # =====================================================
    # FREE CASH FLOW
    # =====================================================

    def calculate_free_cash_flow(self):

        if "free_cash_flow" in self.df.columns:

            self.df["free_cash_flow"] = pd.to_numeric(
                self.df["free_cash_flow"],
                errors="coerce",
            )

        elif {
            "operating_cash_flow",
            "capital_expenditure",
        }.issubset(self.df.columns):

            self.df["free_cash_flow"] = (
                pd.to_numeric(
                    self.df["operating_cash_flow"],
                    errors="coerce",
                )
                - pd.to_numeric(
                    self.df["capital_expenditure"],
                    errors="coerce",
                )
            )

        else:

            self.df["free_cash_flow"] = np.nan

        logging.info(
            "Free Cash Flow calculated"
        )

    # =====================================================
    # CFO QUALITY
    # =====================================================

    def calculate_cfo_quality(self):

        if {
            "operating_cash_flow",
            "net_profit",
        }.issubset(self.df.columns):

            cfo = pd.to_numeric(
                self.df["operating_cash_flow"],
                errors="coerce",
            )

            pat = pd.to_numeric(
                self.df["net_profit"],
                errors="coerce",
            )

            pat = pat.replace(0, np.nan)

            self.df["cfo_pat_ratio"] = (
                cfo / pat
            )

        else:

            self.df["cfo_pat_ratio"] = np.nan

        # Company-level quality score.
        # If multiple years exist, average later in aggregation.
        self.df["cfo_quality_score"] = (
            self.df["cfo_pat_ratio"]
        )

        self.df["cfo_quality_label"] = (
            self.df["cfo_quality_score"]
            .apply(
                self._cfo_quality_label
            )
        )

        logging.info(
            "CFO Quality calculated"
        )

    @staticmethod
    def _cfo_quality_label(value):

        if pd.isna(value):
            return "Insufficient Data"

        if value > 1.0:
            return "High Quality"

        if value >= 0.5:
            return "Moderate"

        return "Accrual Risk"

    # =====================================================
    # CAPEX INTENSITY
    # =====================================================

    def calculate_capex_intensity(self):

        if "investing_activity" in self.df.columns:

            investment = pd.to_numeric(
                self.df["investing_activity"],
                errors="coerce",
            ).abs()

        elif "capital_expenditure" in self.df.columns:

            investment = pd.to_numeric(
                self.df["capital_expenditure"],
                errors="coerce",
            ).abs()

        else:

            investment = pd.Series(
                np.nan,
                index=self.df.index,
            )

        if "revenue" in self.df.columns:

            revenue = pd.to_numeric(
                self.df["revenue"],
                errors="coerce",
            )

            revenue = revenue.replace(
                0,
                np.nan,
            )

            self.df["capex_intensity_pct"] = (
                investment / revenue * 100
            )

        else:

            self.df["capex_intensity_pct"] = np.nan

        self.df["capex_label"] = (
            self.df["capex_intensity_pct"]
            .apply(
                self._capex_label
            )
        )

        logging.info(
            "CapEx Intensity calculated"
        )

    @staticmethod
    def _capex_label(value):

        if pd.isna(value):
            return "Insufficient Data"

        if value < 3:
            return "Asset Light"

        if value <= 8:
            return "Moderate"

        return "Capital Intensive"

    # =====================================================
    # DISTRESS SIGNAL
    # =====================================================

    def calculate_distress_signal(self):

        if {
            "operating_cash_flow",
            "financing_activity",
        }.issubset(self.df.columns):

            cfo = pd.to_numeric(
                self.df["operating_cash_flow"],
                errors="coerce",
            )

            cff = pd.to_numeric(
                self.df["financing_activity"],
                errors="coerce",
            )

            self.df["distress_flag"] = (
                (cfo < 0)
                & (cff > 0)
            )

        else:

            self.df["distress_flag"] = False

        logging.info(
            "Distress Signal detection completed"
        )

    # =====================================================
    # DELEVERAGING
    # =====================================================

    def calculate_deleveraging(self):

        self.df["deleveraging_flag"] = False

        if "symbol" not in self.df.columns:
            return

        if "borrowings" not in self.df.columns:
            return

        if "report_date" not in self.df.columns:
            return

        self.df["report_date"] = pd.to_datetime(
            self.df["report_date"],
            errors="coerce",
        )

        self.df = self.df.sort_values(
            [
                "symbol",
                "report_date",
            ]
        )

        previous_borrowings = (
            self.df
            .groupby("symbol")["borrowings"]
            .shift(1)
        )

        if "financing_activity" in self.df.columns:

            cff = pd.to_numeric(
                self.df["financing_activity"],
                errors="coerce",
            )

            borrowing = pd.to_numeric(
                self.df["borrowings"],
                errors="coerce",
            )

            self.df["deleveraging_flag"] = (
                (cff < 0)
                & (borrowing < previous_borrowings)
            )

        logging.info(
            "Deleveraging detection completed"
        )

    # =====================================================
    # FCF CONVERSION
    # =====================================================

    def calculate_fcf_conversion(self):

        if {
            "free_cash_flow",
            "operating_cash_flow",
        }.issubset(self.df.columns):

            cfo = pd.to_numeric(
                self.df["operating_cash_flow"],
                errors="coerce",
            )

            cfo = cfo.replace(
                0,
                np.nan,
            )

            self.df["fcf_conversion_pct"] = (
                pd.to_numeric(
                    self.df["free_cash_flow"],
                    errors="coerce",
                )
                / cfo
                * 100
            )

        else:

            self.df["fcf_conversion_pct"] = np.nan

        logging.info(
            "FCF Conversion calculated"
        )

    # =====================================================
    # FCF CAGR - 5 YEAR
    # =====================================================

    def calculate_fcf_cagr(self):

        self.df["fcf_cagr_5yr"] = np.nan

        if not {
            "symbol",
            "report_date",
            "free_cash_flow",
        }.issubset(self.df.columns):
            return

        temp = self.df.copy()

        temp["report_date"] = pd.to_datetime(
            temp["report_date"],
            errors="coerce",
        )

        temp["free_cash_flow"] = pd.to_numeric(
            temp["free_cash_flow"],
            errors="coerce",
        )

        for symbol, group in temp.groupby(
            "symbol"
        ):

            group = group.sort_values(
                "report_date"
            )

            if len(group) < 6:
                continue

            start = group.iloc[-6]["free_cash_flow"]
            end = group.iloc[-1]["free_cash_flow"]

            if (
                pd.isna(start)
                or pd.isna(end)
                or start <= 0
                or end <= 0
            ):
                continue

            cagr = (
                (end / start) ** (1 / 5)
                - 1
            ) * 100

            self.df.loc[
                self.df["symbol"] == symbol,
                "fcf_cagr_5yr",
            ] = round(cagr, 2)

        logging.info(
            "5-year FCF CAGR calculated"
        )

    # =====================================================
    # CAPITAL ALLOCATION LABEL
    # =====================================================

    def assign_capital_allocation_label(self):

        def label(row):

            if row.get(
                "distress_flag",
                False,
            ):
                return "Distress Signal"

            if row.get(
                "deleveraging_flag",
                False,
            ):
                return "Deleveraging"

            fcf = row.get(
                "free_cash_flow",
                np.nan,
            )

            if pd.notna(fcf) and fcf > 0:
                return "Reinvestor"

            return "Neutral"

        self.df[
            "capital_allocation_label"
        ] = self.df.apply(
            label,
            axis=1,
        )

        logging.info(
            "Capital allocation labels assigned"
        )

    # =====================================================
    # LATEST RECORD PER COMPANY
    # =====================================================

    def latest_records(self):

        if {
            "symbol",
            "report_date",
        }.issubset(self.df.columns):

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

        logging.info(
            "Latest cash flow records retained: %s",
            len(self.df),
        )

    # =====================================================
    # EXPORT
    # =====================================================

    def export_outputs(self):

        required_columns = [
            "company_id",
            "company_name",
            "symbol",
            "sector",
            "cfo_quality_score",
            "cfo_quality_label",
            "capex_intensity_pct",
            "capex_label",
            "fcf_cagr_5yr",
            "fcf_conversion_pct",
            "distress_flag",
            "deleveraging_flag",
            "capital_allocation_label",
        ]

        available_columns = [
            column
            for column in required_columns
            if column in self.df.columns
        ]

        output_df = self.df[
            available_columns
        ].copy()

        excel_path = (
            self.output_dir
            / "cashflow_intelligence.xlsx"
        )

        output_df.to_excel(
            excel_path,
            index=False,
        )

        distress_df = output_df[
            output_df["distress_flag"] == True
        ].copy()

        alert_columns = [
            column
            for column in [
                "company_id",
                "company_name",
                "symbol",
                "sector",
                "operating_cash_flow",
                "financing_activity",
                "net_profit",
                "distress_flag",
            ]
            if column in self.df.columns
            or column in distress_df.columns
        ]

        if not distress_df.empty:

            distress_output = self.df[
                [
                    column
                    for column in alert_columns
                    if column in self.df.columns
                ]
            ].copy()

        else:

            distress_output = pd.DataFrame(
                columns=alert_columns
            )

        distress_path = (
            self.output_dir
            / "distress_alerts.csv"
        )

        distress_output.to_csv(
            distress_path,
            index=False,
        )

        logging.info(
            "Saved: %s",
            excel_path,
        )

        logging.info(
            "Saved: %s",
            distress_path,
        )

        return output_df

    # =====================================================
    # MAIN PIPELINE
    # =====================================================

    def run(self):

        self.normalize_columns()

        self.calculate_free_cash_flow()

        self.calculate_cfo_quality()

        self.calculate_capex_intensity()

        self.calculate_distress_signal()

        self.calculate_deleveraging()

        self.calculate_fcf_conversion()

        self.calculate_fcf_cagr()

        self.assign_capital_allocation_label()

        self.latest_records()

        numeric_columns = (
            self.df
            .select_dtypes(
                include="number"
            )
            .columns
        )

        self.df[numeric_columns] = (
            self.df[numeric_columns]
            .round(2)
        )

        result = self.export_outputs()

        logging.info(
            "Cash Flow Intelligence Engine "
            "Completed Successfully"
        )

        return result