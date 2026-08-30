#!/usr/bin/env python3
"""
UC Admissions Data Challenge - Data Cleaning Pipeline
====================================================
Reads the raw 5 CSVs from the event Data/ folder, cleans them according to the
README's rules, and writes analysis-ready files into cleaned_data/.

RULES HANDLED (from README.md):
1. "Universitywide" is NOT the sum of campuses (it counts students, not apps).
   -> We KEYPT it separate and flag it with is_universitywide.
2. Blank counts are REDACTED (<5 apps or <3 admits), NOT zero.
   -> We keep NaN everywhere. NEVER fillna(0).
3. Do NOT sum school-level ethnicity columns. Use the ethnicity file.
   -> ethnicity file is cleaned separately, never summed from school rows.
4. Sum the counts, then divide. Never average the rates.
   -> All aggregate files recompute rates as sum(admits)/sum(applicants).
5. ~6% of schools lack cds_code (no state characteristics).
   -> Kept, flagged with has_characteristics = cds_code.notna().
6. Coverage gaps across years. -> Kept as NaN, not zero-filled.

OUTPUT FILES (all in cleaned_data/):
  clean_schools.csv                - big table cleaned & typed (65->typed cols)
  clean_dashboard_model.csv        - dashboard_data cleaned (modeling baseline)
  clean_ethnicity.csv              - tidy ethnicity long format
  clean_discipline.csv             - freshman admission by discipline (9 campuses)
  clean_transfer_major.csv        - berkeley transfer named majors
  agg_school_year.csv              - per school per year (UNIVERSITYWIDE only = systemwide)
  agg_campus_year.csv              - per campus per year (all 10 campus rows)
  agg_school_campus_year.csv      - per school per campus per year (9 campuses)
  agg_county_year.csv              - per county per year
  agg_school_latest_2025.csv      - one row per school, 2025 systemwide + traits
  agg_ethnicity_by_campus_year.csv- ethnicity shares by campus/year (from ethnicity file)
"""

import os
import pandas as pd
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "Data")
OUT = os.path.join(BASE, "cleaned_data")
os.makedirs(OUT, exist_ok=True)

def p(name):
    return os.path.join(DATA, name)

# Column groups -------------------------------------------------------------
COUNT_COLS = ["applicants", "admits", "enrollees"]
RATE_COLS = ["admit_rate", "yield_rate"]
GPA_COLS = ["applicant_gpa", "admit_gpa", "enrollee_gpa"]
ETH_GROUPS = ["african_american", "american_indian", "asian", "domestic_unknown",
              "hispanic_latinx", "int_l", "pacific_islander", "white"]
APP_COLS = [f"app_{g}" for g in ETH_GROUPS]
ADM_COLS = [f"adm_{g}" for g in ETH_GROUPS]
ENR_COLS = [f"enr_{g}" for g in ETH_GROUPS]
TRAIT_COLS = ["cohort_students", "graduates", "grad_rate", "ag_completers",
              "ag_completion_rate", "hs_completers", "college_going_rate",
              "enrolled_uc", "enrolled_csu", "enrolled_ccc",
              "enrolled_in_state_private", "enrolled_out_of_state",
              "enrollment_k12", "frpm_count", "frpm_pct",
              "caaspp_ela_mean_score", "caaspp_mathematics_mean_score",
              "caaspp_ela_pct_met", "caaspp_mathematics_pct_met"]

def clean_big_table(path, extra_cols=None):
    """Load + clean one of the two big school-level tables."""
    df = pd.read_csv(path, low_memory=False)
    # Normalize CDS code: strip .0, zero-pad to 14 digits
    df["cds_code"] = (df["cds_code"].astype("string").str.replace(r"\.0$", "", regex=True)
                      .str.zfill(14))
    # Year as int
    df["fall_term"] = df["fall_term"].astype(int)
    # Charters
    df["charter"] = df["charter"].map({"Y": True, "N": False})
    # Counts -> nullable Int
    for c in COUNT_COLS + APP_COLS + ADM_COLS + ENR_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
    # Rates + GPAs -> float
    for c in RATE_COLS + GPA_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype(float)
    # Traits -> float (keep NaN = redacted / not-collected)
    for c in TRAIT_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").astype(float)
    # Extra modeling cols (dashboard_data only)
    if extra_cols:
        for c in extra_cols:
            if c in df.columns:
                df[c] = pd.to_numeric(df[c], errors="coerce").astype(float)
    # Text normalization
    for c in ["high_school", "city", "county", "cde_district", "school_type"]:
        df[c] = df[c].astype("string").str.strip()
    # Flags
    df["is_universitywide"] = (df["campus"] == "Universitywide")
    df["is_campus"] = (df["campus"] != "Universitywide")
    df["has_characteristics"] = df["cds_code"].notna()
    return df

