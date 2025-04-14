import os
import ldclient
from ldclient.config import Config
from threading import Lock, Event
import streamlit as st
import pandas as pd

# Set sdk_key to your LaunchDarkly SDK key.
sdk_key = os.getenv("LAUNCHDARKLY_SDK_KEY")

feature_flag_key = "inflation-adjustment"

def show_evaluation_result(key: str, value: bool):
    print()
    print(f"*** The {key} feature flag evaluates to {value}")

def ENABLE_INFLATION_ADJUSTMENT():
    ENABLE_INFLATION_ADJUSTMENT = True



class FlagValueChangeListener:
    def __init__(self):
        self.__show_banner = True
        self.__lock = Lock()

    def flag_value_change_listener(self, flag_change):
        with self.__lock:
            if self.__show_banner and flag_change.new_value:
                ENABLE_INFLATION_ADJUSTMENT()
                self.__show_banner = False

            show_evaluation_result(flag_change.key, flag_change.new_value)

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

# Inflation Adjustment
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

if __name__ == "__main__":
    if not sdk_key:
        print("*** Please set the LAUNCHDARKLY_SDK_KEY env first")
        exit()
    if not feature_flag_key:
        print("*** Please set the LAUNCHDARKLY_FLAG_KEY env first")
        exit()

    ldclient.set_config(Config(sdk_key))

    # Initialize LaunchDarkly client
    ld_client = ldclient.get()
    if not ld_client:
        print("*** Failed to initialize LaunchDarkly client")
        exit()
    # Create a flag value change listener
    flag_value_change_listener = FlagValueChangeListener()
    # Register the listener for feature flag changes
    ld_client.register_flag_value_change_listener(
        feature_flag_key,
        flag_value_change_listener.flag_value_change_listener
    )
    # Evaluate the feature flag initially
    initial_value = ld_client.variation(feature_flag_key, default=False)
    if initial_value:
        ENABLE_INFLATION_ADJUSTMENT()
    show_evaluation_result(feature_flag_key, initial_value) 