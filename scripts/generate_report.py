# generate_report.py
# Bluestock Fintech Capstone
# Day 7 - Task 1: Generate the Final Report PDF
#
# Pulls real numbers from our processed CSVs and charts
# and builds a structured 15-20 page report.

import pandas as pd
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH  = os.path.join(BASE_DIR, "data", "processed")
CHART_PATH  = os.path.join(BASE_DIR, "reports", "charts")
REPORT_PATH = os.path.join(BASE_DIR, "reports")

OUTPUT_FILE = os.path.join(REPORT_PATH, "Final_Report.pdf")


# ── Load all the data we'll reference in the report ────────────
fund_df     = pd.read_csv(os.path.join(CLEAN_PATH, "clean_fund_master.csv"))
perf_df     = pd.read_csv(os.path.join(CLEAN_PATH, "clean_performance.csv"))
sip_df      = pd.read_csv(os.path.join(CLEAN_PATH, "clean_monthly_sip_inflows.csv"))
folio_df    = pd.read_csv(os.path.join(CLEAN_PATH, "clean_industry_folio_count.csv"))
aum_df      = pd.read_csv(os.path.join(CLEAN_PATH, "clean_aum_by_fund_house.csv"))
scorecard   = pd.read_csv(os.path.join(CLEAN_PATH, "fund_scorecard.csv"))
var_df      = pd.read_csv(os.path.join(CLEAN_PATH, "var_cvar_report.csv"))
hhi_df      = pd.read_csv(os.path.join(CLEAN_PATH, "sector_hhi.csv"))
tx_df       = pd.read_csv(os.path.join(CLEAN_PATH, "clean_transactions.csv"))


# ── Styles ───────────────────────────────────────────────────────
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "TitleStyle", parent=styles["Title"],
    fontSize=26, textColor=colors.HexColor("#1976D2"), spaceAfter=20
)

h1 = ParagraphStyle(
    "H1", parent=styles["Heading1"],
    fontSize=18, textColor=colors.HexColor("#1976D2"),
    spaceBefore=14, spaceAfter=10
)

h2 = ParagraphStyle(
    "H2", parent=styles["Heading2"],
    fontSize=13, textColor=colors.HexColor("#0D47A1"),
    spaceBefore=10, spaceAfter=6
)

body = ParagraphStyle(
    "Body", parent=styles["BodyText"],
    fontSize=10.5, leading=15, spaceAfter=8
)

caption = ParagraphStyle(
    "Caption", parent=styles["BodyText"],
    fontSize=9, textColor=colors.gray, spaceAfter=14
)


# ── Helper to safely add an image if it exists ──────────────────
def add_chart(elements, filename, caption_text, width=15*cm):
    path = os.path.join(CHART_PATH, filename)
    if os.path.exists(path):
        elements.append(Image(path, width=width, height=width*0.55))
        elements.append(Paragraph(caption_text, caption))
    else:
        elements.append(Paragraph(f"[Chart not found: {filename}]", caption))


# ── Build the document ──────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT_FILE, pagesize=A4,
    topMargin=2*cm, bottomMargin=2*cm,
    leftMargin=2*cm, rightMargin=2*cm
)

elements = []

# ===================================================================
# COVER PAGE
# ===================================================================
elements.append(Spacer(1, 4*cm))
elements.append(Paragraph("Bluestock Fintech", title_style))
elements.append(Paragraph("Mutual Fund Analytics Platform", styles["Title"]))
elements.append(Spacer(1, 1*cm))
elements.append(Paragraph("Final Capstone Project Report", h2))
elements.append(Spacer(1, 2*cm))
elements.append(Paragraph(f"Prepared by: Intern, Bluestock Fintech", body))
elements.append(Paragraph(f"Date: {datetime.now().strftime('%d %B %Y')}", body))
elements.append(Paragraph("Domain: Mutual Fund / Fintech | Duration: 7 Days", body))
elements.append(PageBreak())


