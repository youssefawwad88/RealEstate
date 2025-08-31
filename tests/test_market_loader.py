"""
Test market loader functionality.
"""
import pandas as pd
import tempfile
import os
from pathlib import Path
from utils.market_loader import (
    load_market_benchmarks, 
    filter_allowed_markets,
    ALLOWED_MARKETS_DEFAULT,
    EXPECTED_COLS
)


def test_loader_imports_and_constants():
    """Test that loader imports correctly and has required constants."""
    # Test constants exist
    assert ALLOWED_MARKETS_DEFAULT == ("dubai", "greece", "cyprus")
    assert isinstance(EXPECTED_COLS, list)
    assert "city_key" in EXPECTED_COLS
    assert "absorption_rate" in EXPECTED_COLS


def test_load_market_benchmarks_missing_file():
    """Test loader handles missing file gracefully."""
    with tempfile.TemporaryDirectory() as temp_dir:
        missing_file = os.path.join(temp_dir, "nonexistent.csv")
        df = load_market_benchmarks(missing_file)
        
        # Should return empty DataFrame with expected schema
        assert df.empty
        assert list(df.columns) == EXPECTED_COLS


def test_load_market_benchmarks_valid_file():
    """Test loader with valid CSV file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        # Write test CSV data
        f.write("city_key,absorption_rate,sale_price_avg,construction_cost_avg,land_comp_avg,land_comp_min,land_comp_max,sale_price_min,sale_price_max,construction_cost_min,construction_cost_max,soft_cost_pct_typical,land_gdv_benchmark,profit_margin_benchmark,demand_score,liquidity_score,volatility_score,last_updated\n")
        f.write("dubai,12,7500,2800,650,400,1200,5000,12000,2000,3500,0.16,0.25,0.18,5,5,3,2025-01-01\n")
        f.write("greece,24,4200,2100,350,200,600,2800,6500,1500,2800,0.18,0.28,0.16,3,3,4,2025-01-01\n")
        f.flush()
        
        try:
            df = load_market_benchmarks(f.name)
            
            # Should load successfully
            assert not df.empty
            assert len(df) == 2
            assert "dubai" in df['city_key'].values
            assert "greece" in df['city_key'].values
            
            # Check data types and values
            assert df.loc[df['city_key'] == 'dubai', 'absorption_rate'].iloc[0] == 12
            assert df.loc[df['city_key'] == 'greece', 'absorption_rate'].iloc[0] == 24
            
        finally:
            os.unlink(f.name)


def test_filter_allowed_markets():
    """Test market filtering functionality."""
    # Create test DataFrame
    test_data = pd.DataFrame({
        'city_key': ['dubai', 'GREECE', 'Cyprus', 'london', 'paris'],
        'absorption_rate': [12, 24, 18, 15, 20],
        'sale_price_avg': [7500, 4200, 4800, 8000, 9000]
    })
    
    # Test default filtering (should include D/G/C case-insensitively)
    filtered = filter_allowed_markets(test_data)
    assert len(filtered) == 3
    
    expected_cities = {'dubai', 'greece', 'cyprus'}  # lowercase
    actual_cities = set(filtered['city_key'].str.lower())
    assert actual_cities == expected_cities
    
    # Test custom allowed markets
    custom_allowed = ('london', 'paris')
    custom_filtered = filter_allowed_markets(test_data, allowed=custom_allowed)
    assert len(custom_filtered) == 2
    assert 'london' in custom_filtered['city_key'].values
    assert 'paris' in custom_filtered['city_key'].values


def test_filter_empty_dataframe():
    """Test filtering with empty DataFrame."""
    empty_df = pd.DataFrame()
    result = filter_allowed_markets(empty_df)
    assert result.empty


def test_filter_missing_city_key():
    """Test filtering with DataFrame missing city_key column."""
    df_no_city = pd.DataFrame({
        'name': ['test1', 'test2'],
        'value': [1, 2]
    })
    
    result = filter_allowed_markets(df_no_city)
    # Should return original DataFrame unchanged
    assert len(result) == 2
    assert list(result.columns) == ['name', 'value']


def test_case_insensitive_filtering():
    """Test that filtering works case-insensitively."""
    test_data = pd.DataFrame({
        'city_key': ['DUBAI', 'Greece', 'cYpRuS', 'OTHER'],
        'value': [1, 2, 3, 4]
    })
    
    filtered = filter_allowed_markets(test_data)
    assert len(filtered) == 3
    
    # Original case should be preserved
    cities = set(filtered['city_key'])
    assert cities == {'DUBAI', 'Greece', 'cYpRuS'}