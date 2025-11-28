import pandas as pd

def calculate_nps(df: pd.DataFrame, nps_column: str, weight_column: str = None) -> float:
    """
    Calculates NPS Score.
    NPS = % Promoters (9-10) - % Detractors (0-6)
    """
    if nps_column not in df.columns:
        return 0.0
        
    # Ensure numeric
    df[nps_column] = pd.to_numeric(df[nps_column], errors='coerce')
    valid_df = df.dropna(subset=[nps_column])
    
    if valid_df.empty:
        return 0.0

    if weight_column and weight_column in valid_df.columns:
        weights = valid_df[weight_column]
    else:
        weights = pd.Series([1] * len(valid_df), index=valid_df.index)

    total_weight = weights.sum()
    if total_weight == 0:
        return 0.0

    # Promoters: 9-10
    promoters_mask = valid_df[nps_column] >= 9
    promoters_weighted = weights[promoters_mask].sum()
    
    # Passives: 7-8
    passives_mask = (valid_df[nps_column] >= 7) & (valid_df[nps_column] <= 8)
    passives_weighted = weights[passives_mask].sum()
    
    # Detractors: 0-6
    detractors_mask = valid_df[nps_column] <= 6
    detractors_weighted = weights[detractors_mask].sum()
    
    # NPS = (Promoters % - Detractors %) * 100
    nps_score = ((promoters_weighted - detractors_weighted) / total_weight) * 100
    
    # Distribution (0-10)
    distribution = {}
    for score in range(11):
        score_mask = valid_df[nps_column] == score
        score_weighted = weights[score_mask].sum()
        distribution[str(score)] = {
            "count": round(score_weighted, 1),
            "percent": round((score_weighted / total_weight) * 100, 1)
        }
        
    return {
        "score": round(nps_score, 1),
        "breakdown": {
            "promoters": round((promoters_weighted / total_weight) * 100, 1),
            "passives": round((passives_weighted / total_weight) * 100, 1),
            "detractors": round((detractors_weighted / total_weight) * 100, 1)
        },
        "distribution": distribution,
        "total_weight": round(total_weight, 1)
    }

import re

def _extract_numeric_value(series: pd.Series) -> pd.Series:
    """
    Extracts numeric values from a series that might contain labels (e.g., "7 - Extremely satisfied").
    """
    # First, try direct numeric conversion
    numeric_series = pd.to_numeric(series, errors='coerce')
    
    # If we have a significant number of NaNs (and the original wasn't all NaN), try regex extraction
    if numeric_series.isna().sum() > 0 and series.notna().sum() > 0:
        # Regex to find the first integer in the string
        def extract_first_int(val):
            if pd.isna(val): return val
            match = re.search(r'(\d+)', str(val))
            return int(match.group(1)) if match else None
            
        # Apply regex only to non-numeric values (or just apply to all if mixed)
        # To be safe and handle "7 - Label", we can try applying to the string representation
        extracted = series.astype(str).apply(extract_first_int)
        
        # Combine: prefer the direct numeric if valid (though direct numeric on "7 - Label" is NaN)
        # So we should probably use the extracted version for anything that failed conversion
        # Or just use extracted version for everything if it looks like labels.
        
        # Let's fill NaNs in numeric_series with extracted values
        numeric_series = numeric_series.fillna(pd.to_numeric(extracted, errors='coerce'))
        
    return numeric_series

def calculate_top_3_box(df: pd.DataFrame, columns: list[str], weight_column: str = None) -> dict[str, float]:
    """
    Calculates Top 3 Box % for a 7-point scale (5, 6, 7) for multiple columns.
    Returns a dictionary {column_name: percentage}.
    """
    results = {}
    for col in columns:
        if col not in df.columns:
            results[col] = 0.0
            continue
            
        # Create a copy for this column's calculation to avoid messing up other iterations
        # Ensure numeric using robust extraction
        col_series = _extract_numeric_value(df[col])
        
        # We need to align weights with valid data for THIS column
        valid_mask = col_series.notna()
        
        if not valid_mask.any():
            results[col] = 0.0
            continue

        if weight_column and weight_column in df.columns:
            weights = df.loc[valid_mask, weight_column]
            values = col_series[valid_mask]
        else:
            values = col_series[valid_mask]
            weights = pd.Series([1] * len(values), index=values.index)

        total_weight = weights.sum()
        if total_weight == 0:
            results[col] = 0.0
            continue

        # Top 3 Box: 5, 6, 7
        top_box_mask = values >= 5
        top_box_weighted = weights[top_box_mask].sum()
        
        results[col] = round((top_box_weighted / total_weight) * 100, 1)
        
    return results

