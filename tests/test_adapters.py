"""
Test suite for adapter modules.
Tests market data, currency, and geospatial adapters.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from modules.adapters.market_lookup import (
    MarketBenchmarks,
    MarketDataAdapter,
    get_market_adapter,
    validate_inputs_against_market,
    get_market_summary,
)

from modules.adapters.currency import (
    ExchangeRate,
    StaticCurrencyProvider,
    LiveCurrencyProvider,
    CurrencyService,
    convert_currency,
    get_exchange_rates_vs_usd,
)

from modules.adapters.geospatial import (
    Coordinates,
    Address,
    ParcelInfo,
    NearbyAmenity,
    StubGeospatialProvider,
    GeospatialService,
    haversine_distance,
    analyze_location,
)

from modules.policies.registry import ConfigRegistry
from datetime import datetime, timedelta


class TestMarketBenchmarks:
    """Test market benchmarks data container."""
    
    def test_market_benchmarks_creation(self):
        """Test creating market benchmarks."""
        benchmarks = MarketBenchmarks(
            location_key="test_location",
            land_comps_psm={"land_comp_avg": 500},
            sale_prices={"sale_price_avg_sqm": 4000},
            construction_costs={"construction_cost_avg": 2000},
            market_indicators={"demand_score": 4},
            data_freshness_days=30,
            confidence_score=0.85
        )
        
        assert benchmarks.location_key == "test_location"
        assert benchmarks.land_comps_psm["land_comp_avg"] == 500
        assert benchmarks.data_freshness_days == 30
        assert benchmarks.confidence_score == 0.85


class TestMarketDataAdapter:
    """Test market data adapter functionality."""
    
    @pytest.fixture
    def mock_ruleset(self):
        """Create mock ruleset for testing."""
        ruleset = Mock()
        ruleset.country_code = "TEST"
        ruleset.country_rules.currency = "TCC"
        ruleset.country_rules.name = "Test Country"
        
        # Mock market config
        ruleset.market_config.locations = {
            "test_city": {
                "tier": 1,
                "demand_score": 4,
                "liquidity_score": 3
            }
        }
        
        ruleset.market_config.data_keys = {
            "land_comps": ["land_comp_min", "land_comp_avg", "land_comp_max"],
            "sale_prices": ["sale_price_avg_sqm"],
            "construction_costs": ["construction_cost_avg"],
            "market_indicators": ["absorption_rate", "demand_score"]
        }
        
        ruleset.market_config.fallback_values = {
            "land_comp_avg": 400,
            "sale_price_avg_sqm": 3500,
            "construction_cost_avg": 1800,
            "absorption_rate": 3.5
        }
        
        ruleset.market_config.validation = {
            "sale_price_variance_threshold": 0.30,
            "construction_cost_variance_threshold": 0.25
        }
        
        return ruleset
    
    def test_load_fallback_benchmarks(self, mock_ruleset):
        """Test loading fallback benchmark values."""
        adapter = MarketDataAdapter(mock_ruleset)
        benchmarks = adapter._get_fallback_benchmarks("test_city")
        
        assert benchmarks.location_key == "test_city"
        assert benchmarks.land_comps_psm["land_comp_avg"] == 400
        assert benchmarks.sale_prices["sale_price_avg_sqm"] == 3500
        assert benchmarks.construction_costs["construction_cost_avg"] == 1800
        assert benchmarks.market_indicators["demand_score"] == 4
        assert benchmarks.market_indicators["absorption_rate"] == 3.5
        assert benchmarks.confidence_score == 0.7  # Lower for fallback data
    
    def test_validate_sale_price_within_range(self, mock_ruleset):
        """Test sale price validation within acceptable range."""
        adapter = MarketDataAdapter(mock_ruleset)
        benchmarks = adapter._get_fallback_benchmarks("test_city")
        
        # Price within 30% of market average (3500)
        warnings = adapter._validate_sale_price(3200, benchmarks, mock_ruleset.market_config.validation)
        assert len(warnings) == 0
    
    def test_validate_sale_price_outside_range(self, mock_ruleset):
        """Test sale price validation outside acceptable range."""
        adapter = MarketDataAdapter(mock_ruleset)
        benchmarks = adapter._get_fallback_benchmarks("test_city")
        
        # Price significantly above market average
        warnings = adapter._validate_sale_price(5000, benchmarks, mock_ruleset.market_config.validation)
        assert len(warnings) == 1
        assert "sale_price" in warnings
        assert "significantly above" in warnings["sale_price"]
    
    def test_validate_construction_cost_within_range(self, mock_ruleset):
        """Test construction cost validation within range."""
        adapter = MarketDataAdapter(mock_ruleset)
        benchmarks = adapter._get_fallback_benchmarks("test_city")
        
        # Cost within 25% of market average (1800)
        warnings = adapter._validate_construction_cost(1600, benchmarks, mock_ruleset.market_config.validation)
        assert len(warnings) == 0
    
    def test_validate_construction_cost_outside_range(self, mock_ruleset):
        """Test construction cost validation outside range."""
        adapter = MarketDataAdapter(mock_ruleset)
        benchmarks = adapter._get_fallback_benchmarks("test_city")
        
        # Cost significantly below market average
        warnings = adapter._validate_construction_cost(1200, benchmarks, mock_ruleset.market_config.validation)
        assert len(warnings) == 1
        assert "construction_cost" in warnings
        assert "significantly below" in warnings["construction_cost"]
    
    def test_validate_inputs_against_market(self, mock_ruleset):
        """Test comprehensive input validation."""
        adapter = MarketDataAdapter(mock_ruleset)
        
        inputs_dict = {
            "expected_sale_price_psm": 5000,  # Too high
            "construction_cost_psm": 1200,   # Too low
            "soft_cost_pct": 0.20            # Different from typical
        }
        
        warnings = adapter.validate_inputs_against_market(inputs_dict, "test_city")
        
        assert len(warnings) >= 2  # At least sale price and construction cost warnings
        assert "sale_price" in warnings
        assert "construction_cost" in warnings
    
    def test_get_market_summary(self, mock_ruleset):
        """Test market summary generation."""
        adapter = MarketDataAdapter(mock_ruleset)
        summary = adapter.get_market_summary("test_city")
        
        assert summary["location"] == "Test City"
        assert summary["country"] == "Test Country"
        assert summary["currency"] == "TCC"
        assert summary["market_tier"] == 1
        assert summary["demand_strength"] == "Strong"  # Score 4 -> Strong
        assert "data_confidence" in summary
        assert "data_freshness" in summary
    
    def test_get_available_locations(self, mock_ruleset):
        """Test getting available locations."""
        adapter = MarketDataAdapter(mock_ruleset)
        locations = adapter.get_available_locations()
        
        assert "test_city" in locations


class TestExchangeRate:
    """Test exchange rate data structure."""
    
    def test_exchange_rate_creation(self):
        """Test creating exchange rate."""
        timestamp = datetime.now()
        rate = ExchangeRate(
            base_currency="USD",
            target_currency="EUR",
            rate=0.85,
            timestamp=timestamp,
            provider="test_provider"
        )
        
        assert rate.base_currency == "USD"
        assert rate.target_currency == "EUR"
        assert rate.rate == 0.85
        assert rate.timestamp == timestamp
        assert rate.provider == "test_provider"
    
    def test_exchange_rate_age_calculation(self):
        """Test exchange rate age calculation."""
        old_timestamp = datetime.now() - timedelta(hours=2)
        rate = ExchangeRate(
            base_currency="USD",
            target_currency="EUR",
            rate=0.85,
            timestamp=old_timestamp,
            provider="test"
        )
        
        assert rate.age_hours >= 1.9  # Should be approximately 2 hours
        assert rate.is_stale == True  # Assuming 24h threshold


class TestStaticCurrencyProvider:
    """Test static currency provider."""
    
    def test_static_provider_same_currency(self):
        """Test conversion between same currencies."""
        provider = StaticCurrencyProvider()
        rate = provider.get_exchange_rate("USD", "USD")
        
        assert rate.rate == 1.0
        assert rate.base_currency == "USD"
        assert rate.target_currency == "USD"
    
    def test_static_provider_usd_to_jod(self):
        """Test USD to JOD conversion."""
        provider = StaticCurrencyProvider()
        rate = provider.get_exchange_rate("USD", "JOD")
        
        assert rate.rate == 0.708  # Static rate for JOD
        assert rate.base_currency == "USD"
        assert rate.target_currency == "JOD"
    
    def test_static_provider_jod_to_aed(self):
        """Test JOD to AED conversion via USD."""
        provider = StaticCurrencyProvider()
        rate = provider.get_exchange_rate("JOD", "AED")
        
        # JOD to USD: 1/0.708, USD to AED: 3.673
        expected_rate = 3.673 / 0.708
        assert abs(rate.rate - expected_rate) < 0.001
    
    def test_static_provider_unsupported_currency(self):
        """Test conversion with unsupported currency."""
        provider = StaticCurrencyProvider()
        rate = provider.get_exchange_rate("USD", "XXX")
        
        assert rate is None
    
    def test_static_provider_multiple_rates(self):
        """Test getting multiple exchange rates."""
        provider = StaticCurrencyProvider()
        rates = provider.get_multiple_rates("USD", ["JOD", "AED", "EUR"])
        
        assert len(rates) == 3
        assert "JOD" in rates
        assert "AED" in rates
        assert "EUR" in rates
        assert rates["JOD"].rate == 0.708
        assert rates["AED"].rate == 3.673
    
    def test_static_provider_availability(self):
        """Test provider availability."""
        provider = StaticCurrencyProvider()
        assert provider.is_available() == True
    
    def test_static_provider_supported_currencies(self):
        """Test getting supported currencies."""
        provider = StaticCurrencyProvider()
        currencies = provider.get_supported_currencies()
        
        assert "USD" in currencies
        assert "JOD" in currencies
        assert "AED" in currencies
        assert "EUR" in currencies


class TestCurrencyService:
    """Test currency service functionality."""
    
    def test_currency_service_initialization(self):
        """Test currency service initialization."""
        service = CurrencyService(live_provider=False)
        
        # Should have static provider
        assert len(service.providers) == 1
        assert isinstance(service.providers[0], StaticCurrencyProvider)
    
    def test_currency_service_get_exchange_rate(self):
        """Test getting exchange rate through service."""
        service = CurrencyService(live_provider=False)
        rate = service.get_exchange_rate("USD", "JOD")
        
        assert rate is not None
        assert rate.base_currency == "USD"
        assert rate.target_currency == "JOD"
        assert rate.rate == 0.708
    
    def test_currency_service_convert_amount(self):
        """Test currency amount conversion."""
        service = CurrencyService(live_provider=False)
        converted = service.convert_amount(1000, "USD", "JOD")
        
        assert converted == 708  # 1000 * 0.708
    
    def test_currency_service_rates_vs_usd(self):
        """Test getting rates vs USD."""
        service = CurrencyService(live_provider=False)
        rates = service.get_rates_vs_usd(["JOD", "AED", "EUR"])
        
        assert "JOD" in rates
        assert "AED" in rates
        assert "EUR" in rates
        assert rates["JOD"] == 0.708
        assert rates["AED"] == 3.673
    
    def test_currency_service_caching(self):
        """Test exchange rate caching."""
        service = CurrencyService(live_provider=False)
        
        # First call
        rate1 = service.get_exchange_rate("USD", "JOD", use_cache=True)
        
        # Second call should use cache
        rate2 = service.get_exchange_rate("USD", "JOD", use_cache=True)
        
        assert rate1.rate == rate2.rate
        # Should be same timestamp if from cache
        assert rate1.timestamp == rate2.timestamp
    
    def test_convert_currency_convenience_function(self):
        """Test convenience function for currency conversion."""
        converted = convert_currency(1000, "USD", "JOD")
        
        assert converted == 708
    
    def test_get_exchange_rates_vs_usd_convenience(self):
        """Test convenience function for getting USD rates."""
        rates = get_exchange_rates_vs_usd()
        
        assert isinstance(rates, dict)
        assert "JOD" in rates
        assert "AED" in rates


class TestCoordinates:
    """Test coordinates data structure."""
    
    def test_valid_coordinates(self):
        """Test creating valid coordinates."""
        coords = Coordinates(latitude=25.2048, longitude=55.2708)
        
        assert coords.latitude == 25.2048
        assert coords.longitude == 55.2708
    
    def test_invalid_latitude(self):
        """Test invalid latitude validation."""
        with pytest.raises(ValueError, match="Invalid latitude"):
            Coordinates(latitude=91.0, longitude=0.0)
        
        with pytest.raises(ValueError, match="Invalid latitude"):
            Coordinates(latitude=-91.0, longitude=0.0)
    
    def test_invalid_longitude(self):
        """Test invalid longitude validation."""
        with pytest.raises(ValueError, match="Invalid longitude"):
            Coordinates(latitude=0.0, longitude=181.0)
        
        with pytest.raises(ValueError, match="Invalid longitude"):
            Coordinates(latitude=0.0, longitude=-181.0)
    
    def test_distance_calculation(self):
        """Test distance calculation between coordinates."""
        dubai = Coordinates(25.2048, 55.2708)
        abu_dhabi = Coordinates(24.4539, 54.3773)
        
        distance = dubai.distance_to(abu_dhabi)
        
        # Distance between Dubai and Abu Dhabi is approximately 140km
        assert 130 <= distance <= 150


class TestAddress:
    """Test address data structure."""
    
    def test_address_creation(self):
        """Test creating address."""
        address = Address(
            street="123 Main Street",
            city="Dubai",
            region="Dubai",
            country="UAE",
            postal_code="12345"
        )
        
        assert address.street == "123 Main Street"
        assert address.city == "Dubai"
        assert address.region == "Dubai"
        assert address.country == "UAE"
        assert address.postal_code == "12345"
    
    def test_address_string_representation(self):
        """Test address string formatting."""
        address = Address(
            street="123 Main Street",
            city="Dubai",
            region="Dubai",
            country="UAE",
            postal_code="12345"
        )
        
        address_str = str(address)
        expected = "123 Main Street, Dubai, Dubai, UAE, 12345"
        assert address_str == expected
    
    def test_address_without_postal_code(self):
        """Test address without postal code."""
        address = Address(
            street="123 Main Street",
            city="Dubai",
            region="Dubai",
            country="UAE"
        )
        
        address_str = str(address)
        expected = "123 Main Street, Dubai, Dubai, UAE"
        assert address_str == expected


class TestHaversineDistance:
    """Test haversine distance calculation."""
    
    def test_same_coordinates(self):
        """Test distance between same coordinates."""
        distance = haversine_distance(25.2048, 55.2708, 25.2048, 55.2708)
        assert distance == 0.0
    
    def test_known_distance(self):
        """Test known distance calculation."""
        # Dubai to Abu Dhabi
        distance = haversine_distance(25.2048, 55.2708, 24.4539, 54.3773)
        
        # Should be approximately 140km
        assert 130 <= distance <= 150
    
    def test_long_distance(self):
        """Test long distance calculation."""
        # Dubai to London
        distance = haversine_distance(25.2048, 55.2708, 51.5074, -0.1278)
        
        # Should be approximately 5500km
        assert 5400 <= distance <= 5600


class TestStubGeospatialProvider:
    """Test stub geospatial provider."""
    
    def test_geocode_known_city(self):
        """Test geocoding known city."""
        provider = StubGeospatialProvider()
        coords = provider.geocode_address("Downtown Dubai, UAE")
        
        assert coords is not None
        # Should be close to Dubai coordinates
        assert abs(coords.latitude - 25.2048) < 0.1
        assert abs(coords.longitude - 55.2708) < 0.1
    
    def test_geocode_unknown_location(self):
        """Test geocoding unknown location."""
        provider = StubGeospatialProvider()
        coords = provider.geocode_address("Unknown Location")
        
        assert coords is None
    
    def test_reverse_geocode_dubai_area(self):
        """Test reverse geocoding in Dubai area."""
        provider = StubGeospatialProvider()
        dubai_coords = Coordinates(25.2048, 55.2708)
        address = provider.reverse_geocode(dubai_coords)
        
        assert address is not None
        assert "dubai" in address.city.lower()
        assert address.country == "UAE"
        assert address.region == "Dubai"
    
    def test_reverse_geocode_remote_location(self):
        """Test reverse geocoding remote location."""
        provider = StubGeospatialProvider()
        remote_coords = Coordinates(0.0, 0.0)  # Middle of ocean
        address = provider.reverse_geocode(remote_coords)
        
        assert address is None  # Too far from any known city
    
    def test_get_parcel_info(self):
        """Test getting parcel information."""
        provider = StubGeospatialProvider()
        dubai_coords = Coordinates(25.2048, 55.2708)
        parcel = provider.get_parcel_info(dubai_coords)
        
        assert parcel is not None
        assert parcel.coordinates == dubai_coords
        assert parcel.parcel_id.startswith("PARCEL_")
        assert parcel.area_sqm >= 500
        assert parcel.area_sqm <= 2500
        assert parcel.zoning in ["G_PLUS_4", "G_PLUS_9", "HIGH_RISE", "MIXED_USE"]
        assert parcel.ownership_type in ["freehold", "leasehold"]
    
    def test_find_nearby_amenities(self):
        """Test finding nearby amenities."""
        provider = StubGeospatialProvider()
        dubai_coords = Coordinates(25.2048, 55.2708)
        
        amenities = provider.find_nearby_amenities(
            dubai_coords,
            radius_m=1000,
            categories=["school", "hospital", "retail"]
        )
        
        assert len(amenities) == 3  # One for each category
        
        for amenity in amenities:
            assert isinstance(amenity, NearbyAmenity)
            assert amenity.category in ["school", "hospital", "retail"]
            assert amenity.distance_m <= 1000
            assert isinstance(amenity.coordinates, Coordinates)
    
    def test_find_nearby_amenities_default_categories(self):
        """Test finding amenities with default categories."""
        provider = StubGeospatialProvider()
        dubai_coords = Coordinates(25.2048, 55.2708)
        
        amenities = provider.find_nearby_amenities(dubai_coords, radius_m=500)
        
        # Should include default categories
        assert len(amenities) == 5  # Default categories: school, hospital, transport, retail, mosque
        categories = [a.category for a in amenities]
        assert "school" in categories
        assert "hospital" in categories
        assert "transport" in categories
        assert "retail" in categories
        assert "mosque" in categories


class TestGeospatialService:
    """Test geospatial service functionality."""
    
    def test_analyze_location_with_address(self):
        """Test location analysis with address string."""
        service = GeospatialService()
        analysis = service.analyze_location("Dubai Marina, Dubai, UAE", analysis_radius_m=1000)
        
        assert "coordinates" in analysis
        assert "parcel_info" in analysis
        assert "amenities" in analysis
        
        # Check coordinates
        coords = analysis["coordinates"]
        assert "latitude" in coords
        assert "longitude" in coords
        
        # Check parcel info
        parcel = analysis["parcel_info"]
        assert "parcel_id" in parcel
        assert "area_sqm" in parcel
        assert "zoning" in parcel
        
        # Check amenities analysis
        amenities = analysis["amenities"]
        assert "total_count" in amenities
        assert "by_category" in amenities
        assert "accessibility_score" in amenities
        assert "nearest_amenities" in amenities
        assert amenities["total_count"] > 0
        assert 0 <= amenities["accessibility_score"] <= 100
    
    def test_analyze_location_with_coordinates(self):
        """Test location analysis with coordinates object."""
        service = GeospatialService()
        coords = Coordinates(25.2048, 55.2708)
        analysis = service.analyze_location(coords, analysis_radius_m=500)
        
        assert analysis["coordinates"]["latitude"] == coords.latitude
        assert analysis["coordinates"]["longitude"] == coords.longitude
        assert analysis["analysis_radius_m"] == 500
    
    def test_analyze_location_unknown_address(self):
        """Test location analysis with unknown address."""
        service = GeospatialService()
        analysis = service.analyze_location("Unknown Location", analysis_radius_m=1000)
        
        assert "error" in analysis
        assert "Could not geocode address" in analysis["error"]
    
    def test_calculate_commute_analysis(self):
        """Test commute analysis calculation."""
        service = GeospatialService()
        from_coords = Coordinates(25.2048, 55.2708)  # Dubai
        to_addresses = ["Abu Dhabi, UAE", "Sharjah, UAE"]
        
        commute_times = service.calculate_commute_analysis(from_coords, to_addresses)
        
        assert len(commute_times) == 2
        
        for address in to_addresses:
            assert address in commute_times
            commute_info = commute_times[address]
            assert "distance_km" in commute_info
            assert "commute_minutes" in commute_info
            assert "commute_category" in commute_info
            assert commute_info["commute_category"] in ["short", "medium", "long"]
    
    def test_amenity_analysis_scoring(self):
        """Test amenity accessibility scoring."""
        service = GeospatialService()
        
        # Create mock amenities at different distances
        amenities = [
            NearbyAmenity("School 1", "school", Coordinates(25.2048, 55.2708), 300, "Mock school"),
            NearbyAmenity("Hospital 1", "hospital", Coordinates(25.2048, 55.2708), 400, "Mock hospital"),
            NearbyAmenity("Transport 1", "transport", Coordinates(25.2048, 55.2708), 600, "Mock transport"),
            NearbyAmenity("Retail 1", "retail", Coordinates(25.2048, 55.2708), 800, "Mock retail"),
        ]
        
        analysis = service._analyze_amenities(amenities)
        
        assert analysis["by_category"]["school"] == 1
        assert analysis["by_category"]["hospital"] == 1
        assert analysis["by_category"]["transport"] == 1
        assert analysis["by_category"]["retail"] == 1
        
        # All amenities are within 1km, so should get high score
        # school(300m): 25pts, hospital(400m): 25pts, transport(600m): 15pts, retail(800m): 15pts = 80pts
        assert analysis["accessibility_score"] == 80


class TestLocationAnalysisConvenience:
    """Test convenience function for location analysis."""
    
    def test_analyze_location_convenience_function(self):
        """Test convenience function for location analysis."""
        analysis = analyze_location("Dubai, UAE", analysis_radius_m=1000)
        
        assert isinstance(analysis, dict)
        assert "coordinates" in analysis
        assert "parcel_info" in analysis
        assert "amenities" in analysis
        assert analysis["analysis_radius_m"] == 1000