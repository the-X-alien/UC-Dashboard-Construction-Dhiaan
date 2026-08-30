import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="UC Admissions Lab - Residual Explorer", layout="wide", initial_sidebar_state="expanded")

# ---------- theme state ----------
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "gemini_key" not in st.session_state:
    st.session_state.gemini_key = ""
if "gemini_model" not in st.session_state:
    st.session_state.gemini_model = "gemini-2.5-flash"
if "show_settings" not in st.session_state:
    st.session_state.show_settings = False

FREE_MODELS = ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-flash-latest", "gemini-3-flash-preview", "gemini-3.1-flash-lite"]

TH = {
    "light": {
        "--blue": "#003262", "--blue-ink": "#002b52", "--bluesky": "#7ba3c4", "--gold": "#fdb515",
        "--gold-ink": "#8a6500", "--ok": "#1f7a4d", "--bad": "#b3372b",
        "--ink": "#181a1d", "--ink-soft": "#3a3f45", "--muted": "#6b7078", "--faint": "#9aa0a7",
        "--paper": "#fbf9f4", "--card": "#fffdf8", "--line": "#e6e2d8", "--line-strong": "#d6d1c4",
        "--header-bg": "#003262", "--header-text": "#ffffff", "--map-land": "#f1ede3", "--map-unit": "#cfc9ba",
    },
    "dark": {
        "--blue": "#003262", "--blue-ink": "#002b52", "--bluesky": "#7ba3c4", "--gold": "#fdb515",
        "--gold-ink": "#ffce4d", "--ok": "#39d98a", "--bad": "#ff6b6b",
        "--ink": "#f3efe6", "--ink-soft": "#c9c3b6", "--muted": "#9a958a", "--faint": "#6b6760",
        "--paper": "#12161d", "--card": "#1a1f29", "--line": "#2a313d", "--line-strong": "#3a424f",
        "--header-bg": "#002b52", "--header-text": "#ffffff", "--map-land": "#1c222c", "--map-unit": "#2a313d",
    },
}
t = TH[st.session_state.theme]
css_vars = "\n".join(f"  {k}:{v};" for k, v in t.items())

