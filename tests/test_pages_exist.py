"""
Test that required pages exist as specified in the problem statement.
"""
from pathlib import Path


def test_home_page_exists():
    """Test that 0_Home.py exists as required."""
    assert (Path("dashboard") / "pages" / "0_Home.py").exists()


def test_pages_directory_exists():
    """Test that pages directory exists."""
    assert (Path("dashboard") / "pages").exists()