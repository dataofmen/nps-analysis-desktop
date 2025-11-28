import pandas as pd
import sys
import os

# Add current directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from weighting import calculate_weights
from analysis import calculate_nps

def verify_fix():
    print("Loading data...")
    # Load Survey Data
    nps_df = pd.read_csv('validate/commerce_nps_data.csv')
    
    # Load Population Data
    pop_df = pd.read_csv('validate/commerce_population.csv')
    
    print(f"Survey Data: {len(nps_df)} rows")
    print(f"Population Data: {len(pop_df)} rows")
    
    # Prepare Targets
    # Group by gender and age_group and sum mem_rate
    # Note: mem_rate is string in CSV, need to convert to float
    pop_df['mem_rate'] = pd.to_numeric(pop_df['mem_rate'], errors='coerce')
    
    # Normalize keys in population data (remove spaces) - mimicking backend logic
    # But wait, the backend logic does this inside preview_segments.
    # Here we are manually constructing targets to pass to calculate_weights.
    # So we should normalize them here to match what the backend would produce.
    pop_df['gender'] = pop_df['gender'].astype(str).str.replace(" ", "")
    pop_df['age_group'] = pop_df['age_group'].astype(str).str.replace(" ", "")
    
    # Create segment key
    pop_df['Segment'] = pop_df['gender'] + "_" + pop_df['age_group']
    
    # Sum mem_rate by segment
    # mem_rate is percentage (0-100), convert to proportion (0-1)
    target_series = pop_df.groupby('Segment')['mem_rate'].sum() / 100.0
    targets = target_series.to_dict()
    
    print(f"Created {len(targets)} targets.")
    print(f"Target Sum: {target_series.sum()}")
    print("Sample Targets:", list(targets.items())[:3])
    
    # Filter Survey Data (Match User Script Logic)
    print("Filtering survey data (dropping NaNs in gender/age_group)...")
    initial_len = len(nps_df)
    nps_df = nps_df.dropna(subset=['gender', 'age_group'])
    print(f"Dropped {initial_len - len(nps_df)} rows. Remaining: {len(nps_df)}")
    
    # Check Q1 Parsing
    nps_df['Q1_numeric'] = pd.to_numeric(nps_df['Q1'], errors='coerce')
    q1_nans = nps_df['Q1_numeric'].isna().sum()
    print(f"Q1 NaNs after to_numeric: {q1_nans}")
    
    # Calculate Weights
    print("Calculating weights...")
    weighted_df = calculate_weights(nps_df, ['gender', 'age_group'], targets)
    
    # Calculate NPS Components manually to compare
    valid_df = weighted_df.dropna(subset=['Q1'])
    # Ensure Q1 is numeric
    valid_df['Q1'] = pd.to_numeric(valid_df['Q1'], errors='coerce')
    
    promoters = valid_df[valid_df['Q1'] >= 9]
    detractors = valid_df[valid_df['Q1'] <= 6]
    passives = valid_df[(valid_df['Q1'] >= 7) & (valid_df['Q1'] <= 8)]
    
    total_weight = valid_df['Weight'].sum()
    prom_weight = promoters['Weight'].sum()
    det_weight = detractors['Weight'].sum()
    
    print(f"Total Weight: {total_weight}")
    print(f"Promoter Weight: {prom_weight}")
    print(f"Detractor Weight: {det_weight}")
    
    nps_manual = ((prom_weight - det_weight) / total_weight) * 100
    print(f"Manual Weighted NPS: {nps_manual}")
    
    # Calculate NPS using backend function
    print("Calculating NPS via backend function...")
    nps = calculate_nps(weighted_df, 'Q1', 'Weight')
    
    print(f"\nCalculated NPS: {nps}")
    print(f"Expected NPS: 30.96")
    
    diff = abs(nps - 30.96)
    print(f"Difference: {diff:.4f}")
    
    if diff < 0.1:
        print("SUCCESS: Result matches expected value!")
    else:
        print("WARNING: Result still differs significantly.")

if __name__ == "__main__":
    verify_fix()
