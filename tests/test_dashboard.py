"""
Tests for the Streamlit dashboard functionality.
Tests the core workflow of deal analysis, market data, and CSV operations.
"""

import pytest
import pandas as pd
import tempfile
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from modules.deal_model import create_deal_from_dict
from modules.market_lookup import get_available_cities, get_market_summary
from utils.io import load_csv, save_csv, get_data_dir
from utils.scoring import format_currency, get_color_indicator


class TestDashboardIntegration:
    """Test dashboard integration functionality."""
    
    def test_deal_analysis_workflow(self):
        """Test the complete deal analysis workflow used by Add Deal page."""
        
        # Sample deal inputs matching the dashboard form
        deal_inputs = {
            'site_name': 'Test Dashboard Site',
            'land_area_sqm': 1200.0,
            'asking_price': 600000.0,
            'taxes_fees': 30000.0,
            'zoning': 'Residential',
            'far': 1.6,
            'coverage': 0.45,
            'max_floors': 4,
            'efficiency_ratio': 0.85,
            'expected_sale_price_psm': 4200.0,
            'construction_cost_psm': 2100.0,
            'soft_cost_pct': 0.16,
            'profit_target_pct': 0.20,
            'financing_cost': 45000.0,
            'holding_period_months': 30,
            'access_width_m': 6.0,
            'utilities': 'Full'
        }
        
        # Test deal analysis
        deal = create_deal_from_dict(deal_inputs)
        
        # Verify key outputs exist
        assert deal.outputs is not None
        assert deal.outputs.residual_land_value > 0
        assert deal.outputs.gdv > 0
        assert deal.outputs.land_pct_gdv > 0
        assert deal.outputs.breakeven_sale_price > 0
        
        # Test viability scoring
        assert deal.viability is not None
        assert deal.viability.overall_score in ['green', 'yellow', 'red']
        assert deal.viability.overall_status is not None
        
        # Test sensitivity analysis
        assert deal.sensitivity is not None
        assert deal.sensitivity.base_residual > 0
    
    def test_market_research_data_loading(self):
        """Test market research CSV data loading."""
        
        # Test market research file exists
        market_research_path = get_data_dir() / "processed" / "market_research.csv"
        assert market_research_path.exists(), "Market research CSV should exist"
        
        # Load and validate structure
        market_df = load_csv(market_research_path)
        
        # Check required columns
        required_columns = [
            'city_key', 'land_comp_avg', 'sale_price_avg', 
            'construction_cost_avg', 'demand_score', 'last_updated'
        ]
        
        for col in required_columns:
            assert col in market_df.columns, f"Column {col} missing from market research data"
        
        # Verify data types
        assert len(market_df) > 0, "Market research should have data"
        assert market_df['city_key'].dtype == 'object'
        assert pd.api.types.is_numeric_dtype(market_df['land_comp_avg'])
        assert pd.api.types.is_numeric_dtype(market_df['sale_price_avg'])
    
    def test_city_selection_from_market_data(self):
        """Test city selection functionality used by benchmarks page."""
        
        # Load market research data
        market_research_path = get_data_dir() / "processed" / "market_research.csv"
        market_df = load_csv(market_research_path)
        
        # Get available cities
        available_cities = sorted(market_df['city_key'].unique().tolist())
        
        # Verify cities exist
        assert len(available_cities) > 0
        assert 'default' in available_cities
        
        # Test city data retrieval
        for city in available_cities[:3]:  # Test first 3 cities
            city_data = market_df[market_df['city_key'] == city]
            assert not city_data.empty, f"Data should exist for city {city}"
            
            city_row = city_data.iloc[0]
            assert city_row['land_comp_avg'] > 0
            assert city_row['sale_price_avg'] > 0
    
    def test_csv_append_functionality(self):
        """Test CSV append functionality used by Pipeline page."""
        
        # Create temporary file for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            test_csv_path = Path(temp_dir) / "test_acquisitions.csv"
            
            # Create initial data
            initial_data = pd.DataFrame([{
                'site_name': 'Site 1',
                'asking_price': 500000,
                'residual_land_value': 450000,
                'overall_score': 'green'
            }])
            
            # Save initial data
            save_csv(initial_data, test_csv_path)
            assert test_csv_path.exists()
            
            # Load and verify
            loaded_data = load_csv(test_csv_path)
            assert len(loaded_data) == 1
            assert loaded_data.iloc[0]['site_name'] == 'Site 1'
            
            # Append new data
            new_data = pd.DataFrame([{
                'site_name': 'Site 2',
                'asking_price': 750000,
                'residual_land_value': 600000,
                'overall_score': 'yellow'
            }])
            
            # Simulate append operation
            combined_data = pd.concat([loaded_data, new_data], ignore_index=True)
            save_csv(combined_data, test_csv_path)
            
            # Verify append worked
            final_data = load_csv(test_csv_path)
            assert len(final_data) == 2
            assert final_data.iloc[1]['site_name'] == 'Site 2'
    
    def test_viability_flags_calculation(self):
        """Test viability flag calculations used in Add Deal page."""
        
        # Test land % GDV flags
        test_cases = [
            {'land_pct_gdv': 10.0, 'expected': 'low'},
            {'land_pct_gdv': 22.0, 'expected': 'good'},
            {'land_pct_gdv': 35.0, 'expected': 'high'},
        ]
        
        for case in test_cases:
            land_pct = case['land_pct_gdv']
            
            if 15 <= land_pct <= 30:
                flag = 'good'
            elif land_pct < 15:
                flag = 'low'
            else:
                flag = 'high'
            
            assert flag == case['expected'], f"Land % GDV flag calculation failed for {land_pct}%"
    
    def test_market_benchmarking(self):
        """Test market benchmarking functionality."""
        
        # Test market summary generation
        available_cities = get_available_cities()
        
        for city in available_cities[:2]:  # Test 2 cities
            try:
                market_summary = get_market_summary(city)
                
                # Verify structure
                assert isinstance(market_summary, dict)
                assert 'city' in market_summary
                
            except Exception as e:
                pytest.fail(f"Market summary failed for {city}: {e}")
    
    def test_formatting_utilities(self):
        """Test formatting utilities used across dashboard."""
        
        # Test currency formatting
        test_values = [1000, 1000000, 1500.50]
        
        for value in test_values:
            formatted = format_currency(value)
            assert '$' in formatted
            assert isinstance(formatted, str)
        
        # Test color indicators
        scores = ['green', 'yellow', 'red']
        
        for score in scores:
            indicator = get_color_indicator(score)
            assert isinstance(indicator, str)
            assert len(indicator) > 0