# 1. Clean the two big tables ----------------------------------------------
print(">>> Cleaning bay_area_modeling_table.csv ...")
schools = clean_big_table(p("bay_area_modeling_table.csv"))
schools.to_csv(os.path.join(OUT, "clean_schools.csv"), index=False)

print(">>> Cleaning dashboard_data.csv ...")
extra = ["expected_admit_rate", "admit_rate_residual", "peer_cohort_students",
         "peer_ag_completers", "peer_applicants", "peer_admits", "peer_enrollees"]
dashboard = clean_big_table(p("dashboard_data.csv"), extra_cols=extra)
dashboard.to_csv(os.path.join(OUT, "clean_dashboard_model.csv"), index=False)

# 2. Ethnicity (tidy, already long) ----------------------------------------
print(">>> Cleaning uc_admissions_summary_by_ethnicity.csv ...")
eth = pd.read_csv(p("uc_admissions_summary_by_ethnicity.csv"), low_memory=False)
eth["fall_term"] = eth["fall_term"].astype(int)
eth["n"] = pd.to_numeric(eth["n"], errors="coerce").astype("Int64")
eth = eth.rename(columns={"count_type": "count_category"})
eth["count_category"] = eth["count_category"].map(
    {"App": "applicants", "Adm": "admits", "Enr": "enrollees"})
eth.to_csv(os.path.join(OUT, "clean_ethnicity.csv"), index=False)

# Ethnicity shares by campus/year (proper: from the file, not school rows)
esh = (eth.pivot_table(index=["campus", "fall_term"],
                       columns="count_category", values="n", aggfunc="sum")
       .reset_index())
esh["admit_rate"] = esh["admits"] / esh["applicants"]
esh["yield_rate"] = esh["enrollees"] / esh["admits"]
esh.to_csv(os.path.join(OUT, "agg_ethnicity_by_campus_year.csv"), index=False)

# 3. Discipline (freshman by major area) -----------------------------------
print(">>> Cleaning uc_freshman_admission_by_discipline.csv ...")
disc = pd.read_csv(p("uc_freshman_admission_by_discipline.csv"), low_memory=False)
disc["fall_term"] = disc["fall_term"].astype(int)
for c in ["applicants", "admits", "enrollees"]:
    disc[c] = pd.to_numeric(disc[c], errors="coerce").astype("Int64")
for c in ["admit_rate", "yield_rate", "admit_gpa_p25", "admit_gpa_p75",
          "enrollee_gpa_p25", "enrollee_gpa_p75"]:
    disc[c] = pd.to_numeric(disc[c], errors="coerce").astype(float)
disc.to_csv(os.path.join(OUT, "clean_discipline.csv"), index=False)

# 4. Transfer named majors (Berkeley) -------------------------------------
print(">>> Cleaning uc_transfer_admission_by_major.csv ...")
tr = pd.read_csv(p("uc_transfer_admission_by_major.csv"), low_memory=False)
tr["fall_term"] = tr["fall_term"].astype(int)
for c in ["applicants", "admits", "enrollees"]:
    tr[c] = pd.to_numeric(tr[c], errors="coerce").astype("Int64")
for c in ["admit_rate", "yield_rate", "admit_gpa_p25", "admit_gpa_p75",
          "enrollee_gpa_p25", "enrollee_gpa_p75"]:
    tr[c] = pd.to_numeric(tr[c], errors="coerce").astype(float)
tr.to_csv(os.path.join(OUT, "clean_transfer_major.csv"), index=False)

