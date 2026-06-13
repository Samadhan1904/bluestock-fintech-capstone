# notebooks/

Jupyter notebooks for exploratory and advanced analysis.

| Notebook | Day | Contents |
|---|---|---|
| `03_EDA_Analysis.ipynb` | 3 | 9 charts - NAV trends, AUM growth, SIP inflows, demographics, geography, folio growth, correlation matrix, sector allocation + 10 findings |
| `04_Performance_Analytics.ipynb` | 4 | Daily returns, CAGR, Sharpe, Sortino, Alpha/Beta, Max Drawdown, Fund Scorecard, benchmark comparison |
| `05_Advanced_Analytics.ipynb` | 6 | VaR/CVaR, rolling Sharpe, investor cohort analysis, SIP continuity, sector HHI |

Days 1-2 (ingestion and cleaning) are implemented as `.py` scripts in
`scripts/` rather than notebooks - see `scripts/README.md`.

## Running

Start Jupyter from the project root:
```
jupyter notebook --NotebookApp.iopub_data_rate_limit=1.0e10
```
