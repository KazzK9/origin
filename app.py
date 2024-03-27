import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time, timedelta
from src.fetch_data import load_data_from_lag_to_today
from src.process_data import col_date, col_donnees, main_process
import logging
import os
import glob
from pathlib import Path  # Make sure to import Path
import json  # Make sure to import json

logging.basicConfig(level=logging.INFO)

# Constants
DATA_POINTS_PER_HOUR: int = 4  # Assuming there are 4 data points per hour
DATA_POINTS_PER_DAY: int = 96  # Assuming there are 96 data points per day

# Initialize directories for data storage
os.makedirs("data/raw/", exist_ok=True)
os.makedirs("data/interim/", exist_ok=True)

# Remove outdated JSON files
for file_path in glob.glob("data/raw/*json"):
    try:
        os.remove(file_path)
    except FileNotFoundError as e:
        logging.warning(e)

# Title for your app
st.title("Data Visualization App")

# Function to load daily data
@st.cache(ttl=15 * 60)
def load_data():
    load_data_from_lag_to_today(LAG_N_DAYS)
    main_process()  # This processes and ensures the data is up-to-date
    data = pd.read_csv("data/interim/daily_data.csv", parse_dates=[col_date])
    return data

# Load daily data
df = load_data()

# Displaying the line chart for daily data with hover data
st.subheader("Line Chart of Numerical Data Over Time")
fig = px.line(df, x=col_date, y=col_donnees, title="Consommation en fonction du temps", hover_data={col_date: "|%B %d, %Y", col_donnees: True})
st.plotly_chart(fig)

# Calculate total consumption for the last 7 days
recent_consumption = df[df[col_date] >= (df[col_date].max() - pd.Timedelta(days=7))][col_donnees].sum()
st.subheader(f"Total Consumption for the Last 7 Days: {recent_consumption:.2f} units")

# Calculate the number of expected data points from now to tomorrow at 12PM
now = datetime.now()
tomorrow_noon = datetime.combine((now + timedelta(days=1)).date(), time(12, 0))
hours_until_tomorrow_noon = (tomorrow_noon - now).total_seconds() / 3600
expected_data_points = int(hours_until_tomorrow_noon * DATA_POINTS_PER_HOUR)

# Display the number of expected data points
st.subheader(f"Expected Data Points Until Tomorrow 12 PM: {expected_data_points}")
