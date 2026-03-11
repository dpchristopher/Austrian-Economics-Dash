# -*- coding: utf-8 -*-
"""
utils/styles.py
----------------
Centralized CSS injection for the Austrian Economics Dashboard.
Call inject_styles() at the top of every page (after set_page_config).
"""
import streamlit as st


def inject_styles() -> None:
    """Inject the full terminal-aesthetic CSS layer into the current page."""
    st.markdown(
        """
        <style>
        /* ── Google Fonts ──────────────────────────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Barlow+Condensed:wght@400;600;700&display=swap');

        /* ── Global reset & base ───────────────────────────────────────────── */
        html, body, [class*="css"] {
            font-size: 14px;
            color: #ffffff;
            letter-spacing: 0.02em;
        }
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 2rem !important;
        }

        /* ── Noise texture overlay ─────────────────────────────────────────── */
        body::before {
            content: '';
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
            pointer-events: none;
            z-index: 9999;
            opacity: 0.4;
        }

        /* ── Hide default Streamlit chrome ─────────────────────────────────── */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display: none;}

        /* ── Sidebar ───────────────────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background-color: #0d0d0d !important;
            border-left: 3px solid #e63946;
            min-width: 260px !important;
            max-width: 260px !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding: 24px 16px !important;
        }
        /* Nav links */
        [data-testid="stSidebarNav"] a {
            font-size: 13px !important;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #888888 !important;
            border-bottom: 1px solid #1a1a1a;
            padding: 6px 0 !important;
            display: block;
        }
        [data-testid="stSidebarNav"] a:hover {
            color: #ffffff !important;
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            color: #e63946 !important;
        }

        /* ── Sidebar app name block ────────────────────────────────────────── */
        .sidebar-title {
            font-family: 'Barlow Condensed', sans-serif;
            font-size: 22px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            border-bottom: 1px solid #e63946;
            padding-bottom: 12px;
            margin-bottom: 20px;
        }
        .sidebar-sub {
            font-size: 11px;
            color: #888888;
            margin-top: 2px;
        }

        /* ── Page headers ──────────────────────────────────────────────────── */
        h1 {
            font-family: 'Barlow Condensed', sans-serif !important;
            font-size: 42px !important;
            font-weight: 700 !important;
            letter-spacing: 0.08em !important;
            text-transform: uppercase;
            color: #ffffff !important;
            margin-bottom: 4px !important;
        }
        h2 {
            font-family: 'Barlow Condensed', sans-serif !important;
            font-size: 24px !important;
            letter-spacing: 0.06em !important;
            text-transform: uppercase;
            color: #cccccc !important;
        }
        h3 {
            font-family: 'Barlow Condensed', sans-serif !important;
            font-size: 18px !important;
            letter-spacing: 0.04em !important;
            color: #888888 !important;
        }
        h4 {
            font-family: 'Barlow Condensed', sans-serif !important;
            font-size: 15px !important;
            letter-spacing: 0.04em !important;
            text-transform: uppercase;
            color: #888888 !important;
        }

        /* ── KPI metric cards ──────────────────────────────────────────────── */
        [data-testid="metric-container"] {
            background: #111111 !important;
            border: 1px solid #222222 !important;
            border-top: 2px solid #e63946 !important;
            border-radius: 0 !important;
            padding: 16px !important;
            box-shadow: 0 0 20px rgba(230, 57, 70, 0.05);
        }
        [data-testid="metric-container"] label {
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 11px !important;
            text-transform: uppercase;
            letter-spacing: 0.12em !important;
            color: #888888 !important;
        }
        [data-testid="metric-container"] [data-testid="stMetricValue"] {
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 28px !important;
            font-weight: 600 !important;
            color: #ffffff !important;
        }
        [data-testid="metric-container"] [data-testid="stMetricDelta"] svg {
            display: none;
        }
        [data-testid="stMetricDelta"] > div {
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 12px !important;
        }

        /* ── Expanders ─────────────────────────────────────────────────────── */
        [data-testid="stExpander"] {
            background: #111111 !important;
            border-left: 3px solid #e63946 !important;
            border-top: 1px solid #1e1e1e !important;
            border-right: 1px solid #1e1e1e !important;
            border-bottom: 1px solid #1e1e1e !important;
            border-radius: 0 !important;
        }
        [data-testid="stExpander"]:hover {
            border-left-color: #ff4d5a !important;
        }
        [data-testid="stExpander"] summary {
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 12px !important;
            text-transform: uppercase;
            letter-spacing: 0.1em !important;
            color: #e63946 !important;
            padding: 12px 16px !important;
            list-style: none;
        }
        [data-testid="stExpander"] summary::-webkit-details-marker {
            display: none;
        }
        [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
            padding: 16px !important;
            font-size: 13px !important;
            line-height: 1.7 !important;
            color: #cccccc !important;
        }

        /* ── Sliders ───────────────────────────────────────────────────────── */
        [data-testid="stSlider"] [data-testid="stTickBar"] {
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 11px !important;
            color: #888888 !important;
        }
        [data-testid="stSlider"] > div > div > div {
            background: #222222 !important;
            height: 2px !important;
        }
        [data-testid="stSlider"] [role="slider"] {
            background: #e63946 !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            border: none !important;
        }
        /* Active track fill */
        [data-testid="stSlider"] > div > div > div > div {
            background: #e63946 !important;
        }

        /* ── Buttons ───────────────────────────────────────────────────────── */
        .stButton > button {
            background: #1a1a1a !important;
            border: 1px solid #333333 !important;
            color: #ffffff !important;
            border-radius: 0 !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 12px !important;
            text-transform: uppercase;
            letter-spacing: 0.08em !important;
        }
        .stButton > button:hover {
            border-color: #e63946 !important;
            color: #e63946 !important;
            background: #1a1a1a !important;
        }

        /* ── Radio & checkbox ──────────────────────────────────────────────── */
        [data-testid="stRadio"] input,
        [data-testid="stCheckbox"] input {
            accent-color: #e63946 !important;
        }

        /* ── Selectbox & multiselect ───────────────────────────────────────── */
        [data-testid="stSelectbox"] > div > div,
        [data-testid="stMultiSelect"] > div > div {
            background: #111111 !important;
            border: 1px solid #333333 !important;
            border-radius: 0 !important;
            color: #ffffff !important;
        }
        /* Multiselect tags */
        [data-testid="stMultiSelect"] span[data-baseweb="tag"] {
            background: #e63946 !important;
            color: #ffffff !important;
            border-radius: 0 !important;
        }
        /* Dropdown panel */
        [data-baseweb="popover"] ul {
            background: #111111 !important;
            border: 1px solid #333333 !important;
            border-radius: 0 !important;
        }
        [data-baseweb="popover"] li:hover {
            background: #1e1e1e !important;
        }

        /* ── Dataframes / tables ───────────────────────────────────────────── */
        [data-testid="stDataFrame"] {
            background: #0d0d0d !important;
            border: 1px solid #1e1e1e !important;
        }
        [data-testid="stDataFrame"] th {
            background: #1a1a1a !important;
            color: #e63946 !important;
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 11px !important;
            text-transform: uppercase;
        }
        [data-testid="stDataFrame"] td {
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 12px !important;
            color: #cccccc !important;
            border: 1px solid #1e1e1e !important;
        }
        [data-testid="stDataFrame"] tr:hover td {
            background: #141414 !important;
        }

        /* ── Horizontal rules ──────────────────────────────────────────────── */
        hr {
            border: none !important;
            border-top: 1px solid #1e1e1e !important;
            margin: 24px 0 !important;
        }

        /* ── Info / warning boxes ──────────────────────────────────────────── */
        [data-testid="stAlert"][data-kind="info"],
        div[data-testid="stInfo"] {
            background: #0d1a1a !important;
            border-left: 3px solid #e63946 !important;
            border-radius: 0 !important;
            font-size: 13px !important;
        }
        [data-testid="stAlert"][data-kind="warning"],
        div[data-testid="stWarning"] {
            background: #1a1000 !important;
            border-left: 3px solid #ff9900 !important;
            border-radius: 0 !important;
        }

        /* ── Plotly chart containers ───────────────────────────────────────── */
        [data-testid="stPlotlyChart"] {
            border: 1px solid #1e1e1e !important;
            border-radius: 0 !important;
        }

        /* ── Number / data text ────────────────────────────────────────────── */
        .stMetric, .stTable, .dataframe {
            font-family: 'IBM Plex Mono', monospace !important;
        }

        /* ── Caption text ──────────────────────────────────────────────────── */
        [data-testid="stCaptionContainer"],
        .stCaption {
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 11px !important;
            color: #555555 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def divider() -> None:
    """Render a styled horizontal divider consistent with the terminal aesthetic."""
    st.markdown(
        '<hr style="border:none; border-top: 1px solid #1e1e1e; margin: 32px 0;">',
        unsafe_allow_html=True,
    )
