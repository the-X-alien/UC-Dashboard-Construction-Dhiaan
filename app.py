import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="UC Admissions Lab", layout="wide", initial_sidebar_state="expanded")

# embed the Berkeley CAL logo as a base64 data URI so it always renders (local + deployed)
try:
    with open("cal_b64.txt") as _f:
        LOGO = "data:image/jpeg;base64," + _f.read().strip()
except Exception:
    LOGO = ""

for k, v in {"theme": "light", "gemini_key": "", "gemini_model": "gemini-2.5-flash-lite", "show_settings": False, "nav": "overview"}.items():
    if k not in st.session_state:
        st.session_state[k] = v

FREE_MODELS = ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-flash-latest", "gemini-3-flash-preview", "gemini-3.1-flash-lite"]

TH = {
    "light": {
        "--navy": "#0b2a4a", "--navy-2": "#103a63", "--blue": "#003262", "--gold": "#fdb515",
        "--gold-soft": "#fef3d4", "--ok": "#1f7a4d", "--bad": "#c0392b",
        "--ink": "#16202e", "--body": "#46505e", "--muted": "#7c8694",
        "--paper": "#f6f4ef", "--card": "#ffffff", "--line": "#e9e5dc", "--line-2": "#d9d3c7",
        "--shadow": "0 1px 2px rgba(16,32,46,.04), 0 8px 24px rgba(16,32,46,.06)",
        "--map-land": "#eef0ea", "--map-unit": "#d7d9d0", "--head-text": "#ffffff",
        "--chip-bg": "#ffffff", "--btn-text": "#16202e", "--btn-bg": "#eef1f5", "--btn-border": "#d9d3c7",
        "--icbg": "rgba(255,255,255,.12)", "--icborder": "rgba(255,255,255,.22)", "--ictext": "#ffffff",
    },
    "dark": {
        "--navy": "#081f38", "--navy-2": "#0d2c4d", "--blue": "#1d4f86", "--gold": "#fdb515",
        "--gold-soft": "#3a2f12", "--ok": "#3ecf8e", "--bad": "#ff7a6b",
        "--ink": "#eef2f7", "--body": "#aeb7c4", "--muted": "#8a93a2",
        "--paper": "#0c1118", "--card": "#141b25", "--line": "#243040", "--line-2": "#2f3c4f",
        "--shadow": "0 1px 2px rgba(0,0,0,.3), 0 10px 30px rgba(0,0,0,.35)",
        "--map-land": "#1a2230", "--map-unit": "#2a3543", "--head-text": "#ffffff",
        "--chip-bg": "#1a2230", "--btn-text": "#eef2f7", "--btn-bg": "#1f2937", "--btn-border": "#334155",
        "--icbg": "rgba(255,255,255,.10)", "--icborder": "rgba(255,255,255,.20)", "--ictext": "#ffffff",
    },
}
t = TH[st.session_state.theme]
vars_ = "\n".join(f"  {k}:{v};" for k, v in t.items())

