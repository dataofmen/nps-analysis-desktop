import pandas as pd

def get_segment_counts(df: pd.DataFrame, segment_columns: list[str]) -> list[str]:
    """
    Returns a list of unique segments found in the dataframe based on the specified columns.
    """
    if not segment_columns:
        return []
        
    # Check if columns exist
    missing = [col for col in segment_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Create segment series
    if len(segment_columns) == 1:
        segments = df[segment_columns[0]].astype(str).str.replace(" ", "")
    else:
        segments = df[segment_columns].astype(str).apply(lambda x: x.str.replace(" ", "")).agg('_'.join, axis=1)
        
    return sorted(segments.unique().tolist())

def assess_weight_risk(weight):
    """
    Assess the risk level of a weight value.
    Based on practical criteria:
    - Best: < 1.5
    - Good: 1.5 <= weight < 2.0
    - Acceptable: 2.0 <= weight < 3.0
    - Risk: 3.0 <= weight < 5.0
    - Critical: >= 5.0
    """
    if weight < 1.5:
        return 'Best'
    elif weight < 2.0:
        return 'Good'
    elif weight < 3.0:
        return 'Acceptable'
    elif weight < 5.0:
        return 'Risk'
    else:
        return 'Critical'

def calculate_weights(df: pd.DataFrame, config: WeightingConfig) -> pd.DataFrame:
    """
    Calculates weights based on cell-based weighting.
    
    Args:
        df: The survey data.
        segment_columns: List of columns to combine to form the segment (e.g. ['Age', 'Gender']).
        targets: Dictionary where key is the segment value (joined by '_') and value is the target proportion (0-1).
                 Example: {'18-24_Male': 0.1, '25-34_Female': 0.15}
                 
    Returns:
        DataFrame with a new 'Weight' column.
    """
    df = df.copy()
    
    # Create a segment column
    if len(segment_columns) == 1:
        df['Segment'] = df[segment_columns[0]].astype(str).str.replace(" ", "")
    else:
        # Apply whitespace removal to each column before joining
        df['Segment'] = df[segment_columns].astype(str).apply(lambda x: x.str.replace(" ", "")).agg('_'.join, axis=1)
        
    # Calculate Sample Proportions
    total_count = len(df)
    sample_counts = df['Segment'].value_counts()
    
    # Calculate Weights
    def get_weight(segment):
        target_prop = targets.get(segment, 0)
        sample_count = sample_counts.get(segment, 0)
        sample_prop = sample_count / total_count if total_count > 0 else 0
        
        if sample_prop == 0:
            return 0 
        
        return target_prop / sample_prop

    df['Weight'] = df['Segment'].apply(get_weight)
    
    # Normalize weights so mean is 1 (preserves total N)
    if df['Weight'].mean() > 0:
        df['Weight'] = df['Weight'] / df['Weight'].mean()
        
    return df

def calculate_targets(pop_df: pd.DataFrame, segment_columns: list[str], target_column: str = None) -> dict[str, float]:
    """
    Calculates target proportions from population data.
    """
    # Check if columns exist
    missing = [col for col in segment_columns if col not in pop_df.columns]
    if missing:
        return {}

    df = pop_df.copy()
    
    # Create segment column
    if len(segment_columns) == 1:
        df['Segment'] = df[segment_columns[0]].astype(str).str.replace(" ", "")
    else:
        df['Segment'] = df[segment_columns].astype(str).apply(lambda x: x.str.replace(" ", "")).agg('_'.join, axis=1)
        
    # Calculate weights/counts
    if target_column and target_column in df.columns:
        # Use the specified column as weight (e.g. mem_rate)
        df[target_column] = pd.to_numeric(df[target_column], errors='coerce').fillna(0)
        segment_sums = df.groupby('Segment')[target_column].sum()
    else:
        # Just count rows
        segment_sums = df['Segment'].value_counts()
        
    total = segment_sums.sum()
    if total == 0:
        return {}
        
    proportions = (segment_sums / total).to_dict()
    return {k: round(v, 4) for k, v in proportions.items()}
