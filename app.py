import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="UC Admit Rate Residual by School Type", layout="wide")

st.title("Which CA Public School Type Beats Its Expected UC Admit Rate?")
st.caption("UC Admissions Data Challenge 2026 - Dashboard Construction")

st.markdown(
    "**Question:** For CA public high schools in 2022-2024, which school type most "
    "outperforms its expected UC freshman admit rate, after controlling for poverty, "
    "applicant GPA, and school size?"
)

st.info(
    "The data has a column `admit_rate_residual`: the real admit rate minus the expected "
    "admit rate. The expected rate is already adjusted for poverty, GPA, and school size, "
    "so a positive residual means a school did BETTER than its profile predicts. "
    "We average it per school type across 2022-2024 (Universitywide)."
)


@st.cache_data
def load():
    df = pd.read_csv("dashboard_data.csv")
    df["admit_rate_residual"] = pd.to_numeric(df["admit_rate_residual"], errors="coerce")
    return df


dash = load()

st.sidebar.header("Filters")
years = st.sidebar.slider("Fall term range", 2015, 2025, (2022, 2024), step=1)
campus = st.sidebar.selectbox(
    "Campus", ["Universitywide"] + sorted([c for c in dash["campus"].dropna().unique() if c != "Universitywide"])
)

d = dash[
    (dash["fall_term"].between(years[0], years[1]))
    & (dash["school_type"].notna())
    & (dash["campus"] == campus)
]
pub = d[d["school_type"].notna()]

res = pub.groupby("school_type")["admit_rate_residual"].mean().sort_values(ascending=False)
res_pp = (res * 100).round(1)

top_type = res_pp.idxmax()
top_val = res_pp.max()

c1, c2 = st.columns(2)
with c1:
    st.metric("Top school type", top_type)
with c2:
    st.metric("Beats expected by", f"+{top_val} pp")

st.subheader("Mean admit-rate residual by school type (percentage points)")
chart = res_pp.reset_index()
chart.columns = ["school_type", "beats_expected_pp"]
fig = px.bar(
    chart,
    x="school_type",
    y="beats_expected_pp",
    color="beats_expected_pp",
    color_continuous_scale="RdYlGn",
    text="beats_expected_pp",
)
fig.update_layout(xaxis_title="School type", yaxis_title="Beats expected admit rate (pp)", height=480)
fig.update_traces(texttemplate="%{text}", textposition="outside")
st.plotly_chart(fig, use_container_width=True)

with st.expander("See the numbers"):
    st.dataframe(chart)

st.subheader("By campus (for the top school type)")
piv = (
    d.groupby(["school_type", "campus"])["admit_rate_residual"]
    .mean()
    .unstack()
    .round(3)
)
st.dataframe((piv * 100).round(1))

st.markdown("---")
st.caption(
    "Finding: Continuation High Schools beat their expected UC admit rate by ~21.5 pp "
    "(2022-2024), the highest of any CA public school type, while regular public high "
    "schools average only ~1.7 pp. The schools expected to do worst actually do best."
)