# 5. AGGREGATES (sum counts, then divide) --------------------------------
def agg_recompute(g):
    d = {}
    for c in COUNT_COLS:
        d[c] = g[c].sum(min_count=1)
    apps = d["applicants"]
    adm = d["admits"]
    enr = d["enrollees"]
    d["admit_rate"] = (adm / apps) if (pd.notna(apps) and apps != 0) else np.nan
    d["yield_rate"] = (enr / adm) if (pd.notna(adm) and adm != 0) else np.nan
    return pd.Series(d)

# 5a. School x Year (UNIVERSITYWIDE ONLY = correct systemwide number)
print(">>> Building agg_school_year (Universitywide) ...")
sw = schools[schools["is_universitywide"]].copy()
agg_sy = sw.groupby(["high_school", "fall_term"], as_index=False).apply(agg_recompute)
# attach school traits (take first non-null per school-year)
traits_first = (sw.sort_values("fall_term")
                .groupby(["high_school", "fall_term"], as_index=False)[
                    ["city", "county", "cde_district", "cds_code", "school_type",
                     "charter"] + TRAIT_COLS].first())
agg_sy = agg_sy.merge(traits_first, on=["high_school", "fall_term"], how="left")
agg_sy.to_csv(os.path.join(OUT, "agg_school_year.csv"), index=False)

# 5b. Campus x Year (all 10 campus rows, including Universitywide)
print(">>> Building agg_campus_year ...")
agg_cy = schools.groupby(["campus", "fall_term"], as_index=False).apply(agg_recompute)
agg_cy.to_csv(os.path.join(OUT, "agg_campus_year.csv"), index=False)

# 5c. School x Campus x Year (9 real campuses)
print(">>> Building agg_school_campus_year ...")
sc = schools[schools["is_campus"]].copy()
agg_scy = sc.groupby(["high_school", "campus", "fall_term"], as_index=False).apply(agg_recompute)
agg_scy.to_csv(os.path.join(OUT, "agg_school_campus_year.csv"), index=False)

# 5d. County x Year (Universitywide)
print(">>> Building agg_county_year ...")
agg_cty = sw.groupby(["county", "fall_term"], as_index=False).apply(agg_recompute)
agg_cty.to_csv(os.path.join(OUT, "agg_county_year.csv"), index=False)

# 5e. Latest 2025 per school (systemwide + traits) - sprint-ready
print(">>> Building agg_school_latest_2025 ...")
latest = agg_sy[agg_sy["fall_term"] == 2025].copy()
latest = latest.sort_values("admits", ascending=False)
latest.to_csv(os.path.join(OUT, "agg_school_latest_2025.csv"), index=False)

# Summary ----------------------------------------------------------------
print("\n===== DONE =====")
print(f"cleaned_data/ files written:")
for f in sorted(os.listdir(OUT)):
    fp = os.path.join(OUT, f)
    sz = os.path.getsize(fp) // 1024
    rows = sum(1 for _ in open(fp, "rb")) - 1
    print(f"  {f:38s} {rows:>7,} rows  {sz:>6,} KB")

# Quick sanity checks
print("\n--- SANITY CHECKS ---")
cy = pd.read_csv(os.path.join(OUT, "agg_campus_year.csv"))
uw = cy[cy["campus"] == "Universitywide"][cy["fall_term"] == 2025]
berk = cy[(cy["campus"] == "Berkeley") & (cy["fall_term"] == 2025)]
print(f"2025 Universitywide admits (RIGHT, students): {int(uw['admits'].iloc[0]):,}")
print(f"2025 Berkeley admits (sum of campus apps):    {int(berk['admits'].iloc[0]):,}")
sy = pd.read_csv(os.path.join(OUT, "agg_school_year.csv"))
mh = sy[sy["high_school"].str.contains("MILPITAS", case=False, na=False)]
if len(mh):
    r = mh[mh["fall_term"] == 2025].iloc[0]
    print(f"Milpitas HS 2025: {int(r['applicants'])} apps -> {int(r['admits'])} admits "
          f"({r['admit_rate']*100:.1f}%)")
