-- Query 1: Year-over-Year (YoY) % Change in International Headcount
-- Uses LAG() window function to calculate annual growth per institution.

WITH international_by_year AS (
    SELECT 
        i.institution_name,
        f.fiscal_year,
        SUM(f.headcount) AS intl_headcount
    FROM fact_student_headcount f
    JOIN dim_institution i ON f.institution_id = i.institution_id
    WHERE f.student_type = 'International'
    GROUP BY i.institution_name, f.fiscal_year
)
SELECT 
    institution_name,
    fiscal_year,
    intl_headcount,
    LAG(intl_headcount) OVER (
        PARTITION BY institution_name 
        ORDER BY fiscal_year
    ) AS prev_year_headcount,
    ROUND(
        (CAST(intl_headcount AS FLOAT) - LAG(intl_headcount) OVER (
            PARTITION BY institution_name ORDER BY fiscal_year
        )) / NULLIF(LAG(intl_headcount) OVER (
            PARTITION BY institution_name ORDER BY fiscal_year
        ), 0) * 100, 2
    ) AS yoy_pct_change
FROM international_by_year
ORDER BY institution_name, fiscal_year;


-- Query 2: Rank Institutions by International Student Share (Most Recent Year)
-- Uses ROW_NUMBER() / RANK() to rank schools by international proportion in 2024/2025.

WITH student_breakdown AS (
    SELECT 
        i.institution_name,
        SUM(CASE WHEN f.student_type = 'International' THEN f.headcount ELSE 0 END) AS intl_headcount,
        SUM(f.headcount) AS total_headcount
    FROM fact_student_headcount f
    JOIN dim_institution i ON f.institution_id = i.institution_id
    WHERE f.fiscal_year = '2024/2025'
    GROUP BY i.institution_name
)
SELECT 
    institution_name,
    intl_headcount,
    total_headcount,
    ROUND(CAST(intl_headcount AS FLOAT) / NULLIF(total_headcount, 0) * 100, 2) AS intl_share_pct,
    RANK() OVER (
        ORDER BY CAST(intl_headcount AS FLOAT) / NULLIF(total_headcount, 0) DESC
    ) AS intl_share_rank
FROM student_breakdown
ORDER BY intl_share_rank;


