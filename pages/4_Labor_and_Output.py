# -*- coding: utf-8 -*-
"""
pages/4_Labor_and_Output.py
GDP, unemployment, industrial production, and retail vs food inflation.
"""
import streamlit as st
import pandas as pd
from utils.data_loader import load_data, get_date_range
from utils.chart_helpers import make_line_chart, make_area_chart, add_recession_bands, render_summary_stats
from utils.mises_scraper import get_mises_articles, match_articles
from utils.styles import inject_styles
from utils.ticker import render_ticker

st.set_page_config(
    page_title="Labor & Output | Austrian Economics Dashboard",
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
    <h1>Labor &amp; Output</h1>
    <div style="width: 60px; height: 2px; background: #e63946; margin-top: 8px;"></div>
    <p style="color: #888888; font-size: 13px; letter-spacing: 0.04em; margin-top: 12px;">
        GDP growth and unemployment are the headline numbers. Industrial production and real consumption are what's underneath.
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
_export_cols = [c for c in ["DATE", "GDP_Growth_Rate", "Unemployment_Rate",
    "Industrial_Production_Index", "Retail_Sales", "Food_CPI"] if c in dff.columns]
st.download_button("⬇ Export Data (CSV)", data=dff[_export_cols].to_csv(index=False),
    file_name="austrian_dashboard_labor_output.csv", mime="text/csv")

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

# ── Chart 1 — GDP Growth vs Unemployment ──────────────────────────────────────
fig1 = make_line_chart(
    dff,
    series_list=["GDP_Growth_Rate", "Unemployment_Rate"],
    title="GDP Growth Rate vs Unemployment Rate",
    secondary_series=["Unemployment_Rate"],
    x_start=start_date,
    x_end=end_date,
)
add_recession_bands(fig1)
fig1.update_layout(
    yaxis=dict(title="GDP Growth Rate (%)"),
    yaxis2=dict(title="Unemployment Rate (%)"),
)
st.plotly_chart(fig1, use_container_width=True)

with st.expander("📊 What this measures"):
    st.markdown(
        "GDP Growth Rate measures the quarter-over-quarter percentage change in the inflation-adjusted "
        "value of all goods and services produced in the United States. It is the broadest measure of "
        "economic output and the primary benchmark for recession identification — two consecutive "
        "quarters of negative growth is the common rule of thumb, though the NBER uses a broader set "
        "of criteria. The Unemployment Rate measures the percentage of the labor force actively "
        "seeking work but unable to find it. Okun's Law, a well-established empirical relationship, "
        "holds that for every 1% increase in unemployment, GDP falls roughly 2%. The two series "
        "typically move inversely — watching where they diverge is often more informative than "
        "watching either alone."
    )

# ── Chart 2 — Industrial Production Index ─────────────────────────────────────
ipi_df = dff[["DATE", "Industrial_Production_Index"]].dropna().copy()
if len(ipi_df) >= 2:
    fig2 = make_area_chart(
        ipi_df,
        "Industrial_Production_Index",
        "Industrial Production Index (1970–Present)",
        x_start=start_date,
        x_end=end_date,
    )
    add_recession_bands(fig2)
    fig2.update_layout(yaxis=dict(title="Index (2017 = 100)"))
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("📊 What this measures"):
        st.markdown(
            "The Industrial Production Index measures the real output of manufacturing, mining, and "
            "utilities sectors — the physical economy rather than the service and financial economy. It "
            "is produced by the Federal Reserve and is one of the four series the NBER uses to officially "
            "date recessions. Because industrial production responds quickly to changes in demand and "
            "credit conditions, it is considered a coincident indicator — it moves with the business cycle "
            "in real time rather than leading or lagging it. Sustained divergence between industrial "
            "production and GDP can signal an economy increasingly dependent on services and finance "
            "rather than physical output."
        )

# ── Chart 3 — Retail Sales vs Food CPI ────────────────────────────────────────
fig3 = make_line_chart(
    dff,
    series_list=["Retail_Sales", "Food_CPI"],
    title="Retail Sales vs Food CPI",
    secondary_series=["Food_CPI"],
    x_start=start_date,
    x_end=end_date,
)
add_recession_bands(fig3)
fig3.update_layout(
    yaxis=dict(title="Retail Sales (Millions $)"),
    yaxis2=dict(title="Food CPI"),
)
st.plotly_chart(fig3, use_container_width=True)

with st.expander("📊 What this measures"):
    st.markdown(
        "Retail Sales measures the total receipts of retail stores — it is a direct read on consumer "
        "spending, which accounts for roughly 70% of US GDP. It is a nominal figure, meaning it is "
        "not adjusted for inflation. Food CPI measures price changes specifically in food purchased "
        "for home consumption. Because food is a non-discretionary expense with relatively inelastic "
        "demand, food price inflation is particularly burdensome for lower-income households who "
        "spend a larger share of their income on groceries. When retail sales growth is driven by "
        "food price inflation rather than increased consumption volume, it represents spending pressure "
        "rather than economic strength."
    )

# ── Period Statistics ──────────────────────────────────────────────────────────
render_summary_stats(df, ["GDP_Growth_Rate", "Unemployment_Rate", "Industrial_Production_Index",
    "Retail_Sales", "Food_CPI"], start_date, end_date)

# ── Austrian Perspective ───────────────────────────────────────────────────────
with st.expander("📖 Austrian Perspective"):
    st.markdown(
        """
Austrian economists distinguish sharply between genuine economic growth — driven by savings,
capital accumulation, and productive investment — and the statistical growth that can be
manufactured through credit expansion and government spending. GDP, as a measure, cannot
make this distinction. It treats a hospital visit and a factory expansion as equivalent
contributions to output. It counts government expenditure as production regardless of whether
that expenditure generates real value.

The industrial production index offers a more honest look at the physical economy — what is
actually being made. The divergence between financial market performance and industrial output
that becomes visible post-2000, and particularly post-2008, reflects a capital allocation
problem Austrians predicted: cheap credit flows toward financial engineering and asset
speculation rather than productive capacity. An economy that borrows to consume rather than
saves to invest produces the GDP numbers without building the underlying wealth.

The retail sales and food CPI comparison grounds the analysis in household reality. When
food prices outpace income growth — as they did sharply from 2020 onward — nominal retail
sales figures become misleading. Households are spending more dollars to buy fewer goods.
This is not prosperity. It is inflation making itself visible at the grocery store, the most
democratically experienced price in the economy.
        """
    )

    articles = get_mises_articles()
    matched = match_articles(
        articles,
        ["GDP", "unemployment", "industrial production", "economic growth",
            "capital", "labor", "wages", "output", "manufacturing",
            "productivity", "jobs", "recession", "economy", "retail"],
    )
    if matched:
        st.markdown("**Recent Mises Wire — Related Reading:**")
        for article in matched:
            st.markdown(f"📰 [{article['title']}]({article['url']}) — {article['date'][:10]}")
    else:
        st.markdown("*No recent articles matched this topic. Browse [Mises Wire](https://mises.org/wire) for the latest.*")
