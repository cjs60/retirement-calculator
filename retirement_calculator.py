import streamlit as st
import pandas as pd

def calculate_annual_savings(future_value, annual_rate, years):
    if annual_rate == 0:
        return future_value / years
    r = annual_rate
    n = years
    pmt = (future_value * r) / ((1 + r) ** n - 1)
    return pmt

def project_growth(pmt, annual_rate, years):
    balance = 0
    growth = []
    for year in range(1, years + 1):
        balance = balance * (1 + annual_rate) + pmt
        growth.append((year, balance))
    return pd.DataFrame(growth, columns=["Year", "Balance"])

st.title("💰 Retirement Savings Calculator")

st.markdown("""
This calculator helps you estimate how much to save each year to reach your retirement goal.
""")

# Inputs
target = st.number_input("Target Retirement Amount ($)", min_value=10000.0, value=1000000.0, step=10000.0, format="%.2f")
years = st.number_input("Years Until Retirement", min_value=1, value=30)
rate_percent = st.slider("Expected Annual Return (%)", 0.0, 15.0, 7.0)
annual_rate = rate_percent / 100

# Inflation
adjust_for_inflation = st.checkbox("Adjust for Inflation")
if adjust_for_inflation:
    inflation_percent = st.slider("Expected Inflation Rate (%)", 0.0, 10.0, 2.5)
    inflation_rate = inflation_percent / 100
    adjusted_target = target / ((1 + inflation_rate) ** years)
    st.markdown(f"🎯 Inflation-adjusted target: **${adjusted_target:,.2f}**")
else:
    adjusted_target = target

# Calculate
if st.button("Calculate"):
    required_savings = calculate_annual_savings(adjusted_target, annual_rate, years)
    st.success(f"✅ You need to save **${required_savings:,.2f}** per year to reach your goal of ${target:,.2f} in {years} years.")

    # Growth projection
    df_growth = project_growth(required_savings, annual_rate, years)
    st.line_chart(df_growth.set_index("Year"))

    with st.expander("📊 View data"):
        st.dataframe(df_growth.style.format({"Balance": "${:,.2f}"}))

st.caption("Note: This assumes consistent annual contributions and a fixed return rate, compounded yearly.")