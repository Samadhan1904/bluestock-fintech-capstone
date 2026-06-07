# data_cleaning.py
# Bluestock Fintech Capstone Project
# Day 2 - Tasks 1, 2, 3: Clean all datasets
# Task 1: nav_history.csv
# Task 2: investor_transactions.csv
# Task 3: scheme_performance.csv
# Written by: Intern, Bluestock Fintech
# Date: June 2026

import pandas as pd
import numpy as np
import os
import re
from datetime import datetime


# Path setup - same as Day 1
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH    = os.path.join(BASE_DIR, "data", "raw")
CLEAN_PATH  = os.path.join(BASE_DIR, "data", "processed")
REPORT_PATH = os.path.join(BASE_DIR, "reports")

# Make sure processed folder exists
os.makedirs(CLEAN_PATH, exist_ok=True)
os.makedirs(REPORT_PATH, exist_ok=True)


# ================================================================
# TASK 1 - Clean nav_history.csv
# ================================================================
# NAV data has a few common problems:
# 1. Date column comes as text - needs to be datetime
# 2. Weekends and holidays have no NAV - need forward fill
# 3. Occasional duplicate entries
# 4. Rarely, corrupted rows with NAV = 0 or negative

def clean_nav_history():

    print("\n" + "=" * 60)
    print("  TASK 1 - Cleaning nav_history.csv")
    print("=" * 60)

    # Load the raw file
    filepath = os.path.join(RAW_PATH, "02_nav_history.csv")
    df = pd.read_csv(filepath)

    print(f"\n  Raw data shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"  Columns: {list(df.columns)}")

    # ── Step 1: Convert date from text to datetime ─────────────
    # Right now date is stored as a string like "2022-01-03"
    # We need it as a proper datetime object so we can sort,
    # filter, and do date math with it
    print(f"\n  Step 1: Converting date column to datetime...")
    before_dtype = df["date"].dtype
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    after_dtype = df["date"].dtype
    print(f"    Before: {before_dtype}")
    print(f"    After : {after_dtype}")

    # Check if any dates failed to parse
    bad_dates = df["date"].isna().sum()
    if bad_dates > 0:
        print(f"    WARNING: {bad_dates} dates could not be parsed - dropping them")
        df = df.dropna(subset=["date"])
    else:
        print(f"    All dates parsed successfully")

    # ── Step 2: Sort by amfi_code and date ────────────────────
    # We sort so that when we do forward fill, values flow
    # correctly within each fund's timeline
    # Without sorting, forward fill could mix up different funds
    print(f"\n  Step 2: Sorting by amfi_code and date...")
    df = df.sort_values(["amfi_code", "date"]).reset_index(drop=True)
    print(f"    Sorted - first date: {df['date'].min().date()}")
    print(f"    Sorted - last date : {df['date'].max().date()}")

    # ── Step 3: Remove duplicates ──────────────────────────────
    # A fund can only have one NAV per day
    # If there are duplicate (amfi_code + date) pairs, keep the first one
    print(f"\n  Step 3: Removing duplicate entries...")
    before_count = len(df)
    df = df.drop_duplicates(subset=["amfi_code", "date"], keep="first")
    after_count = len(df)
    removed = before_count - after_count
    if removed > 0:
        print(f"    Removed {removed} duplicate rows")
    else:
        print(f"    No duplicates found - data is clean here")

    # ── Step 4: Forward fill missing NAV values ────────────────
    # Markets are closed on weekends and public holidays
    # On those days there is no NAV published
    # Standard practice is to carry forward the last known NAV
    # We do this per fund (groupby amfi_code) so Fund A's NAV
    # doesn't accidentally fill Fund B's gaps
    print(f"\n  Step 4: Forward filling missing NAV values...")

    # First check how many NAV values are missing
    missing_before = df["nav"].isna().sum()
    print(f"    Missing NAV values before fill: {missing_before}")

    # Forward fill within each fund separately
    df["nav"] = df.groupby("amfi_code")["nav"].transform(
        lambda x: x.ffill()
    )

    missing_after = df["nav"].isna().sum()
    filled = missing_before - missing_after
    print(f"    Missing NAV values after fill : {missing_after}")
    print(f"    Values filled                 : {filled}")

    # ── Step 5: Validate NAV > 0 ──────────────────────────────
    # NAV can never be zero or negative in real life
    # If we find any, something is wrong with that row
    print(f"\n  Step 5: Validating NAV values are greater than 0...")
    invalid_nav = df[df["nav"] <= 0]
    if len(invalid_nav) > 0:
        print(f"    WARNING: Found {len(invalid_nav)} rows with NAV <= 0")
        print(f"    Dropping these rows...")
        df = df[df["nav"] > 0]
    else:
        print(f"    All NAV values are positive - good")

    # ── Step 6: Compute daily return % ────────────────────────
    # daily_return = how much did NAV change from yesterday
    # Formula: (today_nav / yesterday_nav) - 1
    # We compute this per fund so Fund A's first row doesn't
    # use Fund B's last row as "yesterday"
    print(f"\n  Step 6: Computing daily return percentage...")
    df["daily_return_pct"] = df.groupby("amfi_code")["nav"].transform(
        lambda x: x.pct_change() * 100
    )
    # First row for each fund will be NaN since there's no previous day
    # That's expected and fine
    print(f"    Daily returns computed for all funds")
    print(f"    Sample returns (last 5 rows):")
    print(df[["amfi_code", "date", "nav", "daily_return_pct"]].tail().to_string(index=False))

    # ── Step 7: Final check ────────────────────────────────────
    print(f"\n  Step 7: Final validation...")
    print(f"    Final shape          : {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"    Date range           : {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"    Unique funds         : {df['amfi_code'].nunique()}")
    print(f"    NAV range            : {df['nav'].min():.4f} to {df['nav'].max():.4f}")
    print(f"    Any remaining nulls  : {df.isnull().sum().sum()}")

    # ── Save cleaned file ──────────────────────────────────────
    output_path = os.path.join(CLEAN_PATH, "clean_nav.csv")
    df.to_csv(output_path, index=False)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"\n  Saved: data/processed/clean_nav.csv ({size_kb:.1f} KB)")

    return df


# ================================================================
# TASK 2 - Clean investor_transactions.csv
# ================================================================
# Main issues in transaction data:
# 1. transaction_type has inconsistent values (sip, SIP, Sip etc.)
# 2. Some amounts might be zero or negative
# 3. Date format needs fixing
# 4. KYC status should only be Verified or Pending

def clean_investor_transactions():

    print("\n" + "=" * 60)
    print("  TASK 2 - Cleaning investor_transactions.csv")
    print("=" * 60)

    filepath = os.path.join(RAW_PATH, "08_investor_transactions.csv")
    df = pd.read_csv(filepath)

    print(f"\n  Raw data shape: {df.shape[0]:,} rows x {df.shape[1]} columns")

    # ── Step 1: Fix date format ────────────────────────────────
    print(f"\n  Step 1: Converting transaction_date to datetime...")
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    bad = df["transaction_date"].isna().sum()
    if bad > 0:
        print(f"    WARNING: {bad} dates could not be parsed - dropping")
        df = df.dropna(subset=["transaction_date"])
    else:
        print(f"    All dates converted successfully")

    # ── Step 2: Standardise transaction_type ──────────────────
    # In real data you often get the same value written many ways
    # "sip", "SIP", "Sip", "S.I.P" - all mean the same thing
    # We standardise to exactly 3 values: SIP, Lumpsum, Redemption
    print(f"\n  Step 2: Standardising transaction_type values...")
    print(f"    Before standardisation:")
    print(f"    {df['transaction_type'].value_counts().to_dict()}")

    # Strip whitespace and convert to title case first
    df["transaction_type"] = df["transaction_type"].str.strip()

    # Map all variations to standard values
    # .str.lower() makes comparison case-insensitive
    type_mapping = {
        "sip"         : "SIP",
        "s.i.p"       : "SIP",
        "systematic"  : "SIP",
        "lumpsum"     : "Lumpsum",
        "lump sum"    : "Lumpsum",
        "lump-sum"    : "Lumpsum",
        "one time"    : "Lumpsum",
        "onetime"     : "Lumpsum",
        "redemption"  : "Redemption",
        "redeem"      : "Redemption",
        "withdrawal"  : "Redemption",
    }

    # Apply mapping - convert to lowercase first for matching
    df["transaction_type"] = df["transaction_type"].str.lower().map(
        lambda x: next(
            (v for k, v in type_mapping.items() if k in str(x).lower()),
            df.loc[df["transaction_type"].str.lower() == x, "transaction_type"].iloc[0]
            if any(df["transaction_type"].str.lower() == x) else x.title()
        )
    )

    # Simpler approach - just title case whatever is there
    # and then fix specific known variations
    df["transaction_type"] = df["transaction_type"].str.strip().str.title()
    df["transaction_type"] = df["transaction_type"].replace({
        "Sip"        : "SIP",
        "S.I.P"      : "SIP",
        "Lump Sum"   : "Lumpsum",
        "Lump-Sum"   : "Lumpsum",
        "Redeem"     : "Redemption",
        "Withdrawal" : "Redemption",
    })

    print(f"\n    After standardisation:")
    print(f"    {df['transaction_type'].value_counts().to_dict()}")

    # Check for any unexpected values
    valid_types = ["SIP", "Lumpsum", "Redemption"]
    unexpected = df[~df["transaction_type"].isin(valid_types)]
    if len(unexpected) > 0:
        print(f"\n    WARNING: {len(unexpected)} rows have unexpected transaction types:")
        print(f"    {unexpected['transaction_type'].unique()}")
    else:
        print(f"\n    All transaction types are valid")

    # ── Step 3: Validate amount > 0 ───────────────────────────
    # Transaction amount should always be positive
    # Zero or negative amounts are data entry errors
    print(f"\n  Step 3: Validating transaction amounts...")
    invalid_amounts = df[df["amount_inr"] <= 0]
    if len(invalid_amounts) > 0:
        print(f"    WARNING: {len(invalid_amounts)} rows with amount <= 0 - dropping")
        df = df[df["amount_inr"] > 0]
    else:
        print(f"    All amounts are positive - good")

    print(f"    Amount range: Rs.{df['amount_inr'].min():,} to Rs.{df['amount_inr'].max():,}")
    print(f"    Average SIP amount: Rs.{df[df['transaction_type']=='SIP']['amount_inr'].mean():,.0f}")

    # ── Step 4: Check KYC status values ───────────────────────
    # KYC status should only be Verified or Pending
    # Any other value is a data quality issue
    print(f"\n  Step 4: Checking KYC status values...")
    print(f"    KYC status breakdown:")
    print(f"    {df['kyc_status'].value_counts().to_dict()}")

    valid_kyc = ["Verified", "Pending"]
    invalid_kyc = df[~df["kyc_status"].isin(valid_kyc)]
    if len(invalid_kyc) > 0:
        print(f"    WARNING: {len(invalid_kyc)} rows with unexpected KYC status")
        # Standardise casing
        df["kyc_status"] = df["kyc_status"].str.strip().str.title()
    else:
        print(f"    All KYC status values are valid")

    # ── Step 5: Remove duplicates ──────────────────────────────
    print(f"\n  Step 5: Checking for duplicate transactions...")
    before = len(df)
    # A transaction is duplicate if same investor, date, fund, type and amount
    df = df.drop_duplicates(
        subset=["investor_id", "transaction_date", "amfi_code",
                "transaction_type", "amount_inr"],
        keep="first"
    )
    removed = before - len(df)
    if removed > 0:
        print(f"    Removed {removed} duplicate transactions")
    else:
        print(f"    No duplicates found")

    # ── Step 6: Final check ────────────────────────────────────
    print(f"\n  Step 6: Final validation...")
    print(f"    Final shape         : {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"    Date range          : {df['transaction_date'].min().date()} to {df['transaction_date'].max().date()}")
    print(f"    Unique investors    : {df['investor_id'].nunique():,}")
    print(f"    Transaction types   : {df['transaction_type'].unique().tolist()}")
    print(f"    States covered      : {df['state'].nunique()}")
    print(f"    Any remaining nulls : {df.isnull().sum().sum()}")

    # Save
    output_path = os.path.join(CLEAN_PATH, "clean_transactions.csv")
    df.to_csv(output_path, index=False)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"\n  Saved: data/processed/clean_transactions.csv ({size_kb:.1f} KB)")

    return df


# ================================================================
# TASK 3 - Clean scheme_performance.csv
# ================================================================
# Performance data issues to check:
# 1. Return columns should all be numeric
# 2. Flag funds with negative Sharpe ratio (poor risk-adjusted return)
# 3. Expense ratio should be between 0.1% and 2.5%

def clean_scheme_performance():

    print("\n" + "=" * 60)
    print("  TASK 3 - Cleaning scheme_performance.csv")
    print("=" * 60)

    filepath = os.path.join(RAW_PATH, "07_scheme_performance.csv")
    df = pd.read_csv(filepath)

    print(f"\n  Raw data shape: {df.shape[0]} rows x {df.shape[1]} columns")

    # ── Step 1: Validate return columns are numeric ────────────
    # These columns should all be numbers - if any are text
    # it means something went wrong during data collection
    print(f"\n  Step 1: Validating return columns are numeric...")

    return_cols = [
        "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
        "benchmark_3yr_pct", "alpha", "beta",
        "sharpe_ratio", "sortino_ratio", "std_dev_ann_pct",
        "max_drawdown_pct"
    ]

    for col in return_cols:
        if col in df.columns:
            # Try converting to numeric - non-numeric values become NaN
            before_nulls = df[col].isna().sum()
            df[col] = pd.to_numeric(df[col], errors="coerce")
            after_nulls = df[col].isna().sum()
            new_nulls = after_nulls - before_nulls

            if new_nulls > 0:
                print(f"    WARNING: {col} had {new_nulls} non-numeric values - set to NaN")
            else:
                print(f"    {col:<25} - numeric OK")

    # ── Step 2: Flag negative Sharpe ratios ───────────────────
    # Sharpe ratio measures return per unit of risk
    # Negative Sharpe means the fund performed worse than
    # just keeping money in a bank fixed deposit
    # These funds need to be flagged for review
    print(f"\n  Step 2: Flagging negative Sharpe ratios...")

    if "sharpe_ratio" in df.columns:
        negative_sharpe = df[df["sharpe_ratio"] < 0]
        if len(negative_sharpe) > 0:
            print(f"    Found {len(negative_sharpe)} funds with negative Sharpe ratio:")
            for _, row in negative_sharpe.iterrows():
                print(f"      {row['scheme_name'][:50]} -> Sharpe: {row['sharpe_ratio']}")
        else:
            print(f"    No funds with negative Sharpe ratio - good sign")

        # Add a flag column so we can easily filter these later
        df["poor_risk_adjusted_return"] = df["sharpe_ratio"] < 0
        print(f"    Added 'poor_risk_adjusted_return' flag column")

    # ── Step 3: Validate expense ratio range ──────────────────
    # SEBI rules say expense ratio must be between 0.1% and 2.5%
    # Anything outside this range is a data error
    print(f"\n  Step 3: Checking expense ratio range (0.1% to 2.5%)...")

    if "expense_ratio_pct" in df.columns:
        too_low  = df[df["expense_ratio_pct"] < 0.1]
        too_high = df[df["expense_ratio_pct"] > 2.5]

        if len(too_low) > 0:
            print(f"    WARNING: {len(too_low)} funds with expense ratio below 0.1%:")
            for _, row in too_low.iterrows():
                print(f"      {row['scheme_name'][:50]} -> {row['expense_ratio_pct']}%")
        else:
            print(f"    No funds with expense ratio below 0.1%")

        if len(too_high) > 0:
            print(f"    WARNING: {len(too_high)} funds with expense ratio above 2.5%:")
            for _, row in too_high.iterrows():
                print(f"      {row['scheme_name'][:50]} -> {row['expense_ratio_pct']}%")
        else:
            print(f"    No funds with expense ratio above 2.5%")

        print(f"\n    Expense ratio summary:")
        print(f"      Min : {df['expense_ratio_pct'].min()}%")
        print(f"      Max : {df['expense_ratio_pct'].max()}%")
        print(f"      Avg : {df['expense_ratio_pct'].mean():.3f}%")

    # ── Step 4: Check for missing values ──────────────────────
    print(f"\n  Step 4: Checking for missing values...")
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if missing.empty:
        print(f"    No missing values found")
    else:
        for col, count in missing.items():
            print(f"    {col}: {count} missing")

    # ── Step 5: Final summary ──────────────────────────────────
    print(f"\n  Step 5: Performance data summary...")
    print(f"    Total funds          : {len(df)}")
    print(f"    Avg 1yr return       : {df['return_1yr_pct'].mean():.2f}%")
    print(f"    Avg 3yr return       : {df['return_3yr_pct'].mean():.2f}%")
    print(f"    Avg Sharpe ratio     : {df['sharpe_ratio'].mean():.3f}")
    print(f"    Best Sharpe          : {df['sharpe_ratio'].max():.3f}")
    print(f"    Worst max drawdown   : {df['max_drawdown_pct'].min():.2f}%")
    print(f"    Best max drawdown    : {df['max_drawdown_pct'].max():.2f}%")

    # Save
    output_path = os.path.join(CLEAN_PATH, "clean_performance.csv")
    df.to_csv(output_path, index=False)
    size_kb = os.path.getsize(output_path) / 1024
    print(f"\n  Saved: data/processed/clean_performance.csv ({size_kb:.1f} KB)")

    return df


# ================================================================
# CLEAN REMAINING 7 DATASETS
# ================================================================
# The other 7 datasets don't need heavy cleaning
# but we still standardise dates and save clean versions

def clean_remaining_datasets():

    print("\n" + "=" * 60)
    print("  Cleaning remaining 7 datasets")
    print("=" * 60)

    # List of remaining files with their date columns
    # Format: (short_name, filename, [date_columns])
    remaining = [
        ("fund_master",          "01_fund_master.csv",           ["launch_date"]),
        ("aum_by_fund_house",    "03_aum_by_fund_house.csv",     ["date"]),
        ("monthly_sip_inflows",  "04_monthly_sip_inflows.csv",   ["month"]),
        ("category_inflows",     "05_category_inflows.csv",      ["month"]),
        ("industry_folio_count", "06_industry_folio_count.csv",  ["month"]),
        ("portfolio_holdings",   "09_portfolio_holdings.csv",    ["portfolio_date"]),
        ("benchmark_indices",    "10_benchmark_indices.csv",     ["date"]),
    ]

    for name, filename, date_cols in remaining:
        filepath = os.path.join(RAW_PATH, filename)

        if not os.path.exists(filepath):
            print(f"\n  File not found: {filename} - skipping")
            continue

        df = pd.read_csv(filepath)

        # Convert date columns
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # Remove duplicates
        df = df.drop_duplicates()

        # Save clean version
        output_path = os.path.join(CLEAN_PATH, f"clean_{name}.csv")
        df.to_csv(output_path, index=False)

        print(f"\n  {name}")
        print(f"    Shape : {df.shape[0]:,} rows x {df.shape[1]} columns")
        print(f"    Saved : data/processed/clean_{name}.csv")

    print(f"\n  All remaining datasets cleaned and saved")


# ================================================================
# MAIN
# ================================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("  Bluestock Fintech - Data Cleaning Pipeline")
    print("  Day 2 - Tasks 1, 2, 3")
    print(f"  Started: {datetime.now().strftime('%d %B %Y %H:%M:%S')}")
    print("=" * 60)

    # Run all three main cleaning tasks
    print("\n  Running Task 1 - nav_history...")
    nav_df = clean_nav_history()

    print("\n  Running Task 2 - investor_transactions...")
    tx_df = clean_investor_transactions()

    print("\n  Running Task 3 - scheme_performance...")
    perf_df = clean_scheme_performance()

    # Clean the remaining 7 datasets as well
    print("\n  Cleaning remaining datasets...")
    clean_remaining_datasets()

    # Final summary
    print("\n" + "=" * 60)
    print("  Data Cleaning Complete!")
    print("=" * 60)
    print(f"  clean_nav.csv            : {len(nav_df):,} rows")
    print(f"  clean_transactions.csv   : {len(tx_df):,} rows")
    print(f"  clean_performance.csv    : {len(perf_df):,} rows")
    print(f"\n  All files saved in: data/processed/")
    print(f"\n  Next: run database_setup.py to load data into SQLite")
    print(f"  Finished: {datetime.now().strftime('%d %B %Y %H:%M:%S')}")
    print()

