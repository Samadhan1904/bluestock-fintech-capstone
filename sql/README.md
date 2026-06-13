# sql/

- `schema.sql` - Star schema DDL: 1 dimension table (dim_fund) and
  6 fact tables (fact_nav, fact_transactions, fact_performance,
  fact_portfolio, fact_aum, fact_sip_industry) plus indexes.

- `queries.sql` - 10 analytical queries covering AUM rankings,
  monthly NAV trends, SIP YoY growth, transactions by state,
  low expense ratio funds, transaction type splits, top Sharpe
  funds, SIP by age group, monthly NAV trends, and benchmark
  outperformance.

## Recreating the Database

```
python scripts/database_setup.py
```

This reads schema.sql, creates `data/db/bluestock_mf.db`, loads all
cleaned CSVs, and runs queries.sql (results saved to
`reports/query_results_day2.txt`).
