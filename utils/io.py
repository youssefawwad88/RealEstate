"""
I/O utility functions for TerraFlow system.
Handles data loading, saving, and file operations.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
import json


def load_csv(file_path: str | Path) -> pd.DataFrame:
    """
    Load CSV file with error handling.

    Args:
        file_path: Path to the CSV file

    Returns:
        DataFrame containing the CSV data

    Raises:
        FileNotFoundError: If the file doesn't exist
        pd.errors.EmptyDataError: If the file is empty
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return pd.read_csv(path)


def save_csv(df: pd.DataFrame, file_path: str | Path, index: bool = False) -> None:
    """
    Save DataFrame to CSV with directory creation.

    Args:
        df: DataFrame to save
        file_path: Path where to save the CSV
        index: Whether to include the index in the saved file
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)


def load_json(file_path: str | Path) -> Dict[str, Any]:
    """
    Load JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Dictionary containing the JSON data
    """
    path = Path(file_path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Dict[str, Any], file_path: str | Path, indent: int = 2) -> None:
    """
    Save dictionary to JSON file.

    Args:
        data: Dictionary to save
        file_path: Path where to save the JSON
        indent: Number of spaces for indentation
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)


def get_project_root() -> Path:
    """
    Get the project root directory.

    Returns:
        Path to the project root
    """
    return Path(__file__).parent.parent


def get_data_dir() -> Path:
    """
    Get the data directory path.

    Returns:
        Path to the data directory
    """
    return get_project_root() / "data"
