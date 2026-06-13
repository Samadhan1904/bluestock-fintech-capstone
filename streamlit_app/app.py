# app.py
# Bluestock Fintech - Mutual Fund Analytics Web App
# Bonus Challenge B2 - Streamlit alternative to Power BI
#
# Run locally with: streamlit run streamlit_app/app.py

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os


# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Bluestock MF Analytics",
    page_icon="📊",
    layout="wide"
)

# ─────────────────────────────────────────────────────────────
# THEME TOGGLE - add this near the top of app.py, right after
# st.set_page_config() and before the custom CSS block
# ─────────────────────────────────────────────────────────────

# put the toggle in the sidebar so it doesn't take up main space
with st.sidebar:
    st.markdown("### Display Settings")
    dark_mode = st.toggle("Dark mode", value=False)

# pick colors based on the toggle
if dark_mode:
    bg_color     = "#0E1117"
    card_color   = "#1C2128"
    text_color   = "#FAFAFA"
    border_color = "#30363D"
    accent       = "#4FA8FF"
else:
    bg_color     = "#FFFFFF"
    card_color   = "#EAF4FB"
    text_color   = "#1C2B36"
    border_color = "#D6E4F0"
    accent       = "#2E86DE"

# apply the colors via CSS - this overrides the static config.toml
# at runtime so we can switch live without restarting the app
st.markdown(f"""
<style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}

    .block-container {{ padding-top: 1.5rem; }}

    div[data-testid="stMetric"] {{
        background-color: {card_color};
        border: 1px solid {border_color};
        border-radius: 10px;
        padding: 12px 16px;
    }}

    button[data-baseweb="tab"] {{
        font-size: 16px;
        font-weight: 600;
    }}

    .rec-card {{
        background-color: {card_color};
        border-left: 5px solid {accent};
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        color: {text_color};
    }}

    /* sidebar background */
    section[data-testid="stSidebar"] {{
        background-color: {card_color};
    }}
</style>
""", unsafe_allow_html=True)

# ── Paths ─────────────────────────────────────────────────────
# this file lives in streamlit_app/, so go up one level to project root
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH  = os.path.join(BASE_DIR, "data", "processed")


# ── Load data (cached so it doesn't reload on every click) ─────
@st.cache_data
def load_data():
    fund_df   = pd.read_csv(os.path.join(DATA_PATH, "clean_fund_master.csv"))
    nav_df    = pd.read_csv(os.path.join(DATA_PATH, "clean_nav.csv"), parse_dates=["date"])
    tx_df     = pd.read_csv(os.path.join(DATA_PATH, "clean_transactions.csv"), parse_dates=["transaction_date"])
    sip_df    = pd.read_csv(os.path.join(DATA_PATH, "clean_monthly_sip_inflows.csv"))
    folio_df  = pd.read_csv(os.path.join(DATA_PATH, "clean_industry_folio_count.csv"))
    aum_df    = pd.read_csv(os.path.join(DATA_PATH, "clean_aum_by_fund_house.csv"))
    scorecard = pd.read_csv(os.path.join(DATA_PATH, "fund_scorecard.csv"))
    sharpe_df = pd.read_csv(os.path.join(DATA_PATH, "sharpe_values.csv"))
    var_df    = pd.read_csv(os.path.join(DATA_PATH, "var_cvar_report.csv"))
    return fund_df, nav_df, tx_df, sip_df, folio_df, aum_df, scorecard, sharpe_df, var_df


fund_df, nav_df, tx_df, sip_df, folio_df, aum_df, scorecard, sharpe_df, var_df = load_data()


# ── Sidebar navigation ───────────────────────────────────────
st.sidebar.title("Bluestock Fintech")
st.sidebar.caption("Mutual Fund Analytics Platform")

