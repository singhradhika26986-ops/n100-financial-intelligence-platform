# 📈 N100 Financial Intelligence Platform

A comprehensive financial analytics platform built using Python, SQLite, Pandas, and Yahoo Finance. The project collects historical market data, financial statements, and generates advanced financial ratios and KPIs for Nifty 100 companies.

---

## 🚀 Features

- Download Nifty 100 company details
- Download 5 years historical stock prices
- Store data in SQLite database
- Load Balance Sheet
- Load Income Statement
- Load Cash Flow Statement
- Financial Ratio Engine
- CAGR Analysis
- Cash Flow KPI Analysis
- Capital Allocation Analysis
- Clean ETL Pipeline
- Modular Project Structure

---

## 📂 Project Structure

```
N100_FINANCIAL_INTELLIGENCE_PLATFORM/
│
├── config/
├── data/
│   ├── raw/
│   └── processed/
├── reports/
├── output/
├── scripts/
├── sql/
├── src/
│   ├── analytics/
│   └── screener/
├── tests/
├── requirements.txt
├── schema.sql
└── README.md
```

---

## 🛠 Tech Stack

- Python
- Pandas
- NumPy
- SQLite
- yFinance
- Logging
- Git
- GitHub

---

## 📊 Database Tables

### Raw Tables

- companies
- stock_prices
- balance_sheet
- income_statement
- cash_flow

### Analytics Tables

- financial_ratios

---

## 📈 Financial Metrics

### Profitability

- ROE
- ROA
- ROCE
- Net Profit Margin
- Operating Profit Margin

### Leverage

- Debt to Equity
- Interest Coverage Ratio

### Efficiency

- Asset Turnover

### Growth

- Revenue CAGR
- PAT CAGR
- EPS CAGR

### Cash Flow KPIs

- Free Cash Flow
- OCF Margin
- Cash Conversion Ratio

### Capital Allocation

- Dividend Payout Ratio
- Retention Ratio
- Reinvestment Ratio

---

## ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/singhradhika26986-ops/n100-financial-intelligence-platform.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Run Project

Download Company Data

```bash
python scripts/data_ingestion.py
```

Download Stock Prices

```bash
python scripts/stock_price_loader.py
```

Load Financial Statements

```bash
python scripts/financial_data_loader.py
```

Generate Financial Ratios

```bash
python -m scripts.financial_ratio_loader
```

---

## 📌 Current Status

- ✔ Data Ingestion Completed
- ✔ Stock Price Loader Completed
- ✔ SQLite Database Completed
- ✔ Financial Statement Loader Completed
- ✔ Ratio Engine Completed
- ✔ CAGR Engine Completed
- ✔ Cash Flow KPI Engine Completed
- ✔ Capital Allocation Engine Completed

---

## 📊 Sample Output

- 100 Nifty Companies Loaded
- 119,346 Historical Stock Price Records
- 462 Financial Records Processed
- Financial Ratios Generated Successfully

---

## 👩‍💻 Author

**Rajni kumari**

GitHub:
https://github.com/singhradhika26986-ops

---

## 📄 License

This project is developed for educational and portfolio purposes.