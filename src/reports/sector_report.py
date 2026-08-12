import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.dashboard.utils.db import execute_query


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


BASE_DIR = Path(__file__).resolve().parents[2]

OUTPUT_DIR = (
    BASE_DIR
    / "reports"
    / "sectors"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


class SectorReport:

    def __init__(self, sector):

        self.sector = sector

        self.data = pd.DataFrame()

        logging.info(
            "Sector report initialized: %s",
            sector,
        )

    # =====================================================
    # LOAD DATA
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

            INNER JOIN companies c
                ON c.symbol = f.symbol

            WHERE c.industry = ?
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
            l."Free Cash Flow" AS free_cash_flow

        FROM companies c

        INNER JOIN latest l
            ON c.symbol = l.symbol

        WHERE l.rn = 1
          AND c.industry = ?

        ORDER BY l.ROE DESC
        """

        self.data = execute_query(
            query,
            (
                self.sector,
                self.sector,
            ),
        )

        if self.data.empty:
            raise ValueError(
                f"No data found for sector: {self.sector}"
            )

        logging.info(
            "Loaded %s companies for %s",
            len(self.data),
            self.sector,
        )

    # =====================================================
    # CLEAN NUMERIC DATA
    # =====================================================

    def clean_data(self):

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
        ]

        for column in numeric_columns:

            if column in self.data.columns:

                self.data[column] = pd.to_numeric(
                    self.data[column],
                    errors="coerce",
                )

    # =====================================================
    # TOP COMPANIES
    # =====================================================

    def top_companies(self):

        columns = [
            "company_name",
            "symbol",
            "ROE",
            "ROCE",
            "NPM",
            "OPM",
            "debt_equity",
            "ICR",
            "revenue_cagr",
            "pat_cagr",
            "free_cash_flow",
        ]

        available = [
            column
            for column in columns
            if column in self.data.columns
        ]

        result = (
            self.data[available]
            .sort_values(
                "ROE",
                ascending=False,
                na_position="last",
            )
            .head(10)
        )

        return result

    # =====================================================
    # ROE CHART
    # =====================================================

    def roe_chart(self):

        data = (
            self.data
            .sort_values(
                "ROE",
                ascending=False,
                na_position="last",
            )
            .head(10)
            .dropna(
                subset=["ROE"]
            )
        )

        if data.empty:
            return None

        fig, ax = plt.subplots(
            figsize=(8, 4)
        )

        ax.barh(
            data["company_name"],
            data["ROE"],
        )

        ax.invert_yaxis()

        ax.set_xlabel(
            "ROE (%)"
        )

        ax.set_title(
            f"{self.sector} - ROE Comparison"
        )

        fig.tight_layout()

        path = (
            OUTPUT_DIR
            / (
                self.safe_filename()
                + "_roe.png"
            )
        )

        fig.savefig(
            path,
            dpi=150,
            bbox_inches="tight",
        )

        plt.close(fig)

        return path

    # =====================================================
    # ROCE CHART
    # =====================================================

    def roce_chart(self):

        data = (
            self.data
            .sort_values(
                "ROCE",
                ascending=False,
                na_position="last",
            )
            .head(10)
            .dropna(
                subset=["ROCE"]
            )
        )

        if data.empty:
            return None

        fig, ax = plt.subplots(
            figsize=(8, 4)
        )

        ax.barh(
            data["company_name"],
            data["ROCE"],
        )

        ax.invert_yaxis()

        ax.set_xlabel(
            "ROCE (%)"
        )

        ax.set_title(
            f"{self.sector} - ROCE Comparison"
        )

        fig.tight_layout()

        path = (
            OUTPUT_DIR
            / (
                self.safe_filename()
                + "_roce.png"
            )
        )

        fig.savefig(
            path,
            dpi=150,
            bbox_inches="tight",
        )

        plt.close(fig)

        return path

    # =====================================================
    # SAFE FILE NAME
    # =====================================================

    def safe_filename(self):

        value = str(
            self.sector
        ).strip()

        for char in [
            "/",
            "\\",
            ":",
            "*",
            "?",
            '"',
            "<",
            ">",
            "|",
        ]:

            value = value.replace(
                char,
                "_",
            )

        return value.replace(
            " ",
            "_",
        )

    # =====================================================
    # BUILD PDF
    # =====================================================

    def build(self):

        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import (
            getSampleStyleSheet,
        )
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            BaseDocTemplate,
            Frame,
            Image,
            PageBreak,
            PageTemplate,
            Paragraph,
            Spacer,
            Table,
            TableStyle,
        )

        self.load_data()

        self.clean_data()

        roe_chart = self.roe_chart()

        roce_chart = self.roce_chart()

        filename = (
            self.safe_filename()
            + "_sector_report.pdf"
        )

        output_path = (
            OUTPUT_DIR
            / filename
        )

        styles = getSampleStyleSheet()

        title_style = styles["Title"]

        heading_style = styles["Heading2"]

        body_style = styles["BodyText"]

        doc = BaseDocTemplate(
            str(output_path),
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
            id="sector_frame",
        )

        doc.addPageTemplates(
            [
                PageTemplate(
                    id="Sector",
                    frames=[frame],
                )
            ]
        )

        story = []

        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        story.append(
            Paragraph(
                f"{self.sector} — Sector Report",
                title_style,
            )
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

        # -------------------------------------------------
        # KPI SUMMARY
        # -------------------------------------------------

        avg_roe = self.data["ROE"].mean()

        avg_roce = self.data["ROCE"].mean()

        avg_npm = self.data["NPM"].mean()

        avg_opm = self.data["OPM"].mean()

        summary = [
            [
                "Companies",
                "Avg ROE",
                "Avg ROCE",
                "Avg NPM",
                "Avg OPM",
            ],
            [
                str(len(self.data)),
                (
                    f"{avg_roe:.2f}%"
                    if pd.notna(avg_roe)
                    else "N/A"
                ),
                (
                    f"{avg_roce:.2f}%"
                    if pd.notna(avg_roce)
                    else "N/A"
                ),
                (
                    f"{avg_npm:.2f}%"
                    if pd.notna(avg_npm)
                    else "N/A"
                ),
                (
                    f"{avg_opm:.2f}%"
                    if pd.notna(avg_opm)
                    else "N/A"
                ),
            ],
        ]

        summary_table = Table(
            summary,
            colWidths=[
                30 * mm,
                30 * mm,
                30 * mm,
                30 * mm,
                30 * mm,
            ],
        )

        summary_table.setStyle(
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
                        "ALIGN",
                        (0, 0),
                        (-1, -1),
                        "CENTER",
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                ]
            )
        )

        story.append(
            summary_table
        )

        story.append(
            Spacer(1, 5 * mm)
        )

        # -------------------------------------------------
        # CHARTS
        # -------------------------------------------------

        if roe_chart:

            story.append(
                Image(
                    str(roe_chart),
                    width=175 * mm,
                    height=75 * mm,
                )
            )

        story.append(
            Spacer(1, 2 * mm)
        )

        if roce_chart:

            story.append(
                Image(
                    str(roce_chart),
                    width=175 * mm,
                    height=75 * mm,
                )
            )

        story.append(
            PageBreak()
        )

        # -------------------------------------------------
        # TOP COMPANIES TABLE
        # -------------------------------------------------

        story.append(
            Paragraph(
                "Top Companies",
                heading_style,
            )
        )

        top = self.top_companies()

        table_data = [
            [
                "Company",
                "Symbol",
                "ROE",
                "ROCE",
                "NPM",
                "D/E",
            ]
        ]

        for _, row in top.iterrows():

            table_data.append(
                [
                    str(
                        row.get(
                            "company_name",
                            "",
                        )
                    ),
                    str(
                        row.get(
                            "symbol",
                            "",
                        )
                    ),
                    self.format_value(
                        row.get("ROE")
                    ),
                    self.format_value(
                        row.get("ROCE")
                    ),
                    self.format_value(
                        row.get("NPM")
                    ),
                    self.format_value(
                        row.get("debt_equity")
                    ),
                ]
            )

        table = Table(
            table_data,
            repeatRows=1,
            colWidths=[
                65 * mm,
                28 * mm,
                20 * mm,
                20 * mm,
                20 * mm,
                20 * mm,
            ],
        )

        table.setStyle(
            TableStyle(
                [
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
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
                        7,
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE",
                    ),
                ]
            )
        )

        story.append(table)

        story.append(
            Spacer(1, 5 * mm)
        )

        # -------------------------------------------------
        # SECTOR INSIGHTS
        # -------------------------------------------------

        story.append(
            Paragraph(
                "Sector Insights",
                heading_style,
            )
        )

        insights = []

        if pd.notna(avg_roe):

            insights.append(
                f"Average sector ROE is "
                f"{avg_roe:.2f}%."
            )

        if pd.notna(avg_roce):

            insights.append(
                f"Average sector ROCE is "
                f"{avg_roce:.2f}%."
            )

        if pd.notna(avg_npm):

            insights.append(
                f"Average net profit margin is "
                f"{avg_npm:.2f}%."
            )

        if pd.notna(avg_opm):

            insights.append(
                f"Average operating margin is "
                f"{avg_opm:.2f}%."
            )

        for insight in insights:

            story.append(
                Paragraph(
                    f"• {insight}",
                    body_style,
                )
            )

            story.append(
                Spacer(1, 1 * mm)
            )

        story.append(
            Spacer(1, 4 * mm)
        )

        story.append(
            Paragraph(
                "This report is generated from the "
                "latest available financial record "
                "for each company in the sector.",
                body_style,
            )
        )

        doc.build(story)

        logging.info(
            "Sector report generated: %s",
            output_path,
        )

        return output_path

    # =====================================================
    # FORMAT VALUE
    # =====================================================

    @staticmethod
    def format_value(value):

        if pd.isna(value):
            return "N/A"

        try:
            return f"{float(value):.2f}"

        except Exception:
            return str(value)


# =========================================================
# BATCH SECTOR REPORT GENERATION
# =========================================================

def get_sectors():

    query = """
    SELECT DISTINCT
        industry
    FROM companies
    WHERE industry IS NOT NULL
      AND TRIM(industry) != ''
    ORDER BY industry
    """

    df = execute_query(query)

    return df["industry"].tolist()


def generate_all_sector_reports():

    sectors = get_sectors()

    print(
        f"SECTORS FOUND: {len(sectors)}"
    )

    generated = []

    for sector in sectors:

        try:

            report = SectorReport(
                sector
            ).build()

            generated.append(
                {
                    "sector": sector,
                    "path": str(report),
                }
            )

        except Exception as exc:

            logging.exception(
                "Failed sector: %s",
                sector,
            )

            print(
                f"FAILED: {sector} -> {exc}"
            )

    print()
    print("=" * 60)
    print("SECTOR REPORT SUMMARY")
    print("=" * 60)
    print(
        f"Sectors found     : {len(sectors)}"
    )
    print(
        f"Reports generated : {len(generated)}"
    )
    print(
        f"Output directory  : {OUTPUT_DIR}"
    )
    print("=" * 60)

    return generated


if __name__ == "__main__":

    generate_all_sector_reports()