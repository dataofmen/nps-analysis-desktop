import requests
import os

BASE_URL = "http://localhost:8000"
FILES_DIR = "/Users/hmkwon/Project/NPS_DP"

def upload_file(endpoint, filename):
    filepath = os.path.join(FILES_DIR, filename)
    with open(filepath, 'rb') as f:
        files = {'file': (filename, f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/upload/{endpoint}", files=files)
        print(f"Uploaded {filename}: {response.status_code}")
        if response.status_code != 200:
            print(response.text)

def seed_data():
    print("Seeding data...")
    upload_file("qualtrics", "dummy_qualtrics.csv")
    upload_file("population", "dummy_population.csv")
    upload_file("coding", "dummy_coding.csv")
    print("Data seeding complete.")

if __name__ == "__main__":
    seed_data()
