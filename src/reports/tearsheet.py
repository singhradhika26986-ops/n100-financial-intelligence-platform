import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    PageTemplate,
    PageBreak,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from src.dashboard.utils.db import execute_query


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


class CompanyTearsheet:
    """
    Sprint 5 - Day 33

    Two-page company financial tearsheet.

    Page 1:
    - Company header
    - 6 KPI tiles
    - Revenue & Net Profit chart
    - ROE & ROCE trend chart

    Page 2:
    - Balance Sheet composition stacked bar
    - Cash Flow waterfall
    - Pros
    - Cons
    - Capital Allocation badge
    """

    def __init__(
        self,
        symbol,
        output_dir="reports/tearsheets",
    ):

        self.symbol = str(symbol).upper()

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.company = {}
        self.financial = pd.DataFrame()
        self.balance = pd.DataFrame()
        self.cashflow = pd.DataFrame()

        styles = getSampleStyleSheet()

        self.body_style = ParagraphStyle(
            "TearsheetBody",
            parent=styles["BodyText"],
            fontSize=8,
            leading=10,
        )

        self.small_style = ParagraphStyle(
            "TearsheetSmall",
            parent=styles["BodyText"],
            fontSize=7,
            leading=9,
        )

        self.kpi_style = ParagraphStyle(
            "TearsheetKPI",
            parent=styles["BodyText"],
            fontSize=8,
            leading=10,
            alignment=TA_LEFT,
        )

        self.section_style = ParagraphStyle(
            "TearsheetSection",
            parent=styles["Heading2"],
            fontSize=11,
            leading=13,
            spaceAfter=4,
        )

        logging.info(
            "Tearsheet initialized for %s",
            self.symbol,
        )

    # =====================================================
    # DATA LOADING
    # =====================================================

    def load_company(self):

        query = """
        SELECT *
        FROM companies
        WHERE symbol = ?
        LIMIT 1
        """

        df = execute_query(
            query,
            (self.symbol,),
        )

        if df.empty:
            raise ValueError(
                f"Company not found: {self.symbol}"
            )

        self.company = df.iloc[0].to_dict()

    def load_financial_data(self):

        query = """
        SELECT *
        FROM financial_ratios
        WHERE symbol = ?
        ORDER BY report_date ASC
        """

        self.financial = execute_query(
            query,
            (self.symbol,),
        )

        if self.financial.empty:
            raise ValueError(
                f"No financial data found for {self.symbol}"
            )

        self.financial["report_date"] = pd.to_datetime(
            self.financial["report_date"],
            errors="coerce",
        )

        self.financial = (
            self.financial
            .dropna(subset=["report_date"])
            .sort_values("report_date")
            .reset_index(drop=True)
        )

    def load_balance_sheet(self):

        query = """
        SELECT *
        FROM balance_sheet
        WHERE symbol = ?
        ORDER BY report_date ASC
        """

        self.balance = execute_query(
            query,
            (self.symbol,),
        )

        if not self.balance.empty:

            self.balance["report_date"] = pd.to_datetime(
                self.balance["report_date"],
                errors="coerce",
            )

            self.balance = (
                self.balance
                .dropna(subset=["report_date"])
                .sort_values("report_date")
                .reset_index(drop=True)
            )

    def load_cashflow(self):

        query = """
        SELECT *
        FROM cash_flow
        WHERE symbol = ?
        ORDER BY report_date ASC
        """

        self.cashflow = execute_query(
            query,
            (self.symbol,),
        )

        if not self.cashflow.empty:

            self.cashflow["report_date"] = pd.to_datetime(
                self.cashflow["report_date"],
                errors="coerce",
            )

            self.cashflow = (
                self.cashflow
                .dropna(subset=["report_date"])
                .sort_values("report_date")
                .reset_index(drop=True)
            )

    def load_data(self):

        self.load_company()
        self.load_financial_data()
        self.load_balance_sheet()
        self.load_cashflow()

        logging.info(
            "Data loaded for %s",
            self.symbol,
        )

    # =====================================================
    # VALUE HELPERS
    # =====================================================

    @staticmethod
    def number(value):

        if pd.isna(value):
            return "N/A"

        try:

            value = float(value)

            if abs(value) >= 1_000_000_000_000:
                return f"{value / 1_000_000_000_000:.2f}T"

            if abs(value) >= 1_000_000_000:
                return f"{value / 1_000_000_000:.2f}B"

            if abs(value) >= 1_000_000:
                return f"{value / 1_000_000:.2f}M"

            if abs(value) >= 1_000:
                return f"{value / 1_000:.2f}K"

            return f"{value:.2f}"

        except Exception:
            return "N/A"

    @staticmethod
    def value_from_row(row, candidates):

        for column in candidates:

            if column in row.index:

                value = pd.to_numeric(
                    row[column],
                    errors="coerce",
                )

                if pd.notna(value):
                    return value

        return np.nan

    def latest_financial(self):

        return self.financial.iloc[-1]

    # =====================================================
    # KPI HELPERS
    # =====================================================

    def _percent(self, row, columns):

        value = self.value_from_row(
            row,
            columns,
        )

        if pd.isna(value):
            return "N/A"

        return f"{value:.2f}%"

    def _plain(self, row, columns):

        value = self.value_from_row(
            row,
            columns,
        )

        if pd.isna(value):
            return "N/A"

        return f"{value:.2f}"

    def get_kpis(self):

        row = self.latest_financial()

        return [
            (
                "Revenue",
                self.number(
                    self.value_from_row(
                        row,
                        ["revenue"],
                    )
                ),
            ),
            (
                "Net Profit",
                self.number(
                    self.value_from_row(
                        row,
                        ["net_profit"],
                    )
                ),
            ),
            (
                "ROE",
                self._percent(
                    row,
                    ["ROE"],
                ),
            ),
            (
                "ROCE",
                self._percent(
                    row,
                    ["ROCE"],
                ),
            ),
            (
                "D/E",
                self._plain(
                    row,
                    ["D/E", "debt_equity"],
                ),
            ),
            (
                "ICR",
                self._plain(
                    row,
                    ["ICR"],
                ),
            ),
        ]

    # =====================================================
    # PAGE 1 - REVENUE / PROFIT CHART
    # =====================================================

    def revenue_profit_chart(self):

        data = self.financial.tail(10).copy()

        if data.empty:
            return None

        if "revenue" not in data.columns:
            return None

        if "net_profit" not in data.columns:
            return None

        data["revenue"] = pd.to_numeric(
            data["revenue"],
            errors="coerce",
        )

        data["net_profit"] = pd.to_numeric(
            data["net_profit"],
            errors="coerce",
        )

        data = data.dropna(
            subset=[
                "revenue",
                "net_profit",
            ]
        )

        if data.empty:
            return None

        labels = [
            str(year)
            for year in data["report_date"].dt.year
        ]

        x = np.arange(len(data))
        width = 0.35

        fig, ax = plt.subplots(
            figsize=(7.0, 3.0)
        )

        ax.bar(
            x - width / 2,
            data["revenue"] / 1e9,
            width,
            label="Revenue",
        )

        ax.bar(
            x + width / 2,
            data["net_profit"] / 1e9,
            width,
            label="Net Profit",
        )

        ax.set_xticks(x)
        ax.set_xticklabels(
            labels,
            rotation=45,
            ha="right",
            fontsize=7,
        )

        ax.set_ylabel(
            "₹ Billion",
            fontsize=8,
        )

        ax.set_title(
            "10-Year Revenue & Net Profit",
            fontsize=10,
        )

        ax.legend(
            fontsize=7,
        )

        fig.tight_layout()

        path = (
            self.output_dir
            / f"{self.symbol}_revenue_profit.png"
        )

        fig.savefig(
            path,
            dpi=150,
            bbox_inches="tight",
        )

        plt.close(fig)

        return path

    # =====================================================
    # PAGE 1 - ROE / ROCE
    # =====================================================

    def roe_roce_chart(self):

        data = self.financial.tail(10).copy()

        if data.empty:
            return None

        if "ROE" not in data.columns:
            return None

        if "ROCE" not in data.columns:
            return None

        data["ROE"] = pd.to_numeric(
            data["ROE"],
            errors="coerce",
        )

        data["ROCE"] = pd.to_numeric(
            data["ROCE"],
            errors="coerce",
        )

        data = data.dropna(
            subset=[
                "ROE",
                "ROCE",
            ],
            how="all",
        )

        if data.empty:
            return None

        labels = [
            str(year)
            for year in data["report_date"].dt.year
        ]

        x = np.arange(len(data))

        fig, ax = plt.subplots(
            figsize=(7.0, 3.0)
        )

        ax.plot(
            x,
            data["ROE"],
            marker="o",
            label="ROE",
        )

        ax.plot(
            x,
            data["ROCE"],
            marker="o",
            label="ROCE",
        )

        ax.set_xticks(x)
        ax.set_xticklabels(
            labels,
            rotation=45,
            ha="right",
            fontsize=7,
        )

        ax.set_ylabel(
            "%",
            fontsize=8,
        )

        ax.set_title(
            "ROE & ROCE Trend",
            fontsize=10,
        )

        ax.legend(
            fontsize=7,
        )

        fig.tight_layout()

        path = (
            self.output_dir
            / f"{self.symbol}_roe_roce.png"
        )

        fig.savefig(
            path,
            dpi=150,
            bbox_inches="tight",
        )

        plt.close(fig)

        return path

    # =====================================================
    # PAGE 2 - BALANCE SHEET STACKED BAR
    # =====================================================

    def balance_sheet_chart(self):

        if self.balance.empty:
            return None

        required = [
            "report_date",
            "shareholders_equity",
            "total_debt",
            "total_assets",
        ]

        if not all(
            column in self.balance.columns
            for column in required
        ):
            return None

        data = self.balance.copy()

        data["equity"] = pd.to_numeric(
            data["shareholders_equity"],
            errors="coerce",
        ).fillna(0)

        data["borrowings"] = pd.to_numeric(
            data["total_debt"],
            errors="coerce",
        ).fillna(0)

        data["assets"] = pd.to_numeric(
            data["total_assets"],
            errors="coerce",
        ).fillna(0)

        data["other_liabilities"] = (
            data["assets"]
            - data["equity"]
            - data["borrowings"]
        ).clip(lower=0)

        data = data.tail(5).copy()

        if data.empty:
            return None

        labels = [
            str(year)
            for year in data["report_date"].dt.year
        ]

        equity = data["equity"] / 1e9
        borrowings = data["borrowings"] / 1e9
        other = data["other_liabilities"] / 1e9

        x = np.arange(len(data))

        fig, ax = plt.subplots(
            figsize=(7.0, 2.8)
        )

        ax.bar(
            x,
            equity,
            label="Equity",
        )

        ax.bar(
            x,
            borrowings,
            bottom=equity,
            label="Borrowings",
        )

        ax.bar(
            x,
            other,
            bottom=equity + borrowings,
            label="Other Liabilities",
        )

        ax.set_xticks(x)
        ax.set_xticklabels(
            labels,
            fontsize=7,
        )

        ax.set_ylabel(
            "₹ Billion",
            fontsize=8,
        )

        ax.set_title(
            "Balance Sheet Composition",
            fontsize=10,
        )

        ax.legend(
            fontsize=7,
            loc="upper left",
        )

        fig.tight_layout()

        path = (
            self.output_dir
            / f"{self.symbol}_balance_sheet.png"
        )

        fig.savefig(
            path,
            dpi=150,
            bbox_inches="tight",
        )

        plt.close(fig)

        return path

    # =====================================================
    # PAGE 2 - CASH FLOW WATERFALL
    # =====================================================

    def cashflow_waterfall(self):

        if self.cashflow.empty:
            return None

        latest = self.cashflow.iloc[-1]

        cfo = self.value_from_row(
            latest,
            ["operating_cash_flow"],
        )

        capex = self.value_from_row(
            latest,
            ["capital_expenditure"],
        )

        fcf = self.value_from_row(
            latest,
            ["free_cash_flow"],
        )

        if pd.isna(cfo):
            cfo = 0.0

        if pd.isna(capex):
            capex = 0.0

        if pd.isna(fcf):
            fcf = cfo + capex

        # The current cash_flow table does not contain
        # a CFF / financing_activity column.
        # Therefore we do not invent a CFF value.
        cff_available = "financing_activity" in latest.index

        if cff_available:

            cff = self.value_from_row(
                latest,
                [
                    "financing_activity",
                    "cash_from_financing",
                    "financing_cash_flow",
                ],
            )

            if pd.isna(cff):
                cff = 0.0

            final_fcf = cfo + capex + cff

        else:

            cff = np.nan
            final_fcf = fcf

        labels = [
            "CFO",
            "CapEx",
            "CFF",
            "Net Cash Flow",
        ]

        # Waterfall starts
        # CFO -> CapEx -> CFF -> Net Cash Flow.
        values = [
            cfo,
            capex,
            cff if pd.notna(cff) else 0.0,
            final_fcf,
        ]

        fig, ax = plt.subplots(
            figsize=(7.0, 2.8)
        )

        running = 0.0

        for index, value in enumerate(values):

            if index == len(values) - 1:

                ax.bar(
                    index,
                    value / 1e9,
                )

                continue

            value_b = value / 1e9

            if value_b >= 0:

                bottom = running

                ax.bar(
                    index,
                    value_b,
                    bottom=bottom,
                )

                running += value_b

            else:

                bottom = running + value_b

                ax.bar(
                    index,
                    abs(value_b),
                    bottom=bottom,
                )

                running += value_b

        ax.axhline(
            0,
            linewidth=0.8,
        )

        ax.set_xticks(
            range(len(labels))
        )

        ax.set_xticklabels(
            labels,
            fontsize=7,
        )

        ax.set_ylabel(
            "₹ Billion",
            fontsize=8,
        )

        title = (
            "Latest-Year Cash Flow Waterfall"
        )

        if not cff_available:

            title += " (CFF unavailable)"

        ax.set_title(
            title,
            fontsize=10,
        )

        fig.tight_layout()

        path = (
            self.output_dir
            / f"{self.symbol}_cashflow_waterfall.png"
        )

        fig.savefig(
            path,
            dpi=150,
            bbox_inches="tight",
        )

        plt.close(fig)

        return path

    # =====================================================
    # PROS / CONS
    # =====================================================

    def generate_pros_cons(self):

        row = self.latest_financial()

        pros = []
        cons = []

        roe = self.value_from_row(
            row,
            ["ROE"],
        )

        roce = self.value_from_row(
            row,
            ["ROCE"],
        )

        npm = self.value_from_row(
            row,
            ["NPM"],
        )

        de = self.value_from_row(
            row,
            ["D/E", "debt_equity"],
        )

        icr = self.value_from_row(
            row,
            ["ICR"],
        )

        fcf = self.value_from_row(
            row,
            [
                "Free Cash Flow",
                "free_cash_flow",
            ],
        )

        if pd.notna(roe) and roe > 20:
            pros.append(
                f"Strong ROE of {roe:.2f}%."
            )

        if pd.notna(roce) and roce > 15:
            pros.append(
                f"Healthy ROCE of {roce:.2f}%."
            )

        if pd.notna(npm) and npm > 15:
            pros.append(
                f"Strong net margin of {npm:.2f}%."
            )

        if pd.notna(de) and de < 0.5:
            pros.append(
                f"Moderate leverage with D/E of {de:.2f}."
            )

        if pd.notna(icr) and icr > 5:
            pros.append(
                f"Strong interest coverage of {icr:.2f}x."
            )

        if pd.notna(fcf) and fcf > 0:
            pros.append(
                "Positive free cash flow."
            )

        if pd.notna(roe) and roe < 10:
            cons.append(
                f"Low ROE of {roe:.2f}%."
            )

        if pd.notna(roce) and roce < 10:
            cons.append(
                f"Low ROCE of {roce:.2f}%."
            )

        if pd.notna(npm) and npm < 5:
            cons.append(
                f"Low net margin of {npm:.2f}%."
            )

        if pd.notna(de) and de > 2:
            cons.append(
                f"Elevated D/E of {de:.2f}."
            )

        if pd.notna(icr) and icr < 1.5:
            cons.append(
                f"Weak interest coverage of {icr:.2f}x."
            )

        if pd.notna(fcf) and fcf < 0:
            cons.append(
                "Negative free cash flow."
            )

        if not pros:
            pros.append(
                "No major positive signal identified."
            )

        if not cons:
            cons.append(
                "No major negative signal identified."
            )

        return pros, cons

    # =====================================================
    # CAPITAL ALLOCATION
    # =====================================================

    def capital_allocation_label(self):

        row = self.latest_financial()

        fcf = self.value_from_row(
            row,
            [
                "Free Cash Flow",
                "free_cash_flow",
            ],
        )

        ccr = self.value_from_row(
            row,
            [
                "Cash Conversion Ratio",
                "cash_conversion_ratio",
            ],
        )

        if (
            pd.notna(fcf)
            and fcf > 0
            and pd.notna(ccr)
            and ccr >= 0.5
        ):
            return "Reinvestor"

        if (
            pd.notna(fcf)
            and fcf < 0
        ):
            return "Distress Signal"

        return "Neutral"

    # =====================================================
    # HEADER / FOOTER
    # =====================================================

    def draw_header_footer(
        self,
        canvas,
        doc,
    ):

        canvas.saveState()

        width, height = A4

        canvas.setFillColor(
            colors.HexColor("#0B1F3A")
        )

        canvas.rect(
            0,
            height - 22 * mm,
            width,
            22 * mm,
            fill=1,
            stroke=0,
        )

        canvas.setFillColor(
            colors.white
        )

        company_name = self.company.get(
            "company_name",
            self.symbol,
        )

        canvas.setFont(
            "Helvetica-Bold",
            14,
        )

        canvas.drawString(
            15 * mm,
            height - 14 * mm,
            str(company_name),
        )

        canvas.setFont(
            "Helvetica",
            9,
        )

        canvas.drawRightString(
            width - 15 * mm,
            height - 14 * mm,
            self.symbol,
        )

        canvas.setFillColor(
            colors.grey
        )

        canvas.setFont(
            "Helvetica",
            7,
        )

        canvas.drawString(
            15 * mm,
            8 * mm,
            "N100 Financial Intelligence Platform",
        )

        canvas.drawRightString(
            width - 15 * mm,
            8 * mm,
            f"Page {doc.page}",
        )

        canvas.restoreState()

    # =====================================================
    # BUILD PDF
    # =====================================================

    def build(self):

        self.load_data()

        revenue_chart = (
            self.revenue_profit_chart()
        )

        roe_chart = (
            self.roe_roce_chart()
        )

        balance_chart = (
            self.balance_sheet_chart()
        )

        cashflow_chart = (
            self.cashflow_waterfall()
        )

        pros, cons = (
            self.generate_pros_cons()
        )

        capital_label = (
            self.capital_allocation_label()
        )

        company_name = self.company.get(
            "company_name",
            self.symbol,
        )

        industry = self.company.get(
            "industry",
            "N/A",
        )

        output_path = (
            self.output_dir
            / f"{self.symbol}_tearsheet.pdf"
        )

        doc = BaseDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=28 * mm,
            bottomMargin=15 * mm,
        )

        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height,
            id="main_frame",
        )

        doc.addPageTemplates(
            [
                PageTemplate(
                    id="Tearsheet",
                    frames=[frame],
                    onPage=self.draw_header_footer,
                )
            ]
        )

        story = []

        # =================================================
        # PAGE 1
        # =================================================

        story.append(
            Paragraph(
                f"<b>{company_name}</b>",
                self.styles_title(),
            )
        )

        story.append(
            Paragraph(
                f"Ticker: {self.symbol} &nbsp;&nbsp; "
                f"Sector: {industry}",
                self.body_style,
            )
        )

        story.append(
            Spacer(1, 4 * mm)
        )

        # -------------------------------------------------
        # KPI TILES
        # -------------------------------------------------

        kpis = self.get_kpis()

        kpi_cells = []

        for label, value in kpis:

            kpi_cells.append(
                Paragraph(
                    f"<b>{label}</b><br/>"
                    f"<font size='13'><b>{value}</b></font>",
                    self.kpi_style,
                )
            )

        kpi_table = Table(
            [
                kpi_cells[:3],
                kpi_cells[3:6],
            ],
            colWidths=[
                58 * mm,
                58 * mm,
                58 * mm,
            ],
            rowHeights=[
                17 * mm,
                17 * mm,
            ],
        )

        kpi_table.setStyle(
            TableStyle(
                [
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.lightgrey,
                    ),
                    (
                        "INNERGRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.lightgrey,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        5,
                    ),
                ]
            )
        )

        story.append(kpi_table)

        story.append(
            Spacer(1, 3 * mm)
        )

        # -------------------------------------------------
        # REVENUE / PROFIT
        # -------------------------------------------------

        if revenue_chart:

            story.append(
                Image(
                    str(revenue_chart),
                    width=170 * mm,
                    height=67 * mm,
                )
            )

        story.append(
            Spacer(1, 2 * mm)
        )

        # -------------------------------------------------
        # ROE / ROCE
        # -------------------------------------------------

        if roe_chart:

            story.append(
                Image(
                    str(roe_chart),
                    width=170 * mm,
                    height=67 * mm,
                )
            )

        # =================================================
        # PAGE 2
        # =================================================

        story.append(
            PageBreak()
        )

        story.append(
            Paragraph(
                "Balance Sheet Composition",
                self.section_style,
            )
        )

        if balance_chart:

            story.append(
                Image(
                    str(balance_chart),
                    width=170 * mm,
                    height=61 * mm,
                )
            )

        else:

            story.append(
                Paragraph(
                    "Balance Sheet data unavailable.",
                    self.body_style,
                )
            )

        story.append(
            Spacer(1, 2 * mm)
        )

        # -------------------------------------------------
        # CASH FLOW
        # -------------------------------------------------

        story.append(
            Paragraph(
                "Cash Flow Waterfall",
                self.section_style,
            )
        )

        if cashflow_chart:

            story.append(
                Image(
                    str(cashflow_chart),
                    width=170 * mm,
                    height=61 * mm,
                )
            )

        else:

            story.append(
                Paragraph(
                    "Cash Flow data unavailable.",
                    self.body_style,
                )
            )

        story.append(
            Spacer(1, 2 * mm)
        )

        # -------------------------------------------------
        # PROS / CONS
        # -------------------------------------------------

        pros_data = [
            [
                Paragraph(
                    "<b>Pros</b>",
                    self.body_style,
                ),
                Paragraph(
                    "<b>Cons</b>",
                    self.body_style,
                ),
            ]
        ]

        max_items = max(
            len(pros),
            len(cons),
        )

        for index in range(max_items):

            pro_text = (
                f"• {pros[index]}"
                if index < len(pros)
                else ""
            )

            con_text = (
                f"• {cons[index]}"
                if index < len(cons)
                else ""
            )

            pros_data.append(
                [
                    Paragraph(
                        pro_text,
                        self.small_style,
                    ),
                    Paragraph(
                        con_text,
                        self.small_style,
                    ),
                ]
            )

        pros_cons_table = Table(
            pros_data,
            colWidths=[
                85 * mm,
                85 * mm,
            ],
            repeatRows=1,
        )

        pros_cons_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.lightgrey,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP",
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (0, 0),
                        colors.HexColor("#EAF6EA"),
                    ),
                    (
                        "BACKGROUND",
                        (1, 0),
                        (1, 0),
                        colors.HexColor("#FBEAEA"),
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "RIGHTPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        4,
                    ),
                ]
            )
        )

        story.append(
            pros_cons_table
        )

        story.append(
            Spacer(1, 3 * mm)
        )

        # -------------------------------------------------
        # CAPITAL ALLOCATION
        # -------------------------------------------------

        allocation_table = Table(
            [
                [
                    Paragraph(
                        "<b>Capital Allocation Pattern</b>",
                        self.body_style,
                    ),
                    Paragraph(
                        f"<b>{capital_label}</b>",
                        self.body_style,
                    ),
                ]
            ],
            colWidths=[
                100 * mm,
                70 * mm,
            ],
        )

        allocation_table.setStyle(
            TableStyle(
                [
                    (
                        "BOX",
                        (0, 0),
                        (-1, -1),
                        0.8,
                        colors.HexColor("#0B1F3A"),
                    ),
                    (
                        "BACKGROUND",
                        (1, 0),
                        (1, 0),
                        colors.HexColor("#E8EEF5"),
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                    (
                        "LEFTPADDING",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6,
                    ),
                ]
            )
        )

        story.append(
            allocation_table
        )

        # =================================================
        # BUILD
        # =================================================

        doc.build(story)

        logging.info(
            "Tearsheet generated: %s",
            output_path,
        )

        return output_path

    # =====================================================
    # TITLE STYLE
    # =====================================================

    def styles_title(self):

        return ParagraphStyle(
            "TearsheetTitle",
            parent=getSampleStyleSheet()["Title"],
            fontSize=15,
            leading=17,
            spaceAfter=2,
        )