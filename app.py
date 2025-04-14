from flask import Flask, render_template, request, jsonify
import math
import ldclient
from ldclient.config import Config
from ldclient import Context
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get environment variables
sdk_key = os.getenv('LAUNCHDARKLY_SDK_KEY')
inflation_flag_key = 'inflation-adjuster'

logger.debug(f"SDK Key: {sdk_key[:5]}...")
logger.debug(f"Feature Flag Key: {inflation_flag_key}")

if not sdk_key:
    logger.error("Missing required environment variable: LAUNCHDARKLY_SDK_KEY")
    raise ValueError("Missing required environment variable: LAUNCHDARKLY_SDK_KEY")

# Initialize LaunchDarkly client
try:
    config = Config(sdk_key)
    ldclient.set_config(config)
    ld_client = ldclient.get()
    logger.info("LaunchDarkly client initialized successfully")
    
    # Test the client connection
    if ld_client.is_initialized():
        logger.info("LaunchDarkly client is properly initialized")
        # Test the feature flag
        test_context = Context.builder('test-user').kind('user').set('country', 'United States').build()
        test_result = ld_client.variation(inflation_flag_key, test_context, False)
        logger.info(f"Test feature flag evaluation: {test_result}")
    else:
        logger.error("LaunchDarkly client failed to initialize properly")
except Exception as e:
    logger.error(f"Failed to initialize LaunchDarkly client: {str(e)}")
    raise

app = Flask(__name__)

def get_feature_flag_status():
    try:
        # Create a proper Context object with location
        context = Context.builder('default-user').kind('user').set('country', 'United States').build()
        status = ld_client.variation(inflation_flag_key, context, False)
        logger.debug(f"Feature flag '{inflation_flag_key}' status: {status}")
        return status
    except Exception as e:
        logger.error(f"Error checking feature flag: {str(e)}", exc_info=True)
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check-feature-flag')
def check_feature_flag():
    try:
        status = get_feature_flag_status()
        logger.debug(f"Feature flag check result: {status}")
        return jsonify({
            'inflation_enabled': status,
            'error': None
        })
    except Exception as e:
        logger.error(f"Error in check-feature-flag endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'inflation_enabled': False,
            'error': str(e)
        }), 500

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.json
        logger.debug(f"Received calculation request: {data}")
        
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
        logger.debug(f"Calculation result: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in calculate endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

def calculate_retirement(current_age, retirement_age, current_savings, monthly_contribution, 
                        annual_return, inflation_rate, desired_income, life_expectancy):
    try:
        # Convert annual values to monthly
        monthly_return = (1 + annual_return) ** (1/12) - 1
        logger.debug(f"Monthly return rate: {monthly_return}")
        
        # Get inflation rate from feature flag
        flag_value = get_feature_flag_status()
        logger.debug(f"Feature flag value: {flag_value}")
        
        if flag_value:
            monthly_inflation = (1 + inflation_rate) ** (1/12) - 1
            logger.info(f"Using custom inflation rate: {inflation_rate}%")
        else:
            monthly_inflation = (1 + 0.02) ** (1/12) - 1
            logger.info("Using default inflation rate: 2%")
        
        # Calculate number of months until retirement
        months_to_retirement = (retirement_age - current_age) * 12
        logger.debug(f"Months to retirement: {months_to_retirement}")
        
        # Calculate future value of current savings
        future_value_current_savings = current_savings * (1 + monthly_return) ** months_to_retirement
        logger.debug(f"Future value of current savings: {future_value_current_savings}")
        
        # Calculate future value of monthly contributions
        future_value_contributions = monthly_contribution * ((1 + monthly_return) ** months_to_retirement - 1) / monthly_return
        logger.debug(f"Future value of contributions: {future_value_contributions}")
        
        # Total retirement savings at retirement
        total_savings = future_value_current_savings + future_value_contributions
        logger.debug(f"Total savings: {total_savings}")
        
        # Calculate number of months in retirement and convert to integer
        months_in_retirement = int((life_expectancy - retirement_age) * 12)
        logger.debug(f"Months in retirement: {months_in_retirement}")
        
        # Calculate monthly withdrawal amount adjusted for inflation
        monthly_withdrawal = desired_income / 12
        logger.debug(f"Monthly withdrawal: {monthly_withdrawal}")
        
        # Calculate if savings are sufficient
        required_savings = 0
        for month in range(months_in_retirement):
            required_savings += monthly_withdrawal * (1 + monthly_inflation) ** month / (1 + monthly_return) ** month
        logger.debug(f"Required savings: {required_savings}")
        
        return {
            'total_savings': round(total_savings, 2),
            'required_savings': round(required_savings, 2),
            'is_sufficient': total_savings >= required_savings,
            'shortfall': round(max(0, required_savings - total_savings), 2),
            'inflation_enabled': flag_value
        }
    except Exception as e:
        logger.error(f"Error in retirement calculation: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    app.run(debug=True) 