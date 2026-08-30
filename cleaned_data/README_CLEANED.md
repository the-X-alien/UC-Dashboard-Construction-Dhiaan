# CLEANED DATA — what's in here & how to use it

All files produced by `clean_data.py` from the raw `Data/` folder.
Run `python clean_data.py` again any time to regenerate.

## CRITICAL RULES (from the original README — already baked in)
- `Universitywide` rows = "admitted to AT LEAST ONE UC" (counts students). It is NOT
  the sum of the 9 campuses. Use `agg_school_year.csv` / `agg_campus_year.csv` correctly.
- Blank cells = REDACTED (<5 applicants or <3 admits/enrollees). They are kept as empty,
  NEVER filled with 0. Don't sum them.
- For race/ethnicity: use `clean_ethnicity.csv` and `agg_ethnicity_by_campus_year.csv`.
  Do NOT sum the school-level `app_*`/`adm_*`/`enr_*` columns.
- Rates are always recomputed as SUM(counts)/SUM(counts). Never average a column of rates.

## FILE GUIDE

### Big school-level tables (one row = 1 school, 1 year, 1 campus)
- `clean_schools.csv` (34,311 rows) — raw table, typed & cleaned.
    - Flags added: `is_universitywide`, `is_campus`, `has_characteristics`.
    - CDS code normalized to 14-digit string. Charter -> True/False. Counts -> Int64.
- `clean_dashboard_model.csv` (34,311 rows) — same + modeling cols
    (`expected_admit_rate`, `admit_rate_residual`, `peer_*`). Use this if you want a
    model baseline without fitting one.

### Tidy / small files
- `clean_ethnicity.csv` (4,239) — long format: campus, year, category(App/Adm/Enr), ethnicity, n.
- `clean_discipline.csv` (101) — freshman admit rate by major AREA, 9 campuses, Fall 2025.
    Great for "is CS worth it?" questions. CS rows: Berkeley 0.06, UCLA 0.07, etc.
- `clean_transfer_major.csv` (49) — named majors at Berkeley transfers, Fall 2025.
    Has ComputerScience (0.03!) vs DataScience (0.14) — gold for CS penalty story.

### PRE-AGGREGATED (sprint-ready — just read, no math needed)
- `agg_school_year.csv` (4,560) — per school per year, UNIVERSITYWIDE only (correct systemwide).
    Already has recomputed admit_rate/yield_rate + school traits joined on.
    **Use this for "how did X school do in year Y" questions.**
- `agg_campus_year.csv` (165) — per campus per year (all 10 rows incl Universitywide).
    **Use for "what's Berkeley's admit rate in 2025" type questions.**
- `agg_school_campus_year.csv` (29,277) — per school per campus per year (9 real campuses).
    **Use for "which UC does Milpitas send most kids to" type questions.**
- `agg_county_year.csv` (189) — per county per year.
- `agg_school_latest_2025.csv` (244) — one row per Bay Area school, 2025 systemwide + traits,
    sorted by admits. **Top schools at a glance. MHS is row ~top.**
- `agg_ethnicity_by_campus_year.csv` (90) — ethnicity shares by campus/year (from the
    ethnicity file, properly summed). **Use for equity questions.**

## ANSWERING SPRINT QUESTIONS — which file
| Question type | File to open |
|---|---|
| "What % of X school got into UC in year Y?" | agg_school_year.csv |
| "Berkeley/UCLA admit rate in 2025?" | agg_campus_year.csv |
| "How many MHS kids got into UC 2025?" | agg_school_latest_2025.csv (filter high_school contains MILPITAS) |
| "Is CS worth the lower odds?" | clean_discipline.csv (filter broad_discipline == Computer Science) |
| "Berkeley CS vs Data Science?" | clean_transfer_major.csv |
| "Equity / race gap?" | clean_ethnicity.csv or agg_ethnicity_by_campus_year.csv |
| "Which UC does my school feed into most?" | agg_school_campus_year.csv |
| "County-level comparison?" | agg_county_year.csv |

## For Power BI / Tableau / OpenCode
- All CSVs are UTF-8, clean headers, no merged cells, no embedded formulas.
- Load `clean_schools.csv` as your main fact table. Join `agg_*` tables as needed.
- Drag `fall_term` as the time axis, `campus`/`county`/`high_school` as dimensions.
- Use the pre-computed `*_rate` columns; do NOT recompute from raw counts in the viz
  unless you use SUM-aggregation (Power BI/Tableau default to SUM which is correct here).

## Regenerate
```
python clean_data.py
```
Dependencies: pandas, numpy (already installed).
