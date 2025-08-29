"""
Custom exceptions for TerraFlow system.
Provides specific error types for different failure scenarios.
"""

from typing import Optional, Dict, Any, List


class TerraFlowError(Exception):
    """Base exception for TerraFlow errors."""
    
    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
    
    def __str__(self) -> str:
        """String representation of error."""
        base_msg = self.message
        if self.error_code:
            base_msg = f"[{self.error_code}] {base_msg}"
        
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            base_msg += f" (Context: {context_str})"
        
        return base_msg


class ConfigurationError(TerraFlowError):
    """Raised when configuration is invalid or missing."""
    
    def __init__(
        self,
        message: str,
        country_code: Optional[str] = None,
        config_file: Optional[str] = None
    ):
        context = {}
        if country_code:
            context["country_code"] = country_code
        if config_file:
            context["config_file"] = config_file
            
        super().__init__(message, "CONFIG_ERROR", context)


class ValidationError(TerraFlowError):
    """Raised when input validation fails."""
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        validation_code: Optional[str] = None
    ):
        context = {}
        if field:
            context["field"] = field
        if value is not None:
            context["value"] = str(value)
            
        error_code = validation_code or "VALIDATION_ERROR"
        super().__init__(message, error_code, context)


class ZoningComplianceError(ValidationError):
    """Raised when development parameters violate zoning rules."""
    
    def __init__(
        self,
        message: str,
        zoning_code: str,
        parameter: str,
        provided_value: Any,
        max_allowed: Any
    ):
        context = {
            "zoning_code": zoning_code,
            "parameter": parameter,
            "provided_value": str(provided_value),
            "max_allowed": str(max_allowed)
        }
        super().__init__(message, parameter, provided_value, "ZONING_COMPLIANCE_ERROR")
        self.context.update(context)


class CalculationError(TerraFlowError):
    """Raised when financial calculations fail or produce invalid results."""
    
    def __init__(
        self,
        message: str,
        calculation_type: Optional[str] = None,
        input_values: Optional[Dict[str, Any]] = None
    ):
        context = {}
        if calculation_type:
            context["calculation_type"] = calculation_type
        if input_values:
            context["input_values"] = str(input_values)
            
        super().__init__(message, "CALCULATION_ERROR", context)


class MarketDataError(TerraFlowError):
    """Raised when market data is unavailable or invalid."""
    
    def __init__(
        self,
        message: str,
        location_key: Optional[str] = None,
        country_code: Optional[str] = None,
        data_source: Optional[str] = None
    ):
        context = {}
        if location_key:
            context["location_key"] = location_key
        if country_code:
            context["country_code"] = country_code
        if data_source:
            context["data_source"] = data_source
            
        super().__init__(message, "MARKET_DATA_ERROR", context)


class CurrencyConversionError(TerraFlowError):
    """Raised when currency conversion fails."""
    
    def __init__(
        self,
        message: str,
        from_currency: Optional[str] = None,
        to_currency: Optional[str] = None,
        amount: Optional[float] = None
    ):
        context = {}
        if from_currency:
            context["from_currency"] = from_currency
        if to_currency:
            context["to_currency"] = to_currency
        if amount is not None:
            context["amount"] = amount
            
        super().__init__(message, "CURRENCY_CONVERSION_ERROR", context)


