import pandas as pd

FULL_DATA_FILE = '/Users/hmkwon/Project/011_NPS/csv_output/food_nps_data.csv'
df = pd.read_csv(FULL_DATA_FILE, encoding='utf-8-sig')

missing_gender = df['gender'].isna().sum()
print(f"Rows with missing gender: {missing_gender}")

if missing_gender > 0:
    print("Confirmed: Full data contains rows with missing gender.")
else:
    print("No missing gender found.")
