import pandas as pd

# File Paths
FULL_DATA_FILE = '/Users/hmkwon/Project/011_NPS/csv_output/food_nps_data.csv'
OPEN_DATA_FILE = '/Users/hmkwon/Project/011_NPS/csv_output/food_nps_data_open.csv'

print("Checking respondent counts...")

try:
    # Load Full Data
    df_full = pd.read_csv(FULL_DATA_FILE, encoding='utf-8-sig')
    total_respondents = df_full['ResponseId'].nunique()
    print(f"Total Respondents (Qualtrics): {total_respondents:,}")

    # Load Open Data
    df_open = pd.read_csv(OPEN_DATA_FILE, encoding='utf-8-sig')
    
    # Filter for valid category as per script logic
    df_open_valid = df_open[df_open['category'].notna()]
    comment_respondents = df_open_valid['ResponseId'].nunique()
    print(f"Respondents with Valid Comments (Coding): {comment_respondents:,}")
    
    diff = total_respondents - comment_respondents
    print(f"Difference (Non-commenters): {diff:,}")
    
    if diff > 0:
        print(f"Conclusion: {diff:,} respondents ({diff/total_respondents*100:.2f}%) did NOT provide a valid open-ended response.")
    else:
        print("Conclusion: Everyone provided a valid open-ended response.")

except Exception as e:
    print(f"Error: {e}")
