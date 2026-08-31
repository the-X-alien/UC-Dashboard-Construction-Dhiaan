# UC Admissions Data Challenge 2026 - Submission

**Team:** the-X-alien (Dhiaan Dave)
**Live app:** https://uc-admissions-datathon-dhiaan.streamlit.app/

## The question
For California public high schools in 2022-2024, which school type most outperforms its expected UC freshman admit rate, after controlling for poverty, applicant GPA, and school size?

## The finding
**Continuation High Schools** beat their expected admit rate by **+21.5 percentage points** (2022-2024) - the largest over-performance of any public school type. Regular public high schools barely beat expectation (+1.7pp).

School type | Beats expectation by
--- | ---
Continuation High Schools | +21.5pp
Alternative Schools of Choice | +9.0pp
K-12 Schools (Public) | +3.9pp
High Schools (Public) | +1.7pp
High Schools in 1 District | +0.6pp

## How we got there (methodology)
- **Metric:** `admit_rate_residual` (pp), the gap between a school's actual and predicted admit rate. Precomputed by the organizers; larger = more over-performance.
- **Aggregation:** we sum applicant and admit counts per school type, then divide (never average percentages - that biases toward small schools).
- **Universitywide is not a campus sum:** reported separately to avoid a classic aggregation error.
- **Context, not headline:** the crowded finding (CS lowers UC odds, Davis harshest) is shown as background so we don't duplicate what every team shows.
- **Poverty does not explain it:** FRPM% vs residual correlation is near zero - the gap holds after poverty is controlled.
- **Reproducible:** every number traces to `dashboard_notebook.ipynb` on the cleaned data.

## The dashboard
A Streamlit app with: Overview (KPI cards + school-type bar), School Map (green = beats, red = below, filterable by type), Top Schools ranking, Deep Analysis (county over-performance + FRPM-vs-residual), and an AI Lab (Gemini validates and stress-tests the finding; it never fabricates it).

## Run it locally
```
pip install -r requirements.txt
streamlit run app.py
```

## Files
- `app.py` - the dashboard
- `requirements.txt` - dependencies (streamlit, pandas, numpy, plotly)
- `cleaned_data/` - cleaned source CSVs
- `dashboard_notebook.ipynb` - the methodology notebook (reproducible numbers)
- `UC-FINAL-PRESENTATION.pptx` - the final A+ presentation (rubric: Question, Finding, Rigor, Dashboard, Presentation)
- `README.md` - this file
