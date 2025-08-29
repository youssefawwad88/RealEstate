"""
Market data lookup module for TerraFlow.
Provides market benchmarks and comparable data by location.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
from pathlib import Path
import json


class MarketData:
    """Container for market benchmarks and comparable data."""

    def __init__(
        self,
        city_key: str,
        land_comps_psm: Dict[str, float],
        sale_prices: Dict[str, float],
        construction_costs: Dict[str, float],
        market_indicators: Dict[str, Any],
    ):
        self.city_key = city_key
        self.land_comps_psm = land_comps_psm
        self.sale_prices = sale_prices
        self.construction_costs = construction_costs
        self.market_indicators = market_indicators

    def get_benchmark(self, metric: str, default: Optional[float] = None) -> float:
        """Get a specific market benchmark value."""
        benchmarks = {**self.land_comps_psm, **self.sale_prices, **self.construction_costs, **self.market_indicators}
        return benchmarks.get(metric, default)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "city_key": self.city_key,
            "land_comps_psm": self.land_comps_psm,
            "sale_prices": self.sale_prices,
            "construction_costs": self.construction_costs,
            "market_indicators": self.market_indicators,
        }


# Default market data for major cities
DEFAULT_MARKET_DATA = {
    "toronto": MarketData(
        city_key="toronto",
        land_comps_psm={
            "land_comp_min": 300.0,
            "land_comp_avg": 500.0,
            "land_comp_max": 800.0,
            "land_per_buildable_avg": 400.0,
        },
        sale_prices={
            "sale_price_min": 3200.0,
            "sale_price_avg": 4000.0,
            "sale_price_max": 5500.0,
            "price_per_buildable": 3800.0,
        },
        construction_costs={
            "construction_cost_min": 1600.0,
            "construction_cost_avg": 2000.0,
            "construction_cost_max": 2800.0,
            "soft_cost_pct_typical": 0.15,
        },
        market_indicators={
            "absorption_rate": 4.2,  # units per month
            "land_gdv_benchmark": 22.0,  # typical land % of GDV
            "profit_margin_benchmark": 20.0,  # typical developer profit %
            "demand_score": 4,  # 1-5 scale
            "liquidity_score": 4,  # 1-5 scale
            "volatility_score": 3,  # 1-5 scale (higher = more volatile)
            "last_updated": "2024-01-15",
        },
    ),
    "vancouver": MarketData(
        city_key="vancouver",
        land_comps_psm={
            "land_comp_min": 400.0,
            "land_comp_avg": 650.0,
            "land_comp_max": 1200.0,
            "land_per_buildable_avg": 550.0,
        },
        sale_prices={
            "sale_price_min": 4000.0,
            "sale_price_avg": 5200.0,
            "sale_price_max": 7500.0,
            "price_per_buildable": 5000.0,
        },
        construction_costs={
            "construction_cost_min": 1800.0,
            "construction_cost_avg": 2200.0,
            "construction_cost_max": 3000.0,
            "soft_cost_pct_typical": 0.16,
        },
        market_indicators={
            "absorption_rate": 3.8,
            "land_gdv_benchmark": 24.0,
            "profit_margin_benchmark": 18.0,
            "demand_score": 5,
            "liquidity_score": 4,
            "volatility_score": 4,
            "last_updated": "2024-01-15",
        },
    ),
    "calgary": MarketData(
        city_key="calgary",
        land_comps_psm={
            "land_comp_min": 200.0,
            "land_comp_avg": 300.0,
            "land_comp_max": 500.0,
            "land_per_buildable_avg": 280.0,
        },
        sale_prices={
            "sale_price_min": 2800.0,
            "sale_price_avg": 3400.0,
            "sale_price_max": 4200.0,
            "price_per_buildable": 3200.0,
        },
        construction_costs={
            "construction_cost_min": 1400.0,
            "construction_cost_avg": 1700.0,
            "construction_cost_max": 2200.0,
            "soft_cost_pct_typical": 0.14,
        },
        market_indicators={
            "absorption_rate": 5.1,
            "land_gdv_benchmark": 20.0,
            "profit_margin_benchmark": 22.0,
            "demand_score": 3,
            "liquidity_score": 3,
            "volatility_score": 2,
            "last_updated": "2024-01-15",
        },
    ),
    "montreal": MarketData(
        city_key="montreal",
        land_comps_psm={
            "land_comp_min": 250.0,
            "land_comp_avg": 380.0,
            "land_comp_max": 600.0,
            "land_per_buildable_avg": 320.0,
        },
        sale_prices={
            "sale_price_min": 2600.0,
            "sale_price_avg": 3200.0,
            "sale_price_max": 4200.0,
            "price_per_buildable": 3000.0,
        },
        construction_costs={
            "construction_cost_min": 1500.0,
            "construction_cost_avg": 1800.0,
            "construction_cost_max": 2300.0,
            "soft_cost_pct_typical": 0.13,
        },
        market_indicators={
            "absorption_rate": 4.5,
            "land_gdv_benchmark": 21.0,
            "profit_margin_benchmark": 19.0,
            "demand_score": 4,
            "liquidity_score": 4,
            "volatility_score": 2,
            "last_updated": "2024-01-15",
        },
    ),
    "default": MarketData(
        city_key="default",
        land_comps_psm={
            "land_comp_min": 250.0,
            "land_comp_avg": 400.0,
            "land_comp_max": 650.0,
            "land_per_buildable_avg": 350.0,
        },
        sale_prices={
            "sale_price_min": 3000.0,
            "sale_price_avg": 3800.0,
            "sale_price_max": 5000.0,
            "price_per_buildable": 3600.0,
        },
        construction_costs={
            "construction_cost_min": 1600.0,
            "construction_cost_avg": 1900.0,
            "construction_cost_max": 2500.0,
            "soft_cost_pct_typical": 0.15,
        },
        market_indicators={
            "absorption_rate": 4.0,
            "land_gdv_benchmark": 22.0,
            "profit_margin_benchmark": 20.0,
            "demand_score": 3,
            "liquidity_score": 3,
            "volatility_score": 3,
            "last_updated": "2024-01-15",
        },
    ),
}


def load_market_data(city_key: str) -> MarketData:
    """
    Load market data for a specific city.

    Args:
        city_key: City identifier (e.g., 'toronto', 'vancouver')

    Returns:
        MarketData instance with benchmarks and comparables
    """
    city_key = city_key.lower().strip()

    # Try to load from custom data file first
    custom_data = _load_custom_market_data(city_key)
    if custom_data:
        return custom_data

    # Fall back to default data
    if city_key in DEFAULT_MARKET_DATA:
        return DEFAULT_MARKET_DATA[city_key]
    else:
        # Return default market data if city not found
        return DEFAULT_MARKET_DATA["default"]


def _load_custom_market_data(city_key: str) -> Optional[MarketData]:
    """
    Load market data from custom JSON files.

    Args:
        city_key: City identifier

    Returns:
        MarketData instance if file exists, None otherwise
    """
    try:
        data_dir = Path(__file__).parent.parent / "data" / "market"
        file_path = data_dir / f"{city_key}_market.json"

        if file_path.exists():
            with open(file_path, "r") as f:
                data = json.load(f)

            return MarketData(
                city_key=data["city_key"],
                land_comps_psm=data["land_comps_psm"],
                sale_prices=data["sale_prices"],
                construction_costs=data["construction_costs"],
                market_indicators=data["market_indicators"],
            )

    except Exception:
        # Silently fail and return None to fall back to defaults
        pass

    return None


def save_market_data(market_data: MarketData) -> bool:
    """
    Save market data to JSON file.

    Args:
        market_data: MarketData instance to save

    Returns:
        True if successful, False otherwise
    """
    try:
        data_dir = Path(__file__).parent.parent / "data" / "market"
        data_dir.mkdir(parents=True, exist_ok=True)

        file_path = data_dir / f"{market_data.city_key}_market.json"

        with open(file_path, "w") as f:
            json.dump(market_data.to_dict(), f, indent=2)

        return True

    except Exception:
        return False


def get_available_cities() -> List[str]:
    """
    Get list of available cities with market data.

    Returns:
        List of city keys
    """
    cities = list(DEFAULT_MARKET_DATA.keys())

    # Add custom cities from files
    try:
        data_dir = Path(__file__).parent.parent / "data" / "market"
        if data_dir.exists():
            for file_path in data_dir.glob("*_market.json"):
                city_key = file_path.stem.replace("_market", "")
                if city_key not in cities:
                    cities.append(city_key)
    except Exception:
        pass

    return sorted(cities)


def validate_inputs_against_market(inputs_dict: Dict[str, Any], city_key: str = "default") -> Dict[str, str]:
    """
    Validate user inputs against market benchmarks.

    Args:
        inputs_dict: Dictionary of user inputs
        city_key: City for market comparison

    Returns:
        Dictionary of validation warnings
    """
    market_data = load_market_data(city_key)
    warnings = {}

    # Check sale price assumptions
    if "expected_sale_price_psm" in inputs_dict:
        sale_price = inputs_dict["expected_sale_price_psm"]
        market_min = market_data.sale_prices["sale_price_min"]
        market_max = market_data.sale_prices["sale_price_max"]
        market_avg = market_data.sale_prices["sale_price_avg"]

        if sale_price < market_min * 0.8:
            warnings["sale_price"] = (
                f"Sale price ${sale_price:,.0f} is well below market range (${market_min:,.0f}-${market_max:,.0f})"
            )
        elif sale_price > market_max * 1.2:
            warnings["sale_price"] = (
                f"Sale price ${sale_price:,.0f} is well above market range (${market_min:,.0f}-${market_max:,.0f})"
            )
        elif abs(sale_price - market_avg) / market_avg > 0.15:
            warnings["sale_price"] = (
                f"Sale price ${sale_price:,.0f} differs significantly from market average ${market_avg:,.0f}"
            )

    # Check construction cost assumptions
    if "construction_cost_psm" in inputs_dict:
        construction_cost = inputs_dict["construction_cost_psm"]
        cost_min = market_data.construction_costs["construction_cost_min"]
        cost_max = market_data.construction_costs["construction_cost_max"]
        cost_avg = market_data.construction_costs["construction_cost_avg"]

        if construction_cost < cost_min * 0.8:
            warnings["construction_cost"] = (
                f"Construction cost ${construction_cost:,.0f} may be optimistic (market: ${cost_min:,.0f}-${cost_max:,.0f})"
            )
        elif construction_cost > cost_max * 1.2:
            warnings["construction_cost"] = (
                f"Construction cost ${construction_cost:,.0f} seems high (market: ${cost_min:,.0f}-${cost_max:,.0f})"
            )

    # Check soft cost percentage
    if "soft_cost_pct" in inputs_dict:
        soft_cost_pct = inputs_dict["soft_cost_pct"]
        typical_soft_cost = market_data.construction_costs["soft_cost_pct_typical"]

        if abs(soft_cost_pct - typical_soft_cost) > 0.05:  # 5% difference threshold
            warnings["soft_cost"] = f"Soft cost {soft_cost_pct:.1%} differs from typical {typical_soft_cost:.1%}"

    return warnings


def get_market_summary(city_key: str = "default") -> Dict[str, Any]:
    """
    Get formatted market summary for display.

    Args:
        city_key: City identifier

    Returns:
        Dictionary with formatted market data
    """
    market_data = load_market_data(city_key)

    return {
        "city": city_key.title(),
        "land_price_range": f"${market_data.land_comps_psm['land_comp_min']:,.0f} - ${market_data.land_comps_psm['land_comp_max']:,.0f}",
        "sale_price_range": f"${market_data.sale_prices['sale_price_min']:,.0f} - ${market_data.sale_prices['sale_price_max']:,.0f}",
        "construction_cost_avg": f"${market_data.construction_costs['construction_cost_avg']:,.0f}",
        "absorption_rate": f"{market_data.market_indicators['absorption_rate']:.1f} units/month",
        "typical_land_gdv": f"{market_data.market_indicators['land_gdv_benchmark']:.0f}%",
        "typical_profit": f"{market_data.market_indicators['profit_margin_benchmark']:.0f}%",
        "market_strength": _score_to_text(market_data.market_indicators["demand_score"]),
        "last_updated": market_data.market_indicators.get("last_updated", "Unknown"),
    }


def _score_to_text(score: int) -> str:
    """Convert numeric score to descriptive text."""
    if score >= 4:
        return "Strong"
    elif score >= 3:
        return "Moderate"
    else:
        return "Weak"
