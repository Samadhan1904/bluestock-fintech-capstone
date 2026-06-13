"""
data_ingestion.py
Bluestock Fintech Capstone Project
Day 1 - Loads all 10 CSV datasets, prints shape/dtypes/head,
explores fund master, and validates AMFI codes.
"""
# Bluestock Fintech Capstone Project
# Day 1 - Task 3: Load all 10 CSV datasets and explore them
# Written by: Intern, Bluestock Fintech
# Date: June 2026

import pandas as pd
import numpy as np
import os
from datetime import datetime


# I'm building the path to data/raw/ relative to this script
# so it works on any machine without hardcoding full paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
REPORT_PATH = os.path.join(BASE_DIR, "reports")


# These are the 10 CSV files provided by Bluestock
# Key = short name I'll use in code, Value = actual filename
# If filenames are different, just update the right side
DATASETS = {
    "fund_master"           : "01_fund_master.csv",
    "nav_history"           : "02_nav_history.csv",
    "aum_by_fund_house"     : "03_aum_by_fund_house.csv",
    "monthly_sip_inflows"   : "04_monthly_sip_inflows.csv",
    "category_inflows"      : "05_category_inflows.csv",
    "industry_folio_count"  : "06_industry_folio_count.csv",
    "scheme_performance"    : "07_scheme_performance.csv",
    "investor_transactions" : "08_investor_transactions.csv",
    "portfolio_holdings"    : "09_portfolio_holdings.csv",
    "benchmark_indices"     : "10_benchmark_indices.csv",
}


def load_and_explore(short_name, filename):
    # Build full path to the CSV file
    filepath = os.path.join(RAW_PATH, filename)

    # Check if file actually exists before trying to open it
    # This gives a clear message instead of a confusing error
    if not os.path.exists(filepath):
        print(f"\n  File not found: {filename}")
        print(f"  Please put it in the data/raw/ folder and try again.\n")
        return None, {}

    # Load the CSV into a pandas DataFrame
    # A DataFrame is basically an Excel sheet in Python - rows and columns
    df = pd.read_csv(filepath)

    rows, cols = df.shape

    print("\n" + "=" * 60)
    print(f"  Dataset  : {short_name}")
    print(f"  File     : {filename}")
    print("=" * 60)

    # --- Shape ---
    # shape tells us how big the dataset is
    # (rows, columns) - always in that order
    print(f"\n  Shape: {rows} rows x {cols} columns")

    # --- Column names ---
    print(f"\n  Columns ({cols}):")
    for col in df.columns:
        print(f"    - {col}")

    # --- Data types ---
    # This is important because dates sometimes load as text (object)
    # and we need to fix that later in Day 2 cleaning
    print(f"\n  Data Types:")
    for col, dtype in df.dtypes.items():
        note = ""
        # Flag date columns that loaded as text - common issue
        if "date" in col.lower() and str(dtype) == "object":
            note = "  <-- needs datetime conversion"
        print(f"    {col:<35} {str(dtype)}{note}")

    # --- Head - first 5 rows ---
    # Just to see what the actual data looks like
    print(f"\n  First 5 rows:")
    print(df.head().to_string(index=True))

    # --- Missing values ---
    # isnull() marks missing cells as True
    # sum() counts them per column
    print(f"\n  Missing Values:")
    missing = df.isnull().sum()
    missing_cols = missing[missing > 0]

    if missing_cols.empty:
        print("    No missing values found - data looks clean here")
    else:
        print(f"    Found {missing_cols.sum()} missing values total:")
        for col, count in missing_cols.items():
            pct = round((count / rows) * 100, 2)
            print(f"    {col}: {count} missing ({pct}%)")

    # --- Duplicate rows ---
    # duplicated() returns True for rows that are exact copies
    # of a row that appeared before them
    dupes = df.duplicated().sum()
    print(f"\n  Duplicate Rows: ", end="")
    if dupes == 0:
        print("None found")
    else:
        print(f"{dupes} duplicates found - will remove in Day 2")

    # --- Basic stats for numeric columns ---
    # describe() gives count, mean, min, max etc.
    # Helps spot things like negative NAV values which shouldn't exist
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        print(f"\n  Numeric Summary:")
        print(df[numeric_cols].describe().round(3).to_string())

    # --- Anomaly checks ---
    # These are things that shouldn't happen in financial data
    # but sometimes do due to data entry errors
    print(f"\n  Anomaly Checks:")
    anomalies = []

    # NAV, amounts and ratios should never be negative
    should_be_positive = ["nav", "amount", "aum", "expense_ratio",
                          "sip_inflow", "weight_pct", "amount_inr"]
    for col in df.columns:
        if any(p in col.lower() for p in should_be_positive):
            if pd.api.types.is_numeric_dtype(df[col]):
                neg = (df[col] < 0).sum()
                if neg > 0:
                    msg = f"{col} has {neg} negative values - investigate"
                    anomalies.append(msg)
                    print(f"    WARNING: {msg}")

    # Date columns stored as text need fixing later
    for col in df.columns:
        if "date" in col.lower() and df[col].dtype == object:
            msg = f"{col} is text not datetime - fix in Day 2"
            anomalies.append(msg)
            print(f"    NOTE: {msg}")

    # Columns that are completely empty are useless
    for col in df.columns:
        if df[col].isnull().all():
            msg = f"{col} column is completely empty"
            anomalies.append(msg)
            print(f"    WARNING: {msg}")

    if not anomalies:
        print("    No issues found")

    # Return the dataframe and a summary dict for the report
    summary = {
        "filename"      : filename,
        "rows"          : rows,
        "cols"          : cols,
        "total_missing" : int(missing_cols.sum()),
        "missing_cols"  : list(missing_cols.index),
        "duplicates"    : int(dupes),
        "anomalies"     : anomalies,
    }

    return df, summary