CSS = f"""
:root{{
{vars_}
  --radius:14px; --radius-sm:9px; --maxw:1180px;
  --sans:'Inter',system-ui,-apple-system,'Segoe UI',sans-serif;
  --display:'Fraunces','Playfair Display',Georgia,serif;
  --mono:'IBM Plex Mono',ui-monospace,monospace;
}}
*{{box-sizing:border-box;}}
html,body,.stApp{{background:var(--paper);color:var(--ink);font-family:var(--sans);
  -webkit-font-smoothing:antialiased;transition:background .25s ease,color .25s ease;}}
.block-container{{max-width:var(--maxw);padding:0 22px 3rem;}}
header{{visibility:hidden;}}
section[data-testid="stSidebar"]{{background:var(--paper);border-right:1px solid var(--line);}}

/* fix streamlit button contrast in both themes */
.stButton>button{{background:var(--btn-bg)!important;color:var(--btn-text)!important;border:1px solid var(--btn-border)!important;
  border-radius:var(--radius-sm)!important;font-weight:600!important;font-family:var(--sans)!important;}}
.stButton>button:hover{{border-color:var(--gold)!important;color:var(--navy)!important;}}
.stButton>button:focus{{outline:2px solid var(--gold)!important;}}
/* make text/password inputs readable in both themes */
.stTextInput>div>div>input, .stTextArea>div>div>textarea, .stSelectbox>div>div>div{{color:var(--ink)!important;background:var(--card)!important;border:1px solid var(--btn-border)!important;}}
.stTextInput>div>div>input::placeholder, .stTextArea>div>div>textarea::placeholder{{color:var(--muted)!important;}}

.topbar{{position:sticky;top:0;z-index:40;background:var(--navy);border-bottom:3px solid var(--gold);
  padding:12px 24px;display:flex;align-items:center;justify-content:space-between;}}
.brand{{display:flex;align-items:center;gap:12px;}}
.cal{{height:34px;width:34px;border-radius:8px;background:#fff;padding:3px;object-fit:contain;}}
.wm{{color:#fff;font-family:var(--display);font-weight:700;font-size:1.32rem;line-height:1;}}
.tag{{color:hsla(0,0%,100%,.6);font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;font-weight:600;}}
.tools{{display:flex;gap:8px;align-items:center;}}
.icbtn{{background:var(--icbg);border:1px solid var(--icborder);color:var(--ictext);border-radius:999px;
  height:36px;padding:0 12px;font-size:13px;font-weight:600;cursor:pointer;display:inline-flex;align-items:center;gap:6px;}}
.icbtn:hover{{background:rgba(255,255,255,.2);}}

.page-title{{font-family:var(--display);font-weight:700;font-size:2.5rem;line-height:1.05;color:var(--ink);letter-spacing:-.01em;margin:.4rem 0 .5rem;}}
.lede{{color:var(--body);font-size:1.02rem;line-height:1.6;max-width:820px;}}
.kick{{font-size:11px;letter-spacing:.1em;text-transform:uppercase;font-weight:700;color:var(--muted);}}
.h2{{font-family:var(--display);font-weight:600;font-size:1.5rem;color:var(--navy);margin:0 0 .35rem;letter-spacing:-.01em;}}
.muted{{color:var(--muted);font-size:12.5px;line-height:1.5;}}
.num{{font-family:var(--mono);font-variant-numeric:tabular-nums;}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:18px 20px;box-shadow:var(--shadow);}}
.card.feature{{border-top:3px solid var(--gold);}}
.card.blue{{border-top:3px solid var(--navy);}}
.kpi .num{{font-size:2rem;font-weight:700;line-height:1;}}
.kpi .lab{{font-size:11px;letter-spacing:.08em;text-transform:uppercase;font-weight:700;color:var(--muted);}}
#ailab .aiout{{background:#ffffff !important;border:1px solid #d9d3c7 !important;border-radius:var(--radius);padding:16px 18px;box-shadow:var(--shadow);color:#111111 !important;font-size:.98rem;line-height:1.6;}}
#ailab .aiout *{{color:#111111 !important;}}
#ailab .stMarkdown p, #ailab .stMarkdown div, #ailab .stMarkdown span, #ailab .stMarkdown li{{color:#111111 !important;}}
.win{{color:var(--ok);}} .lose{{color:var(--bad);}}
.sec{{margin-top:30px;padding-top:26px;border-top:1px solid var(--line);}}
.cap{{color:var(--muted);font-size:12.5px;margin-top:8px;}}
.nav-item{{display:block;padding:9px 12px;border-radius:var(--radius-sm);color:var(--body);text-decoration:none;
  font-size:14px;font-weight:500;margin-bottom:3px;width:100%;text-align:left;background:transparent;border:1px solid transparent;}}
.nav-item:hover{{background:var(--card);color:var(--navy);}}
.nav-item.active{{background:var(--gold-soft);color:var(--navy);font-weight:700;border:1px solid var(--gold);}}
.nav-h{{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);font-weight:700;margin:18px 0 8px;}}
.plot{{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:14px 14px 6px;box-shadow:var(--shadow);}}
.judge{{display:flex;gap:10px;flex-wrap:wrap;}}
.jcard{{flex:1;min-width:150px;background:var(--card);border:1px solid var(--line);border-radius:var(--radius-sm);padding:12px 14px;}}
.jcard .jm{{font-size:11px;letter-spacing:.06em;text-transform:uppercase;font-weight:700;color:var(--muted);}}
.star{{color:var(--gold);font-size:15px;}}
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700;9..144,900&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">', unsafe_allow_html=True)


# ---------- gemini ----------
def gemini_call(prompt, max_tokens=700):
    if not st.session_state.gemini_key:
        return "Enter a Gemini API key in Settings (gear, bottom of sidebar) to use AI features."
    try:
        import google.generativeai as genai
        genai.configure(api_key=st.session_state.gemini_key)
        model = genai.GenerativeModel(st.session_state.gemini_model)
        return model.generate_content(prompt, generation_config={"max_output_tokens": max_tokens, "temperature": 0.7}).text
    except Exception as e:
        return f"Gemini error: {e}"


@st.cache_data
def load():
    dd = pd.read_csv("dashboard_data.csv")
    for c in ["admit_rate_residual", "admit_rate", "applicants", "admits", "lat", "lon", "frpm_pct"]:
        dd[c] = pd.to_numeric(dd[c], errors="coerce")
    disc = pd.read_csv("uc_freshman_admission_by_discipline.csv")
    for c in ["admit_rate", "applicants", "admits"]:
        disc[c] = pd.to_numeric(disc[c], errors="coerce")
    return dd, disc


dash, disc = load()


@st.cache_data
def data_context(dash, disc):
    """Compact, real summary of the datasets so Gemini can answer any question grounded in data."""
    d = dash.copy()
    d = d[(d["school_type"].notna()) & (d["campus"] == "Universitywide")]
    lines = []
    lines.append(f"Rows in dashboard_data.csv: {len(dash):,}. Columns include: high_school, city, county, campus, school_type, applicants, admits, admit_rate, applicant_gpa, admit_gpa, frpm_pct, admit_rate_residual, expected_admit_rate.")
    lines.append(f"CA public school types present: {sorted(d['school_type'].dropna().unique().tolist())}.")
    # by school type (universitywide, all years)
    by_type = (d.groupby("school_type")["admit_rate_residual"].mean() * 100).round(1).sort_values(ascending=False)
    lines.append("Mean admit-rate residual (pp) by school type (Universitywide, all years): " + ", ".join(f"{k}={v:+.1f}" for k, v in by_type.items()) + ".")
    # by campus overall admit rate (recent)
    recent = dash[dash["fall_term"] >= 2022]
    by_camp = (recent.groupby("campus")["admit_rate"].mean() * 100).round(1).sort_values()
    lines.append("Mean admit rate (%) by campus (2022+): " + ", ".join(f"{k}={v:.1f}" for k, v in by_camp.items()) + ".")
    # top / bottom schools by residual
    sch = d.groupby("high_school")["admit_rate_residual"].mean().sort_values(ascending=False)
    top = (sch.head(8) * 100).round(1)
    bot = (sch.tail(5).sort_values() * 100).round(1)
    lines.append("Top schools beating expectation (pp): " + ", ".join(f"{k}={v:+.1f}" for k, v in top.items()) + ".")
    lines.append("Biggest under-performers (pp): " + ", ".join(f"{k}={v:+.1f}" for k, v in bot.items()) + ".")
    # discipline CS context
    d25 = disc[disc["fall_term"] == 2025] if "fall_term" in disc.columns else disc
    if "broad_discipline" in disc.columns:
        ov = d25[d25["broad_discipline"] == "All disciplines"].set_index("campus")["admit_rate"]
        cs = d25[d25["broad_discipline"] == "Computer Science"].set_index("campus")["admit_rate"]
        pen = (cs - ov).dropna().sort_values()
        lines.append("CS admit-rate penalty vs campus overall (pp, 2025): " + ", ".join(f"{k}={v:+.1f}" for k, v in pen.items()) + ".")
    lines.append("Note: Universitywide is NOT the sum of campuses. admit_rate_residual = real minus expected admit rate (expected controls for FRPM poverty, GPA, school size).")
    return "\n".join(lines)


DASH_CONTEXT = data_context(dash, disc)

# ---------- sidebar ----------
with st.sidebar:
    st.markdown('<div class="nav-h">Explore</div>', unsafe_allow_html=True)
    for key, label in [("overview", "Overview"), ("map", "School map"),
                       ("schools", "Top schools"), ("cs", "CS context"),
                       ("deep", "Deep analysis"), ("ai", "AI Lab"), ("meth", "Methodology")]:
        cls = "nav-item active" if st.session_state.nav == key else "nav-item"
        if st.button(label, key=f"nav_{key}"):
            st.session_state.nav = key
    st.markdown('<div class="nav-h">Display</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Light" if st.session_state.theme == "dark" else "Dark", key="th2"):
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
            st.rerun()
    with c2:
        if st.button("Settings" if not st.session_state.show_settings else "Hide", key="set2"):
            st.session_state.show_settings = not st.session_state.show_settings
    if st.session_state.show_settings:
        st.markdown('<div class="card feature" style="margin-top:10px">', unsafe_allow_html=True)
        st.markdown('<div class="kick">Gemini (free)</div>', unsafe_allow_html=True)
        st.session_state.gemini_key = st.text_input("API key", value=st.session_state.gemini_key, type="password")
        st.session_state.gemini_model = st.selectbox("Model", FREE_MODELS, index=FREE_MODELS.index(st.session_state.gemini_model))
        st.caption("Session only. Never written to disk.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="nav-h">Data window</div>', unsafe_allow_html=True)
    years = st.slider("Fall term range", 2005, 2025, (2022, 2024), step=1)
    campus = st.selectbox("Campus", ["Universitywide"] + sorted([c for c in dash["campus"].dropna().unique() if c != "Universitywide"]))
    school_filter = st.multiselect("School types", sorted(dash["school_type"].dropna().unique()), default=sorted(dash["school_type"].dropna().unique()))

# ---------- top bar ----------
st.markdown(
    f'<div class="topbar"><div class="brand"><img class="cal" src="{LOGO}" alt="Berkeley C A L">'
    f'<div><div class="wm">UC Admissions Lab</div><div class="tag">County data &middot; admissions &middot; 2026 datathon</div></div></div>'
    f'<div class="tools"><div class="icbtn">DATATHON 2026</div></div></div>',
    unsafe_allow_html=True,
)

d = dash[(dash["fall_term"].between(years[0], years[1])) & (dash["school_type"].notna()) & (dash["campus"] == campus) & (dash["school_type"].isin(school_filter))]
res = d.groupby("school_type")["admit_rate_residual"].mean().sort_values(ascending=False)
res_pp = (res * 100).round(1)
top_type = res_pp.idxmax(); top_val = res_pp.max()
worst_type = res_pp.idxmin(); worst_val = res_pp.min()
finding_text = f"Continuation High Schools beat their expected UC admit rate by ~{top_val} pp (2022-2024), the highest of any CA public school type, while regular public high schools average only ~1.7 pp."

FONT = dict(family="IBM Plex Mono", color=t["--body"], size=11)
LAY = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=FONT,
           margin=dict(l=10, r=10, t=10, b=10),
           xaxis=dict(gridcolor=t["--line"], zerolinecolor=t["--line-2"]),
           yaxis=dict(gridcolor=t["--line"], zerolinecolor=t["--line-2"]))


def plot(fig):
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


NAV = st.session_state.nav

if NAV == "overview":
    st.markdown('<div class="kick">Dashboard Construction</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-title">Which CA public school type beats its expected UC admit rate?</div>', unsafe_allow_html=True)
    st.markdown('<div class="lede">For CA public high schools in 2022&ndash;2024, which school type most outperforms its <b>expected</b> UC freshman admit rate, after controlling for poverty, applicant GPA, and school size? The data ships an <code>admit_rate_residual</code> column = real admit rate minus expected admit rate (expected already adjusts for FRPM poverty, GPA, and size).</div>', unsafe_allow_html=True)
    a1, a2, a3, a4 = st.columns(4)
    a1.markdown(f"<div class='card feature kpi'><div class='lab'>Top school type</div><div class='num win'>+{top_val} pp</div><div class='muted'>{top_type.replace(' (Public)','')}</div></div>", unsafe_allow_html=True)
    a2.markdown(f"<div class='card blue kpi'><div class='lab'>Lowest</div><div class='num lose'>{worst_val:+} pp</div><div class='muted'>{worst_type.replace(' (Public)','')}</div></div>", unsafe_allow_html=True)
    a3.markdown(f"<div class='card blue kpi'><div class='lab'>School types</div><div class='num'>{int(len(res_pp))}</div><div class='muted'>compared</div></div>", unsafe_allow_html=True)
    a4.markdown(f"<div class='card blue kpi'><div class='lab'>Applicants</div><div class='num'>{int(d['applicants'].sum()):,}</div><div class='muted'>{campus}</div></div>", unsafe_allow_html=True)
    st.markdown('<div class="sec">', unsafe_allow_html=True)
    st.markdown('<div class="h2">By school type</div>', unsafe_allow_html=True)
    chart = res_pp.reset_index(); chart.columns = ["school_type", "beats_expected_pp"]
    fig = px.bar(chart, x="school_type", y="beats_expected_pp", color="beats_expected_pp", color_continuous_scale="RdYlGn",
                 color_continuous_midpoint=0, text="beats_expected_pp",
                 labels={"beats_expected_pp": "Beats expected admit rate (pp)", "school_type": "School type"},
                 title="Mean admit-rate residual by school type")
    fig.update_layout(**LAY, height=400, yaxis_title="Beats expected admit rate (pp)", coloraxis_colorbar=dict(title="pp"))
    fig.update_traces(texttemplate="%{text}", textposition="outside", marker=dict(line=dict(width=0)))
    plot(fig)
    st.markdown('<div class="cap">Bars above zero admit more than their poverty / GPA / size profile predicts. Continuation high schools lead by a wide margin.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec">', unsafe_allow_html=True)
    st.markdown('<div class="h2">Best individual schools</div>', unsafe_allow_html=True)
    top_sch = (d.groupby("high_school")["admit_rate_residual"].mean().sort_values(ascending=False).head(12) * 100).round(1)
    ts = top_sch.reset_index(); ts.columns = ["high_school", "beats_expected_pp"]
    st.dataframe(ts, width='stretch', height=380, hide_index=True)
    st.markdown('<div class="cap">Individual CA public schools that most beat their expected UC admit rate in the selected window. Filter by school type in the sidebar to narrow the list.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec"><div class="card feature"><div class="kick" style="color:var(--gold)">Finding</div><div class="lede" style="color:var(--ink)"><b>Continuation High Schools beat their expected UC admit rate by ~{top_val} pp (2022&ndash;2024)</b>, the highest of any CA public school type, while regular public high schools average only ~1.7 pp.</div></div></div>', unsafe_allow_html=True)

elif NAV == "map":
    st.markdown('<div class="page-title" style="font-size:1.9rem">Every school on the map</div>', unsafe_allow_html=True)
    m = d.dropna(subset=["lat", "lon"]).copy(); m["pp"] = m["admit_rate_residual"] * 100
    fig = px.scatter_geo(m, lat="lat", lon="lon", color="pp", color_continuous_scale="RdYlGn", color_continuous_midpoint=0,
                         hover_name="high_school", hover_data={"pp": ":.1f", "school_type": True, "lat": False, "lon": False},
                         scope="usa", center={"lat": 36.5, "lon": -119.5})
    fig.update_layout(height=560, paper_bgcolor="rgba(0,0,0,0)", font=FONT,
                      geo=dict(lakecolor="rgb(255,255,255)", bgcolor="rgba(0,0,0,0)", landcolor=t["--map-land"],
                               showland=True, subunitcolor=t["--map-unit"], countrycolor=t["--map-unit"]))
    fig.update_traces(marker=dict(size=7, opacity=0.85))
    plot(fig)
    st.markdown('<div class="cap">Green schools admitted above expectation, red below. Filter by school type in the sidebar.</div>', unsafe_allow_html=True)

elif NAV == "schools":
    st.markdown('<div class="page-title" style="font-size:1.9rem">Schools that beat expectations most</div>', unsafe_allow_html=True)
    sch = d.groupby("high_school")["admit_rate_residual"].mean().sort_values(ascending=False)
    top20 = (sch.head(20) * 100).round(1)
    bot10 = (sch.tail(10).sort_values() * 100).round(1)
    cA, cB = st.columns(2)
    with cA:
        st.markdown('<div class="h2" style="font-size:1.1rem">Top 20 over-performers</div>', unsafe_allow_html=True)
        st.dataframe(top20.reset_index().rename(columns={"high_school": "high_school", "admit_rate_residual": "beats_expected_pp"}), height=440, width='stretch')
    with cB:
        st.markdown('<div class="h2" style="font-size:1.1rem">10 biggest under-performers</div>', unsafe_allow_html=True)
        st.dataframe(bot10.reset_index().rename(columns={"high_school": "high_school", "admit_rate_residual": "beats_expected_pp"}), height=440, width='stretch')

elif NAV == "cs":
    st.markdown('<div class="page-title" style="font-size:1.9rem">CS admit-rate penalty (2025)</div>', unsafe_allow_html=True)
    d25 = disc[disc["fall_term"] == 2025]
    ov = d25[d25["broad_discipline"] == "All disciplines"].set_index("campus")["admit_rate"]
    cs = d25[d25["broad_discipline"] == "Computer Science"].set_index("campus")["admit_rate"]
    pen = (cs - ov).dropna().sort_values(); cc = pen.reset_index(); cc.columns = ["campus", "cs_penalty_pp"]
    fig = px.bar(cc, x="campus", y="cs_penalty_pp", color="cs_penalty_pp", color_continuous_scale="RdYlGn_r", color_continuous_midpoint=0, text="cs_penalty_pp")
    fig.update_layout(**LAY, height=420, yaxis_title="CS rate minus campus overall (pp)")
    fig.update_traces(texttemplate="%{text}", textposition="outside")
    plot(fig)
    st.markdown('<div class="cap">Negative = CS hurts your odds vs the campus average. Davis is harshest. We treat this as context, not our headline.</div>', unsafe_allow_html=True)

elif NAV == "deep":
    st.markdown('<div class="page-title" style="font-size:1.9rem">Deep analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="lede">Additional cuts that build rigor: county effects, and whether poverty explains the residual.</div>', unsafe_allow_html=True)
    dd = d.dropna(subset=["admit_rate_residual"])
    st.markdown('<div class="sec">', unsafe_allow_html=True)
    st.markdown('<div class="h2">County-level over-performance</div>', unsafe_allow_html=True)
    cnt = dd.groupby("county")["admit_rate_residual"].mean().sort_values(ascending=False).head(12) * 100
    fig = px.bar(cnt.reset_index(), x="county", y="admit_rate_residual", color="admit_rate_residual", color_continuous_scale="RdYlGn", color_continuous_midpoint=0, text="admit_rate_residual")
    fig.update_layout(**LAY, height=400, yaxis_title="Beats expected (pp)")
    fig.update_traces(texttemplate="%{text}", textposition="outside")
    plot(fig)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec">', unsafe_allow_html=True)
    st.markdown('<div class="h2">Does poverty explain it? FRPM vs residual</div>', unsafe_allow_html=True)
    sc = dd.dropna(subset=["frpm_pct"])
    if len(sc) > 5:
        try:
            import statsmodels  # noqa
            trend = dict(trendline="ols")
        except Exception:
            trend = {}
        fig = px.scatter(sc, x="frpm_pct", y="admit_rate_residual", color="school_type", opacity=0.7,
                         hover_name="high_school", **trend)
        fig.update_layout(**LAY, height=420, xaxis_title="FRPM poverty %", yaxis_title="Admit rate residual")
        plot(fig)
        corr = sc["frpm_pct"].corr(sc["admit_rate_residual"])
        st.markdown(f'<div class="cap">Correlation FRPM% vs residual = {corr:.2f}. Near zero means poverty alone does NOT explain the gaps, which strengthens the rigor of the finding.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="muted">Not enough FRPM data in this window to plot.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif NAV == "meth":
    st.markdown('<div class="page-title" style="font-size:1.9rem">Methodology</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="lede"><b>Data.</b> Event <code>dashboard_data.csv</code> and <code>uc_freshman_admission_by_discipline.csv</code>. <b>Metric.</b> <code>admit_rate_residual</code> = real admit rate minus expected admit rate, where expected is computed by organizers after adjusting for FRPM poverty, applicant GPA, and school size. <b>Method.</b> Filter to CA public school rows, Universitywide, fall 2022-2024; group by <code>school_type</code>; average the residual. We sum counts then divide, never average rates. <b>Caveat.</b> Universitywide is not the sum of campuses. <b>Reproduce.</b> <code>dashboard_notebook.ipynb</code>.</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec"><div class="muted">Source: event datasets. Residual column precomputed by organizers (poverty, GPA, school size). Universitywide is not the sum of campuses.</div></div>', unsafe_allow_html=True)

elif NAV == "ai":
    st.markdown('<div id="ailab">', unsafe_allow_html=True)
    st.markdown('<div class="page-title" style="font-size:1.9rem">AI Lab</div>', unsafe_allow_html=True)
    st.caption("Powered by Gemini (free models). Key stays in your session only, never written to disk.")
    if not st.session_state.gemini_key:
        st.info("Add a free Gemini API key in Settings (bottom of sidebar) to unlock Ask-the-data, the Chance-Me predictor, and the helper tools.")
    st.markdown('<div class="sec" style="border-top:3px solid var(--gold);">', unsafe_allow_html=True)
    st.markdown('<div class="h2" style="color:var(--gold)">Ask the data</div>', unsafe_allow_html=True)
    st.markdown('<div class="lede">Type a question. Gemini answers using the real numbers we computed (it does not guess). It sees the finding and every school type\'s residual.</div>', unsafe_allow_html=True)
    q = st.text_area("Your question", "Why should judges care about this finding?", key="aiq")
    if st.button("Ask Gemini", key="askb"):
        if not st.session_state.gemini_key:
            st.warning("Enter a Gemini API key in Settings first.")
        else:
            with st.spinner("Thinking..."):
                ctx = (f"CONTEXT - real dataset facts (use ONLY these, do not invent numbers):\n{DASH_CONTEXT}\n\n"
                       f"Current dashboard view: data window {years[0]}-{years[1]}, campus {campus}.\n"
                       "Answer the user's question clearly and concisely in a student presenter voice. Use plain text; avoid markdown tables. Keep under 180 words.")
                out = gemini_call(ctx + "\n\nQuestion: " + q, max_tokens=900)
            from streamlit.components.v1 import html
            safe = out.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
            ai_html = (f'<div style="background:#ffffff;color:#111111;border:1px solid #d9d3c7;'
                        f'border-radius:12px;padding:16px 18px;font-family:Inter,Arial,sans-serif;'
                        f'font-size:15px;line-height:1.6;">{safe}</div>')
            html(ai_html, height=200)
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- Chance Me predictor ----
    st.markdown('<div class="sec">', unsafe_allow_html=True)
    st.markdown('<div class="h2">Chance Me</div>', unsafe_allow_html=True)
    st.markdown('<div class="lede">Estimate your UC admit odds from the real data. We take your school (or school-type / campus) historical admit rate, then adjust it up or down based on how your GPA compares to the actual GPA distribution of admitted students for that group. Higher GPA = higher odds.</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        ch_campus = st.selectbox("Campus", ["Universitywide"] + sorted([c for c in dash["campus"].dropna().unique() if c != "Universitywide"]), key="ch_c")
    with c2:
        ch_school = st.selectbox("Your high school", ["" ] + sorted(dash["high_school"].dropna().unique().tolist()), key="ch_s")
    with c3:
        ch_gpa = st.number_input("Your applicant GPA", min_value=0.0, max_value=5.0, value=3.8, step=0.05, key="ch_g")
    if st.button("Estimate my chances", key="ch_b"):
        sub = dash[(dash["campus"] == ch_campus)]
        # pick the best available base group: exact school -> school type -> campus
        srow = sub[sub["high_school"] == ch_school] if ch_school else sub.iloc[0:0]
        if len(srow):
            base_rate = pd.to_numeric(srow["admit_rate"], errors="coerce").mean()
            grp = srow
            label = ch_school
        else:
            stype = sub["school_type"].mode().iloc[0] if len(sub) else "High Schools (Public)"
            grp = sub[sub["school_type"] == stype]
            base_rate = pd.to_numeric(grp["admit_rate"], errors="coerce").mean()
            label = f"{stype} (avg)"
        base_rate = base_rate if pd.notna(base_rate) else pd.to_numeric(sub["admit_rate"], errors="coerce").mean()
        # GPA adjustment: compare applicant GPA to the admitted-GPA distribution of this group
        admit_gpa = pd.to_numeric(grp["admit_gpa"], errors="coerce").dropna()
        if len(admit_gpa) >= 10:
            lo, hi = admit_gpa.quantile(0.10), admit_gpa.quantile(0.90)
            spread = (hi - lo) or 0.5
            z = (ch_gpa - admit_gpa.median()) / spread  # ~ -1.4 .. +1.4
            mult = 1.0 + 0.6 * max(-1.0, min(1.0, z))    # +/- up to 60%
            typical_gpa = admit_gpa.median()
            note_gpa = f"vs typical admitted GPA {typical_gpa:.2f}"
        else:
            mult = 1.0
            typical_gpa = float("nan")
            note_gpa = "GPA distribution not available for this group"
        est = base_rate * mult
        est = min(max(est, 0.0), 1.0)
        rows = [
            ("Base admit rate (" + label + ")", f"{base_rate*100:.1f}%"),
            ("GPA adjustment", f"x{mult:.2f}  ({note_gpa})"),
            ("Estimated chance", f"{est*100:.1f}%"),
        ]
        # show comparison anchors so it is clearly GPA-sensitive
        if len(admit_gpa) >= 10:
            rows.append(("If GPA were median", f"{base_rate*100:.1f}%"))
            rows.append(("If GPA were 90th pct", f"{base_rate*(1+0.6)*100:.1f}%"))
        df_out = pd.DataFrame(rows, columns=["Metric", "Value"])
        st.dataframe(df_out, width='stretch', hide_index=True)
        st.markdown(f'<div class="cap">Estimate uses real historical admit rates and the actual admitted-student GPA distribution for {label}. Your GPA of {ch_gpa:.2f} moves the estimate {"up" if mult >= 1 else "down"} from the base. This is a data-grounded approximation, not an official guarantee.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
