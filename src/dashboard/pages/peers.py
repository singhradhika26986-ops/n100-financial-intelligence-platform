import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import get_screener_data


def show():
    st.success("PEERS PAGE LOADED")

    st.title("🤝 Peer Comparison")

    data = get_screener_data()

    if data.empty:
        st.warning("No company data available.")
        return

    company_names = sorted(data["company_name"].unique().tolist())

    selected = st.multiselect(
        "Select Companies",
        company_names,
        default=company_names[:2],
    )

    if len(selected) < 2:
        st.info("Please select at least two companies.")
        return

    comparison = data[
        data["company_name"].isin(selected)
    ].copy()

    st.subheader("Comparison Table")

    display_columns = [
        "company_name",
        "symbol",
        "industry",
        "ROE",
        "ROCE",
        "NPM",
        "OPM",
        "debt_equity",
        "ICR",
        "revenue_cagr",
        "pat_cagr",
        "free_cash_flow",
    ]

    st.dataframe(
        comparison[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Selected Companies",
            len(selected),
        )

    with col2:
        st.metric(
            "Records",
            len(comparison),
        )

    st.divider()

    st.subheader("ROE Comparison")

    fig = px.bar(
        comparison,
        x="company_name",
        y="ROE",
        color="company_name",
        title="ROE Comparison",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()

    st.subheader("ROCE Comparison")

    fig = px.bar(
        comparison,
        x="company_name",
        y="ROCE",
        color="company_name",
        title="ROCE Comparison",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()

    st.subheader("Revenue CAGR Comparison")

    fig = px.bar(
        comparison,
        x="company_name",
        y="revenue_cagr",
        color="company_name",
        title="Revenue CAGR",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()

    st.subheader("PAT CAGR Comparison")

    fig = px.bar(
        comparison,
        x="company_name",
        y="pat_cagr",
        color="company_name",
        title="PAT CAGR",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()

    st.subheader("Free Cash Flow Comparison")

    fig = px.bar(
        comparison,
        x="company_name",
        y="free_cash_flow",
        color="company_name",
        title="Free Cash Flow",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )