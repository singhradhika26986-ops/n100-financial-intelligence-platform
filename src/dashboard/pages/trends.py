import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import (
    get_companies,
    get_financial_ratios,
)


def show():

    st.title("Trend Analysis")

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

    if ratios.empty:
        st.warning("No financial ratio data available.")
        return

    ratios = ratios.copy()
    ratios["report_date"] = pd.to_datetime(ratios["report_date"], errors="coerce")
    ratios = ratios.dropna(subset=["report_date"])

    metric_columns = [
        "ROE",
        "ROCE",
        "NPM",
        "OPM",
        "D/E",
        "ICR",
        "Revenue CAGR",
        "PAT CAGR",
        "Free Cash Flow",
        "OCF Margin",
        "Cash Conversion Ratio",
        "Dividend Payout",
        "Retention Ratio",
        "Reinvestment Ratio",
    ]

    available_metrics = [
        column for column in metric_columns if column in ratios.columns
    ]

    if not available_metrics:
        st.warning("No trend metrics available.")
        return

    selected_metric = st.selectbox(
        "Select Financial Metric",
        available_metrics,
    )

    trend_data = (
    ratios
    .sort_values("report_date")
    .dropna(subset=[selected_metric])
    )

    if trend_data.empty:
        st.warning("No data available for the selected metric.")
        return

    fig = px.line(
        trend_data,
        x="report_date",
        y=selected_metric,
        markers=True,
        title=f"{selected_metric} Trend",
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Report Date",
        yaxis_title=selected_metric,
        height=500,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()

    st.subheader("Trend Data")

    display_columns = [
        "report_date",
        "ROE",
        "ROCE",
        "NPM",
        "OPM",
        "D/E",
        "ICR",
        "Revenue CAGR",
        "PAT CAGR",
        "Free Cash Flow",
    ]

    available_columns = [
        col for col in display_columns
        if col in trend_data.columns
    ]

    st.dataframe(
        trend_data[available_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    values = trend_data[selected_metric].dropna()

    col1, col2, col3 = st.columns(3)

    if values.empty:

        with col1:
            st.metric("Latest", "N/A")

        with col2:
            st.metric("Highest", "N/A")

        with col3:
            st.metric("Lowest", "N/A")

    else:

        with col1:
            st.metric("Latest", f"{values.iloc[-1]:.2f}")

        with col2:
            st.metric("Highest", f"{values.max():.2f}")

        with col3:
            st.metric("Lowest", f"{values.min():.2f}")

    st.divider()