def calculate_response_rate(df: pd.DataFrame, columns: list[str], id_column: str = None, weight_column: str = None) -> dict[str, float]:
    """
    Calculates response rate (non-empty / total) for multiple columns.
    If id_column is provided, calculates based on unique respondents.
    If weight_column is provided, calculates weighted response rate.
    """
    results = {}
    
    if df.empty:
        return {col: 0.0 for col in columns}

    # Determine Total Base
    if id_column and id_column in df.columns:
        # Respondent-based
        if weight_column and weight_column in df.columns:
            # Weighted Unique Respondents
            # We need one weight per ID. Assuming weight is constant per ID.
            unique_weights = df[[id_column, weight_column]].drop_duplicates(subset=[id_column])
            total = unique_weights[weight_column].sum()
        else:
            # Unweighted Unique Respondents
            total = df[id_column].nunique()
    else:
        # Row-based (fallback or for simple data)
        if weight_column and weight_column in df.columns:
            total = df[weight_column].sum()
        else:
            total = len(df)
    
    if total == 0:
        return {col: 0.0 for col in columns}

    for col in columns:
        if col not in df.columns:
            results[col] = 0.0
            continue
            
        # Filter non-empty
        # We consider a respondent "responded" if they have at least one non-empty row for this column
        valid_mask = df[col].notna() & (df[col].astype(str).str.strip() != '')
        valid_df = df[valid_mask]
        
        if id_column and id_column in df.columns:
            if weight_column and weight_column in df.columns:
                # Weighted Unique Respondents who answered
                unique_responders = valid_df[[id_column, weight_column]].drop_duplicates(subset=[id_column])
                count = unique_responders[weight_column].sum()
            else:
                count = valid_df[id_column].nunique()
        else:
            if weight_column and weight_column in df.columns:
                count = df.loc[valid_mask, weight_column].sum()
            else:
                count = len(valid_df)
        
        results[col] = round((count / total) * 100, 1)
        
    return results

def calculate_category_stats(df: pd.DataFrame, column: str, id_column: str = None, weight_column: str = None, parent_column: str = None) -> dict[str, float]:
    """
    Calculates the percentage of respondents who mentioned each category in the given column.
    Handles multi-row data (one respondent can have multiple categories).
    If parent_column is provided, keys will be formatted as "Category (Parent)".
    """
    if df.empty or column not in df.columns:
        return {}

    # 1. Determine Total Base (Unique Respondents)
    # Reverted to use Total Segment Population (Incidence Rate) as requested.
    if id_column and id_column in df.columns:
        if weight_column and weight_column in df.columns:
            # Weighted Unique Respondents
            unique_weights = df[[id_column, weight_column]].drop_duplicates(subset=[id_column])
            total_base = unique_weights[weight_column].sum()
        else:
            total_base = df[id_column].nunique()
    else:
        # Fallback: Total rows
        if weight_column and weight_column in df.columns:
            total_base = df[weight_column].sum()
        else:
            total_base = len(df)

    if total_base == 0:
        return {}

    # Filter out empty categories for numerator calculation
    valid_df = df[df[column].notna() & (df[column].astype(str).str.strip() != '')].copy()
    
    if valid_df.empty:
        return {}

    stats = {}
    
    if parent_column and parent_column in df.columns:
        # Group by Parent and Category
        # Get unique pairs
        pairs = valid_df[[parent_column, column]].drop_duplicates()
        
        for _, row in pairs.iterrows():
            parent = row[parent_column]
            cat = row[column]
            
            # Filter for this specific pair
            cat_df = valid_df[(valid_df[parent_column] == parent) & (valid_df[column] == cat)]
            
            if id_column and id_column in df.columns:
                if weight_column and weight_column in df.columns:
                    unique_responders = cat_df[[id_column, weight_column]].drop_duplicates(subset=[id_column])
                    count = unique_responders[weight_column].sum()
                else:
                    count = cat_df[id_column].nunique()
            else:
                if weight_column and weight_column in df.columns:
                    count = cat_df[weight_column].sum()
                else:
                    count = len(cat_df)
            
            # Format key: "Sub (Parent)"
            key = f"{cat} ({parent})"
            stats[key] = round((count / total_base) * 100, 1)
            
    else:
        # Original logic: Group by Category only
        categories = valid_df[column].unique()
        
        for cat in categories:
            cat_df = valid_df[valid_df[column] == cat]
            
            if id_column and id_column in df.columns:
                if weight_column and weight_column in df.columns:
                    unique_responders = cat_df[[id_column, weight_column]].drop_duplicates(subset=[id_column])
                    count = unique_responders[weight_column].sum()
                else:
                    count = cat_df[id_column].nunique()
            else:
                if weight_column and weight_column in df.columns:
                    count = cat_df[weight_column].sum()
                else:
                    count = len(cat_df)
            
            stats[str(cat)] = round((count / total_base) * 100, 1)
        
    # Sort by percentage descending
    return dict(sorted(stats.items(), key=lambda item: item[1], reverse=True))
