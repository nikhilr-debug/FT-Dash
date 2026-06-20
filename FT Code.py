import streamlit as st
import pandas as pd
import requests
import datetime
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Vahan Performance Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Design tokens (from reference HTML) ───────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg:       #0f1117;
  --surface:  #1a1d27;
  --surface2: #21263a;
  --surface3: #2a2f45;
  --br:       rgba(255,255,255,0.07);
  --br2:      rgba(255,255,255,0.13);
  --text:     #eaeaea;
  --muted:    #8b8fa8;
  --faint:    #4a4f6a;
  --r:        8px;
  --rl:       12px;

  --red:      #ff6b6b;
  --red-bg:   #2d1515;
  --red-b:    #e05252;
  --amber:    #ffc97a;
  --amber-bg: #2d1e07;
  --amber-b:  #d4891a;
  --green:    #6dd67b;
  --green-bg: #102216;
  --green-b:  #4a9e2f;
  --blue:     #7cb9f8;
  --blue-bg:  #0d1e38;
  --blue-b:   #2f7dd4;
  --purple:   #b08cff;
  --purple-bg:#1e1435;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-size: 13px;
  line-height: 1.5;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container {
  padding: 1.5rem 2rem 4rem !important;
  max-width: 1380px !important;
}
/* Remove default element gaps */
div[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* ── Header ── */
.dash-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.25rem;
  padding-bottom: 1rem;
  border-bottom: 0.5px solid var(--br2);
}
.dash-title {
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text);
}
.dash-title span { color: var(--blue); }
.dash-meta {
  font-size: 0.75rem;
  color: var(--muted);
  margin-top: 2px;
}
.live-dot {
  display: inline-block;
  width: 7px; height: 7px;
  background: var(--green-b);
  border-radius: 50%;
  margin-right: 5px;
  box-shadow: 0 0 6px var(--green-b);
  animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }

/* ── Section label ── */
.sec-ttl {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--muted);
  margin: 1.4rem 0 .65rem;
  display: flex;
  align-items: center;
  gap: 8px;
}
.sec-ttl-line { flex: 1; height: 0.5px; background: var(--br); }

/* ── KPI cards ── */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 1rem;
}
.kpi {
  background: var(--surface);
  border: 0.5px solid var(--br);
  border-radius: var(--rl);
  padding: 14px 16px;
  position: relative;
  overflow: hidden;
}
.kpi::before {
  content:'';
  position:absolute;
  top:0;left:0;right:0;
  height:2px;
  background: linear-gradient(90deg, var(--blue-b), var(--purple));
}
.kpi-lbl {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .07em;
  color: var(--muted);
  margin-bottom: 6px;
}
.kpi-val {
  font-size: 24px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  letter-spacing: -.02em;
  line-height: 1;
  color: var(--text);
}
.kpi-sub { font-size: 11px; margin-top: 6px; color: var(--muted); }

/* ── Pill badges ── */
.pill {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 700;
  white-space: nowrap;
}
.pr { background: var(--red-bg);    color: var(--red); }
.pg { background: var(--green-bg);  color: var(--green); }
.pa { background: var(--amber-bg);  color: var(--amber); }
.pb { background: var(--blue-bg);   color: var(--blue); }
.pz { background: var(--surface2);  color: var(--muted); }

/* ── Tables ── */
.tw {
  background: var(--surface);
  border: 0.5px solid var(--br);
  border-radius: var(--rl);
  overflow: hidden;
  margin-bottom: 12px;
}
.dash-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.dash-table th {
  text-align: left;
  font-size: 10px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: .05em;
  padding: 8px 12px;
  border-bottom: 0.5px solid var(--br2);
  background: var(--surface2);
  font-weight: 700;
  white-space: nowrap;
}
.dash-table td {
  padding: 8px 12px;
  border-bottom: 0.5px solid var(--br);
  color: var(--text);
  white-space: nowrap;
  vertical-align: middle;
}
.dash-table tr:last-child td { border-bottom: none; }
.dash-table tr:hover td { background: var(--surface2); }
.td-r { text-align: right; }
.td-bold { font-weight: 600; }
.td-muted { color: var(--muted); font-size: 11px; }
.n { text-align: right; font-variant-numeric: tabular-nums; }

/* ── Mini bar inside table ── */
.bwrap {
  height: 4px;
  background: var(--surface3);
  border-radius: 2px;
  display: inline-block;
  vertical-align: middle;
  width: 56px;
  margin-right: 6px;
}
.bfill { height: 4px; border-radius: 2px; background: var(--blue-b); }

