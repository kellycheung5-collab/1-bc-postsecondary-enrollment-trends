# Data Exploration & Quality Log

## 1. Dataset Overview & Schema Discrepancies
* **`fte-enrollments-actual.csv`**: Contains 275 rows across 6 columns (`Fiscal Year`, `Institution`, `FTE Actual`, and 3 trailing `Unnamed` columns).
* **`fte-enrollments-target.csv`**: Contains 275 rows across 6 columns (`Fiscal Year`, `Institution`, `FTE Target`, and 3 trailing `Unnamed` columns).
* **`operating-grants.csv`**: Contains 275 rows across 3 clean columns (`Fiscal Year`, `Institution`, `Operating Grant`).
* **`student-headcount-by-region.csv`**: Contains student headcount broken down by `Institution`, `Fiscal Year`, and `Economic Development Region`. Uses abbreviated institution codes rather than full canonical names.

## 2. Identified Data Quirks & Anomalies
* **Trailing Whitespace (Target Dataset):** The `Institution` column in `fte-enrollments-target.csv` contains trailing spaces across 6 institution names (`Capilano University `, `Kwantlen Polytechnic University `, `Nicola Valley Institute of Technology `, `Thompson Rivers University `, `University of the Fraser Valley `, and `Vancouver Island University `).
* **Abbreviated Institution Names (Headcount Dataset):** `student-headcount-by-region.csv` uses short codes (e.g., `BCIT`, `UBC`, `VCC`) instead of full canonical names.
* **String Formatting in Numeric Fields:** 
  * `Operating Grant` in `operating-grants.csv` contains currency symbols and commas (e.g., `"$112,235,228"`), requiring string cleaning before conversion.
  * `FTE Actual` and `FTE Target` contain formatted numeric strings with commas (e.g., `"13,279"`).
* **Unnecessary Metadata Columns:** `Unnamed: 3` through `Unnamed: 5` in `fte-enrollments-actual.csv` and `fte-enrollments-target.csv` contain 100% `NaN` values and must be dropped.
* **Fiscal Year Mismatches & Data Boundaries:**
  * Datasets cover varying historical and projected time ranges.
  * Only **9 fiscal years** (`FY 2016/17` through `FY 2024/25`) overlap across all transactional datasets.
  * `fte-enrollments-actual.csv` starts earlier (`FY 2014/15`), while `fte-enrollments-target.csv` extends into future projections (`FY 2026/27`).

## 3. Cleaning Action Items
1. Drop all empty `Unnamed:` columns from FTE actual and target DataFrames.
2. Apply `.str.strip()` to `Institution` string values across all raw DataFrames to eliminate trailing/leading whitespace.
3. Translate institution short codes in `student-headcount-by-region.csv` to canonical names using `institution-mapping-base.csv` (or explicit dictionary lookup).
4. Remove `$` and `,` characters from numeric columns (`Operating Grant`, `FTE Actual`, `FTE Target`, `Headcount`) and cast to integer types (`int64`).
5. Apply `.str.strip()` to `Fiscal Year` values and filter/join on the 9 overlapping years (`FY 2016/17` to `FY 2024/25`) during the pipeline merge step.