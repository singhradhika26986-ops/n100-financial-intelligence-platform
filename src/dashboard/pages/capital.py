import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import (
    get_companies,
    get_balance_sheet,
    get_cash_flow,
)


def show():

    st.title("💰 Capital Allocation")

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

    balance_sheet = get_balance_sheet(symbol)
    cash_flow = get_cash_flow(symbol)

    if balance_sheet.empty:
        st.warning("Balance sheet data not available.")
        return

    balance_sheet = balance_sheet.copy()

    if "report_date" in balance_sheet.columns:
        balance_sheet["report_date"] = pd.to_datetime(
            balance_sheet["report_date"],
            errors="coerce",
        )

        balance_sheet = balance_sheet.sort_values(
            "report_date"
        )

    latest = balance_sheet.iloc[-1]

    st.subheader("Capital Structure")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Assets",
            f"{latest['total_assets']:,.0f}",
        )

    with col2:
        st.metric(
            "Total Debt",
            f"{latest['total_debt']:,.0f}",
        )

    with col3:
        st.metric(
            "Shareholders Equity",
            f"{latest['shareholders_equity']:,.0f}",
        )

    with col4:
        st.metric(
            "Cash",
            f"{latest['cash']:,.0f}",
        )

    st.divider()

        # ---------------------------------
    # Balance Sheet Trend
    # ---------------------------------

    if "report_date" in balance_sheet.columns:

        st.subheader("Assets vs Debt")

        fig = px.line(
            balance_sheet,
            x="report_date",
            y=[
                "total_assets",
                "total_debt",
            ],
            markers=True,
            title="Assets vs Total Debt",
        )

        fig.update_layout(
            template="plotly_white",
            height=500,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    st.divider()

    # ---------------------------------
    # Balance Sheet Table
    # ---------------------------------

    st.subheader("Balance Sheet History")

    st.dataframe(
        balance_sheet,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # ---------------------------------
    # Cash Flow
    # ---------------------------------

    st.subheader("Cash Flow")

    if cash_flow.empty:

        st.info("Cash flow data not available.")

    else:

        cash_flow = cash_flow.copy()

        if "report_date" in cash_flow.columns:
            cash_flow["report_date"] = pd.to_datetime(
                cash_flow["report_date"],
                errors="coerce",
            )

            cash_flow = cash_flow.sort_values(
                "report_date"
            )

        st.dataframe(
            cash_flow,
            use_container_width=True,
            hide_index=True,
        )

        latest_cf = cash_flow.iloc[-1]

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Operating Cash Flow",
                f"{latest_cf['operating_cash_flow']:,.0f}",
            )

        with col2:
            st.metric(
                "Free Cash Flow",
                f"{latest_cf['free_cash_flow']:,.0f}",
            )

        if "report_date" in cash_flow.columns:

            fig = px.bar(
                cash_flow,
                x="report_date",
                y="free_cash_flow",
                title="Free Cash Flow Trend",
            )

            fig.update_layout(
                template="plotly_white",
                height=450,
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
            )

    st.divider()

    # ---------------------------------
    # Download CSV
    # ---------------------------------

    csv = balance_sheet.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Download Balance Sheet",
        data=csv,
        file_name="balance_sheet.csv",
        mime="text/csv",
    )

    st.divider()

    # ---------------------------------
    # Summary
    # ---------------------------------

    summary = {
        "Balance Sheet Records": len(balance_sheet),
        "Cash Flow Records": len(cash_flow),
        "Latest Report Date": str(
            latest["report_date"]
        ) if "report_date" in latest else "N/A",
    }

    st.subheader("Capital Allocation Summary")

    st.json(summary)