import pandas as pd
import io
import chardet
from io import BytesIO

file_path = '/Users/hmkwon/Project/NPS_DP/input_data/commerce/commerce_nps_2511_rgn.csv'

print(f"Loading {file_path}...")
with open(file_path, 'rb') as f:
    file_content = f.read()

# Detect encoding
detected = chardet.detect(file_content)
encoding = detected['encoding'] or 'utf-8'
print(f"Detected encoding: {encoding}")

# Try UTF-8-BOM first
try:
    df = pd.read_csv(BytesIO(file_content), encoding='utf-8-sig')
    print("Used encoding: utf-8-sig")
except:
    df = pd.read_csv(BytesIO(file_content), encoding=encoding)
    print(f"Used encoding: {encoding}")

print(f"Initial rows (pandas read): {len(df)}")

# Simulate Metadata Removal Logic
print("\n--- Checking Metadata Removal Logic ---")
if len(df) > 2:
    first_row = df.iloc[0].astype(str).values
    second_row = df.iloc[1].astype(str).values
    print(f"First row values (first 5): {first_row[:5]}")
    print(f"Second row values (first 5): {second_row[:5]}")
    
    is_question_text = any(v in ['Start Date', 'End Date', 'Response Type'] for v in first_row[:10])
    is_import_id = any('{"ImportId":' in str(v) for v in second_row[:10])
    
    if is_question_text or is_import_id:
        print(f"❌ Metadata removal TRIGGERED. QuestionText: {is_question_text}, ImportId: {is_import_id}")
        df_removed = df.iloc[2:].reset_index(drop=True)
        print(f"Rows after metadata removal: {len(df_removed)}")
    else:
        print("✅ Metadata removal NOT triggered")
        df_removed = df

# Simulate NPS Filtering Logic
print("\n--- Checking NPS Filtering Logic ---")
# Handle Q1 alias
if 'Q1' in df_removed.columns and 'Q1_1' not in df_removed.columns:
    df_removed.rename(columns={'Q1': 'Q1_1'}, inplace=True)

if 'Q1_1' not in df_removed.columns:
    print("CRITICAL: Q1_1 column missing!")
else:
    df_removed['Q1_1'] = pd.to_numeric(df_removed['Q1_1'], errors='coerce')
    
    invalid_nps = df_removed[~((df_removed['Q1_1'].notna()) & (df_removed['Q1_1'] >= 0) & (df_removed['Q1_1'] <= 10))]
    if not invalid_nps.empty:
        print(f"❌ Found {len(invalid_nps)} rows with invalid NPS scores:")
        print(invalid_nps[['ResponseId', 'Q1_1']].head())
    else:
        print("✅ No rows with invalid NPS scores found")

    df_final = df_removed[df_removed['Q1_1'].notna() & (df_removed['Q1_1'] >= 0) & (df_removed['Q1_1'] <= 10)]
    print(f"Final rows: {len(df_final)}")