/* ── Funnel stages ── */
.fn-stages {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-bottom: 10px;
}
.fn-stg {
  background: var(--surface);
  border: 0.5px solid var(--br);
  border-radius: var(--r);
  padding: 13px 14px;
  text-align: center;
}
.fn-val {
  font-size: 22px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
.fn-lbl {
  font-size: 10px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: .05em;
  margin: 4px 0 3px;
}
.fn-delta { font-size: 12px; font-weight: 600; margin-top: 3px; }

/* ── RCA ── */
.rca-card {
  background: var(--surface);
  border: 0.5px solid var(--br);
  border-radius: var(--rl);
  padding: 16px 20px;
  margin-bottom: 10px;
}
.rca-ttl {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--muted);
  margin-bottom: 10px;
}
.rca-body { font-size: 13px; line-height: 1.75; color: var(--text); }
.rca-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 7px 0;
  border-bottom: 0.5px solid var(--br);
  font-size: 12.5px;
}
.rca-item:last-child { border-bottom: none; }
.rca-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
}
.dot-g { background: var(--green-b); box-shadow: 0 0 5px var(--green-b); }
.dot-r { background: var(--red-b);   box-shadow: 0 0 5px var(--red-b); }
.dot-a { background: var(--amber-b); }

/* ── chart card ── */
.chart-card {
  background: var(--surface);
  border: 0.5px solid var(--br);
  border-radius: var(--rl);
  padding: 14px 16px;
  margin-bottom: 12px;
}
.chart-hdr {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}
.chart-title { font-size: 12px; font-weight: 700; color: var(--text); }
.chart-sub   { font-size: 11px; color: var(--muted); }

/* Streamlit tab override */
button[data-baseweb="tab"] {
  background: transparent !important;
  color: var(--muted) !important;
  font-weight: 600 !important;
  font-size: 12px !important;
  border-radius: var(--r) !important;
  padding: 6px 16px !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
  background: var(--surface) !important;
  color: var(--text) !important;
  border: 0.5px solid var(--br) !important;
}
div[data-baseweb="tab-list"] {
  background: var(--surface2) !important;
  border: 0.5px solid var(--br) !important;
  border-radius: var(--rl) !important;
  padding: 3px !important;
  gap: 2px !important;
}
div[data-baseweb="tab-highlight"] { display: none !important; }
div[data-baseweb="tab-border"]    { display: none !important; }

/* Streamlit selectbox */
div[data-baseweb="select"] > div {
  background: var(--surface2) !important;
  border: 0.5px solid var(--br2) !important;
  border-radius: var(--r) !important;
  color: var(--text) !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── Plotly dark theme ──────────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#8b8fa8", size=11),
    margin=dict(l=0, r=0, t=28, b=0),
    showlegend=True,
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02,
        xanchor="right", x=1,
        font=dict(size=10), bgcolor="rgba(0,0,0,0)",
    ),
    xaxis=dict(
        showgrid=False, zeroline=False,
        tickfont=dict(size=10, color="#8b8fa8"),
        linecolor="rgba(255,255,255,0.07)",
    ),
    yaxis=dict(
        showgrid=True, gridcolor="rgba(255,255,255,0.05)",
        zeroline=False, tickfont=dict(size=10, color="#8b8fa8"),
    ),
    bargap=0.35,
)

BAR_CUR  = "#2f7dd4"
BAR_PRV  = "#4a4f6a"
BAR_POS  = "#4a9e2f"
BAR_NEG  = "#e05252"

# ── Data fetch ─────────────────────────────────────────────────────────────────
API_URL = (
    "https://redash.vahan.link/api/queries/17613/results.json"
    "?api_key=4aFm2iOoyx8I91svQccdeZr0jmaiUsMFSRinZcmu"
)

@st.cache_data(ttl=3600)
def fetch_data():
    try:
        r = requests.get(API_URL, timeout=30)
        r.raise_for_status()
        rows = r.json()["query_result"]["data"]["rows"]
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"⚠️ Failed to fetch data: {e}")
        return pd.DataFrame()

DATE_COLS = [
    "referral_date_si", "marked_unique", "activation_date", "first_date_of_work",
    "5th_order_date", "10th_order_date", "20th_order_date", "30th_order_date",
    "50th_order_date", "60th_order_date", "80th_order_date", "100th_order_date",
    "120th_order_date", "150th_order_date", "200th_order_date",
]

def parse_dates(df):
    for c in DATE_COLS:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce").dt.date
    return df

