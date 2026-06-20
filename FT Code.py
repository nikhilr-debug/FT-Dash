import streamlit as st
import pandas as pd
import requests
import datetime
import numpy as np

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Vahan Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --bg: #f5f4f0;
  --surface: #ffffff;
  --border: rgba(0,0,0,0.08);
  --text: #111111;
  --muted: #666666;
  --green-fg: #1e5c14;
  --green-bg: #eef6e8;
  --red-fg: #8b1a1a;
  --red-bg: #fdf0f0;
  --accent: #2d6a4f;
}

html, body, [class*="css"] {
  font-family: 'Inter', sans-serif;
  background-color: var(--bg) !important;
  color: var(--text);
}

.stApp {
  background-color: var(--bg) !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
  padding: 2rem 2.5rem 4rem !important;
  max-width: 1400px;
}

/* Page header */
.dash-header {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 0.25rem;
}
.dash-title {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--text);
}
.dash-subtitle {
  font-size: 0.85rem;
  color: var(--muted);
  font-weight: 400;
}
.period-badge {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 3px 10px;
  border-radius: 99px;
  background: #e8e6e0;
  color: var(--muted);
  margin-left: 0.5rem;
}

/* Metric card */
.metric-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  min-height: 108px;
}
.metric-label {
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.5rem;
}
.metric-value {
  font-size: 2rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  color: var(--text);
  line-height: 1;
  margin-bottom: 0.4rem;
}
.metric-sub {
  font-size: 0.78rem;
  color: var(--muted);
}

/* Delta pill */
.pill {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 99px;
}
.pill-pos { color: var(--green-fg); background: var(--green-bg); }
.pill-neg { color: var(--red-fg);   background: var(--red-bg); }
.pill-neu { color: var(--muted);    background: #f0efeb; }

/* Section label */
.section-label {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
  margin: 1.75rem 0 0.75rem;
  border-bottom: 1px solid var(--border);
  padding-bottom: 0.4rem;
}

/* Data table */
.dash-table {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
  width: 100%;
  border-collapse: collapse;
  font-size: 0.84rem;
}
.dash-table th {
  background: #f8f7f3;
  font-size: 0.70rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--muted);
  padding: 10px 16px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}
