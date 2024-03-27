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
        # list_df.append(pd.read_json(p))
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
    last_7_days_consumption = calculate_last_7_days_consumption(df)
    # This value can be written to a file or directly returned, depending on your preference
    with open('data/interim/last_7_days_consumption.txt', 'w') as f:
        f.write(str(last_7_days_consumption))


def calculate_last_7_days_consumption(df: pd.DataFrame):
    df[col_date] = pd.to_datetime(df[col_date])
    df.set_index(col_date, inplace=True)
    # Calculate the rolling sum for the last 7 days
    df['rolling_sum'] = df[col_donnees].rolling('7D').sum()
    # Get the last value, which is the sum of the last 7 days
    last_7_days_consumption = df['rolling_sum'].iloc[-1]
    return last_7_days_consumption


if __name__ == "__main__":

    # data_file: str = "data/raw/eco2mix-regional-tr.csv"
    main_process()

