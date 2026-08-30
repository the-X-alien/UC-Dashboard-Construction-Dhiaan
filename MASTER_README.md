# UC Admissions Data Challenge 2026 - Dhiaan

Combined submission for the UC Admissions Data Challenge (Cupertino Library, Aug 30 2026):
the **Question Sprint** (50% of score) and the **Dashboard Construction** (50% of score).

## What's inside

### Question Sprint (`/sprint`)
Ten numeric questions answered with pandas in Google Colab. Each answer is verified two ways
(pandas + SQL) and the two agree.

| # | Question | Answer |
|---|----------|--------|
| 1 | Fall 2025, avg # UC campuses an applicant applied to | **5.74** |
| 2 | UCLA 2025 admit rate, CA public high schools | **8.29%** |
| 3 | Campus where CS costs the most vs its own overall rate | **Davis** |
| 4 | IQR of Berkeley CS admit GPA, 2025 | **0.02** |
| 5 | Of 9 campuses, # where White admit rate > Hispanic/Latino(a) | **9** |
| 6 | Systemwide 2025: White or Hispanic/Latino(a) higher admit rate | **Hispanic/Latino(a)** |
| 7 | Bay Area 2023 grads enrolled in a CA CC within 12 months | **34.04%** |
| 8 | Mission San Jose 2023, share of a-g completers who applied to UC | **99.06%** |
| 9 | Distinct CA public high schools with >=1 UC applicant, 2025 | **193** |
| 10 | Of 5 schools, which beats expected Berkeley admit rate most (2022-25) | **MISSION SENIOR HIGH SCHOOL** |

Files: `sprint_notebook.ipynb` (Colab, one cell per question), `sprint_formulas.txt` (plain
explanations), `sprint_formulas.md` (pandas + SQL).

### Dashboard Construction (`/dashboard`)
**Question:** For CA public high schools in 2022-2024, which school type most outperforms its
*expected* UC freshman admit rate, after controlling for poverty, applicant GPA, and school size?

The dataset ships an `admit_rate_residual` column = real admit rate minus expected admit rate
(expected already adjusts for FRPM poverty, GPA, and school size), so a positive residual means a
school admitted more than its profile predicted.

**Finding:** Continuation High Schools beat their expected UC admit rate by ~21.5 pp (2022-2024),
the highest of any CA public school type, while regular public high schools average only ~1.7 pp.
The schools expected to send the fewest students to UC are the ones that most outperform their
predicted admit rate.

Files: `app.py` (Streamlit dashboard), `dashboard_notebook.ipynb` (Colab answer),
`dashboard_formulas.txt` (plain explanation), `dashboard_data.csv` + `uc_freshman_admission_by_discipline.csv`
(source data from the event Google Drive).

## Run the dashboard locally
```
pip install streamlit plotly pandas
streamlit run app.py
```

## Data
All source files come from the event Google Drive. `Universitywide` is not the sum of campuses
and is never treated as one. Rates are computed by summing counts then dividing, never by
averaging rates.
