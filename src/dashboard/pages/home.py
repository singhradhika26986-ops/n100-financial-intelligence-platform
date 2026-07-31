import streamlit as st
import plotly.express as px

from utils.db import (
    get_companies,
    get_available_years,
    get_industries,
    get_home_kpis,
    get_sector_summary,
    get_top_companies,
)


def show():

    st.title("📈 N100 Financial Intelligence Platform")

    # -----------------------------
    # Load Data
    # -----------------------------

    companies = get_companies()
    industries = get_industries()
    years = get_available_years()

    kpis = get_home_kpis()
    sector_summary = get_sector_summary()
    top_companies = get_top_companies()

    # -----------------------------
    # Sidebar
    # -----------------------------

    st.sidebar.header("Dashboard Filters")

    selected_year = st.sidebar.selectbox(
        "Financial Years",
        years["years"].tolist() if not years.empty else ["N/A"],
    )

    st.sidebar.info(
        f"Selected Year : {selected_year}"
    )

    # -----------------------------
    # KPI Section
    # -----------------------------

    st.subheader("Dashboard Overview")

    total_companies = (
        int(kpis.iloc[0]["total_companies"])
        if not kpis.empty
        else 0
    )

    total_industries = (
        int(kpis.iloc[0]["total_industries"])
        if not kpis.empty
        else 0
    )

    total_years = (
        years["years"].nunique()
        if not years.empty
        else 0
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Companies",
            total_companies,
        )

    with col2:
        st.metric(
            "Industries",
            total_industries,
        )

    with col3:
        st.metric(
            "Financial Years",
            total_years,
        )

    st.divider()

    # -----------------------------
    # Charts Section
    # -----------------------------

    left, right = st.columns([1, 1])

    with left:

     st.subheader("Industry Distribution")

    if sector_summary.empty:

        st.info("No sector data available.")
    else:
        fig = px.pie(
            sector_summary,
            names="industry",
            values="company_count",
            hole=0.55,
            title="Companies by Industry",
        )

        fig.update_layout(
            height=450,
            showlegend=True,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


    with right:

     st.subheader("Top Companies")

     st.dataframe(
        top_companies,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # -----------------------------
    # Company Master Table
    # -----------------------------

    st.subheader("Nifty 100 Companies")

    search_text = st.text_input(
        "🔍 Search Company",
        placeholder="Type company name or ticker...",
    )

    filtered_companies = companies.copy()

    if search_text.strip():
        search = search_text.lower()

        filtered_companies = filtered_companies[
          filtered_companies["company_name"].str.lower().str.contains(
            search, na=False
        )
        |
        filtered_companies["symbol"].str.lower().str.contains(
            search, na=False
        )
    ]

    st.dataframe(
    filtered_companies,
    use_container_width=True,
    hide_index=True,
    )

    st.caption(
        f"Showing {len(filtered_companies)} of {len(companies)} companies"
    )

    st.divider()