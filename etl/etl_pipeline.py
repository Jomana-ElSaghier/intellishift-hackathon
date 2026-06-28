"""
==========================================================
Sales Business Intelligence ETL Pipeline
==========================================================

Pipeline Flow

1. Extract Data
2. Validate Data
3. Transform Data
4. Generate Reports
5. Normalize Data
6. Load Database
7. Verify Database

==========================================================
"""

import time

from extract import extract_data
from validate import validate_data
from transform import transform_data
from reports import (
    generate_business_insights,
    print_business_report,
    save_business_report,
    generate_data_quality_report
)
from normalize import normalize_data
from load import (
    test_connection,
    load_all_data,
    verify_database,
    database_summary
)


# ==========================================================
# PRINT HEADER
# ==========================================================

def print_header():

    print("\n")
    print("=" * 70)
    print(" SALES BUSINESS INTELLIGENCE ETL PIPELINE ")
    print("=" * 70)


# ==========================================================
# PRINT STEP
# ==========================================================

def print_step(step, title):

    print("\n")
    print("-" * 70)
    print(f"[STEP {step}/7] {title}")
    print("-" * 70)


# ==========================================================
# MAIN PIPELINE
# ==========================================================

def run_pipeline():

    start = time.time()
    print_header()

    # ------------------------------------------------------
    # STEP 1
    # ------------------------------------------------------

    print_step(1, "Extracting Data")
    df = extract_data("../Data.csv")
    print("Data Extracted Successfully")

    # ------------------------------------------------------
    # STEP 2
    # ------------------------------------------------------

    print_step(2, "Validating Dataset")
    validate_data(df)
    print("Validation Completed")

    # ------------------------------------------------------
    # STEP 3
    # ------------------------------------------------------

    print_step(3, "Transforming Dataset")
    df = transform_data(df)
    print("✓ Transformation Completed")

    # ------------------------------------------------------
    # STEP 4
    # ------------------------------------------------------
    print_step(4, "Generating Reports")
    insights = generate_business_insights(df)
    print_business_report(insights)
    save_business_report(insights)
    generate_data_quality_report(df)
    
    print("Reports Generated Successfully")

    # ------------------------------------------------------
    # STEP 5
    # ------------------------------------------------------

    print_step(5, "Normalizing Data")
    normalize_data(df)
    print("Normalized CSV Files Created")

    # ------------------------------------------------------
    # STEP 6
    # ------------------------------------------------------

    print_step(6, "Loading PostgreSQL Database")
    test_connection()
    load_all_data()
    print("Database Loaded Successfully")

    # ------------------------------------------------------
    # STEP 7
    # ------------------------------------------------------

    print_step(7, "Verifying Database")
    verify_database()
    database_summary()
    print("Database Verification Completed")

    # ------------------------------------------------------

    end = time.time()

    print("\n")
    print("=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print(f"Execution Time : {round(end-start,2)} seconds")
if __name__ == "__main__":

        run_pipeline()