# ===================================================================
# SECTION 1: EXECUTIVE SUMMARY
# ===================================================================
elements.append(Paragraph("1. Executive Summary", h1))
elements.append(Paragraph(
    "This project implements an end-to-end Mutual Fund Analytics Platform for "
    "Bluestock Fintech, covering data ingestion, cleaning, database design, "
    "exploratory analysis, performance and risk metrics, an interactive Power BI "
    "dashboard, and advanced investor analytics. The platform tracks 40 real "
    "mutual fund schemes across 10 AMCs, with NAV history spanning January 2022 "
    "to May 2026, alongside industry-wide AUM, SIP and folio growth data sourced "
    "from AMFI India and mfapi.in.", body
))

total_funds = len(fund_df)
total_houses = fund_df["fund_house"].nunique()
total_investors = tx_df["investor_id"].nunique()
total_tx = len(tx_df)

summary_data = [
    ["Metric", "Value"],
    ["Total schemes tracked", str(total_funds)],
    ["Fund houses (AMCs)", str(total_houses)],
    ["NAV history records", "46,000"],
    ["Investor transactions", f"{total_tx:,}"],
    ["Unique investors", f"{total_investors:,}"],
    ["Industry AUM (Dec 2025)", "Rs. 81 lakh crore"],
    ["Monthly SIP inflow (Dec 2025)", "Rs. 31,002 crore"],
    ["Total MF folios (Dec 2025)", "26.12 crore"],
]

t = Table(summary_data, colWidths=[8*cm, 7*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1976D2")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("FONTSIZE", (0,0), (-1,-1), 9.5),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F5F5F5")]),
    ("TOPPADDING", (0,0), (-1,-1), 6),
    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
]))
elements.append(Spacer(1, 0.3*cm))
elements.append(t)
elements.append(PageBreak())


# ===================================================================
# SECTION 2: DATA SOURCES
# ===================================================================
elements.append(Paragraph("2. Data Sources & Datasets", h1))
elements.append(Paragraph(
    "All data used in this project is sourced from publicly available AMFI India "
    "data, the mfapi.in REST API, and NSE/BSE benchmark indices. Ten datasets were "
    "provided covering fund master details, NAV history, AUM by fund house, "
    "monthly SIP inflows, category-wise inflows, industry folio counts, scheme "
    "performance metrics, investor transactions, portfolio holdings, and "
    "benchmark index prices.", body
))

elements.append(Paragraph("2.1 Live API Integration", h2))
elements.append(Paragraph(
    "In addition to the provided CSV files, live NAV data was fetched directly "
    "from the mfapi.in REST API (no authentication required) for 6 key large-cap "
    "schemes including HDFC Top 100, SBI Bluechip, ICICI Bluechip, Nippon Large Cap, "
    "Axis Bluechip and Kotak Bluechip, demonstrating real-time data ingestion "
    "capability.", body
))
elements.append(PageBreak())


# ===================================================================
# SECTION 3: ETL PIPELINE
# ===================================================================
elements.append(Paragraph("3. ETL Pipeline", h1))
elements.append(Paragraph(
    "The ETL pipeline follows the standard Extract, Transform, Load pattern "
    "implemented in Python using Pandas and SQLAlchemy.", body
))

elements.append(Paragraph("3.1 Extract", h2))
elements.append(Paragraph(
    "data_ingestion.py loads all 10 provided CSV datasets, prints shape, data "
    "types and head for each, and flags anomalies such as missing values, "
    "duplicates and date columns stored as text. live_nav_fetch.py calls the "
    "mfapi.in API to fetch live NAV history for 6 schemes and saves them as "
    "raw CSVs.", body
))

elements.append(Paragraph("3.2 Transform", h2))
elements.append(Paragraph(
    "data_cleaning.py converts all date columns to proper datetime objects, "
    "sorts NAV data by fund and date, forward-fills missing NAV values for "
    "weekends and holidays, removes duplicate rows, validates that NAV values "
    "are positive, standardises transaction types to SIP/Lumpsum/Redemption, "
    "validates transaction amounts and expense ratios against SEBI ranges "
    "(0.1% to 2.5%), and computes daily return percentages for every fund.", body
))

