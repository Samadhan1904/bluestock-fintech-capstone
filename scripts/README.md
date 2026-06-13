# scripts/

Python scripts that automate the ETL pipeline, analytics, and report
generation for this project.

| Script | Purpose |
|---|---|
| `data_ingestion.py` | Loads all 10 raw CSVs, prints shape/dtypes/head, validates AMFI codes |
| `live_nav_fetch.py` | Fetches live NAV history from mfapi.in for 6 schemes |
| `data_cleaning.py` | Cleans nav_history, transactions, performance + 7 other datasets |
| `database_setup.py` | Builds SQLite DB from schema.sql, loads data, runs 10 queries |
| `recommender.py` | Fund recommendation engine based on risk appetite + Sharpe ratio |
| `generate_report.py` | Builds Final_Report.pdf from processed data and charts |
| `generate_presentation.py` | Builds the 12-slide Bluestock_MF_Presentation.pptx |
| `run_pipeline.py` | Master script - runs the full pipeline end to end |

## How to Run the Full Pipeline

```
python scripts/run_pipeline.py
```
