# BC Post-Secondary Enrollment & Funding Trends

An end-to-end SQL and Python analytics project evaluating international and domestic enrollment patterns, system-wide headcount stability, and provincial operating grant distribution across B.C. public post-secondary institutions.

---

## Problem Statement

Public post-secondary institutions in British Columbia have experienced significant demographic and policy shifts over the past decade. Understanding how international student enrollment has evolved relative to domestic enrollment—and how provincial operating grants per Full-Time Equivalent (FTE) are distributed across regional colleges, institutes, and research universities—is critical for institutional resource allocation and policy analysis.

This project addresses three core analytical questions:
1. **Enrollment Composition**: How has the proportion of international versus domestic student headcount shifted across public institutions over time?
2. **System Stability**: What are the multi-year FTE headcount trends, and how smoothly does the system adjust using a 3-year rolling average?
3. **Funding Efficiency**: How do provincial operating grants per actual FTE vary across different institutional designations and geographic regions?

---

## Data Sources & Licensing

This project utilizes open datasets provided by the Government of British Columbia under the **Open Government Licence — British Columbia**:

* **Full-Time Equivalent (FTE) Enrolments**: [FTE Enrolments at B.C. Public Post-Secondary Institutions](https://catalogue.data.gov.bc.ca/dataset/full-time-equivalent-enrolments-at-b-c-public-post-secondary-institutions)
* **FTE Targets**: [Full-Time Equivalent Enrolment Targets](https://catalogue.data.gov.bc.ca/dataset/full-time-equivalent-enrolment-targets-at-public-post-secondary-institutions)
* **Operating Grants**: [Operating Grants at B.C. Public Post-Secondary Institutions](https://open.canada.ca/data/en/dataset/6358b21a-ce9f-4b73-a4d0-7e30f7885959)
* **Domestic and International Student Headcount**: [Headcount by Economic Development Region and Institution](https://open.canada.ca/data/en/dataset/ace77db4-1f4f-4db1-91bf-9cf8475d9dfc)


> **Data Baseline**: All source datasets reflect official public records retrieved and verified as available on **September 9, 2026**.
>
> **Scope Note**: This analysis exclusively covers **21 public post-secondary institutions** in British Columbia. Private colleges and non-funded institutions are excluded from the underlying provincial datasets.
>
> **Data Availability**: Raw source files (`.csv`) are excluded from version control via `.gitignore` following repository size best practices. Download the source files from the links above into `data/raw/` to initialize the project locally.

---

## Project Structure

```text
1-bc-postsecondary-enrollment-trends/
├── data/
│   ├── processed/                      # Cleaned datasets, enrollment.db, and exported PNG charts
│   └── raw/                            # Source CSV downloads from B.C. Open Data
├── notebooks/
│   ├── 01_data_inspection.ipynb        # Initial exploratory analysis and data profile inspection
│   └── 05_python_analysis_viz.ipynb    # Visualizations and database query integration
├── scripts/
│   ├── 02_data_cleaning.py             # Data transformation, standardization, and tidying
│   ├── 03_db_migration.py              # SQLite schema build and data loading
│   └── generate_institution_mapping.py # Cross-dataset institution name mapping generator
├── sql/
│   └── 04_analytical_queries.sql       # Analytical SQL queries (CTEs, Window Functions)
├── .gitignore                          # Excludes raw data, SQLite DBs, and virtual environments
├── LICENSE                             # MIT License
├── README.md                           # Project documentation
├── notes.md                            # Data inspection and mapping development notes
└── requirements.txt                    # Pinned project dependencies