class GeospatialError(TerraFlowError):
    """Raised when geospatial operations fail."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        coordinates: Optional[str] = None,
        address: Optional[str] = None
    ):
        context = {}
        if operation:
            context["operation"] = operation
        if coordinates:
            context["coordinates"] = coordinates
        if address:
            context["address"] = address
            
        super().__init__(message, "GEOSPATIAL_ERROR", context)


class DataProcessingError(TerraFlowError):
    """Raised when data processing operations fail."""
    
    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        record_count: Optional[int] = None,
        failed_records: Optional[List[str]] = None
    ):
        context = {}
        if operation:
            context["operation"] = operation
        if record_count is not None:
            context["record_count"] = record_count
        if failed_records:
            context["failed_records"] = str(failed_records)
            
        super().__init__(message, "DATA_PROCESSING_ERROR", context)


class FileOperationError(TerraFlowError):
    """Raised when file operations fail."""
    
    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        operation: Optional[str] = None
    ):
        context = {}
        if file_path:
            context["file_path"] = file_path
        if operation:
            context["operation"] = operation
            
        super().__init__(message, "FILE_OPERATION_ERROR", context)


class APIError(TerraFlowError):
    """Raised when external API calls fail."""
    
    def __init__(
        self,
        message: str,
        api_endpoint: Optional[str] = None,
        status_code: Optional[int] = None,
        response_data: Optional[str] = None
    ):
        context = {}
        if api_endpoint:
            context["api_endpoint"] = api_endpoint
        if status_code is not None:
            context["status_code"] = status_code
        if response_data:
            context["response_data"] = response_data
            
        super().__init__(message, "API_ERROR", context)


def handle_calculation_errors(func):
    """
    Decorator to handle calculation errors and provide better error messages.
    
    Usage:
        @handle_calculation_errors
        def my_calculation_function():
            # calculation code
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ZeroDivisionError as e:
            raise CalculationError(
                f"Division by zero in {func.__name__}: {str(e)}",
                calculation_type=func.__name__,
                input_values={"args": str(args), "kwargs": str(kwargs)}
            )
        except ValueError as e:
            raise CalculationError(
                f"Invalid value in {func.__name__}: {str(e)}",
                calculation_type=func.__name__,
                input_values={"args": str(args), "kwargs": str(kwargs)}
            )
        except Exception as e:
            if isinstance(e, TerraFlowError):
                raise  # Re-raise TerraFlow errors as-is
            
            raise CalculationError(
                f"Unexpected error in {func.__name__}: {str(e)}",
                calculation_type=func.__name__,
                input_values={"args": str(args), "kwargs": str(kwargs)}
            )
    
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def handle_validation_errors(func):
    """
    Decorator to handle validation errors with better context.
    
    Usage:
        @handle_validation_errors
        def my_validation_function():
            # validation code
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            # Convert ValueError to ValidationError
            raise ValidationError(
                f"Validation failed in {func.__name__}: {str(e)}"
            )
        except Exception as e:
            if isinstance(e, TerraFlowError):
                raise  # Re-raise TerraFlow errors as-is
                
            raise ValidationError(
                f"Unexpected validation error in {func.__name__}: {str(e)}"
            )
    
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def create_error_summary(errors: List[Exception]) -> Dict[str, Any]:
    """
    Create error summary from list of exceptions.
    
    Args:
        errors: List of exceptions
        
    Returns:
        Dictionary with error summary
    """
    if not errors:
        return {"total_errors": 0, "error_types": {}, "messages": []}
    
    error_types = {}
    messages = []
    
    for error in errors:
        error_type = type(error).__name__
        error_types[error_type] = error_types.get(error_type, 0) + 1
        
        if isinstance(error, TerraFlowError):
            messages.append({
                "type": error_type,
                "code": error.error_code,
                "message": error.message,
                "context": error.context
            })
        else:
            messages.append({
                "type": error_type,
                "message": str(error)
            })
    
    return {
        "total_errors": len(errors),
        "error_types": error_types,
        "messages": messages
    }


def format_validation_errors(validation_issues: List) -> str:
    """
    Format validation issues into readable error message.
    
    Args:
        validation_issues: List of ValidationIssue objects
        
    Returns:
        Formatted error message string
    """
    if not validation_issues:
        return "No validation errors"
    
    error_lines = []
    for issue in validation_issues:
        line = f"- {issue.message}"
        if hasattr(issue, 'field') and issue.field:
            line += f" (Field: {issue.field})"
        if hasattr(issue, 'suggestion') and issue.suggestion:
            line += f" | Suggestion: {issue.suggestion}"
        error_lines.append(line)
    
    return "\n".join(error_lines)