# Bluestock Fintech — Data Dictionary

Day 2 | 07 June 2026

---

## dim_fund
Master list of all 40 mutual fund schemes.

| Column | Type | Description |
|--------|------|-------------|
| amfi_code | INTEGER | Unique AMFI scheme code, primary key |
| fund_house | TEXT | AMC name e.g. SBI Mutual Fund |
| scheme_name | TEXT | Full official scheme name |
| category | TEXT | Equity / Debt / Hybrid |
| sub_category | TEXT | Large Cap / Mid Cap / Small Cap etc. |
| plan | TEXT | Direct or Regular |
| benchmark | TEXT | Index the fund compares against |
| expense_ratio_pct | REAL | Annual AMC fee between 0.1 and 2.5 percent |
| risk_category | TEXT | SEBI risk level Low/Moderate/High/Very High |

## fact_nav
Daily NAV history for all 40 funds. Around 46,000 rows.

| Column | Type | Description |
|--------|------|-------------|
| amfi_code | INTEGER | Links to dim_fund |
| nav_date | TEXT | Date in YYYY-MM-DD format |
| nav | REAL | NAV value in rupees |
| daily_return_pct | REAL | Percentage change from previous day |

## fact_transactions
Investor transactions including SIP, Lumpsum and Redemption. Around 32,000 rows.

| Column | Type | Description |
|--------|------|-------------|
| investor_id | TEXT | Unique investor identifier |
| transaction_date | TEXT | Date of transaction |
| amfi_code | INTEGER | Links to dim_fund |
| transaction_type | TEXT | SIP / Lumpsum / Redemption |
| amount_inr | INTEGER | Transaction amount in rupees |
| state | TEXT | Investor home state |
| city_tier | TEXT | T30 top 30 cities or B30 beyond top 30 |
| age_group | TEXT | 18-25 / 26-35 / 36-45 / 46-55 / 56+ |
| kyc_status | TEXT | Verified or Pending |

## fact_performance
Risk and return metrics per fund. One row per scheme.

| Column | Type | Description |
|--------|------|-------------|
| return_1yr_pct | REAL | 1 year return percentage |
| return_3yr_pct | REAL | 3 year CAGR percentage |
| alpha | REAL | Extra return above benchmark, positive means outperformed |
| beta | REAL | Market sensitivity, 1.0 means moves same as Nifty |
| sharpe_ratio | REAL | Return per unit of risk, higher is better |
| max_drawdown_pct | REAL | Worst peak to trough fall, negative value |

---

## Data Sources

- AMFI India: fund master, expense ratios, risk categories
- mfapi.in: historical NAV data
- NSE/BSE: benchmark index prices
- Simulated: investor transaction data using real demographic patterns