-- Query 3: Running 3-Year Rolling Average of FTE Enrolment
-- Uses window functions with ROWS BETWEEN 2 PRECEDING AND CURRENT ROW.
WITH annual_fte AS (
    SELECT 
        i.institution_name,
        f.fiscal_year,
        SUM(f.fte_actual) AS total_fte
    FROM fact_institution_financials_fte f
    JOIN dim_institution i ON f.institution_id = i.institution_id
    GROUP BY i.institution_name, f.fiscal_year
)
SELECT 
    institution_name,
    fiscal_year,
    total_fte,
    ROUND(
        AVG(total_fte) OVER (
            PARTITION BY institution_name 
            ORDER BY fiscal_year 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 2
    ) AS rolling_3yr_avg_fte
FROM annual_fte
ORDER BY institution_name, fiscal_year;


-- Query 4: Funding per FTE Trend
-- Joins actual FTE and operating grant facts via CTEs.
WITH fte_totals AS (
    SELECT 
        institution_id,
        fiscal_year,
        SUM(fte_actual) AS total_fte
    FROM fact_institution_financials_fte
    GROUP BY institution_id, fiscal_year
),
grant_totals AS (
    SELECT 
        institution_id,
        fiscal_year,
        SUM(operating_grant) AS total_grant
    FROM fact_institution_financials_fte
    GROUP BY institution_id, fiscal_year
)
SELECT 
    i.institution_name,
    f.fiscal_year,
    g.total_grant AS operating_grant_cad,
    f.total_fte AS actual_fte,
    ROUND(g.total_grant / NULLIF(f.total_fte, 0), 2) AS grant_per_fte
FROM fte_totals f
JOIN grant_totals g 
    ON f.institution_id = g.institution_id 
   AND f.fiscal_year = g.fiscal_year
JOIN dim_institution i 
    ON f.institution_id = i.institution_id
ORDER BY i.institution_name, f.fiscal_year;


-- Query 5: Actual FTE vs. Target FTE Variance
-- Analyzes planned vs. actual performance by institution and year.
SELECT 
    i.institution_name,
    f.fiscal_year,
    SUM(f.fte_target) AS target_fte,
    SUM(f.fte_actual) AS actual_fte,
    SUM(f.fte_actual) - SUM(f.fte_target) AS fte_variance,
    ROUND(
        (SUM(f.fte_actual) - SUM(f.fte_target)) / NULLIF(SUM(f.fte_target), 0) * 100, 2
    ) AS variance_pct
FROM fact_institution_financials_fte f
JOIN dim_institution i ON f.institution_id = i.institution_id
GROUP BY i.institution_name, f.fiscal_year
ORDER BY i.institution_name, f.fiscal_year;


-- Query 6: Institutions  with Steepest International Declines
-- Compares max peak international headcount against recent totals.
WITH intl_by_inst AS (
    SELECT 
        i.institution_name,
        f.fiscal_year,
        SUM(f.headcount) AS intl_headcount
    FROM fact_student_headcount f
    JOIN dim_institution i ON f.institution_id = i.institution_id
    WHERE f.student_type = 'International'
    GROUP BY i.institution_name, f.fiscal_year
),
inst_peak_vs_recent AS (
    SELECT 
        institution_name,
        MAX(intl_headcount) AS peak_intl_headcount,
        SUM(CASE WHEN fiscal_year = '2024/2025' THEN intl_headcount ELSE 0 END) AS recent_intl_headcount
    FROM intl_by_inst
    GROUP BY institution_name
)
SELECT 
    institution_name,
    peak_intl_headcount,
    recent_intl_headcount,
    recent_intl_headcount - peak_intl_headcount AS headcount_drop,
    ROUND(
        (CAST(recent_intl_headcount AS FLOAT) - peak_intl_headcount) / NULLIF(peak_intl_headcount, 0) * 100, 2
    ) AS pct_drop_from_peak
FROM inst_peak_vs_recent
WHERE peak_intl_headcount > 0
ORDER BY pct_drop_from_peak ASC;

-- Query 7: Domestic vs. International Student Headcount
-- Compares Domestic vs. International Student Headcount for BC Postsecondary institutions.
SELECT 
    fiscal_year,
    student_type,
    SUM(headcount) AS total_headcount
FROM fact_student_headcount
WHERE student_type IN ('Domestic', 'International')
GROUP BY fiscal_year, student_type
ORDER BY fiscal_year, student_type;


-- Query 8: Institution International Student Headcount Change from 2023/2024 to 2024/2025
-- Examines International Student Headcount at each institution.
WITH intl_by_inst AS (
    SELECT 
        i.institution_name,
        f.fiscal_year,
        SUM(f.headcount) AS intl_headcount
    FROM fact_student_headcount f
    JOIN dim_institution i ON f.institution_id = i.institution_id
    WHERE f.student_type = 'International'
      AND f.fiscal_year IN ('2023/2024', '2024/2025')
    GROUP BY i.institution_name, f.fiscal_year
)
SELECT 
    institution_name,
    SUM(CASE WHEN fiscal_year = '2023/2024' THEN intl_headcount ELSE 0 END) AS hc_2023_24,
    SUM(CASE WHEN fiscal_year = '2024/2025' THEN intl_headcount ELSE 0 END) AS hc_2024_25,
    SUM(CASE WHEN fiscal_year = '2024/2025' THEN intl_headcount ELSE 0 END) - 
    SUM(CASE WHEN fiscal_year = '2023/2024' THEN intl_headcount ELSE 0 END) AS net_change
FROM intl_by_inst
GROUP BY institution_name
ORDER BY net_change ASC;