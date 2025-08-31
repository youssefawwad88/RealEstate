"""
Test navigation path functionality for Streamlit Cloud compatibility.
"""

import pytest
import subprocess
import sys
from pathlib import Path


class TestNavigationPaths:
    """Test navigation path safety and smoke tests."""
    
    def test_pages_directory_exists(self):
        """Assert Path('dashboard/pages') exists."""
        pages_dir = Path("dashboard/pages")
        assert pages_dir.exists(), f"Pages directory {pages_dir} should exist"
        
    def test_expected_page_files_exist(self):
        """Assert each expected filename exists."""
        expected_files = [
            "0_Home.py",
            "1_Add_Deal.py", 
            "2_Pipeline.py",
            "3_Benchmarks.py",
            "4_Configs_Viewer.py"
        ]
        
        pages_dir = Path("dashboard/pages")
        for filename in expected_files:
            file_path = pages_dir / filename
            assert file_path.exists(), f"Expected page file {file_path} should exist"
            
    def test_streamlit_app_bootable(self):
        """Import dashboard.streamlit_app in a subprocess and confirm it exits 0 (bootable)."""
        # Run the import in a subprocess to avoid Streamlit context issues
        result = subprocess.run(
            [sys.executable, "-c", "import dashboard.streamlit_app"],
            capture_output=True,
            text=True,
            cwd=Path.cwd()
        )
        
        # Should exit with code 0 (success)
        if result.returncode != 0:
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
        
        assert result.returncode == 0, f"Streamlit app should be importable without errors. Exit code: {result.returncode}, stderr: {result.stderr}"
        
    def test_directory_listings_utility(self):
        """Print directory listings to logs for debugging."""
        pages_dir = Path("dashboard/pages")
        if pages_dir.exists():
            files = sorted([p.name for p in pages_dir.glob('*.py')])
            print(f"Available pages/*.py files: {files}")
        else:
            print(f"Pages directory {pages_dir} does not exist")
            
        dashboard_dir = Path("dashboard")
        if dashboard_dir.exists():
            files = sorted([p.name for p in dashboard_dir.iterdir() if p.is_file()])
            print(f"Dashboard directory files: {files}")