# -*- coding: utf-8 -*-
"""
utils/chart_helpers.py
-----------------------
Reusable Plotly chart functions for the Austrian Economics Dashboard.
All charts share the same dark Bloomberg-inspired theme.
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── Color palette ──────────────────────────────────────────────────────────────
COLORS = ["#e63946", "#ffffff", "#888888"]

# ── Base theme dict ────────────────────────────────────────────────────────────
_BASE_LAYOUT = dict(
    paper_bgcolor="#0a0a0a",
    plot_bgcolor="#0a0a0a",
    font=dict(color="#ffffff", family="sans-serif", size=12),
    xaxis=dict(
        gridcolor="#222222",
        showgrid=True,
        zeroline=False,
        tickfont=dict(color="#888888"),
        title_font=dict(color="#888888"),
    ),
    yaxis=dict(
        gridcolor="#222222",
        showgrid=True,
        zeroline=False,
        tickfont=dict(color="#888888"),
        title_font=dict(color="#888888"),
    ),
    legend=dict(
        bgcolor="#141414",
        bordercolor="#222222",
        borderwidth=1,
        font=dict(color="#ffffff", size=11),
    ),
    margin=dict(l=60, r=60, t=60, b=40),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#141414", bordercolor="#222222", font_color="#ffffff"),
)

# ── NBER recession periods ─────────────────────────────────────────────────────
RECESSION_PERIODS = [
    ("1973-11", "1975-03"),
    ("1980-01", "1980-07"),
    ("1981-07", "1982-11"),
    ("1990-07", "1991-03"),
    ("2001-03", "2001-11"),
    ("2007-12", "2009-06"),
    ("2020-02", "2020-04"),
]


def _apply_theme(fig: go.Figure, with_secondary: bool = False) -> go.Figure:
    """Apply the base dark theme to a figure."""
    layout = dict(_BASE_LAYOUT)
    # Deep-copy mutable sub-dicts so we can safely mutate
    layout["xaxis"] = dict(_BASE_LAYOUT["xaxis"])
    layout["yaxis"] = dict(_BASE_LAYOUT["yaxis"])
    layout["legend"] = dict(_BASE_LAYOUT["legend"])
    layout["margin"] = dict(_BASE_LAYOUT["margin"])
    layout["font"] = dict(_BASE_LAYOUT["font"])
    layout["hoverlabel"] = dict(_BASE_LAYOUT["hoverlabel"])

    if with_secondary:
        layout["yaxis2"] = dict(
            overlaying="y",
            side="right",
            gridcolor="#222222",
            showgrid=False,
            zeroline=False,
            tickfont=dict(color="#888888"),
            title_font=dict(color="#888888"),
        )

    fig.update_layout(**layout)
    return fig


def make_line_chart(
    df: pd.DataFrame,
    series_list: list,
    title: str,
    date_col: str = "DATE",
    secondary_series: list = None,
    x_start=None,
    x_end=None,
) -> go.Figure:
    """
    Multi-series line chart with optional right Y-axis.

    Parameters
    ----------
    df : DataFrame containing date_col and all series columns
    series_list : column names to plot
    title : chart title
    date_col : name of the date column (default 'DATE')
    secondary_series : column names to place on right Y-axis.
        If None, auto-detects: if max ratio between any two series > 10x,
        puts the smaller-range series on the right axis.
    """
    # ── Auto-detect secondary axis ─────────────────────────────────────────────
    if secondary_series is None:
        secondary_series = []
        if len(series_list) >= 2:
            maxes = {}
            for s in series_list:
                if s in df.columns:
                    col_max = df[s].max()
                    if not pd.isna(col_max):
                        maxes[s] = col_max
            if len(maxes) >= 2:
                max_of_maxes = max(maxes.values())
                for s, mx in maxes.items():
                    if mx > 0 and max_of_maxes / mx > 10:
                        secondary_series.append(s)

    fig = go.Figure()

    for i, series in enumerate(series_list):
        if series not in df.columns:
            continue
        color = COLORS[i % len(COLORS)]
        on_secondary = series in secondary_series

        fig.add_trace(
            go.Scatter(
                x=df[date_col],
                y=df[series],
                name=series.replace("_", " "),
                line=dict(color=color, width=2),
                yaxis="y2" if on_secondary else "y",
                connectgaps=False,
            )
        )

    fig.update_layout(
        title=dict(text=title, font=dict(color="#ffffff", size=16), x=0)
    )
    _apply_theme(fig, with_secondary=bool(secondary_series))
    if x_start is not None and x_end is not None:
        fig.update_xaxes(range=[x_start, x_end])
    return fig


def make_area_chart(
    df: pd.DataFrame,
    series: str,
    title: str,
    date_col: str = "DATE",
    x_start=None,
    x_end=None,
) -> go.Figure:
    """
    Single-series filled area chart.
    """
    fig = go.Figure()

    if series in df.columns:
        fig.add_trace(
            go.Scatter(
                x=df[date_col],
                y=df[series],
                name=series.replace("_", " "),
                fill="tozeroy",
                line=dict(color="#e63946", width=2),
                fillcolor="rgba(230, 57, 70, 0.12)",
                connectgaps=False,
            )
        )

    fig.update_layout(
        title=dict(text=title, font=dict(color="#ffffff", size=16), x=0)
    )
    _apply_theme(fig)
    if x_start is not None and x_end is not None:
        fig.update_xaxes(range=[x_start, x_end])
    return fig


def add_recession_bands(fig: go.Figure, df: pd.DataFrame = None) -> go.Figure:
    """
    Overlay NBER recession shading on an existing Plotly figure.

    Parameters
    ----------
    fig : Plotly figure to annotate
    df  : included for API consistency; not used (recession dates are hardcoded)
    """
    for start, end in RECESSION_PERIODS:
        fig.add_vrect(
            x0=start,
            x1=end,
            fillcolor="rgba(255,255,255,0.04)",
            layer="below",
            line_width=0,
        )
    return fig


def render_summary_stats(
    df: pd.DataFrame,
    series_list: list,
    start_date,
    end_date,
) -> None:
    """
    Render a styled "Period Statistics" expander below charts.

    Parameters
    ----------
    df         : Full dashboard DataFrame (will be filtered internally).
    series_list: Column names to summarise.
    start_date : Python date object — start of selected range.
    end_date   : Python date object — end of selected range.
    """
    mask = (df["DATE"].dt.date >= start_date) & (df["DATE"].dt.date <= end_date)
    dff = df[mask].copy()

    rows = []
    for col in series_list:
        if col not in dff.columns:
            continue
        s = dff[col].dropna()
        if len(s) == 0:
            continue
        current  = s.iloc[-1]
        pmin     = s.min()
        pmax     = s.max()
        pmean    = s.mean()
        pct_chg  = ((current - s.iloc[0]) / abs(s.iloc[0]) * 100) if s.iloc[0] != 0 else 0.0
        rows.append((col, current, pmin, pmax, pmean, pct_chg))

    if not rows:
        return

    header = (
        "<tr style='background:#1a1a1a;'>"
        "<th style='padding:8px 12px;color:#e63946;text-align:left;font-size:11px;"
        "text-transform:uppercase;letter-spacing:0.08em;border-bottom:1px solid #333;'>Series</th>"
        "<th style='padding:8px 12px;color:#e63946;text-align:right;font-size:11px;"
        "text-transform:uppercase;letter-spacing:0.08em;border-bottom:1px solid #333;'>Current</th>"
        "<th style='padding:8px 12px;color:#e63946;text-align:right;font-size:11px;"
        "text-transform:uppercase;letter-spacing:0.08em;border-bottom:1px solid #333;'>Min</th>"
        "<th style='padding:8px 12px;color:#e63946;text-align:right;font-size:11px;"
        "text-transform:uppercase;letter-spacing:0.08em;border-bottom:1px solid #333;'>Max</th>"
        "<th style='padding:8px 12px;color:#e63946;text-align:right;font-size:11px;"
        "text-transform:uppercase;letter-spacing:0.08em;border-bottom:1px solid #333;'>Mean</th>"
        "<th style='padding:8px 12px;color:#e63946;text-align:right;font-size:11px;"
        "text-transform:uppercase;letter-spacing:0.08em;border-bottom:1px solid #333;'>Change</th>"
        "</tr>"
    )

    body = ""
    for col, current, pmin, pmax, pmean, pct_chg in rows:
        chg_color = "#4caf50" if pct_chg >= 0 else "#e63946"
        chg_sign  = "+" if pct_chg >= 0 else ""
        body += (
            f"<tr style='border-bottom:1px solid #1e1e1e;'>"
            f"<td style='padding:8px 12px;color:#cccccc;font-size:12px;'>"
            f"{col.replace('_', ' ')}</td>"
            f"<td style='padding:8px 12px;color:#ffffff;text-align:right;font-size:12px;'>"
            f"{current:.2f}</td>"
            f"<td style='padding:8px 12px;color:#888888;text-align:right;font-size:12px;'>"
            f"{pmin:.2f}</td>"
            f"<td style='padding:8px 12px;color:#888888;text-align:right;font-size:12px;'>"
            f"{pmax:.2f}</td>"
            f"<td style='padding:8px 12px;color:#888888;text-align:right;font-size:12px;'>"
            f"{pmean:.2f}</td>"
            f"<td style='padding:8px 12px;color:{chg_color};text-align:right;font-size:12px;"
            f"font-weight:600;'>{chg_sign}{pct_chg:.2f}%</td>"
            f"</tr>"
        )

    table_html = (
        "<div style='background:#111111;border:1px solid #1e1e1e;overflow:auto;'>"
        "<table style='width:100%;border-collapse:collapse;"
        "font-family:\"IBM Plex Mono\",monospace;'>"
        f"<thead>{header}</thead>"
        f"<tbody>{body}</tbody>"
        "</table></div>"
    )

    with st.expander("📊 Period Statistics"):
        st.markdown(table_html, unsafe_allow_html=True)
