"""
normalize.py

Normalize transformed data into relational
tables WITHOUT generating IDs.

The database will generate IDs automatically.
"""

import pandas as pd
from pathlib import Path


def normalize_data(df, output_folder="../processed"):

    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("NORMALIZING DATA")
    print("=" * 60)

    # ==========================================
    # CUSTOMERS
    # ==========================================

    customers = (
        df[
            [
                "Customer ID",
                "Customer Name",
                "Segment"
            ]
        ]
        .drop_duplicates()
        .rename(columns={
            "Customer ID": "customer_id",
            "Customer Name": "customer_name",
            "Segment": "segment"
        })
    )

    customers.to_csv(
        output_folder / "customers.csv",
        index=False
    )

    print(f"Customers : {len(customers)}")

    # ==========================================
    # LOCATIONS
    # ==========================================

    locations = (
        df[
            [
                "Country",
                "Region",
                "State",
                "City",
                "Postal Code"
            ]
        ]
        .drop_duplicates()
        .rename(columns={
            "Country": "country",
            "Region": "region",
            "State": "state",
            "City": "city",
            "Postal Code": "postal_code"
        })
    )

    locations.to_csv(
        output_folder / "locations.csv",
        index=False
    )

    print(f"Locations : {len(locations)}")

    # ==========================================
    # SHIPPING MODES
    # ==========================================

    shipping = (
        df[
            [
                "Ship Mode"
            ]
        ]
        .drop_duplicates()
        .rename(columns={
            "Ship Mode": "ship_mode"
        })
    )

    shipping.to_csv(
        output_folder / "shipping_modes.csv",
        index=False
    )

    print(f"Shipping Modes : {len(shipping)}")

    # ==========================================
    # CATEGORIES
    # ==========================================

    categories = (
        df[
            [
                "Category"
            ]
        ]
        .drop_duplicates()
        .rename(columns={
            "Category": "category_name"
        })
    )

    categories.to_csv(
        output_folder / "categories.csv",
        index=False
    )

    print(f"Categories : {len(categories)}")

    # ==========================================
    # SUBCATEGORIES
    # ==========================================

    subcategories = (
        df[
            [
                "Sub-Category",
                "Category"
            ]
        ]
        .drop_duplicates()
        .rename(columns={
            "Sub-Category": "subcategory_name",
            "Category": "category_name"
        })
    )

    subcategories.to_csv(
        output_folder / "subcategories.csv",
        index=False
    )

    print(f"Subcategories : {len(subcategories)}")

    # ==========================================
    # PRODUCTS
    # ==========================================

    products = (
    df[
        [
            "Product ID",
            "Product Name",
            "Sub-Category"
        ]
      ]
      .sort_values("Product ID")
      .drop_duplicates(subset=["Product ID"])
      .rename(columns={
        "Product ID": "product_id",
        "Product Name": "product_name",
        "Sub-Category": "subcategory_name"
      })
    )

    products.to_csv(
        output_folder / "products.csv",
        index=False
    )

    print(f"Products : {len(products)}")

    # ==========================================
    # ORDERS
    # ==========================================

    orders = (
        df[
            [
                "Order ID",
                "Customer ID",
                "Country",
                "Region",
                "State",
                "City",
                "Postal Code",
                "Ship Mode",
                "Order Date",
                "Ship Date"
            ]
        ]
        .sort_values("Order ID")
        .drop_duplicates()
        .rename(columns={
            "Order ID": "order_id",
            "Customer ID": "customer_id",
            "Country": "country",
            "Region": "region",
            "State": "state",
            "City": "city",
            "Postal Code": "postal_code",
            "Ship Mode": "ship_mode",
            "Order Date": "order_date",
            "Ship Date": "ship_date"
        })
    )

    orders.to_csv(
        output_folder / "orders.csv",
        index=False
    )

    print(f"Orders : {len(orders)}")

    # ==========================================
    # ORDER ITEMS
    # ==========================================

    order_items = (
        df[
            [
                "Row ID",
                "Order ID",
                "Product ID",
                "Sales"
            ]
        ]
        .drop_duplicates(subset=["Row ID"])
        .rename(columns={
            "Row ID": "row_id",
            "Order ID": "order_id",
            "Product ID": "product_id",
            "Sales": "sales"
        })
    )

    order_items.to_csv(
        output_folder / "order_items.csv",
        index=False
    )

    print(f"Order Items : {len(order_items)}")

    print("\nNormalization Completed Successfully!")

    return {
        "customers": customers,
        "locations": locations,
        "shipping_modes": shipping,
        "categories": categories,
        "subcategories": subcategories,
        "products": products,
        "orders": orders,
        "order_items": order_items
    }
    print("\nNormalization Summary")
