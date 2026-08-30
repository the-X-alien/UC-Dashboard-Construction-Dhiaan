# UC Dashboard Construction - Dhiaan

## Question
For CA public high schools in 2022-2024, which school type most outperforms its expected UC freshman admit rate, after controlling for poverty, applicant GPA, and school size?

- Time window: fall terms 2022, 2023, 2024
- Population: CA public high schools (Universitywide)
- Metric: mean admit_rate_residual in percentage points, by school type

## Method
The dataset already includes `admit_rate_residual`, defined as the real admit rate minus the expected admit rate. The expected rate is computed by the event organizers after adjusting for school poverty (FRPM), applicant GPA, and school size, so a positive residual means a school beat what its profile predicted. We filter to public school rows in the 2022-2024 window at the Universitywide level, group by `school_type`, and average the residual. The dashboard lets you change the year range and campus and re-runs the same calculation.

## Finding
Continuation High Schools beat their expected UC admit rate by about 21.5 percentage points across 2022-2024, the highest of any CA public school type. Alternative Schools of Choice (+10.1pp) and K-12 Public schools (+7.2pp) also clear expectations, while regular public high schools average only about +1.7pp. The schools commonly expected to send the fewest students to UC are the ones that most outperform their predicted admit rate.

## Files
- `app.py` - Streamlit dashboard
- `dashboard_notebook.ipynb` - Colab notebook that computes the answer
- `dashboard_formulas.txt` - plain explanation of the calculation
- `dashboard_data.csv` - source data (from the event Google Drive)

## Run locally
```
pip install streamlit plotly pandas
streamlit run app.py
```
