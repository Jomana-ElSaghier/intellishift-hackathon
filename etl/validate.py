"""
validate.py
-------------
Performs data quality validation on the raw dataset.
"""

import pandas as pd


def validate_data(df: pd.DataFrame):
    """
    Validate dataset quality and return a report dictionary.
    """

    report = {}

    # ==========================
    # Basic Information
    # ==========================
    report["rows"] = len(df)
    report["columns"] = len(df.columns)

    # ==========================
    # Missing Values
    # ==========================
    report["missing_values"] = df.isnull().sum().to_dict()

    # ==========================
    # Duplicate Rows
    # ==========================
    report["duplicate_rows"] = int(df.duplicated().sum())

    # ==========================
    # Invalid Sales
    # ==========================
    report["invalid_sales"] = int((df["Sales"] <= 0).sum())

    # ==========================
    # Missing Customer IDs
    # ==========================
    report["missing_customer_ids"] = int(df["Customer ID"].isnull().sum())

    # ==========================
    # Missing Product IDs
    # ==========================
    report["missing_product_ids"] = int(df["Product ID"].isnull().sum())

    # ==========================
    # Missing Order IDs
    # ==========================
    report["missing_order_ids"] = int(df["Order ID"].isnull().sum())

    # ==========================
    # Unique Counts
    # ==========================
    report["unique_customers"] = df["Customer ID"].nunique()
    report["unique_products"] = df["Product ID"].nunique()
    report["unique_orders"] = df["Order ID"].nunique()

    return report


def print_validation_report(report):
    """
    Print validation results.
    """

    print("=" * 60)
    print("DATA VALIDATION REPORT")
    print("=" * 60)

    print(f"Rows: {report['rows']}")
    print(f"Columns: {report['columns']}")

    print("\nMissing Values")
    print("-" * 30)

    for column, value in report["missing_values"].items():
        print(f"{column}: {value}")

    print("\nDuplicate Rows")
    print("-" * 30)
    print(report["duplicate_rows"])

    print("\nInvalid Sales")
    print("-" * 30)
    print(report["invalid_sales"])

    print("\nMissing Customer IDs")
    print("-" * 30)
    print(report["missing_customer_ids"])

    print("\nMissing Product IDs")
    print("-" * 30)
    print(report["missing_product_ids"])

    print("\nMissing Order IDs")
    print("-" * 30)
    print(report["missing_order_ids"])

    print("\nUnique Counts")
    print("-" * 30)
    print(f"Customers : {report['unique_customers']}")
    print(f"Products  : {report['unique_products']}")
    print(f"Orders    : {report['unique_orders']}")

    print("=" * 60)