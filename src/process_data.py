import pandas as pd
from typing import List
import os
import glob
from pathlib import Path
import json

col_date: str = "date_heure"
col_donnees: str = "consommation"
cols: List[str] = [col_date, col_donnees]
fic_export_data: str = "data/interim/data.csv"


def load_data():
    list_fic: list[str] = [Path(e) for e in glob.glob("data/raw/*json")]
    list_df: list[pd.DataFrame] = []
    for p in list_fic:
        with open(p, "r") as f:
            dict_data: dict = json.load(f)
            df: pd.DataFrame = pd.DataFrame.from_dict(dict_data.get("results"))
            list_df.append(df)

    df: pd.DataFrame = pd.concat(list_df, ignore_index=True)
    return df


def format_data(df: pd.DataFrame):
    # typage
    df[col_date] = pd.to_datetime(df[col_date])
    # ordre
    df = df.sort_values(col_date)
    # filtrage colonnes
    df = df[cols]
    # dédoublonnage
    df = df.drop_duplicates()
    return df


def export_data(df: pd.DataFrame, filename: str):
    # Builds the path to the file
    file_path = os.path.join("data/interim", filename)
    
    # Ensures the directories exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Exports the DataFrame to a CSV file
    df.to_csv(file_path, index=False)


def main_process():
    df: pd.DataFrame = load_data()
    df = format_data(df)
    export_data(df, "daily_data.csv")  # Keep the original daily data export
    last_7_days_consumption = calculate_last_7_days_consumption(df)
    with open('data/interim/last_7_days_consumption.txt', 'w') as f:
        f.write(str(last_7_days_consumption))


def calculate_last_7_days_consumption(df: pd.DataFrame):
    # Filter data for the last 7 days
    end_date = df[col_date].max()
    start_date = end_date - pd.Timedelta(days=6)
    filtered_df = df[(df[col_date] >= start_date) & (df[col_date] <= end_date)]
    
    # Calculate total consumption for the last 7 days
    total_consumption_last_7_days = filtered_df[col_donnees].sum()
    
    return total_consumption_last_7_days


if __name__ == "__main__":
    main_process()
