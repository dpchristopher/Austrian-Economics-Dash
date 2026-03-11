# -*- coding: utf-8 -*-
"""
pages/1_Money_and_Inflation.py
Money supply expansion, CPI, purchasing power erosion, and PCE.
"""
import streamlit as st
import pandas as pd
from utils.data_loader import load_data, get_date_range
from utils.chart_helpers import make_line_chart, make_area_chart, add_recession_bands, render_summary_stats
from utils.mises_scraper import get_mises_articles, match_articles
from utils.styles import inject_styles
from utils.ticker import render_ticker

st.set_page_config(
    page_title="Money & Inflation | Austrian Economics Dashboard",
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
    <h1>Money &amp; Inflation</h1>
    <div style="width: 60px; height: 2px; background: #e63946; margin-top: 8px;"></div>
    <p style="color: #888888; font-size: 13px; letter-spacing: 0.04em; margin-top: 12px;">
        The Federal Reserve has expanded the money supply by over 2,000% since 1970. Below is what followed.
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
_export_cols = [c for c in ["DATE", "M2_Money_Supply", "CPI_All_Urban_Consumers",
    "PCE_Price_Index", "Federal_Funds_Rate"] if c in dff.columns]
st.download_button("⬇ Export Data (CSV)", data=dff[_export_cols].to_csv(index=False),
    file_name="austrian_dashboard_money_inflation.csv", mime="text/csv")

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

# ── Chart 1 — M2 vs CPI ────────────────────────────────────────────────────────
fig1 = make_line_chart(
    dff,
    series_list=["M2_Money_Supply", "CPI_All_Urban_Consumers"],
    title="M2 Money Supply vs Consumer Price Index",
    secondary_series=["CPI_All_Urban_Consumers"],
    x_start=start_date,
    x_end=end_date,
)
add_recession_bands(fig1)
fig1.update_layout(
    yaxis=dict(title="M2 Money Supply (Billions)"),
    yaxis2=dict(title="CPI"),
)
st.plotly_chart(fig1, use_container_width=True)

with st.expander("📊 What this measures"):
    st.markdown(
        "M2 Money Supply measures the total amount of money in circulation including cash, checking "
        "deposits, and easily convertible near-money assets like savings accounts and money market funds. "
        "It is one of the Federal Reserve's primary indicators of monetary conditions. Rapid M2 growth "
        "can signal expansionary monetary policy, while contraction may indicate tightening. The "
        "Consumer Price Index (CPI) measures the average change in prices paid by urban consumers for "
        "a basket of goods and services. It is the most widely cited measure of inflation in the United "
        "States and directly influences Fed policy decisions, Social Security adjustments, and "
        "inflation-linked bond yields. Economists watch the relationship between M2 and CPI to assess "
        "whether monetary expansion is passing through to consumer prices."
    )

# ── Chart 2 — Purchasing Power Erosion ────────────────────────────────────────
cpi_valid = dff[["DATE", "CPI_All_Urban_Consumers"]].dropna()
if len(cpi_valid) >= 2:
    cpi_base = cpi_valid["CPI_All_Urban_Consumers"].iloc[0]
    pp_df = cpi_valid.copy()
    pp_df["Purchasing_Power"] = 100.0 * cpi_base / pp_df["CPI_All_Urban_Consumers"]
    fig2 = make_area_chart(pp_df, "Purchasing_Power", "Purchasing Power of $1 Over Time",
                           x_start=start_date, x_end=end_date)
    add_recession_bands(fig2)
    fig2.update_layout(yaxis=dict(title="Value ($, indexed to 100 at period start)"))
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("📊 What this measures"):
        st.markdown(
            "Purchasing power measures the real value of money — specifically, how much a fixed amount "
            "of currency can actually buy over time. This chart indexes purchasing power to the start of "
            "the selected date range, showing the cumulative erosion caused by inflation. A decline from "
            "1.00 to 0.50 means that $1 at the start of the period buys only what $0.50 could then. "
            "Economists use purchasing power analysis to evaluate the real-world impact of inflation on "
            "households, particularly fixed-income earners and retirees whose nominal income does not "
            "automatically adjust with prices."
        )

# ── Chart 3 — PCE vs Federal Funds Rate ───────────────────────────────────────
fig3 = make_line_chart(
    dff,
    series_list=["Federal_Funds_Rate", "PCE_Price_Index"],
    title="PCE Inflation vs Federal Funds Rate",
    secondary_series=["PCE_Price_Index"],
    x_start=start_date,
    x_end=end_date,
)
add_recession_bands(fig3)
fig3.update_layout(
    yaxis=dict(title="Federal Funds Rate (%)"),
    yaxis2=dict(title="PCE Price Index"),
)
st.plotly_chart(fig3, use_container_width=True)

with st.expander("📊 What this measures"):
    st.markdown(
        "The Personal Consumption Expenditures (PCE) Price Index is the Federal Reserve's preferred "
        "inflation measure over CPI because it accounts for substitution behavior — when consumers "
        "switch to cheaper alternatives as prices rise. The Federal Funds Rate is the interest rate at "
        "which banks lend reserve balances to each other overnight. It is the Fed's primary monetary "
        "policy tool: raising rates slows borrowing and spending to cool inflation, while cutting rates "
        "stimulates economic activity. The relationship between PCE and the Fed Funds Rate reflects the "
        "Fed's reaction function — how aggressively it responds to inflation with rate adjustments."
    )

# ── Period Statistics ──────────────────────────────────────────────────────────
render_summary_stats(df, ["M2_Money_Supply", "CPI_All_Urban_Consumers",
    "PCE_Price_Index", "Federal_Funds_Rate"], start_date, end_date)

# ── Austrian Perspective ───────────────────────────────────────────────────────
with st.expander("📖 Austrian Perspective"):
    st.markdown(
        """
The Austrian theory of money, rooted in Ludwig von Mises' work on the quantity theory and
business cycles, holds that inflation is not a rise in prices — it is an expansion of the money
supply. Price increases are merely the visible symptom. The charts above show the mechanism
clearly: M2 expanded aggressively, particularly post-2008 and again in 2020, and consumer
prices followed with a lag of roughly 12–24 months — exactly as Austrian theory predicts.

The Cantillon Effect explains why this matters beyond the headline CPI number. When new money
enters the economy, it doesn't raise all prices simultaneously. It flows first to those closest
to the money creation — financial institutions, asset markets, government contractors. By the
time it reaches wages and consumer goods, prices have already risen. The result is a silent
redistribution of wealth from savers and wage earners toward asset holders and the politically
connected. The purchasing power chart above is not an abstraction — it represents the real
decline in what an hour of labor can buy.

The Federal Reserve's dual mandate — price stability and maximum employment — creates a
structural tension that Austrians argue is irresolvable. Suppressing rates to stimulate
employment requires money expansion, which produces inflation, which then requires rate hikes
to suppress — a cycle that never restores the purchasing power lost in each iteration. Each
trough in real purchasing power since 1970 sits lower than the last.
        """
    )

    articles = get_mises_articles()
    matched = match_articles(
        articles,
        ["inflation", "money supply", "cantillon", "federal reserve",
            "purchasing power", "monetary policy", "currency", "prices",
            "CPI", "deflation", "money printing", "quantitative easing",
            "QE", "dollar", "debasement", "M2"],
    )
    if matched:
        st.markdown("**Recent Mises Wire — Related Reading:**")
        for article in matched:
            st.markdown(f"📰 [{article['title']}]({article['url']}) — {article['date'][:10]}")
    else:
        st.markdown("*No recent articles matched this topic. Browse [Mises Wire](https://mises.org/wire) for the latest.*")
