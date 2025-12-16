import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

from summary import summary_tab
from monetary_policy import monetary_policy_tab
from fiscal_n_debt import render_debt_stability_tab
# ----------------------------------
# Page configuration
# ----------------------------------
st.set_page_config(
    page_title="South Korea Macroeconomic Dashboard",
    layout="wide"
)

st.title("🇰🇷 South Korea Macroeconomic Dashboard (2018–2025)")
st.caption("Macro transmission–based analysis")

# ----------------------------------
# Load data
# ----------------------------------
@st.cache_data
def load_data():
    file_path = os.path.join('data', 'cleaned_full_data.csv') # Uncomment for streamlit cloud deployment
    # file_path = "../data/cleaned_full_data.csv"  # Uncomment for Local relative path for development
    if not os.path.exists(file_path):
        st.error(f"Error: Dataset not found at path: {file_path}")
        st.stop() # Stops the script execution gracefully
    df = pd.read_csv(
        file_path,
        parse_dates=["date"]    
    )
    df = df.set_index("date").sort_index()
    return df

df = load_data()

# ----------------------------------
# Tabs (Macro Transmission Channels)
# ----------------------------------
tabs = st.tabs([
    "Summary",
    "🟦 Monetary & Inflation",
    "🟩 Fiscal & Debt",
    "🟨 Growth Cycle",
    "🟥 Asset Markets",
    "🟪 External Sector"
])

# ==================================
# Tab 0: Summary
# ==================================
with tabs[0]:
    summary_tab(df)
    
# ==================================
# 🟦 Tab 1: Monetary & Inflation
# ==================================
with tabs[1]:
    monetary_policy_tab(df)

# ==================================
# 🟩 Tab 2: Fiscal & Government Debt
# ==================================
with tabs[2]:
    render_debt_stability_tab(df)   


