# recommender.py
# Bluestock Fintech Capstone
# Day 6 - Task 5: Simple fund recommendation model
#
# Logic: investor tells us their risk appetite (Low/Moderate/High)
# we filter funds matching that risk grade and return
# the top 3 funds by Sharpe ratio within that risk category

import pandas as pd
import os


BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEAN_PATH = os.path.join(BASE_DIR, "data", "processed")


def load_data():
    # we need fund master for risk_category and
    # sharpe values for ranking within each risk group
    fund_df   = pd.read_csv(os.path.join(CLEAN_PATH, "clean_fund_master.csv"))
    sharpe_df = pd.read_csv(os.path.join(CLEAN_PATH, "sharpe_values.csv"))

    # merge so we have risk_category and sharpe_ratio in one table
    merged = fund_df.merge(
        sharpe_df[["amfi_code", "sharpe_ratio"]],
        on="amfi_code", how="left"
    )
    return merged


def recommend_funds(risk_appetite, data, top_n=3):
    """
    Recommend top funds based on investor risk appetite.

    risk_appetite : "Low", "Moderate", or "High"
    data          : merged fund + sharpe dataframe
    top_n         : how many funds to return (default 3)

    Returns a dataframe with the top funds sorted by sharpe ratio.
    """

    # map investor friendly terms to actual risk_category values
    # in our data risk_category has: Low, Moderate, Moderately High, High, Very High
    risk_map = {
        "Low"      : ["Low"],
        "Moderate" : ["Moderate", "Moderately High"],
        "High"     : ["High", "Very High"]
    }

    if risk_appetite not in risk_map:
        print(f"Invalid risk appetite: {risk_appetite}")
        print("Choose from: Low, Moderate, High")
        return pd.DataFrame()

    target_categories = risk_map[risk_appetite]

    # filter funds matching the risk categories
    matching = data[data["risk_category"].isin(target_categories)].copy()

    if matching.empty:
        print(f"No funds found for risk appetite: {risk_appetite}")
        return pd.DataFrame()

    # sort by sharpe ratio descending and take top N
    top_funds = matching.sort_values("sharpe_ratio", ascending=False).head(top_n)

    return top_funds[["scheme_name", "fund_house", "category",
                       "risk_category", "sharpe_ratio", "expense_ratio_pct"]]


def print_recommendation(risk_appetite, data):
    print("\n" + "=" * 60)
    print(f"  Fund Recommendations for: {risk_appetite} Risk Appetite")
    print("=" * 60)

    recs = recommend_funds(risk_appetite, data)

    if recs.empty:
        print("  No recommendations available")
        return

    for i, row in enumerate(recs.itertuples(), 1):
        print(f"\n  #{i}  {row.scheme_name}")
        print(f"       Fund House     : {row.fund_house}")
        print(f"       Category       : {row.category}")
        print(f"       Risk Grade     : {row.risk_category}")
        print(f"       Sharpe Ratio   : {row.sharpe_ratio}")
        print(f"       Expense Ratio  : {row.expense_ratio_pct}%")


if __name__ == "__main__":

    print("Bluestock Fintech - Fund Recommendation Engine")
    print("Based on Sharpe ratio ranking within risk category\n")

    data = load_data()
    print(f"Loaded {len(data)} funds with risk and sharpe data")

    # show available risk categories in our data
    print(f"\nRisk categories in data: {sorted(data['risk_category'].unique())}")

    # generate recommendations for all 3 risk appetites
    for appetite in ["Low", "Moderate", "High"]:
        print_recommendation(appetite, data)

    print("\n" + "=" * 60)
    print("  Recommendation logic:")
    print("  Low      -> funds with risk_category = Low")
    print("  Moderate -> funds with risk_category = Moderate/Moderately High")
    print("  High     -> funds with risk_category = High/Very High")
    print("  Within each group, top 3 ranked by Sharpe ratio")
    print("=" * 60)

