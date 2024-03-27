import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time, timedelta
from src.fetch_data import load_data_from_lag_to_today
from src.process_data import col_date, col_donnees, main_process
import logging
import os
import glob
from pathlib import Path  # Import Path
import json  # Import json

logging.basicConfig(level=logging.INFO)

# Constants
DATA_POINTS_PER_HOUR: int = 4
DATA_POINTS_PER_DAY: int = 96

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
    list_fic: list[str] = [Path(e) for e in glob.glob("data/raw/*json")]
    list_df: list[pd.DataFrame] = []
    for p in list_fic:
        with open(p, "r") as f:
            dict_data: dict = json.load(f)
            # Check if 'results' key is present and not empty
            if "results" in dict_data and dict_data["results"]:
                df: pd.DataFrame = pd.DataFrame.from_dict(dict_data.get("results"))
                list_df.append(df)
    
    # If list_df is empty, return an empty DataFrame with expected columns
    if not list_df:
        return pd.DataFrame(columns=[col_date, col_donnees])

    df: pd.DataFrame = pd.concat(list_df, ignore_index=True)
    return df


# Load daily data
df = load_data()

# Displaying the line chart for daily data
st.subheader("Line Chart of Numerical Data Over Time")
fig = px.line(df, x=col_date, y=col_donnees, title="Consommation en fonction du temps")
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
