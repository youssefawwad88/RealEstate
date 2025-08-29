"""
Test suite for utility modules.
Tests logging, error handling, and unit conversion utilities.
"""

import pytest
import tempfile
import logging
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from utils.logging import (
    TerraFlowFormatter,
    setup_logging,
    get_logger,
    LoggingContext,
    log_deal_calculation,
    log_validation_issues,
    init_terraflow_logging,
)

from utils.errors import (
    TerraFlowError,
    ConfigurationError,
    ValidationError,
    ZoningComplianceError,
    CalculationError,
    MarketDataError,
    handle_calculation_errors,
    handle_validation_errors,
    create_error_summary,
    format_validation_errors,
)

from utils.units import (
    AreaUnit,
    LengthUnit,
    VolumeUnit,
    Measurement,
    convert_area,
    convert_length,
    convert_volume,
    area_sqm_to_sqft,
    area_sqft_to_sqm,
    format_area,
    parse_area_string,
    standardize_area_units,
    calculate_price_per_unit,
    common_real_estate_conversions,
)


class TestTerraFlowFormatter:
    """Test custom logging formatter."""
    
    def test_formatter_basic_formatting(self):
        """Test basic log formatting."""
        formatter = TerraFlowFormatter()
        
        # Create mock log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.module = "test_module"
        record.funcName = "test_function"
        
        formatted = formatter.format(record)
        
        assert "Test message" in formatted
        assert "INFO" in formatted
        assert "test_module" in formatted
        assert "test_function" in formatted
    
    def test_formatter_with_extra_context(self):
        """Test formatting with extra context."""
        formatter = TerraFlowFormatter()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Deal calculation completed",
            args=(),
            exc_info=None
        )
        record.module = "test_module"
        record.funcName = "test_function"
        record.deal_id = "DEAL_123"
        record.country_code = "UAE"
        record.execution_time = 150.5
        
        formatted = formatter.format(record)
        
        assert "deal_id" in formatted
        assert "DEAL_123" in formatted
        assert "country_code" in formatted
        assert "UAE" in formatted
        assert "execution_time_ms" in formatted
        assert "150.5" in formatted
    
    def test_formatter_without_timestamp(self):
        """Test formatter without timestamp."""
        formatter = TerraFlowFormatter(include_timestamp=False)
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        assert "timestamp" not in formatted
        assert "Test message" in formatted


