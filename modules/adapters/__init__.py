"""
TerraFlow adapters package.
External system integrations and data adapters.
"""

from .market_lookup import (
    MarketBenchmarks,
    MarketDataAdapter,
    get_market_adapter,
    validate_inputs_against_market,
    get_market_summary,
)

from .currency import (
    ExchangeRate,
    CurrencyProvider,
    StaticCurrencyProvider,
    LiveCurrencyProvider,
    CurrencyService,
    get_currency_service,
    convert_currency,
    get_exchange_rates_vs_usd,
)

from .geospatial import (
    Coordinates,
    Address,
    ParcelInfo,
    NearbyAmenity,
    GeospatialProvider,
    StubGeospatialProvider,
    GeospatialService,
    get_geospatial_service,
    analyze_location,
    haversine_distance,
)

__all__ = [
    # Market lookup
    "MarketBenchmarks",
    "MarketDataAdapter", 
    "get_market_adapter",
    "validate_inputs_against_market",
    "get_market_summary",
    
    # Currency
    "ExchangeRate",
    "CurrencyProvider",
    "StaticCurrencyProvider",
    "LiveCurrencyProvider", 
    "CurrencyService",
    "get_currency_service",
    "convert_currency",
    "get_exchange_rates_vs_usd",
    
    # Geospatial
    "Coordinates",
    "Address",
    "ParcelInfo",
    "NearbyAmenity",
    "GeospatialProvider",
    "StubGeospatialProvider",
    "GeospatialService", 
    "get_geospatial_service",
    "analyze_location",
    "haversine_distance",
]