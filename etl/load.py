"""
===========================================================
load.py

Load normalized CSV files into PostgreSQL
using the normalized database schema.

Author: Member 2 - ETL & Data Engineering
===========================================================
"""

import pandas as pd

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy import text
import pandas as pd

def normalize_postal(value):
    if pd.isna(value):
        return ""
    return str(value).strip()
# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "intellishift",
    "username": "postgres",
    "password": "JHSJ"
}

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_CONFIG['username']}:"
    f"{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:"
    f"{DB_CONFIG['port']}/"
    f"{DB_CONFIG['database']}"
)

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True
)
# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Return database connection.
    """

    return engine.connect()
# ============================================================
# READ NORMALIZED FILES
# ============================================================

def read_normalized_data(folder="../processed"):
    """
    Read every normalized CSV file.
    """

    folder = Path(folder)

    data = {

        "customers":
        pd.read_csv(folder / "customers.csv"),

        "locations":
        pd.read_csv(folder / "locations.csv"),

        "shipping_modes":
        pd.read_csv(folder / "shipping_modes.csv"),

        "categories":
        pd.read_csv(folder / "categories.csv"),

        "subcategories":
        pd.read_csv(folder / "subcategories.csv"),

        "products":
        pd.read_csv(folder / "products.csv"),

        "orders":
        pd.read_csv(folder / "orders.csv"),

        "order_items":
        pd.read_csv(folder / "order_items.csv")

    }

    return data
# ============================================================
# INSERT DATAFRAME
# ============================================================

def insert_dataframe(df, table_name, connection):

    print(f"Loading {table_name}...")

    df.to_sql(
        table_name,
        con=connection,
        if_exists="append",
        index=False,
        chunksize=500
    )

    print(f"Loaded {len(df)} rows -> {table_name}")
# ============================================================
# CLEAR DATABASE
# ============================================================

def clear_database(connection):
    """
    Remove all existing data
    before loading.
    """

    print("\nCleaning Database...")

    connection.execute(text("""

        TRUNCATE TABLE

            order_items,

            orders,

            products,

            subcategories,

            categories,

            shipping_modes,

            locations,

            customers

        RESTART IDENTITY

        CASCADE;

    """))

    print("Database Cleaned Successfully.")
# ============================================================
# TRANSACTION
# ============================================================

def begin_transaction():
    """
    Start transaction.
    """

    return engine.begin()
# ============================================================
# PRINT SECTION
# ============================================================

def print_section(title):

    print()

    print("=" * 65)

    print(title)

    print("=" * 65)
# ============================================================
# TEST DATABASE
# ============================================================

def test_connection():

    try:

        with engine.connect() as conn:

            conn.execute(text("SELECT 1"))

        print("Database Connected Successfully.")

    except Exception as e:

        print("Database Connection Failed.")

        raise e
# ============================================================
# LOAD CUSTOMERS
# ============================================================

def load_customers(data, connection):

    print_section("Loading Customers")

    insert_dataframe(
        data["customers"],
        "customers",
        connection
        
    )


# ============================================================
# LOAD LOCATIONS
# ============================================================

def load_locations(data,connection):

    print_section("Loading Locations")

    insert_dataframe(
        data["locations"],
        "locations",
        connection
    )


# ============================================================
# LOAD SHIPPING MODES
# ============================================================

def load_shipping_modes(data , connection):

    print_section("Loading Shipping Modes")

    insert_dataframe(
        data["shipping_modes"],
        "shipping_modes",
        connection
    )


# ============================================================
# LOAD CATEGORIES
# ============================================================

def load_categories(data , connection):

    print_section("Loading Categories")

    insert_dataframe(
        data["categories"],
        "categories",
        connection
    )
# ============================================================
# CATEGORY LOOKUP
# ============================================================

def get_category_lookup(connection):

    query = text("""

        SELECT
            category_id,
            category_name
        FROM categories

    """)

    result = connection.execute(query)

    lookup = {}

    for row in result:

        lookup[row.category_name] = row.category_id

    return lookup
# ============================================================
# LOAD SUBCATEGORIES
# ============================================================

def load_subcategories(data, connection):

    print_section("Loading Subcategories")

    category_lookup = get_category_lookup(connection)

    subcategories = data["subcategories"].copy()

    subcategories["category_id"] = (
        subcategories["category_name"]
        .map(category_lookup)
    )

    if subcategories["category_id"].isna().any():

        raise Exception(
            "Category lookup failed."
        )

    subcategories = subcategories[
        [
            "subcategory_name",
            "category_id"
        ]
    ]

    insert_dataframe(
        subcategories,
        "subcategories",
        connection
    )
# ============================================================
# LOAD PARENT TABLES
# ============================================================

def load_parent_tables(data, connection):

    print_section("Loading Parent Tables")

    load_customers(data, connection)

    load_locations(data, connection)

    load_shipping_modes(data, connection)

    load_categories(data, connection)

    load_subcategories(
        data,
        connection
    )

    print()

    print("Parent Tables Loaded Successfully.")
# ============================================================
# SUBCATEGORY LOOKUP
# ============================================================

def get_subcategory_lookup(connection):

    query = text("""
        SELECT
            subcategory_id,
            subcategory_name
        FROM subcategories;
    """)

    result = connection.execute(query)

    lookup = {}

    for row in result:
        lookup[row.subcategory_name] = row.subcategory_id

    return lookup
# ============================================================
# SHIPPING LOOKUP
# ============================================================

def get_shipping_lookup(connection):

    query = text("""
        SELECT
            shipping_id,
            ship_mode
        FROM shipping_modes;
    """)

    result = connection.execute(query)

    lookup = {}

    for row in result:
        lookup[row.ship_mode] = row.shipping_id

    return lookup
# ============================================================
# LOCATION LOOKUP
# ============================================================

def get_location_lookup(connection):

    query = text("""
        SELECT
            location_id,
            country,
            region,
            state,
            city,
            postal_code
        FROM locations;
    """)

    result = connection.execute(query)

    lookup = {}

    for row in result:

        key = (
            row.country,
            row.region,
            row.state,
            row.city,
            normalize_postal(row.postal_code)
        )

        lookup[key] = row.location_id

    return lookup
# ============================================================
# LOAD PRODUCTS
# ============================================================

def load_products(data, connection):

    
    print_section("Loading Products")

    sub_lookup = get_subcategory_lookup(connection)

    products = data["products"].copy()

    products["subcategory_id"] = (
        products["subcategory_name"]
        .map(sub_lookup)
    )

    if products["subcategory_id"].isna().any():

        raise Exception(
            "Subcategory lookup failed."
        )

    products = products[
        [
            "product_id",
            "product_name",
            "subcategory_id"
        ]
    ]

    insert_dataframe(
        products,
        
        "products",
        connection
    )
# ============================================================
# LOAD ORDERS
# ============================================================

def load_orders(data, connection):

    print_section("Loading Orders")

    shipping_lookup = get_shipping_lookup(connection)

    location_lookup = get_location_lookup(connection)

    orders = data["orders"].copy()

    # Shipping

    orders["shipping_id"] = (
        orders["ship_mode"]
        .map(shipping_lookup)
    )

    # Location

    def map_location(row):

        key = (
            row["country"],
            row["region"],
            row["state"],
            row["city"],
        normalize_postal(row["postal_code"])
        )

        return location_lookup[key]

    orders["location_id"] = (
        orders.apply(
            map_location,
            axis=1
        )
    )

    if orders["shipping_id"].isna().any():

        raise Exception(
            "Shipping lookup failed."
        )

    if orders["location_id"].isna().any():

        raise Exception(
            "Location lookup failed."
        )

    orders = orders[
        [
            "order_id",
            "customer_id",
            "location_id",
            "shipping_id",
            "order_date",
            "ship_date"
        ]
    ]

    insert_dataframe(
        orders,
        "orders",
        connection
    )
# ============================================================
# LOAD ORDER ITEMS
# ============================================================

def load_order_items(data, connection):

    print_section("Loading Order Items")

    insert_dataframe(
        data["order_items"],
        "order_items",
        connection
    )
# ============================================================
# LOAD CHILD TABLES
# ============================================================

def load_child_tables(data, connection):

    load_products(
        data,
        connection
    )

    load_orders(
        data,
        connection
    )

    load_order_items(
        data,
        connection
    )

    print()

    print("Child Tables Loaded Successfully.")
# ============================================================
# COMPLETE LOADING PROCESS
# ============================================================

def load_all_data(folder="../processed"):
    """
    Complete ETL Loading Process
    """

    print("\n")
    print("=" * 70)
    print("STARTING DATABASE LOADING")
    print("=" * 70)

    data = read_normalized_data(folder)

    with engine.begin() as connection:

        try:

            # ------------------------------------------
            # Clean Database
            # ------------------------------------------

            clear_database(connection)

            # ------------------------------------------
            # Parent Tables
            # ------------------------------------------

            load_parent_tables(
                data,
                connection
            )

            # ------------------------------------------
            # Child Tables
            # ------------------------------------------

            load_child_tables(
                data,
                connection
            )

            print("\nDatabase Loaded Successfully!")

        except Exception as e:

            print("\nLoading Failed!")

            print(e)

            raise
# ============================================================
# VERIFY DATABASE
# ============================================================

def verify_database():

    print("\n")
    print("=" * 70)
    print("VERIFYING DATABASE")
    print("=" * 70)

    tables = [
        "customers",
        "locations",
        "shipping_modes",
        "categories",
        "subcategories",
        "products",
        "orders",
        "order_items"

    ]

    with engine.connect() as connection:
        for table in tables:
            query = text(
                f"SELECT COUNT(*) FROM {table};"
            )
            count = connection.execute(query).scalar()
            print(f"{table:<20} {count}")
# ============================================================
# DATABASE SUMMARY
# ============================================================

def database_summary():

    print("\n")
    print("=" * 70)
    print("DATABASE LOADED SUCCESSFULLY")
    print("=" * 70)
    print("""
Tables Loaded:
Customers
Locations
Shipping Modes
Categories
Subcategories
Products
Orders
Order Items
""")