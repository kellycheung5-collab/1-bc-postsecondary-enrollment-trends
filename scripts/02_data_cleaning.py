import os
import pandas as pd

# Define paths relative to repository root
RAW_DIR = os.path.join("data", "raw")
PROCESSED_DIR = os.path.join("data", "processed")

# Ensure output directory exists
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Load institution mapping reference
mapping_path = os.path.join(RAW_DIR, "institution_mapping.csv")
df_mapping = pd.read_csv(mapping_path)
INSTITUTION_MAP = dict(
    zip(df_mapping["abbrev_or_raw"].str.strip(), df_mapping["canonical_name"].str.strip())
)


def clean_currency_and_float(series: pd.Series) -> pd.Series:
    """Removes currency symbols and commas, converting to float64. Some FTE numbers are decima;"""
    return (
        series.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .astype("float64")
    )


def clean_fte_actual() -> pd.DataFrame:
    """Cleans actual FTE enrollments dataset."""
    file_path = os.path.join(RAW_DIR, "fte-enrollments-actual.csv")
    df = pd.read_csv(file_path)

    # 1. Drop trailing unnamed columns
    unnamed_cols = [c for c in df.columns if "Unnamed" in c]
    df = df.drop(columns=unnamed_cols)

    # 2. Strip whitespace
    df["Fiscal Year"] = df["Fiscal Year"].astype(str).str.strip()
    df["Institution"] = df["Institution"].astype(str).str.strip()

    # 3. Map canonical institution names
    df["Institution"] = df["Institution"].replace(INSTITUTION_MAP)

    # 4. Clean numeric types
    df["FTE Actual"] = clean_currency_and_float(df["FTE Actual"])

    return df


def clean_fte_target() -> pd.DataFrame:
    """Cleans target FTE enrollments dataset."""
    file_path = os.path.join(RAW_DIR, "fte-enrollments-target.csv")
    df = pd.read_csv(file_path)

    # 1. Drop trailing unnamed columns
    unnamed_cols = [c for c in df.columns if "Unnamed" in c]
    df = df.drop(columns=unnamed_cols)

    # 2. Strip whitespace
    df["Fiscal Year"] = df["Fiscal Year"].astype(str).str.strip()
    df["Institution"] = df["Institution"].astype(str).str.strip()

    # 3. Map canonical institution names
    df["Institution"] = df["Institution"].replace(INSTITUTION_MAP)

    # 4. Clean numeric types
    df["FTE Target"] = clean_currency_and_float(df["FTE Target"])

    return df


def clean_operating_grants() -> pd.DataFrame:
    """Cleans operating grants dataset."""
    file_path = os.path.join(RAW_DIR, "operating-grants.csv")
    df = pd.read_csv(file_path)

    # 1. Strip whitespace
    df["Fiscal Year"] = df["Fiscal Year"].astype(str).str.strip()
    df["Institution"] = df["Institution"].astype(str).str.strip()

    # 2. Map canonical institution names
    df["Institution"] = df["Institution"].replace(INSTITUTION_MAP)

    # 3. Clean numeric types
    df["Operating Grant"] = clean_currency_and_float(df["Operating Grant"])

    return df


def clean_student_headcount() -> pd.DataFrame:
    """Cleans student headcount by region dataset."""
    file_path = os.path.join(RAW_DIR, "student-headcount-by-region.csv")
    df = pd.read_csv(file_path)

    # Rename Academic Year (or Year) to Fiscal Year
    df = df.rename(columns={"Academic Year": "Fiscal Year"})

    # 1. Strip whitespace
    df["Fiscal Year"] = df["Fiscal Year"].astype(str).str.strip()
    df["Institution"] = df["Institution"].astype(str).str.strip()
    df["Economic Development Region"] = df["Economic Development Region"].astype(str).str.strip()
    df["International/Domestic"] = df["International/Domestic"].astype(str).str.strip().str.title()

    # 2. Map canonical institution names
    df["Institution"] = df["Institution"].replace(INSTITUTION_MAP)

    # 3. Convert Headcount to numeric (coercing '*' and missing values to NaN)
    df["Headcount"] = pd.to_numeric(df["Headcount"], errors="coerce")

    # 4. Drop suppressed/missing records so processed CSV only contains valid integers
    df = df.dropna(subset=["Headcount"])
    df["Headcount"] = df["Headcount"].astype(int)

    return df


def main():
    print("Starting data cleaning pipeline")

    df_actual = clean_fte_actual()
    df_actual.to_csv(
        os.path.join(PROCESSED_DIR, "clean-fte-actual.csv"), index=False
    )
    print("Saved clean-fte-actual.csv")

    df_target = clean_fte_target()
    df_target.to_csv(
        os.path.join(PROCESSED_DIR, "clean-fte-target.csv"), index=False
    )
    print("Saved clean-fte-target.csv")

    df_grants = clean_operating_grants()
    df_grants.to_csv(
        os.path.join(PROCESSED_DIR, "clean-operating-grants.csv"), index=False
    )
    print("Saved clean-operating-grants.csv")

    df_headcount = clean_student_headcount()
    df_headcount.to_csv(
        os.path.join(PROCESSED_DIR, "clean-student-headcount.csv"), index=False
    )
    print("Saved clean-student-headcount.csv")

    print("Data cleaning pipeline executed successfully")


if __name__ == "__main__":
    main()