# data/

This folder contains all data used in the Bluestock MF Capstone project.

## Structure

- **raw/** - Original provided CSV files (01-10) plus live NAV CSVs
  fetched from mfapi.in on Day 1. These files are never modified.

- **processed/** - Cleaned and derived datasets produced by
  `data_cleaning.py`, `database_setup.py` and the Day 4/6 notebooks.
  Includes clean_*.csv files plus computed metrics
  (returns, CAGR, Sharpe, Sortino, VaR, HHI, fund scorecard etc.)

- **db/** - `bluestock_mf.db` SQLite database (not committed to GitHub,
  see .gitignore). Recreate it by running `scripts/database_setup.py`
  after the schema in `sql/schema.sql`.

## Regenerating

```
python scripts/data_ingestion.py
python scripts/data_cleaning.py
python scripts/database_setup.py
```
