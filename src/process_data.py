import pandas as pd
from typing import List
import os
import glob
from pathlib import Path
import json

col_date: str = "date_heure"
col_donnees: str = "consommation"
cols: List[str] = [col_date, col_donnees]
fic_export_data: str = "data/interim/daily_data.csv"

def load_data():
    list_fic = glob.glob("data/raw/*.json")
    list_df = []
    for p in list_fic:
        with open(p, "r") as f:
            dict_data = json.load(f)
            df = pd.DataFrame.from_dict(dict_data.get("results"))
            list_df.append(df)

    df = pd.concat(list_df, ignore_index=True)
    return df

def format_data(df: pd.DataFrame):
    df[col_date] = pd.to_datetime(df[col_date])
    df = df.sort_values(col_date)
    df = df[cols]
    df = df.drop_duplicates()
    return df

def export_data(df: pd.DataFrame, filename: str):
    os.makedirs("data/interim", exist_ok=True)
    df.to_csv(filename, index=False)

def main_process():
    df = load_data()
    df = format_data(df)
    export_data(df, fic_export_data)
    last_7_days_consumption = calculate_last_7_days_consumption(df)
    with open('data/interim/last_7_days_consumption.txt', 'w') as f:
        f.write(str(last_7_days_consumption))

def calculate_last_7_days_consumption(df: pd.DataFrame):
    df[col_date] = pd.to_datetime(df[col_date])
    df.set_index(col_date, inplace=True)
    df['rolling_sum'] = df[col_donnees].rolling('7D').sum()
    last_7_days_consumption = df['rolling_sum'].iloc[-1]
    return last_7_days_consumption

if __name__ == "__main__":
    main_process()
