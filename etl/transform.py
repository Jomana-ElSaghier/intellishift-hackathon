"""
transform.py
-------------------
Transforms and cleans the dataset.
"""

import pandas as pd


def transform_data(df: pd.DataFrame):
    """
    Clean and transform the dataset.
    """

    # ==========================
    # Remove Extra Spaces
    # ==========================
    df.columns = df.columns.str.strip()

    string_columns = df.select_dtypes(include="object").columns

    for col in string_columns:
        df[col] = df[col].astype(str).str.strip()

    # ==========================
    # Remove Duplicate Rows
    # ==========================
    df = df.drop_duplicates()

    # ==========================
    # Convert Dates
    # ==========================
    df["Order Date"] = pd.to_datetime(
        df["Order Date"],
        dayfirst=True,
        errors="coerce"
    )

    df["Ship Date"] = pd.to_datetime(
        df["Ship Date"],
        dayfirst=True,
        errors="coerce"
    )

    # ==========================
    # Remove Invalid Dates
    # ==========================
    df = df.dropna(subset=["Order Date", "Ship Date"])

    # ==========================
    # Convert Sales
    # ==========================
    df["Sales"] = pd.to_numeric(
        df["Sales"],
        errors="coerce"
    )

    # Remove invalid sales
    df = df[df["Sales"] > 0]

    # ==========================
    # Feature Engineering
    # ==========================

    # Shipping Delay
    df["Shipping Delay"] = (
        df["Ship Date"] -
        df["Order Date"]
    ).dt.days

    # Remove negative delays
    df = df[df["Shipping Delay"] >= 0]

    # Year
    df["Year"] = df["Order Date"].dt.year

    # Month Number
    df["Month"] = df["Order Date"].dt.month

    # Month Name
    df["Month Name"] = df["Order Date"].dt.month_name()

    # Quarter
    df["Quarter"] = df["Order Date"].dt.quarter

    # Weekday
    df["Weekday"] = df["Order Date"].dt.day_name()

    return df