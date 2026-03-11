# -*- coding: utf-8 -*-
"""
pages/7_About.py
About page for the Austrian Economics Dashboard.
"""
import streamlit as st
from utils.styles import inject_styles
from utils.data_loader import load_data, get_date_range
from utils.ticker import render_ticker

st.set_page_config(
    page_title="About | Austrian Economics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_styles()

df = load_data()
min_date, max_date = get_date_range(df)
render_ticker(df)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom: 32px;">
    <h1>About This Dashboard</h1>
    <div style="width: 60px; height: 2px; background: #e63946; margin-top: 8px;"></div>
    <p style="color: #888888; font-size: 13px; letter-spacing: 0.04em; margin-top: 12px;">
        Data, methodology, and the analytical framework behind the numbers.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Section 1 — The Thesis ─────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom: 32px; max-width: 860px;">
    <h2 style="margin-bottom: 16px;">The Thesis</h2>
    <p style="color: #cccccc; font-size: 14px; line-height: 1.8; margin-bottom: 16px;">
        This dashboard was built to explore a simple but uncomfortable question: what happens
        to an economy when the price of money is set by committee rather than by markets?
    </p>
    <p style="color: #cccccc; font-size: 14px; line-height: 1.8; margin-bottom: 16px;">
        The data covers January 1970 through December 2024 — 55 years of monetary policy,
        business cycles, asset price inflation, and the slow erosion of purchasing power.
        The Austrian school of economics provides the analytical lens. The data provides
        the verdict.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr style="border:none; border-top: 1px solid #1e1e1e; margin: 32px 0;">', unsafe_allow_html=True)

# ── Section 2 — Data Sources ───────────────────────────────────────────────────
st.markdown('<h2 style="margin-bottom: 20px;">Data Sources</h2>', unsafe_allow_html=True)
st.markdown("""
<table style="width:100%;border-collapse:collapse;font-family:'IBM Plex Mono',monospace;font-size:13px;max-width:800px;">
  <thead>
    <tr style="background:#1a1a1a;">
      <th style="padding:10px 16px;color:#e63946;text-align:left;border-bottom:1px solid #333;text-transform:uppercase;letter-spacing:0.08em;font-size:11px;">Source</th>
      <th style="padding:10px 16px;color:#e63946;text-align:left;border-bottom:1px solid #333;text-transform:uppercase;letter-spacing:0.08em;font-size:11px;">Series</th>
      <th style="padding:10px 16px;color:#e63946;text-align:left;border-bottom:1px solid #333;text-transform:uppercase;letter-spacing:0.08em;font-size:11px;">Coverage</th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom:1px solid #1e1e1e;">
      <td style="padding:10px 16px;color:#ffffff;">Federal Reserve (FRED)</td>
      <td style="padding:10px 16px;color:#888888;">21 macroeconomic series</td>
      <td style="padding:10px 16px;color:#888888;">1970–2024</td>
    </tr>
    <tr style="border-bottom:1px solid #1e1e1e;">
      <td style="padding:10px 16px;color:#ffffff;">Yahoo Finance</td>
      <td style="padding:10px 16px;color:#888888;">S&amp;P 500, Gold Price</td>
      <td style="padding:10px 16px;color:#888888;">1985–2024</td>
    </tr>
    <tr>
      <td style="padding:10px 16px;color:#ffffff;">Mises Institute (mises.org/wire)</td>
      <td style="padding:10px 16px;color:#888888;">Related articles</td>
      <td style="padding:10px 16px;color:#888888;">Live</td>
    </tr>
  </tbody>
</table>
""", unsafe_allow_html=True)

st.markdown('<hr style="border:none; border-top: 1px solid #1e1e1e; margin: 32px 0;">', unsafe_allow_html=True)

# ── Section 3 — Methodology ────────────────────────────────────────────────────
with st.expander("📖 Methodology"):
    st.markdown("""
All data is pulled programmatically via the FRED API and Yahoo Finance. Monthly
frequency is enforced throughout — daily series are averaged to monthly, quarterly
series are forward-filled within each quarter, and annual series are forward-filled
within each year. GDP growth is calculated as quarter-over-quarter percent change
in real GDP (FRED: GDPC1), forward-filled across each quarter's three months.

The dataset spans 660 monthly observations across 25 series. Series with different
start dates retain their full available history — early NaN values reflect data
availability, not gaps. All series share a common end date determined by the
shortest-coverage series (Median Household Income and Student Loan Debt, both
through December 2024).

The Housing Affordability Index is a derived series: Median Home Sales Price
divided by Median Household Income. Higher values indicate less affordability.
    """)

st.markdown('<hr style="border:none; border-top: 1px solid #1e1e1e; margin: 32px 0;">', unsafe_allow_html=True)

# ── Section 4 — Austrian Economics Resources ───────────────────────────────────
st.markdown('<h2 style="margin-bottom: 20px;">Austrian Economics Resources</h2>', unsafe_allow_html=True)
st.markdown("""
<div style="display:flex;flex-direction:column;gap:14px;max-width:700px;">
  <div style="border-left:3px solid #e63946;padding:10px 16px;background:#111111;">
    <a href="https://mises.org" target="_blank"
       style="color:#ffffff;font-family:'IBM Plex Mono',monospace;font-size:13px;font-weight:600;text-decoration:none;">
      Mises Institute
    </a>
    <p style="color:#888888;font-size:12px;margin-top:4px;font-family:'IBM Plex Mono',monospace;">
      Primary repository of Austrian economics literature
    </p>
  </div>
  <div style="border-left:3px solid #333333;padding:10px 16px;background:#111111;">
    <a href="https://mises.org/library/human-action-0" target="_blank"
       style="color:#ffffff;font-family:'IBM Plex Mono',monospace;font-size:13px;font-weight:600;text-decoration:none;">
      Human Action — Ludwig von Mises
    </a>
    <p style="color:#888888;font-size:12px;margin-top:4px;font-family:'IBM Plex Mono',monospace;">
      Foundational text of the Austrian school
    </p>
  </div>
  <div style="border-left:3px solid #333333;padding:10px 16px;background:#111111;">
    <a href="https://mises.org/library/prices-and-production-and-other-works" target="_blank"
       style="color:#ffffff;font-family:'IBM Plex Mono',monospace;font-size:13px;font-weight:600;text-decoration:none;">
      Prices and Production — Friedrich Hayek
    </a>
    <p style="color:#888888;font-size:12px;margin-top:4px;font-family:'IBM Plex Mono',monospace;">
      Business cycle theory and capital structure
    </p>
  </div>
  <div style="border-left:3px solid #333333;padding:10px 16px;background:#111111;">
    <a href="https://mises.org/library/what-has-government-done-our-money" target="_blank"
       style="color:#ffffff;font-family:'IBM Plex Mono',monospace;font-size:13px;font-weight:600;text-decoration:none;">
      What Has Government Done to Our Money — Murray Rothbard
    </a>
    <p style="color:#888888;font-size:12px;margin-top:4px;font-family:'IBM Plex Mono',monospace;">
      Monetary theory primer
    </p>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr style="border:none; border-top: 1px solid #1e1e1e; margin: 32px 0;">', unsafe_allow_html=True)

# ── Section 5 — Built By ───────────────────────────────────────────────────────
st.markdown('<h2 style="margin-bottom: 20px;">Built By</h2>', unsafe_allow_html=True)
st.markdown("""
<div style="background:#111111;border-top:2px solid #e63946;border:1px solid #222222;
            padding:20px 24px;max-width:400px;font-family:'IBM Plex Mono',monospace;">
  <div style="font-size:16px;font-weight:600;color:#ffffff;letter-spacing:0.04em;">
    Daniel Prickett
  </div>
  <div style="font-size:12px;color:#888888;margin-top:6px;letter-spacing:0.04em;">
    MSBA Candidate, Wake Forest University
  </div>
  <div style="margin-top:16px;display:flex;gap:20px;">
    <a href="#" style="color:#e63946;font-size:12px;text-decoration:none;letter-spacing:0.06em;">
      LinkedIn ↗
    </a>
    <a href="#" style="color:#e63946;font-size:12px;text-decoration:none;letter-spacing:0.06em;">
      GitHub ↗
    </a>
  </div>
</div>
""", unsafe_allow_html=True)
