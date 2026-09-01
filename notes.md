# Data Exploration & Quality Log

## 1. Dataset Overview & Schema Discrepancies
* **`fte-enrollments-actual.csv`**: Contains 275 rows across 6 columns. Three trailing columns (`Unnamed: 3`, `Unnamed: 4`, `Unnamed: 5`) contain 100% `NaN` values.
* **`fte-enrollments-target.csv`**: Contains 275 rows across 6 columns. Also contains three trailing `Unnamed` null columns.
* **`operating-grants.csv`**: Contains 275 rows across 3 clean columns (`Fiscal Year`, `Institution`, `Operating Grant`).

## 2. Identified Data Quirks & Anomalies
* **Trailing Whitespace (Target Dataset):** The `Institution` column in `fte-enrollments-target.csv` contains trailing spaces across 6 institution names (`Capilano University `, `Kwantlen Polytechnic University `, `Nicola Valley Institute of Technology `, `Thompson Rivers University `, `University of the Fraser Valley `, and `Vancouver Island University `).
* **String Formatting in Numeric Fields:** 
  * `Operating Grant` in `operating-grants.csv` contains currency symbols and commas (e.g., `"$112,235,228"`), requiring string cleaning before numeric conversion.
  * `FTE Actual` and `FTE Target` contain formatted numeric strings with commas (e.g., `"13,279"`).
* **Unnecessary Metadata Columns:** `Unnamed: 3` through `Unnamed: 5` in `fte-enrollments-actual.csv` and `fte-enrollments-target.csv` contain no data and must be dropped.
* **Fiscal Year Mismatches & Data Boundaries:**
  * The datasets do not cover the exact same time period.
  * Only **9 fiscal years** (`FY 2016/17` through `FY 2024/25`) overlap across all three transactional datasets.
  * `fte-enrollments-actual.csv` starts earlier (`FY 2014/15`), while `fte-enrollments-target.csv` extends further into future projections (`FY 2026/27`).

## 3. Cleaning Action Items
1. Drop all `Unnamed:` columns from FTE actual and target DataFrames.
2. Apply `.str.strip()` to `Institution` string values across all raw DataFrames to ensure standard canonical joins.
3. Remove `$` and `,` characters from numeric columns (`Operating Grant`, `FTE Actual`, `FTE Target`) and cast to numeric types (`int64`).
4. Apply `.str.strip()` to `Fiscal Year` values and filter/join on the 9 overlapping years (`FY 2016/17` to `FY 2024/25`) during merge step.