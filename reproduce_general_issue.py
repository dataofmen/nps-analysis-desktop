
import sys
import os
import pandas as pd

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

import data_processing

file_path = '/Users/hmkwon/Project/NPS_DP/input_data/commerce/commerce_nps_2511_rgn12.csv'

print(f"Loading {file_path} using data_processing.load_qualtrics_data...")
with open(file_path, 'rb') as f:
    file_content = f.read()

try:
    df = data_processing.load_qualtrics_data(file_content, os.path.basename(file_path))
    print(f"✅ Loaded {len(df)} rows.")
    
    if len(df) == 3428:
        print("SUCCESS: Row count matches expected (3428).")
    else:
        print(f"FAILURE: Row count mismatch. Expected 3428, got {len(df)}.")
        
except Exception as e:
    print(f"Error: {e}")
