import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from datetime import date, timedelta, datetime as dt

def import_data():
    """Load the file into a DataFrame.
    """
    filename = "data/BabyDaybook_20220510_auto.db"

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
    data = data[data.svt_date < "2022-05-10"].copy() # last day date incomplete

    # aggregation
    daily_df = (data[["svt_date", "type", "volume"]]
                    .groupby(["svt_date", "type"])
                    .agg({"svt_date": "size", "volume": "sum"})
                    .rename(columns={"svt_date": "freq"})
                    .reset_index()
                    .sort_values(["svt_date", "type"])
                )
    return data, daily_df

def plot_daily_trend(
        daily_df,
        action_type,
        linecolour,
    ):
    """Plot daily trends.
    """
    # data in TS form
    daily_dates = daily_df.groupby(["svt_date"]).size().reset_index(name = "drop")
    plot_data = daily_dates.merge(daily_df[daily_df.type == action_type], how='left', on='svt_date')
    plot_data.set_index("svt_date", inplace=True)

    # create a static plot with matplotlib
    fig, ax = plt.subplots()
    fig.set_size_inches(18, 10) # img size

    ax.plot(
        "freq",
        data = plot_data,
        color = linecolour,
        linewidth = 1,
        marker = 'o',
        markersize = 5,
        markeredgecolor = "yellow",
    )
    ax.set(
        xlabel = "Date",
        ylabel = "Frequency",
        title = action_type,
    )
    plt.legend()

    # xticks
    plt.xticks(rotation = 30)
    for label in ax.get_xticklabels()[::2]: # hide some dates on x-axis
        label.set_visible(False)

    # export img
    plt.savefig("img/" + action_type + ".png")
    print("Generated plot for", action_type)

def plot_volumes(
        daily_df,
        action_types,
        linecolours,
    ):
    """Plot daily trends.
    """
    # data in TS form
    plot_data = daily_df.groupby(["svt_date"]).size().reset_index(name = "drop")
    for action in action_types:
        plot_data = plot_data.merge(daily_df.loc[daily_df.type == action, ["svt_date", "volume"]]
                                            .rename(columns={"volume": action}),
                                    how='left', on='svt_date')
    plot_data.set_index("svt_date", inplace=True)

    # create a static plot with matplotlib
    fig, ax = plt.subplots()
    fig.set_size_inches(18, 10) # img size

    for action, colour in zip(action_types, linecolours):
        ax.plot(
            action,
            data = plot_data,
            color = colour,
            linewidth = 1,
            marker = 'o',
            markersize = 5,
            markeredgecolor = "yellow",
        )
    ax.set(
        xlabel = "Date",
        ylabel = "Volume",
        title = "Volumes",
    )
    plt.legend(action_types)

    # xticks
    plt.xticks(rotation = 30)
    for label in ax.get_xticklabels()[::2]: # hide some dates on x-axis
        label.set_visible(False)

    # export img
    plt.savefig("img/" + "_".join(action_types) + "_volumes.png")
    print("Generated volumes plot for", ", ".join(action_types))

def main():
    events_log_full = import_data()
    events_log_df, daily_df = transform_data(events_log_full)

    # outputs:
    plot_daily_trend(daily_df, "bottle", "blue")
    plot_daily_trend(daily_df, "pump", "red")
    plot_daily_trend(daily_df, "diaper_change", "green")
    plot_volumes(daily_df, ["pump", "bottle"], ["red", "blue"])

    # \\\\DEBUG:
    # events_log_df.to_csv("data/events_log_df.csv", index=False)
    # daily_df.to_csv("data/daily_df.csv", index=False)
    # plot_data.to_csv("data/plot_data.csv", index=False)

if __name__ == "__main__":
    main()
