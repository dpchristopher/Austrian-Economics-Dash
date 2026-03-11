# -*- coding: utf-8 -*-
"""
utils/data_loader.py
--------------------
Loads and caches the Econ_Dashboard_Dataset.csv.
Path is resolved relative to this file so the app works on any machine.
"""
import streamlit as st
import pandas as pd
from pathlib import Path

# Resolve CSV path relative to this file (utils/ -> project root)
DATA_PATH = Path(__file__).parent.parent / "Econ_Dashboard_Dataset.csv"


@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load the dataset from CSV. Cached per session.

    Returns a DataFrame with:
    - DATE column as datetime (first of each month)
    - All other columns as float64
    - NaN values preserved in early rows where series have shorter histories
    - Rows sorted ascending by DATE
    """
    df = pd.read_csv(DATA_PATH)
    df["DATE"] = pd.to_datetime(df["DATE"], format="%Y-%m")
    df = df.sort_values("DATE").reset_index(drop=True)
    return df


def get_date_range(df: pd.DataFrame) -> tuple:
    """Return (min_date, max_date) as Timestamps from the DATE column."""
    return df["DATE"].min(), df["DATE"].max()
