
# Afficionado Coffee Roasters
## Sales Trend and Time-Based Performance Analysis

### Project Overview
This project analyzes transaction data from Afficionado Coffee Roasters to understand hourly demand, revenue patterns, store performance, and product category sales.

### Objectives
- Identify peak and off-peak transaction hours.
- Compare sales performance across store locations.
- Analyze revenue by time of day.
- Compare hourly demand across stores.
- Identify high-performing product categories.

### Tools and Technologies
- Python
- Pandas
- Matplotlib
- Seaborn
- Plotly
- Streamlit

### Dashboard Features
- Interactive revenue, quantity, and transaction metrics.
- Store location filters.
- Hour-range slider.
- Time-of-day analysis.
- Cross-location hourly heatmap.
- Product category comparison.

### Key Findings
- Total recorded revenue: $698,812.33
- Total transactions: 149,116
- Total quantity sold: 214,470
- Peak transaction hour: 10:00 AM
- Highest-revenue store: Hell's Kitchen
- Highest-revenue product category: Coffee

### Data Limitation
The supplied dataset does not contain a transaction date. Therefore, weekday, daily, weekly, and chronological annual sales trends could not be reliably calculated.

### Run Locally
Install the dependencies:

    py -m pip install -r requirements.txt

Run the dashboard:

    py -m streamlit run app.py
