import pandas as pd
import numpy as np

# File Paths
DATA_FILE = '/Users/hmkwon/Project/011_NPS/csv_output/food_nps_data_open.csv'
WEIGHT_FILE = '/Users/hmkwon/Project/011_NPS/nps_by_group.csv'

# Load Data
print("Loading data...")
df = pd.read_csv(DATA_FILE, encoding='utf-8-sig')
df_weight = pd.read_csv(WEIGHT_FILE, encoding='utf-8-sig')

# Preprocessing (Same as user script)
df = df[df['gender'].notna()].copy()
df = df[df['category'].notna()].copy()
df = df[df['sub_category'].notna()].copy()
df = df[df['Q1_1'].notna()].copy()
df['Q1_1'] = pd.to_numeric(df['Q1_1'], errors='coerce')
df = df[df['Q1_1'].notna()].copy()

# NPS Grouping
def classify_nps(score):
    if score <= 6: return 'Detractor'
    elif score <= 8: return 'Passive'
    else: return 'Promoter'

df['nps_group'] = df['Q1_1'].apply(classify_nps)

# Merge Weights
# The user script iterates through weight groups. Here we merge for efficiency.
# Note: User script filters by gender/age/region. We assume these columns exist in df.
# Check if columns match
print("Merging weights...")
merged_df = pd.merge(df, df_weight, on=['gender', 'age_group', 'rgn_nm'], how='left')
merged_df['Weight'] = merged_df['가중치'].fillna(1.0)

# Calculate Stats
results = []

for nps_group in ['Promoter', 'Passive', 'Detractor']:
    group_df = merged_df[merged_df['nps_group'] == nps_group]
    
    # 1. Incidence Rate (App Method)
    # Base = All unique respondents in this NPS group
    base_incidence = group_df.drop_duplicates(subset=['ResponseId'])['Weight'].sum()
    
    # 2. Distribution Rate (Script Method)
    # Base = Unique respondents in this NPS group WHO HAVE A VALID CATEGORY
    # Since we already filtered df for notna category, in this specific dataframe they are the same?
    # WAIT. The user script loads the OPEN END data file. This file ONLY contains rows with comments.
    # So `df` ONLY has respondents with comments.
    # BUT, the "App Method" uses the QUALTRICS file (all respondents) as the base.
    # So I need to know the TOTAL number of respondents in the NPS group, even those without comments.
    
    # Ah, I don't have the full Qualtrics file path here easily, but I can infer from the user's context.
    # However, the user asked to compare "App Method" vs "Script Method".
    # The "App Method" uses the `qualtrics` data store which has ALL respondents.
    # The "Script Method" uses `food_nps_data_open.csv` which likely only has comments.
    
    # If I can't load the full Qualtrics data, I can't calculate the true Incidence Rate base.
    # BUT, the user provided `nps_by_group.csv` as weights. 
    # Does this file contain the total counts?
    # The user script calculates `group_total` from `df_group` which is filtered from `df` (open ends).
    # So the user script's "Distribution Rate" base is "Respondents with comments".
    
    # To get "Incidence Rate", I need the count of ALL respondents in that NPS group.
    # Let's assume the `food_nps_data.csv` (without _open) exists?
    # Or I can use the `nps_by_group.csv` to estimate the total population if it has counts?
    # No, `nps_by_group.csv` seems to be just weights.
    
    # Let's try to load the full data file if possible.
    # Based on previous context, `food_nps_data.csv` might be the full file.
    FULL_DATA_FILE = '/Users/hmkwon/Project/011_NPS/csv_output/food_nps_data.csv'
    
    try:
        full_df = pd.read_csv(FULL_DATA_FILE, encoding='utf-8-sig')
        full_df['Q1_1'] = pd.to_numeric(full_df['Q1_1'], errors='coerce')
        full_df['nps_group'] = full_df['Q1_1'].apply(classify_nps)
        
        full_merged = pd.merge(full_df, df_weight, on=['gender', 'age_group', 'rgn_nm'], how='left')
        full_merged['Weight'] = full_merged['가중치'].fillna(1.0)
        
        full_group_df = full_merged[full_merged['nps_group'] == nps_group]
        base_incidence = full_group_df.drop_duplicates(subset=['ResponseId'])['Weight'].sum()
        
    except FileNotFoundError:
        print(f"Warning: Full data file {FULL_DATA_FILE} not found. Cannot calculate true Incidence Rate.")
        base_incidence = 0

    # Base for Distribution (Script Method)
    # Filtered for valid category (already done in group_df)
    base_distribution = group_df.drop_duplicates(subset=['ResponseId'])['Weight'].sum()
    
    print(f"\nGroup: {nps_group}")
    print(f"  Base (Incidence - All Respondents): {base_incidence:,.2f}")
    print(f"  Base (Distribution - Commenters): {base_distribution:,.2f}")
    
    # Calculate Top 5 Categories
    cat_counts = group_df.groupby('category').apply(
        lambda x: x.drop_duplicates(subset=['ResponseId'])['Weight'].sum()
    ).sort_values(ascending=False).head(5)
    
    for cat, count in cat_counts.items():
        incidence_rate = (count / base_incidence * 100) if base_incidence > 0 else 0
        distribution_rate = (count / base_distribution * 100) if base_distribution > 0 else 0
        diff = incidence_rate - distribution_rate
        
        results.append({
            "Group": nps_group,
            "Category": cat,
            "Incidence %": round(incidence_rate, 2),
            "Distribution %": round(distribution_rate, 2),
            "Diff %": round(diff, 2)
        })

# Output Results
print("\nComparison of Top 5 Categories per Group:")
print(f"{'Group':<10} | {'Category':<20} | {'Incidence %':<12} | {'Dist %':<12} | {'Diff %':<12}")
print("-" * 80)
for r in results:
    print(f"{r['Group']:<10} | {r['Category']:<20} | {r['Incidence %']:<12} | {r['Distribution %']:<12} | {r['Diff %']:<12}")
