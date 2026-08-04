import streamlit as st
import plotly.express as px

from utils.db import get_companies


def show():

    st.title("🏭 Sector Analysis")

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

    if sector_summary.empty:
        st.warning("No sector data available.")
        return

    # ---------------------------------
    # Sector Distribution Chart
    # ---------------------------------

    st.subheader("Sector Distribution")

    fig = px.bar(
        sector_summary,
        x="industry",
        y="Company Count",
        text="Company Count",
        title="Companies by Industry",
    )

    fig.update_layout(
        template="plotly_white",
        xaxis_title="Industry",
        yaxis_title="Number of Companies",
        height=500,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()

    # ---------------------------------
    # Sector Summary Table
    # ---------------------------------

    st.subheader("Sector Summary")

    st.dataframe(
        sector_summary,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # ---------------------------------
    # KPI Cards
    # ---------------------------------

    total_sectors = len(sector_summary)

    largest_sector = sector_summary.iloc[0]

    smallest_sector = sector_summary.iloc[-1]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Sectors",
            total_sectors,
        )

    with col2:
        st.metric(
            "Largest Sector",
            largest_sector["industry"],
        )
        st.caption(
            f'{largest_sector["Company Count"]} companies'
        )

    with col3:
        st.metric(
            "Smallest Sector",
            smallest_sector["industry"],
        )
        st.caption(
            f'{smallest_sector["Company Count"]} companies'
        )

    st.divider()

    # ---------------------------------
    # Download CSV
    # ---------------------------------

    csv = sector_summary.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="📥 Download Sector Summary",
        data=csv,
        file_name="sector_summary.csv",
        mime="text/csv",
    )

    st.divider()

    # ---------------------------------
    # Top 10 Sectors
    # ---------------------------------

    st.subheader("Top 10 Sectors")

    st.dataframe(
        sector_summary.head(10),
        use_container_width=True,
        hide_index=True,
    )