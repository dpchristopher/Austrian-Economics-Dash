# -*- coding: utf-8 -*-
"""
econ.py — Austrian Economics Dashboard
Homepage: KPI overview cards + navigation prompt.
Run with:  streamlit run econ.py
"""
import streamlit as st
import pandas as pd
from utils.data_loader import load_data, get_date_range

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="Austrian Economics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS injection ───────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Tighten top padding */
    .block-container { padding-top: 1.5rem !important; }

    /* Dividers */
    hr { border-color: #222222 !important; margin: 0.5rem 0; }

    /* Sidebar title block */
    .sidebar-title { font-size: 16px; font-weight: 700; color: #e63946; letter-spacing: 1px; }
    .sidebar-sub   { font-size: 11px; color: #888888; margin-top: 2px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Load data ──────────────────────────────────────────────────────────────────
df = load_data()
min_date, max_date = get_date_range(df)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<div class='sidebar-title'>AUSTRIAN ECON</div>"
        "<div class='sidebar-sub'>Dashboard</div>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.caption("Data: FRED API + Yahoo Finance")
    st.caption(f"Last updated: {max_date.strftime('%B %Y')}")

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='color:#ffffff; margin-bottom:0; font-size:2.2rem;'>"
    "Austrian Economics Dashboard"
    "</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h3 style='color:#e63946; margin-top:4px; font-weight:400; font-size:1.1rem;'>"
    "Exploring the real cost of monetary policy \u2014 1970 to present"
    "</h3>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color:#888888; font-size:14px; margin-bottom:20px;'>"
    "The following data tells the story of what happens when governments price money, "
    "suppress rates, and spend futures they haven\u2019t earned."
    "</p>",
    unsafe_allow_html=True,
)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

# ── KPI card configuration ─────────────────────────────────────────────────────
# higher_is_bad:
#   True  -> increase = red (worsening)
#   False -> increase = white (improving)
#   None  -> always white (neutral / ambiguous from Austrian lens)
KPI_CARDS = [
    {
        "col":          "Federal_Funds_Rate",
        "label":        "Federal Funds Rate",
        "format":       lambda v: f"{v:.2f}%",
        "higher_is_bad": None,
    },
    {
        "col":          "M2_Money_Supply",
        "label":        "M2 Money Supply",
        "format":       lambda v: f"${v / 1000:.2f}T",
        "higher_is_bad": True,
    },
    {
        "col":          "CPI_All_Urban_Consumers",
        "label":        "CPI (All Urban)",
        "format":       lambda v: f"{v:.1f}",
        "higher_is_bad": True,
    },
    {
        "col":          "Unemployment_Rate",
        "label":        "Unemployment Rate",
        "format":       lambda v: f"{v:.1f}%",
        "higher_is_bad": True,
    },
    {
        "col":          "Treasury_10yr",
        "label":        "10yr Treasury",
        "format":       lambda v: f"{v:.2f}%",
        "higher_is_bad": None,
    },
    {
        "col":          "Housing_Affordability_Index",
        "label":        "Home Affordability",
        "format":       lambda v: f"{v:.2f}",
        "higher_is_bad": True,
    },
]


# ── KPI helper functions ───────────────────────────────────────────────────────
def _get_kpi_values(col_name: str, months_back: int = 12):
    """Return (current_value, prior_value) using non-NaN monthly positions."""
    series = df[col_name].dropna()
    if len(series) == 0:
        return None, None
    current = series.iloc[-1]
    prior = series.iloc[-(months_back + 1)] if len(series) > months_back else None
    return current, prior


def _delta_color(pct_change: float, higher_is_bad) -> str:
    """Return hex color string for the delta indicator."""
    if higher_is_bad is None:
        return "#ffffff"
    if pct_change > 0:
        return "#e63946" if higher_is_bad else "#ffffff"
    if pct_change < 0:
        return "#ffffff" if higher_is_bad else "#e63946"
    return "#888888"  # no change


def _kpi_card_html(label: str, current, prior, format_fn, higher_is_bad: bool) -> str:
    """Build the HTML string for one KPI card."""
    # ── No data ────────────────────────────────────────────────────────────────
    if current is None or pd.isna(current):
        return (
            "<div style='"
            "background:#141414;border:1px solid #222222;border-radius:4px;"
            "padding:18px 12px;text-align:center;min-height:115px;'>"
            f"<div style='color:#888888;font-size:10px;text-transform:uppercase;"
            f"letter-spacing:1.5px;margin-bottom:10px;'>{label}</div>"
            "<div style='color:#555555;font-size:22px;font-weight:700;margin-bottom:8px;'>"
            "N/A</div>"
            "<div style='color:#555555;font-size:11px;'>No data</div>"
            "</div>"
        )

    current_str = format_fn(current)

    # ── Delta ──────────────────────────────────────────────────────────────────
    if prior is None or pd.isna(prior) or prior == 0:
        delta_html = (
            "<div style='color:#555555;font-size:11px;'>&#8212;&nbsp;Prior N/A</div>"
        )
    else:
        pct = (current - prior) / abs(prior) * 100
        arrow = "&#9650;" if pct > 0 else "&#9660;"  # ▲ ▼ as HTML entities
        color = _delta_color(pct, higher_is_bad)
        delta_html = (
            f"<div style='color:{color};font-size:11px;'>"
            f"{arrow}&nbsp;{abs(pct):.1f}%&nbsp;vs 12mo ago"
            "</div>"
        )

    return (
        "<div style='"
        "background:#141414;border:1px solid #222222;border-radius:4px;"
        "padding:18px 12px;text-align:center;min-height:115px;width:100%;'>"
        f"<div style='color:#888888;font-size:10px;text-transform:uppercase;"
        f"letter-spacing:1.5px;margin-bottom:10px;'>{label}</div>"
        f"<div style='color:#ffffff;font-size:22px;font-weight:700;"
        f"margin-bottom:8px;font-family:monospace;'>{current_str}</div>"
        f"{delta_html}"
        "</div>"
    )


# ── Render KPI cards ───────────────────────────────────────────────────────────
kpi_cols = st.columns(6, gap="small")

for col_widget, config in zip(kpi_cols, KPI_CARDS):
    with col_widget:
        current, prior = _get_kpi_values(config["col"])
        html = _kpi_card_html(
            config["label"],
            current,
            prior,
            config["format"],
            config["higher_is_bad"],
        )
        st.markdown(html, unsafe_allow_html=True)

# ── Navigation prompt ──────────────────────────────────────────────────────────
st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#888888;text-align:center;font-size:14px;margin-top:12px;'>"
    "Use the sidebar to explore money supply, credit markets, housing, labor, "
    "and the generational cost of short-term thinking."
    "</p>",
    unsafe_allow_html=True,
)
