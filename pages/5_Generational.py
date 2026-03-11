# -*- coding: utf-8 -*-
"""
pages/5_Generational.py
Intergenerational cost of deficit spending, debt, student loans, and affordability.
Two sections: (A) Then vs Now comparison table, (B) time series charts.
"""
import streamlit as st
import pandas as pd
from utils.data_loader import load_data, get_date_range
from utils.chart_helpers import make_line_chart, make_area_chart, add_recession_bands, render_summary_stats
from utils.mises_scraper import get_mises_articles, match_articles
from utils.styles import inject_styles
from utils.ticker import render_ticker

st.set_page_config(
    page_title="Generational Cost | Austrian Economics Dashboard",
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
    <h1>Generational Cost</h1>
    <div style="width: 60px; height: 2px; background: #e63946; margin-top: 8px;"></div>
    <p style="color: #888888; font-size: 13px; letter-spacing: 0.04em; margin-top: 12px;">
        Every dollar of deficit spending is a tax on someone who cannot yet vote. Below is the bill.
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION A — Then vs Now Comparison Table
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    "<h3 style='color:#ffffff; margin-top:8px; margin-bottom:4px;'>"
    "Then vs Now: Entering the Economy</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#888888; font-size:13px; margin-bottom:16px;'>"
    "Boomer Prime = January 1985 &nbsp;|&nbsp; Today = most recent available data"
    "</p>",
    unsafe_allow_html=True,
)

boomer_target = pd.Timestamp("1985-01-01")
boomer_idx = (df["DATE"] - boomer_target).abs().idxmin()
boomer_row = df.loc[boomer_idx]

METRICS = [
    ("Federal Funds Rate",       "Federal_Funds_Rate",          lambda v: f"{v:.2f}%",       "neutral"),
    ("30yr Mortgage Rate",       "Mortgage_Rate_30yr",          lambda v: f"{v:.2f}%",       "higher"),
    ("Home Affordability Index", "Housing_Affordability_Index", lambda v: f"{v:.2f}",        "lower"),
    ("CPI (All Urban)",          "CPI_All_Urban_Consumers",     lambda v: f"{v:.1f}",        "higher"),
    ("Unemployment Rate",        "Unemployment_Rate",           lambda v: f"{v:.1f}%",       "higher"),
    ("Federal Debt Total",       "Federal_Debt_Total",          lambda v: f"${v/1000:.2f}T", "higher"),
    ("M2 Money Supply",          "M2_Money_Supply",             lambda v: f"${v/1000:.2f}T", "higher"),
]


def _get_today_value(col: str):
    series = df[col].dropna()
    return series.iloc[-1] if len(series) > 0 else None


def _today_color(worse_direction: str, today_val, boomer_val) -> str:
    if today_val is None or boomer_val is None or pd.isna(today_val) or pd.isna(boomer_val):
        return "#888888"
    if worse_direction == "higher":
        return "#e63946" if today_val > boomer_val else "#ffffff"
    elif worse_direction == "lower":
        return "#e63946" if today_val < boomer_val else "#ffffff"
    return "#ffffff"


table_rows = ""
for label, col, fmt, worse_dir in METRICS:
    boomer_val = boomer_row.get(col, None)
    today_val = _get_today_value(col)
    boomer_str = fmt(boomer_val) if boomer_val is not None and not pd.isna(boomer_val) else "N/A"
    today_str = fmt(today_val) if today_val is not None and not pd.isna(today_val) else "N/A"
    today_color = _today_color(worse_dir, today_val, boomer_val)
    table_rows += (
        f"<tr>"
        f"<td style='padding:10px 16px;color:#ffffff;border-bottom:1px solid #222222;'>{label}</td>"
        f"<td style='padding:10px 16px;color:#ffffff;border-bottom:1px solid #222222;"
        f"text-align:right;font-family:monospace;'>{boomer_str}</td>"
        f"<td style='padding:10px 16px;color:{today_color};border-bottom:1px solid #222222;"
        f"text-align:right;font-family:monospace;font-weight:700;'>{today_str}</td>"
        f"</tr>"
    )

