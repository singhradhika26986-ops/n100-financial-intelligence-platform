import os
import logging
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class PeerComparisonReport:

    """
    Sprint 3
    Day 20
    Peer Comparison Report
    """

    def __init__(self, dataframe):

        self.df = dataframe.copy()

        self.output_folder = "reports/peer_reports"

        os.makedirs(
            self.output_folder,
            exist_ok=True
        )

        logging.info(
            "Peer Comparison Report Started"
        )

    # =====================================
    # Required Columns
    # =====================================

    def get_columns(self):

        columns = [

            "company_name",
            "symbol",
            "Sector",

            "ROE",
            "ROCE",
            "NPM",
            "D/E",

            "Revenue CAGR",
            "PAT CAGR",

            "Composite Score",

            "Peer Score",

            "Overall Rank",

            "Rating"

        ]

        return [

            column

            for column in columns

            if column in self.df.columns

        ]
    
        # =====================================
    # Generate Company Report
    # =====================================

    def generate_company_report(self, row):

        columns = self.get_columns()

        report = pd.DataFrame({

            "Metric": columns,

            "Value": [

                row.get(column, None)

                for column in columns

            ]

        })

        company_name = row.get(

            "company_name",

            row.get(

                "symbol",

                "Unknown"

            )

        )

        file_name = (

            company_name

            .replace(" ", "_")

            .replace("/", "_")

            + "_Peer_Report.xlsx"

        )

        output_path = os.path.join(

            self.output_folder,

            file_name

        )

        report.to_excel(

            output_path,

            index=False

        )

        logging.info(

            f"Report Saved : {file_name}"

        )

            # =====================================
    # Generate Reports for All Companies
    # =====================================

    def generate_all_reports(self):

        total = len(self.df)

        logging.info(
            f"Generating Reports for {total} companies..."
        )

        for _, row in self.df.iterrows():

            try:

                self.generate_company_report(row)

            except Exception as e:

                company_name = row.get(
                    "company_name",
                    row.get(
                        "symbol",
                        "Unknown"
                    )
                )

                logging.warning(
                    f"{company_name} : {e}"
                )

        logging.info(
            "All Peer Comparison Reports Generated Successfully"
        )

    # =====================================
    # MAIN RUN
    # =====================================

    def run(self):

        self.generate_all_reports()

        logging.info(
            "Peer Comparison Report Completed Successfully"
        )

        return self.df