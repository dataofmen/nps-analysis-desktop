"""
Test script for Food NPS (배달의민족) API endpoints.

Tests the complete workflow:
1. Upload Qualtrics survey data
2. Upload population weighting data
3. Upload category coding data
4. Run weighted NPS analysis
5. Validate results

Usage:
    python test_food_nps_api.py
"""

import requests
import json
from pathlib import Path


BASE_URL = "http://localhost:8000"


def test_upload_qualtrics():
    """Test uploading Korean food NPS Qualtrics data."""
    print("\n" + "="*60)
    print("Testing: Upload Qualtrics Data")
    print("="*60)

    file_path = Path("dummy_qualtrics_food.csv")
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/food-nps/upload/qualtrics", files=files)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Upload successful!")
        print(f"   - Rows: {data['rows']}")
        print(f"   - Valid NPS scores: {data['valid_nps_scores']}")
        print(f"   - Columns: {len(data['columns'])}")
        return True
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False


def test_upload_population():
    """Test uploading population weighting data."""
    print("\n" + "="*60)
    print("Testing: Upload Population Data")
    print("="*60)

    file_path = Path("dummy_population_food.csv")
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/food-nps/upload/population", files=files)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Upload successful!")
        print(f"   - Segments: {data['segments']}")
        print(f"   - Total weight: {data['total_weight']:.4f}")
        print(f"   - Columns: {len(data['columns'])}")
        return True
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False


def test_upload_coding():
    """Test uploading category coding data."""
    print("\n" + "="*60)
    print("Testing: Upload Coding Data")
    print("="*60)

    file_path = Path("dummy_coding_food.csv")
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f, 'text/csv')}
        response = requests.post(f"{BASE_URL}/food-nps/upload/coding", files=files)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Upload successful!")
        print(f"   - Rows: {data['rows']}")
        print(f"   - Unique categories: {data['unique_categories']}")
        return True
    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False


def test_status():
    """Check upload status."""
    print("\n" + "="*60)
    print("Testing: Check Status")
    print("="*60)

    response = requests.get(f"{BASE_URL}/food-nps/status")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status retrieved successfully!")
        print(f"   - Qualtrics uploaded: {data['qualtrics_uploaded']} ({data['qualtrics_rows']} rows)")
        print(f"   - Population uploaded: {data['population_uploaded']} ({data['population_segments']} segments)")
        print(f"   - Coding uploaded: {data['coding_uploaded']} ({data['coding_rows']} rows)")
        return True
    else:
        print(f"❌ Status check failed: {response.status_code}")
        return False


def test_analyze():
    """Test weighted NPS analysis."""
    print("\n" + "="*60)
    print("Testing: Analyze Food NPS")
    print("="*60)

    response = requests.post(f"{BASE_URL}/food-nps/analyze")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Analysis successful!")
        print(f"\n   📊 Overall Results:")
        print(f"   - NPS Score: {data['nps_score']}")
        print(f"   - Total Responses: {data['total_responses']}")
        print(f"   - Promoters: {data['promoters_pct']}%")
        print(f"   - Passives: {data['passives_pct']}%")
        print(f"   - Detractors: {data['detractors_pct']}%")
        print(f"   - Scale Factor: {data['scale_factor']}")

        # Show sample demographic breakdown
        if 'demographic_breakdown' in data and len(data['demographic_breakdown']) > 0:
            print(f"\n   👥 Sample Demographic Segments (first 5):")
            for segment in data['demographic_breakdown'][:5]:
                segment_desc = f"{segment.get('gender', '?')} / {segment.get('age_group', '?')} / {segment.get('rgn_nm', '?')}"
                print(f"   - {segment_desc}: NPS={segment['nps']}, n={segment['count']}")

        # Show category analysis if available
        if 'category_analysis' in data:
            print(f"\n   📁 Category Analysis:")
            for nps_group in ['Promoter', 'Passive', 'Detractor']:
                if nps_group in data['category_analysis']:
                    categories = data['category_analysis'][nps_group]
                    if categories:
                        print(f"\n   {nps_group}s - Top 3 Categories:")
                        for cat in categories[:3]:
                            print(f"      - {cat['category']}: {cat['response_rate']}% (n={cat['count']})")

        return True
    else:
        print(f"❌ Analysis failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False


def validate_nps_score(nps_score: float):
    """Validate NPS score is within expected range for 배달의민족."""
    print("\n" + "="*60)
    print("Validating NPS Score")
    print("="*60)

    # Based on MANUAL_monthly_analysis.md: Expected NPS ~-18.0
    expected_range = (-30, -10)

    if expected_range[0] <= nps_score <= expected_range[1]:
        print(f"✅ NPS score {nps_score} is within expected range {expected_range}")
        return True
    else:
        print(f"⚠️  NPS score {nps_score} is outside expected range {expected_range}")
        print(f"   This may indicate data quality issues or methodology differences")
        return False


def run_all_tests():
    """Run all Food NPS API tests."""
    print("\n" + "="*60)
    print("🧪 Food NPS API Test Suite")
    print("배달의민족 NPS 분석 시스템 테스트")
    print("="*60)

    results = {
        "upload_qualtrics": False,
        "upload_population": False,
        "upload_coding": False,
        "status_check": False,
        "analyze": False
    }

    # Run tests in sequence
    results["upload_qualtrics"] = test_upload_qualtrics()
    results["upload_population"] = test_upload_population()
    results["upload_coding"] = test_upload_coding()
    results["status_check"] = test_status()
    results["analyze"] = test_analyze()

    # Summary
    print("\n" + "="*60)
    print("📋 Test Summary")
    print("="*60)

    total_tests = len(results)
    passed_tests = sum(results.values())

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\n   Total: {passed_tests}/{total_tests} tests passed")

    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Food NPS API is working correctly.")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please check the errors above.")

    return passed_tests == total_tests


if __name__ == "__main__":
    import sys

    print("Starting Food NPS API tests...")
    print("Make sure the backend server is running: uvicorn backend.main:app --reload")
    print()

    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server")
        print("   Please start the server: uvicorn backend.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
