# -*- coding: utf-8 -*-
"""
pages/3_Housing.py
Home prices, affordability, mortgage rates, and lumber PPI.
"""
import streamlit as st
import pandas as pd
from utils.data_loader import load_data, get_date_range
from utils.chart_helpers import make_line_chart, add_recession_bands, render_summary_stats
from utils.mises_scraper import get_mises_articles, match_articles
from utils.styles import inject_styles
from utils.ticker import render_ticker

st.set_page_config(
    page_title="Housing | Austrian Economics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_styles()

# ── Load data ──────────────────────────────────────────────────────────────────
df = load_data()
min_date, max_date = get_date_range(df)
render_ticker(df)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom: 32px;">
    <h1>Housing</h1>
    <div style="width: 60px; height: 2px; background: #e63946; margin-top: 8px;"></div>
    <p style="color: #888888; font-size: 13px; letter-spacing: 0.04em; margin-top: 12px;">
        Home ownership was the foundation of the American middle class. Below is what four decades of monetary policy did to its price.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Date range slider ──────────────────────────────────────────────────────────
date_range = st.slider(
    "Date Range",
    min_value=min_date.to_pydatetime().date(),
    max_value=max_date.to_pydatetime().date(),
    value=(min_date.to_pydatetime().date(), max_date.to_pydatetime().date()),
    format="YYYY-MM",
)
start_date, end_date = date_range
mask = (df["DATE"].dt.date >= start_date) & (df["DATE"].dt.date <= end_date)
dff = df[mask].copy()

# ── Download button ─────────────────────────────────────────────────────────────
st.markdown("""<style>
div.stDownloadButton > button {
    background: transparent; border: 1px solid #333333; color: #888888;
    font-family: 'IBM Plex Mono', monospace; font-size: 11px;
    letter-spacing: 0.08em; padding: 6px 14px; border-radius: 0;
}
div.stDownloadButton > button:hover { border-color: #e63946; color: #e63946; }
</style>""", unsafe_allow_html=True)
_export_cols = [c for c in ["DATE", "Median_Home_Sales_Price", "Case_Shiller_Home_Price_Index",
    "Housing_Affordability_Index", "Mortgage_Rate_30yr", "Lumber_PPI"] if c in dff.columns]
st.download_button("⬇ Export Data (CSV)", data=dff[_export_cols].to_csv(index=False),
    file_name="austrian_dashboard_housing.csv", mime="text/csv")

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

# ── Chart 1 — Median vs Case-Shiller ──────────────────────────────────────────
fig1 = make_line_chart(
    dff,
    series_list=["Median_Home_Sales_Price", "Case_Shiller_Home_Price_Index"],
    title="Median Home Sales Price vs Case-Shiller Index",
    secondary_series=["Case_Shiller_Home_Price_Index"],
    x_start=start_date,
    x_end=end_date,
)
add_recession_bands(fig1)
fig1.update_layout(
    yaxis=dict(title="Median Home Sales Price ($)"),
    yaxis2=dict(title="Case-Shiller Index"),
)
st.plotly_chart(fig1, use_container_width=True)

with st.expander("📊 What this measures"):
    st.markdown(
        "The Median Home Sales Price is the midpoint of all home transaction prices in a given period "
        "— half of homes sold for more, half for less. It is simple and widely cited but sensitive to "
        "the mix of homes being sold. The Case-Shiller Home Price Index tracks repeat sales of the "
        "same properties over time, controlling for changes in housing mix and quality. It is "
        "considered a more accurate measure of pure price appreciation. Economists use both together: "
        "median price for affordability analysis, Case-Shiller for measuring true price inflation in "
        "the housing market."
    )

# ── Chart 2 — Affordability Collapse ──────────────────────────────────────────
fig2 = make_line_chart(
    dff,
    series_list=["Housing_Affordability_Index", "Mortgage_Rate_30yr"],
    title="Housing Affordability Index vs 30yr Mortgage Rate",
    secondary_series=["Mortgage_Rate_30yr"],
    x_start=start_date,
    x_end=end_date,
)
add_recession_bands(fig2)
fig2.update_layout(
    yaxis=dict(title="Affordability Index"),
    yaxis2=dict(title="30yr Mortgage Rate (%)"),
)

afford_window = dff[
    (dff["DATE"] >= "2022-06-01")
    & (dff["DATE"] <= "2023-06-30")
    & dff["Housing_Affordability_Index"].notna()
]
if len(afford_window) > 0:
    min_idx = afford_window["Housing_Affordability_Index"].idxmin()
    ann_date = afford_window.loc[min_idx, "DATE"]
    ann_val = afford_window.loc[min_idx, "Housing_Affordability_Index"]
    fig2.add_annotation(
        x=ann_date,
        y=ann_val,
        text="Rate hikes + elevated prices<br>= historic unaffordability",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#e63946",
        arrowwidth=1,
        font=dict(color="#e63946", size=10),
        bgcolor="#141414",
        bordercolor="#222222",
        borderwidth=1,
        ay=-50,
        ax=20,
    )

st.plotly_chart(fig2, use_container_width=True)

with st.expander("📊 What this measures"):
    st.markdown(
        "The Housing Affordability Index shown here is a ratio of median home sales price to median "
        "household income. A ratio of 3.0 is traditionally considered the upper bound of affordability "
        "— at that level, a household earning the median income can purchase the median home with a "
        "conventional 20% down payment and standard debt-to-income ratios. Ratios above 4.0 or 5.0 "
        "indicate significant affordability stress. The 30-year fixed mortgage rate compounds this "
        "effect: even if home prices stabilize, rising rates increase monthly payments, effectively "
        "raising the real cost of purchase. The combination of elevated prices and high rates produces "
        "affordability conditions worse than either factor alone."
    )

# ── Chart 3 — Home Prices vs Lumber ───────────────────────────────────────────
fig3 = make_line_chart(
    dff,
    series_list=["Median_Home_Sales_Price", "Lumber_PPI"],
    title="Home Prices vs Lumber Producer Price Index",
    secondary_series=["Lumber_PPI"],
    x_start=start_date,
    x_end=end_date,
)
add_recession_bands(fig3)
fig3.update_layout(
    yaxis=dict(title="Median Home Sales Price ($)"),
    yaxis2=dict(title="Lumber PPI"),
)
st.plotly_chart(fig3, use_container_width=True)

with st.expander("📊 What this measures"):
    st.markdown(
        "Lumber is one of the primary input costs in residential construction. The Producer Price Index "
        "(PPI) for lumber measures wholesale price changes at the production level — before costs are "
        "passed through to builders and ultimately to home buyers. Economists and housing analysts "
        "watch lumber PPI as a leading indicator of construction cost pressure. When lumber prices "
        "spike, builders face margin compression that either slows new construction (reducing supply) "
        "or passes through to higher new home prices (inflating the market). The 2020-2021 lumber "
        "spike — driven by pandemic supply chain disruptions combined with a surge in home renovation "
        "demand — is the most dramatic example in the dataset."
    )

# ── Period Statistics ──────────────────────────────────────────────────────────
render_summary_stats(df, ["Median_Home_Sales_Price", "Case_Shiller_Home_Price_Index",
    "Housing_Affordability_Index", "Mortgage_Rate_30yr", "Lumber_PPI"], start_date, end_date)

# ── Austrian Perspective ───────────────────────────────────────────────────────
with st.expander("📖 Austrian Perspective"):
    st.markdown(
        """
Housing represents perhaps the clearest case study in what Austrians call "crack-up boom"
dynamics — a Fed-fueled asset price spiral that systematically prices out the next generation
while enriching those who entered the market before the monetary expansion began. The
mechanism is straightforward: suppressed rates reduce the monthly cost of borrowing, which
increases the price buyers can pay, which inflates asset values, which is then used to justify
further monetary accommodation.

The affordability index tells the story with uncomfortable precision. A ratio of 5.0 means
the median home costs five times the median household income — a threshold most financial
planners consider the outer bound of sustainable purchase. The 2022–2024 period pushed this
ratio to historic highs not seen in the dataset, combining elevated home prices from a decade
of cheap money with the highest mortgage rates since the early 2000s. The worst of both worlds,
paid for by first-time buyers.

Austrians would note that the lumber price chart adds a supply-side dimension often ignored
in the policy debate. Construction cost inflation — driven by the same monetary expansion that
inflated demand — compressed supply responses. Builders couldn't build fast enough at costs
that penciled out, and the gap between demand and supply was filled not by new housing but by
higher prices. The solution to a monetary problem cannot be found in a zoning meeting.
        """
    )

    articles = get_mises_articles()
    matched = match_articles(
        articles,
        ["housing", "real estate", "mortgage", "affordability",
            "asset inflation", "home prices", "rent", "property",
            "construction", "lumber", "bubble", "homeownership"],
    )
    if matched:
        st.markdown("**Recent Mises Wire — Related Reading:**")
        for article in matched:
            st.markdown(f"📰 [{article['title']}]({article['url']}) — {article['date'][:10]}")
    else:
        st.markdown("*No recent articles matched this topic. Browse [Mises Wire](https://mises.org/wire) for the latest.*")
