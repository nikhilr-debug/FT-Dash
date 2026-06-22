import streamlit as st
import pandas as pd
import requests
import datetime
import numpy as np
import plotly.graph_objects as go

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Vahan Performance Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design tokens & Premium Theme System ──────────────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --bg:        #0f1117;
  --surface:   #1a1d27;
  --surface2:  #21263a;
  --surface3:  #2a2f45;
  --br:        rgba(255,255,255,0.07);
  --br2:       rgba(255,255,255,0.13);
  --text:      #eaeaea;
  --muted:     #8b8fa8;
  --faint:     #4a4f6a;
  --r:         8px;
  --rl:        12px;

  --red:       #ff6b6b;
  --red-bg:    #2d1515;
  --red-b:     #e05252;
  --amber:     #ffc97a;
  --amber-bg:  #2d1e07;
  --amber-b:   #d4891a;
  --green:     #6dd67b;
  --green-bg:  #102216;
  --green-b:   #4a9e2f;
  --blue:      #7cb9f8;
  --blue-bg:   #0d1e38;
  --blue-b:    #2f7dd4;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-size: 13px;
  line-height: 1.5;
}

/* FIXED: Hide Streamlit clutter but explicitly keep sidebar toggle arrow visible */
#MainMenu, footer { display: none !important; }
[data-testid="stToolbar"] { display: none !important; }
header { background: transparent !important; }
[data-testid="collapsedControl"] { 
    visibility: visible !important; 
    z-index: 1000000 !important; 
    background-color: var(--surface) !important;
    border-radius: 0 0 8px 0 !important;
}

