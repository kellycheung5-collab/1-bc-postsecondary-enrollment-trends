import pandas as pd

# Load unique institution strings from raw files
headcount_insts = pd.read_csv('data/raw/student-headcount-by-region.csv')['Institution'].str.strip().dropna().unique()

# Write unique names to a draft CSV seed file
df_seed = pd.DataFrame({'abbrev_or_raw': headcount_insts, 'canonical_name': ''})
df_seed.to_csv('data/raw/institution_mapping_draft.csv', index=False)