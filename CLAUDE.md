# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

NPS Data Processing (NPS_DP) is a full-stack web application for automating NPS (Net Promoter Score) analysis with advanced weighting and segmentation capabilities. Built with FastAPI backend and React + Vite frontend, it processes Qualtrics survey data with population-based weighting for Korean food service NPS analysis.

## Project Structure

```
NPS_DP/
├── backend/                # FastAPI server
│   ├── main.py            # API endpoints and CORS configuration
│   ├── data_processing.py # CSV/Excel file handling and Qualtrics parser
│   ├── weighting.py       # Cell-based weighting algorithm
│   ├── analysis.py        # NPS, Top 3 Box, response rate calculations
│   ├── food_nps.py        # Korean food delivery (배달의민족) NPS analysis
│   ├── requirements.txt   # Python dependencies
│   └── venv/              # Python virtual environment
├── frontend/              # React + Vite + TailwindCSS
│   ├── src/
│   │   ├── App.jsx        # Main app with state management
│   │   └── components/    # FileUpload, WeightingConfig, Dashboard
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Vite build configuration
├── guide/                 # Manual documentation
│   └── MANUAL_monthly_analysis.md  # Korean NPS analysis workflow guide
├── test_food_nps_api.py   # Food NPS API test script
└── dummy_*_food.csv       # Test data files
```

## Development Setup

### Backend (Python FastAPI)

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server (default port 8000)
uvicorn main:app --reload

# Run with custom port
uvicorn main:app --reload --port 8001
```

**Requirements**:
- Python 3.8+
- FastAPI, uvicorn, pandas, python-multipart, openpyxl

### Frontend (React + Vite)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server (default port 5173)
npm run dev

# Build for production
npm run build

# Lint code
npm run lint

# Preview production build
npm run preview
```

**Requirements**:
- Node.js 16+
- React 19, Vite 7, TailwindCSS 4

## Core Architecture

### Backend Data Flow

1. **File Upload (`/upload/*`)**:
   - Accepts Qualtrics survey data, population weights, and coding files
   - Stores in-memory data store: `data_store = {"qualtrics", "population", "coding", "merged"}`
   - Qualtrics parser removes 3-row header metadata automatically

2. **Data Processing (`data_processing.py`)**:
   - `load_qualtrics_data()`: Strips Qualtrics export metadata rows
   - `merge_data()`: Left joins coding data on ResponseId
   - `load_food_nps_data()`: Validates required columns (ResponseId, Q1_1, gender, age_group, rgn_nm, bmclub)

3. **Weighting (`weighting.py`)**:
   - Cell-based weighting algorithm: `Weight = (Target % / Sample %) normalized`
   - Supports multi-dimensional segmentation (e.g., gender_age_region_membership = 60 groups)
   - Auto-normalizes weights to preserve total sample size (mean weight = 1)

4. **Analysis (`analysis.py`)**:
   - `calculate_nps()`: (% Promoters 9-10) - (% Detractors 0-6)
   - `calculate_top_3_box()`: % responses 5-7 on 7-point scale
   - `calculate_response_rate()`: % non-empty open-ended responses
   - All metrics support weighted calculations

5. **Analysis Endpoint (`/analyze`)**:
   - Applies optional weighting configuration
   - Returns NPS, Top 3 Box %, response rate, and weighted flag

### Frontend Component Architecture

- **App.jsx**: State manager for columns and weighting config, fetches backend data
- **FileUpload.jsx**: Handles Qualtrics/population/coding CSV uploads
- **WeightingConfig.jsx**: UI for defining segment columns and target proportions
- **Dashboard.jsx**: Displays NPS metrics, visualizations, and segment breakdowns

### API Endpoints

| Endpoint | Method | Purpose | Request Body |
|----------|--------|---------|--------------|
| `/upload/qualtrics` | POST | Upload Qualtrics survey file | FormData (file) |
| `/upload/population` | POST | Upload population weights | FormData (file) |
| `/upload/coding` | POST | Upload category coding file | FormData (file) |
| `/analyze` | POST | Calculate NPS metrics | `{nps_column, top_box_column, open_end_column, weighting_config?}` |
| `/columns` | GET | Get available columns from merged data | None |
| `/preview-segments` | POST | Preview segment combinations | `{columns: [string]}` |

