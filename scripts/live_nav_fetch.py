# live_nav_fetch.py
# Bluestock Fintech Capstone Project
# Day 1 - Tasks 4 & 5: Fetch live NAV data from mfapi.in
# Task 4: HDFC Top 100 Direct (125497)
# Task 5: SBI Bluechip, ICICI Bluechip, Nippon Large Cap, Axis Bluechip, Kotak Bluechip
# Written by: Intern, Bluestock Fintech
# Date: June 2026

import requests
import pandas as pd
import os
import time
from datetime import datetime


# Path setup - same approach as data_ingestion.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(BASE_DIR, "data", "raw")

# mfapi.in is a free public API - no login or API key needed
# Just hit this URL with a scheme code and it returns full NAV history
BASE_URL = "https://api.mfapi.in/mf/"

# Task 4: HDFC Top 100 Direct is the first one we fetch
# Task 5: Then we fetch these 5 schemes
# I kept all 6 together since the logic is identical for all of them
SCHEMES = {
    "HDFC_Top100_Direct" : 125497,   # Task 4
    "SBI_Bluechip"       : 119551,   # Task 5
    "ICICI_Bluechip"     : 120503,   # Task 5
    "Nippon_LargeCap"    : 118632,   # Task 5
    "Axis_Bluechip"      : 119092,   # Task 5
    "Kotak_Bluechip"     : 120841,   # Task 5
}


def fetch_nav(scheme_name, scheme_code):
    # Build the full API URL for this scheme
    # Example: https://api.mfapi.in/mf/125497
    url = f"{BASE_URL}{scheme_code}"

    print(f"\n  Fetching: {scheme_name} (code: {scheme_code})")
    print(f"  URL: {url}")

    try:
        # Make the GET request to the API
        # timeout=15 means give up if server doesn't reply in 15 seconds
        response = requests.get(url, timeout=15)

        # This will raise an error if we got a bad status code like 404 or 500
        # 200 means OK, anything else means something went wrong
        response.raise_for_status()

        # Convert the JSON response to a Python dictionary
        # The response looks like:
        # {
        #   "meta": { "fund_house": "...", "scheme_name": "...", ... },
        #   "data": [ {"date": "04-06-2026", "nav": "892.45"}, ... ]
        # }
        data = response.json()

        # Pull out the fund details from the meta section
        meta         = data.get("meta", {})
        fund_house   = meta.get("fund_house", "Unknown")
        full_name    = meta.get("scheme_name", scheme_name)
        scheme_cat   = meta.get("scheme_category", "Unknown")
        scheme_type  = meta.get("scheme_type", "Unknown")

        print(f"  Fund House : {fund_house}")
        print(f"  Full Name  : {full_name}")
        print(f"  Category   : {scheme_cat}")

        # The actual NAV records are in data["data"]
        # Each record is a dict: {"date": "DD-MM-YYYY", "nav": "123.45"}
        nav_records = data.get("data", [])

        if not nav_records:
            print(f"  No NAV data returned for this scheme - skipping")
            return None

        # Convert the list of dicts into a pandas DataFrame
        df = pd.DataFrame(nav_records)

        # Add extra columns so we know which fund each row belongs to
        # This is useful when we combine all schemes into one file later
        df["scheme_code"] = scheme_code
        df["scheme_name"] = full_name
        df["fund_house"]  = fund_house
        df["category"]    = scheme_cat

        # Fix the date column - it comes as "04-06-2026" (DD-MM-YYYY)
        # We convert it to a proper datetime so we can sort and filter by date
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")

        # Fix the nav column - it comes as a string like "892.4560"
        # We convert it to a float so we can do math with it
        df["nav"] = pd.to_numeric(df["nav"], errors="coerce")

        # Sort oldest to newest - makes more sense for time series data
        df = df.sort_values("date").reset_index(drop=True)

        # Quick summary of what we got
        latest_nav  = df["nav"].iloc[-1]
        latest_date = df["date"].iloc[-1].strftime("%d %b %Y")
        oldest_date = df["date"].iloc[0].strftime("%d %b %Y")

        print(f"  Records    : {len(df):,}")
        print(f"  Date range : {oldest_date} to {latest_date}")
        print(f"  Latest NAV : Rs. {latest_nav:.4f}")

        return df

    except requests.exceptions.ConnectionError:
        # No internet connection or API server is down
        print(f"  Connection error - check your internet and try again")
        return None

    except requests.exceptions.Timeout:
        # Server took too long to respond
        print(f"  Timeout - server did not respond in 15 seconds")
        return None

    except requests.exceptions.HTTPError as e:
        # Bad status code - maybe the scheme code is wrong
        print(f"  HTTP error: {e}")
        return None

    except Exception as e:
        # Catch anything else unexpected
        print(f"  Unexpected error: {type(e).__name__}: {e}")
        return None


