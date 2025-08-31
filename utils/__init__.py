"""
TerraFlow utilities package.
Helper functions, logging, error handling, and unit conversions.
"""

from .io import (
    load_csv,
    save_csv, 
    load_json,
    save_json,
    get_project_root,
    get_data_dir,
)

from .market_loader import (
    load_market_benchmarks,
    filter_allowed_markets,
)

from .filelock import (
    FileLock,
    FileLockError,
    locked_file_write,
    cleanup_old_backups,
)

from .scoring import (
    score_deal_viability,
    get_color_indicator,
    calculate_sensitivity,
    format_currency,
)

from .logging import (
    TerraFlowFormatter,
    setup_logging,
    get_logger,
    LoggingContext,
    log_deal_calculation,
    log_validation_issues,
    log_market_data_usage,
    log_performance_metric,
    init_terraflow_logging,
    get_terraflow_logger,
)

from .errors import (
    TerraFlowError,
    ConfigurationError,
    ValidationError,
    ZoningComplianceError,
    CalculationError,
    MarketDataError,
    CurrencyConversionError,
    GeospatialError,
    DataProcessingError,
    FileOperationError,
    APIError,
    handle_calculation_errors,
    handle_validation_errors,
    create_error_summary,
    format_validation_errors,
)

from .units import (
    AreaUnit,
    LengthUnit,
    VolumeUnit,
    Measurement,
    convert_area,
    convert_length,
    convert_volume,
    area_sqm_to_sqft,
    area_sqft_to_sqm,
    length_m_to_ft,
    length_ft_to_m,
    format_area,
    format_length,
    parse_area_string,
    standardize_area_units,
    calculate_price_per_unit,
    get_unit_abbreviations,
    common_real_estate_conversions,
)

__all__ = [
    # IO utilities
    "load_csv",
    "save_csv",
    "load_json", 
    "save_json",
    "get_project_root",
    "get_data_dir",
    
    # Market data utilities
    "load_market_benchmarks",
    "filter_allowed_markets",
    
    # File locking utilities
    "FileLock",
    "FileLockError", 
    "locked_file_write",
    "cleanup_old_backups",
    
    # Scoring utilities
    "score_deal_viability",
    "get_color_indicator",
    "calculate_sensitivity",
    "format_currency",
    
    # Logging utilities
    "TerraFlowFormatter",
    "setup_logging",
    "get_logger",
    "LoggingContext",
    "log_deal_calculation",
    "log_validation_issues", 
    "log_market_data_usage",
    "log_performance_metric",
    "init_terraflow_logging",
    "get_terraflow_logger",
    
    # Error handling
    "TerraFlowError",
    "ConfigurationError",
    "ValidationError",
    "ZoningComplianceError",
    "CalculationError",
    "MarketDataError",
    "CurrencyConversionError",
    "GeospatialError",
    "DataProcessingError",
    "FileOperationError",
    "APIError",
    "handle_calculation_errors",
    "handle_validation_errors",
    "create_error_summary",
    "format_validation_errors",
    
    # Unit conversions
    "AreaUnit",
    "LengthUnit",
    "VolumeUnit",
    "Measurement",
    "convert_area",
    "convert_length",
    "convert_volume",
    "area_sqm_to_sqft",
    "area_sqft_to_sqm",
    "length_m_to_ft",
    "length_ft_to_m",
    "format_area",
    "format_length",
    "parse_area_string",
    "standardize_area_units",
    "calculate_price_per_unit",
    "get_unit_abbreviations",
    "common_real_estate_conversions",
]
