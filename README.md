# UC Admissions Lab - Dashboard Construction

## Question
For CA public high schools in 2022-2024, which school type most outperforms its expected UC
freshman admit rate, after controlling for poverty, applicant GPA, and school size?

- Time window: fall terms 2022, 2023, 2024
- Population: CA public high schools (Universitywide)
- Metric: mean admit_rate_residual in percentage points, by school type

## Finding
Continuation High Schools beat their expected UC admit rate by about 21.5 percentage points
across 2022-2024, the highest of any CA public school type. Alternative Schools of Choice
(+10.1pp) and K-12 Public schools (+7.2pp) also clear expectations, while regular public high
schools average only about 1.7pp. The schools expected to send the fewest students to UC are the
ones that most outperform their predicted admit rate.

## Data and metric
Source files: `dashboard_data.csv`, `uc_freshman_admission_by_discipline.csv` (event Google Drive).
The `admit_rate_residual` column is the real admit rate minus the expected admit rate. The expected
rate is computed by the event organizers after adjusting for school poverty (FRPM), applicant GPA,
and school size, so a positive residual means a school admitted more than its profile predicted.

## Method
Filter to CA public school rows, Universitywide, fall 2022-2024; group by `school_type`; average the
residual. Rates are computed by summing counts then dividing, never by averaging rates.
Universitywide is not the sum of campuses and is never treated as one.

## Files
- `app.py` - Streamlit dashboard
- `dashboard_notebook.ipynb` - Colab notebook that computes the answer
- `dashboard_formulas.txt` - plain explanation of the calculation
- `dashboard_data.csv`, `uc_freshman_admission_by_discipline.csv` - source data
- `presentation.html` - judge presentation
- `tools_used.md` - tools and stack

## Gemini features
The AI Lab uses free Gemini models (key entered in-session only, never stored). It offers an
Ask-the-data Q and A, a Judge Scorecard, a Competitor Radar, a Wow Hook opener, and a README
generator. The model is given the real computed numbers so it does not guess.

## Run locally
```
pip install streamlit plotly pandas
streamlit run app.py
```