### Key Data Structures

**WeightingConfig**:
```python
{
    "segment_columns": ["gender", "age_group", "rgn_nm", "bmclub"],
    "targets": {
        "MALE_18-24_수도권_구독": 0.05,
        "FEMALE_25-34_광역시_미구독": 0.08,
        # ... 60 groups total for 2x5x3x2 combinations
    }
}
```

**Analysis Request/Response**:
```python
# Request
{
    "nps_column": "Q1_1",
    "top_box_column": "Q2_1",
    "open_end_column": "Q3",
    "weighting_config": {...}  # Optional
}

# Response
{
    "nps": -17.99,
    "top_box_3_percent": 65.4,
    "response_rate": 42.3,
    "weighted": true
}
```

## Korean Food NPS Analysis Workflow

This application is designed for monthly NPS analysis of Korean food service data. See `guide/MANUAL_monthly_analysis.md` for comprehensive Korean workflow documentation.

**Key Analysis Parameters**:
- **60-Group Weighting**: gender (2) × age_group (5) × rgn_nm (3) × bmclub (2)
- **NPS Classification**: Promoter (9-10), Passive (7-8), Detractor (0-6), High-Risk (0-3)
- **Normalization**: Scale factor = unweighted_total / weighted_total (ensures weighted N = unweighted N)
- **Expected Metrics**: NPS around -18.0, ~2,409 respondents after gender filtering

## Development Patterns

### Qualtrics Data Handling

Qualtrics exports include 3 metadata rows that must be stripped:
- Row 1: Column names (Q1, Q2, etc.)
- Row 2: Question text descriptions
- Row 3: Import tags

The `load_qualtrics_data()` function automatically removes rows 2-3 if ResponseId exists.

### Weighting Algorithm

Cell-based weighting follows this formula:
```
Weight(segment) = Target_Proportion(segment) / Sample_Proportion(segment)
Normalized_Weight = Weight / Mean(Weight)  # Ensures sum(weights) = N
```

This preserves total sample size while adjusting for demographic imbalances.

### In-Memory Data Management

Backend stores all uploaded data in memory (`data_store` dict). No database persistence. Data resets when server restarts. Suitable for single-session analysis workflows.

### React State Flow

1. User uploads files → triggers `fetchColumns()`
2. `App.jsx` receives columns → passes to `WeightingConfig` and `Dashboard`
3. User configures weights → `setWeightingConfig()` updates state
4. `Dashboard` calls `/analyze` with current `weightingConfig`
5. Results render in Dashboard component

## Common Development Tasks

### Add New Analysis Metric

1. Add calculation function in `backend/analysis.py`:
   ```python
   def calculate_my_metric(df, column, weight_column=None):
       # Implement weighted calculation
       return result
   ```

2. Update `AnalysisRequest` model in `backend/main.py`:
   ```python
   class AnalysisRequest(BaseModel):
       my_metric_column: str
   ```

3. Call in `/analyze` endpoint and return in response

4. Update frontend `Dashboard.jsx` to display new metric

### Test API Endpoints

```bash
# Test NPS calculation (from backend directory)
python test_api.py

# Manual curl test
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{"nps_column":"Q1_1","top_box_column":"Q2_1","open_end_column":"Q3"}'
```

### Generate Dummy Data

```bash
# Create test CSV files (from project root)
python seed_data.py
# Creates: dummy_qualtrics.csv, dummy_population.csv, dummy_coding.csv
```

## Food NPS (배달의민족) Specific API

### Overview

Specialized endpoints for Korean food delivery service NPS analysis with 241-segment demographic weighting. Implements the methodology documented in `guide/MANUAL_monthly_analysis.md`.

### Endpoints

**POST `/food-nps/upload/qualtrics`**
- Uploads Korean Qualtrics food NPS survey data
- Validates required columns: ResponseId, Q1_1 (NPS), gender, age_group, rgn_nm, bmclub
- Removes Qualtrics metadata rows automatically
- Returns: row count, column list, valid NPS score count

**POST `/food-nps/upload/population`**
- Uploads population weighting data for 241 demographic segments
- Structure: gender × age_group × rgn_nm × bmclub × division × is_mfo
- Validates mem_rate (weight ratio) column
- Returns: segment count, total weight, column list

