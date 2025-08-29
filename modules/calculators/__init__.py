"""
TerraFlow calculators package.
Pure calculation functions with no external dependencies.
"""

from .residual import (
    DevelopmentCapacity,
    FinancialResults, 
    AcquisitionMetrics,
    calculate_development_capacity,
    calculate_gdv,
    calculate_development_costs,
    calculate_required_profit,
    calculate_residual_land_value,
    calculate_acquisition_metrics,
    calculate_comprehensive_residual,
    calculate_sensitivity_analysis,
)

from .unitize import (
    AreaUnit,
    CurrencyUnit,
    UnitMetrics,
    convert_area,
    convert_currency,
    calculate_unit_metrics,
    standardize_deal_metrics,
    compare_deals_per_unit,
)

__all__ = [
    # Residual calculation classes
    "DevelopmentCapacity",
    "FinancialResults",
    "AcquisitionMetrics",
    
    # Residual calculation functions
    "calculate_development_capacity",
    "calculate_gdv",
    "calculate_development_costs", 
    "calculate_required_profit",
    "calculate_residual_land_value",
    "calculate_acquisition_metrics",
    "calculate_comprehensive_residual",
    "calculate_sensitivity_analysis",
    
    # Unit conversion classes
    "AreaUnit",
    "CurrencyUnit", 
    "UnitMetrics",
    
    # Unit conversion functions
    "convert_area",
    "convert_currency",
    "calculate_unit_metrics",
    "standardize_deal_metrics",
    "compare_deals_per_unit",
]