def explore_fund_master(df):
    # This is Task 6 - understanding the fund master dataset specifically
    # Fund master is the most important reference table in the whole project
    print("\n" + "=" * 60)
    print("  Fund Master - Deep Exploration (Task 6)")
    print("=" * 60)

    # Which AMCs (fund houses) are in our data
    if "fund_house" in df.columns:
        print(f"\n  Fund Houses ({df['fund_house'].nunique()} unique):")
        for fh, count in df["fund_house"].value_counts().items():
            print(f"    {fh} - {count} scheme(s)")

    # Broad category: Equity, Debt, Hybrid
    if "category" in df.columns:
        print(f"\n  Categories:")
        for cat, count in df["category"].value_counts().items():
            print(f"    {cat}: {count} schemes")

    # More specific type: Large Cap, Mid Cap, Liquid etc.
    for col in ["sub_category", "scheme_sub_category", "subcategory"]:
        if col in df.columns:
            print(f"\n  Sub-Categories:")
            for sc, count in df[col].value_counts().items():
                print(f"    {sc}: {count} schemes")
            break

    # Risk level assigned by SEBI: Low / Moderate / High / Very High
    for col in ["risk_category", "risk_grade", "risk"]:
        if col in df.columns:
            print(f"\n  Risk Grades:")
            for rg, count in df[col].value_counts().items():
                print(f"    {rg}: {count} schemes")
            break

    # AMFI code is the unique ID for every mutual fund scheme in India
    # Like a PAN number but for mutual funds
    for col in ["amfi_code", "scheme_code"]:
        if col in df.columns:
            print(f"\n  AMFI Code Info:")
            print(f"    Total schemes : {df[col].nunique()}")
            print(f"    Code range    : {df[col].min()} to {df[col].max()}")
            print(f"    Sample codes  : {df[col].head(5).tolist()}")
            break


