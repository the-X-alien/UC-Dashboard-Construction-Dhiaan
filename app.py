import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="UC Admissions Lab - Residual Explorer", layout="wide")

# ---------- design tokens (UC Admissions Lab brand) ----------
CSS = """
:root{
  --blue:#003262; --blue-ink:#002b52; --bluesky:#7ba3c4; --gold:#fdb515; --gold-ink:#8a6500;
  --ok:#1f7a4d; --bad:#b3372b;
  --ink:#181a1d; --ink-soft:#3a3f45; --muted:#6b7078; --faint:#9aa0a7;
  --paper:#fbf9f4; --card:#fffdf8; --line:#e6e2d8; --line-strong:#d6d1c4;
  --radius:10px;
}
html,body,.stApp{{background:var(--paper);color:var(--ink);
  font-family:'IBM Plex Sans',system-ui,sans-serif;}}
.block-container{{padding-top:0;padding-bottom:2rem;max-width:1160px;}}
header{{visibility:hidden;}}
.stApp header[data-testid="stHeader"]{{background:var(--blue);}}
.topband{{background:var(--blue);border-bottom:3px solid var(--gold);padding:14px 26px;
  display:flex;align-items:center;gap:14px;}}
.topband .wm{{color:#fff;font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:1.25rem;}}
.topband .kick{{color:hsla(0,0%,100%,.6);font-size:10px;letter-spacing:.08em;
  text-transform:uppercase;font-weight:600;}}
.title{{font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:2.1rem;
  letter-spacing:-.02em;color:var(--blue);margin:.2rem 0;}}
.lede{{color:var(--ink-soft);max-width:760px;line-height:1.5;}}
.h2{{font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:1.35rem;color:var(--blue);
  margin:.2rem 0 .3rem;}}
.muted{{color:var(--muted);font-size:12px;}}
.metric-big{{font-family:'IBM Plex Mono',monospace;font-variant-numeric:tabular-nums;
  font-size:1.9rem;font-weight:700;}}
.win{{color:var(--ok);}} .lose{{color:var(--bad);}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);
  padding:16px 18px;}}
.card.feature{{border-top:3px solid var(--gold);}}
.card.blue{{border-top:3px solid var(--blue);}}
.kick-sm{{font-size:10px;letter-spacing:.08em;text-transform:uppercase;font-weight:600;
  color:var(--muted);}}
.section{{border-top:1px solid var(--line);padding-top:22px;margin-top:22px;}}
"""
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
st.markdown(
    '<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">',
    unsafe_allow_html=True,
)

# ---------- header ----------
st.markdown(
    '<div class="topband"><div><div class="wm">UC Admissions Lab</div>'
    '<div class="kick">County data &middot; admissions &middot; 2026 datathon</div></div></div>',
    unsafe_allow_html=True,
)

# ---------- hero band ----------
st.markdown('<div style="padding:22px 0 8px;">', unsafe_allow_html=True)
st.markdown('<div class="kick-sm">Dashboard Construction</div>', unsafe_allow_html=True)
st.markdown('<div class="title">Which CA public school type beats its expected UC admit rate?</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="lede">For CA public high schools in 2022&ndash;2024, which school type most outperforms its '
    '<b>expected</b> UC freshman admit rate, after controlling for poverty, applicant GPA, and school size? '
    'The data ships an <code>admit_rate_residual</code> column = real admit rate minus expected admit rate '
    '(expected already adjusts for FRPM poverty, GPA, and size). Positive = admitted more than the profile predicted.</div>',
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)

# ---------- load ----------
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
campus = st.sidebar.selectbox(
    "Campus",
    ["Universitywide"] + sorted([c for c in dash["campus"].dropna().unique() if c != "Universitywide"]),
)
school_filter = st.sidebar.multiselect(
    "School types", sorted(dash["school_type"].dropna().unique()),
    default=sorted(dash["school_type"].dropna().unique()),
)

d = dash[
    (dash["fall_term"].between(years[0], years[1]))
    & (dash["school_type"].notna())
    & (dash["campus"] == campus)
    & (dash["school_type"].isin(school_filter))
]
res = d.groupby("school_type")["admit_rate_residual"].mean().sort_values(ascending=False)
res_pp = (res * 100).round(1)
top_type = res_pp.idxmax()
top_val = res_pp.max()
worst_type = res_pp.idxmin()
worst_val = res_pp.min()

# ---------- KPI cards ----------
k1, k2, k3, k4 = st.columns(4)
k1.markdown(f"<div class='card feature'><div class='kick-sm'>Top school type</div><div class='metric-big win'>+{top_val} pp</div><div class='muted'>{top_type.replace(' (Public)','')}</div></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='card blue'><div class='kick-sm'>Lowest</div><div class='metric-big lose'>{worst_val:+} pp</div><div class='muted'>{worst_type.replace(' (Public)','')}</div></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='card blue'><div class='kick-sm'>School types</div><div class='metric-big'>{int(len(res_pp))}</div><div class='muted'>compared</div></div>", unsafe_allow_html=True)
k4.markdown(f"<div class='card blue'><div class='kick-sm'>Applicants in view</div><div class='metric-big'>{int(d['applicants'].sum()):,}</div><div class='muted'>{campus}</div></div>", unsafe_allow_html=True)

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="h2">1 &middot; Which school type beats expectations most</div>', unsafe_allow_html=True)
chart = res_pp.reset_index()
chart.columns = ["school_type", "beats_expected_pp"]
fig = px.bar(chart, x="school_type", y="beats_expected_pp",
             color="beats_expected_pp", color_continuous_scale="RdYlGn",
             color_continuous_midpoint=0, text="beats_expected_pp")
