# -*- coding: utf-8 -*-
"""
pages/6_Custom_Chart_Builder.py
Interactive chart builder — pick any series, date range, and chart type.
Includes auto dual-axis inference and pairwise Pearson correlation panel.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_loader import load_data, get_date_range
from utils.chart_helpers import add_recession_bands
from utils.styles import inject_styles
from utils.ticker import render_ticker

st.set_page_config(
    page_title="Custom Chart Builder | Austrian Economics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_styles()

# ── Theme constants ────────────────────────────────────────────────────────────
_BG        = "#0a0a0a"
_BG2       = "#141414"
_GRID      = "#222222"
_TEXT      = "#ffffff"
_MUTED     = "#888888"
_SERIES_COLORS = ["#e63946", "#ffffff", "#888888"]

# ── Load data ──────────────────────────────────────────────────────────────────
df = load_data()
min_date, max_date = get_date_range(df)
render_ticker(df)

# ── Column catalogue ───────────────────────────────────────────────────────────
# All numeric columns except DATE and Housing_Affordability_Index
_EXCLUDED = {"DATE", "Housing_Affordability_Index"}
_ALL_NUMERIC = [c for c in df.columns if c != "DATE" and c not in _EXCLUDED
                and pd.api.types.is_numeric_dtype(df[c])]

# Readable display names: replace underscores with spaces
_DISPLAY_NAMES = {c: c.replace("_", " ") for c in _ALL_NUMERIC}
_REVERSE_NAMES = {v: k for k, v in _DISPLAY_NAMES.items()}  # display → column


# ── Helpers ────────────────────────────────────────────────────────────────────
def _corr_interpretation(r: float) -> str:
    if r > 0.7:
        return "Strong positive"
    if r > 0.4:
        return "Moderate positive"
    if r >= -0.4:
        return "Weak / no relationship"
    if r >= -0.7:
        return "Moderate negative"
    return "Strong negative"


def _corr_color(r: float) -> str:
    return "#e63946" if abs(r) > 0.7 else "#ffffff"


def _build_figure(plot_df, selected_cols, chart_type, secondary_cols):
    """Build and theme a Plotly figure from scratch."""
    fig = go.Figure()

    for i, col in enumerate(selected_cols):
        color = _SERIES_COLORS[i % len(_SERIES_COLORS)]
        on_secondary = col in secondary_cols
        series_data = plot_df[["DATE", col]].dropna()

        if chart_type == "Area" and len(selected_cols) == 1:
            fig.add_trace(go.Scatter(
                x=series_data["DATE"],
                y=series_data[col],
                name=_DISPLAY_NAMES[col],
                fill="tozeroy",
                line=dict(color=color, width=2),
                fillcolor="rgba(230,57,70,0.12)",
                connectgaps=False,
                yaxis="y2" if on_secondary else "y",
            ))
        else:
            fig.add_trace(go.Scatter(
                x=series_data["DATE"],
                y=series_data[col],
                name=_DISPLAY_NAMES[col],
                line=dict(color=color, width=2),
                connectgaps=False,
                yaxis="y2" if on_secondary else "y",
            ))

    _axis_base = dict(
        gridcolor=_GRID,
        showgrid=True,
        zeroline=False,
        tickfont=dict(color=_MUTED),
        title_font=dict(color=_MUTED),
    )

    layout = dict(
        paper_bgcolor=_BG,
        plot_bgcolor=_BG,
        font=dict(color=_TEXT, family="sans-serif", size=12),
        xaxis=dict(**_axis_base),
        yaxis=dict(**_axis_base),
        legend=dict(
            bgcolor=_BG2,
            bordercolor=_GRID,
            borderwidth=1,
            font=dict(color=_TEXT, size=11),
        ),
        margin=dict(l=60, r=60, t=60, b=40),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=_BG2, bordercolor=_GRID, font_color=_TEXT),
        title=dict(
            text="Custom Chart",
            font=dict(color=_TEXT, size=16),
            x=0,
        ),
    )

    if secondary_cols:
        layout["yaxis2"] = dict(
            overlaying="y",
            side="right",
            **_axis_base,
            showgrid=False,
        )

    fig.update_layout(**layout)
    return fig


def _infer_secondary(selected_cols, plot_df):
    """
    Return the set of column names that should go on the secondary (right) axis.
    Rules:
    - Compute mean of non-NaN values for each series.
    - If max_mean / min_mean > 10: put the series with the largest mean on left,
      all others on right.
    - Otherwise: all on left (empty set returned).
    For 3 series where two are close and one is far: the outlier goes on secondary.
    """
    if len(selected_cols) < 2:
        return set()

    means = {}
    for col in selected_cols:
        vals = plot_df[col].dropna()
        if len(vals) > 0:
            means[col] = vals.mean()

    if len(means) < 2:
        return set()

    max_mean = max(means.values())
    min_mean = min(means.values())

    if min_mean == 0 or (max_mean / min_mean) <= 10:
        return set()

    # Put the series with the largest mean on left; all others on right.
    # (Handles 2-series and 3-series cases uniformly.)
    max_col = max(means, key=lambda c: means[c])
    secondary = {c for c in selected_cols if c != max_col}
    return secondary


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom: 32px;">
    <h1>Custom Chart Builder</h1>
    <div style="width: 60px; height: 2px; background: #e63946; margin-top: 8px;"></div>
    <p style="color: #888888; font-size: 13px; letter-spacing: 0.04em; margin-top: 12px;">
        Select any combination of series, adjust the date range, and explore relationships the other pages don't show.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Two-column control strip ───────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    selected_display = st.multiselect(
        "Select Series (up to 3)",
        options=[_DISPLAY_NAMES[c] for c in _ALL_NUMERIC],
        default=[],
        placeholder="Choose series...",
    )
    selected_cols = [_REVERSE_NAMES[d] for d in selected_display]

    # Chart type — Area only when exactly 1 series
    if len(selected_cols) != 1:
        chart_type = "Line"
        if len(selected_cols) > 1:
            st.caption("Chart type fixed to Line when multiple series are selected.")
    else:
        chart_type = st.radio(
            "Chart Type",
            options=["Line", "Area"],
            horizontal=True,
        )

with col_right:
    date_range = st.slider(
        "Date Range",
        min_value=min_date.to_pydatetime().date(),
        max_value=max_date.to_pydatetime().date(),
        value=(min_date.to_pydatetime().date(), max_date.to_pydatetime().date()),
        format="YYYY-MM",
    )
    show_recession = st.checkbox("Show recession bands", value=True)
    show_table = st.checkbox("Show data table below chart", value=False)

# ── Apply date filter ──────────────────────────────────────────────────────────
start_date, end_date = date_range
mask = (df["DATE"].dt.date >= start_date) & (df["DATE"].dt.date <= end_date)
dff = df[mask].copy()

st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)

# ── Guard: too many series ─────────────────────────────────────────────────────
if len(selected_cols) > 3:
    st.warning("Please select a maximum of 3 series.")
    st.stop()

# ── Guard: nothing selected ────────────────────────────────────────────────────
if len(selected_cols) == 0:
    st.info("Select at least one series to build a chart.")
    st.stop()

# ── Validate series have data in range ────────────────────────────────────────
valid_cols = []
for col in selected_cols:
    if dff[col].dropna().empty:
        st.warning(
            f"**{_DISPLAY_NAMES[col]}** has no data in the selected date range."
        )
    else:
        valid_cols.append(col)

if not valid_cols:
    st.stop()

# ── Dual-axis inference ────────────────────────────────────────────────────────
secondary_cols = _infer_secondary(valid_cols, dff)

# ── Build and render chart ─────────────────────────────────────────────────────
fig = _build_figure(dff, valid_cols, chart_type, secondary_cols)

if show_recession:
    add_recession_bands(fig)

fig.update_xaxes(range=[start_date, end_date])
st.plotly_chart(fig, use_container_width=True)

if secondary_cols:
    st.caption(
        "Note: Secondary Y-axis applied automatically due to scale difference between series."
    )

# ── Correlation panel ──────────────────────────────────────────────────────────
if len(valid_cols) >= 2:
    pairs = []
    for i in range(len(valid_cols)):
        for j in range(i + 1, len(valid_cols)):
            a, b = valid_cols[i], valid_cols[j]
            pair_df = dff[["DATE", a, b]].dropna()
            if len(pair_df) >= 3:
                r = pair_df[a].corr(pair_df[b])
                pairs.append((a, b, r))

    if pairs:
        st.markdown(
            "<h4 style='color:#ffffff; margin-top:8px; margin-bottom:8px;'>"
            "Pairwise Correlation</h4>",
            unsafe_allow_html=True,
        )

        # Build HTML table for styled correlation values
        rows_html = ""
        for a, b, r in pairs:
            r_color = _corr_color(r)
            interp = _corr_interpretation(r)
            rows_html += (
                f"<tr>"
                f"<td style='padding:8px 14px;color:#ffffff;border-bottom:1px solid {_GRID};'>"
                f"{_DISPLAY_NAMES[a]}</td>"
                f"<td style='padding:8px 14px;color:#ffffff;border-bottom:1px solid {_GRID};'>"
                f"{_DISPLAY_NAMES[b]}</td>"
                f"<td style='padding:8px 14px;color:{r_color};border-bottom:1px solid {_GRID};"
                f"text-align:right;font-family:monospace;font-weight:700;'>"
                f"{r:+.3f}</td>"
                f"<td style='padding:8px 14px;color:{_MUTED};border-bottom:1px solid {_GRID};'>"
                f"{interp}</td>"
                f"</tr>"
            )

        corr_html = f"""
