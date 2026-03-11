# -*- coding: utf-8 -*-
"""
pages/2_Fed_and_Credit.py
Yield curve, delinquency rates, and high-yield credit spreads.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import load_data, get_date_range
from utils.chart_helpers import make_line_chart, make_area_chart, add_recession_bands, render_summary_stats
from utils.mises_scraper import get_mises_articles, match_articles
from utils.styles import inject_styles
from utils.ticker import render_ticker

st.set_page_config(
    page_title="Fed & Credit | Austrian Economics Dashboard",
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
    <h1>The Fed &amp; Credit</h1>
    <div style="width: 60px; height: 2px; background: #e63946; margin-top: 8px;"></div>
    <p style="color: #888888; font-size: 13px; letter-spacing: 0.04em; margin-top: 12px;">
        Interest rates are the price of time. When that price is set by committee rather than markets, the consequences compound.
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
_export_cols = [c for c in ["DATE", "Treasury_10yr", "Treasury_2yr", "Federal_Funds_Rate",
    "Credit_Card_Delinquency_Rate", "High_Yield_Credit_Spread"] if c in dff.columns]
st.download_button("⬇ Export Data (CSV)", data=dff[_export_cols].to_csv(index=False),
    file_name="austrian_dashboard_fed_credit.csv", mime="text/csv")

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

# ── Chart 1 — Yield Curve ──────────────────────────────────────────────────────
yc_df = dff[["DATE", "Treasury_10yr", "Treasury_2yr"]].dropna(
    subset=["Treasury_10yr", "Treasury_2yr"]
).copy()
if len(yc_df) >= 2:
    yc_df["Yield_Spread"] = yc_df["Treasury_10yr"] - yc_df["Treasury_2yr"]
    fig1 = make_line_chart(
        yc_df,
        series_list=["Yield_Spread", "Treasury_10yr", "Treasury_2yr"],
        title="10yr vs 2yr Treasury + Yield Spread",
        secondary_series=["Yield_Spread"],
        x_start=start_date,
        x_end=end_date,
    )
    fig1.add_trace(
        go.Scatter(
            x=[yc_df["DATE"].min(), yc_df["DATE"].max()],
            y=[0, 0],
            mode="lines",
            line=dict(color="#888888", width=1, dash="dash"),
            yaxis="y2",
            showlegend=False,
            hoverinfo="skip",
        )
    )
    add_recession_bands(fig1)
    fig1.update_layout(
        yaxis=dict(title="Yield (%)"),
        yaxis2=dict(title="Spread (%)"),
    )
    st.plotly_chart(fig1, use_container_width=True)

    with st.expander("📊 What this measures"):
        st.markdown(
            "The yield curve plots interest rates on US Treasury securities across different maturities. "
            "Normally, longer-term bonds yield more than short-term ones to compensate investors for "
            "time risk — producing an upward-sloping curve. When short-term rates exceed long-term rates "
            "the curve inverts, which has preceded every US recession since 1955. The yield spread "
            "(10yr minus 2yr) is the most widely watched inversion indicator. Economists interpret it as "
            "a signal of market expectations: an inverted curve suggests investors expect slower growth "
            "and eventual rate cuts ahead."
        )

# ── Chart 2 — Fed Funds Rate vs Credit Card Delinquency ───────────────────────
delinq_df = dff.dropna(subset=["Credit_Card_Delinquency_Rate"])[
    ["DATE", "Federal_Funds_Rate", "Credit_Card_Delinquency_Rate"]
].copy()
if len(delinq_df) >= 2:
    fig2 = make_line_chart(
        delinq_df,
        series_list=["Federal_Funds_Rate", "Credit_Card_Delinquency_Rate"],
        title="Federal Funds Rate vs Credit Card Delinquency Rate",
        secondary_series=["Credit_Card_Delinquency_Rate"],
        x_start=start_date,
        x_end=end_date,
    )
    add_recession_bands(fig2)
    fig2.update_layout(
        yaxis=dict(title="Federal Funds Rate (%)"),
        yaxis2=dict(title="Delinquency Rate (%)"),
    )
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("📊 What this measures"):
        st.markdown(
            "The Federal Funds Rate directly influences the interest rates consumers pay on credit cards, "
            "auto loans, and adjustable-rate mortgages. Credit card delinquency rate measures the "
            "percentage of credit card balances that are 30 or more days past due. It is a lagging "
            "indicator of consumer financial stress — households typically exhaust savings and reduce "
            "spending before missing payments. Rising delinquency rates signal deteriorating household "
            "balance sheets and often foreshadow broader consumer spending slowdowns. The Fed monitors "
            "this data as part of its financial stability assessment."
        )

# ── Chart 3 — High Yield Credit Spread ────────────────────────────────────────
hy_df = dff[["DATE", "High_Yield_Credit_Spread"]].dropna().copy()
if len(hy_df) >= 2:
    fig3 = make_area_chart(hy_df, "High_Yield_Credit_Spread",
                           "High Yield Credit Spread (Market Stress Indicator)",
                           x_start=start_date, x_end=end_date)
    add_recession_bands(fig3)
    fig3.update_layout(yaxis=dict(title="Spread (%)"))

    spike_windows = {
        "2008 Crisis":    ("2007-01-01", "2010-12-31"),
        "2020 COVID":     ("2019-10-01", "2021-06-30"),
        "2016 Oil Shock": ("2015-01-01", "2017-12-31"),
    }
    for label, (w_start, w_end) in spike_windows.items():
        window = hy_df[
            (hy_df["DATE"] >= w_start)
            & (hy_df["DATE"] <= w_end)
            & (hy_df["High_Yield_Credit_Spread"] > 7.0)
        ]
        if len(window) > 0:
            peak_idx = window["High_Yield_Credit_Spread"].idxmax()
            peak_date = hy_df.loc[peak_idx, "DATE"]
            peak_val = hy_df.loc[peak_idx, "High_Yield_Credit_Spread"]
            fig3.add_annotation(
                x=peak_date,
                y=peak_val,
                text=label,
                showarrow=True,
                arrowhead=2,
                arrowcolor="#888888",
                arrowwidth=1,
                font=dict(color="#888888", size=10),
                bgcolor="#141414",
                bordercolor="#222222",
                borderwidth=1,
                ay=-40,
            )

    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("📊 What this measures"):
        st.markdown(
            "The high yield (or \"junk bond\") credit spread measures the difference in yield between "
            "below-investment-grade corporate bonds and equivalent US Treasury bonds. It represents the "
            "additional return investors demand to hold riskier corporate debt. When spreads widen, it "
            "signals that investors perceive elevated default risk and are demanding more compensation — "
            "a classic indicator of financial market stress. Tight spreads indicate confidence and "
            "risk appetite. Credit spreads are considered a leading indicator because they reflect "
            "forward-looking market sentiment about corporate health and economic conditions."
        )

# ── Period Statistics ──────────────────────────────────────────────────────────
render_summary_stats(df, ["Treasury_10yr", "Treasury_2yr", "Federal_Funds_Rate",
    "Credit_Card_Delinquency_Rate", "High_Yield_Credit_Spread"], start_date, end_date)

# ── Austrian Perspective ───────────────────────────────────────────────────────
with st.expander("📖 Austrian Perspective"):
    st.markdown(
        """
