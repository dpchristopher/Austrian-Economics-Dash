# -*- coding: utf-8 -*-
"""
Home.py — Austrian Economics Dashboard
Homepage: KPI overview cards + navigation prompt.
Run with:  streamlit run Home.py
"""
import streamlit as st
import pandas as pd
import json
from utils.data_loader import load_data, get_date_range
from utils.styles import inject_styles
from utils.ticker import render_ticker

# ── Page config (must be first Streamlit call) ─────────────────────────────────
st.set_page_config(
    page_title="Home | Austrian Economics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

# ── Load data ──────────────────────────────────────────────────────────────────
df = load_data()
min_date, max_date = get_date_range(df)
render_ticker(df)

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
st.markdown("""
<div style="margin-bottom: 32px;">
    <h1>Austrian Economics Dashboard</h1>
    <div style="width: 60px; height: 2px; background: #e63946; margin-top: 8px;"></div>
    <p style="color: #888888; font-size: 13px; letter-spacing: 0.04em; margin-top: 12px;">
        The following data tells the story of what happens when governments price money,
        suppress rates, and spend futures they haven\u2019t earned.
    </p>
</div>
""", unsafe_allow_html=True)

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





# ── Animated KPI cards ─────────────────────────────────────────────────────────
# Build data payload for JS animation
_kpi_payload = []
_fmt_map = {
    "Federal_Funds_Rate":        ("pct2",     1.0),
    "M2_Money_Supply":           ("trillions", 1/1000),
    "CPI_All_Urban_Consumers":   ("decimal1", 1.0),
    "Unemployment_Rate":         ("pct1",     1.0),
    "Treasury_10yr":             ("pct2",     1.0),
    "Housing_Affordability_Index": ("decimal2", 1.0),
}
for config in KPI_CARDS:
    current, prior = _get_kpi_values(config["col"])
    fmt_type, scale = _fmt_map.get(config["col"], ("decimal2", 1.0))
    _c: float | None = float(current) if (current is not None and not pd.isna(current)) else None
    _p: float | None = float(prior)   if (prior   is not None and not pd.isna(prior))   else None
    display_val = _c * scale if _c is not None else None

    delta_pct: float | None = None
    delta_color = "#888888"
    if _c is not None and _p is not None and _p != 0:
        delta_pct = (_c - _p) / abs(_p) * 100
        hib = config["higher_is_bad"]
        if hib is None:
            delta_color = "#aaaaaa"
        elif hib:
            delta_color = "#e63946" if delta_pct > 0 else "#4caf50"
        else:
            delta_color = "#4caf50" if delta_pct > 0 else "#e63946"

    _kpi_payload.append({
        "label":       config["label"],
        "value":       display_val,
        "fmt":         fmt_type,
        "delta_pct":   round(delta_pct, 1) if delta_pct is not None else None,
        "delta_color": delta_color,
    })

_kpi_json = json.dumps(_kpi_payload)

st.components.v1.html(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Barlow+Condensed:wght@700&display=swap');
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ background:#0a0a0a; overflow:hidden; }}
  .kpi-row {{
    display: flex;
    gap: 12px;
    padding: 4px 0 8px 0;
    width: 100%;
  }}
  .kpi-card {{
    flex: 1;
    background: #111111;
    border: 1px solid #222222;
    border-top: 2px solid #e63946;
    padding: 16px 14px;
    min-height: 110px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .kpi-label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #888888;
    margin-bottom: 10px;
  }}
  .kpi-value {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 26px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 8px;
    min-height: 34px;
  }}
  .kpi-delta {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    color: #888888;
  }}
