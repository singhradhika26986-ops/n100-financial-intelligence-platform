import sqlite3
import pandas as pd
import yaml

from src.screener.engine import ScreenerEngine


DB_PATH = "nifty100.db"

conn = sqlite3.connect(DB_PATH)

print("Loading Financial Ratios...")

financial_df = pd.read_sql(
    "SELECT * FROM financial_ratios",
    conn
)

print(financial_df.shape)


with open(
    "config/screener_config.yaml",
    "r"
) as file:

    config = yaml.safe_load(file)


engine = ScreenerEngine(
    financial_df,
    config
)

print("\nRunning Screeners...\n")

quality = engine.get_quality_compounder()
value = engine.get_value_pick()
growth = engine.get_growth_accelerator()
dividend = engine.get_dividend_champion()
debtfree = engine.get_debt_free_bluechip()
turnaround = engine.get_turnaround_watch()


with pd.ExcelWriter(
    "output/screener_output.xlsx"
) as writer:

    quality.to_excel(
        writer,
        sheet_name="Quality Compounder",
        index=False
    )

    value.to_excel(
        writer,
        sheet_name="Value Pick",
        index=False
    )

    growth.to_excel(
        writer,
        sheet_name="Growth Accelerator",
        index=False
    )

    dividend.to_excel(
        writer,
        sheet_name="Dividend Champion",
        index=False
    )

    debtfree.to_excel(
        writer,
        sheet_name="Debt Free Bluechip",
        index=False
    )

    turnaround.to_excel(
        writer,
        sheet_name="Turnaround Watch",
        index=False
    )

print("\nAll Preset Screeners Generated Successfully")

print("\nCompanies Found")

print("Quality :", len(quality))
print("Value :", len(value))
print("Growth :", len(growth))
print("Dividend :", len(dividend))
print("Debt Free :", len(debtfree))
print("Turnaround :", len(turnaround))