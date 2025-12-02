import pandas as pd
import os

files_to_clean = [
    '/Users/hmkwon/Project/NPS_DP/food/food_nps_2511_rgn.csv',
    '/Users/hmkwon/Project/NPS_DP/food/food_nps_2511_rgn12.csv',
    '/Users/hmkwon/Project/NPS_DP/commerce/commerce_nps_2511_rgn.csv',
    '/Users/hmkwon/Project/NPS_DP/commerce/commerce_nps_2511_rgn12.csv'
]

columns_to_check = ['gender', 'age_group', 'rgn_nm', 'bmclub']

print("Starting data cleaning process...\n")

for file_path in files_to_clean:
    try:
        print(f"Processing: {file_path}")
        df = pd.read_csv(file_path)
        
        initial_rows = len(df)
        
        # Determine which columns to check
        current_check_cols = []
        for col in columns_to_check:
            if col == 'rgn_nm':
                if 'rgn_nm' in df.columns:
                    current_check_cols.append('rgn_nm')
                elif 'rgn1_nm' in df.columns and 'rgn2_nm' in df.columns:
                    current_check_cols.extend(['rgn1_nm', 'rgn2_nm'])
                else:
                    print(f"  WARNING: Could not find region column (rgn_nm or rgn1_nm/rgn2_nm) in {file_path}. Skipping...")
                    current_check_cols = []
                    break
            else:
                if col in df.columns:
                    current_check_cols.append(col)
                else:
                    print(f"  WARNING: Missing column {col} in {file_path}. Skipping...")
                    current_check_cols = []
                    break
        
        if not current_check_cols:
            continue
            
        # Drop rows with nulls in specific columns
        df_clean = df.dropna(subset=current_check_cols)
        
        final_rows = len(df_clean)
        dropped_rows = initial_rows - final_rows
        
        # Save to new file
        base, ext = os.path.splitext(file_path)
        output_path = f"{base}_clean{ext}"
        df_clean.to_csv(output_path, index=False)
        
        print(f"  Columns checked: {current_check_cols}")
        print(f"  Original rows: {initial_rows}")
        print(f"  Cleaned rows:  {final_rows}")
        print(f"  Dropped rows:  {dropped_rows}")
        print(f"  Saved to: {output_path}\n")
        
    except Exception as e:
        print(f"  ERROR processing {file_path}: {e}\n")

print("Data cleaning complete.")