page = st.sidebar.radio(
    "Go to",
    ["Home", "NAV Trends", "Fund Scorecard", "Performance Details",
     "Investor Analytics", "Fund Recommender"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Data: AMFI India + mfapi.in (public, educational use only)")


# ════════════════════════════════════════════════════════════
# PAGE: HOME
# ════════════════════════════════════════════════════════════
if page == "Home":

    st.title("📊 Bluestock Fintech — Mutual Fund Analytics")
    st.markdown("End-to-end analytics platform covering 40 schemes across 10 AMCs")

    # KPI row - same numbers as Power BI Page 1
    latest_aum   = aum_df.sort_values("date")["aum_lakh_crore"].iloc[-1]
    latest_sip   = sip_df["sip_inflow_crore"].iloc[-1]
    latest_folio = folio_df["total_folios_crore"].iloc[-1]
    total_schemes = fund_df["amfi_code"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Industry AUM", f"₹{latest_aum:.1f} L Cr")
    col2.metric("Latest SIP Inflow", f"₹{latest_sip:,.0f} Cr")
    col3.metric("Total Folios", f"{latest_folio:.2f} Cr")
    col4.metric("Schemes Tracked", total_schemes)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("AUM Growth by Fund House")
        aum_df["year"] = pd.to_datetime(aum_df["date"]).dt.year
        aum_yearly = aum_df.groupby(["fund_house", "year"])["aum_lakh_crore"].mean().reset_index()
        fig = px.bar(aum_yearly, x="fund_house", y="aum_lakh_crore", color="year",
                      barmode="group", labels={"aum_lakh_crore": "AUM (Lakh Cr)"})
        fig.update_layout(xaxis_tickangle=-30, height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Monthly SIP Inflow Trend")
        fig = px.line(sip_df, x="month", y="sip_inflow_crore",
                       labels={"sip_inflow_crore": "SIP Inflow (Cr)"})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Folio Count Growth")
    fig = px.area(folio_df, x="month", y="total_folios_crore",
                   labels={"total_folios_crore": "Total Folios (Cr)"})
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════
# PAGE: NAV TRENDS
# ════════════════════════════════════════════════════════════
elif page == "NAV Trends":

    st.title("📈 NAV Trends")

    # merge nav with fund names
    nav_merged = nav_df.merge(
        fund_df[["amfi_code", "scheme_name", "fund_house", "category", "sub_category"]],
        on="amfi_code", how="left"
    )

    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.selectbox(
            "Category", ["All"] + sorted(nav_merged["category"].dropna().unique().tolist())
        )
    with col2:
        if category_filter != "All":
            sub_options = sorted(nav_merged[nav_merged["category"]==category_filter]["sub_category"].dropna().unique().tolist())
        else:
            sub_options = sorted(nav_merged["sub_category"].dropna().unique().tolist())
        sub_filter = st.selectbox("Sub-Category", ["All"] + sub_options)

    filtered = nav_merged.copy()
    if category_filter != "All":
        filtered = filtered[filtered["category"] == category_filter]
    if sub_filter != "All":
        filtered = filtered[filtered["sub_category"] == sub_filter]

    # let user pick specific funds to plot
    fund_options = sorted(filtered["scheme_name"].unique().tolist())
    selected_funds = st.multiselect(
        "Select funds to plot (leave empty = first 5)",
        fund_options, default=fund_options[:5]
    )

    plot_data = filtered[filtered["scheme_name"].isin(selected_funds)] if selected_funds else filtered[filtered["scheme_name"].isin(fund_options[:5])]

    fig = px.line(plot_data, x="date", y="nav", color="scheme_name",
                   labels={"nav": "NAV (Rs.)", "date": "Date"})
    fig.update_layout(height=550, legend=dict(orientation="h", y=-0.3))
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════
# PAGE: FUND SCORECARD
# ════════════════════════════════════════════════════════════
elif page == "Fund Scorecard":

    st.title("🏆 Fund Scorecard")
    st.caption("Composite score: 30% 3yr return + 25% Sharpe + 20% Alpha + 15% expense ratio + 10% max drawdown")

    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.selectbox(
            "Category", ["All"] + sorted(scorecard["category"].dropna().unique().tolist())
        )
    with col2:
        house_filter = st.selectbox(
            "Fund House", ["All"] + sorted(scorecard["fund_house"].dropna().unique().tolist())
        )

    filtered = scorecard.copy()
    if category_filter != "All":
        filtered = filtered[filtered["category"] == category_filter]
    if house_filter != "All":
        filtered = filtered[filtered["fund_house"] == house_filter]

    filtered = filtered.sort_values("composite_score", ascending=False)

    st.dataframe(
        filtered[["rank", "scheme_name", "fund_house", "category",
                  "composite_score", "return_3yr_pct", "sharpe_ratio",
                  "alpha", "expense_ratio_pct", "max_drawdown_pct"]],
        use_container_width=True, height=500
    )

    st.subheader("Return vs Risk (bubble size = expense ratio)")
    fig = px.scatter(
        filtered, x="max_drawdown_pct", y="return_3yr_pct",
        size="expense_ratio_pct", color="sharpe_ratio",
        hover_name="scheme_name", color_continuous_scale="Viridis",
        labels={"max_drawdown_pct": "Max Drawdown %", "return_3yr_pct": "3yr Return %"}
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════
# PAGE: PERFORMANCE DETAILS
# ════════════════════════════════════════════════════════════
elif page == "Performance Details":

    st.title("📐 Performance Details — Single Fund")

    fund_name = st.selectbox("Select a fund", sorted(scorecard["scheme_name"].unique()))

    fund_row = scorecard[scorecard["scheme_name"] == fund_name].iloc[0]
    sharpe_row = sharpe_df[sharpe_df["scheme_name"] == fund_name]
    var_row = var_df[var_df["scheme_name"] == fund_name]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Composite Score", f"{fund_row['composite_score']:.1f}/100")
    col2.metric("3yr Return", f"{fund_row['return_3yr_pct']:.2f}%")
    col3.metric("Sharpe Ratio", f"{fund_row['sharpe_ratio']:.2f}")
    col4.metric("Alpha", f"{fund_row['alpha']:.2f}")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Expense Ratio", f"{fund_row['expense_ratio_pct']:.2f}%")
    col2.metric("Max Drawdown", f"{fund_row['max_drawdown_pct']:.2f}%")
    if not var_row.empty:
        col3.metric("VaR 95%", f"{var_row['var_95_pct'].values[0]:.2f}%")
        col4.metric("CVaR 95%", f"{var_row['cvar_95_pct'].values[0]:.2f}%")

    st.markdown("---")

    # NAV chart for this fund
    amfi_code = fund_row["amfi_code"]
    fund_nav = nav_df[nav_df["amfi_code"] == amfi_code].sort_values("date")

    st.subheader(f"NAV History — {fund_name}")
    fig = px.line(fund_nav, x="date", y="nav", labels={"nav": "NAV (Rs.)"})
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════
# PAGE: INVESTOR ANALYTICS
# ════════════════════════════════════════════════════════════
elif page == "Investor Analytics":

    st.title("👥 Investor Analytics")

    col1, col2, col3 = st.columns(3)
    with col1:
        state_filter = st.selectbox("State", ["All"] + sorted(tx_df["state"].unique().tolist()))
    with col2:
        age_filter = st.selectbox("Age Group", ["All"] + sorted(tx_df["age_group"].unique().tolist()))
    with col3:
        tier_filter = st.selectbox("City Tier", ["All"] + sorted(tx_df["city_tier"].unique().tolist()))

    filtered = tx_df.copy()
    if state_filter != "All":
        filtered = filtered[filtered["state"] == state_filter]
    if age_filter != "All":
        filtered = filtered[filtered["age_group"] == age_filter]
    if tier_filter != "All":
        filtered = filtered[filtered["city_tier"] == tier_filter]

    col1, col2, col3 = st.columns(3)
    col1.metric("Transactions", f"{len(filtered):,}")
    col2.metric("Total Amount", f"₹{filtered['amount_inr'].sum()/1e7:.1f} Cr")
    col3.metric("Unique Investors", f"{filtered['investor_id'].nunique():,}")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Investment by State")
        state_inv = filtered.groupby("state")["amount_inr"].sum().sort_values().reset_index()
        fig = px.bar(state_inv, x="amount_inr", y="state", orientation="h",
                      labels={"amount_inr": "Total Amount (Rs.)"})
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Transaction Type Split")
        type_split = filtered.groupby("transaction_type")["amount_inr"].sum().reset_index()
        fig = px.pie(type_split, names="transaction_type", values="amount_inr", hole=0.4)
        fig.update_layout(height=450)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Average SIP Amount by Age Group")
    sip_filtered = filtered[filtered["transaction_type"] == "SIP"]
    age_sip = sip_filtered.groupby("age_group")["amount_inr"].mean().reset_index()
    fig = px.bar(age_sip, x="age_group", y="amount_inr",
                  category_orders={"age_group": ["18-25","26-35","36-45","46-55","56+"]},
                  labels={"amount_inr": "Avg SIP Amount (Rs.)"})
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════
# PAGE: FUND RECOMMENDER
# ════════════════════════════════════════════════════════════
elif page == "Fund Recommender":

    st.title("🤖 Fund Recommendation Engine")
    st.caption("Recommends top 3 funds by Sharpe ratio within your risk appetite")

    risk_appetite = st.radio("Select your risk appetite", ["Low", "Moderate", "High"], horizontal=True)

    risk_map = {
        "Low"      : ["Low"],
        "Moderate" : ["Moderate", "Moderately High"],
        "High"     : ["High", "Very High"]
    }

    merged = fund_df.merge(sharpe_df[["amfi_code", "sharpe_ratio"]], on="amfi_code", how="left")
    matching = merged[merged["risk_category"].isin(risk_map[risk_appetite])]
    top3 = matching.sort_values("sharpe_ratio", ascending=False).head(3)

    st.subheader(f"Top 3 Recommendations for {risk_appetite} Risk Appetite")

    for i, row in enumerate(top3.itertuples(), 1):
        with st.container(border=True):
            st.markdown(f"### #{i}  {row.scheme_name}")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Fund House", row.fund_house)
            col2.metric("Sharpe Ratio", f"{row.sharpe_ratio:.2f}")
            col3.metric("Risk Grade", row.risk_category)
            col4.metric("Expense Ratio", f"{row.expense_ratio_pct:.2f}%")


st.markdown("---")
st.caption("Bluestock Fintech | Educational project | Data from AMFI India & mfapi.in")
