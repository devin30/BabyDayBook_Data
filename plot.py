import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import pandas as pd
import numpy as np
import os

def plot_daily_trend(
        daily_df_pivot,
        action_types,
        title,
        linecolours,
    ):
    """Plot daily trends.
    """
    data = daily_df_pivot.copy()
    data.set_index("svt_date", inplace=True)

    # create a static plot with matplotlib
    fig, ax = plt.subplots()
    fig.set_size_inches(18, 5) # img size

    for action, colour in zip(action_types, linecolours):
        ax.plot(
            action,
            data = data,
            color = colour,
            linewidth = 1,
            marker = 'o',
            markersize = 5,
            markeredgecolor = "yellow",
        )

    ax.set(
        xlabel = "Date",
        ylabel = "Trend",
        title = title,
    )
    plt.legend(action_types)
    ax.xaxis.set_major_locator(mdates.MonthLocator())

    # export img
    plt.savefig("img/" + "_".join(action_types) + ".png")
    print("Generated volumes plot for", ", ".join(action_types))
