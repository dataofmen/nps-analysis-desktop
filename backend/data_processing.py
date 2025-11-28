import pandas as pd
import io

def load_file(file_content: bytes, filename: str) -> pd.DataFrame:
    if filename.endswith('.csv'):
        return pd.read_csv(io.BytesIO(file_content))
    elif filename.endswith('.xlsx') or filename.endswith('.xls'):
        return pd.read_excel(io.BytesIO(file_content))
    else:
        raise ValueError("Unsupported file format")

def load_qualtrics_data(file_content: bytes, filename: str) -> pd.DataFrame:
    df = load_file(file_content, filename)
    # Qualtrics standard export often has 3 header rows.
    # Row 0: Column Names (e.g. Q1, Q2)
    # Row 1: Question Text
    # Row 2: Import Tags
    # We want to keep Row 0 as header.
    # We should remove Row 1 and 2 if they look like metadata.
    
    # Heuristic: Check if 'ResponseId' is in columns.
    # If so, check if the first row values for 'ResponseId' are not actual IDs (e.g. they are descriptions).
    if 'ResponseId' in df.columns:
        # If the first value in ResponseId column is not a typical ID (e.g. it contains spaces or is 'Response ID'), drop it.
        # Actually, Qualtrics 2nd and 3rd rows usually have specific content.
        # Row 2 (index 0) often has "Start Date" description.
        # Row 3 (index 1) often has "{"ImportId":...}"
        
        # Let's just drop the first 2 rows if the dataframe is large enough.
        if len(df) > 2:
             # Check if row 0 contains "Start Date" or similar metadata text in some columns
             # This is a simple heuristic.
             df = df.iloc[2:].reset_index(drop=True)
    return df

def merge_data(qualtrics_df: pd.DataFrame, coding_df: pd.DataFrame) -> pd.DataFrame:
    if coding_df is None or coding_df.empty:
        return qualtrics_df
        
    # Attempt to find a common key. 'ResponseId' is standard.
    key = 'ResponseId'
    if key in qualtrics_df.columns and key in coding_df.columns:
        # Identify columns in coding_df that are already in qualtrics_df (excluding key)
        common_cols = [c for c in coding_df.columns if c in qualtrics_df.columns and c != key]
        
        # Drop these common columns from coding_df before merging to avoid suffixes
        coding_df_clean = coding_df.drop(columns=common_cols)
        
        return pd.merge(qualtrics_df, coding_df_clean, on=key, how='left')
    
    return qualtrics_df

# New functions for food dataset

def load_food_nps_data(file_content: bytes, filename: str) -> pd.DataFrame:
    """Load food NPS survey data CSV."""
    df = load_file(file_content, filename)
    # Ensure required columns exist
    required = {'ResponseId', 'Q1_1', 'gender', 'age_group', 'rgn_nm', 'bmclub'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in food NPS data: {missing}")
    return df

def load_food_population(file_content: bytes, filename: str) -> pd.DataFrame:
    """Load food population weighting file CSV."""
    df = load_file(file_content, filename)
    required = {'gender', 'age_group', 'rgn_nm', 'bmclub', 'mem_rate'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in population data: {missing}")
    return df

