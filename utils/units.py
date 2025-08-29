"""
Unit conversion and measurement utilities.
Handles conversions between different units commonly used in real estate.
"""

from typing import Dict, Union, Optional
from enum import Enum
from dataclasses import dataclass


class AreaUnit(Enum):
    """Area measurement units."""
    SQM = "sqm"          # Square meters
    SQFT = "sqft"        # Square feet
    SQ_YARD = "sq_yard"  # Square yards
    HECTARE = "hectare"  # Hectares
    ACRE = "acre"        # Acres
    DUNUM = "dunum"      # Dunum (Middle East)


class LengthUnit(Enum):
    """Length measurement units."""
    METER = "m"          # Meters
    FOOT = "ft"          # Feet
    YARD = "yard"        # Yards
    KILOMETER = "km"     # Kilometers
    MILE = "mile"        # Miles


class VolumeUnit(Enum):
    """Volume measurement units."""
    CUBIC_METER = "cbm"  # Cubic meters
    CUBIC_FOOT = "cbft"  # Cubic feet
    LITER = "l"          # Liters
    GALLON = "gal"       # Gallons


# Conversion factors to base units (meters, square meters, cubic meters)
AREA_CONVERSIONS = {
    AreaUnit.SQM: 1.0,
    AreaUnit.SQFT: 0.092903,
    AreaUnit.SQ_YARD: 0.836127,
    AreaUnit.HECTARE: 10000.0,
    AreaUnit.ACRE: 4046.86,
    AreaUnit.DUNUM: 1000.0,  # 1 dunum = 1000 sqm (varies by region)
}

LENGTH_CONVERSIONS = {
    LengthUnit.METER: 1.0,
    LengthUnit.FOOT: 0.3048,
    LengthUnit.YARD: 0.9144,
    LengthUnit.KILOMETER: 1000.0,
    LengthUnit.MILE: 1609.34,
}

VOLUME_CONVERSIONS = {
    VolumeUnit.CUBIC_METER: 1.0,
    VolumeUnit.CUBIC_FOOT: 0.0283168,
    VolumeUnit.LITER: 0.001,
    VolumeUnit.GALLON: 0.00378541,  # US gallon
}


@dataclass
class Measurement:
    """Generic measurement with value and unit."""
    
    value: float
    unit: Union[AreaUnit, LengthUnit, VolumeUnit]
    
    def convert_to(self, target_unit: Union[AreaUnit, LengthUnit, VolumeUnit]) -> 'Measurement':
        """Convert measurement to target unit."""
        if type(self.unit) != type(target_unit):
            raise ValueError(f"Cannot convert {type(self.unit)} to {type(target_unit)}")
        
        if isinstance(self.unit, AreaUnit):
            converted_value = convert_area(self.value, self.unit, target_unit)
        elif isinstance(self.unit, LengthUnit):
            converted_value = convert_length(self.value, self.unit, target_unit)
        elif isinstance(self.unit, VolumeUnit):
            converted_value = convert_volume(self.value, self.unit, target_unit)
        else:
            raise ValueError(f"Unsupported unit type: {type(self.unit)}")
        
        return Measurement(converted_value, target_unit)
    
    def __str__(self) -> str:
        """String representation of measurement."""
        return f"{self.value:,.2f} {self.unit.value}"


def convert_area(value: float, from_unit: AreaUnit, to_unit: AreaUnit) -> float:
    """
    Convert area between different units.
    
    Args:
        value: Area value to convert
        from_unit: Source unit
        to_unit: Target unit
        
    Returns:
        Converted area value
    """
    if from_unit == to_unit:
        return value
    
    # Convert to square meters first, then to target unit
    sqm_value = value * AREA_CONVERSIONS[from_unit]
    converted_value = sqm_value / AREA_CONVERSIONS[to_unit]
    
    return converted_value


def convert_length(value: float, from_unit: LengthUnit, to_unit: LengthUnit) -> float:
    """
    Convert length between different units.
    
    Args:
        value: Length value to convert
        from_unit: Source unit
        to_unit: Target unit
        
    Returns:
        Converted length value
    """
    if from_unit == to_unit:
        return value
    
    # Convert to meters first, then to target unit
    meter_value = value * LENGTH_CONVERSIONS[from_unit]
    converted_value = meter_value / LENGTH_CONVERSIONS[to_unit]
    
    return converted_value


def convert_volume(value: float, from_unit: VolumeUnit, to_unit: VolumeUnit) -> float:
    """
    Convert volume between different units.
    
    Args:
        value: Volume value to convert
        from_unit: Source unit
        to_unit: Target unit
        
    Returns:
        Converted volume value
    """
    if from_unit == to_unit:
        return value
    
    # Convert to cubic meters first, then to target unit
    cbm_value = value * VOLUME_CONVERSIONS[from_unit]
    converted_value = cbm_value / VOLUME_CONVERSIONS[to_unit]
    
    return converted_value


def area_sqm_to_sqft(sqm: float) -> float:
    """Convert square meters to square feet."""
    return convert_area(sqm, AreaUnit.SQM, AreaUnit.SQFT)


def area_sqft_to_sqm(sqft: float) -> float:
    """Convert square feet to square meters."""
    return convert_area(sqft, AreaUnit.SQFT, AreaUnit.SQM)


def length_m_to_ft(meters: float) -> float:
    """Convert meters to feet."""
    return convert_length(meters, LengthUnit.METER, LengthUnit.FOOT)


def length_ft_to_m(feet: float) -> float:
    """Convert feet to meters."""
    return convert_length(feet, LengthUnit.FOOT, LengthUnit.METER)