# ── Time windows ───────────────────────────────────────────────────────────────
def get_windows(mode):
    today     = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    if mode == "WTD":
        dow       = today.weekday()
        cur_start = today - datetime.timedelta(days=dow)
        cur_end   = yesterday
        prev_start = cur_start - datetime.timedelta(weeks=1)
        prev_end   = cur_end   - datetime.timedelta(weeks=1)
    else:
        cur_start  = today.replace(day=1)
        cur_end    = yesterday
        pm         = today.month - 1 or 12
        py         = today.year if today.month > 1 else today.year - 1
        prev_start = today.replace(year=py, month=pm, day=1)
        offset     = (cur_end - cur_start).days
        prev_end   = prev_start + datetime.timedelta(days=offset)
    return cur_start, cur_end, prev_start, prev_end

# ── Helpers ────────────────────────────────────────────────────────────────────
def fmt(n):
    if pd.isna(n): return "—"
    n = int(n)
    if abs(n) >= 1_000_000: return f"{n/1e6:.1f}M"
    if abs(n) >= 1_000:     return f"{n:,}"
    return str(n)

def pill(val, is_pct=False, is_pp=False):
    if pd.isna(val) or (isinstance(val, float) and not np.isfinite(val)):
        return '<span class="pill pz">—</span>'
    sym  = "+" if val > 0 else ""
    cls  = "pg" if val > 0 else ("pr" if val < 0 else "pz")
    unit = "pp" if is_pp else ("%" if is_pct else "")
    txt  = f"{sym}{val:.1f}{unit}" if (is_pct or is_pp) else f"{sym}{int(val):,}"
    return f'<span class="pill {cls}">{txt}</span>'

def count_in(df, col, s, e):
    if col not in df.columns: return 0
    m = df[col].notna() & (df[col] >= s) & (df[col] <= e)
    return int(m.sum())

def agg(df, col, s, e, by):
    if col not in df.columns or by not in df.columns:
        return pd.Series(dtype=int, name=col)
    sub = df[df[col].notna() & (df[col] >= s) & (df[col] <= e)]
    return sub.groupby(by)[col].count()

def compare(df, col, cs, ce, ps, pe, by):
    c = agg(df, col, cs, ce, by).rename("cur")
    p = agg(df, col, ps, pe, by).rename("prv")
    r = pd.concat([c, p], axis=1).fillna(0).astype(int)
    r["delta"] = r["cur"] - r["prv"]
    r["pct"]   = np.where(r["prv"] > 0, r["delta"] / r["prv"] * 100, np.nan)
    return r.sort_values("delta")

def conv(num, den): return (num / den * 100) if den > 0 else 0.0

def kpi_html(label, value, sub="", pill_html=""):
    return f"""
    <div class="kpi">
      <div class="kpi-lbl">{label}</div>
      <div class="kpi-val">{value}</div>
      <div class="kpi-sub">{sub} {pill_html}</div>
    </div>"""

def section(title):
    st.markdown(
        f'<div class="sec-ttl">{title}<div class="sec-ttl-line"></div></div>',
        unsafe_allow_html=True)

def bar_chart(df_in, x_col, y_cols, labels, colors, title="", height=280):
    """Side-by-side grouped bar chart via Plotly."""
    fig = go.Figure()
    for y, lbl, col in zip(y_cols, labels, colors):
        fig.add_trace(go.Bar(
            x=df_in[x_col], y=df_in[y], name=lbl,
            marker_color=col, marker_line_width=0,
        ))
    layout = dict(**PLOT_LAYOUT)
    layout["height"] = height
    layout["title"]  = dict(text=title, font=dict(size=12, color="#eaeaea"), x=0)
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def delta_bar_chart(df_in, x_col, delta_col, title="", height=260):
    """Single bar chart coloured by positive/negative delta."""
    vals  = df_in[delta_col].values
    cols  = [BAR_POS if v >= 0 else BAR_NEG for v in vals]
    fig   = go.Figure(go.Bar(
        x=df_in[x_col], y=vals,
        marker_color=cols, marker_line_width=0,
        text=[f"{'+' if v>=0 else ''}{int(v):,}" for v in vals],
        textposition="outside",
        textfont=dict(size=10, color="#8b8fa8"),
    ))
    layout = dict(**PLOT_LAYOUT)
    layout["height"]  = height
    layout["title"]   = dict(text=title, font=dict(size=12, color="#eaeaea"), x=0)
    layout["showlegend"] = False
    layout["yaxis"]["showgrid"] = True
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def funnel_bar(stages_data, title="Funnel Volume Comparison", height=300):
    """Grouped bar for funnel stages."""
    labels = [s["label"] for s in stages_data]
    cur_v  = [s["cur"]   for s in stages_data]
    prv_v  = [s["prv"]   for s in stages_data]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Previous", x=labels, y=prv_v,
                         marker_color=BAR_PRV, marker_line_width=0))
    fig.add_trace(go.Bar(name="Current",  x=labels, y=cur_v,
                         marker_color=BAR_CUR, marker_line_width=0))
    layout = dict(**PLOT_LAYOUT)
    layout["height"] = height
    layout["title"]  = dict(text=title, font=dict(size=12, color="#eaeaea"), x=0)
    fig.update_layout(**layout)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════
