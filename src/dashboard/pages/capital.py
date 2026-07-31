import streamlit as st

from utils.db import (    get_companies,
    get_balance_sheet,
    get_cash_flow,
)


def show():

    st.title("Capital Allocation")

    companies = get_companies()

    if companies.empty:
        st.warning("No company data available.")
        return

    company_name = st.selectbox(
        "Select Company",
        companies["company_name"]
    )

    company = companies[
        companies["company_name"] == company_name
    ].iloc[0]

    symbol = company["symbol"]

    balance_sheet = get_balance_sheet(symbol)
    cash_flow = get_cash_flow(symbol)

    if balance_sheet.empty:
        st.info("Balance sheet data is not available.")
        return

    latest_balance = balance_sheet.iloc[0]

    st.subheader("Capital Structure")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Assets",
            f"{latest_balance['total_assets']:,.2f}"
        )

    with col2:
        st.metric(
            "Total Debt",
            f"{latest_balance['total_debt']:,.2f}"
        )

    with col3:
        st.metric(
            "Shareholders' Equity",
            f"{latest_balance['shareholders_equity']:,.2f}"
        )

    with col4:
        st.metric(
            "Cash",
            f"{latest_balance['cash']:,.2f}"
        )

    st.divider()

    st.subheader("Balance Sheet History")

    st.dataframe(
        balance_sheet,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("Cash Flow")

    if cash_flow.empty:
        st.info("Cash flow data is not available.")
    else:
        st.dataframe(
            cash_flow,
            use_container_width=True,
            hide_index=True,
        )

        latest_cash_flow = cash_flow.iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Operating Cash Flow",
                f"{latest_cash_flow['operating_cash_flow']:,.2f}"
            )

        with col2:
            st.metric(
                "Free Cash Flow",
                f"{latest_cash_flow['free_cash_flow']:,.2f}"
            )

    st.divider()

    st.subheader("Capital Allocation Overview")

    summary = {
        "Balance Sheet Records": len(balance_sheet),
        "Cash Flow Records": len(cash_flow),
        "Latest Report Date": latest_balance["report_date"],
    }

    st.json(summary)