# Tools Used

| Tool | Version | Used for |
|------|---------|----------|
| Python | 3.11 | Core language for all analysis and app logic |
| pandas | 2.x | Data cleaning, grouping, and computing admit_rate_residual by school type |
| Google Colab | - | Authoring the sprint and dashboard notebooks (sprint_notebook.ipynb, dashboard_notebook.ipynb) |
| Streamlit | 1.62 | Interactive dashboard web app (app.py) |
| Plotly | latest | Charts: bar, line, scatter_geo map, imshow heatmap, histogram, scatter with OLS trendline |
| GitHub | - | Source control and MLH submission (three repos) |
| Gemini API | gemini-2.5-flash (free) | AI Lab: ask-the-data, judge scorecard, competitor radar, wow hook, README generator. Key entered in-session only |
| Google Fonts | - | Inter, Fraunces, IBM Plex Mono for the dashboard typography |

## Event datasets
- dashboard_data.csv - school-level UC outcomes with admit_rate_residual
- uc_freshman_admission_by_discipline.csv - discipline admit rates (CS context)
- bay_area_modeling_table.csv - county / school cohort outcomes
- uc_admissions_summary_by_ethnicity.csv - ethnicity admit/enroll counts
- uc_transfer_admission_by_major.csv - transfer major GPA bands

## Judge rubric (1-5 each)
QUESTION (time window, population, metric), FINDING (concise + justifiable), RIGOR (nuanced
methodology), DASHBOARD (accurate + reliable), PRESENTATION (well-understood + conveyed).
