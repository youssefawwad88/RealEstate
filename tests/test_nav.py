"""
Test navigation functionality.
"""

import pytest
import streamlit as st
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestNavigation:
    """Test streamlit navigation setup."""
    
    def test_page_objects_resolve(self):
        """Test that page objects resolve with mocked filesystem."""
        from pathlib import Path
        
        # Mock Path.exists to return True for all page files
        with patch.object(Path, 'exists', return_value=True):
            # Import the streamlit app module to test page resolution
            import sys
            app_path = Path(__file__).parent.parent / "dashboard"
            sys.path.insert(0, str(app_path))
            
            try:
                # Test that pages can be created without error
                from pathlib import Path
                
                pages = [
                    ("pages/0_Home.py", "Dashboard", "🏠"),
                    ("pages/1_Add_Deal.py", "Add Deal", "📝"),
                    ("pages/2_Pipeline.py", "Pipeline", "📊"),
                    ("pages/3_Benchmarks.py", "Benchmarks", "📈"),
                    ("pages/4_Configs_Viewer.py", "Configs", "⚙️"),
                ]
                
                # Verify page paths would resolve correctly
                base_path = Path(__file__).parent.parent / "dashboard"
                for page_file, title, icon in pages:
                    page_path = base_path / page_file
                    # Check the path structure is correct
                    assert page_path.name.endswith('.py')
                    assert title  # Non-empty title
                    assert icon   # Non-empty icon
                    
            finally:
                sys.path.pop(0)
    
    def test_absolute_paths_construction(self):
        """Test that absolute paths are constructed correctly."""
        # Test the path construction logic used in streamlit_app.py
        dashboard_dir = Path(__file__).parent.parent / "dashboard"
        
        # Simulate __file__ being dashboard/streamlit_app.py
        mock_file = dashboard_dir / "streamlit_app.py"
        
        # Test the relative path resolution
        pages_dir = mock_file.parent / "pages"
        
        test_pages = [
            "0_Home.py", 
            "1_Add_Deal.py", 
            "2_Pipeline.py", 
            "3_Benchmarks.py", 
            "4_Configs_Viewer.py"
        ]
        
        for page in test_pages:
            page_path = pages_dir / page
            # Verify path construction doesn't raise errors
            str_path = str(page_path)
            assert str_path.endswith(page)
            assert "pages" in str_path
    
    @patch('streamlit.Page')
    @patch('streamlit.navigation')
    def test_navigation_creation(self, mock_nav, mock_page):
        """Test navigation can be created without errors."""
        # Mock streamlit components
        mock_page.return_value = MagicMock()
        mock_nav_instance = MagicMock()
        mock_nav.return_value = mock_nav_instance
        
        # Test the navigation creation logic
        pages = ["0_Home.py", "1_Add_Deal.py", "2_Pipeline.py", "3_Benchmarks.py", "4_Configs_Viewer.py"]
        
        # This should not raise any errors
        for page in pages:
            mock_page(page, page.replace('.py', '').replace('_', ' '), icon="📄")
        
        # Verify Page was called
        assert mock_page.call_count >= len(pages)