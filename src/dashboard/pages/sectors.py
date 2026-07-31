import streamlit as st
import plotly.express as px

from utils.db import get_companies


def show():

    st.title("Sector Analysis")

    companies = get_companies()

    if companies.empty:
        st.warning("No company data available.")
        return

    sector_summary = (
        companies.groupby("industry")
        .size()
        .reset_index(name="Company Count")
        .sort_values("Company Count", ascending=False)
    )

    st.subheader("Sector Distribution")

    fig = px.bar(
        sector_summary,
        x="industry",
        y="Company Count",
        title="Companies by Industry",
        text="Company Count",
    )

    fig.update_layout(
        xaxis_title="Industry",
        yaxis_title="Number of Companies",
        template="plotly_white",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()

    st.subheader("Sector Summary")

    st.dataframe(
        sector_summary,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("Sector Statistics")

    col1, col2, col3 = st.columns(3)

    total_sectors = len(sector_summary)

    largest_sector = sector_summary.iloc[0]

    smallest_sector = sector_summary.iloc[-1]

    with col1:
        st.metric(
            "Total Sectors",
            total_sectors
        )

    with col2:
        st.metric(
            "Largest Sector",
            largest_sector["industry"]
        )

        st.caption(
            f'{largest_sector["Company Count"]} companies'
        )

    with col3:
        st.metric(
            "Smallest Sector",
            smallest_sector["industry"]
        )

        st.caption(
            f'{smallest_sector["Company Count"]} companies'
        )

    st.divider()

    st.subheader("Top 10 Sectors")

    st.dataframe(
        sector_summary.head(10),
        use_container_width=True,
        hide_index=True,
    )