"""
Test market data overlay functionality.

NOTE: This test file is for overlay functionality (reference + processed file merging)
which has been moved out of utils.market_loader as per architectural cleanup.
These tests are commented out until the overlay functionality is implemented
in a separate module (e.g., utils/overlay_loader.py).
"""

# import pytest
# import pandas as pd
# import tempfile
# from pathlib import Path
# from unittest.mock import patch

# from utils.market_loader import load_market_data, get_available_cities


# Overlay tests commented out until overlay functionality is implemented
# in a separate module per architectural cleanup requirements

# class TestMarketOverlay:
    """Test market data reference/processed overlay pattern."""
    
    def test_reference_only(self):
        """Test loading when only reference file exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create reference directory and file
            ref_dir = temp_path / "reference"
            ref_dir.mkdir()
            
            reference_data = pd.DataFrame({
                'city_key': ['toronto', 'vancouver'],
                'land_comp_avg': [500, 400],
                'sale_price_avg': [5200, 6000]
            })
            reference_data.to_csv(ref_dir / "market_research.csv", index=False)
            
            # Mock get_data_dir to return our temp directory
            with patch('utils.market_loader.get_data_dir', return_value=temp_path):
                result_df = load_market_data()
                
                assert len(result_df) == 2
                assert 'toronto' in result_df['city_key'].values
                assert 'vancouver' in result_df['city_key'].values
                assert result_df[result_df['city_key'] == 'toronto']['sale_price_avg'].iloc[0] == 5200
    
    def test_processed_overlay(self):
        """Test overlay when both reference and processed files exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create reference directory and file
            ref_dir = temp_path / "reference"
            ref_dir.mkdir()
            reference_data = pd.DataFrame({
                'city_key': ['toronto', 'vancouver', 'calgary'],
                'land_comp_avg': [500, 400, 350],
                'sale_price_avg': [5200, 6000, 4200]
            })
            reference_data.to_csv(ref_dir / "market_research.csv", index=False)
            
            # Create processed directory and file with overrides
            proc_dir = temp_path / "processed"  
            proc_dir.mkdir()
            processed_data = pd.DataFrame({
                'city_key': ['toronto', 'dubai_downtown'],  # Override toronto, add new city
                'land_comp_avg': [600, 1200],  # Toronto override: 500->600
                'sale_price_avg': [5500, 8500]  # Toronto override: 5200->5500
            })
            processed_data.to_csv(proc_dir / "market_research.csv", index=False)
            
            # Mock get_data_dir to return our temp directory
            with patch('utils.market_loader.get_data_dir', return_value=temp_path):
                result_df = load_market_data()
                
                # Check union of cities: reference (toronto, vancouver, calgary) + processed (dubai_downtown)
                # toronto should be overridden by processed values
                expected_cities = {'toronto', 'vancouver', 'calgary', 'dubai_downtown'}
                actual_cities = set(result_df['city_key'].values)
                assert actual_cities == expected_cities
                
                # Check toronto was overridden by processed values
                toronto_row = result_df[result_df['city_key'] == 'toronto'].iloc[0]
                assert toronto_row['land_comp_avg'] == 600  # Processed value
                assert toronto_row['sale_price_avg'] == 5500  # Processed value
                
                # Check vancouver kept reference values
                vancouver_row = result_df[result_df['city_key'] == 'vancouver'].iloc[0]
                assert vancouver_row['land_comp_avg'] == 400  # Reference value
                assert vancouver_row['sale_price_avg'] == 6000  # Reference value
                
                # Check new city from processed
                dubai_row = result_df[result_df['city_key'] == 'dubai_downtown'].iloc[0]
                assert dubai_row['land_comp_avg'] == 1200
                assert dubai_row['sale_price_avg'] == 8500
    
    def test_processed_precedence_for_duplicates(self):
        """Test that processed data takes precedence for duplicate cities.""" 
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create reference directory and file
            ref_dir = temp_path / "reference"
            ref_dir.mkdir()
            reference_data = pd.DataFrame({
                'city_key': ['toronto'],
                'land_comp_avg': [500],
                'sale_price_avg': [5200],
                'demand_score': [4]
            })
            reference_data.to_csv(ref_dir / "market_research.csv", index=False)
            
            # Create processed directory with same city but different values
            proc_dir = temp_path / "processed"
            proc_dir.mkdir()
            processed_data = pd.DataFrame({
                'city_key': ['toronto'],
                'land_comp_avg': [700],  # Different from reference
                'sale_price_avg': [5800],  # Different from reference  
                'demand_score': [5]  # Different from reference
            })
            processed_data.to_csv(proc_dir / "market_research.csv", index=False)
            
            # Mock get_data_dir to return our temp directory
            with patch('utils.market_loader.get_data_dir', return_value=temp_path):
                result_df = load_market_data()
                
                # Should have only one toronto row with processed values
                assert len(result_df) == 1
                toronto_row = result_df.iloc[0]
                assert toronto_row['city_key'] == 'toronto'
                assert toronto_row['land_comp_avg'] == 700  # Processed wins
                assert toronto_row['sale_price_avg'] == 5800  # Processed wins
                assert toronto_row['demand_score'] == 5  # Processed wins
    
    def test_get_available_cities(self):
        """Test that get_available_cities returns correct city list."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create reference directory and file
            ref_dir = temp_path / "reference"
            ref_dir.mkdir()
            reference_data = pd.DataFrame({
                'city_key': ['toronto', 'vancouver', 'calgary'],
                'land_comp_avg': [500, 400, 350]
            })
            reference_data.to_csv(ref_dir / "market_research.csv", index=False)
            
            # Mock get_data_dir to return our temp directory
            with patch('utils.market_loader.get_data_dir', return_value=temp_path):
                cities = get_available_cities()
                
                expected_cities = ['toronto', 'vancouver', 'calgary']
                assert sorted(cities) == sorted(expected_cities)
    
    def test_missing_reference_file_error(self):
        """Test that missing reference file raises FileNotFoundError."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Don't create reference file, only processed
            proc_dir = temp_path / "processed"
            proc_dir.mkdir()
            processed_data = pd.DataFrame({'city_key': ['toronto']})
            processed_data.to_csv(proc_dir / "market_research.csv", index=False)
            
            # Mock get_data_dir to return our temp directory
            with patch('utils.market_loader.get_data_dir', return_value=temp_path):
                with pytest.raises(FileNotFoundError, match="Reference market data not found"):
                    load_market_data()