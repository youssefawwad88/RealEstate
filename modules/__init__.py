"""
TerraFlow core modules.
Modular architecture with calculators, policies, and adapters.
"""

# Import from existing modules (keeping compatibility)
from .deal_model import (
    LandInputs,
    CalculatedOutputs,
    ViabilityScores,
    SensitivityAnalysis,
    LandDeal,
    create_deal_from_dict,
    batch_process_deals,
)

from .land_acquisition import (
    collect_land_inputs,
    validate_inputs,
    save_inputs_to_csv,
    load_historical_data,
    get_acquisition_summary,
)

# Import from new modular structure
from .calculators import (
    DevelopmentCapacity,
    FinancialResults,
    AcquisitionMetrics,
    calculate_development_capacity,
    calculate_gdv,
    calculate_comprehensive_residual,
    calculate_sensitivity_analysis,
    AreaUnit,
    CurrencyUnit,
    UnitMetrics,
    calculate_unit_metrics,
    standardize_deal_metrics,
)

from .policies import (
    CountryRules,
    ZoningRules,
    FinanceRules,
    RuleSet,
    ConfigRegistry,
    get_registry,
    get_ruleset,
    get_available_countries,
    ValidationSeverity,
    ValidationIssue,
    ValidationReport,
    validate_deal_comprehensive,
)

from .adapters import (
    MarketBenchmarks,
    MarketDataAdapter,
    get_market_adapter,
    validate_inputs_against_market,
    get_market_summary,
    ExchangeRate,
    CurrencyService,
    convert_currency,
    Coordinates,
    Address,
    ParcelInfo,
    analyze_location,
)

__all__ = [
    # Existing deal model compatibility
    "LandInputs",
    "CalculatedOutputs", 
    "ViabilityScores",
    "SensitivityAnalysis",
    "LandDeal",
    "create_deal_from_dict",
    "batch_process_deals",
    
    # Land acquisition
    "collect_land_inputs",
    "validate_inputs",
    "save_inputs_to_csv",
    "load_historical_data", 
    "get_acquisition_summary",
    
    # Calculator functions and classes
    "DevelopmentCapacity",
    "FinancialResults",
    "AcquisitionMetrics", 
    "calculate_development_capacity",
    "calculate_gdv",
    "calculate_comprehensive_residual",
    "calculate_sensitivity_analysis",
    "AreaUnit",
    "CurrencyUnit",
    "UnitMetrics",
    "calculate_unit_metrics",
    "standardize_deal_metrics",
    
    # Policy and configuration system
    "CountryRules",
    "ZoningRules",
    "FinanceRules", 
    "RuleSet",
    "ConfigRegistry",
    "get_registry",
    "get_ruleset",
    "get_available_countries",
    "ValidationSeverity",
    "ValidationIssue", 
    "ValidationReport",
    "validate_deal_comprehensive",
    
    # Adapter integrations
    "MarketBenchmarks",
    "MarketDataAdapter",
    "get_market_adapter",
    "validate_inputs_against_market",
    "get_market_summary",
    "ExchangeRate",
    "CurrencyService",
    "convert_currency",
    "Coordinates",
    "Address",
    "ParcelInfo", 
    "analyze_location",
]
