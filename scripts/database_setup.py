"""
database_setup.py
Bluestock Fintech Capstone Project
Day 2 - Creates SQLite database from schema.sql, loads cleaned
CSVs, runs 10 analytical queries, writes data dictionary.
"""
# Bluestock Fintech Capstone
# Day 2 - Tasks 4, 5, 6, 7
# Creates the SQLite database, loads all cleaned data,
# runs 10 analytical queries and writes the data dictionary

import pandas as pd
import sqlite3
import os
from datetime import datetime
from sqlalchemy import create_engine, text


BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH  = os.path.join(BASE_DIR, "data", "processed")
DB_DIR      = os.path.join(BASE_DIR, "data", "db")
SQL_PATH    = os.path.join(BASE_DIR, "sql")
REPORT_PATH = os.path.join(BASE_DIR, "reports")
DB_PATH     = os.path.join(DB_DIR, "bluestock_mf.db")

os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(SQL_PATH, exist_ok=True)
os.makedirs(REPORT_PATH, exist_ok=True)


def setup_database():
    print("\n" + "=" * 60)
    print("  Setting up SQLite database")
    print("=" * 60)

    schema_path = os.path.join(SQL_PATH, "schema.sql")

    if not os.path.exists(schema_path):
        print(f"\n  ERROR: schema.sql not found in sql/ folder")
        print(f"  Please place schema.sql in the sql/ folder first")
        return None

    # create the db file and run schema.sql to build all tables
    conn = sqlite3.connect(DB_PATH)
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

    print(f"\n  Database created: data/db/bluestock_mf.db")
    print(f"  All tables created from schema.sql")

    # sqlalchemy makes it easy to load pandas dataframes into sqlite
    engine = create_engine(f"sqlite:///{DB_PATH}")
    print(f"  SQLAlchemy connection ready")
    return engine


def load_data(engine):
    print(f"\n  Loading cleaned CSVs into database...")
    print(f"\n  {'Table':<22} {'Rows':>8}   File")
    print(f"  {'─'*22} {'─'*8}   {'─'*30}")

    # table name on the left, csv filename on the right
    tables = {
        "dim_fund"          : "clean_fund_master.csv",
        "fact_nav"          : "clean_nav.csv",
        "fact_transactions" : "clean_transactions.csv",
        "fact_performance"  : "clean_performance.csv",
        "fact_portfolio"    : "clean_portfolio_holdings.csv",
        "fact_aum"          : "clean_aum_by_fund_house.csv",
        "fact_sip_industry" : "clean_monthly_sip_inflows.csv",
    }

    for table, csvfile in tables.items():
        path = os.path.join(CLEAN_PATH, csvfile)

        if not os.path.exists(path):
            print(f"  {table:<22} SKIPPED - file not found: {csvfile}")
            continue

        df = pd.read_csv(path)
        df.to_sql(table, con=engine, if_exists="append", index=False)
        print(f"  {table:<22} {len(df):>8,}   {csvfile}")


def verify_database(engine):
    print(f"\n  Verifying row counts in each table...")
    print(f"\n  {'Table':<25} {'Rows':>8}")
    print(f"  {'─'*25} {'─'*8}")

    tables = [
        "dim_fund", "fact_nav", "fact_transactions",
        "fact_performance", "fact_portfolio",
        "fact_aum", "fact_sip_industry"
    ]

    total = 0
    with engine.connect() as conn:
        for t in tables:
            try:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {t}")).fetchone()[0]
                total += count
                print(f"  {t:<25} {count:>8,}")
            except Exception as e:
                print(f"  {t:<25} ERROR: {e}")

    print(f"  {'─'*25} {'─'*8}")
    print(f"  {'TOTAL':<25} {total:>8,}")
    size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
    print(f"\n  Database size: {size_mb:.1f} MB")


