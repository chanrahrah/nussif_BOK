import streamlit as st
import pandas as pd
import numpy as np

def render_debt_stability_tab(cleaned_full_data):
    st.header("Debt & Financial Stability")

    df = build_debt_stability_df(cleaned_full_data)

    # =========================
    # SECTION 1: LEVELS
    # =========================
    st.subheader("Leverage Levels")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Household Debt (Monthly)**")
        st.line_chart(df["household_debt"])

        latest_hh = df["household_debt"].iloc[-1]
        hh_yoy = df["hh_debt_yoy"].iloc[-1]

        st.metric(
            label="Latest Household Debt",
            value=f"{latest_hh:,.0f}",
            delta=f"{hh_yoy:.2f}% YoY"
        )

    with col2:
        st.markdown("**Corporate Debt**")
        st.line_chart(df["corporate_debt"])

        latest_corp = df["corporate_debt"].iloc[-1]
        corp_yoy = df["corp_debt_yoy"].iloc[-1]

        st.metric(
            label="Latest Corporate Debt",
            value=f"{latest_corp:,.0f}",
            delta=f"{corp_yoy:.2f}% YoY"
        )

    # =========================
    # SECTION 2: DEBT TO GDP
    # =========================
    if "hh_debt_to_gdp" in df.columns:
        st.subheader("Debt Sustainability")

        st.line_chart(
            df[["hh_debt_to_gdp", "corp_debt_to_gdp"]]
        )

        st.caption("Debt-to-GDP ratios measure whether leverage is supported by income.")

    # =========================
    # SECTION 3: MOMENTUM & STRESS
    # =========================
    st.subheader("Momentum & Financial Stress")

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("**Debt Growth vs Income Growth**")
        st.line_chart(
            df[["hh_debt_yoy", "gdp_yoy"]]
        )

        spread = df["hh_debt_vs_income"].iloc[-1]
        st.metric(
            label="Debt – Income Growth Spread",
            value=f"{spread:.2f} pp"
        )

    with col4:
        st.markdown("**Household Debt Acceleration**")
        st.line_chart(df["hh_debt_accel"])
        st.caption("Positive acceleration = leverage risk building")

    # =========================
    # SECTION 4: POLICY INTERPRETATION
    # =========================
    st.subheader("Policy Interpretation")

    interpretation = generate_debt_policy_signal(df)

    st.info(interpretation)

def build_debt_stability_df(df):
    """
    Build debt & financial stability indicators from cleaned_full_data
    """

    df = df.copy()
    df.index = pd.to_datetime(df.index)

    col_map = {
        "household_debt": "Present Debt of Household",
        "corporate_debt": "Financial Corporations -   Domestic Currency",
        "gdp": "Gross domestic product at market prices(GDP)"
    }

    df_debt = pd.DataFrame(index=df.index)
    for key, col in col_map.items():
        if col in df.columns:
            df_debt[key] = df[col]

    # --- Growth rates (YoY) ---
    df_debt["hh_debt_yoy"] = df_debt["household_debt"].pct_change(12) * 100
    df_debt["corp_debt_yoy"] = df_debt["corporate_debt"].pct_change(12) * 100

    if "gdp" in df_debt.columns:
        df_debt["gdp_yoy"] = df_debt["gdp"].pct_change(12) * 100

        # Debt-to-GDP
        df_debt["hh_debt_to_gdp"] = df_debt["household_debt"] / df_debt["gdp"]
        df_debt["corp_debt_to_gdp"] = df_debt["corporate_debt"] / df_debt["gdp"]

        # Debt vs income pressure
        df_debt["hh_debt_vs_income"] = (
            df_debt["hh_debt_yoy"] - df_debt["gdp_yoy"]
        )

    # --- Acceleration (momentum change) ---
    df_debt["hh_debt_accel"] = (
        df_debt["hh_debt_yoy"] - df_debt["hh_debt_yoy"].shift(3)
    )

    df_debt["corp_debt_accel"] = (
        df_debt["corp_debt_yoy"] - df_debt["corp_debt_yoy"].shift(3)
    )

    return df_debt

def generate_debt_policy_signal(df):
    """
    Generate a macro-style interpretation based on debt indicators
    """

    hh_level = df["household_debt"].iloc[-1]
    hh_yoy = df["hh_debt_yoy"].iloc[-1]
    accel = df["hh_debt_accel"].iloc[-1]
    spread = df.get("hh_debt_vs_income", pd.Series([0])).iloc[-1]

    messages = []

    # Debt vs income
    if spread > 0:
        messages.append(
            "Household debt is rising faster than income, increasing balance-sheet stress."
        )
    else:
        messages.append(
            "Household debt growth remains broadly in line with income."
        )

    # Acceleration
    if accel > 0:
        messages.append(
            "Debt momentum is accelerating, suggesting rising financial vulnerability."
        )
    else:
        messages.append(
            "Debt momentum is slowing, reducing near-term financial stability risks."
        )

    # Policy constraint
    if spread > 0 and accel > 0:
        messages.append(
            "This constrains the Bank of Korea’s ability to cut rates aggressively, "
            "even if growth slows."
        )
    else:
        messages.append(
            "Debt dynamics allow the Bank of Korea greater flexibility in adjusting policy."
        )

    return " ".join(messages)

