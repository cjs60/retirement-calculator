from flask import Flask, render_template, request, jsonify
import math
import ldclient
from ldclient.config import Config
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize LaunchDarkly client
ldclient.set_config(Config(os.getenv('LAUNCHDARKLY_SDK_KEY')))
inflation_flag_key = os.getenv("LAUNCHDARKLY_INFLATION_FLAG_KEY")
ld_client = ldclient.get()

app = Flask(__name__)

def calculate_retirement(current_age, retirement_age, current_savings, monthly_contribution, 
                        annual_return, inflation_rate, desired_income, life_expectancy):
    # Convert annual values to monthly
    monthly_return = (1 + annual_return) ** (1/12) - 1
    
    # Check if inflation rate feature is enabled
    user = {
        "key": "user-key",  # You can make this dynamic based on user session
        "custom": {
            "name": "Sandy",
            "current_age": current_age,
            "retirement_age": retirement_age
        }
    }
    
    # Get inflation rate from feature flag if enabled
    if ld_client.variation(inflation_flag_key, user, False):
        monthly_inflation = (1 + inflation_rate) ** (1/12) - 1
    else:
        # Default inflation rate of 2% if feature is disabled
        monthly_inflation = (1 + 0.02) ** (1/12) - 1
    
    # Calculate number of months until retirement
    months_to_retirement = (retirement_age - current_age) * 12
    
    # Calculate future value of current savings
    future_value_current_savings = current_savings * (1 + monthly_return) ** months_to_retirement
    
    # Calculate future value of monthly contributions
    future_value_contributions = monthly_contribution * ((1 + monthly_return) ** months_to_retirement - 1) / monthly_return
    
    # Total retirement savings at retirement
    total_savings = future_value_current_savings + future_value_contributions
    
    # Calculate number of months in retirement
    months_in_retirement = (life_expectancy - retirement_age) * 12
    
    # Calculate monthly withdrawal amount adjusted for inflation
    monthly_withdrawal = desired_income / 12
    
    # Calculate if savings are sufficient
    required_savings = 0
    for month in range(months_in_retirement):
        required_savings += monthly_withdrawal * (1 + monthly_inflation) ** month / (1 + monthly_return) ** month
    
    return {
        'total_savings': round(total_savings, 2),
        'required_savings': round(required_savings, 2),
        'is_sufficient': total_savings >= required_savings,
        'shortfall': round(max(0, required_savings - total_savings), 2),
        'inflation_enabled': ld_client.variation(inflation_flag_key, user, False)
    }

def get_feature_flag_status(user_key="default-user"):
    user = {
        "key": user_key,
        "custom": {
            "name": "Sandy"
        }
    }
    return ld_client.variation(inflation_flag_key, user, False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    result = calculate_retirement(
        float(data['currentAge']),
        float(data['retirementAge']),
        float(data['currentSavings']),
        float(data['monthlyContribution']),
        float(data['annualReturn']) / 100,
        float(data['inflationRate']) / 100,
        float(data['desiredIncome']),
        float(data['lifeExpectancy'])
    )
    return jsonify(result)

@app.route('/check-feature-flag')
def check_feature_flag():
    return jsonify({
        'inflation_enabled': get_feature_flag_status()
    })

if __name__ == '__main__':
    app.run(debug=True) 