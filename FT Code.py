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

# ── Design tokens & Custom Layout Injection ───────────────────────────────────
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

html, body, [class*="css"], .stApp {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
  font-size: 13px;
  line-height: 1.5;
}

#MainMenu, footer, header { visibility: hidden !important; }
.block-container {
  padding: 1.5rem 2rem 4rem !important;
  max-width: 1440px !important;
}
div[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

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

.pill {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 700;
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
.dash-table td {
  padding: 8px 12px;
  border-bottom: 0.5px solid var(--br);
  color: var(--text);
  white-space: nowrap;
}
.dash-table tr:last-child td { border-bottom: none; }
.dash-table tr:hover td { background: var(--surface2); }
.n { text-align: right; font-variant-numeric: tabular-nums; }

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
.rca-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 7px 0;
  border-bottom: 0.5px solid var(--br);
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

/* Header Sorting System Linkages Override */
.stButton > button {
  background-color: var(--surface2) !important;
  color: var(--muted) !important;
  border: 0.5px solid var(--br2) !important;
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
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#8b8fa8", size=11),
    margin=dict(l=0, r=0, t=10, b=0), showlegend=False,
    xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#8b8fa8")),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)"),
    bargap=0.4
)

# ── Data Core Engine ──────────────────────────────────────────────────────────
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

df = raw.copy()
ft = "first_date_of_work"
df[ft] = pd.to_datetime(df[ft], errors="coerce").dt.date

# ── Time window configurations ────────────────────────────────────────────────
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

st.sidebar.markdown("### 🎛️ Parameters")
mode = st.sidebar.selectbox("Comparison Window Mode", ["WTD", "MTD"])

if mode == "WTD":
    dow = today.weekday()
    cs, ce = today - datetime.timedelta(days=dow), yesterday
    ps, pe = cs - datetime.timedelta(weeks=1), ce - datetime.timedelta(weeks=1)
else:
    cs, ce = today.replace(day=1), yesterday
    pm, py = (today.month - 1 or 12), (today.year if today.month > 1 else today.year - 1)
    prev_start = today.replace(year=py, month=pm, day=1)
    ps, pe = prev_start, prev_start + datetime.timedelta(days=(ce - cs).days)

# ── Global Sidebar Filters ────────────────────────────────────────────────────
st.sidebar.markdown("### 🔍 Scope Segments")
client_opts = ["All Clients"] + sorted(list(df["company_name"].dropna().unique()))
sel_client = st.sidebar.selectbox("Client Scope", client_opts)

city_opts = ["All Cities"] + sorted(list(df["jobCity"].dropna().unique()))
sel_city = st.sidebar.selectbox("City Scope", city_opts)

vl_opts = ["All VLs"] + sorted(list(df["vl_name"].dropna().unique()))
sel_vl = st.sidebar.selectbox("Vendor Partner Scope", vl_opts)

if sel_client != "All Clients": df = df[df["company_name"] == sel_client]
if sel_city != "All Cities": df = df[df["jobCity"] == sel_city]
if sel_vl != "All VLs": df = df[df["vl_name"] == sel_vl]

# ── Header Markup Execution ───────────────────────────────────────────────────
st.markdown(f"""
<div class="dash-header">
  <div>
    <div class="dash-title">Vahan <span>Placement Analytics</span> Engine</div>
    <div class="dash-meta"><span class="live-dot"></span>Live Lookback · Cutoff up to {yesterday.strftime('%d %b %Y')}</div>
  </div>
  <div><span class="pill pb" style="font-size:11px;">{cs.strftime('%b %d')} - {ce.strftime('%b %d')} vs {ps.strftime('%b %d')} - {pe.strftime('%b %d')}</span></div>
</div>""", unsafe_allow_html=True)

# ── Calculation Helpers ────────────────────────────────────────────────────────
def fmt(n):
    if pd.isna(n): return "—"
    return f"{int(n):,}" if abs(n) < 1e6 else f"{n/1e6:.1f}M"

def pill_markup(val):
    if pd.isna(val): return '<span class="pill pz">—</span>'
    cls = "pg" if val >= 0 else "pr"
    return f'<span class="pill {cls}">{"+" if val > 0 else ""}{val:.1f}%</span>'

def volume_pill(val):
    if pd.isna(val): return '<span class="pill pz">—</span>'
    cls = "pg" if val >= 0 else "pr"
    return f'<span class="pill {cls}">{"+" if val > 0 else ""}{int(val):,}</span>'

def compute_comparison_matrix(dataframe, group_key):
    c = dataframe[(dataframe[ft] >= cs) & (dataframe[ft] <= ce)].groupby(group_key).size().rename("cur")
    p = dataframe[(dataframe[ft] >= ps) & (dataframe[ft] <= pe)].groupby(group_key).size().rename("prv")
    res = pd.concat([c, p], axis=1).fillna(0).astype(int)
    res["delta"] = res["cur"] - res["prv"]
    res["pct"] = np.where(res["prv"] > 0, (res["delta"] / res["prv"]) * 100, np.nan)
    return res

# ── Header Sorting Orchestrator Component ─────────────────────────────────────
def draw_sortable_header(table_id, col_specs):
    """Generates column buttons that update state variables on click."""
    state_key = f"sort_state_{table_id}"
    if state_key not in st.session_state:
        st.session_state[state_key] = (col_specs[0][1], False) # default sorting col, desc=False

    current_col, current_desc = st.session_state[state_key]
    grid_cols = st.columns([spec[2] for spec in col_specs])
    
    for idx, (label, field, weight) in enumerate(col_specs):
        icon = " ▴" if current_col == field and not current_desc else (" ▾" if current_col == field else "")
        if grid_cols[idx].button(f"{label}{icon}", key=f"btn_{table_id}_{field}", use_container_width=True):
            if current_col == field:
                st.session_state[state_key] = (field, not current_desc)
            else:
                st.session_state[state_key] = (field, True) # default down sorting on change
            st.rerun()
    return st.session_state[state_key]

# ── Operational Global Volumes ────────────────────────────────────────────────
cur_tot = len(df[(df[ft] >= cs) & (df[ft] <= ce)])
prv_tot = len(df[(df[ft] >= ps) & (df[ft] <= pe)])
dlt_tot = cur_tot - prv_tot
pct_tot = (dlt_tot / prv_tot * 100) if prv_tot > 0 else np.nan

# ── Tabs Configuration Layout ─────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📦 Client Operations", "🗺️ Region & Area Maps", "🤖 AI Insight Summary & RCA"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: CLIENT OPERATIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(kpi_html("Current Period FT", fmt(cur_tot)), unsafe_allow_html=True)
    with k2: st.markdown(kpi_html("Previous Period FT", fmt(prv_tot)), unsafe_allow_html=True)
    with k3: st.markdown(kpi_html("Δ Volume", fmt(dlt_tot), pill_html=volume_pill(dlt_tot)), unsafe_allow_html=True)
    with k4: st.markdown(kpi_html("Δ % Shift", f"{pct_tot:+.1f}%" if pd.notna(pct_tot) else "—", pill_html=pill_markup(pct_tot)), unsafe_allow_html=True)
    
    # 8-Week Trend Line Chart
    section("Trailing 8-Week Placement Run-Rate")
    df_trend = pd.DataFrame({ft: df[ft].dropna()})
    df_trend['datetime'] = pd.to_datetime(df_trend[ft])
    df_trend['Week_Start'] = df_trend['datetime'].dt.to_period('W').dt.start_time.dt.date
    trend_data = df_trend[(df_trend['Week_Start'] >= (yesterday - datetime.timedelta(weeks=8))) & (df_trend['Week_Start'] <= yesterday)].groupby('Week_Start').size().reset_index(name='Placements')
    
    if not trend_data.empty:
        trend_data = trend_data.sort_values('Week_Start')
        trend_data['Label'] = trend_data['Week_Start'].apply(lambda x: f"W/C {x.strftime('%d %b')}")
        fig = go.Figure(go.Scatter(x=trend_agg=trend_data['Label'], y=trend_data['Placements'], mode='lines+markers+text', line=dict(color=BAR_CUR, width=3), text=trend_data['Placements'], textposition="top center", marker=dict(size=8)))
        fig.update_layout(**PLOT_LAYOUT, height=220)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key="8_week_trend_line")

    # Client Performance Snapshot Table
    section("All Active Client Execution Matrix")
    client_mat = compute_comparison_matrix(df, "company_name").reset_index()
    client_mat.columns = ["Client", "cur", "prv", "delta", "pct"]
    
    c_sort_col, c_sort_desc = draw_sortable_header("client_table", [("Client Name", "Client", 4), ("Current FT", "cur", 2), ("Previous FT", "prv", 2), ("Δ Volume", "delta", 2), ("Δ %", "pct", 2)])
    client_mat = client_mat.sort_values(c_sort_col, ascending=not c_sort_desc)
    
    max_c = client_mat["cur"].max() or 1
    t_html = '<div class="tw"><table class="dash-table"><tbody>'
    for _, r in client_mat.iterrows():
        bw = int(min(100, r["cur"] / max_c * 100))
        t_html += f"""<tr>
            <td style="width:33.3%; font-weight:600;">{r['Client']}</td>
            <td class="n" style="width:16.6%;">{fmt(r['cur'])}</td>
            <td class="n" style="width:16.6%; color:var(--muted);">{fmt(r['prv'])}</td>
            <td class="n" style="width:16.6%;">{volume_pill(r['delta'])}</td>
            <td class="n" style="width:16.6%;">{pill_markup(r['pct'])}</td>
        </tr>"""
    t_html += "</tbody></table></div>"
    st.markdown(t_html, unsafe_allow_html=True)

    # Growing Clients Table
    section("Growing Clients Overview — Ranked by Δ%")
    growing_clients = client_mat[client_mat["delta"] > 0].sort_values("pct", ascending=False)
    gc_sort_col, gc_sort_desc = draw_sortable_header("growing_clients", [("Client Name", "Client", 4), ("Current FT", "cur", 2), ("Previous FT", "prv", 2), ("Δ Volume", "delta", 2), ("Δ %", "pct", 2)])
    growing_clients = growing_clients.sort_values(gc_sort_col, ascending=not gc_sort_desc)
    
    t_html = '<div class="tw"><table class="dash-table"><tbody>'
    for _, r in growing_clients.iterrows():
        t_html += f"""<tr>
            <td style="width:33.3%; font-weight:600; color:var(--green);">{r['Client']}</td>
            <td class="n" style="width:16.6%;">{fmt(r['cur'])}</td>
            <td class="n" style="width:16.6%; color:var(--muted);">{fmt(r['prv'])}</td>
            <td class="n" style="width:16.6%;">{volume_pill(r['delta'])}</td>
            <td class="n" style="width:16.6%;">{pill_markup(r['pct'])}</td>
        </tr>"""
    t_html += "</tbody></table></div>"
    st.markdown(t_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: REGION & AREA MAPS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    r_cols, am_cols = st.columns(2)
    
    with r_cols:
        section("Regional Placement Analysis")
        reg_mat = compute_comparison_matrix(df, "region").reset_index()
        reg_mat.columns = ["Region", "cur", "prv", "delta", "pct"]
        r_sort_col, r_sort_desc = draw_sortable_header("region_table", [("Region", "Region", 4), ("Current", "cur", 2), ("Δ Vol", "delta", 2), ("Δ %", "pct", 2)])
        reg_mat = reg_mat.sort_values(r_sort_col, ascending=not r_sort_desc)
        
        t_html = '<div class="tw"><table class="dash-table"><tbody>'
        for _, r in reg_mat.iterrows():
            t_html += f"""<tr>
                <td style="width:40%; font-weight:600;">{r['Region']}</td>
                <td class="n" style="width:20%;">{fmt(r['cur'])}</td>
                <td class="n" style="width:20%;">{volume_pill(r['delta'])}</td>
                <td class="n" style="width:20%;">{pill_markup(r['pct'])}</td>
            </tr>"""
        t_html += "</tbody></table></div>"
        st.markdown(t_html, unsafe_allow_html=True)

    with am_cols:
        section("Account Manager Allocation")
        am_mat = compute_comparison_matrix(df, "am_name").reset_index()
        am_mat.columns = ["AM", "cur", "prv", "delta", "pct"]
        am_sort_col, am_sort_desc = draw_sortable_header("am_table", [("Manager", "AM", 4), ("Current", "cur", 2), ("Δ Vol", "delta", 2), ("Δ %", "pct", 2)])
        am_mat = am_mat.sort_values(am_sort_col, ascending=not am_sort_desc)
        
        t_html = '<div class="tw"><table class="dash-table"><tbody>'
        for _, r in am_mat.iterrows():
            t_html += f"""<tr>
                <td style="width:40%; font-weight:600;">{r['AM']}</td>
                <td class="n" style="width:20%;">{fmt(r['cur'])}</td>
                <td class="n" style="width:20%;">{volume_pill(r['delta'])}</td>
                <td class="n" style="width:20%;">{pill_markup(r['pct'])}</td>
            </tr>"""
        t_html += "</tbody></table></div>"
        st.markdown(t_html, unsafe_allow_html=True)

    # Region Breakdown for Gap Clients
    section("Region Breakdown for Gap Clients (Shortfall Contributors Only)")
    gap_clients_names = client_mat[client_mat["delta"] < 0]["Client"].unique()
    if len(gap_clients_names) > 0:
        df_gap = df[df["company_name"].isin(gap_clients_names)]
        gap_reg = compute_comparison_matrix(df_gap, ["company_name", "region"]).reset_index()
        gap_reg.columns = ["Client", "Region", "cur", "prv", "delta", "pct"]
        
        gr_sort_col, gr_sort_desc = draw_sortable_header("gap_regions", [("Client Name", "Client", 3), ("Region Layer", "Region", 3), ("Current", "cur", 2), ("Δ Shortfall", "delta", 2), ("Δ %", "pct", 2)])
        gap_reg = gap_reg.sort_values(gr_sort_col, ascending=not gr_sort_desc)
        
        t_html = '<div class="tw"><table class="dash-table"><tbody>'
        for _, r in gap_reg.iterrows():
            t_html += f"""<tr>
                <td style="width:30%; font-weight:600;">{r['Client']}</td>
                <td style="width:30%; color:var(--muted);">{r['Region']}</td>
                <td class="n" style="width:13.3%;">{fmt(r['cur'])}</td>
                <td class="n" style="width:13.3%; color:var(--red);">{fmt(r['delta'])}</td>
                <td class="n" style="width:13.3%;">{pill_markup(r['pct'])}</td>
            </tr>"""
        t_html += "</tbody></table></div>"
        st.markdown(t_html, unsafe_allow_html=True)
    else:
        st.info("No tracking clients currently display a negative placement variance.")

    # Growing Regions — by MTD Δ%
    section("Growing Regions Profile — Ranked by Δ% Surge")
    growing_regions = reg_mat[reg_mat["delta"] > 0].sort_values("pct", ascending=False)
    gr_col, gr_desc = draw_sortable_header("growing_regions", [("Region Zone", "Region", 4), ("Current", "cur", 2), ("Previous", "prv", 2), ("Δ Volume", "delta", 2), ("Δ %", "pct", 2)])
    growing_regions = growing_regions.sort_values(gr_col, ascending=not gr_desc)
    
    t_html = '<div class="tw"><table class="dash-table"><tbody>'
    for _, r in growing_regions.iterrows():
        t_html += f"""<tr>
            <td style="width:33.3%; font-weight:600; color:var(--green);">{r['Region']}</td>
            <td class="n" style="width:16.6%;">{fmt(r['cur'])}</td>
            <td class="n" style="width:16.6%; color:var(--muted);">{fmt(r['prv'])}</td>
            <td class="n" style="width:16.6%;">{volume_pill(r['delta'])}</td>
            <td class="n" style="width:16.6%;">{pill_markup(r['pct'])}</td>
        </tr>"""
    t_html += "</tbody></table></div>"
    st.markdown(t_html, unsafe_allow_html=True)

    # Vendor Laggards & Leaders Row
    v_left, v_right = st.columns(2)
    vl_master = compute_comparison_matrix(df, "vl_name").reset_index()
    vl_master.columns = ["VL", "cur", "prv", "delta", "pct"]
    
    with v_left:
        section("Top 10 Degrowing Vendor Lines (VL)")
        degrow_vl = vl_master[vl_master["delta"] < 0].nsmallest(10, "delta")
        dv_col, dv_desc = draw_sortable_header("degrow_vls", [("Vendor Partner (VL)", "VL", 5), ("Current", "cur", 2), ("Δ Drop", "delta", 3)])
        degrow_vl = degrow_vl.sort_values(dv_col, ascending=not dv_desc)
        
        t_html = '<div class="tw"><table class="dash-table"><tbody>'
        for _, r in degrow_vl.iterrows():
            t_html += f"""<tr>
                <td style="width:50%; font-weight:600;">{r['VL']}</td>
                <td class="n" style="width:20%;">{fmt(r['cur'])}</td>
                <td class="n" style="width:30%;">{volume_pill(r['delta'])}</td>
            </tr>"""
        t_html += "</tbody></table></div>"
        st.markdown(t_html, unsafe_allow_html=True)

    with v_right:
        section("Top 10 Growing Vendor Lines (VL)")
        grow_vl = vl_master[vl_master["delta"] > 0].nlargest(10, "delta")
        gv_col, gv_desc = draw_sortable_header("growing_vls", [("Vendor Partner (VL)", "VL", 5), ("Current", "cur", 2), ("Δ Surge", "delta", 3)])
        grow_vl = grow_vl.sort_values(gv_col, ascending=not gv_desc)
        
        t_html = '<div class="tw"><table class="dash-table"><tbody>'
        for _, r in grow_vl.iterrows():
            t_html += f"""<tr>
                <td style="width:50%; font-weight:600; color:var(--green);">{r['VL']}</td>
                <td class="n" style="width:20%;">{fmt(r['cur'])}</td>
                <td class="n" style="width:30%;">{volume_pill(r['delta'])}</td>
            </tr>"""
        t_html += "</tbody></table></div>"
        st.markdown(t_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: AI INSIGHT SUMMARY & RCA
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    section("Automated Performance Attribution Profile")
    
    # Structural Calculation Elements (Attribution Vectors)
    att_df = pd.DataFrame([
        {"dim": "Client Account", "name": r["Client"], "delta": r["delta"]} for _, r in client_mat.iterrows()
    ] + [
        {"dim": "Regional Zone", "name": r["Region"], "delta": r["delta"]} for _, r in reg_mat.iterrows()
    ] + [
        {"dim": "Vendor Partner (VL)", "name": r["VL"], "delta": r["delta"]} for _, r in vl_master.iterrows()
    ])
    
    top_performers = att_df.nlargest(3, "delta")
    worst_laggards = att_df.nsmallest(3, "delta")
    
    worst_client = client_mat.nsmallest(1, "delta").iloc[0] if not client_mat.empty else None
    worst_region = reg_mat.nsmallest(1, "delta").iloc[0] if not reg_mat.empty else None
    
    summary_trend = "a operational decline" if dlt_tot < 0 else "a positive expansion trajectory"
    color_token = "var(--red)" if dlt_tot < 0 else "var(--green)"
    
    st.markdown(f"""
    <div class="rca-card">
      <div class="rca-ttl">Executive Attribution Overview</div>
      <div class="rca-body">
        Evaluations across active operational boundaries show {summary_trend} of 
        <strong style="color:{color_token}">{fmt(abs(dlt_tot))} final placements (FT)</strong> 
        ({pct_tot:+.1f}% shift) compared to the previous timeframe baseline. 
        {"Primary headwinds were concentrated inside the <strong>" + worst_region['Region'] + "</strong> region, led by underperformance inside <strong>" + worst_client['Client'] + "</strong> accounts." if dlt_tot < 0 and worst_client is not None else "Operational execution patterns remain stable across main regional vectors."}
      </div>
    </div>""", unsafe_allow_html=True)
    
    as_left, as_right = st.columns(2)
    
    with as_left:
        st.markdown('<div class="rca-card"><div class="rca-ttl">Top Growth Drivers</div>', unsafe_allow_html=True)
        for _, r in top_performers.iterrows():
            if r["delta"] > 0:
                st.markdown(f"""<div class="rca-item"><div class="rca-dot dot-g"></div>
                    <div><strong>[{r['dim']}]</strong> {r['name']} generated an increase of <span style="color:var(--green); font-weight:700;">+{int(r['delta']):,}</span> placements.</div>
                </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with as_right:
        st.markdown('<div class="rca-card"><div class="rca-ttl">Top Deficit Drivers</div>', unsafe_allow_html=True)
        for _, r in worst_laggards.iterrows():
            if r["delta"] < 0:
                st.markdown(f"""<div class="rca-item"><div class="rca-dot dot-r"></div>
                    <div><strong>[{r['dim']}]</strong> {r['name']} generated a loss of <span style="color:var(--red); font-weight:700;">{int(r['delta']):,}</span> placements.</div>
                </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
