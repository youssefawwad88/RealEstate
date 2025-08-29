"""
Unit metrics and standardization functions.
Converts between different measurement units and calculates per-unit metrics.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class AreaUnit(Enum):
    """Supported area units."""
    SQM = "sqm"  # Square meters
    SQFT = "sqft"  # Square feet
    HECTARE = "hectare"
    ACRE = "acre"


class CurrencyUnit(Enum):
    """Supported currency units."""
    USD = "USD"
    JOD = "JOD"  # Jordanian Dinar
    AED = "AED"  # UAE Dirham
    EUR = "EUR"
    GBP = "GBP"


@dataclass
class UnitMetrics:
    """Standardized unit metrics for deal comparison."""
    
    # Land metrics
    land_cost_per_sqm: float
    land_cost_per_buildable_sqm: float
    land_cost_pct_gdv: float
    
    # Development metrics
    construction_cost_per_sqm: float
    gdv_per_sqm: float
    gdv_per_buildable_sqm: float
    
    # Profitability metrics
    profit_per_sqm: float
    profit_margin_pct: float
    residual_per_sqm: float
    
    # Efficiency metrics
    buildable_ratio: float  # Buildable area / Land area
    efficiency_ratio: float  # Net / Gross area
    
    # Units used
    area_unit: str
    currency_unit: str


# Conversion constants
AREA_CONVERSIONS = {
    (AreaUnit.SQM, AreaUnit.SQFT): 10.764,
    (AreaUnit.SQFT, AreaUnit.SQM): 0.0929,
    (AreaUnit.SQM, AreaUnit.HECTARE): 0.0001,
    (AreaUnit.HECTARE, AreaUnit.SQM): 10000,
    (AreaUnit.SQFT, AreaUnit.ACRE): 0.0000229,
    (AreaUnit.ACRE, AreaUnit.SQFT): 43560,
    (AreaUnit.HECTARE, AreaUnit.ACRE): 2.471,
    (AreaUnit.ACRE, AreaUnit.HECTARE): 0.405,
}


def convert_area(value: float, from_unit: AreaUnit, to_unit: AreaUnit) -> float:
    """
    Convert area between different units.
    
    Args:
        value: Area value to convert
        from_unit: Source unit
        to_unit: Target unit
        
    Returns:
        Converted area value
        
    Raises:
        ValueError: If conversion is not supported
    """
    if from_unit == to_unit:
        return value
        
    # Direct conversion
    conversion_key = (from_unit, to_unit)
    if conversion_key in AREA_CONVERSIONS:
        return value * AREA_CONVERSIONS[conversion_key]
        
    # Reverse conversion
    reverse_key = (to_unit, from_unit)
    if reverse_key in AREA_CONVERSIONS:
        return value / AREA_CONVERSIONS[reverse_key]
        
    # Multi-step conversion through SQM
    if from_unit != AreaUnit.SQM:
        value_sqm = convert_area(value, from_unit, AreaUnit.SQM)
        return convert_area(value_sqm, AreaUnit.SQM, to_unit)
        
    raise ValueError(f"Unsupported area conversion from {from_unit} to {to_unit}")


def convert_currency(
    value: float,
    from_currency: CurrencyUnit,
    to_currency: CurrencyUnit,
    exchange_rates: Optional[Dict[str, float]] = None
) -> float:
    """
    Convert currency between different units.
    
    Args:
        value: Currency value to convert
        from_currency: Source currency
        to_currency: Target currency
        exchange_rates: Dictionary of exchange rates vs USD
        
    Returns:
        Converted currency value
        
    Raises:
        ValueError: If exchange rates not provided for conversion
    """
    if from_currency == to_currency:
        return value
        
    if not exchange_rates:
        raise ValueError("Exchange rates required for currency conversion")
        
    # Convert to USD first, then to target currency
    if from_currency != CurrencyUnit.USD:
        from_rate = exchange_rates.get(from_currency.value, 1.0)
        value_usd = value / from_rate
    else:
        value_usd = value
        
    if to_currency != CurrencyUnit.USD:
        to_rate = exchange_rates.get(to_currency.value, 1.0)
        return value_usd * to_rate
    else:
        return value_usd


def calculate_unit_metrics(
    land_area_sqm: float,
    gross_buildable_sqm: float,
    net_sellable_sqm: float,
    asking_price: float,
    construction_cost_total: float,
    gdv: float,
    profit: float,
    residual_land_value: float,
    area_unit: AreaUnit = AreaUnit.SQM,
    currency_unit: CurrencyUnit = CurrencyUnit.USD
) -> UnitMetrics:
    """
    Calculate comprehensive unit metrics for deal comparison.
    
    Args:
        land_area_sqm: Total land area in square meters
        gross_buildable_sqm: Gross buildable area in square meters  
        net_sellable_sqm: Net sellable area in square meters
        asking_price: Land asking price
        construction_cost_total: Total construction cost
        gdv: Gross Development Value
        profit: Developer profit
        residual_land_value: Calculated residual land value
        area_unit: Unit for area measurements
        currency_unit: Unit for currency values
        
    Returns:
        UnitMetrics with all calculated per-unit values
    """
    # Calculate base metrics in square meters
    land_cost_per_sqm = asking_price / land_area_sqm if land_area_sqm > 0 else 0
    land_cost_per_buildable_sqm = asking_price / gross_buildable_sqm if gross_buildable_sqm > 0 else 0
    land_cost_pct_gdv = (asking_price / gdv * 100) if gdv > 0 else 0
    
    construction_cost_per_sqm = construction_cost_total / gross_buildable_sqm if gross_buildable_sqm > 0 else 0
    gdv_per_sqm = gdv / net_sellable_sqm if net_sellable_sqm > 0 else 0
    gdv_per_buildable_sqm = gdv / gross_buildable_sqm if gross_buildable_sqm > 0 else 0
    
    profit_per_sqm = profit / net_sellable_sqm if net_sellable_sqm > 0 else 0
    profit_margin_pct = (profit / gdv * 100) if gdv > 0 else 0
    residual_per_sqm = residual_land_value / land_area_sqm if land_area_sqm > 0 else 0
    
    buildable_ratio = gross_buildable_sqm / land_area_sqm if land_area_sqm > 0 else 0
    efficiency_ratio = net_sellable_sqm / gross_buildable_sqm if gross_buildable_sqm > 0 else 0
    
    # Convert to requested units if needed
    if area_unit != AreaUnit.SQM:
        # Convert area-based metrics
        area_conversion_factor = convert_area(1.0, AreaUnit.SQM, area_unit)
        land_cost_per_sqm /= area_conversion_factor
        land_cost_per_buildable_sqm /= area_conversion_factor
        construction_cost_per_sqm /= area_conversion_factor
        gdv_per_sqm /= area_conversion_factor
        gdv_per_buildable_sqm /= area_conversion_factor
        profit_per_sqm /= area_conversion_factor
        residual_per_sqm /= area_conversion_factor
    
    return UnitMetrics(
        land_cost_per_sqm=land_cost_per_sqm,
        land_cost_per_buildable_sqm=land_cost_per_buildable_sqm,
        land_cost_pct_gdv=land_cost_pct_gdv,
        construction_cost_per_sqm=construction_cost_per_sqm,
        gdv_per_sqm=gdv_per_sqm,
        gdv_per_buildable_sqm=gdv_per_buildable_sqm,
        profit_per_sqm=profit_per_sqm,
        profit_margin_pct=profit_margin_pct,
        residual_per_sqm=residual_per_sqm,
        buildable_ratio=buildable_ratio,
        efficiency_ratio=efficiency_ratio,
        area_unit=area_unit.value,
        currency_unit=currency_unit.value
    )


def standardize_deal_metrics(
    deal_dict: Dict[str, Any],
    target_area_unit: AreaUnit = AreaUnit.SQM,
    target_currency: CurrencyUnit = CurrencyUnit.USD,
    exchange_rates: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Standardize deal metrics to common units for comparison.
    
    Args:
        deal_dict: Dictionary with deal parameters
        target_area_unit: Target unit for area measurements
        target_currency: Target currency unit
        exchange_rates: Exchange rates for currency conversion
        
    Returns:
        Dictionary with standardized metrics
    """
    standardized = deal_dict.copy()
    
    # Get current units
    current_area_unit = AreaUnit(deal_dict.get("area_unit", "sqm"))
    current_currency = CurrencyUnit(deal_dict.get("currency_unit", "USD"))
    
    # Convert area-based values
    if current_area_unit != target_area_unit:
        area_fields = [
            "land_area_sqm", "gross_buildable_sqm", "net_sellable_sqm"
        ]
        
        for field in area_fields:
            if field in standardized:
                standardized[field] = convert_area(
                    standardized[field], current_area_unit, target_area_unit
                )
        
        # Convert per-area rates
        rate_conversion = convert_area(1.0, target_area_unit, current_area_unit)
        rate_fields = [
            "expected_sale_price_psm", "construction_cost_psm"
        ]
        
        for field in rate_fields:
            if field in standardized:
                standardized[field] *= rate_conversion
    
    # Convert currency values
    if current_currency != target_currency and exchange_rates:
        currency_fields = [
            "asking_price", "taxes_fees", "gdv", "hard_costs", 
            "soft_costs", "total_dev_cost", "required_profit", 
            "residual_land_value", "financing_cost"
        ]
        
        for field in currency_fields:
            if field in standardized:
                standardized[field] = convert_currency(
                    standardized[field], current_currency, target_currency, exchange_rates
                )
    
    # Update unit indicators
    standardized["area_unit"] = target_area_unit.value
    standardized["currency_unit"] = target_currency.value
    
    return standardized


