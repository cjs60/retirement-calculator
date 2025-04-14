from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from launchdarkly_api import LaunchDarklyApi
from ldclient import LDClient, Config
import os

app = FastAPI()

# LaunchDarkly setup
sdk_key = os.getenv("LAUNCHDARKLY_SDK_KEY")
inflation_flag_key = os.getenv("LAUNCHDARKLY_INFLATION_FLAG_KEY")
ld_client = LDClient(Config(sdk_key))

@app.get("/", response_class=HTMLResponse)
async def form():
    user = {"key": "example-user"}
    use_inflation_adjustment = ld_client.variation(inflation_flag_key, user, False)

    inflation_fields = ""
    if use_inflation_adjustment:
        inflation_fields = """
            Expected Annual Inflation (%): <input type="number" step="0.01" name="inflation_rate" value="2" /><br/>
            <input type=\"checkbox\" name=\"adjust_for_inflation\" checked /> Adjust for inflation<br/>
        """

    html = f"""
    <html>
    <head><title>Retirement Calculator</title></head>
    <body>
        <h1>Retirement Calculator</h1>
        <form method="post">
            Annual Savings: <input type="number" step="0.01" name="annual_savings" value="10000" /><br/>
            Interest Rate (%): <input type="number" step="0.01" name="interest_rate" value="5" /><br/>
            Years Until Retirement: <input type="number" name="years" value="30" /><br/>
            {inflation_fields}
            <input type="submit" value="Calculate" />
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

@app.post("/", response_class=HTMLResponse)
async def calculate(
    annual_savings: float = Form(...),
    interest_rate: float = Form(...),
    years: int = Form(...),
    inflation_rate: float = Form(2.0),
    adjust_for_inflation: str = Form(None)
):
    user = {"key": "example-user"}
    use_inflation_adjustment = ld_client.variation(inflation_flag_key, user, False)

    if use_feature:
        rate = interest_rate / 100
        apply_inflation = use_inflation_adjustment and adjust_for_inflation is not None
        inflation = inflation_rate / 100 if apply_inflation else 0
        real_rate = rate - inflation

        future_value = 0
        for _ in range(years):
            future_value = (future_value + annual_savings) * (1 + real_rate)

        inflation_note = " (adjusted for inflation)" if apply_inflation else ""
        message = f"<h2>Projected Retirement Savings{inflation_note}: ${future_value:,.2f}</h2>"
    else:
        message = "<h2>The retirement calculator feature is currently disabled.</h2>"

    return HTMLResponse(content=f"""
    <html>
    <head><title>Retirement Calculator</title></head>
    <body>
        <h1>Retirement Calculator</h1>
        {message}
        <a href="/">Try Again</a>
    </body>
    </html>
    """)
