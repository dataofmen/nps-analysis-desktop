import sys
print("DEBUG: Starting main.py imports...", flush=True)
from fastapi import FastAPI, UploadFile, File, HTTPException
print("DEBUG: Imported fastapi", flush=True)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import pandas as pd
print("DEBUG: Imported pandas", flush=True)
import data_processing
print("DEBUG: Imported data_processing", flush=True)
import weighting
print("DEBUG: Imported weighting", flush=True)
import analysis
print("DEBUG: Imported analysis", flush=True)
import food_nps
print("DEBUG: Imported food_nps", flush=True)
from fastapi.responses import StreamingResponse
import io

app = FastAPI(title="NPS Analysis Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
data_store = {
    "qualtrics": None,
    "population": None,
    "coding": None,
    "merged": None,
    # Food NPS specific storage
    "food_qualtrics": None,
    "food_population": None,
    "food_coding": None
}

@app.post("/reset")
async def reset_data():
    global data_store
    data_store = {
        "qualtrics": None,
        "population": None,
        "coding": None,
        "merged": None,
        "food_qualtrics": None,
        "food_population": None,
        "food_coding": None
    }
    return {"message": "Data store reset successfully"}

@app.post("/upload/qualtrics")
async def upload_qualtrics(file: UploadFile = File(...)):
    content = await file.read()
    try:
        df = data_processing.load_qualtrics_data(content, file.filename)
        data_store["qualtrics"] = df
        # If coding is already there, merge
        if data_store["coding"] is not None:
             data_store["merged"] = data_processing.merge_data(df, data_store["coding"])
        else:
             data_store["merged"] = df
        return {"message": "Qualtrics data uploaded", "columns": df.columns.tolist(), "rows": len(df)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/upload/population")
async def upload_population(file: UploadFile = File(...)):
    content = await file.read()
    try:
        df = data_processing.load_file(content, file.filename)
        data_store["population"] = df
        return {"message": "Population data uploaded", "columns": df.columns.tolist(), "rows": len(df)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/upload/coding")
async def upload_coding(file: UploadFile = File(...)):
    content = await file.read()
    try:
        df = data_processing.load_file(content, file.filename)
        data_store["coding"] = df
        if data_store["qualtrics"] is not None:
             data_store["merged"] = data_processing.merge_data(data_store["qualtrics"], df)
        return {"message": "Coding data uploaded", "columns": df.columns.tolist(), "rows": len(df)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

class WeightingConfig(BaseModel):
    segment_columns: List[str]
    targets: Dict[str, float] # Key: "Male_18-24", Value: 0.1
    target_column: Optional[str] = None

class AnalysisRequest(BaseModel):
    nps_column: str
    top_box_columns: List[str]
    open_end_columns: List[str]
    weighting_config: Optional[WeightingConfig] = None
    group_by_columns: List[str] = []
    group_weighting_columns: Optional[List[str]] = None

class PreviewRequest(BaseModel):
    segment_columns: List[str]
    target_column: Optional[str] = None

@app.post("/preview-segments")
async def preview_segments(request: PreviewRequest):
    # Use qualtrics data for segmentation to avoid duplication from coding data
    df = data_store["qualtrics"]
    if df is None:
        # Fallback to merged if qualtrics is missing (shouldn't happen in normal flow)
        df = data_store["merged"]
        
    if df is None:
        raise HTTPException(status_code=400, detail="No data uploaded")
    
    try:
        # Normalize whitespace in segment columns
        if request.segment_columns:
             for col in request.segment_columns:
                 if col in df.columns and df[col].dtype == 'object':
                     df[col] = df[col].str.replace(r'\s+', '', regex=True)

        # Calculate segments
        segments = weighting.get_segment_counts(df, request.segment_columns)
        
        # Calculate suggested targets from population data if available
        suggested_targets = {}
        if data_store["population"] is not None:
             pop_df = data_store["population"]
             suggested_targets = weighting.calculate_targets(pop_df, request.segment_columns, request.target_column)

        return {
            "segments": segments,
            "suggested_targets": suggested_targets
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


def perform_analysis(request: AnalysisRequest, df: pd.DataFrame):
    # Apply weighting if config provided
    excluded_count = 0
    weight_col = None
    
    if request.weighting_config and request.weighting_config.segment_columns:
        try:
            # Filter out rows with missing segment data
            initial_count = len(df)
            for col in request.weighting_config.segment_columns:
                if col in df.columns:
                     # Replace whitespace with NaN
                     df[col] = df[col].replace(r'^\s*$', pd.NA, regex=True)
            
            df = df.dropna(subset=request.weighting_config.segment_columns)
            excluded_count = initial_count - len(df)
            
            if len(df) == 0:
                 raise HTTPException(status_code=400, detail="All rows excluded due to missing segment data.")

            # Calculate weights on the unique respondent data
            df = weighting.calculate_weights(df, request.weighting_config.segment_columns, request.weighting_config.targets)
            weight_col = 'Weight'
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Weighting error: {str(e)}")
    
    # Calculate metrics
    nps = analysis.calculate_nps(df, request.nps_column, weight_col)
    top_box = analysis.calculate_top_3_box(df, request.top_box_columns, weight_col)
    
    # Calculate Segmented Results if group_by_columns are provided
    segmented_results = {}
    if request.group_by_columns:
        for col in request.group_by_columns:
            if col in df.columns:
                col_results = {}
                groups = df[col].dropna().unique()
                
                for group in groups:
                    group_df = df[df[col] == group]
                    current_weight_col = weight_col
                    
                    # Apply Subset Weighting if configured
                    if request.group_weighting_columns and request.weighting_config:
                        try:
                            pop_df = data_store["population"]
                            if pop_df is not None:
                                subset_targets = weighting.calculate_targets(
                                    pop_df, 
                                    request.group_weighting_columns, 
                                    request.weighting_config.target_column
                                )
                                weighted_group_df = weighting.calculate_weights(
                                    group_df, 
                                    request.group_weighting_columns, 
                                    subset_targets
                                )
                                group_df = weighted_group_df
                                current_weight_col = 'Weight'
                        except Exception as e:
                            print(f"Subset weighting failed for group {group}: {e}")
                    
                    group_nps_data = analysis.calculate_nps(group_df, request.nps_column, current_weight_col)
                    group_nps = group_nps_data['score'] if isinstance(group_nps_data, dict) else group_nps_data
                    
                    group_top_box = analysis.calculate_top_3_box(group_df, request.top_box_columns, current_weight_col)
                    
                    col_results[str(group)] = {
                        "nps": group_nps,
                        "top_box_3_percent": group_top_box
                    }
                
                segmented_results[col] = col_results
    
    return {
        "nps": nps,
        "top_box_3_percent": top_box,
        "weighted": weight_col is not None,
        "excluded_count": excluded_count,
        "segmented_results": segmented_results
    }

@app.post("/analyze")
async def analyze_data(request: AnalysisRequest):
    # Use qualtrics data for analysis to ensure 1 row per respondent
    df = data_store["qualtrics"]
    if df is None:
        df = data_store["merged"]
        
    if df is None:
        raise HTTPException(status_code=400, detail="No data uploaded")
    
    return perform_analysis(request, df)

@app.post("/export/quantitative")
async def export_quantitative(request: AnalysisRequest):
    df = data_store["qualtrics"]
    if df is None:
        df = data_store["merged"]
    if df is None:
        raise HTTPException(status_code=400, detail="No data uploaded")

    results = perform_analysis(request, df)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: Overview
        overview_data = {
            "Metric": ["NPS Score", "Promoters %", "Passives %", "Detractors %", "Top Box %"],
            "Value": [
                results["nps"]["score"],
                results["nps"]["breakdown"]["promoters"],
                results["nps"]["breakdown"]["passives"],
                results["nps"]["breakdown"]["detractors"],
                results["top_box_3_percent"]
            ]
        }
        pd.DataFrame(overview_data).to_excel(writer, sheet_name="Overview", index=False)
        
        # Sheet 2: Segmented Results
        if results["segmented_results"]:
            rows = []
            for group_col, group_data in results["segmented_results"].items():
                for group_val, metrics in group_data.items():
                    rows.append({
                        "Group Column": group_col,
                        "Group Value": group_val,
                        "NPS": metrics["nps"],
                        "Top Box %": metrics["top_box_3_percent"]
                    })
            pd.DataFrame(rows).to_excel(writer, sheet_name="Segments", index=False)

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=nps_analysis_quantitative.xlsx"}
    )

@app.post("/export/open-ended")
async def export_open_ended(request: AnalysisRequest):
    # For open-ended, we need to call analyze_response_rates logic
    # But analyze_response_rates is an endpoint, let's just call it directly or extract logic?
    # It's better to call the function logic. 
    # Since analyze_response_rates is async and depends on request, we can just call it.
    # However, it returns a dict, not markdown. We need to format it.
    
    data = await analyze_response_rates(request)
    
    md_lines = ["# Open-Ended Analysis Results\n"]
    
    for col, segments in data["response_rates"].items():
        md_lines.append(f"## Column: {col}\n")
        for seg_name, stats in segments.items():
            md_lines.append(f"### Segment: {seg_name}")
            md_lines.append(f"- **Total Count**: {stats['total_count']}")
            md_lines.append(f"- **Response Rate**: {stats['response_rate']}%")
            if 'category_stats' in stats:
                md_lines.append("\n| Category | Count | Percentage |")
                md_lines.append("|---|---|---|")
                for cat, val in stats['category_stats'].items():
                    # val is {count, percentage}
                    md_lines.append(f"| {cat} | {val['count']} | {val['percentage']}% |")
            md_lines.append("\n")
            
    md_content = "\n".join(md_lines)
    
    return StreamingResponse(
        io.BytesIO(md_content.encode()),
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=nps_analysis_open_ended.md"}
    )

@app.post("/analyze/response-rates")
async def analyze_response_rates(request: AnalysisRequest):
    # Use merged data for response rates to support coding columns
    merged_df = data_store["merged"]
    qualtrics_df = data_store["qualtrics"]
    
    if merged_df is None:
        # Fallback to qualtrics if merged is missing
        merged_df = qualtrics_df
        
    if merged_df is None:
        raise HTTPException(status_code=400, detail="No data uploaded")
        
    weight_col = None
    excluded_count = 0
    
    # Apply weighting if config provided
    # We must calculate weights based on UNIQUE respondents (qualtrics_df)
    # Then map these weights to the merged_df
    print(f"DEBUG: analyze_response_rates weighting_config: {request.weighting_config}")
    if request.weighting_config and request.weighting_config.segment_columns and qualtrics_df is not None:
        try:
            # 0. Filter missing segment data from qualtrics_df
            initial_q_count = len(qualtrics_df)
            q_df_clean = qualtrics_df.copy()
            
            for col in request.weighting_config.segment_columns:
                if col in q_df_clean.columns:
                     q_df_clean[col] = q_df_clean[col].replace(r'^\s*$', pd.NA, regex=True)
            
            q_df_clean = q_df_clean.dropna(subset=request.weighting_config.segment_columns)
            excluded_count = initial_q_count - len(q_df_clean)
            print(f"DEBUG: Excluded count: {excluded_count} (Initial: {initial_q_count}, Clean: {len(q_df_clean)})")
            
            if len(q_df_clean) == 0:
                 raise HTTPException(status_code=400, detail="All rows excluded due to missing segment data.")

            # 1. Calculate weights on unique respondents
            weighted_q_df = weighting.calculate_weights(q_df_clean, request.weighting_config.segment_columns, request.weighting_config.targets)
            
            # 2. Map weights to merged_df using ResponseId
            # Assuming ResponseId exists in both
            if 'ResponseId' in weighted_q_df.columns and 'ResponseId' in merged_df.columns:
                # Create a mapping series
                weight_map = weighted_q_df.set_index('ResponseId')['Weight']
                
                # Map to merged_df
                # We work on a copy to avoid modifying global store
                merged_df = merged_df.copy()
                merged_df['Weight'] = merged_df['ResponseId'].map(weight_map)
                
                # CRITICAL: Drop rows in merged_df that didn't get a weight (because they were excluded)
                # If a respondent was in merged_df but excluded from weighting, their weight is NaN.
                # We must drop them to exclude them from analysis.
                merged_df = merged_df.dropna(subset=['Weight'])
                
                weight_col = 'Weight'
        except Exception as e:
            # If weighting fails, proceed without weights but log/warn?
            # Or fail? User expects weighting.
            raise HTTPException(status_code=400, detail=f"Weighting error: {str(e)}")

    # Calculate Response Rates (Category Stats)
    # We pass id_column='ResponseId' to ensure we count unique respondents, not rows
    # We pass weight_column if weighting was applied
    id_col = 'ResponseId' if 'ResponseId' in merged_df.columns else None
    
    results = {}
    
    # Pre-calculate segment masks if NPS column is provided
    segments = {"Overall": merged_df}
    print(f"DEBUG: analyze_response_rates called. NPS Column: '{request.nps_column}'")
    if request.nps_column:
        if request.nps_column in merged_df.columns:
            print(f"DEBUG: NPS column found in merged_df. Calculating segments.")
            # Ensure numeric
            nps_series = pd.to_numeric(merged_df[request.nps_column], errors='coerce')
            
            segments["Promoters (9-10)"] = merged_df[nps_series >= 9]
            segments["Passives (7-8)"] = merged_df[(nps_series >= 7) & (nps_series <= 8)]
            segments["Detractors (0-6)"] = merged_df[nps_series <= 6]
            segments["At-Risk (0-3)"] = merged_df[nps_series <= 3]
        else:
            print(f"DEBUG: NPS column '{request.nps_column}' NOT found in merged_df columns: {merged_df.columns.tolist()}")

    for i, col in enumerate(request.open_end_columns):
        if col:
            col_results = {}
            # Identify parent column (previous level)
            parent_col = request.open_end_columns[i-1] if i > 0 and request.open_end_columns[i-1] else None
            
            for seg_name, seg_df in segments.items():
                # Calculate stats for this segment
                # Note: We must use the SAME weight column. 
                # If weighting was applied, 'Weight' is in seg_df (subset of merged_df).
                # Calculate Base N (Total Count)
                total_count = 0
                if id_col and id_col in seg_df.columns:
                    if weight_col and weight_col in seg_df.columns:
                         unique_weights = seg_df[[id_col, weight_col]].drop_duplicates(subset=[id_col])
                         total_count = unique_weights[weight_col].sum()
                    else:
                         total_count = seg_df[id_col].nunique()
                else:
                    if weight_col and weight_col in seg_df.columns:
                         total_count = seg_df[weight_col].sum()
                    else:
                         total_count = len(seg_df)

                # Calculate Response Rate
                rr_dict = analysis.calculate_response_rate(seg_df, [col], id_column=id_col, weight_column=weight_col)
                response_rate = rr_dict.get(col, 0.0)

                # Calculate Stats
                stats = analysis.calculate_category_stats(
                    seg_df, 
                    col, 
                    id_column=id_col, 
                    weight_column=weight_col,
                    parent_column=parent_col
                )
                
                col_results[seg_name] = {
                    "total_count": round(total_count, 1),
                    "response_rate": response_rate,
                    "category_stats": stats
                }
            results[col] = col_results
    
    return {
        "response_rates": results,
        "excluded_count": excluded_count
    }

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/columns")
async def get_columns():
    if data_store["merged"] is None:
         return {"columns": []}
    return {"columns": data_store["merged"].columns.tolist()}

@app.get("/columns/qualtrics")
async def get_qualtrics_columns():
    if data_store["qualtrics"] is None:
         return {"columns": []}
    return {"columns": data_store["qualtrics"].columns.tolist()}

@app.get("/columns/coding")
async def get_coding_columns():
    if data_store["coding"] is None:
         return {"columns": []}
    return {"columns": data_store["coding"].columns.tolist()}

@app.get("/population-columns")
async def get_population_columns():
    if data_store["population"] is None:
         return {"columns": []}
    return {"columns": data_store["population"].columns.tolist()}

class SegmentRequest(BaseModel):
    columns: List[str]
    target_column: Optional[str] = None

@app.post("/preview-segments")
async def preview_segments(request: SegmentRequest):
    df = data_store["qualtrics"]
    if df is None: 
        # Do not fallback to merged. Weighting must be on original respondents.
        raise HTTPException(status_code=400, detail="Qualtrics data not found. Please upload Qualtrics data.")

    if not request.columns:
        return {"segments": []}

    # Create segments from survey data
    try:
        if len(request.columns) == 1:
            segments = df[request.columns[0]].astype(str).str.replace(" ", "").unique().tolist()
        else:
            segments = df[request.columns].astype(str).apply(lambda x: x.str.replace(" ", "")).agg('_'.join, axis=1).unique().tolist()
        
        segments = sorted(segments)
        
        # Calculate targets from population data if available
        suggested_targets = {}
        pop_df = data_store["population"]
        
        print(f"DEBUG: Previewing segments for columns: {request.columns}, Target Col: {request.target_column}")
        if pop_df is not None:
            print(f"DEBUG: Population data available. Columns: {pop_df.columns.tolist()}")
            
            # Normalize column names for matching: lowercase and strip whitespace
            # Map normalized name -> actual population column name
            pop_col_map = {col.lower().strip(): col for col in pop_df.columns}
            
            # Find matching columns in population data
            matched_pop_cols = []
            missing_cols = []
            
            for req_col in request.columns:
                normalized_req = req_col.lower().strip()
                if normalized_req in pop_col_map:
                    matched_pop_cols.append(pop_col_map[normalized_req])
                else:
                    missing_cols.append(req_col)
            
            if not missing_cols:
                try:
                    # Check if target_column is valid if provided
                    target_col_actual = None
                    if request.target_column:
                        if request.target_column in pop_df.columns:
                            target_col_actual = request.target_column
                        elif request.target_column.lower().strip() in pop_col_map:
                            target_col_actual = pop_col_map[request.target_column.lower().strip()]
                        else:
                            print(f"DEBUG: Target column '{request.target_column}' not found in population data.")
                    
                    print(f"DEBUG: Matched Population Columns: {matched_pop_cols}")
                    print(f"DEBUG: Using Target Column: {target_col_actual}")

                    if len(pop_df) > 0:
                        # Group by segment columns
                        if len(matched_pop_cols) == 1:
                            grouper = pop_df[matched_pop_cols[0]].astype(str).str.replace(" ", "")
                        else:
                            grouper = pop_df[matched_pop_cols].astype(str).apply(lambda x: x.str.replace(" ", "")).agg('_'.join, axis=1)
                        
                        if target_col_actual:
                            # Sum the target column (weights)
                            # Ensure target column is numeric
                            try:
                                pop_counts = pop_df.groupby(grouper)[target_col_actual].sum()
                                total_weight = pop_counts.sum()
                            except Exception as e:
                                print(f"Error summing target column: {e}")
                                # Fallback to count
                                pop_counts = grouper.value_counts()
                                total_weight = len(pop_df)
                        else:
                            # Count rows
                            pop_counts = grouper.value_counts()
                            total_weight = len(pop_df)
                            
                        if total_weight > 0:
                            for seg, count in pop_counts.items():
                                suggested_targets[seg] = round(count / total_weight, 4)
                        print(f"DEBUG: Calculated {len(suggested_targets)} targets.")
                except Exception as e:
                    print(f"Error calculating population targets: {e}")
            else:
                print(f"DEBUG: Missing columns in population data (case-insensitive check): {missing_cols}")
                print(f"DEBUG: Available Population Columns: {list(pop_col_map.keys())}")
        else:
            print("DEBUG: No population data uploaded.")

        return {"segments": segments, "suggested_targets": suggested_targets}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Column not found: {str(e)}")


# ============================================================
# Food NPS (배달의민족) Specific Endpoints
# ============================================================

@app.post("/food-nps/upload/qualtrics")
async def upload_food_qualtrics(file: UploadFile = File(...)):
    """Upload Korean food delivery NPS survey data (Qualtrics export)."""
    content = await file.read()
    try:
        df = food_nps.load_food_qualtrics_data(content, file.filename)
        data_store["food_qualtrics"] = df
        return {
            "message": "Food NPS Qualtrics data uploaded successfully",
            "columns": df.columns.tolist(),
            "rows": len(df),
            "valid_nps_scores": len(df[df['Q1_1'].notna()])
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload error: {str(e)}")


@app.post("/food-nps/upload/population")
async def upload_food_population(file: UploadFile = File(...)):
    """Upload population weighting data for Korean food delivery demographics."""
    content = await file.read()
    try:
        df = food_nps.load_food_population_data(content, file.filename)
        data_store["food_population"] = df
        return {
            "message": "Food NPS population data uploaded successfully",
            "columns": df.columns.tolist(),
            "segments": len(df),
            "total_weight": float(df['mem_rate'].sum())
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload error: {str(e)}")


@app.post("/food-nps/upload/coding")
async def upload_food_coding(file: UploadFile = File(...)):
    """Upload category classification data for open-ended responses."""
    content = await file.read()
    try:
        df = food_nps.load_food_coding_data(content, file.filename)
        data_store["food_coding"] = df
        return {
            "message": "Food NPS coding data uploaded successfully",
            "columns": df.columns.tolist(),
            "rows": len(df),
            "unique_categories": df['category'].nunique() if 'category' in df.columns else 0
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload error: {str(e)}")


@app.post("/food-nps/analyze")
async def analyze_food_nps():
    """
    Analyze Korean food delivery NPS with demographic weighting.

    Requires:
    - food_qualtrics: Survey responses with NPS scores
    - food_population: Population weights for 241 segments
    - food_coding (optional): Category classifications for deeper analysis

    Returns:
    - Overall weighted NPS score
    - Promoter/Passive/Detractor distribution
    - Demographic breakdowns
    - Category response rates (if coding data available)
    """
    # Validate required data
    if data_store["food_qualtrics"] is None:
        raise HTTPException(status_code=400, detail="Food Qualtrics data not uploaded")
    if data_store["food_population"] is None:
        raise HTTPException(status_code=400, detail="Food population data not uploaded")

    try:
        result = food_nps.calculate_food_nps_with_weighting(
            qualtrics_df=data_store["food_qualtrics"],
            population_df=data_store["food_population"],
            coding_df=data_store["food_coding"]
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@app.get("/food-nps/status")
async def get_food_nps_status():
    """Check which Food NPS data files have been uploaded."""
    return {
        "qualtrics_uploaded": data_store["food_qualtrics"] is not None,
        "population_uploaded": data_store["food_population"] is not None,
        "coding_uploaded": data_store["food_coding"] is not None,
        "qualtrics_rows": len(data_store["food_qualtrics"]) if data_store["food_qualtrics"] is not None else 0,
        "population_segments": len(data_store["food_population"]) if data_store["food_population"] is not None else 0,
        "coding_rows": len(data_store["food_coding"]) if data_store["food_coding"] is not None else 0
    }

if __name__ == "__main__":
    import sys
    import os
    import tempfile
    
    # Write to a log file in the temp directory to avoid permission errors in .app bundle
    log_dir = tempfile.gettempdir()
    log_file = os.path.join(log_dir, "nps_backend_startup.log")
    
    try:
        with open(log_file, "w") as f:
            f.write(f"Starting backend from {os.getcwd()}...\n")
            f.write(f"Executable: {sys.executable}\n")
            
        import uvicorn
        import multiprocessing
        
        with open(log_file, "a") as f:
            f.write("Imports successful.\n")
            
        multiprocessing.freeze_support()
        
        with open(log_file, "a") as f:
            f.write("Starting uvicorn...\n")
            
        # Print to stdout so Electron can capture it too
        print(f"Backend logging to {log_file}", flush=True)
            
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        try:
            with open(log_file, "a") as f:
                f.write(f"Error: {str(e)}\n")
                import traceback
                traceback.print_exc(file=f)
        except:
            # If we can't even write to temp, just print to stderr
            print(f"Critical Error: {e}", file=sys.stderr)
