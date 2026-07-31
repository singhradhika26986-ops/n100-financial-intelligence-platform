import streamlit as st

from utils.db import (
        get_companies,
    get_company_profile,
    get_balance_sheet,
    get_income_statement,
    get_cash_flow,
)


def show():

    st.title("Financial Reports")

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

    company_id = company["company_id"]
    symbol = company["symbol"]

    profile = get_company_profile(company_id)
    balance_sheet = get_balance_sheet(symbol)
    income_statement = get_income_statement(symbol)
    cash_flow = get_cash_flow(symbol)

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Financial Ratios",
            "Balance Sheet",
            "Income Statement",
            "Cash Flow",
        ]
    )

    with tab1:
        if profile.empty:
            st.info("Financial ratio data is not available.")
        else:
            st.dataframe(
                profile,
                use_container_width=True,
                hide_index=True,
            )

    with tab2:
        if balance_sheet.empty:
            st.info("Balance sheet data is not available.")
        else:
            st.dataframe(
                balance_sheet,
                use_container_width=True,
                hide_index=True,
            )

    with tab3:
        if income_statement.empty:
            st.info("Income statement data is not available.")
        else:
            st.dataframe(
                income_statement,
                use_container_width=True,
                hide_index=True,
            )

    with tab4:
        if cash_flow.empty:
            st.info("Cash flow data is not available.")
        else:
            st.dataframe(
                cash_flow,
                use_container_width=True,
                hide_index=True,
            )

            st.divider()

    st.subheader("Report Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Financial Ratios",
            len(profile)
        )

    with col2:
        st.metric(
            "Balance Sheet",
            len(balance_sheet)
        )

    with col3:
        st.metric(
            "Income Statement",
            len(income_statement)
        )

    with col4:
        st.metric(
            "Cash Flow",
            len(cash_flow)
        )

    st.divider()

    summary = {
        "Company": company_name,
        "Symbol": symbol,
        "Financial Ratio Records": len(profile),
        "Balance Sheet Records": len(balance_sheet),
        "Income Statement Records": len(income_statement),
        "Cash Flow Records": len(cash_flow),
    }

    st.subheader("Summary")

    st.json(summary)