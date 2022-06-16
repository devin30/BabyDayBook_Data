import sqlite3
import pandas as pd
import numpy as np
from datetime import date, timedelta, datetime as dt
import os
import re
from plot import plot_daily_trend, plot_volumes

def import_data():
    """Load the file into a DataFrame.
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
                dbcon)['name']
                )
    # load tables
    baby_db = {}
    for tablename in tables:
        baby_db[tablename] = pd.read_sql_query(
            f"SELECT * from {tablename}",
            sqlite3.connect(filename))

    return baby_db["daily_actions"]

def transform_data(input_data):
    """Extract useful columns and transform time data.
    """
    data = input_data[[
        "svt",
        "type",
        "start_millis",
        "end_millis",
        "pee",
        "poo",
        "volume",]]

    # Convert milliseconds to date
    data.svt = pd.to_datetime(
        data.svt.apply(lambda x: dt.fromtimestamp(x/1000.0)))
    data["svt_date"] = data.svt.apply(lambda x: x.strftime("%Y-%m-%d"))

    data.start_millis = pd.to_datetime(
        data.start_millis.apply(lambda x: dt.fromtimestamp(x/1000.0)))
    data.end_millis = data.end_millis.apply(lambda x: dt.fromtimestamp(x/1000.0) if x != 0 else 0)

    # data cleaning
    data.loc[data.type == "potty", "type"] = "diaper_change"
    data = data[data.svt_date < dt.now().strftime("%Y-%m-%d")].copy() # last day incomplete

    # aggregation
    daily_df = (data[["svt_date", "type", "volume"]]
                    .groupby(["svt_date", "type"])
                    .agg({"svt_date": "size", "volume": "sum"})
                    .rename(columns={"svt_date": "freq"})
                    .reset_index()
                    .sort_values(["svt_date", "type"])
                )
    daily_df.to_csv("data/daily_df.csv", index=False)
    return data, daily_df

def main():
    events_log_full = import_data()
    events_log_df, daily_df = transform_data(events_log_full)
    # events_log_df.to_csv("data/events_log_df.csv", index=False)

    # outputs:
    plot_daily_trend(daily_df, "bottle", "blue")
    plot_daily_trend(daily_df, "pump", "red")
    plot_daily_trend(daily_df, "diaper_change", "green")
    plot_volumes(daily_df, ["pump", "bottle"], ["red", "blue"])

if __name__ == "__main__":
    main()
