from fastapi.testclient import TestClient
from main import app
import pandas as pd
import io

client = TestClient(app)

def test_workflow():
    print("Starting tests...")
    # 1. Upload Qualtrics Data
    # Mocking a CSV with 3 header rows as per our logic
    csv_content = "ResponseId,Q1,Q2\nDesc,Desc,Desc\nImport,Import,Import\nR1,10,5\nR2,5,7\nR3,8,6"
    response = client.post(
        "/upload/qualtrics",
        files={"file": ("qualtrics.csv", csv_content, "text/csv")}
    )
    if response.status_code != 200:
        print(f"Upload failed: {response.json()}")
    assert response.status_code == 200
    assert response.json()["rows"] == 3
    print("Upload successful.")

    # 4. Preview Segments
    response = client.post(
        "/preview-segments",
        json={"columns": ["Q2"]}
    )
    assert response.status_code == 200
    segments = response.json()["segments"]
    assert "5" in segments
    assert "7" in segments
    print("Preview segments successful.")

    # 5. Analyze without weighting
    response = client.post(
        "/analyze",
        json={
            "nps_column": "Q1",
            "top_box_column": "Q2",
            "open_end_column": "Q1"
        }
    )
    assert response.status_code == 200
    data = response.json()
    # NPS: R1(10)->Promoter, R2(5)->Detractor, R3(8)->Passive.
    # Promoters: 1/3, Detractors: 1/3. NPS = 0.
    assert data["nps"] == 0.0
    
    # Top Box (5,6,7): All are 5, 6, 7. So 100%.
    assert data["top_box_3_percent"] == 100.0
    print("Analysis successful.")

    print("All tests passed!")

if __name__ == "__main__":
    test_workflow()
