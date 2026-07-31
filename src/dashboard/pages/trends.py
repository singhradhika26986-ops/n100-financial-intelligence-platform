import streamlit as st
import plotly.express as px

from utils.db import (
        get_companies,
    get_company_profile,
)


def show():

    st.title("Trend Analysis")

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

    profile = get_company_profile(
        company["company_id"]
    )

    if profile.empty:
        st.info("No financial data available.")
        return

    metric_columns = [
        "roe",
        "roa",
        "roce",
        "debt_to_equity",
        "interest_coverage",
        "asset_turnover",
        "revenue_cagr",
        "pat_cagr",
        "eps_cagr",
        "free_cash_flow",
        "ocf_margin",
        "cash_conversion_ratio",
        "dividend_payout",
        "retention_ratio",
        "reinvestment_ratio",
    ]

    available_metrics = [
        column
    for column in metric_columns
        if column in profile.columns
    ]

    selected_metric = st.selectbox(
        "Select Financial Metric",
        available_metrics
    )

    trend_data = profile.sort_values("year")

    fig = px.line(
        trend_data,
        x="year",
        y=selected_metric,
        markers=True,
        title=f"{selected_metric} Trend"
    )

    fig.update_layout(
        xaxis_title="Year",
        yaxis_title=selected_metric,
        template="plotly_white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    st.subheader("Trend Data")

    st.dataframe(
        trend_data,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("Summary")

    values = trend_data[selected_metric].dropna()

    col1, col2, col3 = st.columns(3)

    if values.empty:
        with col1:
            st.metric("Latest Value", "N/A")

        with col2:
            st.metric("Highest Value", "N/A")

        with col3:
            st.metric("Lowest Value", "N/A")
    else:
        latest_value = values.iloc[-1]
        highest_value = values.max()
        lowest_value = values.min()

        with col1:
            st.metric(
                "Latest Value",
                f"{latest_value:.2f}"
            )

        with col2:
            st.metric(
                "Highest Value",
                f"{highest_value:.2f}"
            )

        with col3:
            st.metric(
                "Lowest Value",
                f"{lowest_value:.2f}"
            )