class TestLoggingSetup:
    """Test logging setup functionality."""
    
    def test_setup_logging_basic(self):
        """Test basic logging setup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            
            logger = setup_logging(
                level="INFO",
                log_file=log_file,
                structured=True,
                console=False
            )
            
            assert logger.level == logging.INFO
            assert log_file.exists() == False  # File created on first write
            
            # Test logging
            logger.info("Test message")
            assert log_file.exists() == True
    
    def test_setup_logging_console_only(self):
        """Test console-only logging setup."""
        logger = setup_logging(
            level="DEBUG",
            log_file=None,
            structured=False,
            console=True
        )
        
        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1  # Console handler only
    
    def test_get_logger(self):
        """Test getting logger instance."""
        logger = get_logger("test_module")
        
        assert logger.name == "test_module"
        assert isinstance(logger, logging.Logger)


class TestLoggingContext:
    """Test logging context manager."""
    
    def test_logging_context_basic(self):
        """Test basic logging context functionality."""
        logger = get_logger("test")
        
        with LoggingContext(logger, deal_id="DEAL_123", country_code="UAE"):
            # Context should be added to log records within this block
            pass
        
        # Context manager should clean up filters
        assert len(logger.filters) == 0
    
    def test_log_deal_calculation(self):
        """Test deal calculation logging."""
        logger = get_logger("test")
        
        # Mock logger to capture log calls
        with patch.object(logger, 'info') as mock_info:
            log_deal_calculation(
                logger=logger,
                deal_id="DEAL_123",
                inputs={"land_area_sqm": 1000, "asking_price": 500000},
                outputs={"residual_land_value": 600000, "overall_status": "Viable"},
                execution_time_ms=125.5,
                country_code="UAE"
            )
            
            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert "DEAL_123" in call_args
            assert "600,000" in call_args
            assert "Viable" in call_args
    
    def test_log_validation_issues(self):
        """Test validation issues logging."""
        logger = get_logger("test")
        
        # Mock validation report
        mock_report = Mock()
        mock_report.errors = [
            Mock(message="Test error 1", code="ERROR_1"),
            Mock(message="Test error 2", code="ERROR_2")
        ]
        mock_report.warnings = [
            Mock(message="Test warning", code="WARNING_1")
        ]
        mock_report.is_valid = False
        
        with patch.object(logger, 'warning') as mock_warning, \
             patch.object(logger, 'error') as mock_error, \
             patch.object(logger, 'info') as mock_info:
            
            log_validation_issues(
                logger=logger,
                deal_id="DEAL_123",
                validation_report=mock_report,
                country_code="UAE"
            )
            
            # Should log overall warning about errors
            mock_warning.assert_called()
            
            # Should log individual errors
            assert mock_error.call_count == 2


class TestTerraFlowErrors:
    """Test custom error classes."""
    
    def test_terraflow_error_basic(self):
        """Test basic TerraFlow error."""
        error = TerraFlowError(
            message="Test error message",
            error_code="TEST_ERROR",
            context={"key": "value"}
        )
        
        assert error.message == "Test error message"
        assert error.error_code == "TEST_ERROR"
        assert error.context["key"] == "value"
        assert "[TEST_ERROR]" in str(error)
        assert "Context: key=value" in str(error)
    
    def test_configuration_error(self):
        """Test configuration error."""
        error = ConfigurationError(
            message="Config file not found",
            country_code="UAE",
            config_file="country.yml"
        )
        
        assert error.error_code == "CONFIG_ERROR"
        assert error.context["country_code"] == "UAE"
        assert error.context["config_file"] == "country.yml"
    
    def test_validation_error(self):
        """Test validation error."""
        error = ValidationError(
            message="Invalid value",
            field="far",
            value=5.0,
            validation_code="FAR_EXCEEDED"
        )
        
        assert error.error_code == "FAR_EXCEEDED"
        assert error.context["field"] == "far"
        assert error.context["value"] == "5.0"
    
    def test_zoning_compliance_error(self):
        """Test zoning compliance error."""
        error = ZoningComplianceError(
            message="FAR exceeds zoning limit",
            zoning_code="R1",
            parameter="far",
            provided_value=2.5,
            max_allowed=2.0
        )
        
        assert error.error_code == "ZONING_COMPLIANCE_ERROR"
        assert error.context["zoning_code"] == "R1"
        assert error.context["parameter"] == "far"
        assert error.context["provided_value"] == "2.5"
        assert error.context["max_allowed"] == "2.0"
    
    def test_calculation_error(self):
        """Test calculation error."""
        error = CalculationError(
            message="Division by zero",
            calculation_type="residual_calculation",
            input_values={"gdv": 0, "costs": 100000}
        )
        
        assert error.error_code == "CALCULATION_ERROR"
        assert error.context["calculation_type"] == "residual_calculation"
        assert "gdv" in error.context["input_values"]
    
    def test_market_data_error(self):
        """Test market data error."""
        error = MarketDataError(
            message="Market data unavailable",
            location_key="dubai_marina",
            country_code="UAE",
            data_source="api_provider"
        )
        
        assert error.error_code == "MARKET_DATA_ERROR"
        assert error.context["location_key"] == "dubai_marina"
        assert error.context["country_code"] == "UAE"
        assert error.context["data_source"] == "api_provider"


class TestErrorDecorators:
    """Test error handling decorators."""
    
    def test_handle_calculation_errors_zero_division(self):
        """Test calculation error decorator with zero division."""
        @handle_calculation_errors
        def divide_by_zero():
            return 10 / 0
        
        with pytest.raises(CalculationError) as exc_info:
            divide_by_zero()
        
        assert "Division by zero" in str(exc_info.value)
        assert exc_info.value.error_code == "CALCULATION_ERROR"
    
    def test_handle_calculation_errors_value_error(self):
        """Test calculation error decorator with value error."""
        @handle_calculation_errors
        def invalid_value():
            return float("invalid")
        
        with pytest.raises(CalculationError) as exc_info:
            invalid_value()
        
        assert "Invalid value" in str(exc_info.value)
    
    def test_handle_calculation_errors_terraflow_error_passthrough(self):
        """Test that TerraFlow errors pass through unchanged."""
        @handle_calculation_errors
        def raise_terraflow_error():
            raise ValidationError("Original error")
        
        with pytest.raises(ValidationError) as exc_info:
            raise_terraflow_error()
        
        assert exc_info.value.message == "Original error"
    
    def test_handle_validation_errors_value_error(self):
        """Test validation error decorator."""
        @handle_validation_errors
        def invalid_validation():
            raise ValueError("Invalid input")
        
        with pytest.raises(ValidationError) as exc_info:
            invalid_validation()
        
        assert "Validation failed" in str(exc_info.value)
        assert "Invalid input" in str(exc_info.value)


class TestErrorSummary:
    """Test error summary functions."""
    
    def test_create_error_summary_empty(self):
        """Test error summary with empty list."""
        summary = create_error_summary([])
        
        assert summary["total_errors"] == 0
        assert summary["error_types"] == {}
        assert summary["messages"] == []
    
    def test_create_error_summary_mixed_errors(self):
        """Test error summary with mixed error types."""
        errors = [
            ValidationError("Validation failed"),
            ValidationError("Another validation error"),
            CalculationError("Calculation failed"),
            ValueError("Standard Python error")
        ]
        
        summary = create_error_summary(errors)
        
        assert summary["total_errors"] == 4
        assert summary["error_types"]["ValidationError"] == 2
        assert summary["error_types"]["CalculationError"] == 1
        assert summary["error_types"]["ValueError"] == 1
        
        assert len(summary["messages"]) == 4
        
        # Check TerraFlow error format
        terraflow_messages = [msg for msg in summary["messages"] if "code" in msg]
        assert len(terraflow_messages) == 3  # ValidationError and CalculationError
        
        # Check standard error format
        standard_messages = [msg for msg in summary["messages"] if "code" not in msg]
        assert len(standard_messages) == 1
    
    def test_format_validation_errors_empty(self):
        """Test formatting empty validation errors."""
        formatted = format_validation_errors([])
        assert formatted == "No validation errors"
    
    def test_format_validation_errors_with_issues(self):
        """Test formatting validation errors with issues."""
        # Mock validation issues
        issues = [
            Mock(message="FAR exceeded", field="far", suggestion="Reduce FAR to 2.0"),
            Mock(message="Coverage too high", field="coverage", suggestion="Reduce coverage"),
            Mock(message="Info message", field=None, suggestion=None)
        ]
        
        formatted = format_validation_errors(issues)
        
        assert "FAR exceeded" in formatted
        assert "Field: far" in formatted
        assert "Suggestion: Reduce FAR to 2.0" in formatted
        assert "Coverage too high" in formatted
        assert "Info message" in formatted
        assert formatted.count("-") == 3  # Three bullet points


class TestAreaConversions:
    """Test area unit conversions."""
    
    def test_sqm_to_sqft_conversion(self):
        """Test square meters to square feet conversion."""
        sqft = convert_area(100, AreaUnit.SQM, AreaUnit.SQFT)
        assert abs(sqft - 1076.39) < 0.1  # 100 sqm ≈ 1076.39 sqft
    
    def test_sqft_to_sqm_conversion(self):
        """Test square feet to square meters conversion."""
        sqm = convert_area(1000, AreaUnit.SQFT, AreaUnit.SQM)
        assert abs(sqm - 92.90) < 0.1  # 1000 sqft ≈ 92.90 sqm
    
    def test_same_unit_conversion(self):
        """Test conversion between same units."""
        result = convert_area(500, AreaUnit.SQM, AreaUnit.SQM)
        assert result == 500
    
    def test_hectare_to_sqm_conversion(self):
        """Test hectare to square meters conversion."""
        sqm = convert_area(1, AreaUnit.HECTARE, AreaUnit.SQM)
        assert sqm == 10000  # 1 hectare = 10,000 sqm
    
    def test_acre_to_sqm_conversion(self):
        """Test acre to square meters conversion."""
        sqm = convert_area(1, AreaUnit.ACRE, AreaUnit.SQM)
        assert abs(sqm - 4046.86) < 0.1  # 1 acre ≈ 4046.86 sqm
    
    def test_dunum_to_sqm_conversion(self):
        """Test dunum to square meters conversion."""
        sqm = convert_area(1, AreaUnit.DUNUM, AreaUnit.SQM)
        assert sqm == 1000  # 1 dunum = 1000 sqm (varies by region)


class TestLengthConversions:
    """Test length unit conversions."""
    
    def test_meters_to_feet_conversion(self):
        """Test meters to feet conversion."""
        feet = convert_length(10, LengthUnit.METER, LengthUnit.FOOT)
        assert abs(feet - 32.808) < 0.01  # 10m ≈ 32.808 ft
    
    def test_feet_to_meters_conversion(self):
        """Test feet to meters conversion."""
        meters = convert_length(100, LengthUnit.FOOT, LengthUnit.METER)
        assert abs(meters - 30.48) < 0.01  # 100 ft ≈ 30.48 m
    
    def test_kilometers_to_miles_conversion(self):
        """Test kilometers to miles conversion."""
        miles = convert_length(10, LengthUnit.KILOMETER, LengthUnit.MILE)
        assert abs(miles - 6.214) < 0.01  # 10 km ≈ 6.214 miles


class TestVolumeConversions:
    """Test volume unit conversions."""
    
    def test_cubic_meters_to_cubic_feet(self):
        """Test cubic meters to cubic feet conversion."""
        cbft = convert_volume(10, VolumeUnit.CUBIC_METER, VolumeUnit.CUBIC_FOOT)
        assert abs(cbft - 353.15) < 0.1  # 10 cbm ≈ 353.15 cbft
    
    def test_liters_to_cubic_meters(self):
        """Test liters to cubic meters conversion."""
        cbm = convert_volume(1000, VolumeUnit.LITER, VolumeUnit.CUBIC_METER)
        assert cbm == 1.0  # 1000 L = 1 cbm
    
    def test_gallons_to_liters(self):
        """Test gallons to liters conversion."""
        liters = convert_volume(10, VolumeUnit.GALLON, VolumeUnit.LITER)
        assert abs(liters - 37.85) < 0.1  # 10 US gallons ≈ 37.85 L


class TestMeasurement:
    """Test measurement class functionality."""
    
    def test_measurement_creation(self):
        """Test creating measurement."""
        measurement = Measurement(value=1000, unit=AreaUnit.SQM)
        
        assert measurement.value == 1000
        assert measurement.unit == AreaUnit.SQM
    
    def test_measurement_conversion(self):
        """Test measurement unit conversion."""
        sqm_measurement = Measurement(value=100, unit=AreaUnit.SQM)
        sqft_measurement = sqm_measurement.convert_to(AreaUnit.SQFT)
        
        assert sqft_measurement.unit == AreaUnit.SQFT
        assert abs(sqft_measurement.value - 1076.39) < 0.1
    
    def test_measurement_invalid_conversion(self):
        """Test invalid measurement conversion."""
        area_measurement = Measurement(value=100, unit=AreaUnit.SQM)
        
        with pytest.raises(ValueError, match="Cannot convert"):
            area_measurement.convert_to(LengthUnit.METER)
    
    def test_measurement_string_representation(self):
        """Test measurement string formatting."""
        measurement = Measurement(value=1500.75, unit=AreaUnit.SQM)
        
        measurement_str = str(measurement)
        assert "1,500.75" in measurement_str
        assert "sqm" in measurement_str


class TestConvenienceFunctions:
    """Test convenience conversion functions."""
    
    def test_area_sqm_to_sqft(self):
        """Test sqm to sqft convenience function."""
        sqft = area_sqm_to_sqft(100)
        assert abs(sqft - 1076.39) < 0.1
    
    def test_area_sqft_to_sqm(self):
        """Test sqft to sqm convenience function."""
        sqm = area_sqft_to_sqm(1000)
        assert abs(sqm - 92.90) < 0.1
    
    def test_length_m_to_ft(self):
        """Test meters to feet convenience function."""
        from utils.units import length_m_to_ft
        feet = length_m_to_ft(10)
        assert abs(feet - 32.808) < 0.01
    
    def test_length_ft_to_m(self):
        """Test feet to meters convenience function."""
        from utils.units import length_ft_to_m
        meters = length_ft_to_m(100)
        assert abs(meters - 30.48) < 0.01


class TestFormatting:
    """Test unit formatting functions."""
    
    def test_format_area_basic(self):
        """Test basic area formatting."""
        formatted = format_area(1500.75, AreaUnit.SQM, precision=1)
        assert formatted == "1,500.8 m²"
    
    def test_format_area_different_units(self):
        """Test formatting different area units."""
        # Square feet
        sqft_formatted = format_area(10000, AreaUnit.SQFT, precision=0)
        assert "10,000 ft²" in sqft_formatted
        
        # Hectares
        ha_formatted = format_area(2.5, AreaUnit.HECTARE, precision=1)
        assert "2.5 ha" in ha_formatted
        
        # Acres
        acre_formatted = format_area(5.25, AreaUnit.ACRE, precision=2)
        assert "5.25 acres" in acre_formatted
    
    def test_format_length_basic(self):
        """Test basic length formatting."""
        from utils.units import format_length
        formatted = format_length(25.5, LengthUnit.METER, precision=1)
        assert formatted == "25.5 m"
    
    def test_format_length_different_units(self):
        """Test formatting different length units."""
        from utils.units import format_length
        
        # Feet
        ft_formatted = format_length(100.25, LengthUnit.FOOT, precision=1)
        assert "100.3 ft" in ft_formatted
        
        # Kilometers
        km_formatted = format_length(5.5, LengthUnit.KILOMETER, precision=1)
        assert "5.5 km" in km_formatted


class TestAreaParsing:
    """Test area string parsing."""
    
    def test_parse_area_string_valid(self):
        """Test parsing valid area strings."""
        # Square meters
        measurement = parse_area_string("1500 sqm")
        assert measurement is not None
        assert measurement.value == 1500
        assert measurement.unit == AreaUnit.SQM
        
        # Square feet with comma
        measurement = parse_area_string("16,000 sqft")
        assert measurement is not None
        assert measurement.value == 16000
        assert measurement.unit == AreaUnit.SQFT
        
        # Different formats
        measurement = parse_area_string("2.5 hectare")
        assert measurement is not None
        assert measurement.value == 2.5
        assert measurement.unit == AreaUnit.HECTARE
    
    def test_parse_area_string_invalid(self):
        """Test parsing invalid area strings."""
        # Invalid format
        assert parse_area_string("invalid format") is None
        
        # Missing unit
        assert parse_area_string("1500") is None
        
        # Unknown unit
        assert parse_area_string("1500 unknown") is None
        
        # Invalid number
        assert parse_area_string("invalid sqm") is None


class TestAreaStandardization:
    """Test area standardization functions."""
    
    def test_standardize_area_units_same_unit(self):
        """Test standardization with same units."""
        measurements = {"area1": 1000, "area2": 2000, "area3": 1500}
        standardized = standardize_area_units(measurements, AreaUnit.SQM, AreaUnit.SQM)
        
        assert standardized == measurements  # Should be unchanged
    
    def test_standardize_area_units_conversion(self):
        """Test standardization with unit conversion."""
        measurements = {"area1": 10764, "area2": 21528}  # sqft values
        standardized = standardize_area_units(measurements, AreaUnit.SQFT, AreaUnit.SQM)
        
        # 10764 sqft ≈ 1000 sqm, 21528 sqft ≈ 2000 sqm
        assert abs(standardized["area1"] - 1000) < 1
        assert abs(standardized["area2"] - 2000) < 1
    
    def test_calculate_price_per_unit(self):
        """Test price per unit calculation."""
        prices = calculate_price_per_unit(
            total_price=1000000,  # $1M
            area=250,             # 250 sqm
            area_unit=AreaUnit.SQM
        )
        
        assert prices["price_per_sqm"] == 4000  # $4000/sqm
        assert abs(prices["price_per_sqft"] - 371.61) < 0.1  # ≈$371.61/sqft
    
    def test_calculate_price_per_unit_zero_area(self):
        """Test price per unit with zero area."""
        prices = calculate_price_per_unit(
            total_price=1000000,
            area=0,
            area_unit=AreaUnit.SQM
        )
        
        assert prices == {}  # Should return empty dict


class TestCommonRealEstateConversions:
    """Test common real estate conversion function."""
    
    def test_common_real_estate_conversions(self):
        """Test common real estate unit conversions."""
        conversions = common_real_estate_conversions(1000)  # 1000 sqm
        
        assert "1,000 m²" in conversions["sqm"]
        assert "10,764 ft²" in conversions["sqft"] 
        assert "0.25 acres" in conversions["acres"]  # ≈0.25 acres
        assert "0.10 ha" in conversions["hectares"]  # 0.1 hectares
        assert "1.0 dunum" in conversions["dunum"]   # 1 dunum