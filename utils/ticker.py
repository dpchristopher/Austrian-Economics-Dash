# -*- coding: utf-8 -*-
"""
utils/ticker.py
----------------
Scrolling live ticker bar for the Austrian Economics Dashboard.
Call render_ticker(df) immediately after inject_styles() on every page.
"""
import streamlit as st
import pandas as pd


def render_ticker(df: pd.DataFrame) -> None:
    """
    Render a full-width scrolling ticker bar showing current metric values.
    Self-contained HTML/CSS — does not depend on styles.py since it runs
    inside an isolated st.components iframe.

    Parameters
    ----------
    df : The full dashboard DataFrame from load_data().
    """
    def _latest(col):
        """Return the most recent non-NaN value for a column, or None."""
        if col not in df.columns:
            return None
        s = df[col].dropna()
        return float(s.iloc[-1]) if len(s) > 0 else None

    # ── Pull values ──────────────────────────────────────────────────────────
    ffr    = _latest("Federal_Funds_Rate")
    m2     = _latest("M2_Money_Supply")       # billions → display as trillions
    cpi    = _latest("CPI_All_Urban_Consumers")
    unemp  = _latest("Unemployment_Rate")
    t10    = _latest("Treasury_10yr")
    t2     = _latest("Treasury_2yr")
    afford = _latest("Housing_Affordability_Index")
    mort   = _latest("Mortgage_Rate_30yr")
    gdp    = _latest("GDP_Growth_Rate")
    ipi    = _latest("Industrial_Production_Index")
    oil    = _latest("Oil_Price_WTI")
    gold   = _latest("Gold_Price")
    sp500  = _latest("SP500")

    spread = (t10 - t2) * 100 if (t10 is not None and t2 is not None) else None

    # ── Format helpers ───────────────────────────────────────────────────────
    def pct2(v):  return f"{v:.2f}%" if v is not None else "--"
    def pct1(v):  return f"{v:.1f}%" if v is not None else "--"
    def dec1(v):  return f"{v:.1f}"  if v is not None else "--"
    def dec2(v):  return f"{v:.2f}"  if v is not None else "--"
    def tril(v):  return f"${v / 1000:.2f}T" if v is not None else "--"
    def bps(v):   return f"{v:.1f}bps" if v is not None else "--"
    def usd0(v):  return f"${v:,.0f}" if v is not None else "--"
    def usd2(v):  return f"${v:,.2f}" if v is not None else "--"

    # ── Color logic — highlight notable values red ───────────────────────────
    def color(val, col_name):
        if val is None:
            return "#cccccc"
        if col_name == "ffr"   and val > 4:    return "#e63946"
        if col_name == "cpi"   and val > 5:    return "#e63946"
        if col_name == "unemp" and val > 6:    return "#e63946"
        if col_name == "spread" and val < 0:   return "#e63946"
        return "#ffffff"

    # ── Build item HTML ──────────────────────────────────────────────────────
    SEP = '<span style="color:#333333;padding:0 14px;">|</span>'

    def item(label, value_str, col_name=None, raw_val=None):
        c = color(raw_val, col_name) if col_name else "#ffffff"
        return (
            f'<span style="color:#666666;font-size:11px;letter-spacing:0.08em;">{label}</span>'
            f'<span style="color:{c};margin-left:6px;">{value_str}</span>'
            f'{SEP}'
        )

    items = "".join([
        item("FED FUNDS",       pct2(ffr),   "ffr",    ffr),
        item("M2",              tril(m2)),
        item("CPI",             dec1(cpi),   "cpi",    cpi),
        item("UNEMPLOYMENT",    pct1(unemp), "unemp",  unemp),
        item("10YR",            pct2(t10)),
        item("2YR",             pct2(t2)),
        item("SPREAD",          bps(spread), "spread", spread),
        item("OIL (WTI)",       usd2(oil)),
        item("GOLD",            usd0(gold)),
        item("S&P 500",         usd0(sp500)),
        item("HOME AFFORD.",    dec2(afford)),
        item("MORTGAGE 30YR",   pct2(mort)),
        item("GDP GROWTH",      pct2(gdp)),
        item("INDUSTRIAL PROD", dec1(ipi)),
    ])

    html = f"""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&display=swap');
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      body {{ background: #0a0a0a; overflow: hidden; }}
      .ticker-wrap {{
        width: 100%;
        height: 36px;
        background: #0d0d0d;
        border-bottom: 1px solid #1e1e1e;
        overflow: hidden;
        display: flex;
        align-items: center;
      }}
      .ticker-track {{
        display: inline-flex;
        align-items: center;
        white-space: nowrap;
        animation: ticker-scroll 55s linear infinite;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        padding-left: 24px;
      }}
      @keyframes ticker-scroll {{
        0%   {{ transform: translateX(0); }}
        100% {{ transform: translateX(-50%); }}
      }}
    </style>
    <div class="ticker-wrap">
      <div class="ticker-track">
        <span>{items}</span>
        <span>{items}</span>
      </div>
    </div>
    """

    st.components.v1.html(html, height=40, scrolling=False)
