import streamlit as st


def calculate_annual_savings(future_value, annual_rate, years):
    if annual_rate == 0:
        return future_value / years
    r = annual_rate
    n = years
    pmt = (future_value * r) / ((1 + r) ** n - 1)
    return pmt

st.title("💰 Retirement Savings Calculator")

st.markdown("""
This calculator helps you estimate how much you need to save *each year* to reach your retirement goal.
""")

target = st.number_input("Target Retirement Amount ($)", min_value=10000.0, value=1000000.0, step=10000.0, format="%.2f")
years = st.number_input("Years Until Retirement", min_value=1, value=30)
rate_percent = st.slider("Expected Annual Return (%)", 0.0, 15.0, 7.0)
annual_rate = rate_percent / 100

if st.button("Calculate"):
    required_savings = calculate_annual_savings(target, annual_rate, years)
    st.success(f"✅ You need to save **${required_savings:,.2f}** per year to reach your goal of ${target:,.2f} in {years} years.")

st.caption("Note: This assumes consistent annual contributions and a fixed return rate, compounded yearly.")

