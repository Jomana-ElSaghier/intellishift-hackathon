"""
reports.py
----------------------------------------------------
Generate Business Reports & Data Quality Reports
"""

from pathlib import Path
import pandas as pd


# ======================================================
# BUSINESS INSIGHTS
# ======================================================

def generate_business_insights(df: pd.DataFrame):
    """
    Generate business KPIs and insights.
    """

    insights = {}

    # -----------------------------------------
    # Overall KPIs
    # -----------------------------------------

    insights["Total Revenue"] = round(df["Sales"].sum(), 2)
    insights["Total Orders"] = df["Order ID"].nunique()
    insights["Total Customers"] = df["Customer ID"].nunique()
    insights["Total Products"] = df["Product ID"].nunique()

    # -----------------------------------------
    # Sales
    # -----------------------------------------

    region_sales = df.groupby("Region")["Sales"].sum()

    insights["Top Region"] = region_sales.idxmax()
    insights["Top Region Revenue"] = round(region_sales.max(), 2)

    state_sales = df.groupby("State")["Sales"].sum()

    insights["Top State"] = state_sales.idxmax()

    category_sales = df.groupby("Category")["Sales"].sum()

    insights["Top Category"] = category_sales.idxmax()

    product_sales = df.groupby("Product Name")["Sales"].sum()

    insights["Top Product"] = product_sales.idxmax()

    customer_sales = df.groupby("Customer Name")["Sales"].sum()

    insights["Top Customer"] = customer_sales.idxmax()

    # -----------------------------------------
    # Shipping
    # -----------------------------------------

    insights["Average Shipping Delay"] = round(
        df["Shipping Delay"].mean(),
        2
    )

    shipping_delay = (
        df.groupby("Ship Mode")["Shipping Delay"]
        .mean()
    )

    insights["Fastest Shipping Mode"] = shipping_delay.idxmin()
    insights["Slowest Shipping Mode"] = shipping_delay.idxmax()

    # -----------------------------------------
    # Month
    # -----------------------------------------

    monthly_sales = (
        df.groupby("Month Name")["Sales"]
        .sum()
        .sort_values(ascending=False)
    )

    insights["Best Sales Month"] = monthly_sales.index[0]

    return insights


# ======================================================
# PRINT REPORT
# ======================================================

def print_business_report(insights):

    print("\n")
    print("=" * 70)
    print("BUSINESS INSIGHTS REPORT")
    print("=" * 70)

    for key, value in insights.items():
        print(f"{key:<30}: {value}")


# ======================================================
# SAVE BUSINESS REPORT
# ======================================================

def save_business_report(
    insights,
    output_folder="../reports"
):

    output_folder = Path(output_folder)
    output_folder.mkdir(exist_ok=True)

    report = output_folder / "business_report.md"

    with open(report, "w", encoding="utf-8") as file:

        file.write("# Business Insights Report\n\n")

        for key, value in insights.items():

            file.write(f"- **{key}:** {value}\n")

    print("Business Report Saved.")


# ======================================================
# DATA QUALITY REPORT
# ======================================================

def generate_data_quality_report(
    df,
    output_folder="../reports"
):

    output_folder = Path(output_folder)
    output_folder.mkdir(exist_ok=True)

    report = output_folder / "data_quality_report.md"

    missing = df.isnull().sum()

    duplicates = df.duplicated().sum()

    with open(report, "w", encoding="utf-8") as file:

        file.write("# Data Quality Report\n\n")

        file.write(f"Total Rows: {len(df)}\n\n")

        file.write(f"Total Columns: {len(df.columns)}\n\n")

        file.write(f"Duplicate Rows: {duplicates}\n\n")

        file.write("## Missing Values\n\n")

        for column, value in missing.items():

            file.write(f"- {column}: {value}\n")

    print("Data Quality Report Saved.")