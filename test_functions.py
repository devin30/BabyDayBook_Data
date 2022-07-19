# tests
import pytest
import os
import pandas as pd
from run import import_data, transform_data
from datetime import date, timedelta, datetime as dt

def test_import_data():
    """
    Check if the dataframe contain nonzero num of rows.
    """
    output = import_data()
    assert output.shape[0] > 1000

def test_transform_data():
    """
    Check if the dataframe contain nonzero num of rows.
    """
    # read test data
    data = pd.read_csv("data/events_log_full.csv")
    daily_df_pivot, daily_df = transform_data(data)
    assert daily_df_pivot.shape[0] > 100