def compare_deals_per_unit(deals: list[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare multiple deals on a per-unit basis.
    
    Args:
        deals: List of deal dictionaries with calculated outputs
        
    Returns:
        Dictionary with comparative unit metrics
    """
    if not deals:
        return {}
    
    # Calculate unit metrics for each deal
    deal_metrics = []
    for deal in deals:
        if "outputs" in deal:
            outputs = deal["outputs"]
            inputs = deal.get("inputs", {})
            
            metrics = calculate_unit_metrics(
                land_area_sqm=inputs.get("land_area_sqm", 0),
                gross_buildable_sqm=outputs.get("gross_buildable_sqm", 0),
                net_sellable_sqm=outputs.get("net_sellable_sqm", 0),
                asking_price=inputs.get("asking_price", 0),
                construction_cost_total=outputs.get("hard_costs", 0) + outputs.get("soft_costs", 0),
                gdv=outputs.get("gdv", 0),
                profit=outputs.get("required_profit", 0),
                residual_land_value=outputs.get("residual_land_value", 0)
            )
            
            deal_metrics.append({
                "site_name": inputs.get("site_name", "Unknown"),
                "metrics": metrics
            })
    
    # Calculate summary statistics
    if not deal_metrics:
        return {}
    
    land_costs_psm = [dm["metrics"].land_cost_per_sqm for dm in deal_metrics]
    gdv_psm = [dm["metrics"].gdv_per_sqm for dm in deal_metrics]
    profit_margins = [dm["metrics"].profit_margin_pct for dm in deal_metrics]
    
    return {
        "deal_count": len(deal_metrics),
        "land_cost_psm_avg": sum(land_costs_psm) / len(land_costs_psm),
        "land_cost_psm_range": [min(land_costs_psm), max(land_costs_psm)],
        "gdv_psm_avg": sum(gdv_psm) / len(gdv_psm),
        "gdv_psm_range": [min(gdv_psm), max(gdv_psm)],
        "profit_margin_avg": sum(profit_margins) / len(profit_margins),
        "profit_margin_range": [min(profit_margins), max(profit_margins)],
        "deals": deal_metrics
    }