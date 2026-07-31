import streamlit as st

from utils.db import test_connection
from pages import (
    home,
    profile,
    screener,
    peers,
    trends,
    sectors,
    capital,
    reports,
)

st.set_page_config(
    page_title="N100 Financial Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded",
)

if not test_connection():
    st.error("Unable to connect to the database.")
    st.stop()

PAGES = {
    "Home": home,
    "Company Profile": profile,
    "Screener": screener,
    "Peer Comparison": peers,
    "Trend Analysis": trends,
    "Sector Analysis": sectors,
    "Capital Allocation": capital,
    "Financial Reports": reports,
}

st.sidebar.title("N100 Financial Intelligence Platform")

selected_page = st.sidebar.radio(
    "Navigation",
    list(PAGES.keys()),
)

PAGES[selected_page].show()