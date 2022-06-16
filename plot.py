import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np

def plot_daily_trend_new(
        daily_df,
    ):
    """Plot daily trends.
    """
    daily_df = pd.read_csv("data/daily_df.csv")
    daily_df_freq = pd.pivot_table(
        daily_df,
        values="freq",
        index="svt_date",
        columns="type",
        aggfunc=np.sum
    ).reset_index()[
            ["svt_date", "bottle", "pump", "diaper_change", "tummy_time"]
        ].fillna(0)

    daily_df_vol = pd.pivot_table(
        daily_df,
        values="volume",
        index="svt_date",
        columns="type",
        aggfunc=np.sum
    ).reset_index()[["svt_date", "bottle", "pump"]].fillna(0)

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
    # plot_data.to_csv("data/plot_data.csv", index=False)

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
