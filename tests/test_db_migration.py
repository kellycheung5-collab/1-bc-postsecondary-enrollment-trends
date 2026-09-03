import pytest
import pandas as pd
from sqlalchemy import create_engine, inspect, text
import importlib

# Dynamically import module with numbers in filename
db_migration = importlib.import_module("scripts.03_db_migration")

create_tables = db_migration.create_tables
run_migration = db_migration.run_migration

@pytest.fixture
def test_engine(tmp_path, monkeypatch):
    """Sets up an isolated SQLite database and mock CSV files in a temp folder."""
    db_file = tmp_path / "test_enrollment.db"
    engine = create_engine(f"sqlite:///{db_file}")

    processed_dir = tmp_path / "data" / "processed"
    processed_dir.mkdir(parents=True)

    # Create mock clean CSVs
    pd.DataFrame({
        "Fiscal Year": ["2022/2023"],
        "Institution": ["University of British Columbia"],
        "FTE Actual": [28450.5]
    }).to_csv(processed_dir / "clean-fte-actual.csv", index=False)

    pd.DataFrame({
        "Fiscal Year": ["2022/2023"],
        "Institution": ["University of British Columbia"],
        "FTE Target": [28000.0]
    }).to_csv(processed_dir / "clean-fte-target.csv", index=False)

    pd.DataFrame({
        "Fiscal Year": ["2022/2023"],
        "Institution": ["University of British Columbia"],
        "Operating Grant": [112235228.0]
    }).to_csv(processed_dir / "clean-operating-grants.csv", index=False)

    pd.DataFrame({
        "Fiscal Year": ["2022/2023"],
        "Institution": ["University of British Columbia"],
        "Economic Development Region": ["Mainland/Southwest"],
        "International/Domestic": ["Domestic"],
        "Headcount": [12500]
    }).to_csv(processed_dir / "clean-student-headcount.csv", index=False)

    # Patch working path references inside run_migration
    monkeypatch.chdir(tmp_path)

    return engine


class TestDatabaseMigration:
    """Integration tests for DDL setup and migration pipeline."""

    def test_create_tables(self, test_engine):
        """Verifies that all dimension and fact tables are created."""
        create_tables(test_engine)
        inspector = inspect(test_engine)
        tables = inspector.get_table_names()

        expected_tables = {
            "dim_fiscal_year",
            "dim_institution",
            "dim_region",
            "fact_institution_financials_fte",
            "fact_student_headcount"
        }
        assert expected_tables.issubset(set(tables))

    def test_run_migration_populates_tables(self, test_engine):
        """Verifies dimension mapping and fact table insertion."""
        create_tables(test_engine)
        run_migration(test_engine)

        with test_engine.connect() as conn:
            # Check dimension tables
            inst_count = conn.execute(text("SELECT COUNT(*) FROM dim_institution;")).scalar()
            region_count = conn.execute(text("SELECT COUNT(*) FROM dim_region;")).scalar()
            assert inst_count == 1
            assert region_count == 1

            # Check fact tables
            fin_fact_count = conn.execute(text("SELECT COUNT(*) FROM fact_institution_financials_fte;")).scalar()
            hc_fact_count = conn.execute(text("SELECT COUNT(*) FROM fact_student_headcount;")).scalar()
            assert fin_fact_count == 1
            assert hc_fact_count == 1