import streamlit as st
import pandas as pd
import plotly.express as px
from src.fetch_data import load_data_from_lag_to_today
from src.process_data import col_date, col_donnees, main_process
import logging
import os
import glob

logging.basicConfig(level=logging.INFO)

LAG_N_DAYS: int = 7

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
@st.cache(ttl=15 * 60)  # Corrected decorator to @st.cache
def load_data(lag_days: int):
    load_data_from_lag_to_today(lag_days)
    main_process()
    data = pd.read_csv("data/interim/daily_data.csv", parse_dates=[col_date])
    return data

# Define a function to load weekly aggregated data
@st.cache(ttl=15 * 60)
def load_weekly_data():
    weekly_data = pd.read_csv("data/interim/weekly_data.csv", parse_dates=['week'])
    return weekly_data

# Load daily data
df = load_data(LAG_N_DAYS)

# Creating a line chart for daily data
st.subheader("Line Chart of Numerical Data Over Time")
fig = px.line(df, x=col_date, y=col_donnees, title="Consommation en fonction du temps")
st.plotly_chart(fig)

# Load weekly data
weekly_df = load_weekly_data()

# Creating a bar chart for weekly data
st.subheader("Bar Chart of Total Weekly Consumption")
weekly_fig = px.bar(weekly_df, x='week', y='total_consumption', title="Total Weekly Consommation")
st.plotly_chart(weekly_fig)
