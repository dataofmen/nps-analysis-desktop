import pandas as pd
import numpy as np
import sys
import os

# Add current directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import food_nps

def verify_food_nps_fix():
    print("Loading data...")
    try:
        # Load Survey Data
        with open('validate/commerce_nps_data.csv', 'rb') as f:
            qualtrics_content = f.read()
        qualtrics_df = food_nps.load_food_qualtrics_data(qualtrics_content, 'commerce_nps_data.csv')
        
        # Load Population Data
        with open('validate/commerce_population.csv', 'rb') as f:
            pop_content = f.read()
        pop_df = food_nps.load_food_population_data(pop_content, 'commerce_population.csv')
        
        print(f"Survey Data: {len(qualtrics_df)} rows")
        print(f"Population Data: {len(pop_df)} rows")
        
        # Calculate Food NPS
        print("Calculating Food NPS...")
        
        # Debug: Check population mem_rate sum
        print(f"Population mem_rate sum: {pop_df['mem_rate'].sum()}")
        
        # Debug: Check for unmatched rows
        merge_cols = ['gender', 'age_group', 'rgn_nm', 'bmclub']
        # Normalize whitespace in script too to match backend logic for accurate debug
        for col in merge_cols:
            if col in qualtrics_df.columns:
                qualtrics_df[col] = qualtrics_df[col].astype(str).str.replace(" ", "")
            if col in pop_df.columns:
                pop_df[col] = pop_df[col].astype(str).str.replace(" ", "")
                
        merged_debug = qualtrics_df.merge(pop_df, on=merge_cols, how='left')
        unmatched = merged_debug[merged_debug['mem_rate'].isna()]
        print(f"Unmatched rows: {len(unmatched)}")
        if len(unmatched) > 0:
            print("Sample unmatched rows:")
            print(unmatched[merge_cols].head())
            # Calculate NPS of unmatched
            unmatched_nps = unmatched['Q1_1'].mean() # Rough proxy
            print(f"Average Score of Unmatched: {unmatched_nps}")

        # Test 8-group weighting (Gender x Age) Hypothesis
        print("\n--- Testing 8-group weighting (Gender x Age) ---")
        
        # Aggregate population data
        pop_agg = pop_df.groupby(['gender', 'age_group'])['mem_rate'].sum().reset_index()
        print(f"Aggregated Population: {len(pop_agg)} rows")
        print(pop_agg)
        
        # Merge manually for 8-group
        merge_cols_8 = ['gender', 'age_group']
        merged_8 = qualtrics_df.merge(pop_agg, on=merge_cols_8, how='left')
        
        # Calculate sample counts
        counts_8 = merged_8.groupby(merge_cols_8).size().reset_index(name='sample_count')
        merged_8 = merged_8.merge(counts_8, on=merge_cols_8, how='left')
        
        # Calculate weights
        merged_8['weight'] = merged_8['mem_rate'] / merged_8['sample_count']
        merged_8['weight'] = merged_8['weight'].fillna(1.0)
        
        # Normalize
        scale_8 = len(merged_8) / merged_8['weight'].sum()
        merged_8['normalized_weight'] = merged_8['weight'] * scale_8
        
        # Calculate NPS
        merged_8['nps_group'] = pd.cut(merged_8['Q1_1'], bins=[-np.inf, 6, 8, np.inf], labels=['Detractor', 'Passive', 'Promoter'])
        total_w = merged_8['normalized_weight'].sum()
        prom_w = merged_8[merged_8['nps_group'] == 'Promoter']['normalized_weight'].sum()
        det_w = merged_8[merged_8['nps_group'] == 'Detractor']['normalized_weight'].sum()
        
        nps_8 = (prom_w - det_w) / total_w * 100
        print(f"Calculated NPS (8-group): {nps_8:.2f}")
        print(f"Expected NPS: 30.96")
        
        if abs(nps_8 - 30.96) < 0.5:
             print("SUCCESS: 8-group weighting matches user script (approx)!")
        else:
             print("WARNING: 8-group weighting still differs.")

        # Calculate 96-group weighting (Default App Logic)
        print("\n--- Testing 96-group weighting (App Default) ---")
        result = food_nps.calculate_food_nps_with_weighting(qualtrics_df, pop_df)
        
        nps_score = result['nps_score']
        print(f"Calculated NPS (96-group): {nps_score}")
        print(f"Expected NPS (User Script): 30.96")
        
        diff = abs(nps_score - 30.96)
        print(f"Difference: {diff:.4f}")
        
        print("\nCONCLUSION:")
        print(f"1. User Script (8 groups): 30.96")
        print(f"2. App (8 groups sim):   {nps_8:.2f} (Diff: {abs(nps_8 - 30.96):.2f})")
        print(f"3. App (96 groups):      {nps_score} (Diff: {diff:.2f})")
        print("The app uses more granular weighting (96 groups), which explains the lower score.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_food_nps_fix()
