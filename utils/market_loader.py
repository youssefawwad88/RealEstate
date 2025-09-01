"""
Market data loading utilities for TerraFlow v2.
Infrastructure helpers with no UI dependencies.
"""
import pandas as pd
from pathlib import Path
from typing import List, Optional, Tuple
import os

# Constants
ALLOWED_MARKETS_DEFAULT = ("dubai", "greece", "cyprus")
REFERENCE_PATH = os.getenv("MARKET_RESEARCH_PATH", "data/reference/market_research.csv")
EXPECTED_COLS = [
    "city_key", "land_comp_min", "land_comp_avg", "land_comp_max", 
    "sale_price_min", "sale_price_avg", "sale_price_max",
    "construction_cost_min", "construction_cost_avg", "construction_cost_max",
    "soft_cost_pct_typical", "absorption_rate", "land_gdv_benchmark", 
    "profit_margin_benchmark", "demand_score", "liquidity_score", 
    "volatility_score", "last_updated"
]


def load_market_benchmarks(path: Optional[str] = None) -> pd.DataFrame:
    """
    Load market benchmarks CSV with proper schema.
    
    Args:
        path: Optional path override. If None, uses REFERENCE_PATH
        
    Returns:
        DataFrame with market data or empty DataFrame with expected schema if file missing
    """
    if path is None:
        path = REFERENCE_PATH
    
    file_path = Path(path)
    
    if not file_path.exists():
        # Return empty DataFrame with expected schema
        return pd.DataFrame(columns=EXPECTED_COLS)
    
    try:
        df = pd.read_csv(file_path)
        
        # Validate schema - ensure all expected columns exist
        missing_cols = set(EXPECTED_COLS) - set(df.columns)
        if missing_cols:
            # Add missing columns with default values
            for col in missing_cols:
                df[col] = None
        
        # Ensure columns are in expected order
        df = df[EXPECTED_COLS]
        
        return df
        
    except Exception:
        # If any error occurs, return empty DataFrame with schema
        return pd.DataFrame(columns=EXPECTED_COLS)


def filter_allowed_markets(
    df: pd.DataFrame, 
    allowed: Optional[Tuple[str, ...]] = None
) -> pd.DataFrame:
    """
    Filter DataFrame to only include allowed markets.
    
    Args:
        df: DataFrame with city_key column
        allowed: Tuple of allowed city keys. If None, uses ALLOWED_MARKETS_DEFAULT
        
    Returns:
        Filtered DataFrame with case-insensitive matching
    """
    if allowed is None:
        allowed = ALLOWED_MARKETS_DEFAULT
    
    if df.empty or 'city_key' not in df.columns:
        return df
    
    # Case-insensitive filtering
    allowed_lower = [city.lower() for city in allowed]
    mask = df['city_key'].str.lower().isin(allowed_lower)
    
    return df[mask].copy()