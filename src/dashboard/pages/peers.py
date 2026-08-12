import pandas as pd
import streamlit as st
import plotly.express as px

from utils.db import get_screener_data


def show():
    """
    Peer Comparison Dashboard Page
    """

    st.title("🤝 Peer Comparison")

    st.caption(
        "Compare selected companies across profitability, "
        "growth, leverage and cash-flow metrics."
    )

    # =====================================================
    # LOAD DATA
    # =====================================================

    data = get_screener_data()

    if data.empty:
        st.warning("No company data available.")
        return

    # =====================================================
    # COMPANY SELECTION
    # =====================================================

    company_names = sorted(
        data["company_name"]
        .dropna()
        .unique()
        .tolist()
    )

    if len(company_names) < 2:
        st.warning(
            "At least two companies are required for peer comparison."
        )
        return

    default_companies = company_names[:2]

    selected = st.multiselect(
        "Select Companies",
        options=company_names,
        default=default_companies,
        max_selections=10,
    )

    if len(selected) < 2:
        st.info(
            "Please select at least two companies."
        )
        return

    comparison = data[
        data["company_name"].isin(selected)
    ].copy()

    if comparison.empty:
        st.warning(
            "No comparison data available for the selected companies."
        )
        return

    # =====================================================
    # KPI SECTION
    # =====================================================

    st.subheader("Comparison Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Selected Companies",
            len(selected),
        )

    with col2:
        st.metric(
            "Comparison Records",
            len(comparison),
        )

    with col3:
        industries = (
            comparison["industry"]
            .dropna()
            .nunique()
            if "industry" in comparison.columns
            else 0
        )

        st.metric(
            "Industries",
            industries,
        )

    st.divider()

    # =====================================================
    # COMPARISON TABLE
    # =====================================================

    st.subheader("📊 Comparison Table")

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
        "cash_conversion_ratio",
    ]

    available_columns = [
        column
        for column in display_columns
        if column in comparison.columns
    ]

    st.dataframe(
        comparison[available_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # =====================================================
    # HELPER FOR CHARTS
    # =====================================================

    def show_metric_chart(
        title,
        column,
        y_title,
    ):
        """
        Display a comparison bar chart if the metric exists.
        """

        if column not in comparison.columns:
            st.info(
                f"{column} data is not available."
            )
            return

        chart_data = comparison[
            ["company_name", column]
        ].copy()

        chart_data[column] = pd.to_numeric(
            chart_data[column],
            errors="coerce",
        )

        chart_data = chart_data.dropna(
            subset=[column]
        )

        if chart_data.empty:
            st.info(
                f"No valid {column} data available."
            )
            return

        fig = px.bar(
            chart_data,
            x="company_name",
            y=column,
            color="company_name",
            title=title,
            text_auto=".2f",
        )

        fig.update_layout(
            xaxis_title="Company",
            yaxis_title=y_title,
            showlegend=False,
            template="plotly_white",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # =====================================================
    # PROFITABILITY
    # =====================================================

    st.subheader("💰 Profitability Comparison")

    col1, col2 = st.columns(2)

    with col1:
        show_metric_chart(
            "Return on Equity (ROE)",
            "ROE",
            "ROE (%)",
        )

    with col2:
        show_metric_chart(
            "Return on Capital Employed (ROCE)",
            "ROCE",
            "ROCE (%)",
        )

    col1, col2 = st.columns(2)

    with col1:
        show_metric_chart(
            "Net Profit Margin (NPM)",
            "NPM",
            "NPM (%)",
        )

    with col2:
        show_metric_chart(
            "Operating Profit Margin (OPM)",
            "OPM",
            "OPM (%)",
        )

    st.divider()

    # =====================================================
    # GROWTH
    # =====================================================

    st.subheader("📈 Growth Comparison")

    col1, col2 = st.columns(2)

    with col1:
        show_metric_chart(
            "Revenue CAGR",
            "revenue_cagr",
            "Revenue CAGR (%)",
        )

    with col2:
        show_metric_chart(
            "PAT CAGR",
            "pat_cagr",
            "PAT CAGR (%)",
        )

    st.divider()

    # =====================================================
    # LEVERAGE
    # =====================================================

    st.subheader("🏦 Leverage Comparison")

    show_metric_chart(
        "Debt / Equity",
        "debt_equity",
        "Debt / Equity",
    )

    st.divider()

    # =====================================================
    # CASH FLOW
    # =====================================================

    st.subheader("💵 Cash Flow Comparison")

    col1, col2 = st.columns(2)

    with col1:
        show_metric_chart(
            "Free Cash Flow",
            "free_cash_flow",
            "Free Cash Flow",
        )

    with col2:
        show_metric_chart(
            "Cash Conversion Ratio",
            "cash_conversion_ratio",
            "Cash Conversion Ratio",
        )

    st.divider()

    # =====================================================
    # INTEREST COVERAGE
    # =====================================================

    st.subheader("🛡️ Interest Coverage")

    show_metric_chart(
        "Interest Coverage Ratio",
        "ICR",
        "ICR",
    )

    st.divider()

    # =====================================================
    # SIMPLE PEER SCORE
    # =====================================================

    st.subheader("⭐ Peer Snapshot")

    score_metrics = [
        "ROE",
        "ROCE",
        "NPM",
        "OPM",
        "revenue_cagr",
        "pat_cagr",
    ]

    available_score_metrics = [
        column
        for column in score_metrics
        if column in comparison.columns
    ]

    if available_score_metrics:

        score_data = comparison[
            ["company_name"]
            + available_score_metrics
        ].copy()

        for column in available_score_metrics:

            score_data[column] = pd.to_numeric(
                score_data[column],
                errors="coerce",
            )

        score_data["Peer Snapshot Score"] = (
            score_data[
                available_score_metrics
            ]
            .rank(
                pct=True,
            )
            .mean(axis=1)
            * 100
        ).round(2)

        score_data = score_data.sort_values(
            "Peer Snapshot Score",
            ascending=False,
        )

        st.dataframe(
            score_data[
                [
                    "company_name",
                    "Peer Snapshot Score",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.info(
            "Peer scoring metrics are not available."
        )