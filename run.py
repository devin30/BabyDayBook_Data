import sqlite3
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime as dt
import os
import re
from plot import plot_daily_trend

def import_data():
    """
    Find the latest db file in the folder.
    Load the file into a DataFrame.
    """
    file_re = re.compile(r"BabyDaybook_\d+_auto\.db")
    files = os.listdir("data/")
    data_files = [f for f in files if file_re.match(f)]
    data_files.sort(reverse=True)
    try:
        filename = os.path.join("data",data_files[0])
    except IndexError:
        print("Error: No data file found")
        raise
    print(f"Found file {filename}")

    # set up connect to db
    with sqlite3.connect(filename) as dbcon:
        tables = list(
            pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table';",
                dbcon)['name'])

    # load tables
    baby_db = {}
    for tablename in tables:
        baby_db[tablename] = pd.read_sql_query(
            f"SELECT * from {tablename}",
            sqlite3.connect(filename))
    return baby_db["daily_actions"]

def transform_data(input_data):
    """
    Extract useful columns and transform time columns.
    """
    # Find relevant columns
    data = input_data[[
        "svt",
        "type",
        "start_millis",
        "end_millis",
        "pee",
        "poo",
        "volume",]]

    # Convert milliseconds to date
    for col in ["svt", "start_millis", "end_millis"]:
        data[col] = data[col].apply(
            lambda x: dt.fromtimestamp(x/1000.0) if x != 0 else 0)
    data["svt_date"] = pd.to_datetime(data.svt).apply(lambda x: x.strftime("%Y-%m-%d"))

    # data cleaning
    data.loc[data.type == "potty", "type"] = "diaper_change"
    data = data[data.svt_date < dt.now().strftime("%Y-%m-%d")].copy() # last day incomplete

    # aggregation
    daily_df = (data[
        ["svt_date", "type", "volume"]]
                    .groupby(["svt_date", "type"])
                    .agg({"svt_date": "size", "volume": "sum"})
                    .rename(columns={"svt_date": "freq"})
                    .reset_index()
                    .sort_values(["svt_date", "type"]))

    # pivot daily_df
    daily_df_freq = pd.pivot_table(
        daily_df,
        values = "freq",
        index = "svt_date",
        columns = "type",
        aggfunc = np.sum,
    ).reset_index()[[
        "svt_date",
        "bottle",
        "pump",
        "diaper_change",
        "tummy_time"]].fillna(0)

    daily_df_vol = pd.pivot_table(
        daily_df,
        values = "volume",
        index = "svt_date",
        columns = "type",
        aggfunc = np.sum,
    ).reset_index()[["svt_date", "bottle", "pump"]].fillna(0)

    daily_df_vol.rename(
        columns= {
            "bottle":"bottle_volume",
            "pump":"pump_volume",},
            inplace = True)

    daily_df_pivot = daily_df_freq.merge(
        daily_df_vol,
        how = "left",
        on = "svt_date",
        )
    return daily_df_pivot, daily_df

def main():
    events_log_full = import_data()
    daily_df_pivot, daily_df = transform_data(events_log_full)

    # Metrics: bottle, pump, diaper_change, tummy_time, bottle_volume, pump_volume
    plot_daily_trend(
        daily_df_pivot,
        ["diaper_change"],
        "Diaper Change Times/Day",
        ["green"]
    )
    plot_daily_trend(
        daily_df_pivot,
        ["pump_volume", "bottle_volume"],
        "Feeding and Pumping Volumes",
        ["red", "blue"],
    )

if __name__ == "__main__":
    main()
