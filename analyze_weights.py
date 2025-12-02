
import pandas as pd
import numpy as np
import sys
import os

# Add backend to path to use existing logic
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from food_nps import load_food_qualtrics_data, load_food_population_data, calculate_food_nps_with_weighting

def analyze_weights():
    # Paths
    nps_file = 'input_data/food/food_nps_2511_rgn.csv'
    pop_file = 'input_data/food/food_population_2511_rgn.csv'
    
    print(f"Loading NPS data from {nps_file}...")
    with open(nps_file, 'rb') as f:
        nps_content = f.read()
    qualtrics_df = load_food_qualtrics_data(nps_content, 'food_nps.csv')
    
    print(f"Loading Population data from {pop_file}...")
    with open(pop_file, 'rb') as f:
        pop_content = f.read()
    population_df = load_food_population_data(pop_content, 'food_pop.csv')
    
    # We need to replicate the merge logic from calculate_food_nps_with_weighting
    # to get the dataframe with weights BEFORE it gets aggregated.
    
    # Merge logic from food_nps.py
    merge_cols = ['gender', 'age_group', 'rgn_nm', 'bmclub']
    if 'division' in qualtrics_df.columns and 'division' in population_df.columns:
        merge_cols.append('division')
    if 'is_mfo' in qualtrics_df.columns and 'is_mfo' in population_df.columns:
        qualtrics_df['is_mfo'] = qualtrics_df['is_mfo'].astype(str)
        population_df['is_mfo'] = population_df['is_mfo'].astype(str)
        merge_cols.append('is_mfo')
        
    # Apply mappings to fix mismatches
    if 'division' in qualtrics_df.columns:
        qualtrics_df['division'] = qualtrics_df['division'].replace({'PICKUP': 'TAKEOUT'})
        
    if 'is_mfo' in qualtrics_df.columns:
        print(f"DEBUG: is_mfo unique values before replace: {qualtrics_df['is_mfo'].unique()}")
        qualtrics_df['is_mfo'] = qualtrics_df['is_mfo'].replace({
            '한그룻주문경험O': '1',
            '한그룻주문경험X': '0'
        })
        print(f"DEBUG: is_mfo unique values after replace: {qualtrics_df['is_mfo'].unique()}")

    print(f"Merge columns: {merge_cols}")

    # Normalize whitespace
    for col in merge_cols:
        qualtrics_df[col] = qualtrics_df[col].astype(str).str.replace(" ", "")
        population_df[col] = population_df[col].astype(str).str.replace(" ", "")

    # Check for NaNs before merge
    print("\n--- NaN Check (Qualtrics) ---")
    print(qualtrics_df[merge_cols].isna().sum())
    
    # Apply mappings AFTER normalization
    if 'division' in qualtrics_df.columns:
        qualtrics_df['division'] = qualtrics_df['division'].replace({'PICKUP': 'TAKEOUT'})
        
    if 'is_mfo' in qualtrics_df.columns:
        print(f"DEBUG: is_mfo unique values (normalized): {qualtrics_df['is_mfo'].unique()}")
        qualtrics_df['is_mfo'] = qualtrics_df['is_mfo'].replace({
            '한그룻주문경험O': '1',
            '한그룻주문경험X': '0'
        })
        
    # Check for mismatches
    for col in merge_cols:
        print(f"\n--- Column: {col} ---")
        q_vals = sorted(qualtrics_df[col].unique())
        p_vals = sorted(population_df[col].unique())
        print(f"Qualtrics ({len(q_vals)}): {q_vals[:10]} ...")
        print(f"Population ({len(p_vals)}): {p_vals[:10]} ...")
        
        common = set(q_vals) & set(p_vals)
        print(f"Common values: {len(common)}")
        if len(common) < len(q_vals):
            missing = set(q_vals) - set(p_vals)
            print(f"Missing in Population (First 5): {list(missing)[:5]}")

    merged_df = qualtrics_df.merge(
        population_df[merge_cols + ['mem_rate']],
        on=merge_cols,
        how='left'
    )
    
    # Calculate sample counts
    segment_counts = merged_df.groupby(merge_cols).size().reset_index(name='sample_count')
    merged_df = merged_df.merge(segment_counts, on=merge_cols, how='left')
    
    # Calculate raw weight
    merged_df['weight'] = merged_df['mem_rate'] / merged_df['sample_count']
    merged_df['weight'] = merged_df['weight'].fillna(1.0) # Fallback
    
    # Normalize
    unweighted_total = len(merged_df)
    weighted_total = merged_df['weight'].sum()
    scale_factor = unweighted_total / weighted_total if weighted_total > 0 else 1.0
    merged_df['normalized_weight'] = merged_df['weight'] * scale_factor
    
    # Analysis
    weights = merged_df['normalized_weight']
    
    print("\n--- Weight Statistics ---")
    print(f"Count: {len(weights)}")
    print(f"Min: {weights.min():.4f}")
    print(f"Max: {weights.max():.4f}")
    print(f"Mean: {weights.mean():.4f}")
    print(f"Median: {weights.median():.4f}")
    print(f"Std Dev: {weights.std():.4f}")
    
    # Percentiles
    print(f"1st Percentile: {np.percentile(weights, 1):.4f}")
    print(f"5th Percentile: {np.percentile(weights, 5):.4f}")
    print(f"95th Percentile: {np.percentile(weights, 95):.4f}")
    print(f"99th Percentile: {np.percentile(weights, 99):.4f}")
    
    # Design Effect (Deff) = 1 + CV^2
    cv = weights.std() / weights.mean()
    deff = 1 + cv**2
    print(f"Design Effect (Deff): {deff:.4f}")
    print(f"Effective Sample Size (n_eff): {len(weights)/deff:.2f}")
    
    # Identify Extreme Weights
    high_threshold = 3.0
    low_threshold = 0.3
    
    high_weights = merged_df[merged_df['normalized_weight'] > high_threshold]
    low_weights = merged_df[merged_df['normalized_weight'] < low_threshold]
    
    print(f"\n--- Extreme Weights ---")
    print(f"Rows with weight > {high_threshold}: {len(high_weights)} ({len(high_weights)/len(merged_df)*100:.2f}%)")
    print(f"Rows with weight < {low_threshold}: {len(low_weights)} ({len(low_weights)/len(merged_df)*100:.2f}%)")
    
    if not high_weights.empty:
        print("\nTop 5 Segments with High Weights:")
        cols_to_show = merge_cols + ['sample_count', 'mem_rate', 'normalized_weight']
        print(high_weights[cols_to_show].drop_duplicates().sort_values('normalized_weight', ascending=False).head(5))

    if not low_weights.empty:
        print("\nTop 5 Segments with Low Weights:")
        cols_to_show = merge_cols + ['sample_count', 'mem_rate', 'normalized_weight']
        print(low_weights[cols_to_show].drop_duplicates().sort_values('normalized_weight', ascending=True).head(5))

if __name__ == "__main__":
    analyze_weights()
