"""
run_pipeline.py
Bluestock Fintech Capstone Project

Master script - runs the full ETL and analytics pipeline end to end.

Usage:
    python run_pipeline.py

Steps:
    1. Load and explore all 10 raw datasets
    2. Fetch live NAV data from mfapi.in
    3. Clean all datasets
    4. Build SQLite database + run SQL queries
    5. Run fund recommendation engine
    6. Generate Final Report PDF
    7. Generate presentation deck

Note: Days 3, 4 and 6 (EDA, performance metrics, advanced analytics)
are interactive Jupyter notebooks and are not run by this script -
open them directly in notebooks/.
"""

import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STEPS = [
    ("Data Ingestion (Day 1)",        "scripts/data_ingestion.py"),
    ("Live NAV Fetch (Day 1)",        "scripts/live_nav_fetch.py"),
    ("Data Cleaning (Day 2)",         "scripts/data_cleaning.py"),
    ("Database Setup (Day 2)",        "scripts/database_setup.py"),
    ("Fund Recommender (Day 6)",      "scripts/recommender.py"),
    ("Final Report PDF (Day 7)",      "scripts/generate_report.py"),
    ("Presentation Deck (Day 7)",     "scripts/generate_presentation.py"),
]


def run_step(name, script_path):
    print("\n" + "=" * 60)
    print(f"  Running: {name}")
    print("=" * 60)

    full_path = os.path.join(BASE_DIR, script_path)

    if not os.path.exists(full_path):
        print(f"  SKIPPED - script not found: {script_path}")
        return False

    result = subprocess.run([sys.executable, full_path])

    if result.returncode != 0:
        print(f"\n  FAILED: {name} (exit code {result.returncode})")
        return False

    print(f"\n  Done: {name}")
    return True


if __name__ == "__main__":

    print("\nBluestock Fintech - Full Pipeline Run")
    print("This will run all ETL, cleaning, database and report steps.\n")

    results = []
    for name, path in STEPS:
        success = run_step(name, path)
        results.append((name, success))

    print("\n" + "=" * 60)
    print("  Pipeline Summary")
    print("=" * 60)
    for name, success in results:
        status = "OK" if success else "FAILED / SKIPPED"
        print(f"  {name:<35} {status}")

    print("\nNotebooks (run separately in Jupyter):")
    print("  notebooks/03_EDA_Analysis.ipynb")
    print("  notebooks/04_Performance_Analytics.ipynb")
    print("  notebooks/05_Advanced_Analytics.ipynb")
    print()

