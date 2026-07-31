import streamlit as st
import plotly.express as px

from utils.db import get_screener_data


def show():

    st.title("🔎 Stock Screener")

    data = get_screener_data()

    if data.empty:
        st.warning("No company data available.")
        return

    # -----------------------------
    # Sidebar Filters
    # -----------------------------

    st.sidebar.header("Filters")

    industries = sorted(
        data["industry"].dropna().unique().tolist()
    )

    selected_industry = st.sidebar.selectbox(
        "Industry",
        ["All"] + industries,
    )

    min_roe = st.sidebar.slider(
        "Minimum ROE (%)",
        0.0,
        50.0,
        10.0,
        0.5,
    )

    min_roce = st.sidebar.slider(
        "Minimum ROCE (%)",
        0.0,
        50.0,
        10.0,
        0.5,
    )

    max_de = st.sidebar.slider(
        "Maximum Debt / Equity",
        0.0,
        5.0,
        2.0,
        0.1,
    )

    min_revenue_cagr = st.sidebar.slider(
        "Minimum Revenue CAGR (%)",
        -20.0,
        50.0,
        0.0,
        0.5,
    )

    search = st.text_input(
        "🔍 Search Company",
        placeholder="Enter company name...",
    )

    # -----------------------------
    # Filtering
    # -----------------------------

    filtered = data.copy()

    if selected_industry != "All":
        filtered = filtered[
            filtered["industry"] == selected_industry
        ]

    filtered = filtered[
        (filtered["ROE"] >= min_roe)
        & (filtered["ROCE"] >= min_roce)
        & (filtered["debt_equity"] <= max_de)
        & (filtered["revenue_cagr"] >= min_revenue_cagr)
    ]

    if search.strip():
        filtered = filtered[
            filtered["company_name"].str.contains(
                search,
                case=False,
                na=False,
            )
        ]

    # -----------------------------
    # KPIs
    # -----------------------------

    st.subheader("Screening Results")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Total Companies",
            len(data),
        )

    with col2:
        st.metric(
            "Matching Companies",
            len(filtered),
        )

    st.divider()

    # -----------------------------
    # Results Table
    # -----------------------------

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
        filtered[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    # -----------------------------
    # CSV Download
    # -----------------------------

    csv = filtered[display_columns].to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Download CSV",
        data=csv,
        file_name="stock_screener_results.csv",
        mime="text/csv",
    )

    st.divider()

    # -----------------------------
    # Industry Distribution
    # -----------------------------

    st.subheader("Industry Distribution")

    if not filtered.empty:

        industry_summary = (
            filtered.groupby("industry")
            .size()
            .reset_index(name="Companies")
            .sort_values(
                "Companies",
                ascending=False,
            )
        )

        fig = px.bar(
            industry_summary,
            x="industry",
            y="Companies",
            title="Companies by Industry",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:
        st.info(
            "No companies match the selected filters."
        )