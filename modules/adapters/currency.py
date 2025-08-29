"""
Currency exchange rate provider interface.
Stub implementation for future integration with live FX feeds.
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from abc import ABC, abstractmethod


@dataclass
class ExchangeRate:
    """Exchange rate data point."""
    
    base_currency: str
    target_currency: str
    rate: float
    timestamp: datetime
    provider: str
    
    @property
    def age_hours(self) -> float:
        """Get age of exchange rate in hours."""
        return (datetime.now() - self.timestamp).total_seconds() / 3600
    
    @property
    def is_stale(self, max_age_hours: float = 24.0) -> bool:
        """Check if exchange rate is stale."""
        return self.age_hours > max_age_hours


class CurrencyProvider(ABC):
    """Abstract base class for currency exchange rate providers."""
    
    @abstractmethod
    def get_exchange_rate(
        self,
        base_currency: str,
        target_currency: str
    ) -> Optional[ExchangeRate]:
        """Get current exchange rate between two currencies."""
        pass
    
    @abstractmethod
    def get_multiple_rates(
        self,
        base_currency: str,
        target_currencies: list[str]
    ) -> Dict[str, ExchangeRate]:
        """Get exchange rates for multiple target currencies."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available and responsive."""
        pass


class StaticCurrencyProvider(CurrencyProvider):
    """
    Static currency provider with hardcoded rates.
    Suitable for development and testing environments.
    """
    
    # Static rates vs USD (updated 2024)
    STATIC_RATES = {
        "USD": 1.0,
        "JOD": 0.708,   # Jordanian Dinar (pegged to USD)
        "AED": 3.673,   # UAE Dirham (pegged to USD)
        "EUR": 0.85,    # Euro (approximate)
        "GBP": 0.73,    # British Pound (approximate)
        "SAR": 3.75,    # Saudi Riyal (pegged to USD)
        "QAR": 3.64,    # Qatari Riyal (pegged to USD)
        "KWD": 0.31,    # Kuwaiti Dinar
        "BHD": 0.377,   # Bahraini Dinar (pegged to USD)
        "OMR": 0.385,   # Omani Rial (pegged to USD)
    }
    
    def __init__(self):
        self.provider_name = "StaticCurrencyProvider"
        self.last_update = datetime.now()
    
    def get_exchange_rate(
        self,
        base_currency: str,
        target_currency: str
    ) -> Optional[ExchangeRate]:
        """Get static exchange rate between two currencies."""
        base_currency = base_currency.upper()
        target_currency = target_currency.upper()
        
        if base_currency == target_currency:
            return ExchangeRate(
                base_currency=base_currency,
                target_currency=target_currency,
                rate=1.0,
                timestamp=self.last_update,
                provider=self.provider_name
            )
        
        base_to_usd = self.STATIC_RATES.get(base_currency)
        target_to_usd = self.STATIC_RATES.get(target_currency)
        
        if base_to_usd is None or target_to_usd is None:
            return None
        
        # Convert via USD: base -> USD -> target
        rate = target_to_usd / base_to_usd
        
        return ExchangeRate(
            base_currency=base_currency,
            target_currency=target_currency,
            rate=rate,
            timestamp=self.last_update,
            provider=self.provider_name
        )
    
    def get_multiple_rates(
        self,
        base_currency: str,
        target_currencies: list[str]
    ) -> Dict[str, ExchangeRate]:
        """Get exchange rates for multiple target currencies."""
        rates = {}
        
        for target_currency in target_currencies:
            rate = self.get_exchange_rate(base_currency, target_currency)
            if rate:
                rates[target_currency] = rate
        
        return rates
    
    def is_available(self) -> bool:
        """Static provider is always available."""
        return True
    
    def get_supported_currencies(self) -> list[str]:
        """Get list of supported currency codes."""
        return list(self.STATIC_RATES.keys())


