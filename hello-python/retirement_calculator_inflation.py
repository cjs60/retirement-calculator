import streamlit as st
import pandas as pd
import os
import ldclient
from threading import Lock, Event
from ldclient import Context
from ldclient.config import Config

# --- LaunchDarkly Setup ---
sdk_key = os.getenv("LAUNCHDARKLY_SDK_KEY")
flag_key = "enable-inflation-adjustment"

if not sdk_key:
    st.error("Missing LAUNCHDARKLY_SDK_KEY environment variable.")
    st.stop()

ldclient.set_config(Config(sdk_key))
ld = ldclient.get()

if not ld.is_initialized():
    st.error("LaunchDarkly failed to initialize.")
    st.stop()

# --- Define context ---
context = Context.builder("retirement-user").kind("user").name("Sandy").build()

# --- Flag Listener Class ---
class FlagValueChangeListener:
    def __init__(self, flag_key):
        self.flag_key = flag_key
        self.__lock = Lock()

    def on_flag_value_change(self, flag_change):
        with self.__lock:
            if self.flag_key and flag_change.new_value:
                st.session_state.enable_inflation = flag_change.new_value
                st.experimental_rerun()

# --- Register Listener ---
# Ensure the 'enable_inflation' flag is initialized in the session state to avoid KeyError during access.
if "enable_inflation" not in st.session_state:
    # Set the default value for the flag to False if not explicitly set in LaunchDarkly
    st.session_state.enable_inflation = ld.variation(flag_key, context, False)

listener = FlagValueChangeListener(flag_key=flag_key)
ld.variation(flag_key, context, False)

# --- App Logic ---
def calculate_annual_savings(future_value, annual_rate, years):
    if annual_rate == 0:
        return future_value / years
    return (future_value * annual_rate) / ((1 + annual_rate) ** years - 1)

def project_growth(pmt, annual_rate, years):
    balance = 0
    growth = []
    for year in range(1, years + 1):
        balance = balance * (1 + annual_rate) + pmt
        growth.append((year, balance))
    return pd.DataFrame(growth, columns=["Year", "Balance"])

# --- Streamlit UI ---
st.title("💰 Retirement Savings Calculator")
st.markdown("Estimate how much to save each year to reach your retirement goal.")

target = st.number_input("Target Retirement Amount ($)", min_value=10000.0, value=1000000.0, step=10000.0)
years = st.number_input("Years Until Retirement", min_value=1, value=30)
rate_percent = st.slider("Expected Annual Return (%)", 0.0, 15.0, 7.0)
annual_rate = rate_percent / 100

adjusted_target = target

# Conditionally show inflation options
if st.session_state.enable_inflation:
    st.markdown("🚩 Inflation adjustment is ENABLED (via LaunchDarkly)")
    adjust_for_inflation = st.checkbox("Adjust for Inflation")
    if adjust_for_inflation:
        inflation_percent = st.slider("Expected Inflation Rate (%)", 0.0, 10.0, 2.5)
        inflation_rate = inflation_percent / 100
        adjusted_target = target / ((1 + inflation_rate) ** years)
        st.markdown(f"🎯 Inflation-adjusted target: **${adjusted_target:,.2f}**")
else:
    st.markdown("ℹ️ Inflation adjustment is DISABLED (via LaunchDarkly)")

# --- Perform Calculation ---
if st.button("Calculate"):
    annual_savings = calculate_annual_savings(adjusted_target, annual_rate, years)
    st.success(f"✅ Save **${annual_savings:,.2f}** per year to reach ${target:,.2f} in {years} years.")

    df_growth = project_growth(annual_savings, annual_rate, years)
    st.line_chart(df_growth.set_index("Year"))

    with st.expander("📊 View Data"):
        st.dataframe(df_growth.style.format({"Balance": "${:,.2f}"}))

st.caption("This tool assumes yearly contributions and compound interest.")
