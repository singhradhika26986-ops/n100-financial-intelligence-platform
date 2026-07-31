import streamlit as st
import plotly.express as px

from utils.db import (
    get_companies,
    get_company_profile,
    get_financial_ratios,
    get_balance_sheet,
    get_income_statement,
    get_cash_flow,
)


def show():

    st.title("🏢 Company Profile")

    companies = get_companies()

    if companies.empty:
        st.error("No company data found.")
        return

    company_options = (
        companies["company_name"] + " (" + companies["symbol"] + ")"
    ).tolist()

    selected = st.selectbox(
        "🔍 Search Company",
        company_options,
    )

    symbol = selected.split("(")[-1].replace(")", "").strip()

    company = get_company_profile(symbol)
    ratios = get_financial_ratios(symbol)
    balance_sheet = get_balance_sheet(symbol)
    income_statement = get_income_statement(symbol)
    cash_flow = get_cash_flow(symbol)

    if company.empty:
        st.warning("Ticker not found. Please try another.")
        return

    company = company.iloc[0]

    st.subheader("Company Information")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Company Name:** {company['company_name']}")
        st.write(f"**Symbol:** {company['symbol']}")
        st.write(f"**Industry:** {company['industry']}")

    with col2:
        st.write(f"**Series:** {company['series']}")
        st.write(f"**ISIN Code:** {company['isin_code']}")

    st.divider()

    # -----------------------------
    # KPI Cards
    # -----------------------------

    if ratios.empty:
        st.info("Financial ratio data not available.")
    else:

        latest = ratios.iloc[0]

        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

    with col1:
        st.metric(
            "ROE",
            f"{latest['ROE']:.2f}%"
        )

    with col2:
        st.metric(
            "ROCE",
            f"{latest['ROCE']:.2f}%"
        )

    with col3:
        st.metric(
            "Net Profit Margin",
            f"{latest['NPM']:.2f}%"
        )

    with col4:
        st.metric(
            "Debt / Equity",
            f"{latest['D/E']:.2f}"
        )

    with col5:
        st.metric(
            "Revenue CAGR",
            f"{latest['Revenue CAGR']:.2f}%"
        )

    with col6:
        st.metric(
            "Free Cash Flow",
            f"{latest['Free Cash Flow']:,.0f}"
        )

    st.divider()

    # -----------------------------
    # Charts
    # -----------------------------

    if not ratios.empty:

        chart_data = ratios.sort_values("years")

        st.subheader("Revenue vs Net Profit")

        revenue_chart = px.bar(
            chart_data,
            x="years",
            y=["revenue", "net_profit"],
            barmode="group",
            title="Revenue and Net Profit",
        )

        st.plotly_chart(
            revenue_chart,
            use_container_width=True,
        )

        st.divider()

        st.subheader("ROE vs ROCE Trend")

        roe_chart = px.line(
            chart_data,
            x="years",
            y=["ROE", "ROCE"],
            markers=True,
            title="ROE & ROCE",
        )

        st.plotly_chart(
            roe_chart,
            use_container_width=True,
        )

        st.divider()