.dash-table td {
  padding: 10px 16px;
  border-bottom: 1px solid rgba(0,0,0,0.04);
  color: var(--text);
  vertical-align: middle;
}
.dash-table tr:last-child td { border-bottom: none; }
.dash-table tr:hover td { background: #fafaf8; }
.td-right { text-align: right; }
.td-bold { font-weight: 600; }

/* Funnel bar */
.funnel-bar-wrap {
  background: #f0efeb;
  border-radius: 4px;
  height: 6px;
  width: 100%;
  overflow: hidden;
  display: inline-block;
  vertical-align: middle;
}
.funnel-bar-fill {
  height: 100%;
  background: var(--accent);
  border-radius: 4px;
}

/* RCA block */
.rca-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem 2rem;
  margin-bottom: 1rem;
}
.rca-title {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 0.75rem;
}
.rca-body {
  font-size: 0.9rem;
  line-height: 1.7;
  color: var(--text);
}
.rca-item {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  margin-bottom: 0.5rem;
  font-size: 0.88rem;
  line-height: 1.5;
}
.rca-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  margin-top: 0.45rem;
  flex-shrink: 0;
}
.dot-pos { background: var(--green-fg); }
.dot-neg { background: #c0392b; }
.dot-neu { background: #aaaaaa; }

/* Stframe override */
div[data-testid="stHorizontalBlock"] > div { gap: 1rem; }
div[data-testid="metric-container"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ─── Data fetching ─────────────────────────────────────────────────────────────
API_URL = "https://redash.vahan.link/api/queries/17613/results.json?api_key=4aFm2iOoyx8I91svQccdeZr0jmaiUsMFSRinZcmu"

@st.cache_data(ttl=3600)
def fetch_data():
    try:
        r = requests.get(API_URL, timeout=30)
        r.raise_for_status()
        rows = r.json()["query_result"]["data"]["rows"]
        return pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        return pd.DataFrame()

# ─── Date parsing ──────────────────────────────────────────────────────────────
DATE_COLS = [
    "referral_date_si", "marked_unique", "activation_date", "first_date_of_work",
    "5th_order_date", "10th_order_date", "20th_order_date", "30th_order_date",
    "50th_order_date", "60th_order_date", "80th_order_date", "100th_order_date",
    "120th_order_date", "150th_order_date", "200th_order_date",
]

def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    for col in DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    return df

# ─── Time window calculation ──────────────────────────────────────────────────
def get_windows(mode: str):
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    if mode == "WTD":
        # Current: Mon of this week → yesterday
        dow = today.weekday()  # Mon=0
        cur_start = today - datetime.timedelta(days=dow)
        cur_end = yesterday

        # Previous: Mon of last week → same relative day (cur_end - 7)
        prev_start = cur_start - datetime.timedelta(weeks=1)
        prev_end = cur_end - datetime.timedelta(weeks=1)
    else:  # MTD
        cur_start = today.replace(day=1)
        cur_end = yesterday
        # Previous month same day span
        if today.month == 1:
            prev_month_start = today.replace(year=today.year - 1, month=12, day=1)
        else:
            prev_month_start = today.replace(month=today.month - 1, day=1)
        day_offset = (cur_end - cur_start).days
        prev_start = prev_month_start
        prev_end = prev_month_start + datetime.timedelta(days=day_offset)

    return cur_start, cur_end, prev_start, prev_end

# ─── Helpers ──────────────────────────────────────────────────────────────────
def fmt_num(n):
    if pd.isna(n): return "—"
    n = int(n)
    if abs(n) >= 1_000_000: return f"{n/1_000_000:.1f}M"
    return f"{n:,}"

def fmt_pct(p):
    if pd.isna(p) or not np.isfinite(p): return "—"
    return f"{p:+.1f}%"

def fmt_pp(p):
    if pd.isna(p) or not np.isfinite(p): return "—"
    return f"{p:+.1f}pp"

def delta_pill(val, is_pct=False):
    if pd.isna(val) or not np.isfinite(val):
        return '<span class="pill pill-neu">—</span>'
    sym = "+" if val > 0 else ""
    cls = "pill-pos" if val > 0 else ("pill-neg" if val < 0 else "pill-neu")
    txt = f"{sym}{val:.1f}%" if is_pct else f"{sym}{int(val):,}"
    return f'<span class="pill {cls}">{txt}</span>'

def count_in_window(df, col, start, end):
    if col not in df.columns:
        return 0
    s = df[col]
    mask = s.notna() & (s >= start) & (s <= end)
    return int(mask.sum())

def agg_placements(df, col, start, end, group_by):
    if col not in df.columns or group_by not in df.columns:
        return pd.Series(dtype=int)
    sub = df[df[col].notna() & (df[col] >= start) & (df[col] <= end)]
    return sub.groupby(group_by)[col].count()

def build_comparison(df, col, start_c, end_c, start_p, end_p, group_by):
    cur = agg_placements(df, col, start_c, end_c, group_by).rename("cur")
    prv = agg_placements(df, col, start_p, end_p, group_by).rename("prv")
    res = pd.concat([cur, prv], axis=1).fillna(0).astype(int)
    res["delta"] = res["cur"] - res["prv"]
    res["pct"] = np.where(res["prv"] > 0, (res["delta"] / res["prv"]) * 100, np.nan)
    return res.sort_values("delta")

# ─── HTML table builder ───────────────────────────────────────────────────────
def render_table(df_in, cols, headers, align_right=None):
    if align_right is None: align_right = set()
    rows_html = ""
    for _, row in df_in.iterrows():
        cells = ""
        for col in cols:
            val = row.get(col, "")
            cls = " td-right" if col in align_right else ""
            cells += f'<td class="dash-table-td{cls}">{val}</td>'
        rows_html += f"<tr>{cells}</tr>"
    header_html = "".join(f"<th>{h}</th>" for h in headers)
    return f"""
    <table class="dash-table">
      <thead><tr>{header_html}</tr></thead>
      <tbody>{rows_html}</tbody>
    </table>"""

def metric_card(label, value, sub="", delta_html=""):
    return f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value">{value}</div>
      <div class="metric-sub">{sub} {delta_html}</div>
    </div>"""

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ═══════════════════════════════════════════════════════════════════════════════

with st.spinner("Loading data…"):
    raw = fetch_data()

if raw.empty:
    st.warning("No data available. Check API connectivity.")
    st.stop()

df = parse_dates(raw.copy())

# ─── Header ──────────────────────────────────────────────────────────────────
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown(f"""
    <div class="dash-header">
      <span class="dash-title">Vahan Performance Dashboard</span>
      <span class="dash-subtitle">as of {yesterday.strftime('%d %b %Y')}</span>
    </div>
    """, unsafe_allow_html=True)

with col_h2:
    mode = st.selectbox("", ["WTD", "MTD"], label_visibility="collapsed")

cur_start, cur_end, prev_start, prev_end = get_windows(mode)

period_label = f"{cur_start.strftime('%d %b')} – {cur_end.strftime('%d %b')} vs {prev_start.strftime('%d %b')} – {prev_end.strftime('%d %b')}"
st.markdown(f'<span class="period-badge">{period_label}</span>', unsafe_allow_html=True)
st.markdown("<div style='margin-bottom:1.5rem'></div>", unsafe_allow_html=True)

# ─── Global counts ────────────────────────────────────────────────────────────
ft_col = "first_date_of_work"
cur_total = count_in_window(df, ft_col, cur_start, cur_end)
prv_total = count_in_window(df, ft_col, prev_start, prev_end)
delta_total = cur_total - prv_total
pct_total = (delta_total / prv_total * 100) if prv_total > 0 else np.nan

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Client View", "Region & AM View", "Funnel Health", "AI Summary & RCA"])

# ══════════════════════════════════════════════════════
# TAB 1 — CLIENT VIEW
# ══════════════════════════════════════════════════════
with tab1:
    # Summary metrics row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card("Current Period FT", fmt_num(cur_total),
                                f"{cur_start.strftime('%d %b')} – {cur_end.strftime('%d %b')}"), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Previous Period FT", fmt_num(prv_total),
                                f"{prev_start.strftime('%d %b')} – {prev_end.strftime('%d %b')}"), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("Volume Change (Δ)", fmt_num(delta_total),
                                "absolute", delta_pill(delta_total)), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card("Change %", f"{pct_total:+.1f}%" if np.isfinite(pct_total) else "—",
                                "period-over-period", delta_pill(pct_total, is_pct=True)), unsafe_allow_html=True)

    # Client summary table
    st.markdown('<div class="section-label">Client Performance</div>', unsafe_allow_html=True)

    client_df = build_comparison(df, ft_col, cur_start, cur_end, prev_start, prev_end, "company_name")
    client_df = client_df.reset_index()
    client_df.columns = ["Client", "Current", "Previous", "Δ", "Δ%"]

    # Build display rows
    rows_display = []
    for _, row in client_df.iterrows():
        rows_display.append({
            "client": row["Client"],
            "cur": fmt_num(row["Current"]),
            "prv": fmt_num(row["Previous"]),
            "delta": delta_pill(row["Δ"]),
            "pct": delta_pill(row["Δ%"], is_pct=True),
        })

    tbl_html = """
    <table class="dash-table">
      <thead><tr>
        <th>Client</th>
        <th style="text-align:right">Current</th>
        <th style="text-align:right">Previous</th>
        <th style="text-align:right">Δ Volume</th>
        <th style="text-align:right">Δ %</th>
      </tr></thead><tbody>"""
    for r in rows_display:
        tbl_html += f"""<tr>
          <td class="td-bold">{r['client']}</td>
          <td class="td-right">{r['cur']}</td>
          <td class="td-right">{r['prv']}</td>
          <td class="td-right">{r['delta']}</td>
          <td class="td-right">{r['pct']}</td>
        </tr>"""
    tbl_html += "</tbody></table>"
    st.markdown(tbl_html, unsafe_allow_html=True)

    # Expandable: Client → Region → VL breakdown
    st.markdown('<div class="section-label">Client → Region → VL Breakdown</div>', unsafe_allow_html=True)

    top_clients = client_df.nlargest(5, "Δ", keep="all")["Client"].tolist() if len(client_df) > 0 else []
    bottom_clients = client_df.nsmallest(5, "Δ", keep="all")["Client"].tolist() if len(client_df) > 0 else []
    focus_clients = list(dict.fromkeys(bottom_clients + top_clients))  # deduplicated

    all_clients = sorted(df["company_name"].dropna().unique().tolist()) if "company_name" in df.columns else []
    selected_client = st.selectbox("Select client to drill down", all_clients if all_clients else ["No data"])

    if selected_client and "company_name" in df.columns:
        sub_df = df[df["company_name"] == selected_client]
        with st.expander(f"Breakdown: {selected_client}", expanded=True):
            # Region breakdown
            reg_df = build_comparison(sub_df, ft_col, cur_start, cur_end, prev_start, prev_end, "region").reset_index()
            if not reg_df.empty:
                st.markdown("**By Region**")
                r_html = """<table class="dash-table"><thead><tr>
                  <th>Region</th><th style="text-align:right">Current</th>
                  <th style="text-align:right">Previous</th><th style="text-align:right">Δ</th>
                  <th style="text-align:right">Δ%</th></tr></thead><tbody>"""
                for _, row in reg_df.iterrows():
                    r_html += f"""<tr>
                      <td>{row.iloc[0]}</td>
                      <td class="td-right">{fmt_num(row['cur'])}</td>
                      <td class="td-right">{fmt_num(row['prv'])}</td>
                      <td class="td-right">{delta_pill(row['delta'])}</td>
                      <td class="td-right">{delta_pill(row['pct'], is_pct=True)}</td>
                    </tr>"""
                r_html += "</tbody></table>"
                st.markdown(r_html, unsafe_allow_html=True)

            # VL breakdown
            if "vl_name" in sub_df.columns:
                vl_df = build_comparison(sub_df, ft_col, cur_start, cur_end, prev_start, prev_end, "vl_name").reset_index()
                if not vl_df.empty:
                    st.markdown("**By VL Partner**")
                    v_html = """<table class="dash-table"><thead><tr>
                      <th>VL Partner</th><th style="text-align:right">Current</th>
                      <th style="text-align:right">Previous</th><th style="text-align:right">Δ</th>
                      <th style="text-align:right">Δ%</th></tr></thead><tbody>"""
                    for _, row in vl_df.iterrows():
                        v_html += f"""<tr>
                          <td>{row.iloc[0]}</td>
                          <td class="td-right">{fmt_num(row['cur'])}</td>
                          <td class="td-right">{fmt_num(row['prv'])}</td>
                          <td class="td-right">{delta_pill(row['delta'])}</td>
                          <td class="td-right">{delta_pill(row['pct'], is_pct=True)}</td>
                        </tr>"""
                    v_html += "</tbody></table>"
                    st.markdown(v_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# TAB 2 — REGION & AM VIEW
# ══════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-label">Global Summary</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(metric_card("Current Period", fmt_num(cur_total)), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Previous Period", fmt_num(prv_total)), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("Δ Volume", fmt_num(delta_total), "", delta_pill(delta_total)), unsafe_allow_html=True)
    with c4:
        st.markdown(metric_card("Δ %", f"{pct_total:+.1f}%" if np.isfinite(pct_total) else "—",
                                "", delta_pill(pct_total, is_pct=True)), unsafe_allow_html=True)

    col_r, col_a = st.columns(2)

    def render_group_table(group_col, title, parent_col=col_r):
        with parent_col:
            st.markdown(f'<div class="section-label">{title}</div>', unsafe_allow_html=True)
            if group_col not in df.columns:
                st.info(f"Column `{group_col}` not available.")
                return
            grp = build_comparison(df, ft_col, cur_start, cur_end, prev_start, prev_end, group_col).reset_index()
            if grp.empty:
                st.info("No data for this period.")
                return
            html = """<table class="dash-table"><thead><tr>
              <th style="min-width:130px">{}</th>
              <th style="text-align:right">Current</th>
              <th style="text-align:right">Previous</th>
              <th style="text-align:right">Δ</th>
              <th style="text-align:right">Δ%</th>
            </tr></thead><tbody>""".format(title.split(" ")[0])
            for _, row in grp.iterrows():
                html += f"""<tr>
                  <td class="td-bold">{row.iloc[0]}</td>
                  <td class="td-right">{fmt_num(row['cur'])}</td>
                  <td class="td-right">{fmt_num(row['prv'])}</td>
                  <td class="td-right">{delta_pill(row['delta'])}</td>
                  <td class="td-right">{delta_pill(row['pct'], is_pct=True)}</td>
                </tr>"""
            html += "</tbody></table>"
            st.markdown(html, unsafe_allow_html=True)

    render_group_table("region", "Region Breakdown", col_r)
    render_group_table("am_name", "Account Manager Breakdown", col_a)

    st.markdown('<div class="section-label">Source Channel & Lead Referral Type</div>', unsafe_allow_html=True)
    col_s, col_p = st.columns(2)
    render_group_table("lead_source", "Source Channel", col_s)
    render_group_table("lead_referral_type", "Product Category", col_p)

# ══════════════════════════════════════════════════════
# TAB 3 — FUNNEL HEALTH
# ══════════════════════════════════════════════════════
with tab3:
    stages = [
        ("referral_date_si", "Leads"),
        ("marked_unique",    "Unique Leads"),
        ("activation_date",  "Onboarded (OB)"),
        ("first_date_of_work", "Placements (FT)"),
    ]

    cur_counts = {label: count_in_window(df, col, cur_start, cur_end) for col, label in stages}
    prv_counts = {label: count_in_window(df, col, prev_start, prev_end) for col, label in stages}

    st.markdown('<div class="section-label">Funnel Volume — Current vs Previous</div>', unsafe_allow_html=True)

    cols_f = st.columns(4)
    for i, (_, label) in enumerate(stages):
        cur_v = cur_counts[label]
        prv_v = prv_counts[label]
        d = cur_v - prv_v
        p = (d / prv_v * 100) if prv_v > 0 else np.nan
        with cols_f[i]:
            st.markdown(metric_card(label, fmt_num(cur_v),
                                    f"Prev: {fmt_num(prv_v)}", delta_pill(d)), unsafe_allow_html=True)

    # Conversion rates
    st.markdown('<div class="section-label">Conversion Rates & Stage Drops</div>', unsafe_allow_html=True)

    def conv_rate(numerator, denominator):
        return (numerator / denominator * 100) if denominator > 0 else 0.0

    funnel_labels = [label for _, label in stages]
    conversions = [
        ("Leads → Unique",      "Leads",          "Unique Leads"),
        ("Unique → Onboarded",  "Unique Leads",   "Onboarded (OB)"),
        ("Onboarded → FT",      "Onboarded (OB)", "Placements (FT)"),
    ]

    conv_html = """<table class="dash-table"><thead><tr>
      <th>Conversion Stage</th>
      <th style="text-align:right">Current Rate</th>
      <th style="text-align:right">Previous Rate</th>
      <th style="text-align:right">Δ (pp)</th>
      <th>Visual</th>
    </tr></thead><tbody>"""

    for name, num_lbl, den_lbl in conversions:
        cur_r = conv_rate(cur_counts[num_lbl], cur_counts[den_lbl])
        prv_r = conv_rate(prv_counts[num_lbl], prv_counts[den_lbl])
        pp = cur_r - prv_r
        pp_cls = "pill-pos" if pp >= 0 else "pill-neg"
        bar_w = min(100, int(cur_r))
        conv_html += f"""<tr>
          <td class="td-bold">{name}</td>
          <td class="td-right">{cur_r:.1f}%</td>
          <td class="td-right">{prv_r:.1f}%</td>
          <td class="td-right"><span class="pill {pp_cls}">{pp:+.1f}pp</span></td>
          <td style="width:120px;padding:10px 16px">
            <div class="funnel-bar-wrap">
              <div class="funnel-bar-fill" style="width:{bar_w}%"></div>
            </div>
          </td>
        </tr>"""

    conv_html += "</tbody></table>"
    st.markdown(conv_html, unsafe_allow_html=True)

    # Progressive milestone volume
    milestone_cols = [
        "5th_order_date", "10th_order_date", "20th_order_date", "30th_order_date",
        "50th_order_date", "60th_order_date", "80th_order_date", "100th_order_date",
        "120th_order_date", "150th_order_date", "200th_order_date",
    ]
    available_milestones = [c for c in milestone_cols if c in df.columns]

    if available_milestones:
        st.markdown('<div class="section-label">Progressive Milestone Volumes</div>', unsafe_allow_html=True)
        ms_html = """<table class="dash-table"><thead><tr>
          <th>Milestone</th>
          <th style="text-align:right">Current</th>
          <th style="text-align:right">Previous</th>
          <th style="text-align:right">Δ</th>
        </tr></thead><tbody>"""
        for mc in available_milestones:
            label = mc.replace("_order_date", " Orders").replace("_date", "").replace("_", " ").title()
            cv = count_in_window(df, mc, cur_start, cur_end)
            pv = count_in_window(df, mc, prev_start, prev_end)
            d = cv - pv
            ms_html += f"""<tr>
              <td>{label}</td>
              <td class="td-right">{fmt_num(cv)}</td>
              <td class="td-right">{fmt_num(pv)}</td>
              <td class="td-right">{delta_pill(d)}</td>
            </tr>"""
        ms_html += "</tbody></table>"
        st.markdown(ms_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
# TAB 4 — AI SUMMARY & RCA
# ══════════════════════════════════════════════════════
with tab4:
    # ── Programmatic RCA logic ─────────────────────────────────────────────────

    # Rebuild client comparison for RCA
    client_rca = build_comparison(df, ft_col, cur_start, cur_end, prev_start, prev_end, "company_name").reset_index()
    region_rca = build_comparison(df, ft_col, cur_start, cur_end, prev_start, prev_end, "region").reset_index() \
        if "region" in df.columns else pd.DataFrame()
    am_rca = build_comparison(df, ft_col, cur_start, cur_end, prev_start, prev_end, "am_name").reset_index() \
        if "am_name" in df.columns else pd.DataFrame()

    # Top & bottom movers (client + region combined)
    all_movers = []
    for _, row in client_rca.iterrows():
        all_movers.append({"dim": "Client", "name": row.iloc[0], "delta": row["delta"], "pct": row["pct"]})
    if not region_rca.empty:
        for _, row in region_rca.iterrows():
            all_movers.append({"dim": "Region", "name": row.iloc[0], "delta": row["delta"], "pct": row["pct"]})
    movers_df = pd.DataFrame(all_movers).dropna(subset=["delta"])

    top3 = movers_df.nlargest(3, "delta")
    bot3 = movers_df.nsmallest(3, "delta")

    # Conversion bottlenecks (>2pp drop)
    bottlenecks = []
    for name, num_lbl, den_lbl in [
        ("Leads → Unique", "Leads", "Unique Leads"),
        ("Unique → Onboarded", "Unique Leads", "Onboarded (OB)"),
        ("Onboarded → FT", "Onboarded (OB)", "Placements (FT)"),
    ]:
        cur_r = conv_rate(cur_counts[num_lbl], cur_counts[den_lbl])
        prv_r = conv_rate(prv_counts[num_lbl], prv_counts[den_lbl])
        pp = cur_r - prv_r
        if pp < -2.0:
            bottlenecks.append((name, pp))

    # Identify largest structural driver
    stage_deltas = {
        "Lead generation":   count_in_window(df, "referral_date_si", cur_start, cur_end) -
                              count_in_window(df, "referral_date_si", prev_start, prev_end),
        "Uniqueness filter": count_in_window(df, "marked_unique", cur_start, cur_end) -
                              count_in_window(df, "marked_unique", prev_start, prev_end),
        "Onboarding":        count_in_window(df, "activation_date", cur_start, cur_end) -
                              count_in_window(df, "activation_date", prev_start, prev_end),
        "Placement (FT)":    delta_total,
    }
    worst_stage = min(stage_deltas, key=lambda k: stage_deltas[k])
    trend_word = "declined" if delta_total < 0 else "improved"
    trend_dir  = "downward" if delta_total < 0 else "positive"

    # ── Render RCA ──────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="rca-card">
      <div class="rca-title">Executive Overview</div>
      <div class="rca-body">
        Total placements (FT) <strong>{trend_word}</strong> by <strong>{fmt_num(abs(delta_total))}</strong>
        ({f"{pct_total:+.1f}%" if np.isfinite(pct_total) else "N/A"}) period-over-period ({mode}),
        moving from <strong>{fmt_num(prv_total)}</strong> to <strong>{fmt_num(cur_total)}</strong>.
        The <strong>{worst_stage}</strong> layer experienced the most significant {trend_dir} pressure,
        contributing the largest share of the overall variance.
        Immediate attention is warranted to the dimensions listed below to arrest further deterioration
        or capitalise on existing momentum.
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_pos, col_neg = st.columns(2)

    with col_pos:
        st.markdown('<div class="rca-card"><div class="rca-title">Top 3 Positive Movers</div>', unsafe_allow_html=True)
        items_html = ""
        if top3.empty:
            items_html = '<div class="rca-body" style="color:var(--muted)">No positive movers in this period.</div>'
        else:
            for _, row in top3.iterrows():
                pct_str = f"{row['pct']:+.1f}%" if pd.notna(row["pct"]) and np.isfinite(row["pct"]) else ""
                items_html += f"""<div class="rca-item">
                  <div class="rca-dot dot-pos" style="margin-top:6px"></div>
                  <div><strong>[{row['dim']}] {row['name']}</strong> gained
                  <strong>{fmt_num(row['delta'])}</strong> placements {pct_str}</div>
                </div>"""
        st.markdown(items_html + "</div>", unsafe_allow_html=True)

    with col_neg:
        st.markdown('<div class="rca-card"><div class="rca-title">Top 3 Bottom Movers</div>', unsafe_allow_html=True)
        items_html = ""
        if bot3.empty:
            items_html = '<div class="rca-body" style="color:var(--muted)">No negative movers in this period.</div>'
        else:
            for _, row in bot3.iterrows():
                pct_str = f"{row['pct']:+.1f}%" if pd.notna(row["pct"]) and np.isfinite(row["pct"]) else ""
                items_html += f"""<div class="rca-item">
                  <div class="rca-dot dot-neg" style="margin-top:6px"></div>
                  <div><strong>[{row['dim']}] {row['name']}</strong> dropped
                  <strong>{fmt_num(abs(row['delta']))}</strong> placements {pct_str}</div>
                </div>"""
        st.markdown(items_html + "</div>", unsafe_allow_html=True)

    # Conversion bottlenecks
    st.markdown('<div class="rca-card"><div class="rca-title">Conversion Bottlenecks (&gt;2pp Drop)</div>', unsafe_allow_html=True)
    if not bottlenecks:
        st.markdown('<div class="rca-body" style="color:var(--muted)">No conversion stage experienced a drop exceeding 2 percentage points in this period.</div></div>', unsafe_allow_html=True)
    else:
        b_html = ""
        for stage_name, pp_val in bottlenecks:
            b_html += f"""<div class="rca-item">
              <div class="rca-dot dot-neg" style="margin-top:6px"></div>
              <div>The <strong>{stage_name}</strong> conversion rate dropped by
              <strong>{pp_val:.1f}pp</strong>, indicating a structural leak in this funnel stage
              that requires root-cause investigation.</div>
            </div>"""
        st.markdown(b_html + "</div>", unsafe_allow_html=True)

    # Funnel snapshot table in RCA tab
    st.markdown('<div class="section-label">Funnel Snapshot</div>', unsafe_allow_html=True)
    snap_html = """<table class="dash-table"><thead><tr>
      <th>Stage</th>
      <th style="text-align:right">Current</th>
      <th style="text-align:right">Previous</th>
      <th style="text-align:right">Δ</th>
      <th style="text-align:right">Δ%</th>
    </tr></thead><tbody>"""
    for _, label in stages:
        cv = cur_counts[label]
        pv = prv_counts[label]
        d  = cv - pv
        p  = (d / pv * 100) if pv > 0 else np.nan
        snap_html += f"""<tr>
          <td class="td-bold">{label}</td>
          <td class="td-right">{fmt_num(cv)}</td>
          <td class="td-right">{fmt_num(pv)}</td>
          <td class="td-right">{delta_pill(d)}</td>
          <td class="td-right">{delta_pill(p, is_pct=True)}</td>
        </tr>"""
    snap_html += "</tbody></table>"
    st.markdown(snap_html, unsafe_allow_html=True)

    # Refresh hint
    st.markdown(f"""
    <div style="margin-top:2rem;font-size:0.75rem;color:var(--muted);text-align:right">
      Data cached for 1 hour · Last fetched at session start ·
      Period: {cur_start.strftime('%d %b')} – {cur_end.strftime('%d %b %Y')}
    </div>""", unsafe_allow_html=True)
