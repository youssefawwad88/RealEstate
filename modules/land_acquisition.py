"""
Land acquisition analysis module.
Contains functions for data intake and initial processing.
"""

from typing import Dict, Any, Optional
import pandas as pd
from pathlib import Path
from utils.filelock import locked_file_write


def collect_land_inputs() -> Dict[str, Any]:
    """
    Placeholder function to collect land acquisition inputs.
    In practice, this would be connected to a Colab form or web interface.

    Returns:
        Dictionary containing land acquisition parameters
    """
    # Default example values for testing
    return {
        "site_name": "Example Site",
        "land_area_sqm": 1000.0,
        "asking_price": 500000.0,
        "zoning": "Residential",
        "far": 1.2,
        "coverage": 0.4,
        "max_floors": 3,
        "efficiency_ratio": 0.85,
        "expected_sale_price_psm": 3500.0,
        "construction_cost_psm": 1800.0,
        "soft_cost_pct": 0.15,
        "profit_target_pct": 0.20,
        "taxes_fees": 25000.0,
    }


def validate_inputs(inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean land acquisition inputs.

    Args:
        inputs: Raw input dictionary

    Returns:
        Validated and cleaned inputs

    Raises:
        ValueError: If critical inputs are missing or invalid
    """
    required_fields = [
        "land_area_sqm",
        "asking_price",
        "far",
        "coverage",
        "efficiency_ratio",
        "expected_sale_price_psm",
        "construction_cost_psm",
        "profit_target_pct",
    ]

    for field in required_fields:
        if field not in inputs:
            raise ValueError(f"Missing required field: {field}")
        if not isinstance(inputs[field], (int, float)):
            raise ValueError(f"Field {field} must be numeric")
        if inputs[field] <= 0:
            raise ValueError(f"Field {field} must be positive")

    # Additional validations
    if inputs["efficiency_ratio"] > 1.0:
        raise ValueError("Efficiency ratio cannot exceed 100%")
    if inputs["profit_target_pct"] > 1.0:
        raise ValueError("Profit target cannot exceed 100%")

    return inputs


def save_inputs_to_csv(inputs: Dict[str, Any], file_path: Optional[str] = None) -> str:
    """
    Save inputs to CSV file for tracking with file locking and backup.

    Args:
        inputs: Validated inputs dictionary
        file_path: Optional custom file path

    Returns:
        Path to saved file
    """
    if file_path is None:
        file_path = Path(__file__).parent.parent / "data" / "processed" / "acquisitions.csv"
    
    file_path = Path(file_path)

    # Convert to DataFrame
    new_df = pd.DataFrame([inputs])

    # Use locked file write with backup
    with locked_file_write(file_path) as locked_path:
        # Load existing data if file exists
        if locked_path.exists():
            existing_df = pd.read_csv(locked_path)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            combined_df = new_df

        # Write the combined data
        combined_df.to_csv(locked_path, index=False)
    
    return str(file_path)


def load_historical_data(file_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load historical land acquisition data.

    Args:
        file_path: Optional custom file path

    Returns:
        DataFrame with historical data
    """
    if file_path is None:
        file_path = Path(__file__).parent.parent / "data" / "processed" / "acquisitions.csv"

    try:
        return pd.read_csv(file_path)
    except FileNotFoundError:
        # Return empty DataFrame with expected columns
        columns = [
            "site_name",
            "land_area_sqm",
            "asking_price",
            "zoning",
            "far",
            "coverage",
            "max_floors",
            "efficiency_ratio",
            "expected_sale_price_psm",
            "construction_cost_psm",
            "soft_cost_pct",
            "profit_target_pct",
            "taxes_fees",
        ]
        return pd.DataFrame(columns=columns)


def get_acquisition_summary(inputs: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate a summary of acquisition inputs for display.

    Args:
        inputs: Land acquisition inputs

    Returns:
        Formatted summary dictionary
    """
    return {
        "Site": inputs.get("site_name", "Unnamed"),
        "Land Area": f"{inputs['land_area_sqm']:,.0f} sqm",
        "Asking Price": f"${inputs['asking_price']:,.0f}",
        "Price per sqm": f"${inputs['asking_price']/inputs['land_area_sqm']:,.0f}",
        "Zoning": inputs.get("zoning", "Unknown"),
        "FAR": f"{inputs['far']:.1f}",
        "Coverage": f"{inputs['coverage']:.0%}",
    }