class LiveCurrencyProvider(CurrencyProvider):
    """
    Live currency provider interface.
    Placeholder for future integration with actual FX APIs.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.provider_name = "LiveCurrencyProvider"
        self.base_url = "https://api.exchangerate-api.com"  # Example
        
    def get_exchange_rate(
        self,
        base_currency: str,
        target_currency: str
    ) -> Optional[ExchangeRate]:
        """Get live exchange rate - stub implementation."""
        # TODO: Implement actual API call
        # For now, fall back to static rates
        static_provider = StaticCurrencyProvider()
        return static_provider.get_exchange_rate(base_currency, target_currency)
    
    def get_multiple_rates(
        self,
        base_currency: str,
        target_currencies: list[str]
    ) -> Dict[str, ExchangeRate]:
        """Get multiple live exchange rates - stub implementation."""
        # TODO: Implement batch API call
        static_provider = StaticCurrencyProvider()
        return static_provider.get_multiple_rates(base_currency, target_currencies)
    
    def is_available(self) -> bool:
        """Check if live provider is available - stub implementation."""
        # TODO: Implement actual availability check
        return False  # Not implemented yet


class CurrencyService:
    """
    Currency service that manages providers and caching.
    Provides unified interface for currency operations.
    """
    
    def __init__(self, live_provider: bool = False, api_key: Optional[str] = None):
        """
        Initialize currency service.
        
        Args:
            live_provider: Whether to use live provider (falls back to static)
            api_key: API key for live provider
        """
        self.providers = []
        
        if live_provider:
            live = LiveCurrencyProvider(api_key)
            if live.is_available():
                self.providers.append(live)
        
        # Always include static provider as fallback
        self.providers.append(StaticCurrencyProvider())
        
        self.rate_cache: Dict[str, ExchangeRate] = {}
        self.cache_ttl_hours = 1.0  # Cache rates for 1 hour
    
    def get_exchange_rate(
        self,
        base_currency: str,
        target_currency: str,
        use_cache: bool = True
    ) -> Optional[ExchangeRate]:
        """
        Get exchange rate with provider fallback and caching.
        
        Args:
            base_currency: Base currency code
            target_currency: Target currency code
            use_cache: Whether to use cached rates
            
        Returns:
            ExchangeRate if available, None otherwise
        """
        cache_key = f"{base_currency}_{target_currency}"
        
        # Check cache first
        if use_cache and cache_key in self.rate_cache:
            cached_rate = self.rate_cache[cache_key]
            if not cached_rate.is_stale:
                return cached_rate
        
        # Try providers in order
        for provider in self.providers:
            try:
                rate = provider.get_exchange_rate(base_currency, target_currency)
                if rate:
                    # Cache the rate
                    if use_cache:
                        self.rate_cache[cache_key] = rate
                    return rate
            except Exception:
                # Continue to next provider
                continue
        
        return None
    
    def convert_amount(
        self,
        amount: float,
        base_currency: str,
        target_currency: str
    ) -> Optional[float]:
        """
        Convert amount between currencies.
        
        Args:
            amount: Amount in base currency
            base_currency: Base currency code
            target_currency: Target currency code
            
        Returns:
            Converted amount if exchange rate available, None otherwise
        """
        rate = self.get_exchange_rate(base_currency, target_currency)
        if rate:
            return amount * rate.rate
        return None
    
    def get_rates_vs_usd(self, currency_codes: list[str]) -> Dict[str, float]:
        """
        Get exchange rates vs USD for multiple currencies.
        
        Args:
            currency_codes: List of currency codes
            
        Returns:
            Dictionary mapping currency codes to USD exchange rates
        """
        rates = {}
        
        for currency_code in currency_codes:
            rate = self.get_exchange_rate("USD", currency_code)
            if rate:
                rates[currency_code] = rate.rate
        
        return rates
    
    def clear_cache(self):
        """Clear exchange rate cache."""
        self.rate_cache.clear()


# Global currency service instance
_currency_service = None


def get_currency_service(
    live_provider: bool = False,
    api_key: Optional[str] = None
) -> CurrencyService:
    """Get global currency service instance."""
    global _currency_service
    if _currency_service is None:
        _currency_service = CurrencyService(live_provider, api_key)
    return _currency_service


def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str
) -> Optional[float]:
    """
    Convenience function to convert currency amount.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency code
        to_currency: Target currency code
        
    Returns:
        Converted amount if successful, None otherwise
    """
    service = get_currency_service()
    return service.convert_amount(amount, from_currency, to_currency)


def get_exchange_rates_vs_usd() -> Dict[str, float]:
    """
    Get exchange rates for common currencies vs USD.
    
    Returns:
        Dictionary with currency codes and their USD exchange rates
    """
    service = get_currency_service()
    common_currencies = ["JOD", "AED", "EUR", "GBP", "SAR", "QAR"]
    return service.get_rates_vs_usd(common_currencies)