def run_queries(engine):
    print("\n" + "=" * 60)
    print("  Task 6 - Running 10 SQL queries")
    print("=" * 60)

    queries = {

        "Q1 - Top 5 funds by AUM": """
            SELECT scheme_name, fund_house, aum_crore, expense_ratio_pct
            FROM fact_performance
            ORDER BY aum_crore DESC
            LIMIT 5
        """,

        "Q2 - Average NAV per month (sample)": """
            SELECT
                d.scheme_name,
                SUBSTR(n.date, 1, 7) as month,
                ROUND(AVG(n.nav), 2) as avg_nav
            FROM fact_nav n
            JOIN dim_fund d ON n.amfi_code = d.amfi_code
            GROUP BY d.scheme_name, month
            ORDER BY d.scheme_name, month
            LIMIT 20
        """,

        "Q3 - SIP inflow year over year": """
            SELECT
                SUBSTR(month, 1, 4) as year,
                SUM(sip_inflow_crore) as total_sip_crore,
                ROUND(AVG(active_sip_accounts_crore), 2) as avg_accounts_crore
            FROM fact_sip_industry
            GROUP BY year
            ORDER BY year
        """,

        "Q4 - Total transactions by state": """
            SELECT
                state,
                COUNT(*) as transactions,
                SUM(amount_inr) as total_invested,
                ROUND(AVG(amount_inr), 0) as avg_amount
            FROM fact_transactions
            GROUP BY state
            ORDER BY total_invested DESC
        """,

        "Q5 - Funds with expense ratio under 1 percent": """
            SELECT scheme_name, fund_house, category, plan, expense_ratio_pct
            FROM dim_fund
            WHERE expense_ratio_pct < 1.0
            ORDER BY expense_ratio_pct ASC
        """,

        "Q6 - SIP vs Lumpsum vs Redemption split": """
            SELECT
                transaction_type,
                COUNT(*) as num_transactions,
                SUM(amount_inr) as total_amount,
                ROUND(AVG(amount_inr), 0) as avg_amount
            FROM fact_transactions
            GROUP BY transaction_type
            ORDER BY total_amount DESC
        """,

        "Q7 - Top 5 funds by Sharpe ratio": """
            SELECT scheme_name, fund_house, sharpe_ratio,
                   return_3yr_pct, risk_grade
            FROM fact_performance
            ORDER BY sharpe_ratio DESC
            LIMIT 5
        """,

        "Q8 - Average SIP amount by age group": """
            SELECT
                age_group,
                COUNT(DISTINCT investor_id) as investors,
                ROUND(AVG(amount_inr), 0) as avg_sip_amount,
                SUM(amount_inr) as total_invested
            FROM fact_transactions
            WHERE transaction_type = 'SIP'
            GROUP BY age_group
            ORDER BY avg_sip_amount DESC
        """,

        "Q9 - Monthly NAV trend for SBI Large Cap": """
            SELECT
                SUBSTR(n.date, 1, 7) as month,
                ROUND(AVG(n.nav), 2) as avg_nav,
                ROUND(MIN(n.nav), 2) as min_nav,
                ROUND(MAX(n.nav), 2) as max_nav
            FROM fact_nav n
            JOIN dim_fund d ON n.amfi_code = d.amfi_code
            WHERE d.fund_house = 'SBI Mutual Fund'
            AND d.sub_category = 'Large Cap'
            GROUP BY month
            ORDER BY month
            LIMIT 24
        """,

        "Q10 - Funds that beat their benchmark (alpha > 0)": """
            SELECT scheme_name, fund_house,
                   return_3yr_pct, benchmark_3yr_pct,
                   alpha, beta, sharpe_ratio
            FROM fact_performance
            WHERE alpha > 0
            ORDER BY alpha DESC
        """,
    }

    results_text = ""

    with engine.connect() as conn:
        for name, sql in queries.items():
            print(f"\n  {'─'*55}")
            print(f"  {name}")
            print(f"  {'─'*55}")
            try:
                df = pd.read_sql_query(sql, conn)
                print(df.to_string(index=False))
                print(f"\n  {len(df)} rows returned")

                results_text += f"\n{'='*55}\n{name}\n{'='*55}\n"
                results_text += df.to_string(index=False)
                results_text += f"\n{len(df)} rows\n"

            except Exception as e:
                print(f"  Query failed: {e}")

    # save queries to sql/queries.sql
    queries_file = os.path.join(SQL_PATH, "queries.sql")
    with open(queries_file, "w") as f:
        f.write("-- queries.sql\n")
        f.write("-- Bluestock Fintech Capstone - Day 2 Task 6\n")
        f.write(f"-- {datetime.now().strftime('%d %B %Y')}\n\n")
        for name, sql in queries.items():
            f.write(f"-- {name}\n")
            f.write(sql.strip() + ";\n\n\n")

    # save results to reports
    results_file = os.path.join(REPORT_PATH, "query_results_day2.txt")
    with open(results_file, "w") as f:
        f.write("Bluestock Fintech - SQL Query Results - Day 2\n")
        f.write(f"{datetime.now().strftime('%d %B %Y %H:%M:%S')}\n")
        f.write(results_text)

    print(f"\n  Saved: sql/queries.sql")
    print(f"  Saved: reports/query_results_day2.txt")