class TestPipelineFilteringFunctionality:
    """Test pipeline filtering and display functionality."""
    
    def test_date_range_filtering(self):
        """Test date range filtering functionality."""
        
        # Create test data with dates
        test_data = pd.DataFrame([
            {'site_name': 'Site A', 'date_analyzed': '2024-01-01', 'overall_score': 'green'},
            {'site_name': 'Site B', 'date_analyzed': '2024-01-15', 'overall_score': 'yellow'},
            {'site_name': 'Site C', 'date_analyzed': '2024-02-01', 'overall_score': 'red'},
        ])
        
        # Convert to datetime
        test_data['date_analyzed'] = pd.to_datetime(test_data['date_analyzed'])
        
        # Test filtering by date range
        start_date = pd.to_datetime('2024-01-10').date()
        end_date = pd.to_datetime('2024-01-20').date()
        
        filtered_data = test_data[
            (test_data['date_analyzed'].dt.date >= start_date) &
            (test_data['date_analyzed'].dt.date <= end_date)
        ]
        
        assert len(filtered_data) == 1
        assert filtered_data.iloc[0]['site_name'] == 'Site B'
    
    def test_city_filtering(self):
        """Test city-based filtering functionality."""
        
        test_data = pd.DataFrame([
            {'site_name': 'Site A', 'city_key': 'toronto', 'overall_score': 'green'},
            {'site_name': 'Site B', 'city_key': 'vancouver', 'overall_score': 'yellow'},
            {'site_name': 'Site C', 'city_key': 'toronto', 'overall_score': 'red'},
        ])
        
        # Filter by city
        toronto_deals = test_data[test_data['city_key'] == 'toronto']
        
        assert len(toronto_deals) == 2
        assert all(deal['city_key'] == 'toronto' for _, deal in toronto_deals.iterrows())
    
    def test_score_filtering(self):
        """Test viability score filtering functionality."""
        
        test_data = pd.DataFrame([
            {'site_name': 'Site A', 'overall_score': 'green'},
            {'site_name': 'Site B', 'overall_score': 'green'},
            {'site_name': 'Site C', 'overall_score': 'yellow'},
            {'site_name': 'Site D', 'overall_score': 'red'},
        ])
        
        # Filter by score
        green_deals = test_data[test_data['overall_score'] == 'green']
        
        assert len(green_deals) == 2
        assert all(deal['overall_score'] == 'green' for _, deal in green_deals.iterrows())


