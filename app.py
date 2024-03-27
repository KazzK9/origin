import streamlit as st
import pandas as pd
import plotly.express as px
from src.fetch_data import load_data_from_lag_to_today
from src.process_data import col_date, col_donnees, main_process
import logging
import os
import glob

def remove_data(df: pd.DataFrame, last_n_samples: int = 4*3):

    # df: pd.DataFrame = pd.read_csv(fic_export_data)
    return df.iloc[:-last_n_samples]
    # df.to_csv(fic_export_data, index=False)

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

# Load daily data
df = load_data(LAG_N_DAYS)
df = remove_data(df, last_n_samples=4*24)

# Creating a line chart for daily data
st.subheader("Line Chart of Numerical Data Over Time")
fig = px.line(df, x=col_date, y=col_donnees, title="Consommation en fonction du temps")
st.plotly_chart(fig)

# Calculate total consumption for the last 7 days
recent_consumption = df[df[col_date] >= (df[col_date].max() - pd.Timedelta(days=7))][col_donnees].sum()

# Display total consumption for the last 7 days
st.subheader(f"Total Consumption for the Last 7 Days: {recent_consumption:.2f} units")