def validate_amfi_codes(fund_master_df, nav_history_df):
    # Task 7 - making sure every fund in fund_master has NAV data
    # If a fund has no NAV history we can't calculate any returns for it
    print("\n" + "=" * 60)
    print("  AMFI Code Validation (Task 7)")
    print("=" * 60)

    # Find which column has the AMFI code in each dataset
    master_col = None
    nav_col = None

    for col in ["amfi_code", "scheme_code"]:
        if col in fund_master_df.columns:
            master_col = col
        if col in nav_history_df.columns:
            nav_col = col

    if not master_col or not nav_col:
        print("\n  Could not find AMFI code column in one of the datasets.")
        print(f"  fund_master columns : {list(fund_master_df.columns)}")
        print(f"  nav_history columns : {list(nav_history_df.columns)}")
        return {}

    # Convert to sets so we can do set math (intersection, difference)
    master_codes = set(fund_master_df[master_col].astype(str).unique())
    nav_codes    = set(nav_history_df[nav_col].astype(str).unique())

    matched      = master_codes & nav_codes        # in both
    missing_nav  = master_codes - nav_codes        # in master but no NAV data
    orphan_nav   = nav_codes - master_codes        # has NAV but not in master

    coverage = (len(matched) / len(master_codes)) * 100 if master_codes else 0

    print(f"\n  Codes in fund_master   : {len(master_codes)}")
    print(f"  Codes in nav_history   : {len(nav_codes)}")
    print(f"  Matched in both        : {len(matched)}")
    print(f"  Missing NAV data       : {len(missing_nav)}")
    print(f"  Orphan in NAV          : {len(orphan_nav)}")
    print(f"  Coverage               : {coverage:.1f}%")

    if missing_nav:
        print(f"\n  Funds with no NAV history:")
        for code in sorted(missing_nav):
            # Try to find the fund name for context
            mask = fund_master_df[master_col].astype(str) == code
            if "scheme_name" in fund_master_df.columns:
                name = fund_master_df.loc[mask, "scheme_name"].values
                name = name[0] if len(name) > 0 else "Unknown"
            else:
                name = "Unknown"
            print(f"    Code {code} -> {name}")

    if coverage == 100:
        print("\n  All codes matched perfectly - data is consistent")
    elif coverage >= 90:
        print(f"\n  Good coverage at {coverage:.1f}% - minor gaps to investigate")
    else:
        print(f"\n  Low coverage at {coverage:.1f}% - significant data gaps")

    return {
        "master_codes"   : len(master_codes),
        "nav_codes"      : len(nav_codes),
        "matched"        : len(matched),
        "missing_nav"    : len(missing_nav),
        "orphan_nav"     : len(orphan_nav),
        "coverage_pct"   : round(coverage, 2),
        "missing_codes"  : sorted(missing_nav)
    }