def save_csv(df, scheme_name):
    # Save individual scheme data as its own CSV file
    # Filename format: nav_HDFC_Top100_Direct.csv
    filename = f"nav_{scheme_name}.csv"
    filepath = os.path.join(OUTPUT_PATH, filename)

    df.to_csv(filepath, index=False)

    size_kb = os.path.getsize(filepath) / 1024
    print(f"  Saved: {filename} ({size_kb:.1f} KB)")

    return filepath


if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("  Bluestock Fintech - Live NAV Fetcher")
    print("  Source: mfapi.in (free public API, no auth needed)")
    print(f"  Started: {datetime.now().strftime('%d %B %Y %H:%M:%S')}")
    print("=" * 60)

    # Make sure the output folder exists
    os.makedirs(OUTPUT_PATH, exist_ok=True)

    all_dataframes = []
    success        = 0
    failed         = 0

    print(f"\n  Total schemes to fetch: {len(SCHEMES)}")
    print(f"  Saving files to: {OUTPUT_PATH}\n")

    # Go through each scheme one by one
    for scheme_name, scheme_code in SCHEMES.items():

        print("-" * 50)

        df = fetch_nav(scheme_name, scheme_code)

        if df is not None:
            # Save individual CSV for this scheme
            save_csv(df, scheme_name)
            all_dataframes.append(df)
            success += 1
        else:
            print(f"  Skipping {scheme_name} - could not fetch data")
            failed += 1

        # Wait 1 second between requests
        # This is just being polite to the API server
        # Sending too many requests too fast can get you blocked
        time.sleep(1)

    # Combine all schemes into one master CSV
    # This makes it easy to compare funds side by side later
    print("\n" + "-" * 50)
    if all_dataframes:
        print(f"\n  Combining all {len(all_dataframes)} schemes into one file...")

        combined = pd.concat(all_dataframes, ignore_index=True)
        combined_path = os.path.join(OUTPUT_PATH, "all_schemes_nav_live.csv")
        combined.to_csv(combined_path, index=False)

        size_kb = os.path.getsize(combined_path) / 1024
        print(f"  Saved: all_schemes_nav_live.csv ({size_kb:.1f} KB)")
        print(f"  Total records in combined file: {len(combined):,}")

        # Print a quick snapshot of latest NAV for each fund
        # Good sanity check to make sure data looks right
        print(f"\n  Latest NAV Snapshot:")
        print(f"  {'Scheme':<30} {'Latest NAV':>12}  {'Date'}")
        print(f"  {'─'*30} {'─'*12}  {'─'*12}")

        for name in combined["scheme_name"].unique():
            fund_df  = combined[combined["scheme_name"] == name]
            latest   = fund_df.sort_values("date").iloc[-1]
            nav_val  = f"Rs. {latest['nav']:.4f}"
            date_val = latest["date"].strftime("%d %b %Y")
            # Trim long names so the table stays aligned
            short    = name[:28] if len(name) > 28 else name
            print(f"  {short:<30} {nav_val:>12}  {date_val}")

    # Final summary
    print("\n" + "=" * 60)
    print("  Done!")
    print(f"  Successfully fetched : {success} schemes")
    print(f"  Failed               : {failed} schemes")
    print(f"  Files saved in       : data/raw/")
    print(f"  Finished: {datetime.now().strftime('%d %B %Y %H:%M:%S')}")
    print("=" * 60)
    print()
    print("  Files created:")
    print("    nav_HDFC_Top100_Direct.csv")
    print("    nav_SBI_Bluechip.csv")
    print("    nav_ICICI_Bluechip.csv")
    print("    nav_Nippon_LargeCap.csv")
    print("    nav_Axis_Bluechip.csv")
    print("    nav_Kotak_Bluechip.csv")
    print("    all_schemes_nav_live.csv  (all 6 combined)")
    print()
    print("  Next: git add, commit and push - Task 8")
    print()

