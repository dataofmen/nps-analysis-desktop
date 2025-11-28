import httpx
import pandas as pd
from pathlib import Path

BASE_URL = "http://localhost:8000"

def upload_file(endpoint: str, file_path: Path):
    with file_path.open('rb') as f:
        files = {'file': (file_path.name, f, 'application/octet-stream')}
        response = httpx.post(f"{BASE_URL}{endpoint}", files=files)
    response.raise_for_status()
    return response.json()

def main():
    # Paths to data files
    data_dir = Path(__file__).parent.parent / "backend" / "data"
    nps_file = data_dir / "food_nps_data.csv"
    pop_file = data_dir / "food_population.csv"
    coding_file = Path(__file__).parent.parent / "dummy_coding_food.csv"

    # Upload Qualtrics (NPS) data
    print("Uploading NPS data...")
    upload_file("/upload/qualtrics", nps_file)

    # Upload population weighting data
    print("Uploading population data...")
    upload_file("/upload/population", pop_file)

    # Upload coding data (subjective responses)
    print("Uploading coding data...")
    upload_file("/upload/coding", coding_file)

# Build weighting configuration from population file (disabled for initial test)
    # pop_df = pd.read_csv(pop_file)
    # segment_cols = ["gender", "age_group", "rgn_nm", "bmclub"]
    # targets = {}
    # for _, row in pop_df.iterrows():
    #     key = "_".join([str(row[col]) for col in segment_cols])
    #     targets[key] = float(row["mem_rate"])
    # weighting_config = {
    #     "segment_columns": segment_cols,
    #     "targets": targets,
    # }
    weighting_config = None

    # Prepare analysis request payload
    analysis_payload = {
        "nps_column": "Q1_1",
        "top_box_column": "Q1_1",  # Assuming same column for top‑box calculation
        "open_end_column": "ResponseId",  # Use any column to count rows for response rate
        "weighting_config": weighting_config,
    }

    print("Running analysis...")
    resp = httpx.post(f"{BASE_URL}/analyze", json=analysis_payload)
    resp.raise_for_status()
    print("Analysis result:")
    print(resp.json())

if __name__ == "__main__":
    main()
