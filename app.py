import streamlit as st
import pandas as pd
import plotly.express as px
from src.fetch_data import load_data_from_lag_to_today
from src.process_data import col_date, col_donnees, main_process
import logging
import os
import glob

logging.basicConfig(level=logging.INFO)

# Constants
LAG_N_DAYS: int = 7
EXPECTED_SAMPLES_PER_DAY: int = 24  # or however many you expect per day

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
def load_data(lag_days: int):
    load_data_from_lag_to_today(lag_days)
    main_process()
    data = pd.read_csv("data/interim/daily_data.csv", parse_dates=[col_date])
    return data

# Function to remove the last N samples and return the number of removed samples
def remove_data(df: pd.DataFrame, last_n_samples: int = EXPECTED_SAMPLES_PER_DAY):
    removed_data = df.tail(last_n_samples)
    df.drop(df.tail(last_n_samples).index, inplace=True)
    return df, removed_data.shape[0]

# Load and clean daily data
df, num_removed_samples = remove_data(load_data(LAG_N_DAYS), last_n_samples=EXPECTED_SAMPLES_PER_DAY)

# Displaying the line chart for daily data
st.subheader("Line Chart of Numerical Data Over Time")
fig = px.line(df, x=col_date, y=col_donnees, title="Consommation en fonction du temps")
st.plotly_chart(fig)

# Calculate and display total consumption for the last 7 days
recent_consumption = df[df[col_date] >= (df[col_date].max() - pd.Timedelta(days=7))][col_donnees].sum()
st.subheader(f"Total Consumption for the Last 7 Days: {recent_consumption:.2f} units")

# Display the number of removed samples
st.subheader(f"Number of Missing Data Points: {num_removed_samples}")
