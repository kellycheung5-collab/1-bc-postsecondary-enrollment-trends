import pandas as pd
import importlib

# Dynamically import module with numbers in filename
data_cleaning = importlib.import_module("scripts.02_data_cleaning")

# Extract functions from the imported module
clean_currency_and_float = data_cleaning.clean_currency_and_float
clean_student_headcount = data_cleaning.clean_student_headcount

class TestCleaningHelpers:
    """Unit tests for cleaning helper functions."""

    def test_clean_currency_and_float_stripping(self):
        """Validates removal of dollar signs, commas, and trailing whitespace."""
        s = pd.Series(["$112,235,228", " 477.6 ", "$1,234.56"])
        result = clean_currency_and_float(s)
        expected = pd.Series([112235228.0, 477.6, 1234.56], dtype="float64")
        pd.testing.assert_series_equal(result, expected)


class TestHeadcountCleaning:
    """Unit tests for clean_student_headcount logic using mock files."""

    def test_student_headcount_suppressed_values_dropped(self, tmp_path, monkeypatch):
        """Ensures asterisk '*' suppressed records are dropped and non-null values converted to int."""
        raw_dir = tmp_path / "data" / "raw"
        raw_dir.mkdir(parents=True)

        # Mock institution mapping file
        mapping_csv = raw_dir / "institution_mapping.csv"
        pd.DataFrame({
            "abbrev_or_raw": ["UBC"],
            "canonical_name": ["University of British Columbia"]
        }).to_csv(mapping_csv, index=False)

        # Mock student headcount raw CSV containing suppressed '*' values
        headcount_csv = raw_dir / "student-headcount-by-region.csv"
        pd.DataFrame({
            "Academic Year": ["2022/2023", "2022/2023"],
            "Institution": ["UBC ", "UBC"],
            "Economic Development Region": ["Mainland/Southwest ", "Mainland/Southwest"],
            "International/Domestic": ["DOMESTIC", "INTERNATIONAL"],
            "Headcount": ["12500", "*"]
        }).to_csv(headcount_csv, index=False)

        # Patch RAW_DIR path inside script module
        #monkeypatch.setattr("scripts.02_data_cleaning.RAW_DIR", str(raw_dir))
        monkeypatch.setattr(data_cleaning, "RAW_DIR", str(raw_dir))
        #monkeypatch.setattr("scripts.02_data_cleaning.INSTITUTION_MAP", {"UBC": "University of British Columbia"})
        monkeypatch.setattr(data_cleaning, "INSTITUTION_MAP", {"UBC": "University of British Columbia"})

        cleaned_df = clean_student_headcount()

        # Asterisk record dropped -> 1 record remaining
        assert len(cleaned_df) == 1
        assert cleaned_df["Fiscal Year"].iloc[0] == "2022/2023"
        assert cleaned_df["Institution"].iloc[0] == "University of British Columbia"
        assert cleaned_df["International/Domestic"].iloc[0] == "Domestic"
        assert cleaned_df["Headcount"].dtype == "int64"
        assert cleaned_df["Headcount"].iloc[0] == 12500