.block-container {
  padding: 1.5rem 2rem 4rem !important;
  max-width: 1440px !important;
}
div[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* Dashboard Structural Elements */
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

.sec-ttl {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: var(--muted);
  margin: 1.5rem 0 .75rem;
  display: flex;
  align-items: center;
  gap: 8px;
}
.sec-ttl-line { flex: 1; height: 0.5px; background: var(--br); }

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
  background: linear-gradient(90deg, var(--blue-b), #b08cff);
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
  line-height: 1;
}
.kpi-sub { font-size: 11px; margin-top: 6px; color: var(--muted); }

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
.pz { background: var(--surface2);  color: var(--muted); }

.tw {
  background: var(--surface);
  border: 0.5px solid var(--br);
  border-radius: 0px 0px var(--rl) var(--rl);
  overflow: hidden;
  margin-bottom: 15px;
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
.n { text-align: right; font-variant-numeric: tabular-nums; }
.td-bold { font-weight: 600; }
.td-muted { color: var(--muted); font-size: 11px; }

.rca-card {
  background: var(--surface);
  border: 0.5px solid var(--br);
  border-radius: var(--rl);
  padding: 16px 20px;
  margin-bottom: 12px;
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

/* Custom Header Sorting Interactivity Button Markups */
.stButton > button {
  background-color: var(--surface2) !important;
  color: var(--muted) !important;
  border: 0.5px solid var(--br) !important;
  border-radius: var(--r) var(--r) 0px 0px !important;
  font-size: 10px !important;
  font-weight: 700 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  padding: 6px !important;
  margin: 0 !important;
}
.stButton > button:hover {
  color: var(--text) !important;
  border-color: var(--blue) !important;
}

/* Tab Overrides */
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
div[data-baseweb="select"] > div {
  background: var(--surface2) !important;
  border: 0.5px solid var(--br2) !important;
  border-radius: var(--r) !important;
  color: var(--text) !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#8b8fa8", size=11),
    margin=dict(l=0, r=0, t=15, b=0), showlegend=False,
    xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#8b8fa8"), linecolor="rgba(255,255,255,0.07)"),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", zeroline=False),
    bargap=0.4
)

BAR_CUR  = "#2f7dd4"
BAR_PRV  = "#4a4f6a"

# ── Data Fetch Pipelines ──────────────────────────────────────────────────────
API_URL = "https://redash.vahan.link/api/queries/17613/results.json?api_key=4aFm2iOoyx8I91svQccdeZr0jmaiUsMFSRinZcmu"

@st.cache_data(ttl=3600)
def fetch_data():
    try:
        r = requests.get(API_URL, timeout=30)
        r.raise_for_status()
        return pd.DataFrame(r.json()["query_result"]["data"]["rows"])
    except Exception as e:
        st.error(f"⚠️ API pipeline disconnection: {e}")
        return pd.DataFrame()

raw = fetch_data()
if raw.empty: st.stop()

df_base = raw.copy()
if "cl" in df_base.columns:
    df_base.rename(columns={"cl": "CL"}, inplace=True)

ft = "first_date_of_work"
df_base[ft] = pd.to_datetime(df_base[ft], errors="coerce").dt.date

# ── Global Scope Temporal Anchoring ───────────────────────────────────────────
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

# ── Sidebar Controls ──────────────────────────────────────────────────────────
st.sidebar.markdown("### 🛠️ Data Controls")
if st.sidebar.button("🔄 Force Refresh Data", type="primary", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("### 🎛️ Parameters")
mode = st.sidebar.selectbox("Comparison Window Mode", ["WTD", "MTD"])
exclude_current = st.sidebar.checkbox("Exclude Current Incomplete Week", value=False)

def get_windows(mode, exclude_current):
    if mode == "WTD":
        dow = today.weekday()
        if exclude_current:
            cs = today - datetime.timedelta(days=dow + 7)
            ce = cs + datetime.timedelta(days=6)
            ps = cs - datetime.timedelta(days=7)
            pe = ps + datetime.timedelta(days=6)
        else:
            cs = today - datetime.timedelta(days=dow)
            ce = yesterday
            ps = cs - datetime.timedelta(weeks=1)
            pe = ce - datetime.timedelta(weeks=1)
    else:
        cs = today.replace(day=1)
        ce = yesterday
        pm = today.month - 1 or 12
        py = today.year if today.month > 1 else today.year - 1
        prev_start = today.replace(year=py, month=pm, day=1)
        offset = (ce - cs).days
        ps = prev_start
        pe = prev_start + datetime.timedelta(days=offset)
    return cs, ce, ps, pe

cs, ce, ps, pe = get_windows(mode, exclude_current)

# ── Run-Rate Projection Multiplier Engine ─────────────────────────────────────
days_elapsed = (ce - cs).days + 1
if mode == "WTD":
    total_days = 7
else:
    next_month = cs.replace(day=28) + datetime.timedelta(days=4)
    total_days = (next_month - datetime.timedelta(days=next_month.day)).day

proj_multiplier = total_days / days_elapsed if days_elapsed > 0 else 1.0

# ── Global Sidebar Segment Filters ────────────────────────────────────────────
st.sidebar.markdown("### 🔍 Segment Filters")
client_opts = sorted(list(df_base["company_name"].dropna().unique()))
selected_clients = st.sidebar.multiselect("Client Scope", client_opts, key="global_filter_client")

city_opts = sorted(list(df_base["jobCity"].dropna().unique()))
selected_cities = st.sidebar.multiselect("City Scope", city_opts, key="global_filter_city")

vl_opts = sorted(list(df_base["vl_name"].dropna().unique()))
selected_vls = st.sidebar.multiselect("Vendor Line Scope", vl_opts, key="global_filter_vl")

cl_opts = sorted(list(df_base["CL"].dropna().unique())) if "CL" in df_base.columns else []
selected_cls = st.sidebar.multiselect("Cluster Lead (CL) Scope", cl_opts, key="global_filter_cl")

df = df_base.copy()
if selected_clients: df = df[df["company_name"].isin(selected_clients)]
if selected_cities:  df = df[df["jobCity"].isin(selected_cities)]
if selected_vls:     df = df[df["vl_name"].isin(selected_vls)]
if selected_cls and "CL" in df.columns: df = df[df["CL"].isin(selected_cls)]

# ── Header Markup Execution ───────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
  <div>
    <div class="dash-title">Vahan <span>Performance Analytics</span> Dashboard</div>
    <div class="dash-meta"><span class="live-dot"></span>Live Lookback Tracking · Active Bounds as of Yesterday</div>
  </div>
  <div><span class="pill pb" style="font-size:11px;">Current: {cs.strftime('%b %d')} - {ce.strftime('%b %d')} vs Previous: {ps.strftime('%b %d')} - {pe.strftime('%b %d')}</span></div>
</div>""", unsafe_allow_html=True)

# ── Calculation Helpers ───────────────────────────────────────────────────────
def fmt(n):
    if pd.isna(n): return "—"
    return f"{int(n):,}" if abs(n) < 1e6 else f"{n/1e6:.1f}M"

def pill_markup(val):
    if pd.isna(val) or not np.isfinite(val): return '<span class="pill pz">—</span>'
    cls = "pg" if val >= 0 else "pr"
    return f'<span class="pill {cls}">{"+" if val > 0 else ""}{val:.1f}%</span>'

def volume_pill(val):
    if pd.isna(val): return '<span class="pill pz">—</span>'
    cls = "pg" if val >= 0 else "pr"
    return f'<span class="pill {cls}">{"+" if val > 0 else ""}{int(val):,}</span>'

def kpi_html(label, value, sub="", pill_html=""):
    return f"""
    <div class="kpi">
      <div class="kpi-lbl">{label}</div>
      <div class="kpi-val">{value}</div>
      <div class="kpi-sub">{sub} {pill_html}</div>
    </div>"""

def compute_comparison_matrix(dataframe, group_key):
    c = dataframe[(dataframe[ft] >= cs) & (dataframe[ft] <= ce)].groupby(group_key).size().rename("cur")
    p = dataframe[(dataframe[ft] >= ps) & (dataframe[ft] <= pe)].groupby(group_key).size().rename("prv")
    res = pd.concat([c, p], axis=1)
    
    if "cur" not in res.columns: res["cur"] = 0
    if "prv" not in res.columns: res["prv"] = 0
        
    res = res.fillna(0).astype(int)
    res["delta"] = res["cur"] - res["prv"]
    res["pct"] = np.where(res["prv"] > 0, (res["delta"] / res["prv"]) * 100, np.nan)
    res["proj"] = (res["cur"] * proj_multiplier).round().astype(int)
    return res

def draw_sortable_header(table_id, col_specs):
    state_key = f"sort_state_{table_id}"
    if state_key not in st.session_state:
        st.session_state[state_key] = (col_specs[0][1], False)

    current_col, current_desc = st.session_state[state_key]
    grid_cols = st.columns([spec[2] for spec in col_specs])
    
    for idx, (label, field, weight) in enumerate(col_specs):
        icon = " ▴" if current_col == field and not current_desc else (" ▾" if current_col == field else "")
        if grid_cols[idx].button(f"{label}{icon}", key=f"btn_{table_id}_{str(field)}", use_container_width=True):
            if current_col == field:
                st.session_state[state_key] = (field, not current_desc)
            else:
                st.session_state[state_key] = (field, True)
            st.rerun()
    return st.session_state[state_key]

def section(title):
    st.markdown(f'<div class="sec-ttl">{title}<div class="sec-ttl-line"></div></div>', unsafe_allow_html=True)

# ── Primary Metric Matrices Engine Calculations ──────────────────────────────
cur_tot = len(df[(df[ft] >= cs) & (df[ft] <= ce)])
prv_tot = len(df[(df[ft] >= ps) & (df[ft] <= pe)])
dlt_tot = cur_tot - prv_tot
pct_tot = (dlt_tot / prv_tot * 100) if prv_tot > 0 else np.nan
proj_tot = int(round(cur_tot * proj_multiplier))

client_mat = compute_comparison_matrix(df, "company_name").reset_index()
client_mat.columns = ["Client", "cur", "prv", "delta", "pct", "proj"]

vl_master = compute_comparison_matrix(df, "vl_name").reset_index()
vl_master.columns = ["VL", "cur", "prv", "delta", "pct", "proj"]

# ── Tab Navigation Panels ─────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📦 Client Operations", "🗺️ CL & Region Maps", "🤖 AI Narrative & RCA"])

# ==============================================================================
# TAB 1: CLIENT OPERATIONS
# ==============================================================================
with tab1:
    k1, k2, k3, k4, k5 = st.columns(5)
    k_color = "var(--green)" if dlt_tot > 0 else ("var(--red)" if dlt_tot < 0 else "var(--text)")
    with k1: st.markdown(kpi_html("Current Period FT", f'<span style="color:{k_color}">{fmt(cur_tot)}</span>'), unsafe_allow_html=True)
    with k2: st.markdown(kpi_html("Previous Period FT", fmt(prv_tot)), unsafe_allow_html=True)
    with k3: st.markdown(kpi_html("Projected Full FT", fmt(proj_tot), sub=f"Run-rate rate: {proj_multiplier:.2f}x"), unsafe_allow_html=True)
    with k4: st.markdown(kpi_html("Δ Volume Shift", f'<span style="color:{k_color}">{fmt(dlt_tot)}</span>', pill_html=volume_pill(dlt_tot)), unsafe_allow_html=True)
    with k5: st.markdown(kpi_html("Δ % Shift", f"{pct_tot:+.1f}%" if pd.notna(pct_tot) else "—", pill_html=pill_markup(pct_tot)), unsafe_allow_html=True)

    if mode == "WTD":
        df_trend = df.copy()
        df_trend['datetime'] = pd.to_datetime(df_trend[ft])
        df_trend['Week_Start'] = df_trend['datetime'].dt.to_period('W').dt.start_time.dt.date
        
        dow = today.weekday()
        this_week_monday = today - datetime.timedelta(days=dow)
        if exclude_current:
            df_trend = df_trend[df_trend['Week_Start'] < this_week_monday]
            
        if not df_trend.empty:
            max_trend_w = df_trend['Week_Start'].max()
            active_weeks = [max_trend_w - datetime.timedelta(weeks=i) for i in range(7, -1, -1)]
            df_trend = df_trend[df_trend['Week_Start'].isin(active_weeks)]
            
            trend_data = df_trend.groupby('Week_Start').size().reset_index(name='Placements')
            trend_data = trend_data.sort_values('Week_Start')
            trend_data['Label'] = trend_data['Week_Start'].apply(lambda x: f"W/C {x.strftime('%d %b')}")
            
            section("Trailing 8-Week Placement Trend Lookback")
            fig_trend = go.Figure(go.Scatter(
                x=trend_data['Label'], y=trend_data['Placements'], mode='lines+markers+text',
                line=dict(color=BAR_CUR, width=3), text=trend_data['Placements'], textposition="top center",
                marker=dict(size=8, color=BAR_CUR)
            ))
            fig_trend.update_layout(**PLOT_LAYOUT, height=220)
            st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False}, key="8_week_trend_line_chart")
            
            section("Client × Week Matrix View (FT Volume & WoW Changes)")
            matrix_src = df_trend.groupby(['company_name', 'Week_Start']).size().unstack(fill_value=0)
            col_specs_week = [("Client Profile", "Client", 3)] + [(f"W/C {w.strftime('%d %b')}", w, 1) for w in active_weeks]
            w_col, w_desc = draw_sortable_header("client_week_matrix", col_specs_week)
            
            if w_col == "Client": matrix_src = matrix_src.sort_index(ascending=not w_desc)
            else: matrix_src = matrix_src.sort_values(by=w_col, ascending=not w_desc)
                
            m_tbl = '<div class="tw" style="overflow-x:auto;"><table class="dash-table"><tbody>'
            for client_name, row in matrix_src.iterrows():
                m_tbl += f'<tr><td style="width: 27.2%; font-weight:600;">{client_name}</td>'
                for idx, week_monday in enumerate(active_weeks):
                    val = row.get(week_monday, 0)
                    if idx == 0:
                        wow_str = '<span style="font-size:10px; color:var(--muted);">Base</span>'
                        val_color = "var(--text)"
                    else:
                        prev_week_monday = active_weeks[idx - 1]
                        prev_val = row.get(prev_week_monday, 0)
                        if prev_val > 0:
                            wow_pct = ((val - prev_val) / prev_val) * 100
                            val_color = "var(--green)" if wow_pct > 0 else ("var(--red)" if wow_pct < 0 else "var(--text)")
                            wow_str = f'<span style="font-size:10px; color:{val_color}; font-weight:700;">{wow_pct:+.1f}%</span>'
                        else:
                            val_color = "var(--green)" if val > 0 else "var(--text)"
                            wow_str = f'<span style="font-size:10px; color:{val_color}; font-weight:700;">+100%</span>' if val > 0 else '<span style="font-size:10px; color:var(--muted);">0%</span>'
                    m_tbl += f'<td class="n" style="width: 9.1%;"><div style="font-weight:600; color:{val_color};">{val:,}</div><div>{wow_str}</div></td>'
                m_tbl += '</tr>'
            m_tbl += '</tbody></table></div>'
            st.markdown(m_tbl, unsafe_allow_html=True)

    elif mode == "MTD":
        section("Month-To-Date (MTD) Day-by-Day Run-Rate Tracking")
        sub_cur = df[(df[ft] >= cs) & (df[ft] <= ce)]
        sub_prv = df[(df[ft] >= ps) & (df[ft] <= pe)]
        
        cur_days = sub_cur.groupby(sub_cur[ft].apply(lambda x: x.day)).size().rename("Current Month")
        prv_days = sub_prv.groupby(sub_prv[ft].apply(lambda x: x.day)).size().rename("Previous Month")
        
        mtd_trend = pd.concat([cur_days, prv_days], axis=1).fillna(0).reset_index()
        mtd_trend.columns = ["Day of Month", "Current Month", "Previous Month"]
        
        fig_mtd = go.Figure()
        fig_mtd.add_trace(go.Scatter(x=mtd_trend["Day of Month"], y=mtd_trend["Previous Month"], name="Previous Month Baseline", mode='lines', line=dict(color=BAR_PRV, width=2, dash='dot')))
        fig_mtd.add_trace(go.Scatter(x=mtd_trend["Day of Month"], y=mtd_trend["Current Month"], name="Current Month Runrate", mode='lines+markers', line=dict(color=BAR_CUR, width=3)))
        
        mtd_layout = dict(**PLOT_LAYOUT)
        mtd_layout["height"] = 240
        mtd_layout["showlegend"] = True
        fig_mtd.update_layout(**mtd_layout)
        st.plotly_chart(fig_mtd, use_container_width=True, config={"displayModeBar": False}, key="mtd_day_runrate_chart")

    section("All Clients Performance Analysis")
    c_col, c_desc = draw_sortable_header("client_main", [("Client Name", "Client", 3), ("Current FT", "cur", 2), ("Projected FT", "proj", 2), ("Previous FT", "prv", 2), ("Δ Vol", "delta", 1.5), ("Δ %", "pct", 1.5)])
    client_mat = client_mat.sort_values(c_col, ascending=not c_desc)

    t_html = '<div class="tw"><table class="dash-table"><tbody>'
    for _, r in client_mat.iterrows():
        c_color = "var(--green)" if r['delta'] > 0 else ("var(--red)" if r['delta'] < 0 else "var(--text)")
        t_html += f"""<tr>
            <td style="width:25%; font-weight:600;">{r['Client']}</td>
            <td class="n" style="width:16.6%; font-weight:600; color:{c_color};">{fmt(r['cur'])}</td>
            <td class="n" style="width:16.6%; font-weight:700; color:var(--blue);">{fmt(r['proj'])}</td>
            <td class="n" style="width:16.6%; color:var(--muted);">{fmt(r['prv'])}</td>
            <td class="n" style="width:12.5%;">{volume_pill(r['delta'])}</td>
            <td class="n" style="width:12.5%;">{pill_markup(r['pct'])}</td>
        </tr>"""
    t_html += "</tbody></table></div>"
    st.markdown(t_html, unsafe_allow_html=True)

    section("Growing Clients Matrix — Ranked by % Surge")
    growing_clients = client_mat[client_mat["delta"] > 0]
    if not growing_clients.empty:
        gc_col, gc_desc = draw_sortable_header("growing_clients", [("Client Name", "Client", 3), ("Current FT", "cur", 2), ("Projected FT", "proj", 2), ("Previous FT", "prv", 2), ("Δ Vol", "delta", 1.5), ("Δ %", "pct", 1.5)])
        growing_clients = growing_clients.sort_values(gc_col, ascending=not gc_desc)
        
        t_html = '<div class="tw"><table class="dash-table"><tbody>'
        for _, r in growing_clients.iterrows():
            c_color = "var(--green)" if r['delta'] > 0 else ("var(--red)" if r['delta'] < 0 else "var(--text)")
            t_html += f"""<tr>
                <td style="width:25%; font-weight:600; color:var(--green);">{r['Client']}</td>
                <td class="n" style="width:16.6%; font-weight:600; color:{c_color};">{fmt(r['cur'])}</td>
                <td class="n" style="width:16.6%; font-weight:700; color:var(--blue);">{fmt(r['proj'])}</td>
                <td class="n" style="width:16.6%; color:var(--muted);">{fmt(r['prv'])}</td>
                <td class="n" style="width:12.5%;">{volume_pill(r['delta'])}</td>
                <td class="n" style="width:12.5%;">{pill_markup(r['pct'])}</td>
            </tr>"""
        t_html += "</tbody></table></div>"
        st.markdown(t_html, unsafe_allow_html=True)
    else:
        st.info("No segments meet expansion target profile bounds currently.")

    section("Dynamic Vendor Line (VL) Analytics Tracker")
    vl_left, vl_right = st.columns(2)
    
    with vl_left:
        section("Top 10 Degrowing Vendor Lines (VL)")
        degrow_vl = vl_master[vl_master["delta"] < 0].nsmallest(10, "delta")
        if not degrow_vl.empty:
            dv_col, dv_desc = draw_sortable_header("degrow_vl_table", [("Vendor Partner Line (VL)", "VL", 4), ("Current FT", "cur", 2), ("Projected FT", "proj", 2), ("Δ Deficit", "delta", 2)])
            degrow_vl = degrow_vl.sort_values(dv_col, ascending=not dv_desc)
            
            t_html = '<div class="tw"><table class="dash-table"><tbody>'
            for _, r in degrow_vl.iterrows():
                c_color = "var(--green)" if r['delta'] > 0 else ("var(--red)" if r['delta'] < 0 else "var(--text)")
                t_html += f"""<tr>
                    <td style="width:40%; font-weight:600;">{r['VL']}</td>
                    <td class="n" style="width:20%; font-weight:600; color:{c_color};">{fmt(r['cur'])}</td>
                    <td class="n" style="width:20%; font-weight:700; color:var(--blue);">{fmt(r['proj'])}</td>
                    <td class="n" style="width:20%;">{volume_pill(r['delta'])}</td>
                </tr>"""
            t_html += "</tbody></table></div>"
            st.markdown(t_html, unsafe_allow_html=True)
        else:
            st.info("No vendor lines currently displaying contraction trends.")

    with vl_right:
        section("Top 10 Growing Vendor Lines (VL)")
        grow_vl = vl_master[vl_master["delta"] > 0].nlargest(10, "delta")
        if not grow_vl.empty:
            gv_col, gv_desc = draw_sortable_header("grow_vl_table", [("Vendor Partner Line (VL)", "VL", 4), ("Current FT", "cur", 2), ("Projected FT", "proj", 2), ("Δ Surge", "delta", 2)])
            grow_vl = grow_vl.sort_values(gv_col, ascending=not gv_desc)
            
            t_html = '<div class="tw"><table class="dash-table"><tbody>'
            for _, r in grow_vl.iterrows():
                c_color = "var(--green)" if r['delta'] > 0 else ("var(--red)" if r['delta'] < 0 else "var(--text)")
                t_html += f"""<tr>
                    <td style="width:40%; font-weight:600; color:var(--green);">{r['VL']}</td>
                    <td class="n" style="width:20%; font-weight:600; color:{c_color};">{fmt(r['cur'])}</td>
                    <td class="n" style="width:20%; font-weight:700; color:var(--blue);">{fmt(r['proj'])}</td>
                    <td class="n" style="width:20%;">{volume_pill(r['delta'])}</td>
                </tr>"""
            t_html += "</tbody></table></div>"
            st.markdown(t_html, unsafe_allow_html=True)
        else:
            st.info("No vendor lines currently displaying expansion trends.")

# ==============================================================================
# TAB 2: CL & REGION MAPS
# ==============================================================================
with tab2:
    reg_mat = compute_comparison_matrix(df, "region").reset_index()
    reg_mat.columns = ["Region", "cur", "prv", "delta", "pct", "proj"]

    r_left, r_right = st.columns(2)
    with r_left:
        section("Regional Zone Allocations Table")
        rl_col, rl_desc = draw_sortable_header("reg_main", [("Region Layer", "Region", 3), ("Current", "cur", 2), ("Projected", "proj", 2), ("Δ Vol", "delta", 1.5), ("Δ %", "pct", 1.5)])
        reg_mat = reg_mat.sort_values(rl_col, ascending=not rl_desc)
        
        t_html = '<div class="tw"><table class="dash-table"><tbody>'
        for _, r in reg_mat.iterrows():
            c_color = "var(--green)" if r['delta'] > 0 else ("var(--red)" if r['delta'] < 0 else "var(--text)")
            t_html += f"""<tr>
                <td style="width:30%; font-weight:600;">{r['Region']}</td>
                <td class="n" style="width:20%; font-weight:600; color:{c_color};">{fmt(r['cur'])}</td>
                <td class="n" style="width:20%; font-weight:700; color:var(--blue);">{fmt(r['proj'])}</td>
                <td class="n" style="width:15%;">{volume_pill(r['delta'])}</td>
                <td class="n" style="width:15%;">{pill_markup(r['pct'])}</td>
            </tr>"""
        t_html += "</tbody></table></div>"
        st.markdown(t_html, unsafe_allow_html=True)

    with r_right:
        section("Cluster Lead (CL) Allocations Table")
        if "CL" in df.columns:
            cl_mat = compute_comparison_matrix(df, "CL").reset_index()
            cl_mat.columns = ["CL", "cur", "prv", "delta", "pct", "proj"]
            cl_col, cl_desc = draw_sortable_header("cl_main_table", [("Cluster Lead", "CL", 3), ("Current", "cur", 2), ("Projected", "proj", 2), ("Δ Vol", "delta", 1.5), ("Δ %", "pct", 1.5)])
            cl_mat = cl_mat.sort_values(cl_col, ascending=not cl_desc)
            
            t_html = '<div class="tw"><table class="dash-table"><tbody>'
            for _, r in cl_mat.iterrows():
                c_color = "var(--green)" if r['delta'] > 0 else ("var(--red)" if r['delta'] < 0 else "var(--text)")
                t_html += f"""<tr>
                    <td style="width:30%; font-weight:600;">{r['CL']}</td>
                    <td class="n" style="width:20%; font-weight:600; color:{c_color};">{fmt(r['cur'])}</td>
                    <td class="n" style="width:20%; font-weight:700; color:var(--blue);">{fmt(r['proj'])}</td>
                    <td class="n" style="width:15%;">{volume_pill(r['delta'])}</td>
                    <td class="n" style="width:15%;">{pill_markup(r['pct'])}</td>
                </tr>"""
            t_html += "</tbody></table></div>"
            st.markdown(t_html, unsafe_allow_html=True)
        else:
            st.info("`CL` metadata parameter missing from core query.")

    if "CL" in df.columns and "am_name" in df.columns:
        section("Interactive Drill-Down: Account Managers under Selected Cluster Lead")
        cl_list = sorted(list(df["CL"].dropna().unique()))
        if cl_list:
            sel_drill_cl = st.selectbox("Select Cluster Lead for AM Drilldown", cl_list, key="cl_drill_selectbox")
            if sel_drill_cl:
                df_cl_drill = df[df["CL"] == sel_drill_cl]
                am_drill_mat = compute_comparison_matrix(df_cl_drill, "am_name").reset_index()
                am_drill_mat.columns = ["AM Name", "cur", "prv", "delta", "pct", "proj"]
                
                amd_col, amd_desc = draw_sortable_header("am_drill_table", [("Account Manager Name", "AM Name", 3), ("Current FT", "cur", 2), ("Projected FT", "proj", 2), ("Δ Vol", "delta", 1.5), ("Δ %", "pct", 1.5)])
                am_drill_mat = am_drill_mat.sort_values(amd_col, ascending=not amd_desc)
                
                t_html = '<div class="tw"><table class="dash-table"><tbody>'
                for _, r in am_drill_mat.iterrows():
                    c_color = "var(--green)" if r['delta'] > 0 else ("var(--red)" if r['delta'] < 0 else "var(--text)")
                    t_html += f"""<tr>
                        <td style="width:30%; font-weight:600; color:var(--blue);">{r['AM Name']}</td>
                        <td class="n" style="width:20%; font-weight:600; color:{c_color};">{fmt(r['cur'])}</td>
                        <td class="n" style="width:20%; font-weight:700; color:var(--blue);">{fmt(r['proj'])}</td>
                        <td class="n" style="width:15%;">{volume_pill(r['delta'])}</td>
                        <td class="n" style="width:15%;">{pill_markup(r['pct'])}</td>
                    </tr>"""
                t_html += "</tbody></table></div>"
                st.markdown(t_html, unsafe_allow_html=True)

    section("Region Breakdown for Gap Clients (Shortfall Contributors Only)")
    gap_clients = client_mat[client_mat["delta"] < 0]["Client"].unique()
    if len(gap_clients) > 0:
        df_gap = df[df["company_name"].isin(gap_clients)]
        gap_reg = compute_comparison_matrix(df_gap, ["company_name", "region"]).reset_index()
        gap_reg.columns = ["Client", "Region", "cur", "prv", "delta", "pct", "proj"]
        
        gr_col, gr_desc = draw_sortable_header("gap_reg_table", [("Client Name", "Client", 3), ("Regional Cluster", "Region", 3), ("Current FT", "cur", 2), ("Δ Volume Drop", "delta", 2), ("Δ %", "pct", 2)])
        gap_reg = gap_reg.sort_values(gr_col, ascending=not gr_desc)
        
        t_html = '<div class="tw"><table class="dash-table"><tbody>'
        for _, r in gap_reg.iterrows():
            c_color = "var(--green)" if r['delta'] > 0 else ("var(--red)" if r['delta'] < 0 else "var(--text)")
            t_html += f"""<tr>
                <td style="width:30%; font-weight:600;">{r['Client']}</td>
                <td style="width:30%; color:var(--muted);">{r['Region']}</td>
                <td class="n" style="width:13.3%; font-weight:600; color:{c_color};">{fmt(r['cur'])}</td>
                <td class="n" style="width:13.3%; color:var(--red-b); font-weight:600;">{fmt(r['delta'])}</td>
                <td class="n" style="width:13.3%;">{pill_markup(r['pct'])}</td>
            </tr>"""
        t_html += "</tbody></table></div>"
        st.markdown(t_html, unsafe_allow_html=True)

    section("Growing Regions Profile — Ranked by % Surge")
    growing_regions = reg_mat[reg_mat["delta"] > 0]
    if not growing_regions.empty:
        grg_col, grg_desc = draw_sortable_header("growing_regions_tbl", [("Region Zone", "Region", 3), ("Current", "cur", 2), ("Projected", "proj", 2), ("Δ Vol", "delta", 1.5), ("Δ %", "pct", 1.5)])
        growing_regions = growing_regions.sort_values(grg_col, ascending=not grg_desc)
        
        t_html = '<div class="tw"><table class="dash-table"><tbody>'
        for _, r in growing_regions.iterrows():
            c_color = "var(--green)" if r['delta'] > 0 else ("var(--red)" if r['delta'] < 0 else "var(--text)")
            t_html += f"""<tr>
                <td style="width:30%; font-weight:600; color:var(--green);">{r['Region']}</td>
                <td class="n" style="width:20%; font-weight:600; color:{c_color};">{fmt(r['cur'])}</td>
                <td class="n" style="width:20%; font-weight:700; color:var(--blue);">{fmt(r['proj'])}</td>
                <td class="n" style="width:15%;">{volume_pill(r['delta'])}</td>
                <td class="n" style="width:15%;">{pill_markup(r['pct'])}</td>
            </tr>"""
        t_html += "</tbody></table></div>"
        st.markdown(t_html, unsafe_allow_html=True)

# ==============================================================================
# TAB 3: AI NARRATIVE & RCA
# ==============================================================================
with tab3:
    section("Programmatic Executive Summary & Attribution (Placements Only)")
    
    pool = []
    for _, r in client_mat.iterrows(): pool.append({"type": "Client Profile", "name": r["Client"], "delta": r["delta"]})
    for _, r in reg_mat.iterrows():    pool.append({"type": "Regional Cluster", "name": r["Region"], "delta": r["delta"]})
    for _, r in vl_master.iterrows():   pool.append({"type": "Vendor Line Partner (VL)", "name": r["VL"], "delta": r["delta"]})
    if "CL" in df.columns and 'cl_mat' in locals():
        for _, r in cl_mat.iterrows():   pool.append({"type": "Cluster Lead (CL)", "name": r["CL"], "delta": r["delta"]})
    
    m_df = pd.DataFrame(pool, columns=["type", "name", "delta"]).dropna()
    leaders = m_df[m_df["delta"] > 0].nlargest(3, "delta") if not m_df.empty else pd.DataFrame()
    laggards = m_df[m_df["delta"] < 0].nsmallest(3, "delta") if not m_df.empty else pd.DataFrame()
    
    trend_term = "an operational contraction" if dlt_tot < 0 else "an upward expansion trend"
    hl_color = "var(--red)" if dlt_tot < 0 else "var(--green)"
    
    st.markdown(f"""
    <div class="rca-card">
      <div class="rca-ttl">Performance Review Narrative</div>
      <div class="rca-body">
        Data matching current parameters logs {trend_term} yielding a global net variation of 
        <strong style="color:{hl_color}">{fmt(dlt_tot)} total placements (FT)</strong> ({pct_tot:+.1f}%) 
        compared to the relative historical cycle baseline. Absolute volume shifted from <strong>{fmt(prv_tot)}</strong> 
        units to <strong>{fmt(cur_tot)}</strong> active placements inside the evaluated window frame.
      </div>
    </div>""", unsafe_allow_html=True)

    as_left, as_right = st.columns(2)
    with as_left:
        st.markdown('<div class="rca-card"><div class="rca-ttl">Primary Positive Drivers</div>', unsafe_allow_html=True)
        if not leaders.empty:
            for _, r in leaders.iterrows():
                st.markdown(f"""<div class="rca-item"><div class="rca-dot dot-g"></div>
                    <div><strong>[{r['type']}]</strong> {r['name']} — net change of <span style="color:var(--green); font-weight:700;">+{int(r['delta']):,}</span> placements.</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:var(--muted); font-size:12px;">No active vectors recorded growth steps during this cycle.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with as_right:
        st.markdown('<div class="rca-card"><div class="rca-ttl">Primary Deficit Contributors</div>', unsafe_allow_html=True)
        if not laggards.empty:
            for _, r in laggards.iterrows():
                st.markdown(f"""<div class="rca-item"><div class="rca-dot dot-r"></div>
                    <div><strong>[{r['type']}]</strong> {r['name']} — net change of <span style="color:var(--red); font-weight:700;">{int(r['delta']):,}</span> placements.</div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:var(--muted); font-size:12px;">No active vectors logged shortfalls during this cycle.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