</style>
<div class="kpi-row" id="kpi-row"></div>
<script>
  const DATA = {_kpi_json};

  function formatValue(val, fmt) {{
    if (val === null || val === undefined) return 'N/A';
    switch(fmt) {{
      case 'trillions': return '$' + val.toFixed(2) + 'T';
      case 'pct2':      return val.toFixed(2) + '%';
      case 'pct1':      return val.toFixed(1) + '%';
      case 'decimal1':  return val.toFixed(1);
      case 'decimal2':  return val.toFixed(2);
      default:          return val.toFixed(2);
    }}
  }}

  function easeOutCubic(t) {{ return 1 - Math.pow(1 - t, 3); }}

  const row = document.getElementById('kpi-row');
  const valueEls = [];

  DATA.forEach((card, i) => {{
    const div = document.createElement('div');
    div.className = 'kpi-card';

    const label = document.createElement('div');
    label.className = 'kpi-label';
    label.textContent = card.label;

    const value = document.createElement('div');
    value.className = 'kpi-value';
    value.textContent = card.value !== null ? formatValue(0, card.fmt) : 'N/A';

    const delta = document.createElement('div');
    delta.className = 'kpi-delta';
    if (card.delta_pct !== null && card.delta_pct !== undefined) {{
      const arrow = card.delta_pct > 0 ? '▲' : '▼';
      delta.style.color = card.delta_color;
      delta.textContent = arrow + ' ' + Math.abs(card.delta_pct).toFixed(1) + '% vs 12mo ago';
    }} else {{
      delta.textContent = '— Prior N/A';
    }}

    div.appendChild(label);
    div.appendChild(value);
    div.appendChild(delta);
    row.appendChild(div);
    valueEls.push({{ el: value, value: card.value, fmt: card.fmt }});
  }});

  const DURATION = 1200;
  const start = performance.now();

  function animate() {{
    const elapsed = performance.now() - start;
    const t = Math.min(elapsed / DURATION, 1);
    const progress = easeOutCubic(t);

    valueEls.forEach(item => {{
      if (item.value !== null) {{
        item.el.textContent = formatValue(item.value * progress, item.fmt);
      }}
    }});

    if (t < 1) {{
      requestAnimationFrame(animate);
    }} else {{
      valueEls.forEach(item => {{
        if (item.value !== null) {{
          item.el.textContent = formatValue(item.value, item.fmt);
        }}
      }});
    }}
  }}

  requestAnimationFrame(animate);