def write_data_dictionary():
    print("\n" + "=" * 60)
    print("  Task 7 - Writing data dictionary")
    print("=" * 60)

    path = os.path.join(REPORT_PATH, "data_dictionary.md")

    with open(path, "w") as f:
        f.write("# Bluestock Fintech — Data Dictionary\n\n")
        f.write(f"Day 2 | {datetime.now().strftime('%d %B %Y')}\n\n")
        f.write("---\n\n")

        f.write("## dim_fund\n")
        f.write("Master list of all 40 mutual fund schemes.\n\n")
        f.write("| Column | Type | Description |\n")
        f.write("|--------|------|-------------|\n")
        f.write("| amfi_code | INTEGER | Unique AMFI scheme code, primary key |\n")
        f.write("| fund_house | TEXT | AMC name e.g. SBI Mutual Fund |\n")
        f.write("| scheme_name | TEXT | Full official scheme name |\n")
        f.write("| category | TEXT | Equity / Debt / Hybrid |\n")
        f.write("| sub_category | TEXT | Large Cap / Mid Cap / Small Cap etc. |\n")
        f.write("| plan | TEXT | Direct or Regular |\n")
        f.write("| benchmark | TEXT | Index the fund compares against |\n")
        f.write("| expense_ratio_pct | REAL | Annual AMC fee between 0.1 and 2.5 percent |\n")
        f.write("| risk_category | TEXT | SEBI risk level Low/Moderate/High/Very High |\n\n")

        f.write("## fact_nav\n")
        f.write("Daily NAV history for all 40 funds. Around 46,000 rows.\n\n")
        f.write("| Column | Type | Description |\n")
        f.write("|--------|------|-------------|\n")
        f.write("| amfi_code | INTEGER | Links to dim_fund |\n")
        f.write("| nav_date | TEXT | Date in YYYY-MM-DD format |\n")
        f.write("| nav | REAL | NAV value in rupees |\n")
        f.write("| daily_return_pct | REAL | Percentage change from previous day |\n\n")

        f.write("## fact_transactions\n")
        f.write("Investor transactions including SIP, Lumpsum and Redemption. Around 32,000 rows.\n\n")
        f.write("| Column | Type | Description |\n")
        f.write("|--------|------|-------------|\n")
        f.write("| investor_id | TEXT | Unique investor identifier |\n")
        f.write("| transaction_date | TEXT | Date of transaction |\n")
        f.write("| amfi_code | INTEGER | Links to dim_fund |\n")
        f.write("| transaction_type | TEXT | SIP / Lumpsum / Redemption |\n")
        f.write("| amount_inr | INTEGER | Transaction amount in rupees |\n")
        f.write("| state | TEXT | Investor home state |\n")
        f.write("| city_tier | TEXT | T30 top 30 cities or B30 beyond top 30 |\n")
        f.write("| age_group | TEXT | 18-25 / 26-35 / 36-45 / 46-55 / 56+ |\n")
        f.write("| kyc_status | TEXT | Verified or Pending |\n\n")

        f.write("## fact_performance\n")
        f.write("Risk and return metrics per fund. One row per scheme.\n\n")
        f.write("| Column | Type | Description |\n")
        f.write("|--------|------|-------------|\n")
        f.write("| return_1yr_pct | REAL | 1 year return percentage |\n")
        f.write("| return_3yr_pct | REAL | 3 year CAGR percentage |\n")
        f.write("| alpha | REAL | Extra return above benchmark, positive means outperformed |\n")
        f.write("| beta | REAL | Market sensitivity, 1.0 means moves same as Nifty |\n")
        f.write("| sharpe_ratio | REAL | Return per unit of risk, higher is better |\n")
        f.write("| max_drawdown_pct | REAL | Worst peak to trough fall, negative value |\n\n")

        f.write("---\n\n")
        f.write("## Data Sources\n\n")
        f.write("- AMFI India: fund master, expense ratios, risk categories\n")
        f.write("- mfapi.in: historical NAV data\n")
        f.write("- NSE/BSE: benchmark index prices\n")
        f.write("- Simulated: investor transaction data using real demographic patterns\n")

    print(f"\n  Saved: reports/data_dictionary.md")


if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("  Bluestock Fintech - Database Setup")
    print("  Day 2 - Tasks 4, 5, 6, 7")
    print(f"  Started: {datetime.now().strftime('%d %B %Y %H:%M:%S')}")
    print("=" * 60)

    engine = setup_database()

    if engine:
        load_data(engine)
        verify_database(engine)
        run_queries(engine)
        write_data_dictionary()

    print("\n" + "=" * 60)
    print("  Done!")
    print("=" * 60)
    print(f"  Database  : data/db/bluestock_mf.db")
    print(f"  Schema    : sql/schema.sql")
    print(f"  Queries   : sql/queries.sql")
    print(f"  Dict      : reports/data_dictionary.md")
    print(f"\n  Next: git add, commit, push - Task 8")
    print(f"  Finished: {datetime.now().strftime('%d %B %Y %H:%M:%S')}")
    print()

