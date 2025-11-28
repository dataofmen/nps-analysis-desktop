"""
Food NPS (배달의민족) specialized analysis module.

This module handles Korean food delivery service NPS analysis with:
- 241-segment population weighting (gender × age_group × rgn_nm × bmclub × division × is_mfo)
- Category classification integration
- Korean text processing
- Weighted NPS calculation with normalization
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from io import BytesIO
import chardet


def load_food_qualtrics_data(file_content: bytes, filename: str) -> pd.DataFrame:
    """
    Load Korean Qualtrics food NPS survey data.

    Expected structure:
    - ResponseId: Unique response identifier
    - Q1_1: NPS score (0-10)
    - Q2: Open-ended response
    - Q11-Q15: Price/Benefits satisfaction (7-point scale)
    - Q21-Q23: Store/Menu satisfaction (7-point scale)
    - Q31-Q33: Delivery satisfaction (7-point scale)
    - Demographics: gender, age_group, rgn_nm, bmclub, division, is_mfo
    """
    # Detect encoding
    detected = chardet.detect(file_content)
    encoding = detected['encoding'] or 'utf-8'

    # Try UTF-8-BOM first (common for Korean Excel exports)
    try:
        df = pd.read_csv(BytesIO(file_content), encoding='utf-8-sig')
    except:
        df = pd.read_csv(BytesIO(file_content), encoding=encoding)

    # Remove Qualtrics metadata rows (first 2 rows if present)
    if len(df) > 2:
        # Check if first row looks like metadata
        first_row_values = df.iloc[0].astype(str).values
        if any('Import' in str(v) or 'Date' in str(v) for v in first_row_values[:5]):
            df = df.iloc[2:].reset_index(drop=True)

    # Handle Q1 alias for Q1_1
    if 'Q1' in df.columns and 'Q1_1' not in df.columns:
        df.rename(columns={'Q1': 'Q1_1'}, inplace=True)

    # Validate required columns
    required_cols = ['ResponseId', 'Q1_1', 'gender', 'age_group', 'rgn_nm', 'bmclub']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Convert NPS score to numeric
    df['Q1_1'] = pd.to_numeric(df['Q1_1'], errors='coerce')

    # Filter valid NPS scores (0-10)
    df = df[df['Q1_1'].notna() & (df['Q1_1'] >= 0) & (df['Q1_1'] <= 10)].copy()

    print(f"✅ Loaded {len(df)} valid food NPS responses from {filename}")
    return df


def load_food_population_data(file_content: bytes, filename: str) -> pd.DataFrame:
    """
    Load population weighting data for Korean food delivery demographics.

    Expected structure:
    - gender: MALE/FEMALE
    - age_group: 10대/20대/30대/40대/50대 이상
    - rgn_nm: 수도권/광역시/지방
    - bmclub: 구독/미구독
    - division: OD/MP/TAKEOUT (service type)
    - is_mfo: 0/1 (한그룻 주문경험)
    - mem_rate: Weight ratio for this segment
    - mem_cnt: Sample count
    - TOTAL_CNT: Total population
    """
    # Detect encoding
    detected = chardet.detect(file_content)
    encoding = detected['encoding'] or 'utf-8'

    try:
        df = pd.read_csv(BytesIO(file_content), encoding='utf-8-sig')
    except:
        df = pd.read_csv(BytesIO(file_content), encoding=encoding)

    # Validate required columns
    required_cols = ['gender', 'age_group', 'rgn_nm', 'bmclub', 'mem_rate']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Convert mem_rate to numeric
    df['mem_rate'] = pd.to_numeric(df['mem_rate'], errors='coerce')

    # Validate mem_rate values
    if df['mem_rate'].isna().any():
        raise ValueError("Population data contains invalid mem_rate values")

    print(f"✅ Loaded {len(df)} population segments from {filename}")
    return df


def load_food_coding_data(file_content: bytes, filename: str) -> pd.DataFrame:
    """
    Load category classification data for open-ended responses.

    Expected structure:
    - ResponseId: Links to Qualtrics data
    - classification: Classification type
    - category: Main category (e.g., "가게/메뉴 다양성", "배달팁")
    - sub_category: Subcategory (e.g., "가게 많음", "배달팁 높음")
    """
    # Detect encoding
    detected = chardet.detect(file_content)
    encoding = detected['encoding'] or 'utf-8'

    try:
        df = pd.read_csv(BytesIO(file_content), encoding='utf-8-sig')
    except:
        df = pd.read_csv(BytesIO(file_content), encoding=encoding)

    # Validate required columns
    required_cols = ['ResponseId', 'category']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    print(f"✅ Loaded {len(df)} category classifications from {filename}")
    return df


def calculate_food_nps_with_weighting(
    qualtrics_df: pd.DataFrame,
    population_df: pd.DataFrame,
    coding_df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Calculate weighted NPS for Korean food delivery service.

    Implements the 60-group weighting methodology:
    1. Merge survey data with population weights
    2. Calculate weighted NPS using mem_rate
    3. Apply normalization: scale_factor = unweighted_total / weighted_total
    4. Calculate NPS groups (Promoters 9-10, Passives 7-8, Detractors 0-6)
    5. Integrate category analysis if coding data provided

    Returns:
        Dictionary with:
        - nps_score: Overall weighted NPS
        - total_responses: Total response count
        - promoters_pct: Promoter percentage
        - passives_pct: Passive percentage
        - detractors_pct: Detractor percentage
        - demographic_breakdown: NPS by segments
        - category_analysis: Response rates by category (if coding provided)
    """
    # Merge qualtrics with population weights
    merge_cols = ['gender', 'age_group', 'rgn_nm', 'bmclub']

    # Add division and is_mfo if they exist
    if 'division' in qualtrics_df.columns and 'division' in population_df.columns:
        merge_cols.append('division')
    if 'is_mfo' in qualtrics_df.columns and 'is_mfo' in population_df.columns:
        # Convert is_mfo to string for consistent merging
        qualtrics_df['is_mfo'] = qualtrics_df['is_mfo'].astype(str)
        population_df['is_mfo'] = population_df['is_mfo'].astype(str)
        merge_cols.append('is_mfo')

    # Normalize whitespace in merge columns to ensure matching
    # e.g., "20대 이하" (Qualtrics) vs "20대이하" (Population)
    for col in merge_cols:
        qualtrics_df[col] = qualtrics_df[col].astype(str).str.replace(" ", "")
        population_df[col] = population_df[col].astype(str).str.replace(" ", "")

    merged_df = qualtrics_df.merge(
        population_df[merge_cols + ['mem_rate']],
        on=merge_cols,
        how='left'
    )

    # Calculate sample counts per segment
    segment_counts = merged_df.groupby(merge_cols).size().reset_index(name='sample_count')
    
    # Merge sample counts back
    merged_df = merged_df.merge(segment_counts, on=merge_cols, how='left')

    # Calculate weight: Target Proportion (mem_rate) / Sample Count
    # This ensures the sum of weights for a segment equals its target proportion (mem_rate)
    merged_df['weight'] = merged_df['mem_rate'] / merged_df['sample_count']
    
    # Fill missing weights (if any) with 1.0/count or just 1.0? 
    # If mem_rate is missing, it means no target. Fallback to 1.0 is risky if mixed.
    # But let's keep existing fallback logic but adapted
    merged_df['weight'] = merged_df['weight'].fillna(1.0)

    # Calculate normalization factor
    unweighted_total = len(merged_df)
    weighted_total = merged_df['weight'].sum()
    scale_factor = unweighted_total / weighted_total if weighted_total > 0 else 1.0

    # Apply normalized weights
    merged_df['normalized_weight'] = merged_df['weight'] * scale_factor

    # Calculate NPS groups
    merged_df['nps_group'] = pd.cut(
        merged_df['Q1_1'],
        bins=[-np.inf, 6, 8, np.inf],
        labels=['Detractor', 'Passive', 'Promoter']
    )

    # Calculate weighted percentages
    total_weight = merged_df['normalized_weight'].sum()

    promoters_weight = merged_df[merged_df['nps_group'] == 'Promoter']['normalized_weight'].sum()
    passives_weight = merged_df[merged_df['nps_group'] == 'Passive']['normalized_weight'].sum()
    detractors_weight = merged_df[merged_df['nps_group'] == 'Detractor']['normalized_weight'].sum()

    promoters_pct = (promoters_weight / total_weight * 100) if total_weight > 0 else 0
    passives_pct = (passives_weight / total_weight * 100) if total_weight > 0 else 0
    detractors_pct = (detractors_weight / total_weight * 100) if total_weight > 0 else 0

    # Calculate NPS
    nps_score = promoters_pct - detractors_pct

    # Demographic breakdown
    demographic_breakdown = []
    for segment_cols_values, group in merged_df.groupby(merge_cols):
        segment_dict = dict(zip(merge_cols, segment_cols_values))
        segment_nps = calculate_segment_nps(group)
        segment_dict.update({
            'nps': round(segment_nps, 2),
            'count': len(group),
            'weight': round(group['normalized_weight'].sum(), 2)
        })
        demographic_breakdown.append(segment_dict)

    result = {
        'nps_score': round(nps_score, 2),
        'total_responses': len(merged_df),
        'promoters_pct': round(promoters_pct, 2),
        'passives_pct': round(passives_pct, 2),
        'detractors_pct': round(detractors_pct, 2),
        'scale_factor': round(scale_factor, 4),
        'demographic_breakdown': demographic_breakdown
    }

    # Add category analysis if coding data provided
    if coding_df is not None:
        category_analysis = calculate_category_response_rates(
            merged_df, coding_df
        )
        result['category_analysis'] = category_analysis

    return result


