import os
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


class RadarChartEngine:

    """
    Sprint 3
    Day 19
    Radar Chart Engine
    """

    def __init__(self, dataframe):

        self.df = dataframe.copy()

        self.output_folder = "reports/radar_charts"

        os.makedirs(
            self.output_folder,
            exist_ok=True
        )

        logging.info("Radar Chart Engine Started")

    # ======================================
    # Radar Metrics
    # ======================================

    def get_metrics(self):

        metrics = [

            "ROE",
            "ROCE",
            "NPM",
            "D/E",
            "Free Cash Flow",
            "PAT CAGR",
            "Revenue CAGR",
            "Composite Score"

        ]

        return [

            metric

            for metric in metrics

            if metric in self.df.columns

        ]
    
        # ======================================
    # Draw Radar Chart
    # ======================================

    def create_chart(self, row):

        metrics = self.get_metrics()

        if len(metrics) < 3:

            logging.warning(
                "Not enough metrics for radar chart."
            )

            return

        values = [

            row[metric]

            if pd.notna(row[metric])

            else 0

            for metric in metrics

        ]

        # Close the polygon

        values += values[:1]

        angles = np.linspace(
            0,
            2 * np.pi,
            len(metrics),
            endpoint=False
        ).tolist()

        angles += angles[:1]

        fig = plt.figure(figsize=(8, 8))

        ax = plt.subplot(
            111,
            polar=True
        )

        ax.plot(
            angles,
            values,
            linewidth=2
        )

        ax.fill(
            angles,
            values,
            alpha=0.25
        )

        ax.set_xticks(
            angles[:-1]
        )

        ax.set_xticklabels(
            metrics,
            fontsize=10
        )

        company_name = row.get(
            "company_name",
            row.get(
                "symbol",
                "Unknown"
            )
        )

        ax.set_title(
            company_name,
            fontsize=14,
            pad=20
        )

        file_name = (

            company_name

            .replace(" ", "_")

            .replace("/", "_")

            + "_radar.png"

        )

        plt.savefig(

            os.path.join(

                self.output_folder,

                file_name

            ),

            dpi=300,

            bbox_inches="tight"

        )

        plt.close()

        logging.info(
            f"Radar Chart Saved : {file_name}"
        )

            # ======================================
    # Generate Charts
    # ======================================

    def generate_all_charts(self):

        total = len(self.df)

        logging.info(
            f"Generating Radar Charts for {total} companies..."
        )

        for _, row in self.df.iterrows():

            try:

                self.create_chart(row)

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
            "All Radar Charts Generated Successfully"
        )

    # ======================================
    # MAIN RUN
    # ======================================

    def run(self):

        self.generate_all_charts()

        logging.info(
            "Radar Chart Engine Completed Successfully"
        )

        return self.df