<div style="background:{_BG2};border:1px solid {_GRID};border-radius:4px;
            overflow:hidden;margin-bottom:16px;max-width:720px;">
  <table style="width:100%;border-collapse:collapse;">
    <thead>
      <tr style="background:{_BG};">
        <th style="padding:8px 14px;color:{_MUTED};text-align:left;font-size:11px;
                   text-transform:uppercase;letter-spacing:1.2px;
                   border-bottom:1px solid {_GRID};">Series A</th>
        <th style="padding:8px 14px;color:{_MUTED};text-align:left;font-size:11px;
                   text-transform:uppercase;letter-spacing:1.2px;
                   border-bottom:1px solid {_GRID};">Series B</th>
        <th style="padding:8px 14px;color:{_MUTED};text-align:right;font-size:11px;
                   text-transform:uppercase;letter-spacing:1.2px;
                   border-bottom:1px solid {_GRID};">Correlation</th>
        <th style="padding:8px 14px;color:{_MUTED};text-align:left;font-size:11px;
                   text-transform:uppercase;letter-spacing:1.2px;
                   border-bottom:1px solid {_GRID};">Interpretation</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>
</div>
"""
        st.markdown(corr_html, unsafe_allow_html=True)

# ── Data table ─────────────────────────────────────────────────────────────────
if show_table:
    st.markdown(
        "<h4 style='color:#ffffff; margin-top:8px; margin-bottom:8px;'>Data Table</h4>",
        unsafe_allow_html=True,
    )
    display_df = dff[["DATE"] + valid_cols].copy()
    display_df["DATE"] = display_df["DATE"].dt.strftime("%Y-%m")
    display_df = display_df.rename(columns=_DISPLAY_NAMES)
    st.dataframe(display_df, use_container_width=True)