table_html = f"""
<div style="background:#141414;border:1px solid #222222;border-radius:4px;
            overflow:hidden;margin-bottom:24px;">
  <table style="width:100%;border-collapse:collapse;">
    <thead>
      <tr style="background:#0a0a0a;">
        <th style="padding:10px 16px;color:#888888;text-align:left;font-size:11px;
                   text-transform:uppercase;letter-spacing:1.2px;border-bottom:1px solid #222222;">
          Metric
        </th>
        <th style="padding:10px 16px;color:#888888;text-align:right;font-size:11px;
                   text-transform:uppercase;letter-spacing:1.2px;border-bottom:1px solid #222222;">
          Boomer Prime (Jan 1985)
        </th>
        <th style="padding:10px 16px;color:#888888;text-align:right;font-size:11px;
                   text-transform:uppercase;letter-spacing:1.2px;border-bottom:1px solid #222222;">
          Today
        </th>
      </tr>
    </thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>
</div>
"""
st.markdown(table_html, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION B — Time Series Charts
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<hr style='border-color:#222222;margin:8px 0 20px 0;'>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='color:#ffffff; margin-bottom:4px;'>Time Series</h3>",
    unsafe_allow_html=True,
)

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
_export_cols = [c for c in ["DATE", "Federal_Debt_Total", "Student_Loan_Debt",
    "Housing_Affordability_Index", "Median_Household_Income"] if c in dff.columns]
st.download_button("⬇ Export Data (CSV)", data=dff[_export_cols].to_csv(index=False),
    file_name="austrian_dashboard_generational.csv", mime="text/csv")

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

# ── Chart 1 — Federal Debt Total ──────────────────────────────────────────────
debt_df = dff[["DATE", "Federal_Debt_Total"]].dropna().copy()
if len(debt_df) >= 2:
    fig1 = make_area_chart(debt_df, "Federal_Debt_Total", "Total Federal Debt (Billions)",
                           x_start=start_date, x_end=end_date)
    add_recession_bands(fig1)
    fig1.update_layout(yaxis=dict(title="Billions USD"))

    fiscal_events = [
        ("1981-08-13", "Reagan<br>Tax Cuts"),
        ("2001-06-07", "Bush<br>Tax Cuts"),
        ("2008-10-03", "Financial<br>Crisis"),
        ("2020-03-27", "COVID<br>Stimulus"),
    ]
    for date_str, label in fiscal_events:
        event_ts = pd.Timestamp(date_str)
        if event_ts.date() >= start_date and event_ts.date() <= end_date:
            fig1.add_vline(
                x=date_str,
                line_color="#888888",
                line_dash="dot",
                line_width=1,
            )
            fig1.add_annotation(
                x=date_str,
                y=1.04,
                yref="paper",
                text=label,
                showarrow=False,
                font=dict(color="#888888", size=9),
                bgcolor="#0a0a0a",
                bordercolor="#222222",
                borderwidth=1,
                xanchor="center",
            )

    st.plotly_chart(fig1, use_container_width=True)

    with st.expander("📊 What this measures"):
        st.markdown(
            "Total Federal Debt measures the cumulative amount the US government owes to all creditors "
            "— domestic and foreign — as a result of deficit spending over time. It includes debt held "
            "by the public (Treasury bonds purchased by investors) and intragovernmental debt (money the "
            "Treasury owes to Social Security and other trust funds). As of 2024 it exceeds $36 trillion. "
            "Economists debate the significance of the absolute number versus debt as a percentage of GDP, "
            "which measures the economy's capacity to service the obligation. The trajectory — "
            "particularly the steepening post-2008 and again post-2020 — is the most analytically "
            "relevant feature of the chart."
        )

# ── Chart 2 — Student Loan Debt ───────────────────────────────────────────────
student_df = dff[["DATE", "Student_Loan_Debt"]].dropna().copy()
if len(student_df) >= 2:
    fig2 = make_area_chart(student_df, "Student_Loan_Debt", "Student Loan Debt Outstanding",
                           x_start=start_date, x_end=end_date)
    add_recession_bands(fig2)
    fig2.update_layout(yaxis=dict(title="Billions USD"))
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("📊 What this measures"):
        st.markdown(
            "Student Loan Debt Outstanding measures the total balance of federal and private student "
            "loans held by borrowers. The United States has the largest student loan market in the world "
            "at approximately $1.7 trillion. Unlike most consumer debt, federal student loans cannot be "
            "discharged in bankruptcy, making them a uniquely persistent financial obligation. The rapid "
            "growth since 2006 reflects both rising tuition costs and increased enrollment driven by "
            "federal lending availability. Economists study student debt for its impact on household "
            "formation, homeownership rates, and retirement savings among younger cohorts — all of which "
            "show measurable suppression in high-debt populations."
        )