Austrian Business Cycle Theory (ABCT), developed by Mises and expanded by Friedrich Hayek,
offers the most coherent explanation for the boom-bust pattern visible in the charts above.
The theory holds that when central banks artificially suppress interest rates below their
natural market level, they send false signals to entrepreneurs and investors. Credit becomes
cheap, malinvestment follows — resources flow into projects that appear profitable at
artificially low rates but would never be undertaken if borrowing reflected true time preference.

The yield curve inversion visible in 2006–2007 and again in 2022–2023 is not merely a
recession predictor — it is a signal that the market recognizes the distortion. When short-term
rates exceed long-term rates, the market is pricing in the eventual correction that ABCT
predicts must follow the artificial boom. The credit spread chart confirms the timeline:
spreads compress during the Fed-fueled expansions and explode during the corrections.

The credit card delinquency data adds a human dimension to the theoretical framework. The
lag between rate hikes and delinquency peaks — typically 12 to 18 months — reflects the
exhaustion of household buffers built during the cheap money period. Austrians would argue
this is not a failure of capitalism but a predictable consequence of price-fixing in the
credit markets. The pain is real, but its origin is policy, not markets.
        """
    )

    articles = get_mises_articles()
    matched = match_articles(
        articles,
        ["business cycle", "interest rate", "credit", "yield curve",
            "malinvestment", "federal reserve", "central bank", "recession",
            "boom", "bust", "debt", "banking", "monetary", "neutral rate",
            "treasury", "bonds", "delinquency", "lending"],
    )
    if matched:
        st.markdown("**Recent Mises Wire — Related Reading:**")
        for article in matched:
            st.markdown(f"📰 [{article['title']}]({article['url']}) — {article['date'][:10]}")
    else:
        st.markdown("*No recent articles matched this topic. Browse [Mises Wire](https://mises.org/wire) for the latest.*")
