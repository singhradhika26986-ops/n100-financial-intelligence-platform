import logging
from pathlib import Path

import pandas as pd

from src.dashboard.utils.db import execute_query


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = BASE_DIR / "reports" / "portfolio"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_FILE = OUTPUT_DIR / "portfolio_summary.pdf"


class PortfolioSummary:

    def __init__(self):
        self.data = pd.DataFrame()

    # =====================================================
    # LOAD LATEST COMPANY DATA
    # =====================================================

    def load_data(self):

        query = """
        WITH latest AS (
            SELECT
                f.*,
                ROW_NUMBER() OVER (
                    PARTITION BY f.symbol
                    ORDER BY f.report_date DESC
                ) AS rn
            FROM financial_ratios f
        )

        SELECT
            c.company_name,
            c.symbol,
            c.industry,
            l.report_date,

            l.revenue,
            l.net_profit,

            l.ROE,
            l.ROCE,
            l.NPM,
            l.OPM,

            l."D/E" AS debt_equity,
            l.ICR,

            l."Revenue CAGR" AS revenue_cagr,
            l."PAT CAGR" AS pat_cagr,

            l."Free Cash Flow" AS free_cash_flow,
            l."Cash Conversion Ratio"
                AS cash_conversion_ratio

        FROM companies c

        INNER JOIN latest l
            ON c.symbol = l.symbol

        WHERE l.rn = 1

        ORDER BY c.company_name
        """

        self.data = execute_query(query)

        if self.data.empty:
            raise RuntimeError(
                "No portfolio data available."
            )

        numeric_columns = [
            "revenue",
            "net_profit",
            "ROE",
            "ROCE",
            "NPM",
            "OPM",
            "debt_equity",
            "ICR",
            "revenue_cagr",
            "pat_cagr",
            "free_cash_flow",
            "cash_conversion_ratio",
        ]

        for column in numeric_columns:

            if column in self.data.columns:

                self.data[column] = pd.to_numeric(
                    self.data[column],
                    errors="coerce",
                )

        logging.info(
            "Portfolio data loaded: %s companies",
            len(self.data),
        )

    # =====================================================
    # TREND ARROW
    # =====================================================

    @staticmethod
    def trend_arrow(value):

        if pd.isna(value):
            return "—"

        try:

            value = float(value)

        except Exception:

            return "—"

        if value > 0:
            return "↑"

        if value < 0:
            return "↓"

        return "→"

    # =====================================================
    # FORMAT
    # =====================================================

    @staticmethod
    def fmt(value, suffix=""):

        if pd.isna(value):
            return "N/A"

        try:
            return f"{float(value):.2f}{suffix}"

        except Exception:
            return str(value)

    # =====================================================
    # BUILD PDF
    # =====================================================

    def build(self):

        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import (
            ParagraphStyle,
            getSampleStyleSheet,
        )
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            BaseDocTemplate,
            Frame,
            PageBreak,
            PageTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
        )

        self.load_data()

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "PortfolioTitle",
            parent=styles["Title"],
            fontSize=22,
            leading=26,
            alignment=TA_CENTER,
            spaceAfter=8 * mm,
        )

        company_style = ParagraphStyle(
            "CompanyTitle",
            parent=styles["Heading1"],
            fontSize=17,
            leading=21,
            spaceAfter=3 * mm,
        )

        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=12,
            leading=15,
            spaceBefore=3 * mm,
            spaceAfter=3 * mm,
        )

        body_style = ParagraphStyle(
            "PortfolioBody",
            parent=styles["BodyText"],
            fontSize=9,
            leading=12,
        )

        doc = BaseDocTemplate(
            str(OUTPUT_FILE),
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
        )

        frame = Frame(
            doc.leftMargin,
            doc.bottomMargin,
            doc.width,
            doc.height,
            id="portfolio_frame",
        )

        doc.addPageTemplates(
            [
                PageTemplate(
                    id="Portfolio",
                    frames=[frame],
                )
            ]
        )

        story = []

        # =================================================
        # PORTFOLIO COVER
        # =================================================

        story.append(
            Spacer(1, 25 * mm)
        )

        story.append(
            Paragraph(
                "N100 Financial Intelligence Platform",
                title_style,
            )
        )

        story.append(
            Paragraph(
                "Portfolio Summary Report",
                company_style,
            )
        )

        story.append(
            Spacer(1, 5 * mm)
        )

        story.append(
            Paragraph(
                f"Companies covered: "
                f"{len(self.data)}",
                body_style,
            )
        )

        story.append(
            Spacer(1, 5 * mm)
        )

        story.append(
            Paragraph(
                "Latest available financial data "
                "across the portfolio.",
                body_style,
            )
        )

        story.append(
            PageBreak()
        )

        # =================================================
        # PORTFOLIO OVERVIEW
        # =================================================

        story.append(
            Paragraph(
                "Portfolio Overview",
                company_style,
            )
        )

        avg_roe = self.data["ROE"].mean()
        avg_roce = self.data["ROCE"].mean()
        avg_npm = self.data["NPM"].mean()
        avg_opm = self.data["OPM"].mean()
        avg_de = self.data["debt_equity"].mean()
        avg_icr = self.data["ICR"].mean()

        overview = [
            [
                "Companies",
                "Avg ROE",
                "Avg ROCE",
                "Avg NPM",
                "Avg OPM",
                "Avg D/E",
                "Avg ICR",
            ],
            [
                str(len(self.data)),
                self.fmt(avg_roe, "%"),
                self.fmt(avg_roce, "%"),
                self.fmt(avg_npm, "%"),
                self.fmt(avg_opm, "%"),
                self.fmt(avg_de),
                self.fmt(avg_icr),
            ],
        ]

        overview_table = Table(
            overview,
            colWidths=[
                25 * mm,
                25 * mm,
                25 * mm,
                25 * mm,
                25 * mm,
                25 * mm,
                25 * mm,
            ],
        )

        overview_table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey,
                    ),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#E8EEF5"),
                    ),
                    (
                        "ALIGN",
                        (0, 0),
                        (-1, -1),
                        "CENTER",
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        7,
                    ),
                ]
            )
        )

        story.append(
            overview_table
        )

        story.append(
            Spacer(1, 8 * mm)
        )

        story.append(
            Paragraph(
                "Company-wise Summary",
                company_style,
            )
        )

        # =================================================
        # ONE PAGE PER COMPANY
        # =================================================

        for index, row in self.data.iterrows():

            if index > 0:

                story.append(
                    PageBreak()
                )

            company_name = str(
                row.get(
                    "company_name",
                    "Unknown Company",
                )
            )

            symbol = str(
                row.get(
                    "symbol",
                    "",
                )
            )

            industry = str(
                row.get(
                    "industry",
                    "",
                )
            )

            report_date = str(
                row.get(
                    "report_date",
                    "",
                )
            )

            story.append(
                Paragraph(
                    company_name,
                    company_style,
                )
            )

            story.append(
                Paragraph(
                    f"<b>Symbol:</b> {symbol}"
                    f" &nbsp;&nbsp; "
                    f"<b>Sector:</b> {industry}"
                    f" &nbsp;&nbsp; "
                    f"<b>Report Date:</b> {report_date}",
                    body_style,
                )
            )

            story.append(
                Spacer(1, 5 * mm)
            )

            # -------------------------------------------------
            # SIX REQUIRED KPIs
            # -------------------------------------------------

            roe = row.get("ROE")
            roce = row.get("ROCE")
            npm = row.get("NPM")
            revenue_cagr = row.get("revenue_cagr")
            pat_cagr = row.get("pat_cagr")
            fcf = row.get("free_cash_flow")

            kpi_data = [
                [
                    "ROE",
                    "ROCE",
                    "NPM",
                ],
                [
                    f"{self.fmt(roe, '%')} "
                    f"{self.trend_arrow(roe)}",

                    f"{self.fmt(roce, '%')} "
                    f"{self.trend_arrow(roce)}",

                    f"{self.fmt(npm, '%')} "
                    f"{self.trend_arrow(npm)}",
                ],
                [
                    "Revenue CAGR",
                    "PAT CAGR",
                    "Free Cash Flow",
                ],
                [
                    f"{self.fmt(revenue_cagr, '%')} "
                    f"{self.trend_arrow(revenue_cagr)}",

                    f"{self.fmt(pat_cagr, '%')} "
                    f"{self.trend_arrow(pat_cagr)}",

                    f"{self.fmt(fcf)} "
                    f"{self.trend_arrow(fcf)}",
                ],
            ]

            kpi_table = Table(
                kpi_data,
                colWidths=[
                    58 * mm,
                    58 * mm,
                    58 * mm,
                ],
            )

            kpi_table.setStyle(
                TableStyle(
                    [
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.grey,
                        ),
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor(
                                "#E8EEF5"
                            ),
                        ),
                        (
                            "BACKGROUND",
                            (0, 2),
                            (-1, 2),
                            colors.HexColor(
                                "#E8EEF5"
                            ),
                        ),
                        (
                            "ALIGN",
                            (0, 0),
                            (-1, -1),
                            "CENTER",
                        ),
                        (
                            "FONTSIZE",
                            (0, 0),
                            (-1, -1),
                            9,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            7,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            7,
                        ),
                    ]
                )
            )

            story.append(
                kpi_table
            )

            story.append(
                Spacer(1, 8 * mm)
            )

            # -------------------------------------------------
            # ADDITIONAL FINANCIAL METRICS
            # -------------------------------------------------

            story.append(
                Paragraph(
                    "Additional Financial Metrics",
                    heading_style,
                )
            )

            additional = [
                [
                    "Metric",
                    "Value",
                ],
                [
                    "Operating Margin",
                    self.fmt(
                        row.get("OPM"),
                        "%",
                    ),
                ],
                [
                    "Debt / Equity",
                    self.fmt(
                        row.get("debt_equity")
                    ),
                ],
                [
                    "Interest Coverage",
                    self.fmt(
                        row.get("ICR")
                    ),
                ],
                [
                    "Cash Conversion",
                    self.fmt(
                        row.get(
                            "cash_conversion_ratio"
                        ),
                        "%",
                    ),
                ],
            ]

            additional_table = Table(
                additional,
                colWidths=[
                    80 * mm,
                    80 * mm,
                ],
            )

            additional_table.setStyle(
                TableStyle(
                    [
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.5,
                            colors.grey,
                        ),
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor(
                                "#E8EEF5"
                            ),
                        ),
                        (
                            "FONTSIZE",
                            (0, 0),
                            (-1, -1),
                            9,
                        ),
                    ]
                )
            )

            story.append(
                additional_table
            )

            story.append(
                Spacer(1, 8 * mm)
            )

            # -------------------------------------------------
            # INTERPRETATION
            # -------------------------------------------------

            story.append(
                Paragraph(
                    "Quick Interpretation",
                    heading_style,
                )
            )

            interpretation = []

            if pd.notna(roe):

                if float(roe) >= 15:

                    interpretation.append(
                        "ROE indicates relatively strong "
                        "shareholder return."
                    )

                elif float(roe) < 10:

                    interpretation.append(
                        "ROE is relatively low and "
                        "deserves monitoring."
                    )

            if pd.notna(roce):

                if float(roce) >= 15:

                    interpretation.append(
                        "ROCE indicates efficient use "
                        "of employed capital."
                    )

                elif float(roce) < 10:

                    interpretation.append(
                        "ROCE is relatively weak."
                    )

            if pd.notna(de := row.get("debt_equity")):

                if float(de) > 2:

                    interpretation.append(
                        "Debt/equity is elevated and "
                        "leverage should be monitored."
                    )

            if pd.notna(fcf):

                if float(fcf) < 0:

                    interpretation.append(
                        "Free cash flow is negative."
                    )

                else:

                    interpretation.append(
                        "Free cash flow is positive."
                    )

            if not interpretation:

                interpretation.append(
                    "Insufficient data for a detailed "
                    "automatic interpretation."
                )

            for text in interpretation:

                story.append(
                    Paragraph(
                        f"• {text}",
                        body_style,
                    )
                )

                story.append(
                    Spacer(1, 1.5 * mm)
                )

            story.append(
                Spacer(1, 8 * mm)
            )

            story.append(
                Paragraph(
                    "This summary is generated from "
                    "the latest available financial "
                    "record and is intended for "
                    "analytical use.",
                    body_style,
                )
            )

        doc.build(story)

        logging.info(
            "Portfolio summary generated: %s",
            OUTPUT_FILE,
        )

        return OUTPUT_FILE


if __name__ == "__main__":

    report = PortfolioSummary().build()

    print(
        f"PORTFOLIO PDF CREATED: {report}"
    )