# ── Chart 3 — Purchasing Power vs Housing Affordability ───────────────────────
cpi_valid = dff[["DATE", "CPI_All_Urban_Consumers", "Housing_Affordability_Index"]].copy()
cpi_drop = cpi_valid.dropna(subset=["CPI_All_Urban_Consumers"])
if len(cpi_drop) >= 2:
    cpi_base = cpi_drop["CPI_All_Urban_Consumers"].iloc[0]
    cpi_drop = cpi_drop.copy()
    cpi_drop["Purchasing_Power"] = 100.0 * cpi_base / cpi_drop["CPI_All_Urban_Consumers"]

    fig3 = make_line_chart(
        cpi_drop,
        series_list=["Purchasing_Power", "Housing_Affordability_Index"],
        title="Purchasing Power Erosion vs Housing Affordability",
        secondary_series=["Housing_Affordability_Index"],
        x_start=start_date,
        x_end=end_date,
    )
    add_recession_bands(fig3)
    fig3.update_layout(
        yaxis=dict(title="Purchasing Power (indexed to 100 at period start)"),
        yaxis2=dict(title="Housing Affordability Index"),
    )
    fig3.data[0].line.color = "#ffffff"   # Purchasing_Power
    fig3.data[1].line.color = "#e63946"   # Housing_Affordability_Index
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("📊 What this measures"):
        st.markdown(
            "This chart combines two derived measures to show the dual squeeze on younger households "
            "entering the economy. Purchasing power erosion reflects the cumulative real decline in what "
            "a dollar buys over time due to inflation. The Housing Affordability Index reflects how many "
            "years of median household income are required to purchase the median home. Together they "
            "capture a compounding dynamic: not only has the real value of wages declined, but the primary "
            "asset of middle-class wealth accumulation has become simultaneously more expensive in nominal "
            "terms and less accessible relative to income. Economists refer to this combination as a "
            "wealth-building gap — conditions that make it structurally harder for younger cohorts to "
            "accumulate assets than it was for previous generations at the same life stage."
        )

# ── Period Statistics ──────────────────────────────────────────────────────────
render_summary_stats(df, ["Federal_Debt_Total", "Student_Loan_Debt",
    "Housing_Affordability_Index", "Median_Household_Income"], start_date, end_date)

# ── Austrian Perspective ───────────────────────────────────────────────────────
with st.expander("📖 Austrian Perspective"):
    st.markdown(
        """
The Austrian critique of deficit spending is not partisan — it is mathematical. When a
government spends more than it collects, it finances the difference through borrowing, which
places a claim on future production. That claim must eventually be serviced through taxation,
inflation, or default. In practice, the United States has chosen the first two: taxes have
risen in real terms while inflation has quietly monetized a portion of the outstanding debt.
Both of these outcomes fall most heavily on those who have not yet accumulated assets —
which is to say, the young.

The student loan chart requires particular attention. The explosion of federally backed
student lending post-2000 is a direct consequence of the same dynamic visible in housing:
government-subsidized credit flowing into a supply-constrained market produces price inflation,
not increased access. Tuition costs rose in near-perfect correlation with the availability of
federal loans. The Austrian lesson — that you cannot subsidize demand without inflating price —
applies as clearly in higher education as it does in housing.

The comparison between 1985 and today is not an argument for nostalgia. It is an argument
for honest accounting. A 22-year-old in 1985 entered an economy with a federal debt of
roughly \\$1.8 trillion. A 22-year-old today inherits a share of \\$36 trillion — a number that
does not appear on any balance sheet they signed. The intergenerational transfer embedded in
deficit spending is the defining economic injustice of the era, and it is one that neither
mainstream political party has shown the will to address.
        """
    )

    articles = get_mises_articles()
    matched = match_articles(
        articles,
        ["government debt", "deficit", "student loans", "generational",
            "fiscal policy", "federal debt", "spending", "taxation",
            "entitlements", "social security", "borrowing", "future generations",
            "intergenerational", "tuition", "education"],
    )
    if matched:
        st.markdown("**Recent Mises Wire — Related Reading:**")
        for article in matched:
            st.markdown(f"📰 [{article['title']}]({article['url']}) — {article['date'][:10]}")
    else:
        st.markdown("*No recent articles matched this topic. Browse [Mises Wire](https://mises.org/wire) for the latest.*")
