# Bluestock Fintech — Mutual Fund Analytics Capstone

End-to-end Mutual Fund Analytics Platform built as a 7-day capstone
project for Bluestock Fintech Pvt. Ltd. The platform ingests public
AMFI/mfapi.in data, cleans and stores it in a SQLite star schema,
performs EDA and risk/performance analytics, and presents insights
through a 4-page interactive Power BI dashboard.

> All data is sourced from publicly available AMFI India, mfapi.in
> and NSE/BSE information. This project is for educational purposes
> only and does not constitute financial advice.

---

## Project Overview

| | |
|---|---|
| Domain | Mutual Fund / Fintech |
| Schemes tracked | 40 real schemes across 10 AMCs |
| NAV history | ~46,000 rows, Jan 2022 – May 2026 |
| Investor transactions | ~32,778 rows, 5,000 investors |
| Database | SQLite star schema, 79,318 rows total |
| Dashboard | Power BI, 4 pages, slicers on every page |

---

## Folder Structure

```
bluestock-fintech-capstone/
├── data/
│   ├── raw/            - original CSVs + live NAV from mfapi.in
│   ├── processed/      - cleaned CSVs + computed metrics
│   └── db/              - bluestock_mf.db (SQLite, not in git)
├── notebooks/
│   ├── 03_EDA_Analysis.ipynb
│   ├── 04_Performance_Analytics.ipynb
│   └── 05_Advanced_Analytics.ipynb
├── scripts/
│   ├── data_ingestion.py
│   ├── live_nav_fetch.py
│   ├── data_cleaning.py
│   ├── database_setup.py
│   ├── recommender.py
│   ├── generate_report.py
│   └── generate_presentation.py
├── sql/
│   ├── schema.sql
│   └── queries.sql
├── dashboard/
│   ├── bluestock_mf_dashboard.pbix
│   └── Dashboard.pdf
├── reports/
│   ├── Final_Report.pdf
│   ├── Bluestock_MF_Presentation.pptx
│   ├── charts/
│   ├── data_dictionary.md
│   └── data_quality_day1.txt
├── run_pipeline.py
├── requirements.txt
└── README.md
```

Each folder has its own README with more detail.

---

## Setup Instructions

**1. Clone the repository**
```
git clone https://github.com/Samadhan1904/bluestock-fintech-capstone.git
cd bluestock-fintech-capstone
```

**2. Create a virtual environment**
```
python -m venv venv
venv\Scripts\activate          (Windows)
```

**3. Install dependencies**
```
pip install -r requirements.txt
```

---

## How to Run the ETL Pipeline

Run each step individually:
```
python scripts/data_ingestion.py
python scripts/live_nav_fetch.py
python scripts/data_cleaning.py
python scripts/database_setup.py
```

Or run the master pipeline (does all of the above plus reports):
```
python run_pipeline.py
```

This creates:
- Cleaned CSVs in `data/processed/`
- SQLite database at `data/db/bluestock_mf.db`
- Query results in `reports/query_results_day2.txt`
- Data quality report in `reports/data_quality_day1.txt`

---

## How to Run the Analysis Notebooks

```
jupyter notebook --NotebookApp.iopub_data_rate_limit=1.0e10
```

Then open, in order:
1. `notebooks/03_EDA_Analysis.ipynb` — 9 charts covering NAV trends,
   AUM growth, SIP inflows, demographics, geography, correlations,
   sector allocation
2. `notebooks/04_Performance_Analytics.ipynb` — CAGR, Sharpe, Sortino,
   Alpha/Beta, Max Drawdown, Fund Scorecard, benchmark comparison
3. `notebooks/05_Advanced_Analytics.ipynb` — VaR/CVaR, rolling Sharpe,
   cohort analysis, SIP continuity, sector HHI

---

## How to Open the Dashboard

Open `dashboard/bluestock_mf_dashboard.pbix` in **Power BI Desktop**.
It reads from CSVs in `data/processed/` — click **Refresh** if those
files have been regenerated.

A static PDF export is available at `dashboard/Dashboard.pdf` for
viewing without Power BI.

Pages:
1. Industry Overview — KPI cards, AUM trend, AUM by fund house
2. Fund Performance — Return vs Risk scatter, scorecard, NAV trend
3. Investor Analytics — State/age/city-tier breakdowns
4. SIP & Market Trends — SIP inflow trend, category heatmap

---

## How to Run the Fund Recommender

```
python scripts/recommender.py
```

Given an investor's risk appetite (Low / Moderate / High), it returns
the top 3 funds by Sharpe ratio within the matching risk category.

---

## Key Findings (Summary)

- SBI Mutual Fund is the largest AMC (Rs.12.5 lakh crore AUM)
- Monthly SIP inflows grew 169% (Rs.11,517 Cr → Rs.31,002 Cr, 2022-2025)
- Total MF folios nearly doubled (13.26 Cr → 26.12 Cr)
- All 40 funds show positive alpha vs their 3-year benchmark
- Small Cap funds carry the highest tail risk (VaR/CVaR); Liquid funds
  are near risk-free
- 97.8% of frequent SIP investors show gaps >35 days between SIPs
- All equity portfolios have HHI < 2500 (no high concentration risk)

Full details in `reports/Final_Report.pdf`.

---

## Tech Stack

Python 3.11, Pandas, NumPy, Matplotlib, Seaborn, Plotly, SciPy,
SQLAlchemy, SQLite, Jupyter, Power BI Desktop, ReportLab, python-pptx.

---

## Author

Intern — Bluestock Fintech Pvt. Ltd. | June 2026
