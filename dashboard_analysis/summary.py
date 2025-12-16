import streamlit as st
import pandas as pd


def summary_tab(df):
    st.header("🇰🇷 Korea Macro Summary")

    COLS = {
        "rate": "base_rate",
        "cpi": "Total item",
        "gdp": "Gross domestic product at market prices(GDP)",
        "debt": "govt_debt_to_gdp"
    }

    # ---------------------------
    # 2. Guard against missing required columns
    # ---------------------------
    required_cols = [COLS["rate"], COLS["cpi"]]
    available_cols = set(df.columns)

    for col in required_cols:
        if col not in available_cols:
            st.error(f"Required macro indicator column '{col}' is missing from the DataFrame.")
            return # Stop execution if data is missing

    # ---------------------------
    # 3. Compute latest values and changes directly from the main df
    # ---------------------------

    # Policy Rate Calculations
    rate_series = df[COLS["rate"]].dropna()
    rate_now = rate_series.iloc[-1]
    rate_prev = rate_series.iloc[-2]
    rate_change = rate_now - rate_prev

    # CPI Calculations
    cpi_series = df[COLS["cpi"]].dropna()
    cpi_now = cpi_series.iloc[-1]
    cpi_prev = cpi_series.iloc[-2]
    cpi_change = cpi_now - cpi_prev


    # GDP Calculations (guard against missing optional columns if necessary, otherwise assume they exist)
    if COLS["gdp"] in df.columns:
        gdp_series = df[COLS["gdp"]].dropna()
        gdp_now = gdp_series.iloc[-1]
        gdp_prev_quarter = gdp_series.iloc[-4] # Assumes quarterly data aligned with index frequency
        gdp_change_quarterly = (gdp_now - gdp_prev_quarter) / gdp_prev_quarter * 100
    else:
        gdp_now, gdp_change_quarterly = None, None # Handle gracefully in your display logic

    # Debt Calculations
    if COLS["debt"] in df.columns:
        debt_series = df[COLS["debt"]].dropna()
        debt_now = debt_series.iloc[-1]
        debt_prev_quarter = debt_series.iloc[-4]
        debt_change_quarterly = (debt_now - debt_prev_quarter) / debt_prev_quarter * 100
    else:
        debt_now, debt_change_quarterly = None, None

    # Get the current date from the index of the rate series
    curr_date = rate_series.index[-1].strftime("%B %Y")
    
    # ---------------------------
    # 4. KPI row
    # ---------------------------
    st.markdown(f"#### 📅 As of {curr_date}")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "BOK Base Rate (%)",
        f"{rate_now:.2f}",
        f"{rate_change:+.2f} MoM"
    )

    col2.metric(
        "CPI Inflation (YoY %)",
        f"{cpi_now:.2f}",
        f"{cpi_change:+.2f} MoM"
    )

    col3.metric(
        "GDP",
        f"{gdp_now:.2f}",
        f"{gdp_change_quarterly:+.2f} QoQ"
        )

    col4.metric(
        "Govt Debt / GDP (%)",
        f"{debt_now:.1f}",
        f"{debt_change_quarterly:+.1f} QoQ"
    )

    st.divider()

    # ---------------------------
    # 5. Macro regime logic
    # ---------------------------
    real_rate = rate_now - cpi_now

    if real_rate > 0:
        stance = "Restrictive"
    elif real_rate < 0:
        stance = "Accommodative"
    else:
        stance = "Neutral"

    inflation_trend = "Cooling" if cpi_change < 0 else "Re-accelerating"

    # ---------------------------
    # 6. Narrative summary
    # ---------------------------
    st.subheader("📌 Key Takeaways")

    st.markdown(
        f"""
        - **Real Policy Rate:** {real_rate:.2f}%  
        - **Monetary Policy Stance:** {stance}  
        - **Inflation Trend:** {inflation_trend}
        """
    )

    st.info(
        f"""
        Korea’s monetary environment remains **{stance.lower()}**, with
        the base policy rate exceeding inflation by **{real_rate:.2f}%**.
        Inflation dynamics suggest **{inflation_trend.lower()} pressures**,
        implying a cautious policy path ahead.
        """
    )