elements.append(Paragraph("3.3 Load", h2))
elements.append(Paragraph(
    "database_setup.py creates a SQLite database (bluestock_mf.db) using a "
    "star schema with one dimension table (dim_fund) and six fact tables "
    "(fact_nav, fact_transactions, fact_performance, fact_portfolio, fact_aum, "
    "fact_sip_industry). All cleaned CSVs are loaded via SQLAlchemy, totalling "
    "79,318 rows across the database, with indexes on amfi_code and date columns "
    "for query performance.", body
))
elements.append(PageBreak())


# ===================================================================
# SECTION 4: EDA FINDINGS
# ===================================================================
elements.append(Paragraph("4. Exploratory Data Analysis Findings", h1))
elements.append(Paragraph(
    "Comprehensive EDA was performed across NAV history, AUM growth, SIP "
    "inflows, investor demographics, geography, and portfolio composition. "
    "Nine publication-quality charts were produced covering all required "
    "categories.", body
))

eda_findings = [
    "All 40 equity funds showed consistent upward NAV trends from 2022 to 2026, "
    "with a strong 2023 rally and minor corrections in early 2024.",

    "SBI Mutual Fund is the largest AMC with Rs.12.5 lakh crore AUM as of Dec "
    "2025, roughly 25% larger than the second-largest, ICICI Prudential.",

    "Monthly SIP inflows grew 169% from Rs.11,517 crore (Jan 2022) to Rs.31,002 "
    "crore (Dec 2025), reflecting India's deepening retail equity culture.",

    "Large Cap funds receive the highest and most consistent category inflows, "
    "followed by Flexi Cap and Mid Cap.",

    "The 26-35 age group has the largest number of SIP investors (1,937), while "
    "the 56+ group invests the highest average amount per SIP (Rs.11,575).",

    "Punjab leads total investment by state, closely followed by Tamil Nadu and "
    "Madhya Pradesh, across 12 states covered.",

    "T30 cities contribute the majority of total investment value, though B30 "
    "cities represent a growing share - a key focus area for AMC expansion.",

    "Total MF folios nearly doubled from 13.26 crore (Jan 2022) to 26.12 crore "
    "(Dec 2025), a 97% increase in investor base over 4 years.",

    "Equity funds within the same sub-category show NAV return correlations of "
    "0.85 to 0.95, indicating limited diversification benefit within a category.",

    "Banking and Financial Services is the dominant sector across equity fund "
    "portfolios, typically representing 25-30% of total portfolio weight.",
]

for i, finding in enumerate(eda_findings, 1):
    elements.append(Paragraph(f"<b>{i}.</b> {finding}", body))

elements.append(PageBreak())

elements.append(Paragraph("4.1 NAV Trends - All Equity Funds", h2))
add_chart(elements, "nav_trends_equity.png",
          "Figure 1: Daily NAV for all equity schemes, Jan 2022 - May 2026")

elements.append(Paragraph("4.2 AUM Growth by Fund House", h2))
add_chart(elements, "aum_growth_by_fund_house.png",
          "Figure 2: AUM by fund house, 2022-2025")
elements.append(PageBreak())

elements.append(Paragraph("4.3 SIP Inflow Trend", h2))
add_chart(elements, "sip_inflow_trend.png",
          "Figure 3: Monthly SIP inflows, marking the Rs.31,002 crore all-time high")

elements.append(Paragraph("4.4 Category Inflow Heatmap", h2))
add_chart(elements, "category_inflow_heatmap.png",
          "Figure 4: Category-wise net inflows by month")
elements.append(PageBreak())

elements.append(Paragraph("4.5 Investor Demographics", h2))
add_chart(elements, "investor_demographics.png",
          "Figure 5: Age group distribution and SIP amount by age group")

elements.append(Paragraph("4.6 Geographic Distribution", h2))
add_chart(elements, "geographic_distribution.png",
          "Figure 6: Investment by state and T30 vs B30 split")
elements.append(PageBreak())

elements.append(Paragraph("4.7 Folio Count Growth", h2))
add_chart(elements, "folio_count_growth.png",
          "Figure 7: Total MF folios growth, 2022-2025")

elements.append(Paragraph("4.8 NAV Return Correlation Matrix", h2))
add_chart(elements, "correlation_matrix.png",
          "Figure 8: Correlation of daily returns across 10 selected funds")
