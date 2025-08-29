"""
Configuration registry system for country and city-specific rules.
Loads YAML configuration files and provides RuleSet objects.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from functools import lru_cache


@dataclass 
class CountryRules:
    """Country-specific regulatory and tax rules."""
    
    name: str
    code: str
    currency: str
    language: str
    
    # Tax rates
    transfer_tax_rate: float
    stamp_duty_rate: float = 0.0
    registration_fees: float = 0.0
    legal_fees_rate: float = 0.0
    municipal_fees_rate: float = 0.0
    infrastructure_levy: float = 0.0
    vat_rate: float = 0.0
    corporate_tax_rate: float = 0.0
    withholding_tax_rate: float = 0.0
    
    # Legal requirements
    foreign_ownership_allowed: bool = True
    max_foreign_ownership_pct: float = 1.0
    
    # Financing parameters
    max_ltv_ratio: float = 0.80
    typical_interest_rate: float = 0.05
    min_equity_requirement: float = 0.20


@dataclass
class ZoningRules:
    """Zoning classification with development parameters."""
    
    name: str
    far_max: float
    coverage_max: float
    height_max_m: float
    floors_max: int
    setback_front_m: float
    setback_side_m: float
    setback_rear_m: float
    parking_ratio: float
    
    # Optional mixed-use parameters
    residential_component_min: float = 0.0
    commercial_component_min: float = 0.0


@dataclass
class FinanceRules:
    """Financial parameters and benchmarks."""
    
    profit_targets: Dict[str, float] = field(default_factory=dict)
    soft_costs: Dict[str, float] = field(default_factory=dict) 
    construction_finance: Dict[str, float] = field(default_factory=dict)
    sales: Dict[str, float] = field(default_factory=dict)
    timeline: Dict[str, int] = field(default_factory=dict)
    risk_factors: Dict[str, float] = field(default_factory=dict)
    benchmarks: Dict[str, float] = field(default_factory=dict)


@dataclass
class MarketConfig:
    """Market data configuration and lookup keys."""
    
    data_sources: Dict[str, str] = field(default_factory=dict)
    locations: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    data_keys: Dict[str, List[str]] = field(default_factory=dict)
    validation: Dict[str, float] = field(default_factory=dict)
    fallback_values: Dict[str, float] = field(default_factory=dict)
    integration: Dict[str, Any] = field(default_factory=dict)


@dataclass  
class GlobalConfig:
    """Global system configuration."""
    
    units: Dict[str, str] = field(default_factory=dict)
    scoring: Dict[str, Dict[str, float]] = field(default_factory=dict)
    development: Dict[str, Dict[str, float]] = field(default_factory=dict)
    validation: Dict[str, bool] = field(default_factory=dict)


@dataclass
class RuleSet:
    """Complete rule set for a country/region."""
    
    country_code: str
    global_config: GlobalConfig
    country_rules: CountryRules
    zoning_rules: Dict[str, ZoningRules]
    finance_rules: FinanceRules
    market_config: MarketConfig
    
    def get_zoning(self, zoning_code: str) -> Optional[ZoningRules]:
        """Get zoning rules by code."""
        return self.zoning_rules.get(zoning_code.upper())
    
    def get_profit_target(self, development_type: str) -> float:
        """Get profit target for development type."""
        return self.finance_rules.profit_targets.get(
            development_type, 
            self.global_config.development.get("profit_target", {}).get("min", 0.15)
        )
    
    def get_soft_cost_pct(self) -> float:
        """Get total soft cost percentage."""
        return self.finance_rules.soft_costs.get(
            "total_soft_cost_pct",
            self.global_config.scoring.get("thresholds", {}).get("soft_cost_default", 0.15)
        )


class ConfigRegistry:
    """Registry for loading and caching configuration files."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize registry with configuration directory.
        
        Args:
            config_dir: Path to configuration directory (defaults to configs/)
        """
        if config_dir is None:
            config_dir = Path(__file__).parent.parent.parent / "configs"
        self.config_dir = Path(config_dir)
        
        if not self.config_dir.exists():
            raise ValueError(f"Configuration directory not found: {self.config_dir}")
    
    @lru_cache(maxsize=16)
    def load_global_config(self) -> GlobalConfig:
        """Load global configuration."""
        global_path = self.config_dir / "default" / "global.yml"
        
        if not global_path.exists():
            raise ValueError(f"Global config not found: {global_path}")
            
        with open(global_path, 'r') as f:
            data = yaml.safe_load(f)
            
        return GlobalConfig(
            units=data.get("units", {}),
            scoring=data.get("scoring", {}),
            development=data.get("development", {}),
            validation=data.get("validation", {})
        )
    
    @lru_cache(maxsize=32)
    def load_country_rules(self, country_code: str) -> CountryRules:
        """Load country-specific rules."""
        country_path = self.config_dir / country_code / "country.yml"
        
        if not country_path.exists():
            raise ValueError(f"Country config not found: {country_path}")
            
        with open(country_path, 'r') as f:
            data = yaml.safe_load(f)
            
        country_data = data["country"]
        taxes_data = data.get("taxes", {})
        legal_data = data.get("legal", {})
        financing_data = data.get("financing", {})
        
        return CountryRules(
            name=country_data["name"],
            code=country_data["code"],
            currency=country_data["currency"],
            language=country_data["language"],
            
            # Tax rates
            transfer_tax_rate=taxes_data.get("transfer_tax_rate", 0.0),
            stamp_duty_rate=taxes_data.get("stamp_duty_rate", 0.0),
            registration_fees=taxes_data.get("registration_fees", 0.0),
            legal_fees_rate=taxes_data.get("legal_fees_rate", 0.0),
            municipal_fees_rate=taxes_data.get("municipal_fees_rate", 0.0),
            infrastructure_levy=taxes_data.get("infrastructure_levy", 0.0),
            vat_rate=taxes_data.get("vat_rate", 0.0),
            corporate_tax_rate=taxes_data.get("corporate_tax_rate", 0.0),
            withholding_tax_rate=taxes_data.get("withholding_tax_rate", 0.0),
            
            # Legal requirements
            foreign_ownership_allowed=legal_data.get("foreign_ownership", {}).get("allowed", True),
            max_foreign_ownership_pct=legal_data.get("foreign_ownership", {}).get("max_ownership_pct", 1.0),
            
            # Financing
            max_ltv_ratio=financing_data.get("max_ltv_ratio", 0.80),
            typical_interest_rate=financing_data.get("typical_interest_rate", 0.05),
            min_equity_requirement=financing_data.get("min_equity_requirement", 0.20)
        )
    
    @lru_cache(maxsize=32)
    def load_zoning_rules(self, country_code: str) -> Dict[str, ZoningRules]:
        """Load zoning rules for a country."""
        zoning_path = self.config_dir / country_code / "zoning.yml"
        
        if not zoning_path.exists():
            raise ValueError(f"Zoning config not found: {zoning_path}")
            
        with open(zoning_path, 'r') as f:
            data = yaml.safe_load(f)
            
        zoning_rules = {}
        for zone_code, zone_data in data["zoning"].items():
            zoning_rules[zone_code] = ZoningRules(
                name=zone_data["name"],
                far_max=zone_data["far_max"],
                coverage_max=zone_data["coverage_max"], 
                height_max_m=zone_data["height_max_m"],
                floors_max=zone_data["floors_max"],
                setback_front_m=zone_data["setback_front_m"],
                setback_side_m=zone_data["setback_side_m"],
                setback_rear_m=zone_data["setback_rear_m"],
                parking_ratio=zone_data["parking_ratio"],
                residential_component_min=zone_data.get("residential_component_min", 0.0),
                commercial_component_min=zone_data.get("commercial_component_min", 0.0)
            )
            
        return zoning_rules
    
    @lru_cache(maxsize=32)
    def load_finance_rules(self, country_code: str) -> FinanceRules:
        """Load financial rules for a country."""
        finance_path = self.config_dir / country_code / "finance.yml"
        
        if not finance_path.exists():
            raise ValueError(f"Finance config not found: {finance_path}")
            
        with open(finance_path, 'r') as f:
            data = yaml.safe_load(f)
            
        return FinanceRules(
            profit_targets=data.get("finance", {}).get("profit_targets", {}),
            soft_costs=data.get("finance", {}).get("soft_costs", {}),
            construction_finance=data.get("finance", {}).get("construction_finance", {}),
            sales=data.get("finance", {}).get("sales", {}),
            timeline=data.get("finance", {}).get("timeline", {}),
            risk_factors=data.get("risk_factors", {}),
            benchmarks=data.get("benchmarks", {})
        )
    
    @lru_cache(maxsize=32)
    def load_market_config(self, country_code: str) -> MarketConfig:
        """Load market configuration for a country."""
        market_path = self.config_dir / country_code / "market.yml"
        
        if not market_path.exists():
            raise ValueError(f"Market config not found: {market_path}")
            
        with open(market_path, 'r') as f:
            data = yaml.safe_load(f)
            
        market_data = data.get("market", {})
        
        return MarketConfig(
            data_sources=market_data.get("data_sources", {}),
            locations=market_data.get("locations", {}),
            data_keys=market_data.get("data_keys", {}),
            validation=market_data.get("validation", {}),
            fallback_values=market_data.get("fallback_values", {}),
            integration=market_data.get("integration", {})
        )
    
    @lru_cache(maxsize=32)
    def get_ruleset(self, country_code: str) -> RuleSet:
        """
        Get complete ruleset for a country.
        
        Args:
            country_code: Two-letter country code (e.g., 'JO', 'UAE')
            
        Returns:
            RuleSet with all loaded configurations
        """
        return RuleSet(
            country_code=country_code,
            global_config=self.load_global_config(),
            country_rules=self.load_country_rules(country_code),
            zoning_rules=self.load_zoning_rules(country_code),
            finance_rules=self.load_finance_rules(country_code),
            market_config=self.load_market_config(country_code)
        )
    
    def get_available_countries(self) -> List[str]:
        """Get list of available country codes."""
        countries = []
        for path in self.config_dir.iterdir():
            if path.is_dir() and path.name not in ["default", "__pycache__"]:
                countries.append(path.name)
        return sorted(countries)
    
    def clear_cache(self):
        """Clear all cached configurations."""
        self.load_global_config.cache_clear()
        self.load_country_rules.cache_clear() 
        self.load_zoning_rules.cache_clear()
        self.load_finance_rules.cache_clear()
        self.load_market_config.cache_clear()
        self.get_ruleset.cache_clear()


# Global registry instance
_registry = None


def get_registry(config_dir: Optional[Path] = None) -> ConfigRegistry:
    """Get the global configuration registry instance."""
    global _registry
    if _registry is None or config_dir is not None:
        _registry = ConfigRegistry(config_dir)
    return _registry


def get_ruleset(country_code: str) -> RuleSet:
    """Convenience function to get ruleset for a country."""
    return get_registry().get_ruleset(country_code)


def get_available_countries() -> List[str]:
    """Convenience function to get available country codes."""
    return get_registry().get_available_countries()