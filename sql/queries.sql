-- queries.sql
-- Bluestock Fintech Capstone - Day 2 Task 6
-- 07 June 2026

-- Q1 - Top 5 funds by AUM
SELECT scheme_name, fund_house, aum_crore, expense_ratio_pct
            FROM fact_performance
            ORDER BY aum_crore DESC
            LIMIT 5;


-- Q2 - Average NAV per month (sample)
SELECT
                d.scheme_name,
                SUBSTR(n.date, 1, 7) as month,
                ROUND(AVG(n.nav), 2) as avg_nav
            FROM fact_nav n
            JOIN dim_fund d ON n.amfi_code = d.amfi_code
            GROUP BY d.scheme_name, month
            ORDER BY d.scheme_name, month
            LIMIT 20;


-- Q3 - SIP inflow year over year
SELECT
                SUBSTR(month, 1, 4) as year,
                SUM(sip_inflow_crore) as total_sip_crore,
                ROUND(AVG(active_sip_accounts_crore), 2) as avg_accounts_crore
            FROM fact_sip_industry
            GROUP BY year
            ORDER BY year;


-- Q4 - Total transactions by state
SELECT
                state,
                COUNT(*) as transactions,
                SUM(amount_inr) as total_invested,
                ROUND(AVG(amount_inr), 0) as avg_amount
            FROM fact_transactions
            GROUP BY state
            ORDER BY total_invested DESC;


-- Q5 - Funds with expense ratio under 1 percent
SELECT scheme_name, fund_house, category, plan, expense_ratio_pct
            FROM dim_fund
            WHERE expense_ratio_pct < 1.0
            ORDER BY expense_ratio_pct ASC;


-- Q6 - SIP vs Lumpsum vs Redemption split
SELECT
                transaction_type,
                COUNT(*) as num_transactions,
                SUM(amount_inr) as total_amount,
                ROUND(AVG(amount_inr), 0) as avg_amount
            FROM fact_transactions
            GROUP BY transaction_type
            ORDER BY total_amount DESC;


-- Q7 - Top 5 funds by Sharpe ratio
SELECT scheme_name, fund_house, sharpe_ratio,
                   return_3yr_pct, risk_grade
            FROM fact_performance
            ORDER BY sharpe_ratio DESC
            LIMIT 5;


-- Q8 - Average SIP amount by age group
SELECT
                age_group,
                COUNT(DISTINCT investor_id) as investors,
                ROUND(AVG(amount_inr), 0) as avg_sip_amount,
                SUM(amount_inr) as total_invested
            FROM fact_transactions
            WHERE transaction_type = 'SIP'
            GROUP BY age_group
            ORDER BY avg_sip_amount DESC;


-- Q9 - Monthly NAV trend for SBI Large Cap
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
            LIMIT 24;


-- Q10 - Funds that beat their benchmark (alpha > 0)
SELECT scheme_name, fund_house,
                   return_3yr_pct, benchmark_3yr_pct,
                   alpha, beta, sharpe_ratio
            FROM fact_performance
            WHERE alpha > 0
            ORDER BY alpha DESC;