class TestSmokeTests:
    """Smoke tests for navigation and benchmarks as requested."""
    
    def test_streamlit_app_navigation_builds_pages(self):
        """Test that importing dashboard/streamlit_app.py builds a non-empty pages list."""
        import sys
        dashboard_path = Path(__file__).parent.parent / "dashboard"
        sys.path.insert(0, str(dashboard_path))
        
        try:
            from streamlit_app import pages
            assert len(pages) > 0, "Pages list should not be empty"
            # Should have at least the core pages
            assert len(pages) >= 4, "Should have at least 4 pages (Add Deal, Pipeline, Benchmarks, Configs)"
        finally:
            sys.path.pop(0)
    
    def test_navigation_handles_missing_home_page(self):
        """Test that navigation does not raise when 0_Home.py is missing."""
        import tempfile
        import shutil
        import sys
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy dashboard to temp directory
            temp_dashboard = Path(temp_dir) / "dashboard"
            shutil.copytree(Path(__file__).parent.parent / "dashboard", temp_dashboard)
            
            # Remove Home page
            (temp_dashboard / "pages" / "0_Home.py").unlink()
            
            # Test import doesn't crash
            sys.path.insert(0, str(temp_dashboard))
            
            try:
                from streamlit_app import pages
                # Should have 4 pages instead of 5 (missing Home)
                assert len(pages) == 4, "Should have 4 pages when Home is missing"
                
                # Verify no Home page is loaded
                home_titles = [p.title for p in pages if "Dashboard" in p.title or "Home" in p.title]
                assert len(home_titles) == 0, "Should not have Dashboard/Home page when file is missing"
                
            finally:
                sys.path.pop(0)
    
    def test_benchmarks_available_cities_when_data_present(self):
        """Test that Benchmarks helper returns non-empty available_cities when reference CSV is present."""
        import sys
        sys.path.append(str(Path(__file__).parent.parent))
        
        try:
            from utils.market_loader import load_market_data
            
            # Load market data
            market_df = load_market_data()
            
            # Should have data
            assert market_df is not None, "Market data should not be None"
            assert len(market_df) > 0, "Market data should have rows"
            
            # Should have city_key column
            assert 'city_key' in market_df.columns, "Should have city_key column"
            
            # Get available cities (similar to benchmarks page)
            available_cities = sorted(market_df['city_key'].unique().tolist())
            
            # Should have cities
            assert len(available_cities) > 0, "Should have available cities"
            assert isinstance(available_cities, list), "Available cities should be a list"
            
        except Exception as e:
            pytest.fail(f"Benchmarks data loading failed: {e}")
    
    def test_use_container_width_not_in_dataframe_calls(self):
        """Test that use_container_width is not present in dataframe calls (string scan)."""
        dashboard_path = Path(__file__).parent.parent / "dashboard"
        
        # Search for use_container_width in dataframe calls
        problematic_files = []
        
        for py_file in dashboard_path.rglob("*.py"):
            if py_file.name.startswith("streamlit_app_old"):
                continue  # Skip old files
                
            content = py_file.read_text()
            
            # Check for dataframe calls with use_container_width
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'st.dataframe' in line and 'use_container_width' in line:
                    problematic_files.append(f"{py_file.relative_to(dashboard_path)}:{i}")
                elif '.dataframe(' in line and 'use_container_width' in line:
                    problematic_files.append(f"{py_file.relative_to(dashboard_path)}:{i}")
        
        assert len(problematic_files) == 0, f"Found dataframe calls with use_container_width: {problematic_files}"
    
    def test_streamlit_app_imports_successfully(self):
        """Test that streamlit_app.py can be imported without errors."""
        import sys
        dashboard_path = Path(__file__).parent.parent / "dashboard"
        sys.path.insert(0, str(dashboard_path))
        
        try:
            # This should not raise any ImportError or IndentationError
            import streamlit_app
            assert hasattr(streamlit_app, 'pages'), "Should have pages attribute"
            assert hasattr(streamlit_app, 'nav'), "Should have nav attribute"
        finally:
            sys.path.pop(0)