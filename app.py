import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from src.fetch_data import load_data_from_lag_to_today
from src.process_data import col_date, col_donnees, main_process
import logging
import os
import glob

logging.basicConfig(level=logging.INFO)

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

# Define a function to load daily data
@st.cache(ttl=15 * 60)
def load_data():
    main_process()  # Ensure the processing script is run to format and save data
    data = pd.read_csv("data/interim/daily_data.csv", parse_dates=[col_date])
    return data

# Load daily data
df = load_data()

# Creating a line chart for daily data
st.subheader("Line Chart of Numerical Data Over Time")
fig = px.line(df, x=col_date, y=col_donnees, title="Consommation en fonction du temps")
st.plotly_chart(fig)

# Calculate total consumption for the last 7 days
recent_consumption = df[df[col_date] >= (datetime.now() - timedelta(days=7))][col_donnees].sum()

# Display recent consumption as a written number
st.subheader(f"Total Consumption for the Last 7 Days: {recent_consumption:.2f} units")
