"""
Structured logging utilities for TerraFlow.
Provides consistent logging across the application.
"""

import logging
import sys
from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime


class TerraFlowFormatter(logging.Formatter):
    """Custom formatter for TerraFlow logging."""
    
    def __init__(self, include_timestamp: bool = True, include_module: bool = True):
        self.include_timestamp = include_timestamp
        self.include_module = include_module
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured information."""
        # Base message
        message = record.getMessage()
        
        # Build structured log entry
        log_entry = {
            "level": record.levelname,
            "message": message,
        }
        
        if self.include_timestamp:
            log_entry["timestamp"] = datetime.fromtimestamp(record.created).isoformat()
        
        if self.include_module:
            log_entry["module"] = record.module
            log_entry["function"] = record.funcName
            log_entry["line"] = record.lineno
        
        # Add extra context if provided
        if hasattr(record, 'deal_id'):
            log_entry["deal_id"] = record.deal_id
        if hasattr(record, 'country_code'):
            log_entry["country_code"] = record.country_code
        if hasattr(record, 'execution_time'):
            log_entry["execution_time_ms"] = record.execution_time
        
        # Format as JSON for structured logging
        return json.dumps(log_entry)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    structured: bool = True,
    console: bool = True
) -> logging.Logger:
    """
    Setup TerraFlow logging configuration.
    
    Args:
        level: Logging level ("DEBUG", "INFO", "WARNING", "ERROR")
        log_file: Path to log file (optional)
        structured: Use structured JSON logging
        console: Enable console logging
        
    Returns:
        Configured logger instance
    """
    # Get root logger for TerraFlow
    logger = logging.getLogger("terraflow")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Setup formatters
    if structured:
        formatter = TerraFlowFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "terraflow") -> logging.Logger:
    """Get logger instance for module."""
    return logging.getLogger(name)


class LoggingContext:
    """Context manager for adding structured logging context."""
    
    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context
        self.original_filters = []
    
    def __enter__(self):
        """Add context filter to logger."""
        def add_context(record):
            for key, value in self.context.items():
                setattr(record, key, value)
            return True
        
        self.logger.addFilter(add_context)
        self.original_filters.append(add_context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Remove context filter from logger."""
        for filter_func in self.original_filters:
            self.logger.removeFilter(filter_func)
        self.original_filters.clear()


def log_deal_calculation(
    logger: logging.Logger,
    deal_id: str,
    inputs: Dict[str, Any],
    outputs: Dict[str, Any],
    execution_time_ms: float,
    country_code: str = "Unknown"
):
    """
    Log deal calculation with structured data.
    
    Args:
        logger: Logger instance
        deal_id: Unique deal identifier
        inputs: Deal input parameters
        outputs: Calculated outputs
        execution_time_ms: Calculation time in milliseconds
        country_code: Country code for deal
    """
    with LoggingContext(
        logger,
        deal_id=deal_id,
        country_code=country_code,
        execution_time=execution_time_ms
    ):
        logger.info(
            f"Deal calculation completed: {deal_id}, "
            f"Residual: {outputs.get('residual_land_value', 0):,.0f}, "
            f"Viability: {outputs.get('overall_status', 'Unknown')}"
        )


def log_validation_issues(
    logger: logging.Logger,
    deal_id: str,
    validation_report,
    country_code: str = "Unknown"
):
    """
    Log validation issues for a deal.
    
    Args:
        logger: Logger instance  
        deal_id: Unique deal identifier
        validation_report: ValidationReport instance
        country_code: Country code for deal
    """
    with LoggingContext(
        logger,
        deal_id=deal_id,
        country_code=country_code
    ):
        summary = validation_report.summary()
        
        if validation_report.errors:
            logger.warning(
                f"Deal validation found {len(validation_report.errors)} errors: {deal_id}"
            )
            for error in validation_report.errors:
                logger.error(f"Validation error: {error.message} (Code: {error.code})")
        
        if validation_report.warnings:
            logger.info(
                f"Deal validation found {len(validation_report.warnings)} warnings: {deal_id}"
            )
            for warning in validation_report.warnings:
                logger.warning(f"Validation warning: {warning.message} (Code: {warning.code})")
        
        if validation_report.is_valid:
            logger.info(f"Deal validation passed: {deal_id}")


def log_market_data_usage(
    logger: logging.Logger,
    location_key: str,
    country_code: str,
    data_freshness_days: int,
    confidence_score: float
):
    """
    Log market data usage and quality metrics.
    
    Args:
        logger: Logger instance
        location_key: Market location identifier
        country_code: Country code
        data_freshness_days: Age of market data in days
        confidence_score: Data confidence (0-1)
    """
    with LoggingContext(
        logger,
        country_code=country_code,
        location_key=location_key
    ):
        if data_freshness_days > 90:
            logger.warning(
                f"Market data is {data_freshness_days} days old for {location_key}"
            )
        
        if confidence_score < 0.7:
            logger.warning(
                f"Low confidence market data ({confidence_score:.1%}) for {location_key}"
            )
        
        logger.info(
            f"Using market data: {location_key}, "
            f"Age: {data_freshness_days} days, "
            f"Confidence: {confidence_score:.1%}"
        )


def log_performance_metric(
    logger: logging.Logger,
    operation: str,
    execution_time_ms: float,
    success: bool = True,
    **context
):
    """
    Log performance metrics for operations.
    
    Args:
        logger: Logger instance
        operation: Operation name
        execution_time_ms: Execution time in milliseconds
        success: Whether operation succeeded
        **context: Additional context data
    """
    with LoggingContext(logger, execution_time=execution_time_ms, **context):
        status = "completed" if success else "failed"
        logger.info(f"Performance: {operation} {status} in {execution_time_ms:.2f}ms")
        
        # Log warning for slow operations
        if execution_time_ms > 1000:  # > 1 second
            logger.warning(f"Slow operation detected: {operation} took {execution_time_ms:.2f}ms")


# Module-level logger setup
_terraflow_logger = None


def init_terraflow_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    structured: bool = True
) -> logging.Logger:
    """
    Initialize TerraFlow logging system.
    
    Args:
        level: Logging level
        log_file: Path to log file
        structured: Use structured logging
        
    Returns:
        Configured logger
    """
    global _terraflow_logger
    
    log_path = Path(log_file) if log_file else None
    _terraflow_logger = setup_logging(
        level=level,
        log_file=log_path,
        structured=structured
    )
    
    _terraflow_logger.info("TerraFlow logging system initialized")
    return _terraflow_logger


def get_terraflow_logger() -> logging.Logger:
    """Get the global TerraFlow logger."""
    global _terraflow_logger
    if _terraflow_logger is None:
        _terraflow_logger = init_terraflow_logging()
    return _terraflow_logger