elements.append(PageBreak())

elements.append(Paragraph("4.9 Sector Allocation", h2))
add_chart(elements, "sector_allocation_donut.png",
          "Figure 9: Sector weights across all equity fund portfolios")
elements.append(PageBreak())


# ===================================================================
# SECTION 5: PERFORMANCE ANALYSIS
# ===================================================================
elements.append(Paragraph("5. Performance & Risk Analysis", h1))
elements.append(Paragraph(
    "Key performance and risk metrics were computed from NAV history for all "
    "40 funds, including annualised returns, CAGR, Sharpe ratio, Sortino ratio, "
    "Alpha, Beta, and Maximum Drawdown. A composite Fund Scorecard ranks all "
    "funds on a 0-100 scale combining these metrics with weighted importance.", body
))

elements.append(Paragraph("5.1 Top 10 Funds by Composite Score", h2))

top10 = scorecard.head(10)
score_data = [["Rank", "Scheme", "Score", "3yr Ret%", "Sharpe", "Alpha"]]
for _, row in top10.iterrows():
    score_data.append([
        str(row["rank"]),
        row["scheme_name"][:35],
        f"{row['composite_score']:.1f}",
        f"{row['return_3yr_pct']:.2f}",
        f"{row['sharpe_ratio']:.2f}",
        f"{row['alpha']:.2f}",
    ])

t = Table(score_data, colWidths=[1.2*cm, 7*cm, 1.8*cm, 1.8*cm, 1.6*cm, 1.6*cm])
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1976D2")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
    ("FONTSIZE", (0,0), (-1,-1), 8),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F5F5F5")]),
]))
elements.append(t)
elements.append(Spacer(1, 0.3*cm))

elements.append(Paragraph("5.2 Fund Scorecard Visualisation", h2))
add_chart(elements, "fund_scorecard.png",
          "Figure 10: Composite scorecard - top 20 funds")
elements.append(PageBreak())

elements.append(Paragraph("5.3 Benchmark Comparison", h2))
add_chart(elements, "benchmark_chart.png",
          "Figure 11: Top 5 funds vs Nifty 50 and Nifty 100 (normalised to 100)")

elements.append(Paragraph("5.4 Risk Analysis - VaR and CVaR", h2))
elements.append(Paragraph(
    "Historical Value at Risk (95%) and Conditional VaR were computed for all "
    "funds. Small Cap funds (SBI, Axis, ABSL, Nippon, DSP) show the highest "
    "tail risk with worst single-day losses exceeding 4.5%, while Liquid funds "
    "(ICICI Pru Liquid, Kotak Liquid) are the safest with worst-day losses under "
    "0.1%.", body
))
add_chart(elements, "rolling_sharpe_chart.png",
          "Figure 12: Rolling 90-day Sharpe ratio for 5 selected funds")
elements.append(PageBreak())

elements.append(Paragraph("5.5 Sector Concentration (HHI)", h2))
elements.append(Paragraph(
    "Herfindahl-Hirschman Index was computed for all equity fund portfolios. "
    "All 34 funds with portfolio data scored below the High Concentration "
    "threshold of 2500, with Axis Bluechip the most concentrated (HHI 2064, "
    "38% in Infosys) and SBI Small Cap Regular the most diversified (HHI 1073).", body
))
add_chart(elements, "sector_hhi_chart.png",
          "Figure 13: Sector concentration (HHI) by fund")
elements.append(PageBreak())


# ===================================================================
# SECTION 6: DASHBOARD
# ===================================================================
elements.append(Paragraph("6. Interactive Dashboard", h1))
elements.append(Paragraph(
    "A 4-page interactive Power BI dashboard was built covering Industry "
    "Overview, Fund Performance, Investor Analytics, and SIP & Market Trends. "
    "Every page includes at least 2 interactive slicers for filtering by "
    "fund house, category, state, age group, and time period.", body
))

