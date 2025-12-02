import pandas as pd
import sys

file_path = '/Users/hmkwon/Project/NPS_DP/commerce/commerce_nps_2511_rgn_clean.csv'

try:
    print(f"Generating statistics for: {file_path}\n")
    df = pd.read_csv(file_path)
    
    for col in df.columns:
        print(f"--- Variable: {col} ---")
        print(df[col].value_counts(dropna=False).sort_index())
        print("\n")
        
except Exception as e:
    print(f"ERROR: {e}")
