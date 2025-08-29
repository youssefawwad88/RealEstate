"""
Market data lookup adapter with configuration-driven data sources.
Refactored from original market_lookup.py to use configuration system.
"""

from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
from pathlib import Path
import json
from dataclasses import dataclass

from ..policies.registry import RuleSet, get_ruleset


@dataclass
class MarketBenchmarks:
    """Market benchmark data container."""
    
    location_key: str
    land_comps_psm: Dict[str, float]
    sale_prices: Dict[str, float]
    construction_costs: Dict[str, float]
    market_indicators: Dict[str, Any]
    data_freshness_days: int = 0
    confidence_score: float = 1.0


class MarketDataAdapter:
    """
    Market data adapter that uses configuration-driven data sources.
    Replaces hardcoded market data with configurable lookup system.
    """
    
    def __init__(self, ruleset: RuleSet):
        self.ruleset = ruleset
        self.market_config = ruleset.market_config
        
    def load_market_benchmarks(self, location_key: str) -> Optional[MarketBenchmarks]:
        """
        Load market benchmarks for a specific location.
        
        Args:
            location_key: Geographic location identifier
            
        Returns:
            MarketBenchmarks if data available, None otherwise
        """
        # Check if location is configured
        if location_key not in self.market_config.locations:
            return None
            
        location_info = self.market_config.locations[location_key]
        
        # Try to load from custom data file first
        custom_data = self._load_custom_market_data(location_key)
        if custom_data:
            return custom_data
            
        # Fall back to configured fallback values
        return self._get_fallback_benchmarks(location_key)
    
    def _load_custom_market_data(self, location_key: str) -> Optional[MarketBenchmarks]:
        """Load market data from custom JSON files."""
        try:
            # Construct file path based on country and location
            data_dir = Path(__file__).parent.parent.parent / "data" / "market" / self.ruleset.country_code
            file_path = data_dir / f"{location_key}_market.json"
            
            if file_path.exists():
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    
                return MarketBenchmarks(
                    location_key=location_key,
                    land_comps_psm=data.get("land_comps_psm", {}),
                    sale_prices=data.get("sale_prices", {}),
                    construction_costs=data.get("construction_costs", {}),
                    market_indicators=data.get("market_indicators", {}),
                    data_freshness_days=data.get("data_freshness_days", 0),
                    confidence_score=data.get("confidence_score", 1.0)
                )
                
        except Exception:
            # Silently fail and fall back to defaults
            pass
            
        return None
    
    def _get_fallback_benchmarks(self, location_key: str) -> MarketBenchmarks:
        """Get fallback benchmark values from configuration."""
        fallback_values = self.market_config.fallback_values
        location_info = self.market_config.locations.get(location_key, {})
        
        # Extract configured data keys
        land_keys = self.market_config.data_keys.get("land_comps", [])
        sale_keys = self.market_config.data_keys.get("sale_prices", [])
        cost_keys = self.market_config.data_keys.get("construction_costs", [])
        indicator_keys = self.market_config.data_keys.get("market_indicators", [])
        
        # Build benchmark data from fallback values
        land_comps = {}
        for key in land_keys:
            fallback_key = key.replace("_jod_", "_").replace("_aed_", "_")  # Normalize currency
            if fallback_key in fallback_values or key in fallback_values:
                land_comps[key] = fallback_values.get(key, fallback_values.get(fallback_key, 0))
        
        sale_prices = {}
        for key in sale_keys:
            fallback_key = key.replace("_jod_", "_").replace("_aed_", "_")
            if fallback_key in fallback_values or key in fallback_values:
                sale_prices[key] = fallback_values.get(key, fallback_values.get(fallback_key, 0))
        
        construction_costs = {}
        for key in cost_keys:
            fallback_key = key.replace("_jod", "").replace("_aed", "")
            if fallback_key in fallback_values or key in fallback_values:
                construction_costs[key] = fallback_values.get(key, fallback_values.get(fallback_key, 0))
        
        market_indicators = {}
        for key in indicator_keys:
            if key in fallback_values:
                market_indicators[key] = fallback_values[key]
        
        # Add location-specific metadata
        market_indicators.update({
            "demand_score": location_info.get("demand_score", 3),
            "liquidity_score": location_info.get("liquidity_score", 3),
            "tier": location_info.get("tier", 2)
        })
        
        return MarketBenchmarks(
            location_key=location_key,
            land_comps_psm=land_comps,
            sale_prices=sale_prices,
            construction_costs=construction_costs,
            market_indicators=market_indicators,
            data_freshness_days=90,  # Assume 90 days for fallback data
            confidence_score=0.7     # Lower confidence for fallback data
        )
    
    def validate_inputs_against_market(
        self,
        inputs_dict: Dict[str, Any],
        location_key: str = "default"
    ) -> Dict[str, str]:
        """
        Validate user inputs against market benchmarks.
        
        Args:
            inputs_dict: Dictionary of user inputs
            location_key: Location for market comparison
            
        Returns:
            Dictionary of validation warnings
        """
        benchmarks = self.load_market_benchmarks(location_key)
        if not benchmarks:
            return {"market_data": "Market data not available for validation"}
            
        warnings = {}
        validation_config = self.market_config.validation
        
        # Validate sale price assumptions
        if "expected_sale_price_psm" in inputs_dict:
            sale_price = inputs_dict["expected_sale_price_psm"]
            warnings.update(self._validate_sale_price(sale_price, benchmarks, validation_config))
        
        # Validate construction cost assumptions  
        if "construction_cost_psm" in inputs_dict:
            construction_cost = inputs_dict["construction_cost_psm"]
            warnings.update(self._validate_construction_cost(construction_cost, benchmarks, validation_config))
        
        # Validate soft cost percentage
        if "soft_cost_pct" in inputs_dict:
            soft_cost_pct = inputs_dict["soft_cost_pct"]
            warnings.update(self._validate_soft_costs(soft_cost_pct, benchmarks))
        
        return warnings
    
    def _validate_sale_price(
        self,
        sale_price: float,
        benchmarks: MarketBenchmarks,
        validation_config: Dict[str, float]
    ) -> Dict[str, str]:
        """Validate sale price against market range."""
        warnings = {}
        
        # Find relevant price keys (handle currency variations)
        price_keys = [k for k in benchmarks.sale_prices.keys() if "avg" in k and "sqm" in k]
        if not price_keys:
            return warnings
            
        market_avg = benchmarks.sale_prices[price_keys[0]]
        variance_threshold = validation_config.get("sale_price_variance_threshold", 0.30)
        
        # Check for significant variance
        if abs(sale_price - market_avg) / market_avg > variance_threshold:
            direction = "above" if sale_price > market_avg else "below"
            warnings["sale_price"] = (
                f"Sale price {sale_price:,.0f} is significantly {direction} "
                f"market average {market_avg:,.0f} ({self.ruleset.country_rules.currency})"
            )
        
        return warnings
    
    def _validate_construction_cost(
        self,
        construction_cost: float,
        benchmarks: MarketBenchmarks,
        validation_config: Dict[str, float]
    ) -> Dict[str, str]:
        """Validate construction cost against market range."""
        warnings = {}
        
        # Find relevant cost keys
        cost_keys = [k for k in benchmarks.construction_costs.keys() if "avg" in k]
        if not cost_keys:
            return warnings
            
        market_avg = benchmarks.construction_costs[cost_keys[0]]
        variance_threshold = validation_config.get("construction_cost_variance_threshold", 0.25)
        
        if abs(construction_cost - market_avg) / market_avg > variance_threshold:
            direction = "above" if construction_cost > market_avg else "below"
            warnings["construction_cost"] = (
                f"Construction cost {construction_cost:,.0f} is significantly {direction} "
                f"market average {market_avg:,.0f} ({self.ruleset.country_rules.currency})"
            )
        
        return warnings
    
    def _validate_soft_costs(
        self,
        soft_cost_pct: float,
        benchmarks: MarketBenchmarks
    ) -> Dict[str, str]:
        """Validate soft cost percentage."""
        warnings = {}
        
        typical_soft_cost = benchmarks.construction_costs.get("soft_cost_pct_typical")
        if typical_soft_cost and abs(soft_cost_pct - typical_soft_cost) > 0.05:  # 5% threshold
            warnings["soft_cost"] = (
                f"Soft cost {soft_cost_pct:.1%} differs from typical {typical_soft_cost:.1%}"
            )
        
        return warnings
    
    def get_market_summary(self, location_key: str = "default") -> Dict[str, Any]:
        """
        Get formatted market summary for display.
        
        Args:
            location_key: Location identifier
            
        Returns:
            Dictionary with formatted market data
        """
        benchmarks = self.load_market_benchmarks(location_key)
        if not benchmarks:
            return {"error": f"Market data not available for {location_key}"}
        
        # Extract summary metrics (handle different currency formats)
        land_comps = benchmarks.land_comps_psm
        sale_prices = benchmarks.sale_prices
        construction_costs = benchmarks.construction_costs
        indicators = benchmarks.market_indicators
        
        # Find min/max values
        land_min = next((v for k, v in land_comps.items() if "min" in k), 0)
        land_max = next((v for k, v in land_comps.items() if "max" in k), 0)
        sale_min = next((v for k, v in sale_prices.items() if "min" in k), 0)
        sale_max = next((v for k, v in sale_prices.items() if "max" in k), 0)
        cost_avg = next((v for k, v in construction_costs.items() if "avg" in k), 0)
        
        return {
            "location": location_key.replace("_", " ").title(),
            "country": self.ruleset.country_rules.name,
            "currency": self.ruleset.country_rules.currency,
            "land_price_range": f"{land_min:,.0f} - {land_max:,.0f}",
            "sale_price_range": f"{sale_min:,.0f} - {sale_max:,.0f}",
            "construction_cost_avg": f"{cost_avg:,.0f}",
            "absorption_rate": f"{indicators.get('absorption_rate_units_month', 0):.1f} units/month",
            "typical_land_gdv": f"{indicators.get('land_gdv_benchmark_pct', 20):.0f}%",
            "market_tier": indicators.get("tier", "Unknown"),
            "demand_strength": self._score_to_text(indicators.get("demand_score", 3)),
            "data_confidence": f"{benchmarks.confidence_score:.0%}",
            "data_freshness": f"{benchmarks.data_freshness_days} days"
        }
    
    def get_available_locations(self) -> List[str]:
        """Get list of available location keys."""
        return list(self.market_config.locations.keys())
    
    def _score_to_text(self, score: int) -> str:
        """Convert numeric score to descriptive text."""
        if score >= 4:
            return "Strong"
        elif score >= 3:
            return "Moderate"  
        else:
            return "Weak"


def get_market_adapter(country_code: str) -> MarketDataAdapter:
    """
    Get market data adapter for a specific country.
    
    Args:
        country_code: Two-letter country code
        
    Returns:
        MarketDataAdapter instance
    """
    ruleset = get_ruleset(country_code)
    return MarketDataAdapter(ruleset)


def validate_inputs_against_market(
    inputs_dict: Dict[str, Any],
    country_code: str = "UAE",
    location_key: str = "default"
) -> Dict[str, str]:
    """
    Convenience function to validate inputs against market.
    Maintains compatibility with original API.
    
    Args:
        inputs_dict: Dictionary of user inputs
        country_code: Country code for market rules
        location_key: Location for market comparison
        
    Returns:
        Dictionary of validation warnings
    """
    adapter = get_market_adapter(country_code)
    return adapter.validate_inputs_against_market(inputs_dict, location_key)


def get_market_summary(
    country_code: str = "UAE",
    location_key: str = "default"
) -> Dict[str, Any]:
    """
    Convenience function to get market summary.
    Maintains compatibility with original API.
    """
    adapter = get_market_adapter(country_code)
    return adapter.get_market_summary(location_key)