dashboard_pages = [
    ("dashboard_page1_industry.jpeg", "Page 1: Industry Overview - KPI cards for Total AUM, SIP Inflows, Folios, and Schemes; AUM trend and fund house comparison."),
    ("dashboard_page2_performance.jpeg", "Page 2: Fund Performance - Return vs Risk scatter, sortable scorecard, NAV trend with Fund House/Category/Plan slicers."),
    ("dashboard_page3_investor.jpeg", "Page 3: Investor Analytics - State-wise investment, transaction type split, age group SIP analysis, monthly volume trends."),
    ("dashboard_page4_sip_trends.jpeg", "Page 4: SIP & Market Trends - SIP inflow trend, category inflow heatmap, top categories, folio growth."),
]

for img, cap in dashboard_pages:
    add_chart(elements, img, cap)
    elements.append(Spacer(1, 0.2*cm))

elements.append(PageBreak())


# ===================================================================
# SECTION 7: RECOMMENDATIONS
# ===================================================================
elements.append(Paragraph("7. Recommendations", h1))

recommendations = [
    "<b>For Retail Investors:</b> The top-ranked funds on the composite scorecard "
    "(Axis Midcap, HDFC Mid-Cap Opportunities, ABSL Frontline Equity) combine "
    "strong 3-year returns with healthy Sharpe ratios and should be considered "
    "for Moderate-to-High risk portfolios.",

    "<b>For Low-Risk Investors:</b> The recommendation engine identifies ICICI "
    "Pru Liquid and Kotak Liquid as suitable Low-risk options with minimal "
    "drawdown (under 0.2%) and stable, predictable returns near the risk-free rate.",

    "<b>For AMCs - SIP Discipline:</b> 97.8% of frequent SIP investors show "
    "average gaps exceeding 35 days between transactions. AMCs should strengthen "
    "auto-debit mandates and SMS/app reminders to improve SIP regularity and "
    "reduce churn risk.",

    "<b>For AMCs - Geographic Expansion:</b> While T30 cities dominate current "
    "AUM, B30 cities represent an under-penetrated segment. Targeted digital "
    "onboarding campaigns in B30 regions could accelerate folio growth.",

    "<b>For Portfolio Construction:</b> All equity funds analysed show HHI below "
    "the high-concentration threshold (2500), indicating reasonable sector "
    "diversification industry-wide. However, investors holding multiple funds "
    "within the same sub-category (e.g. multiple Large Cap funds) should note "
    "the 0.85-0.95 NAV correlation, which limits true diversification benefit.",
]

for rec in recommendations:
    elements.append(Paragraph(f"&bull; {rec}", body))

elements.append(Spacer(1, 0.3*cm))


# ===================================================================
# SECTION 8: LIMITATIONS
# ===================================================================
elements.append(Paragraph("8. Limitations", h1))

limitations = [
    "Investor transaction data (32,778 records) is synthetically generated, "
    "though anchored to real Indian demographic and geographic distributions. "
    "Findings on investor behaviour should be interpreted as illustrative "
    "rather than exact industry figures.",

    "The Alpha/Beta computed via OLS regression against Nifty 100 showed very "
    "low R-squared values, likely due to date alignment differences between "
    "NAV and benchmark series. The pre-supplied scheme_performance.csv alpha/beta "
    "values were used for the final scorecard as a more reliable source.",

    "NAV history covers approximately 4.3 years (Jan 2022 - May 2026), which "
    "limits the accuracy of 5-year CAGR calculations; 1-year, 3-year and 4-year "
    "windows were used instead.",

    "The dashboard is built in Power BI Desktop and was not published to Power "
    "BI Service due to free-tier workspace limitations; the .pbix file and PDF "
    "export are provided as deliverables instead.",
]

for lim in limitations:
    elements.append(Paragraph(f"&bull; {lim}", body))

elements.append(Spacer(1, 1*cm))
elements.append(Paragraph(
    "All data in this project is sourced from publicly available information "
    "published by AMFI India, NSE, BSE and open APIs (mfapi.in). This project "
    "is for educational purposes only and does not constitute financial advice. "
    "Mutual Fund investments are subject to market risks.", caption
))


# ── Build the PDF ──────────────────────────────────────────────
doc.build(elements)

print(f"Report generated: {OUTPUT_FILE}")
size_kb = os.path.getsize(OUTPUT_FILE) / 1024
print(f"File size: {size_kb:.1f} KB")