**POST `/food-nps/upload/coding`**
- Uploads category classification data for open-ended Q2 responses
- Links to ResponseId from Qualtrics data
- Categories: "가게/메뉴 다양성", "배달팁", "배달속도", etc.
- Returns: row count, unique category count

**POST `/food-nps/analyze`**
- Calculates weighted NPS using uploaded data
- Requires: food_qualtrics + food_population (coding optional)
- Applies normalization: scale_factor = unweighted_total / weighted_total
- Returns:
  ```json
  {
    "nps_score": -18.24,
    "total_responses": 2409,
    "promoters_pct": 35.2,
    "passives_pct": 28.5,
    "detractors_pct": 36.3,
    "scale_factor": 1.0234,
    "demographic_breakdown": [...],
    "category_analysis": {
      "Promoter": [...],
      "Passive": [...],
      "Detractor": [...]
    }
  }
  ```

**GET `/food-nps/status`**
- Checks which data files have been uploaded
- Returns upload status and row counts for all three data sources

### Testing Food NPS API

```bash
# Run comprehensive test suite
python test_food_nps_api.py

# Tests execute:
# 1. Upload dummy_qualtrics_food.csv
# 2. Upload dummy_population_food.csv
# 3. Upload dummy_coding_food.csv
# 4. Check upload status
# 5. Run weighted NPS analysis
# 6. Validate results against expected range (NPS ~-18.0)
```

### Example Workflow

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Upload survey data
with open("dummy_qualtrics_food.csv", "rb") as f:
    files = {"file": ("dummy_qualtrics_food.csv", f, "text/csv")}
    r = requests.post(f"{BASE_URL}/food-nps/upload/qualtrics", files=files)
    print(r.json())

# 2. Upload population weights
with open("dummy_population_food.csv", "rb") as f:
    files = {"file": ("dummy_population_food.csv", f, "text/csv")}
    r = requests.post(f"{BASE_URL}/food-nps/upload/population", files=files)
    print(r.json())

# 3. Upload category coding (optional)
with open("dummy_coding_food.csv", "rb") as f:
    files = {"file": ("dummy_coding_food.csv", f, "text/csv")}
    r = requests.post(f"{BASE_URL}/food-nps/upload/coding", files=files)
    print(r.json())

# 4. Run analysis
r = requests.post(f"{BASE_URL}/food-nps/analyze")
result = r.json()
print(f"Weighted NPS: {result['nps_score']}")
```

### Data Structure Requirements

**Qualtrics Data (`dummy_qualtrics_food.csv`)**:
- ResponseId: Unique identifier
- Q1_1: NPS score (0-10)
- Q2: Open-ended response (optional)
- Q11-Q33: Satisfaction questions (7-point scale)
- Demographics: gender (MALE/FEMALE), age_group (10대/20대/30대/40대/50대 이상), rgn_nm (수도권/광역시/지방), bmclub (구독/미구독)
- Additional: division (OD/MP/TAKEOUT), is_mfo (0/1)

**Population Data (`dummy_population_food.csv`)**:
- Demographic columns matching Qualtrics
- mem_rate: Weight ratio for each segment
- mem_cnt: Sample count per segment
- TOTAL_CNT: Total population

**Coding Data (`dummy_coding_food.csv`)**:
- ResponseId: Links to Qualtrics
- classification: Classification type
- category: Main category
- sub_category: Detailed subcategory

### Expected Results

Based on `guide/MANUAL_monthly_analysis.md`:
- **Expected NPS**: ~-18.0
- **Sample Size**: ~2,409 respondents after filtering
- **Weighting Method**: 60-group demographic weighting with normalization
- **Response Rate**: Varies by category (20-40% typical)

## Important Notes

- **CORS**: Backend allows all origins (`allow_origins=["*"]`) for development. Restrict in production.
- **File Encoding**: CSV files must be UTF-8-BOM encoded for Korean text compatibility
- **Memory Limits**: Large datasets (>100K rows) may cause memory issues with in-memory storage
- **Weighting Validation**: Always verify normalized weights sum to original sample size
- **Korean Language**: All UI text, documentation, and data labels support Korean (UTF-8)
- **Food NPS**: Use `/food-nps/*` endpoints for Korean food delivery analysis with 241-segment weighting