def format_area(value: float, unit: AreaUnit, precision: int = 0) -> str:
    """
    Format area value with appropriate unit display.
    
    Args:
        value: Area value
        unit: Area unit
        precision: Number of decimal places
        
    Returns:
        Formatted string
    """
    unit_display = {
        AreaUnit.SQM: "m²",
        AreaUnit.SQFT: "ft²", 
        AreaUnit.SQ_YARD: "yd²",
        AreaUnit.HECTARE: "ha",
        AreaUnit.ACRE: "acres",
        AreaUnit.DUNUM: "dunum"
    }
    
    formatted_value = f"{value:,.{precision}f}"
    unit_symbol = unit_display.get(unit, unit.value)
    
    return f"{formatted_value} {unit_symbol}"


def format_length(value: float, unit: LengthUnit, precision: int = 1) -> str:
    """
    Format length value with appropriate unit display.
    
    Args:
        value: Length value
        unit: Length unit
        precision: Number of decimal places
        
    Returns:
        Formatted string
    """
    unit_display = {
        LengthUnit.METER: "m",
        LengthUnit.FOOT: "ft",
        LengthUnit.YARD: "yd", 
        LengthUnit.KILOMETER: "km",
        LengthUnit.MILE: "mi"
    }
    
    formatted_value = f"{value:,.{precision}f}"
    unit_symbol = unit_display.get(unit, unit.value)
    
    return f"{formatted_value} {unit_symbol}"


def parse_area_string(area_str: str) -> Optional[Measurement]:
    """
    Parse area string into Measurement object.
    
    Args:
        area_str: String like "1500 sqm" or "16,000 sqft"
        
    Returns:
        Measurement object or None if parsing fails
    """
    try:
        # Remove commas and split by space
        cleaned = area_str.replace(",", "").strip()
        parts = cleaned.split()
        
        if len(parts) != 2:
            return None
        
        value_str, unit_str = parts
        value = float(value_str)
        
        # Map common unit strings to AreaUnit
        unit_mapping = {
            "sqm": AreaUnit.SQM,
            "m2": AreaUnit.SQM,
            "m²": AreaUnit.SQM,
            "sqft": AreaUnit.SQFT,
            "ft2": AreaUnit.SQFT,
            "ft²": AreaUnit.SQFT,
            "hectare": AreaUnit.HECTARE,
            "ha": AreaUnit.HECTARE,
            "acre": AreaUnit.ACRE,
            "acres": AreaUnit.ACRE,
            "dunum": AreaUnit.DUNUM,
        }
        
        unit = unit_mapping.get(unit_str.lower())
        if not unit:
            return None
        
        return Measurement(value, unit)
        
    except (ValueError, IndexError):
        return None


def standardize_area_units(
    measurements: Dict[str, float],
    source_unit: AreaUnit,
    target_unit: AreaUnit = AreaUnit.SQM
) -> Dict[str, float]:
    """
    Standardize area measurements to common unit.
    
    Args:
        measurements: Dictionary of area measurements
        source_unit: Current unit of measurements
        target_unit: Target unit (default: square meters)
        
    Returns:
        Dictionary with converted measurements
    """
    if source_unit == target_unit:
        return measurements.copy()
    
    standardized = {}
    for key, value in measurements.items():
        standardized[key] = convert_area(value, source_unit, target_unit)
    
    return standardized


def calculate_price_per_unit(
    total_price: float,
    area: float,
    area_unit: AreaUnit = AreaUnit.SQM
) -> Dict[str, float]:
    """
    Calculate price per unit area in multiple units.
    
    Args:
        total_price: Total price
        area: Total area
        area_unit: Unit of area measurement
        
    Returns:
        Dictionary with price per unit in different units
    """
    if area <= 0:
        return {}
    
    # Convert area to different units and calculate price per unit
    area_sqm = convert_area(area, area_unit, AreaUnit.SQM)
    area_sqft = convert_area(area, area_unit, AreaUnit.SQFT)
    
    return {
        "price_per_sqm": total_price / area_sqm if area_sqm > 0 else 0,
        "price_per_sqft": total_price / area_sqft if area_sqft > 0 else 0,
    }


def get_unit_abbreviations() -> Dict[str, str]:
    """Get dictionary of unit abbreviations for display."""
    return {
        # Area units
        "sqm": "m²",
        "sqft": "ft²",
        "sq_yard": "yd²",
        "hectare": "ha",
        "acre": "acres",
        "dunum": "dunum",
        
        # Length units
        "m": "m",
        "ft": "ft",
        "yard": "yd",
        "km": "km",
        "mile": "mi",
        
        # Volume units
        "cbm": "m³",
        "cbft": "ft³",
        "l": "L",
        "gal": "gal",
    }


# Common unit conversions for real estate
def common_real_estate_conversions(area_sqm: float) -> Dict[str, str]:
    """
    Convert area to common real estate units with formatting.
    
    Args:
        area_sqm: Area in square meters
        
    Returns:
        Dictionary with formatted conversions
    """
    return {
        "sqm": format_area(area_sqm, AreaUnit.SQM, 0),
        "sqft": format_area(area_sqm_to_sqft(area_sqm), AreaUnit.SQFT, 0),
        "acres": format_area(convert_area(area_sqm, AreaUnit.SQM, AreaUnit.ACRE), AreaUnit.ACRE, 2),
        "hectares": format_area(convert_area(area_sqm, AreaUnit.SQM, AreaUnit.HECTARE), AreaUnit.HECTARE, 2),
        "dunum": format_area(convert_area(area_sqm, AreaUnit.SQM, AreaUnit.DUNUM), AreaUnit.DUNUM, 1),
    }