</script>
""", height=145)

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

# ── Term Dictionary ────────────────────────────────────────────────────────────
_DICT_BG      = "#141414"
_DICT_BG_HEAD = "#1a1a1a"
_DICT_BORDER  = "#222222"
_DICT_RED     = "#e63946"
_DICT_WHITE   = "#ffffff"
_DICT_MUTED   = "#888888"

def _subheader_row(label: str) -> str:
    return (
        f"<tr style='background:{_DICT_BG_HEAD};'>"
        f"<td colspan='2' style='padding:8px 16px;color:{_DICT_MUTED};"
        f"font-size:10px;text-transform:uppercase;letter-spacing:1.4px;"
        f"border-bottom:1px solid {_DICT_BORDER};font-weight:600;'>"
        f"{label}</td></tr>"
    )

def _term_row(term: str, definition: str) -> str:
    return (
        f"<tr>"
        f"<td style='padding:9px 16px;color:{_DICT_RED};font-weight:700;"
        f"border-bottom:1px solid {_DICT_BORDER};vertical-align:top;"
        f"white-space:nowrap;width:220px;'>{term}</td>"
        f"<td style='padding:9px 16px;color:{_DICT_WHITE};"
        f"border-bottom:1px solid {_DICT_BORDER};font-size:13px;line-height:1.5;'>"
        f"{definition}</td>"
        f"</tr>"
    )

_TERMS = [
    ("__HEADER__", "Core Monetary Terms"),
    ("M2 Money Supply",
     "The broadest commonly used measure of money in circulation, including cash, checking "
     "deposits, savings accounts, and money market funds. Tracked by the Federal Reserve as "
     "an indicator of monetary conditions."),
    ("Consumer Price Index (CPI)",
     "Measures the average change in prices paid by urban consumers for a fixed basket of "
     "goods and services. The most widely cited inflation measure in the US."),
    ("PCE Price Index",
     "The Federal Reserve's preferred inflation measure. Unlike CPI, it accounts for consumer "
     "substitution behavior and covers a broader range of expenditures."),
    ("Federal Funds Rate",
     "The interest rate at which banks lend reserve balances to each other overnight. The Fed's "
     "primary tool for controlling monetary policy and influencing broader interest rates "
     "throughout the economy."),
    ("Purchasing Power",
     "The real value of money — how much a unit of currency can actually buy. Inflation erodes "
     "purchasing power over time."),

    ("__HEADER__", "Credit & Bond Terms"),
    ("Yield Curve",
     "A chart plotting interest rates on Treasury bonds across different maturities. A normal "
     "curve slopes upward; an inverted curve (short rates above long rates) has preceded every "
     "US recession since 1955."),
    ("Yield Spread (10yr - 2yr)",
     "The difference between 10-year and 2-year Treasury yields. Negative values indicate "
     "inversion and are watched as a recession signal."),
    ("High Yield Credit Spread",
     "The extra yield investors demand to hold below-investment-grade (junk) corporate bonds "
     "over equivalent Treasuries. Wide spreads signal market stress; tight spreads signal "
     "confidence."),
    ("Credit Card Delinquency Rate",
     "The percentage of credit card balances 30+ days past due. A lagging indicator of consumer "
     "financial stress."),

    ("__HEADER__", "Housing Terms"),
    ("Case-Shiller Home Price Index",
     "Tracks repeat sales of the same properties over time to measure pure price appreciation, "
     "controlling for housing mix changes. More precise than median price for tracking true home "
     "price inflation."),
    ("Housing Affordability Index",
     "Median home sales price divided by median household income. Higher values mean less "
     "affordable. A ratio above 4.0 indicates significant affordability stress."),
    ("30-Year Fixed Mortgage Rate",
     "The interest rate on the most common US home loan. Directly affects monthly payment costs "
     "and therefore purchasing power in the housing market."),

    ("__HEADER__", "Austrian Economics Terms"),
    ("Austrian Business Cycle Theory (ABCT)",
     "Developed by Mises and Hayek. Holds that central bank credit expansion below the natural "
     "rate of interest causes malinvestment booms that must eventually correct in recessions."),
    ("Cantillon Effect",
     "The observation that newly created money does not raise all prices simultaneously. Those "
     "closest to the money creation (banks, government contractors) benefit first; wage earners "
     "and savers see price increases before income increases."),
    ("Malinvestment",
     "Investment undertaken because artificially cheap credit made it appear profitable, but "
     "which would not have been made under market interest rates. The correction of malinvestment "
     "is what Austrians call the recession phase of the business cycle."),
    ("Natural Rate of Interest",
     "The interest rate that would prevail in a free market, reflecting the true time preferences "
     "of savers and borrowers. Austrian theory holds that central bank rate-setting distorts "
     "this signal."),
    ("Sound Money",
     "Money whose value is stable and not subject to arbitrary expansion by government or central "
     "banks. Historically associated with the gold standard. A foundational concept in Austrian "
     "monetary theory."),
]

_dict_rows = ""
for item in _TERMS:
    if item[0] == "__HEADER__":
        _dict_rows += _subheader_row(item[1])
    else:
        _dict_rows += _term_row(item[0], item[1])

_dict_html = f"""
<div style="background:{_DICT_BG};border:1px solid {_DICT_BORDER};border-radius:4px;
            overflow:hidden;">
  <table style="width:100%;border-collapse:collapse;">
    <tbody>
      {_dict_rows}
    </tbody>
  </table>
</div>
"""

with st.expander("📚 Term Dictionary", expanded=False):
    st.markdown(_dict_html, unsafe_allow_html=True)
