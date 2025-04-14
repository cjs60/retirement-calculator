# Retirement Calculator

A web-based retirement calculator that helps you plan for retirement by taking into account various factors including inflation rate.

## Features

- Calculate retirement savings based on current age and retirement age
- Account for current savings and monthly contributions
- Consider expected annual return on investments
- Factor in inflation rate
- Calculate required savings based on desired retirement income
- Show shortfall or surplus in retirement planning

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## How to Use

1. Enter your current age and planned retirement age
2. Input your current savings and monthly contribution amount
3. Specify your expected annual return on investments
4. Set the inflation rate (default is typically around 2-3%)
5. Enter your desired annual income during retirement
6. Specify your life expectancy
7. Click "Calculate" to see the results

The calculator will show:
- Total savings at retirement
- Required savings to meet your goals
- Any shortfall in your savings
- Whether you're on track to meet your retirement goals 