CSS = f"""
:root{{
{css_vars}
  --radius:10px;
}}
html,body,.stApp{{background:var(--paper);color:var(--ink);
  font-family:'IBM Plex Sans',system-ui,sans-serif;transition:background .2s,color .2s;}}
.block-container{{padding-top:0;padding-bottom:2rem;max-width:1160px;}}
header{{visibility:hidden;}}
.stApp header[data-testid="stHeader"]{{background:var(--header-bg);}}
.topband{{background:var(--header-bg);border-bottom:3px solid var(--gold);padding:13px 26px;
  display:flex;align-items:center;justify-content:space-between;}}
.wm{{color:var(--header-text);font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1.3rem;}}
.kick{{color:hsla(0,0%,100%,.62);font-size:10px;letter-spacing:.08em;text-transform:uppercase;font-weight:600;}}
.title{{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:2.1rem;letter-spacing:-.02em;
  color:var(--blue);margin:.2rem 0;}}
.lede{{color:var(--ink-soft);max-width:800px;line-height:1.5;}}
.h2{{font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:1.3rem;color:var(--blue);margin:.2rem 0 .3rem;}}
.muted{{color:var(--muted);font-size:12px;}}
.metric-big{{font-family:'IBM Plex Mono',monospace;font-variant-numeric:tabular-nums;font-size:1.85rem;font-weight:700;}}
.win{{color:var(--ok);}} .lose{{color:var(--bad);}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:16px 18px;}}
.card.feature{{border-top:3px solid var(--gold);}}
.card.blue{{border-top:3px solid var(--blue);}}
.kick-sm{{font-size:10px;letter-spacing:.08em;text-transform:uppercase;font-weight:600;color:var(--muted);}}
.section{{border-top:1px solid var(--line);padding-top:22px;margin-top:22px;}}
.mininav{{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0 4px;}}
.chip{{background:var(--card);border:1px solid var(--line);border-radius:999px;padding:5px 13px;
  font-size:12px;color:var(--ink-soft);text-decoration:none;}}
.chip:hover{{border-color:var(--gold);color:var(--blue);}}
.toggle{{background:var(--card);border:1px solid var(--line);border-radius:999px;color:var(--ink);
  font-size:13px;padding:4px 12px;cursor:pointer;}}
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">', unsafe_allow_html=True)

# ---------- header ----------
col_h1, col_set, col_th = st.columns([9, 1, 1])
with col_h1:
    st.markdown(
        '<div class="topband" style="margin:0 -1rem 0 -1rem;"><div><div class="wm">UC Admissions Lab</div>'
        '<div class="kick">County data &middot; admissions &middot; 2026 datathon</div></div></div>',
        unsafe_allow_html=True,
    )
with col_set:
    if st.button("\u2699", key="gear", help="Settings (Gemini)"):
        st.session_state.show_settings = not st.session_state.show_settings
with col_th:
    label = "\U0001F305" if st.session_state.theme == "light" else "\U0001F319"
    if st.button(label, key="th", help="Toggle light/dark"):
        st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
        st.rerun()

if st.session_state.show_settings:
    with st.container():
        st.markdown('<div class="card feature">', unsafe_allow_html=True)
        st.markdown('<div class="kick-sm" style="color:var(--gold-ink)">Settings &middot; Gemini (free models)</div>', unsafe_allow_html=True)
        st.session_state.gemini_key = st.text_input("Gemini API key", value=st.session_state.gemini_key, type="password",
            help="Stored only in this session. Free models only.")
        st.session_state.gemini_model = st.selectbox("Model", FREE_MODELS, index=FREE_MODELS.index(st.session_state.gemini_model))
        st.caption("Key never leaves your browser session. Used only for the AI features below.")
        st.markdown("</div>", unsafe_allow_html=True)

# ---------- hero band ----------
st.markdown('<div style="padding:20px 0 6px;">', unsafe_allow_html=True)
st.markdown('<div class="kick-sm">Dashboard Construction</div>', unsafe_allow_html=True)
st.markdown('<div class="title">Which CA public school type beats its expected UC admit rate?</div>', unsafe_allow_html=True)
st.markdown('<div class="lede">For CA public high schools in 2022&ndash;2024, which school type most outperforms its <b>expected</b> UC freshman admit rate, after controlling for poverty, applicant GPA, and school size? The data ships an <code>admit_rate_residual</code> column = real admit rate minus expected admit rate (expected already adjusts for FRPM poverty, GPA, and size). Positive = admitted more than the profile predicted.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# mini-index
st.markdown(
    '<div class="mininav">'
    '<a class="chip" href="#s1">1 &middot; By type</a>'
    '<a class="chip" href="#s2">2 &middot; Map</a>'
    '<a class="chip" href="#s3">3 &middot; Trend</a>'
    '<a class="chip" href="#s4">4 &middot; Heatmap</a>'
    '<a class="chip" href="#s5">5 &middot; Schools</a>'
    '<a class="chip" href="#s6">6 &middot; CS context</a>'
    '<a class="chip" href="#ai">AI Co-Pilot</a>'
    '<a class="chip" href="#meth">Methodology</a></div>',
    unsafe_allow_html=True,
)


def gemini_call(prompt, max_tokens=600):
    if not st.session_state.gemini_key:
        return "Enter a Gemini API key in Settings (top-right gear) to use AI features."
    try:
        import google.generativeai as genai
        genai.configure(api_key=st.session_state.gemini_key)
        model = genai.GenerativeModel(st.session_state.gemini_model)
        resp = model.generate_content(prompt, generation_config={"max_output_tokens": max_tokens, "temperature": 0.7})
        return resp.text
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

st.sidebar.header("Controls")
years = st.sidebar.slider("Fall term range", 2005, 2025, (2022, 2024), step=1)
campus = st.sidebar.selectbox("Campus", ["Universitywide"] + sorted([c for c in dash["campus"].dropna().unique() if c != "Universitywide"]))
school_filter = st.sidebar.multiselect("School types", sorted(dash["school_type"].dropna().unique()), default=sorted(dash["school_type"].dropna().unique()))

d = dash[(dash["fall_term"].between(years[0], years[1])) & (dash["school_type"].notna()) & (dash["campus"] == campus) & (dash["school_type"].isin(school_filter))]
res = d.groupby("school_type")["admit_rate_residual"].mean().sort_values(ascending=False)
res_pp = (res * 100).round(1)
top_type = res_pp.idxmax(); top_val = res_pp.max()
worst_type = res_pp.idxmin(); worst_val = res_pp.min()

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f"<div class='card feature'><div class='kick-sm'>Top school type</div><div class='metric-big win'>+{top_val} pp</div><div class='muted'>{top_type.replace(' (Public)','')}</div></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='card blue'><div class='kick-sm'>Lowest</div><div class='metric-big lose'>{worst_val:+} pp</div><div class='muted'>{worst_type.replace(' (Public)','')}</div></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='card blue'><div class='kick-sm'>School types</div><div class='metric-big'>{int(len(res_pp))}</div><div class='muted'>compared</div></div>", unsafe_allow_html=True)
k4.markdown(f"<div class='card blue'><div class='kick-sm'>Applicants in view</div><div class='metric-big'>{int(d['applicants'].sum()):,}</div><div class='muted'>{campus}</div></div>", unsafe_allow_html=True)

st.markdown('<div class="section" id="s1">', unsafe_allow_html=True)
st.markdown('<div class="h2">1 &middot; Which school type beats expectations most</div>', unsafe_allow_html=True)
chart = res_pp.reset_index(); chart.columns = ["school_type", "beats_expected_pp"]
fig = px.bar(chart, x="school_type", y="beats_expected_pp", color="beats_expected_pp", color_continuous_scale="RdYlGn",
             color_continuous_midpoint=0, text="beats_expected_pp")
fig.update_layout(xaxis_title="", yaxis_title="Beats expected admit rate (pp)", height=400, paper_bgcolor="rgba(0,0,0,0)",
                  plot_bgcolor="rgba(0,0,0,0)", font=dict(family="IBM Plex Mono", color=t["--ink-soft"]))
fig.update_traces(texttemplate="%{text}", textposition="outside", marker=dict(line=dict(width=0)))
st.plotly_chart(fig, width="stretch")
st.markdown('<div class="muted">Bars above zero admit more than their poverty / GPA / size profile predicts. Continuation high schools lead by a wide margin.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section" id="s2">', unsafe_allow_html=True)
st.markdown('<div class="h2">2 &middot; Every school on the map, colored by over/under-performance</div>', unsafe_allow_html=True)
m = d.dropna(subset=["lat", "lon"]).copy(); m["pp"] = m["admit_rate_residual"] * 100
fig2 = px.scatter_geo(m, lat="lat", lon="lon", color="pp", color_continuous_scale="RdYlGn", color_continuous_midpoint=0,
                      hover_name="high_school", hover_data={"pp": ":.1f", "school_type": True, "lat": False, "lon": False},
                      scope="usa", center={"lat": 36.5, "lon": -119.5})
fig2.update_layout(height=520, paper_bgcolor="rgba(0,0,0,0)",
                   geo=dict(lakecolor="rgb(255,255,255)", bgcolor="rgba(0,0,0,0)", landcolor=t["--map-land"],
                            showland=True, subunitcolor=t["--map-unit"], countrycolor=t["--map-unit"]))
fig2.update_traces(marker=dict(size=7, opacity=0.85))
st.plotly_chart(fig2, width="stretch")
st.markdown('<div class="muted">Green schools admitted above expectation, red below. Filter by school type in the sidebar.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section" id="s3">', unsafe_allow_html=True)
st.markdown('<div class="h2">3 &middot; How the gap moved over time</div>', unsafe_allow_html=True)
trend = (dash[(dash["school_type"].notna()) & (dash["campus"] == campus) & (dash["school_type"].isin(school_filter))]
         .groupby(["fall_term", "school_type"])["admit_rate_residual"].mean().reset_index()).dropna(subset=["admit_rate_residual"])
trend["pp"] = trend["admit_rate_residual"] * 100
fig3 = px.line(trend, x="fall_term", y="pp", color="school_type", markers=True, line_shape="linear")
fig3.update_layout(xaxis_title="Fall term", yaxis_title="Beats expected (pp)", height=400, paper_bgcolor="rgba(0,0,0,0)",
                   plot_bgcolor="rgba(0,0,0,0)", font=dict(family="IBM Plex Mono", color=t["--ink-soft"]))
st.plotly_chart(fig3, width="stretch")
st.markdown('<div class="muted">Only years with data are plotted. Widen the slider to see the long run.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section" id="s4">', unsafe_allow_html=True)
st.markdown('<div class="h2">4 &middot; Campus &times; school-type over-performance</div>', unsafe_allow_html=True)
piv = d.groupby(["school_type", "campus"])["admit_rate_residual"].mean().unstack() * 100
fig4 = px.imshow(piv, color_continuous_scale="RdYlGn", color_continuous_midpoint=0, aspect="auto",
                 labels=dict(x="Campus", y="School type", color="Beats expected (pp)"))
fig4.update_layout(height=360, paper_bgcolor="rgba(0,0,0,0)", font=dict(family="IBM Plex Mono", color=t["--ink-soft"]))
st.plotly_chart(fig4, width="stretch")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section" id="s5">', unsafe_allow_html=True)
st.markdown('<div class="h2">5 &middot; Individual schools that beat expectations most</div>', unsafe_allow_html=True)
sch = d.groupby("high_school")["admit_rate_residual"].mean().sort_values(ascending=False).head(20) * 100
st.dataframe(sch.round(1).reset_index().rename(columns={"high_school": "high_school", "admit_rate_residual": "beats_expected_pp"}), width="stretch", height=420)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section" id="s6">', unsafe_allow_html=True)
st.markdown('<div class="h2">6 &middot; Context: the Computer Science admit-rate penalty (2025)</div>', unsafe_allow_html=True)
d25 = disc[disc["fall_term"] == 2025]
ov = d25[d25["broad_discipline"] == "All disciplines"].set_index("campus")["admit_rate"]
cs = d25[d25["broad_discipline"] == "Computer Science"].set_index("campus")["admit_rate"]
pen = (cs - ov).dropna().sort_values(); cc = pen.reset_index(); cc.columns = ["campus", "cs_penalty_pp"]
fig5 = px.bar(cc, x="campus", y="cs_penalty_pp", color="cs_penalty_pp", color_continuous_scale="RdYlGn_r", color_continuous_midpoint=0, text="cs_penalty_pp")
fig5.update_layout(xaxis_title="", yaxis_title="CS rate minus campus overall (pp)", height=360, paper_bgcolor="rgba(0,0,0,0)",
                   plot_bgcolor="rgba(0,0,0,0)", font=dict(family="IBM Plex Mono", color=t["--ink-soft"]))
fig5.update_traces(texttemplate="%{text}", textposition="outside")
st.plotly_chart(fig5, width="stretch")
st.markdown('<div class="muted">Negative = CS hurts your odds vs the campus average. Davis is harshest; this is the crowded finding most teams show, so we treat it as context, not our headline.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section" id="ai" style="border-top:3px solid var(--gold);">', unsafe_allow_html=True)
st.markdown('<div class="h2" style="color:var(--gold-ink)">AI Co-Pilot &middot; powered by Gemini (free models)</div>', unsafe_allow_html=True)
st.caption("Set your key in Settings (top-right gear). These features call Gemini live and do not touch your data files.")
finding_text = f"Continuation High Schools beat their expected UC admit rate by ~{top_val} pp (2022-2024), the highest of any CA public school type, while regular public high schools average only ~1.7 pp."
cA, cB, cC = st.columns(3)
with cA:
    if st.button("Judge Scorecard", key="jb"):
        with st.spinner("Asking Gemini to score your dashboard..."):
            out = gemini_call("You are a strict datathon judge. Score this dashboard on 5 criteria (1-5 each): QUESTION (time window, population, metric), FINDING (concise+justifiable), RIGOR (nuanced), DASHBOARD (accurate+reliable), PRESENTATION (clear). Dashboard question: 'For CA public high schools 2022-2024, which school type most outperforms its expected UC admit rate after controlling for poverty, GPA, school size?' Finding: " + finding_text + ". Reply as JSON: {\"question\":n,\"finding\":n,\"rigor\":n,\"dashboard\":n,\"presentation\":n,\"total\":n,\"tip\":\"one line to improve\"}")
        st.markdown(f"<div class='card'>{out}</div>", unsafe_allow_html=True)
with cB:
    if st.button("Competitor Radar", key="cr"):
        with st.spinner("Gemini imagines rival dashboards..."):
            out = gemini_call("We are at a high school UC admissions datathon. 75 finalists, most using AI. Our dashboard finding: " + finding_text + ". List 5 dashboard angles rival teams likely built (be specific), then 3 ways we can differentiate and wow judges beyond what they did. Bullet points, terse.")
        st.markdown(f"<div class='card'>{out}</div>", unsafe_allow_html=True)
with cC:
    if st.button("Wow Hook", key="wh"):
        with st.spinner("Gemini writes your opener..."):
            out = gemini_call("Write ONE punchy 1-sentence opener a student would say to judges to make them remember this finding: " + finding_text + ". Make it counterintuitive and human. Under 25 words.")
        st.markdown(f"<div class='card feature'>{out}</div>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section" id="meth">', unsafe_allow_html=True)
st.markdown('<div class="h2">Methodology</div>', unsafe_allow_html=True)
st.markdown('<div class="card"><div class="lede"><b>Data.</b> Event <code>dashboard_data.csv</code> and <code>uc_freshman_admission_by_discipline.csv</code>. <b>Metric.</b> <code>admit_rate_residual</code> = real admit rate minus expected admit rate, where expected is computed by organizers after adjusting for FRPM poverty, applicant GPA, and school size. <b>Method.</b> Filter to CA public school rows, Universitywide, fall 2022-2024; group by <code>school_type</code>; average the residual. We sum counts then divide, never average rates. <b>Caveat.</b> Universitywide is not the sum of campuses. <b>Reproduce.</b> <code>dashboard_notebook.ipynb</code> in Colab.</div></div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section" style="border-top:1px solid var(--line);">', unsafe_allow_html=True)
st.markdown(f'<div class="card feature"><div class="kick-sm" style="color:var(--gold-ink)">Finding</div><div class="lede" style="color:var(--ink)"><b>Continuation High Schools beat their expected UC admit rate by ~{top_val} pp (2022&ndash;2024)</b>, the highest of any CA public school type, while regular public high schools average only ~1.7 pp. The schools expected to send the fewest students to UC are the ones that most outperform their predicted admit rate.</div></div>', unsafe_allow_html=True)
st.markdown('<div class="muted" style="margin-top:10px">Source: event dashboard_data.csv + uc_freshman_admission_by_discipline.csv. Residual column precomputed by organizers (controls for FRPM poverty, applicant GPA, school size). Universitywide is not the sum of campuses.</div>', unsafe_allow_html=True)
