import streamlit as st

from utils.db import (
    get_companies,
    get_financial_ratios,
    get_balance_sheet,
    get_income_statement,
    get_cash_flow,
)


def show():

    st.title("📑 Financial Reports")

    companies = get_companies()

    if companies.empty:
        st.warning("No company data available.")
        return

    company_options = (
        companies["company_name"] + " (" + companies["symbol"] + ")"
    ).tolist()

    selected = st.selectbox(
        "Select Company",
        company_options,
    )

    symbol = selected.split("(")[-1].replace(")", "").strip()

    ratios = get_financial_ratios(symbol)
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

    # ---------------------------------
    # Financial Ratios
    # ---------------------------------

    with tab1:

        if ratios.empty:
            st.info("Financial ratio data not available.")
        else:
            st.dataframe(
                ratios,
                use_container_width=True,
                hide_index=True,
            )

    # ---------------------------------
    # Balance Sheet
    # ---------------------------------

    with tab2:

        if balance_sheet.empty:
            st.info("Balance Sheet data not available.")
        else:
            st.dataframe(
                balance_sheet,
                use_container_width=True,
                hide_index=True,
            )

    # ---------------------------------
    # Income Statement
    # ---------------------------------

    with tab3:

        if income_statement.empty:
            st.info("Income Statement data not available.")
        else:
            st.dataframe(
                income_statement,
                use_container_width=True,
                hide_index=True,
            )

    # ---------------------------------
    # Cash Flow
    # ---------------------------------

    with tab4:

        if cash_flow.empty:
            st.info("Cash Flow data not available.")
        else:
            st.dataframe(
                cash_flow,
                use_container_width=True,
                hide_index=True,
            )

    st.divider()

    # ---------------------------------
    # Summary Metrics
    # ---------------------------------

    st.subheader("Report Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Financial Ratios",
            len(ratios),
        )

    with col2:
        st.metric(
            "Balance Sheet",
            len(balance_sheet),
        )

    with col3:
        st.metric(
            "Income Statement",
            len(income_statement),
        )

    with col4:
        st.metric(
            "Cash Flow",
            len(cash_flow),
        )

    st.divider()

    # ---------------------------------
    # Download Reports
    # ---------------------------------

    if not ratios.empty:

        csv = ratios.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "📥 Download Financial Ratios",
            data=csv,
            file_name=f"{symbol}_financial_ratios.csv",
            mime="text/csv",
        )

    # ---------------------------------
    # JSON Summary
    # ---------------------------------

    summary = {
        "Company Symbol": symbol,
        "Financial Ratio Records": len(ratios),
        "Balance Sheet Records": len(balance_sheet),
        "Income Statement Records": len(income_statement),
        "Cash Flow Records": len(cash_flow),
    }

    st.subheader("Summary")

    st.json(summary)