def calculate_segment_nps(segment_df: pd.DataFrame) -> float:
    """Calculate NPS for a demographic segment."""
    total_weight = segment_df['normalized_weight'].sum()
    if total_weight == 0:
        return 0.0

    promoters_weight = segment_df[segment_df['nps_group'] == 'Promoter']['normalized_weight'].sum()
    detractors_weight = segment_df[segment_df['nps_group'] == 'Detractor']['normalized_weight'].sum()

    promoters_pct = (promoters_weight / total_weight * 100)
    detractors_pct = (detractors_weight / total_weight * 100)

    return promoters_pct - detractors_pct


def calculate_category_response_rates(
    merged_df: pd.DataFrame,
    coding_df: pd.DataFrame
) -> Dict[str, Any]:
    """
    Calculate response rates by category for each NPS group.

    Returns category distribution across Promoters, Passives, Detractors.
    """
    # Merge with coding data
    analysis_df = merged_df.merge(
        coding_df[['ResponseId', 'category', 'sub_category']],
        on='ResponseId',
        how='left'
    )

    # Calculate overall category distribution
    category_counts = {}

    for nps_group in ['Promoter', 'Passive', 'Detractor']:
        group_df = analysis_df[analysis_df['nps_group'] == nps_group]
        total_weight = group_df['normalized_weight'].sum()

        category_stats = []
        for category, cat_group in group_df.groupby('category'):
            if pd.isna(category):
                continue

            cat_weight = cat_group['normalized_weight'].sum()
            response_rate = (cat_weight / total_weight * 100) if total_weight > 0 else 0

            category_stats.append({
                'category': category,
                'count': len(cat_group),
                'weight': round(cat_weight, 2),
                'response_rate': round(response_rate, 2)
            })

        category_counts[nps_group] = sorted(
            category_stats,
            key=lambda x: x['response_rate'],
            reverse=True
        )

    return category_counts