fig.update_layout(xaxis_title="", yaxis_title="Beats expected admit rate (pp)", height=400,
                  paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                  font=dict(family="IBM Plex Mono", color="#3a3f45"))
fig.update_traces(texttemplate="%{text}", textposition="outside",
                  marker=dict(line=dict(width=0)))
st.plotly_chart(fig, width="stretch")
st.markdown('<div class="muted">Bars above zero admit more than their poverty / GPA / size profile predicts. Continuation high schools lead by a wide margin.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="h2">2 &middot; Every school on the map, colored by over/under-performance</div>', unsafe_allow_html=True)
m = d.dropna(subset=["lat", "lon"]).copy()
m["pp"] = m["admit_rate_residual"] * 100
fig2 = px.scatter_geo(m, lat="lat", lon="lon", color="pp",
                      color_continuous_scale="RdYlGn", color_continuous_midpoint=0,
                      hover_name="high_school", hover_data={"pp": ":.1f", "school_type": True, "lat": False, "lon": False},
                      scope="usa", center={"lat": 36.5, "lon": -119.5})
fig2.update_layout(height=520, paper_bgcolor="rgba(0,0,0,0)",
                   geo=dict(lakecolor="rgb(255,255,255)", bgcolor="rgba(0,0,0,0)",
                            landcolor="#f1ede3", showland=True, subunitcolor="#cfc9ba",
                            countrycolor="#cfc9ba"))
fig2.update_traces(marker=dict(size=7, opacity=0.85))
st.plotly_chart(fig2, width="stretch")
st.markdown('<div class="muted">Green schools admitted above expectation, red below. Use the sidebar to filter by school type.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="h2">3 &middot; How the gap moved over time</div>', unsafe_allow_html=True)
trend = (dash[(dash["school_type"].notna()) & (dash["campus"] == campus) & (dash["school_type"].isin(school_filter))]
         .groupby(["fall_term", "school_type"])["admit_rate_residual"].mean().reset_index()).dropna(subset=["admit_rate_residual"])
trend["pp"] = trend["admit_rate_residual"] * 100
fig3 = px.line(trend, x="fall_term", y="pp", color="school_type", markers=True, line_shape="linear",
               color_discrete_sequence=px.colors.qualitative.Set1)
fig3.update_layout(xaxis_title="Fall term", yaxis_title="Beats expected (pp)", height=400,
                   paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                   font=dict(family="IBM Plex Mono", color="#3a3f45"))
st.plotly_chart(fig3, width="stretch")
st.markdown('<div class="muted">Only years with data are plotted, so lines stay continuous. Widen the slider to see the long run.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="h2">4 &middot; Campus &times; school-type over-performance</div>', unsafe_allow_html=True)
piv = d.groupby(["school_type", "campus"])["admit_rate_residual"].mean().unstack() * 100
fig4 = px.imshow(piv, color_continuous_scale="RdYlGn", color_continuous_midpoint=0, aspect="auto",
                 labels=dict(x="Campus", y="School type", color="Beats expected (pp)"))
fig4.update_layout(height=360, paper_bgcolor="rgba(0,0,0,0)",
                   font=dict(family="IBM Plex Mono", color="#3a3f45"))
st.plotly_chart(fig4, width="stretch")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="h2">5 &middot; Individual schools that beat expectations most</div>', unsafe_allow_html=True)
sch = d.groupby("high_school")["admit_rate_residual"].mean().sort_values(ascending=False).head(20) * 100
st.dataframe(sch.round(1).reset_index().rename(columns={"high_school": "high_school", "admit_rate_residual": "beats_expected_pp"}),
             width="stretch", height=420)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="h2">6 &middot; Context: the Computer Science admit-rate penalty (2025)</div>', unsafe_allow_html=True)
d25 = disc[disc["fall_term"] == 2025]
ov = d25[d25["broad_discipline"] == "All disciplines"].set_index("campus")["admit_rate"]
cs = d25[d25["broad_discipline"] == "Computer Science"].set_index("campus")["admit_rate"]
pen = (cs - ov).dropna().sort_values()
cc = pen.reset_index()
cc.columns = ["campus", "cs_penalty_pp"]
fig5 = px.bar(cc, x="campus", y="cs_penalty_pp", color="cs_penalty_pp",
              color_continuous_scale="RdYlGn_r", color_continuous_midpoint=0, text="cs_penalty_pp")
fig5.update_layout(xaxis_title="", yaxis_title="CS rate minus campus overall (pp)", height=360,
                   paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                   font=dict(family="IBM Plex Mono", color="#3a3f45"))
fig5.update_traces(texttemplate="%{text}", textposition="outside")
st.plotly_chart(fig5, width="stretch")
st.markdown('<div class="muted">Negative = CS hurts your odds vs the campus average. Davis is harshest; this is the crowded finding most teams will show, so we treat it as context, not our headline.</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section" style="border-top:1px solid var(--line);">', unsafe_allow_html=True)
st.markdown(
    '<div class="card feature"><div class="kick-sm" style="color:var(--gold-ink)">Finding</div>'
    '<div class="lede" style="color:var(--ink)"><b>Continuation High Schools beat their expected UC admit rate by ~21.5 pp (2022&ndash;2024)</b>, '
    'the highest of any CA public school type, while regular public high schools average only ~1.7 pp. '
    'The schools expected to send the fewest students to UC are the ones that most outperform their predicted admit rate.</div></div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="muted" style="margin-top:10px">Source: event dashboard_data.csv + uc_freshman_admission_by_discipline.csv. Residual column precomputed by organizers (controls for FRPM poverty, applicant GPA, school size). Universitywide is not the sum of campuses.</div>', unsafe_allow_html=True)
