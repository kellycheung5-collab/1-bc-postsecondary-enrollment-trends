import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

# Save directly to data/processed/enrollment.db
DB_PATH = "sqlite:///data/processed/enrollment.db"
engine = create_engine(DB_PATH)

# Define Relational Schema (DDL)
DDL_SCHEMA = """
-- Dimension Table: Fiscal Years
CREATE TABLE IF NOT EXISTS dim_fiscal_year (
    fiscal_year TEXT PRIMARY KEY
);

-- Dimension Table: Institutions
CREATE TABLE IF NOT EXISTS dim_institution (
    institution_id INTEGER PRIMARY KEY AUTOINCREMENT,
    institution_name TEXT NOT NULL UNIQUE
);

-- Dimension Table: Regions
CREATE TABLE IF NOT EXISTS dim_region (
    region_id INTEGER PRIMARY KEY AUTOINCREMENT,
    region_name TEXT NOT NULL UNIQUE
);

-- Fact Table: Institutional Financials & FTE Metrics
CREATE TABLE IF NOT EXISTS fact_institution_financials_fte (
    financial_fte_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fiscal_year TEXT NOT NULL,
    institution_id INTEGER NOT NULL,
    fte_actual REAL,
    fte_target REAL,
    operating_grant INTEGER,
    FOREIGN KEY (fiscal_year) REFERENCES dim_fiscal_year(fiscal_year),
    FOREIGN KEY (institution_id) REFERENCES dim_institution(institution_id),
    UNIQUE (fiscal_year, institution_id)
);

-- Fact Table: Student Headcount Demographics
CREATE TABLE IF NOT EXISTS fact_student_headcount (
    headcount_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fiscal_year TEXT NOT NULL,
    institution_id INTEGER NOT NULL,
    region_id INTEGER NOT NULL,
    student_type TEXT NOT NULL,
    headcount INTEGER NOT NULL,
    FOREIGN KEY (fiscal_year) REFERENCES dim_fiscal_year(fiscal_year),
    FOREIGN KEY (institution_id) REFERENCES dim_institution(institution_id),
    FOREIGN KEY (region_id) REFERENCES dim_region(region_id)
);
"""

def create_tables(engine):
    """Executes DDL statements to create database structure."""
    with engine.begin() as conn:
        for statement in DDL_SCHEMA.strip().split(";"):
            if statement.strip():
                conn.execute(text(statement))

def run_migration(engine):
    """Loads cleaned processed files and populates dimension and fact tables."""

    # Read processed datasets from data/processed/
    fte_actual = pd.read_csv("data/processed/clean-fte-actual.csv")
    fte_target = pd.read_csv("data/processed/clean-fte-target.csv")
    operating_grants = pd.read_csv("data/processed/clean-operating-grants.csv")
    student_headcount = pd.read_csv("data/processed/clean-student-headcount.csv")

    # Extract unique values for Dimension Tables
    fiscal_years = pd.DataFrame(
        {"fiscal_year": sorted(student_headcount["Fiscal Year"].unique())}
    )
    
    institutions = pd.DataFrame(
        {"institution_name": sorted(
            set(fte_actual["Institution"])
            .union(set(fte_target["Institution"]))
            .union(set(operating_grants["Institution"]))
            .union(set(student_headcount["Institution"]))
        )}
    )
    
    regions = pd.DataFrame(
        {"region_name": sorted(student_headcount["Economic Development Region"].unique())}
    )

    # Populate Dimension Tables
    with engine.begin() as conn:
        fiscal_years.to_sql("dim_fiscal_year", conn, if_exists="append", index=False)
        institutions.to_sql("dim_institution", conn, if_exists="append", index=False)
        regions.to_sql("dim_region", conn, if_exists="append", index=False)

    # Fetch surrogate keys for mapping
    inst_map = pd.read_sql("SELECT institution_name, institution_id FROM dim_institution", engine)
    region_map = pd.read_sql("SELECT region_name, region_id FROM dim_region", engine)

    # Prepare Financial & FTE Fact Table
    fin_fte_df = fte_actual.merge(
        fte_target, on=["Fiscal Year", "Institution"], how="inner"
    ).merge(
        operating_grants, on=["Fiscal Year", "Institution"], how="inner"
    )

    fin_fte_df = fin_fte_df.merge(
        inst_map, left_on="Institution", right_on="institution_name", how="inner"
    )
    
    fin_fte_fact = fin_fte_df[[
        "Fiscal Year", "institution_id", "FTE Actual", "FTE Target", "Operating Grant"
    ]].rename(columns={
        "Fiscal Year": "fiscal_year",
        "FTE Actual": "fte_actual",
        "FTE Target": "fte_target",
        "Operating Grant": "operating_grant"
    })

    # Prepare Student Headcount Fact Table
    hc_df = student_headcount.merge(
        inst_map, left_on="Institution", right_on="institution_name", how="inner"
    ).merge(
        region_map, left_on="Economic Development Region", right_on="region_name", how="inner"
    )

    hc_fact = hc_df[[
        "Fiscal Year", "institution_id", "region_id", "International/Domestic", "Headcount"
    ]].rename(columns={
        "Fiscal Year": "fiscal_year",
        "International/Domestic": "student_type",
        "Headcount": "headcount"
    })

    # Load Fact Tables
    with engine.begin() as conn:
        fin_fte_fact.to_sql("fact_institution_financials_fte", conn, if_exists="append", index=False)
        hc_fact.to_sql("fact_student_headcount", conn, if_exists="append", index=False)

if __name__ == "__main__":
    create_tables(engine)
    run_migration(engine)