"""
Market data loader with reference/processed overlay support.
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from .io import load_csv, get_data_dir


def load_market_data() -> pd.DataFrame:
    """
    Load market data with reference/processed overlay pattern.
    
    Loads data/reference/market_research.csv (required)
    Overlays data/processed/market_research.csv if present (local overrides)
    
    Returns:
        DataFrame with market research data, processed taking precedence for duplicates
        
    Raises:
        FileNotFoundError: If reference file doesn't exist
    """
    data_dir = get_data_dir()
    reference_path = data_dir / "reference" / "market_research.csv"
    processed_path = data_dir / "processed" / "market_research.csv"
    
    # Reference data is required
    if not reference_path.exists():
        raise FileNotFoundError(f"Reference market data not found: {reference_path}")
    
    # Load reference data
    reference_df = load_csv(reference_path)
    
    # If no processed overlay, return reference data
    if not processed_path.exists():
        return reference_df
    
    # Load and overlay processed data
    try:
        processed_df = load_csv(processed_path)
        
        # Merge with processed taking precedence for duplicates
        # First identify the key column (likely city_key)
        key_col = 'city_key' if 'city_key' in reference_df.columns else reference_df.columns[0]
        
        # Combine data with processed overriding reference for same keys
        combined_df = reference_df.set_index(key_col)
        processed_indexed = processed_df.set_index(key_col)
        
        # Update with processed data (overwrites matching keys)
        combined_df.update(processed_indexed)
        
        # Add any new entries from processed that weren't in reference
        for idx in processed_indexed.index:
            if idx not in combined_df.index:
                combined_df.loc[idx] = processed_indexed.loc[idx]
        
        return combined_df.reset_index()
        
    except Exception as e:
        # If processed file is corrupted, warn and use reference only
        import warnings
        warnings.warn(f"Could not load processed market data ({e}), using reference only")
        return reference_df


def filter_allowed_markets(market_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter market data to only include allowed cities (Dubai, Cyprus, Greece).
    
    Args:
        market_df: DataFrame with market data
        
    Returns:
        Filtered DataFrame with only allowed cities
    """
    ALLOWED_CITIES = {
        # UAE
        "dubai",
        # Cyprus
        "limassol", "nicosia", "larnaca",
        # Greece
        "athens", "thessaloniki"
    }
    
    if 'city_key' not in market_df.columns:
        return market_df  # Return as-is if no city_key column
    
    # Filter to allowed cities (case-insensitive matching)
    filtered_df = market_df[
        market_df["city_key"].str.lower().isin(ALLOWED_CITIES)
    ].copy()
    
    return filtered_df


def get_available_cities() -> list[str]:
    """Get list of available cities from market data."""
    try:
        market_df = load_market_data()
        # Apply market restriction filter
        market_df = filter_allowed_markets(market_df)
        
        if 'city_key' in market_df.columns:
            return market_df['city_key'].tolist()
        else:
            return market_df.iloc[:, 0].tolist()  # First column as fallback
    except Exception:
        return []