def write_quality_report(all_summaries, validation_summary):
    # Save everything we found into a proper report file
    # This becomes our deliverable for Day 1
    os.makedirs(REPORT_PATH, exist_ok=True)
    report_file = os.path.join(REPORT_PATH, "data_quality_day1.txt")

    with open(report_file, "w", encoding="utf-8") as f:

        f.write("=" * 60 + "\n")
        f.write("Bluestock Fintech - Data Quality Report\n")
        f.write("Day 1: Data Ingestion\n")
        f.write(f"Generated: {datetime.now().strftime('%d %B %Y %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

        f.write("SECTION 1 - DATASET OVERVIEW\n")
        f.write("-" * 40 + "\n")
        f.write(f"  {'Dataset':<28} {'Rows':>7} {'Cols':>5} {'Missing':>8} {'Dupes':>6}\n")
        f.write(f"  {'─'*28} {'─'*7} {'─'*5} {'─'*8} {'─'*6}\n")

        total_rows = 0
        for name, s in all_summaries.items():
            f.write(f"  {name:<28} {s['rows']:>7,} {s['cols']:>5} "
                    f"{s['total_missing']:>8,} {s['duplicates']:>6,}\n")
            total_rows += s['rows']

        f.write(f"\n  Total rows across all datasets: {total_rows:,}\n")

        f.write("\n\nSECTION 2 - ANOMALIES FOUND\n")
        f.write("-" * 40 + "\n")
        for name, s in all_summaries.items():
            if s['anomalies']:
                f.write(f"\n  {name}:\n")
                for a in s['anomalies']:
                    f.write(f"    - {a}\n")
            else:
                f.write(f"\n  {name}: No issues found\n")

        f.write("\n\nSECTION 3 - AMFI CODE VALIDATION\n")
        f.write("-" * 40 + "\n")
        if validation_summary:
            f.write(f"  Coverage     : {validation_summary.get('coverage_pct', 0)}%\n")
            f.write(f"  Matched      : {validation_summary.get('matched', 0)}\n")
            f.write(f"  Missing NAV  : {validation_summary.get('missing_nav', 0)}\n")
            missing = validation_summary.get('missing_codes', [])
            if missing:
                f.write(f"  Missing codes: {missing}\n")

        f.write("\n\nSECTION 4 - THINGS TO FIX IN DAY 2\n")
        f.write("-" * 40 + "\n")
        f.write("  1. Convert date columns from text to datetime\n")
        f.write("  2. Forward-fill missing NAV values for weekends and holidays\n")
        f.write("  3. Remove any duplicate rows found\n")
        f.write("  4. Make sure NAV is always greater than 0\n")
        f.write("  5. Check expense_ratio is between 0.1 and 2.5 percent\n")
        f.write("  6. Standardize transaction types to SIP/Lumpsum/Redemption\n")

        f.write("\n" + "=" * 60 + "\n")

    print(f"\n  Report saved to: reports/data_quality_day1.txt")
    return report_file


if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("  Bluestock Fintech - Data Ingestion")
    print("  Day 1, Task 3 - Loading all 10 datasets")
    print(f"  Started: {datetime.now().strftime('%d %B %Y %H:%M:%S')}")
    print("=" * 60)

    # These two dicts will store everything as we go through each file
    dataframes    = {}
    all_summaries = {}

    print(f"\n  Looking for CSV files in: {RAW_PATH}\n")

    # Go through each dataset one by one
    for short_name, filename in DATASETS.items():
        df, summary = load_and_explore(short_name, filename)

        # Only store it if it actually loaded successfully
        if df is not None:
            dataframes[short_name]    = df
            all_summaries[short_name] = summary

    # Quick summary of how many files we managed to load
    print("\n\n" + "=" * 60)
    print("  Loading Summary")
    print("=" * 60)
    print(f"  Successfully loaded : {len(dataframes)} / 10 datasets")

    if len(dataframes) < 10:
        print(f"  Failed to load     : {10 - len(dataframes)} datasets")
        print("  Make sure all CSV files are in the data/raw/ folder")

    total_rows = sum(s["rows"] for s in all_summaries.values())
    print(f"  Total rows loaded  : {total_rows:,}")

    # Task 6 - deeper look at fund_master specifically
    if "fund_master" in dataframes:
        explore_fund_master(dataframes["fund_master"])

    # Task 7 - check AMFI codes are consistent across datasets
    validation_summary = {}
    if "fund_master" in dataframes and "nav_history" in dataframes:
        validation_summary = validate_amfi_codes(
            dataframes["fund_master"],
            dataframes["nav_history"]
        )
    else:
        print("\n  Skipping AMFI validation - need both fund_master and nav_history")

    # Write the quality report
    if all_summaries:
        write_quality_report(all_summaries, validation_summary)

    print("\n" + "=" * 60)
    print("  Done!")
    print(f"  Finished: {datetime.now().strftime('%d %B %Y %H:%M:%S')}")
    print("  Next step: run live_nav_fetch.py for Tasks 4 and 5")
    print("=" * 60 + "\n")