with st.spinner("Fetching live data…"):
    raw = fetch_data()

if raw.empty:
    st.warning("No data returned. Check API connectivity.")
    st.stop()

df = parse_dates(raw.copy())
ft = "first_date_of_work"

# ── Header ─────────────────────────────────────────────────────────────────────
today     = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

h_left, h_right = st.columns([4, 1])
with h_left:
    st.markdown(f"""
    <div class="dash-header">
      <div>
        <div class="dash-title">Vahan <span>Performance</span> Dashboard</div>
        <div class="dash-meta">
          <span class="live-dot"></span>Live · as of {yesterday.strftime('%d %b %Y')} ·
          {len(df):,} records loaded
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

with h_right:
    mode = st.selectbox("Period", ["WTD", "MTD"], label_visibility="collapsed")

cs, ce, ps, pe = get_windows(mode)
period_str = f"{cs.strftime('%d %b')} – {ce.strftime('%d %b')}  vs  {ps.strftime('%d %b')} – {pe.strftime('%d %b')}"
st.markdown(f'<span class="pill pb" style="font-size:11px;margin-bottom:1rem;display:inline-block">{period_str}</span>',
            unsafe_allow_html=True)

# ── Global KPIs ────────────────────────────────────────────────────────────────
cur_tot = count_in(df, ft, cs, ce)
prv_tot = count_in(df, ft, ps, pe)
dlt_tot = cur_tot - prv_tot
pct_tot = (dlt_tot / prv_tot * 100) if prv_tot > 0 else np.nan

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📦  Client View",
    "🗺️  Region & AM",
    "🔬  Funnel Health",
    "🤖  AI Summary & RCA",
])

# ════════════════════════════════════════════════════════════
# TAB 1 — CLIENT VIEW
# ════════════════════════════════════════════════════════════
with tab1:
    # KPI row
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(kpi_html("Current Period FT", fmt(cur_tot),
                                   f"{cs.strftime('%d %b')} – {ce.strftime('%d %b')}"), unsafe_allow_html=True)
    with k2: st.markdown(kpi_html("Previous Period FT", fmt(prv_tot),
                                   f"{ps.strftime('%d %b')} – {pe.strftime('%d %b')}"), unsafe_allow_html=True)
    with k3: st.markdown(kpi_html("Δ Volume", fmt(dlt_tot), "absolute", pill(dlt_tot)), unsafe_allow_html=True)
    with k4: st.markdown(kpi_html("Δ %", f"{pct_tot:+.1f}%" if np.isfinite(pct_tot) else "—",
                                   "period-over-period", pill(pct_tot, is_pct=True)), unsafe_allow_html=True)
    st.markdown("<div style='margin-top:.5rem'></div>", unsafe_allow_html=True)

    # Client comparison data
    cl_df = compare(df, ft, cs, ce, ps, pe, "company_name").reset_index()
    cl_df.columns = ["Client", "cur", "prv", "delta", "pct"]

    # Bar chart: grouped cur vs prv by client
    section("Client Volume — Current vs Previous")
    chart_df = cl_df.sort_values("cur", ascending=False).head(15)
    bar_chart(chart_df, "Client", ["prv", "cur"], ["Previous", "Current"],
              [BAR_PRV, BAR_CUR], height=300)

    # Delta bar chart
    section("Client Volume Change (Δ)")
    delta_bar_chart(cl_df.sort_values("delta"), "Client", "delta", height=260)

    # Summary table
    section("Client Performance Table")
    max_cur = cl_df["cur"].max() or 1
    tbl = '<div class="tw"><table class="dash-table"><thead><tr>'
    tbl += '<th>Client</th><th class="n">Current</th><th class="n">Previous</th>'
    tbl += '<th class="n">Δ Volume</th><th class="n">Δ %</th><th>Share</th></tr></thead><tbody>'
    for _, r in cl_df.sort_values("delta").iterrows():
        bar_w = int(min(100, r["cur"] / max_cur * 100)) if max_cur > 0 else 0
        tbl += f"""<tr>
          <td class="td-bold">{r['Client']}</td>
          <td class="n">{fmt(r['cur'])}</td>
          <td class="n td-muted">{fmt(r['prv'])}</td>
          <td class="n">{pill(r['delta'])}</td>
          <td class="n">{pill(r['pct'], is_pct=True)}</td>
          <td>
            <div class="bwrap"><div class="bfill" style="width:{bar_w}%"></div></div>
            <span style="font-size:10px;color:var(--muted)">{r['cur']/cur_tot*100:.0f}%</span>
          </td>
        </tr>"""
    tbl += "</tbody></table></div>"
    st.markdown(tbl, unsafe_allow_html=True)

    # Drill-down
    section("Drill-Down: Client → Region → VL Partner")
    all_clients = sorted(df["company_name"].dropna().unique()) if "company_name" in df.columns else []
    sel = st.selectbox("Select client", all_clients, label_visibility="collapsed")
    if sel:
        sub = df[df["company_name"] == sel]
        dc1, dc2 = st.columns(2)

        with dc1:
            section("By Region")
            rg = compare(sub, ft, cs, ce, ps, pe, "region").reset_index()
            if not rg.empty:
                rg.columns = ["Region", "cur", "prv", "delta", "pct"]
                bar_chart(rg, "Region", ["prv", "cur"], ["Previous", "Current"],
                          [BAR_PRV, BAR_CUR], height=220)
        with dc2:
            section("By VL Partner")
            if "vl_name" in sub.columns:
                vl = compare(sub, ft, cs, ce, ps, pe, "vl_name").reset_index()
                if not vl.empty:
                    vl.columns = ["VL", "cur", "prv", "delta", "pct"]
                    bar_chart(vl.sort_values("cur", ascending=False).head(12),
                              "VL", ["prv", "cur"], ["Previous", "Current"],
                              [BAR_PRV, BAR_CUR], height=220)

# ════════════════════════════════════════════════════════════
# TAB 2 — REGION & AM
# ════════════════════════════════════════════════════════════
with tab2:
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(kpi_html("Current FT", fmt(cur_tot)), unsafe_allow_html=True)
    with k2: st.markdown(kpi_html("Previous FT", fmt(prv_tot)), unsafe_allow_html=True)
    with k3: st.markdown(kpi_html("Δ Volume", fmt(dlt_tot), "", pill(dlt_tot)), unsafe_allow_html=True)
    with k4: st.markdown(kpi_html("Δ %", f"{pct_tot:+.1f}%" if np.isfinite(pct_tot) else "—",
                                   "", pill(pct_tot, is_pct=True)), unsafe_allow_html=True)
    st.markdown("<div style='margin-top:.5rem'></div>", unsafe_allow_html=True)

    def render_group(col_name, display_name, parent_col=None):
        ctx = parent_col if parent_col else st
        if col_name not in df.columns:
            ctx.info(f"`{col_name}` not in dataset.")
            return
        grp = compare(df, ft, cs, ce, ps, pe, col_name).reset_index()
        if grp.empty:
            ctx.info("No data.")
            return
        grp.columns = [display_name, "cur", "prv", "delta", "pct"]

        # Chart
        section(f"{display_name} — Volume Comparison")
        bar_chart(grp.sort_values("cur", ascending=False).head(12),
                  display_name, ["prv", "cur"], ["Previous", "Current"],
                  [BAR_PRV, BAR_CUR], height=240)

        # Delta chart
        section(f"{display_name} — Change (Δ)")
        delta_bar_chart(grp.sort_values("delta"), display_name, "delta", height=220)

        # Table
        section(f"{display_name} Table")
        tbl = '<div class="tw"><table class="dash-table"><thead><tr>'
        tbl += f'<th>{display_name}</th><th class="n">Current</th><th class="n">Previous</th>'
        tbl += '<th class="n">Δ</th><th class="n">Δ %</th></tr></thead><tbody>'
        for _, r in grp.sort_values("delta").iterrows():
            tbl += f"""<tr>
              <td class="td-bold">{r[display_name]}</td>
              <td class="n">{fmt(r['cur'])}</td>
              <td class="n td-muted">{fmt(r['prv'])}</td>
              <td class="n">{pill(r['delta'])}</td>
              <td class="n">{pill(r['pct'], is_pct=True)}</td>
            </tr>"""
        tbl += "</tbody></table></div>"
        if parent_col:
            parent_col.markdown(tbl, unsafe_allow_html=True)
        else:
            st.markdown(tbl, unsafe_allow_html=True)

    col_r, col_a = st.columns(2)
    with col_r: render_group("region",  "Region",          col_r)
    with col_a: render_group("am_name", "Account Manager", col_a)

    section("Source Channel & Product Category")
    col_s, col_p = st.columns(2)
    with col_s: render_group("lead_source",        "Source Channel",    col_s)
    with col_p: render_group("lead_referral_type", "Product Category",  col_p)

# ════════════════════════════════════════════════════════════
# TAB 3 — FUNNEL HEALTH
# ════════════════════════════════════════════════════════════
with tab3:
    stages = [
        ("referral_date_si", "Leads"),
        ("marked_unique",    "Unique Leads"),
        ("activation_date",  "Onboarded"),
        ("first_date_of_work", "Placements (FT)"),
    ]
    cur_c = {lbl: count_in(df, col, cs, ce) for col, lbl in stages}
    prv_c = {lbl: count_in(df, col, ps, pe) for col, lbl in stages}

    # Stage cards
    section("Funnel Volume — Current Period")
    cols_f = st.columns(4)
    stage_colors = ["#2f7dd4", "#b08cff", "#d4891a", "#4a9e2f"]
    for i, (_, lbl) in enumerate(stages):
        cv, pv = cur_c[lbl], prv_c[lbl]
        d = cv - pv
        p = (d / pv * 100) if pv > 0 else np.nan
        d_html = pill(d)
        with cols_f[i]:
            st.markdown(f"""
            <div class="fn-stg" style="border-top:2px solid {stage_colors[i]}">
              <div class="fn-val" style="color:{stage_colors[i]}">{fmt(cv)}</div>
              <div class="fn-lbl">{lbl}</div>
              <div class="fn-lmtd" style="color:var(--muted)">Prev: {fmt(pv)}</div>
              <div class="fn-delta">{d_html}</div>
            </div>""", unsafe_allow_html=True)

    # Grouped funnel bar chart
    section("Funnel Volume Comparison")
    stage_data = [{"label": lbl, "cur": cur_c[lbl], "prv": prv_c[lbl]} for _, lbl in stages]
    funnel_bar(stage_data, height=300)

    # Conversion rates table
    conv_stages = [
        ("Leads → Unique",     "Leads",        "Unique Leads"),
        ("Unique → Onboarded", "Unique Leads", "Onboarded"),
        ("Onboarded → FT",     "Onboarded",    "Placements (FT)"),
    ]
    section("Conversion Rates & Stage Drops")
    conv_tbl = '<div class="tw"><table class="dash-table"><thead><tr>'
    conv_tbl += '<th>Stage</th><th class="n">Current Rate</th><th class="n">Previous Rate</th>'
    conv_tbl += '<th class="n">Δ (pp)</th><th>Bar</th></tr></thead><tbody>'

    conv_chart_data = []
    for name, num_lbl, den_lbl in conv_stages:
        cr = conv(cur_c[num_lbl], cur_c[den_lbl])
        pr = conv(prv_c[num_lbl], prv_c[den_lbl])
        pp = cr - pr
        bar_w = int(min(100, cr))
        bar_col = "#4a9e2f" if pp >= 0 else "#e05252"
        conv_tbl += f"""<tr>
          <td class="td-bold">{name}</td>
          <td class="n">{cr:.1f}%</td>
          <td class="n td-muted">{pr:.1f}%</td>
          <td class="n">{pill(pp, is_pp=True)}</td>
          <td>
            <div class="bwrap" style="width:80px">
              <div class="bfill" style="width:{bar_w}%;background:{bar_col}"></div>
            </div>
            <span style="font-size:10px;color:var(--muted)">{cr:.0f}%</span>
          </td>
        </tr>"""
        conv_chart_data.append({"Stage": name, "Current": cr, "Previous": pr, "Δpp": pp})

    conv_tbl += "</tbody></table></div>"
    st.markdown(conv_tbl, unsafe_allow_html=True)

    # Conversion rate bar chart
    section("Conversion Rate Chart")
    if conv_chart_data:
        cdf = pd.DataFrame(conv_chart_data)
        bar_chart(cdf, "Stage", ["Previous", "Current"], ["Previous Rate", "Current Rate"],
                  [BAR_PRV, BAR_CUR], height=240)

    # Milestone volumes
    ms_cols = [c for c in [
        "5th_order_date","10th_order_date","20th_order_date","30th_order_date",
        "50th_order_date","60th_order_date","80th_order_date","100th_order_date",
        "120th_order_date","150th_order_date","200th_order_date"
    ] if c in df.columns]

    if ms_cols:
        section("Progressive Milestone Volumes")
        ms_rows = []
        for mc in ms_cols:
            lbl = mc.replace("_order_date","th Order").replace("_date","").replace("_"," ")
            cv = count_in(df, mc, cs, ce)
            pv = count_in(df, mc, ps, pe)
            ms_rows.append({"Milestone": lbl, "cur": cv, "prv": pv, "delta": cv - pv})
        ms_df = pd.DataFrame(ms_rows)
        bar_chart(ms_df, "Milestone", ["prv", "cur"], ["Previous", "Current"],
                  [BAR_PRV, BAR_CUR], height=260)

        ms_tbl = '<div class="tw"><table class="dash-table"><thead><tr>'
        ms_tbl += '<th>Milestone</th><th class="n">Current</th><th class="n">Previous</th><th class="n">Δ</th>'
        ms_tbl += '</tr></thead><tbody>'
        for r in ms_rows:
            ms_tbl += f"""<tr>
              <td>{r['Milestone']}</td>
              <td class="n">{fmt(r['cur'])}</td>
              <td class="n td-muted">{fmt(r['prv'])}</td>
              <td class="n">{pill(r['delta'])}</td>
            </tr>"""
        ms_tbl += "</tbody></table></div>"
        st.markdown(ms_tbl, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 4 — AI SUMMARY & RCA
# ════════════════════════════════════════════════════════════
with tab4:
    # Rebuild comparison frames
    cl_rca  = compare(df, ft, cs, ce, ps, pe, "company_name").reset_index()
    rg_rca  = compare(df, ft, cs, ce, ps, pe, "region").reset_index() if "region" in df.columns else pd.DataFrame()
    am_rca  = compare(df, ft, cs, ce, ps, pe, "am_name").reset_index() if "am_name" in df.columns else pd.DataFrame()

    # Build mover pool
    movers = []
    for _, r in cl_rca.iterrows():
        movers.append({"dim": "Client", "name": r.iloc[0], "delta": r["delta"], "pct": r["pct"]})
    if not rg_rca.empty:
        for _, r in rg_rca.iterrows():
            movers.append({"dim": "Region", "name": r.iloc[0], "delta": r["delta"], "pct": r["pct"]})
    if not am_rca.empty:
        for _, r in am_rca.iterrows():
            movers.append({"dim": "AM", "name": r.iloc[0], "delta": r["delta"], "pct": r["pct"]})

    mv_df = pd.DataFrame(movers).dropna(subset=["delta"])
    top3  = mv_df.nlargest(3, "delta")
    bot3  = mv_df.nsmallest(3, "delta")

    # Bottlenecks
    bottlenecks = []
    cur_c2 = {lbl: count_in(df, col, cs, ce) for col, lbl in stages}
    prv_c2 = {lbl: count_in(df, col, ps, pe) for col, lbl in stages}
    for name, num_lbl, den_lbl in conv_stages:
        cr = conv(cur_c2[num_lbl], cur_c2[den_lbl])
        pr = conv(prv_c2[num_lbl], prv_c2[den_lbl])
        pp = cr - pr
        if pp < -2.0:
            bottlenecks.append((name, pp, cr, pr))

    # Worst structural stage
    stage_d = {
        "Lead Generation":   cur_c2.get("Leads",0) - prv_c2.get("Leads",0),
        "Uniqueness Filter": cur_c2.get("Unique Leads",0) - prv_c2.get("Unique Leads",0),
        "Onboarding":        cur_c2.get("Onboarded",0) - prv_c2.get("Onboarded",0),
        "Placements (FT)":   dlt_tot,
    }
    worst = min(stage_d, key=lambda k: stage_d[k])
    trend = "declined" if dlt_tot < 0 else "improved"

    # ── Executive Overview ──
    section("Executive Overview")
    st.markdown(f"""
    <div class="rca-card">
      <div class="rca-ttl">Overall Summary</div>
      <div class="rca-body">
        Total placements (FT) <strong>{trend}</strong> by
        <strong style="color:{'var(--red)' if dlt_tot < 0 else 'var(--green)'}">{fmt(abs(dlt_tot))}</strong>
        ({f"{pct_tot:+.1f}%" if np.isfinite(pct_tot) else "N/A"}) period-over-period ({mode}),
        from <strong>{fmt(prv_tot)}</strong> → <strong>{fmt(cur_tot)}</strong>.
        The <strong style="color:var(--amber)">{worst}</strong> layer drove the largest share of this variance.
        Immediate review of the dimensions below is recommended to arrest further decline or
        reinforce positive momentum.
      </div>
    </div>""", unsafe_allow_html=True)

    # Top & Bottom movers side-by-side
    mc1, mc2 = st.columns(2)

    with mc1:
        section("Top 3 Positive Movers")
        items = ""
        if top3.empty:
            items = '<div style="color:var(--muted);font-size:12px;padding:8px 0">No positive movers this period.</div>'
        else:
            for _, r in top3.iterrows():
                p_str = f"{r['pct']:+.1f}%" if pd.notna(r["pct"]) and np.isfinite(r["pct"]) else ""
                items += f"""<div class="rca-item">
                  <div class="rca-dot dot-g"></div>
                  <div><strong>[{r['dim']}]</strong> {r['name']} —
                  gained <strong style="color:var(--green)">{fmt(r['delta'])}</strong>
                  placements <span style="color:var(--muted)">{p_str}</span></div>
                </div>"""
        st.markdown(f'<div class="rca-card"><div class="rca-ttl">Gainers</div>{items}</div>',
                    unsafe_allow_html=True)

    with mc2:
        section("Top 3 Bottom Movers")
        items = ""
        if bot3.empty:
            items = '<div style="color:var(--muted);font-size:12px;padding:8px 0">No negative movers this period.</div>'
        else:
            for _, r in bot3.iterrows():
                p_str = f"{r['pct']:+.1f}%" if pd.notna(r["pct"]) and np.isfinite(r["pct"]) else ""
                items += f"""<div class="rca-item">
                  <div class="rca-dot dot-r"></div>
                  <div><strong>[{r['dim']}]</strong> {r['name']} —
                  dropped <strong style="color:var(--red)">{fmt(abs(r['delta']))}</strong>
                  placements <span style="color:var(--muted)">{p_str}</span></div>
                </div>"""
        st.markdown(f'<div class="rca-card"><div class="rca-ttl">Laggards</div>{items}</div>',
                    unsafe_allow_html=True)

    # Mover bar chart
    section("Movers Visual — Delta by Dimension")
    if not mv_df.empty:
        mv_sorted = mv_df.sort_values("delta")
        delta_bar_chart(mv_sorted, "name", "delta", height=300)

    # Conversion bottlenecks
    section("Conversion Bottlenecks (>2pp Drop)")
    if not bottlenecks:
        st.markdown("""<div class="rca-card">
          <div class="rca-body" style="color:var(--muted)">
            ✅ No conversion stage dropped more than 2pp this period. Funnel is structurally healthy.
          </div></div>""", unsafe_allow_html=True)
    else:
        items = ""
        for sname, pp_val, cr, pr in bottlenecks:
            items += f"""<div class="rca-item">
              <div class="rca-dot dot-r"></div>
              <div><strong>{sname}</strong> dropped
              <strong style="color:var(--red)">{pp_val:.1f}pp</strong>
              (from <strong>{pr:.1f}%</strong> → <strong>{cr:.1f}%</strong>).
              Investigate drop-off in this funnel stage immediately.</div>
            </div>"""
        st.markdown(f'<div class="rca-card"><div class="rca-ttl">Bottlenecks</div>{items}</div>',
                    unsafe_allow_html=True)

    # Full funnel snapshot
    section("Full Funnel Snapshot")
    snap_tbl = '<div class="tw"><table class="dash-table"><thead><tr>'
    snap_tbl += '<th>Stage</th><th class="n">Current</th><th class="n">Previous</th>'
    snap_tbl += '<th class="n">Δ</th><th class="n">Δ %</th></tr></thead><tbody>'
    for _, lbl in stages:
        cv = cur_c2.get(lbl, 0)
        pv = prv_c2.get(lbl, 0)
        d  = cv - pv
        p  = (d / pv * 100) if pv > 0 else np.nan
        snap_tbl += f"""<tr>
          <td class="td-bold">{lbl}</td>
          <td class="n">{fmt(cv)}</td>
          <td class="n td-muted">{fmt(pv)}</td>
          <td class="n">{pill(d)}</td>
          <td class="n">{pill(p, is_pct=True)}</td>
        </tr>"""
    snap_tbl += "</tbody></table></div>"
    st.markdown(snap_tbl, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:2rem;font-size:11px;color:var(--muted);text-align:right">
      Data cached 1 hr · Period: {cs.strftime('%d %b')} – {ce.strftime('%d %b %Y')} · {len(df):,} records
    </div>""", unsafe_allow_html=True)
