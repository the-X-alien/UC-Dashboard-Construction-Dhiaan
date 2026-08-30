# UC Question Sprint - Dhiaan

Ten numeric questions from the UC Admissions Data Challenge question sprint, answered with pandas in Google Colab.

## Questions and answers
1. In fall 2025, how many UC campuses did the average applicant apply to? **5.74**
2. Fall 2025 UCLA admit rate for applicants from CA public high schools. **8.29%**
3. Fall 2025 campus where Computer Science costs the most admit rate vs its own overall rate. **Davis**
4. IQR of admit GPA for Berkeley Computer Science in fall 2025. **0.02**
5. In fall 2025, how many of the 9 UC campuses had White freshman admit rate higher than Hispanic/Latino(a)? **9**
6. Systemwide fall 2025, higher freshman admit rate: White or Hispanic/Latino(a)? **Hispanic/Latino(a)**
7. Of Bay Area high school graduates in class of 2023, share enrolled at a CA Community College within 12 months. **34.04%**
8. Mission San Jose High School fall 2023, share of a-g completers who applied to UC. **99.06%**
9. Distinct CA public high schools that sent at least one freshman applicant to UC in fall 2025. **193**
10. Of five listed schools, which most outperforms its expected Berkeley admit rate 2022-2025 (controls for a-g completion, poverty, applicant GPA, school size)? **MISSION SENIOR HIGH SCHOOL**

## Method
Each question was solved with a single pandas block. The event CSVs were used directly (no external stats): `bay_area_modeling_table.csv` for applicant counts, CCC enrollment, and school-level outcomes; `dashboard_data.csv` for campus and school residual rates; `uc_admissions_summary_by_ethnicity.csv` for ethnicity admit rates; `uc_freshman_admission_by_discipline.csv` for CS vs overall discipline rates; `uc_transfer_admission_by_major.csv` for Berkeley CS GPA bands. Every answer was cross-checked with a second method (SQL) and the two agreed.

## Files
- `sprint_notebook.ipynb` - Colab notebook, one cell per question, prints each answer
- `sprint_formulas.txt` - plain explanation of each formula
- `Data/` - source datasets from the event Google Drive
