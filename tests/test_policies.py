"""
Test suite for policy registry and validation systems.
Tests configuration loading and validation logic.
"""

import pytest
import tempfile
import yaml
from pathlib import Path

from modules.policies.registry import (
    ConfigRegistry,
    RuleSet,
    CountryRules,
    ZoningRules,
    FinanceRules,
    MarketConfig,
    GlobalConfig,
    get_registry,
    get_ruleset,
)

from modules.policies.validation import (
    ValidationSeverity,
    ValidationIssue,
    ValidationReport,
    ZoningValidator,
    PermitValidator,
    FinancingValidator,
    validate_deal_comprehensive,
)

from utils.errors import ConfigurationError


class TestConfigRegistry:
    """Test configuration registry functionality."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory with test configs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "configs"
            
            # Create directory structure
            (config_dir / "default").mkdir(parents=True)
            (config_dir / "TEST").mkdir(parents=True)
            
            # Create global config
            global_config = {
                "units": {"area": "sqm", "currency": "USD"},
                "scoring": {
                    "weights": {"residual_score": 0.4, "land_pct_score": 0.35},
                    "thresholds": {"residual_margin_buffer": 0.10}
                },
                "development": {
                    "efficiency_ratio": {"min": 0.6, "max": 0.95},
                    "profit_target": {"min": 0.05, "max": 0.5}
                },
                "validation": {"strict_mode": False}
            }
            
            with open(config_dir / "default" / "global.yml", 'w') as f:
                yaml.dump(global_config, f)
            
            # Create test country config
            country_config = {
                "country": {"name": "Test Country", "code": "TEST", "currency": "TCC", "language": "en"},
                "taxes": {"transfer_tax_rate": 0.05, "vat_rate": 0.10},
                "legal": {
                    "foreign_ownership": {"allowed": True, "max_ownership_pct": 1.0}
                },
                "financing": {
                    "max_ltv_ratio": 0.75,
                    "typical_interest_rate": 0.06,
                    "min_equity_requirement": 0.25
                }
            }
            
            with open(config_dir / "TEST" / "country.yml", 'w') as f:
                yaml.dump(country_config, f)
            
            # Create test zoning config
            zoning_config = {
                "zoning": {
                    "R1": {
                        "name": "Test Residential",
                        "far_max": 2.0,
                        "coverage_max": 0.5,
                        "height_max_m": 20,
                        "floors_max": 5,
                        "setback_front_m": 5,
                        "setback_side_m": 3,
                        "setback_rear_m": 4,
                        "parking_ratio": 1.5
                    }
                }
            }
            
            with open(config_dir / "TEST" / "zoning.yml", 'w') as f:
                yaml.dump(zoning_config, f)
            
            # Create test finance config
            finance_config = {
                "finance": {
                    "profit_targets": {"residential": 0.18},
                    "soft_costs": {"total_soft_cost_pct": 0.16}
                },
                "benchmarks": {"land_cost_gdv_typical": 0.22}
            }
            
            with open(config_dir / "TEST" / "finance.yml", 'w') as f:
                yaml.dump(finance_config, f)
            
            # Create test market config
            market_config = {
                "market": {
                    "data_sources": {"primary": "test_data"},
                    "locations": {
                        "test_city": {"tier": 1, "demand_score": 4}
                    },
                    "fallback_values": {"land_comp_avg_tcc_sqm": 100}
                }
            }
            
            with open(config_dir / "TEST" / "market.yml", 'w') as f:
                yaml.dump(market_config, f)
            
            yield config_dir
    
    def test_load_global_config(self, temp_config_dir):
        """Test loading global configuration."""
        registry = ConfigRegistry(temp_config_dir)
        global_config = registry.load_global_config()
        
        assert global_config.units["area"] == "sqm"
        assert global_config.units["currency"] == "USD"
        assert global_config.scoring["weights"]["residual_score"] == 0.4
        assert global_config.development["efficiency_ratio"]["min"] == 0.6
    
    def test_load_country_rules(self, temp_config_dir):
        """Test loading country-specific rules."""
        registry = ConfigRegistry(temp_config_dir)
        country_rules = registry.load_country_rules("TEST")
        
        assert country_rules.name == "Test Country"
        assert country_rules.code == "TEST"
        assert country_rules.currency == "TCC"
        assert country_rules.transfer_tax_rate == 0.05
        assert country_rules.vat_rate == 0.10
        assert country_rules.foreign_ownership_allowed == True
        assert country_rules.max_ltv_ratio == 0.75
    
    def test_load_zoning_rules(self, temp_config_dir):
        """Test loading zoning rules."""
        registry = ConfigRegistry(temp_config_dir)
        zoning_rules = registry.load_zoning_rules("TEST")
        
        assert "R1" in zoning_rules
        r1_zone = zoning_rules["R1"]
        assert r1_zone.name == "Test Residential"
        assert r1_zone.far_max == 2.0
        assert r1_zone.coverage_max == 0.5
        assert r1_zone.floors_max == 5
        assert r1_zone.parking_ratio == 1.5
    
    def test_load_finance_rules(self, temp_config_dir):
        """Test loading finance rules."""
        registry = ConfigRegistry(temp_config_dir)
        finance_rules = registry.load_finance_rules("TEST")
        
        assert finance_rules.profit_targets["residential"] == 0.18
        assert finance_rules.soft_costs["total_soft_cost_pct"] == 0.16
        assert finance_rules.benchmarks["land_cost_gdv_typical"] == 0.22
    
    def test_load_market_config(self, temp_config_dir):
        """Test loading market configuration."""
        registry = ConfigRegistry(temp_config_dir)
        market_config = registry.load_market_config("TEST")
        
        assert market_config.data_sources["primary"] == "test_data"
        assert "test_city" in market_config.locations
        assert market_config.locations["test_city"]["tier"] == 1
        assert market_config.fallback_values["land_comp_avg_tcc_sqm"] == 100
    
    def test_get_complete_ruleset(self, temp_config_dir):
        """Test loading complete ruleset."""
        registry = ConfigRegistry(temp_config_dir)
        ruleset = registry.get_ruleset("TEST")
        
        assert isinstance(ruleset, RuleSet)
        assert ruleset.country_code == "TEST"
        assert isinstance(ruleset.global_config, GlobalConfig)
        assert isinstance(ruleset.country_rules, CountryRules)
        assert isinstance(ruleset.zoning_rules, dict)
        assert isinstance(ruleset.finance_rules, FinanceRules)
        assert isinstance(ruleset.market_config, MarketConfig)
    
    def test_missing_config_error(self, temp_config_dir):
        """Test error handling for missing configuration."""
        registry = ConfigRegistry(temp_config_dir)
        
        with pytest.raises(ValueError, match="Country config not found"):
            registry.load_country_rules("MISSING")
    
    def test_get_available_countries(self, temp_config_dir):
        """Test getting available countries."""
        registry = ConfigRegistry(temp_config_dir)
        countries = registry.get_available_countries()
        
        assert "TEST" in countries
        assert "default" not in countries  # Should be filtered out


class TestRuleSet:
    """Test RuleSet functionality."""
    
    @pytest.fixture
    def sample_ruleset(self, temp_config_dir):
        """Create sample ruleset for testing."""
        registry = ConfigRegistry(temp_config_dir)
        return registry.get_ruleset("TEST")
    
    def test_get_zoning(self, sample_ruleset):
        """Test getting zoning rules by code."""
        r1_zone = sample_ruleset.get_zoning("R1")
        assert r1_zone is not None
        assert r1_zone.name == "Test Residential"
        
        missing_zone = sample_ruleset.get_zoning("MISSING")
        assert missing_zone is None
    
    def test_get_profit_target(self, sample_ruleset):
        """Test getting profit target for development type."""
        residential_profit = sample_ruleset.get_profit_target("residential")
        assert residential_profit == 0.18
        
        # Should return default for unknown type
        unknown_profit = sample_ruleset.get_profit_target("unknown")
        assert unknown_profit == 0.05  # Global minimum
    
    def test_get_soft_cost_pct(self, sample_ruleset):
        """Test getting soft cost percentage."""
        soft_cost_pct = sample_ruleset.get_soft_cost_pct()
        assert soft_cost_pct == 0.16


class TestValidationIssue:
    """Test validation issue classes."""
    
    def test_validation_issue_creation(self):
        """Test creating validation issues."""
        issue = ValidationIssue(
            severity=ValidationSeverity.ERROR,
            category="zoning",
            code="FAR_EXCEEDED",
            message="FAR exceeds maximum allowed",
            field="far",
            value=3.0,
            suggestion="Reduce FAR to 2.5"
        )
        
        assert issue.severity == ValidationSeverity.ERROR
        assert issue.category == "zoning"
        assert issue.code == "FAR_EXCEEDED"
        assert issue.field == "far"
        assert issue.value == 3.0
    
    def test_validation_report(self):
        """Test validation report functionality."""
        report = ValidationReport(is_valid=True)
        
        # Add a warning
        warning = ValidationIssue(
            severity=ValidationSeverity.WARNING,
            category="zoning",
            code="FAR_HIGH",
            message="FAR is close to maximum"
        )
        report.add_issue(warning)
        
        assert len(report.warnings) == 1
        assert len(report.errors) == 0
        assert report.is_valid == True
        
        # Add an error
        error = ValidationIssue(
            severity=ValidationSeverity.ERROR,
            category="zoning", 
            code="FAR_EXCEEDED",
            message="FAR exceeds maximum"
        )
        report.add_issue(error)
        
        assert len(report.warnings) == 1
        assert len(report.errors) == 1
        assert report.is_valid == False
    
    def test_validation_report_summary(self):
        """Test validation report summary."""
        report = ValidationReport(is_valid=True)
        
        # Add issues of different severities
        for severity in [ValidationSeverity.INFO, ValidationSeverity.WARNING, ValidationSeverity.ERROR]:
            issue = ValidationIssue(
                severity=severity,
                category="test",
                code=f"TEST_{severity.value.upper()}",
                message=f"Test {severity.value} message"
            )
            report.add_issue(issue)
        
        summary = report.summary()
        assert summary["info"] == 1
        assert summary["warning"] == 1
        assert summary["error"] == 1
        assert summary["critical"] == 0


class TestZoningValidator:
    """Test zoning validation functionality."""
    
    @pytest.fixture
    def sample_ruleset(self, temp_config_dir):
        """Create sample ruleset for testing."""
        registry = ConfigRegistry(temp_config_dir)
        return registry.get_ruleset("TEST")
    
    def test_valid_zoning_compliance(self, sample_ruleset):
        """Test validation of compliant zoning parameters."""
        validator = ZoningValidator(sample_ruleset)
        
        report = validator.validate_zoning_compliance(
            zoning_code="R1",
            land_area_sqm=1000,
            far=1.5,  # Under 2.0 limit
            coverage=0.4,  # Under 0.5 limit
            max_floors=3,  # Under 5 limit
            building_height_m=15,  # Under 20m limit
            setbacks={"front": 6, "side": 4, "rear": 5}  # All exceed minimums
        )
        
        assert report.is_valid == True
        assert len(report.errors) == 0
    
    def test_far_exceeded_error(self, sample_ruleset):
        """Test FAR exceeded validation."""
        validator = ZoningValidator(sample_ruleset)
        
        report = validator.validate_zoning_compliance(
            zoning_code="R1",
            land_area_sqm=1000,
            far=2.5,  # Exceeds 2.0 limit
            coverage=0.4,
            max_floors=3
        )
        
        assert report.is_valid == False
        assert len(report.errors) == 1
        assert report.errors[0].code == "FAR_EXCEEDED"
        assert report.errors[0].field == "far"
        assert report.errors[0].value == 2.5
    
    def test_coverage_exceeded_error(self, sample_ruleset):
        """Test coverage exceeded validation."""
        validator = ZoningValidator(sample_ruleset)
        
        report = validator.validate_zoning_compliance(
            zoning_code="R1",
            land_area_sqm=1000,
            far=1.5,
            coverage=0.6,  # Exceeds 0.5 limit
            max_floors=3
        )
        
        assert report.is_valid == False
        assert len(report.errors) == 1
        assert report.errors[0].code == "COVERAGE_EXCEEDED"
    
    def test_floors_exceeded_error(self, sample_ruleset):
        """Test floors exceeded validation."""
        validator = ZoningValidator(sample_ruleset)
        
        report = validator.validate_zoning_compliance(
            zoning_code="R1",
            land_area_sqm=1000,
            far=1.5,
            coverage=0.4,
            max_floors=6  # Exceeds 5 limit
        )
        
        assert report.is_valid == False
        assert len(report.errors) == 1
        assert report.errors[0].code == "FLOORS_EXCEEDED"
    
    def test_height_exceeded_error(self, sample_ruleset):
        """Test height exceeded validation."""
        validator = ZoningValidator(sample_ruleset)
        
        report = validator.validate_zoning_compliance(
            zoning_code="R1",
            land_area_sqm=1000,
            far=1.5,
            coverage=0.4,
            max_floors=3,
            building_height_m=25  # Exceeds 20m limit
        )
        
        assert report.is_valid == False
        assert len(report.errors) == 1
        assert report.errors[0].code == "HEIGHT_EXCEEDED"
    
    def test_setback_insufficient_error(self, sample_ruleset):
        """Test insufficient setback validation."""
        validator = ZoningValidator(sample_ruleset)
        
        report = validator.validate_zoning_compliance(
            zoning_code="R1",
            land_area_sqm=1000,
            far=1.5,
            coverage=0.4,
            max_floors=3,
            setbacks={"front": 3, "side": 2, "rear": 2}  # All below minimums
        )
        
        assert report.is_valid == False
        assert len(report.errors) == 3  # Three setback violations
        setback_codes = [error.code for error in report.errors]
        assert all(code == "SETBACK_INSUFFICIENT" for code in setback_codes)
    
    def test_unknown_zoning_error(self, sample_ruleset):
        """Test unknown zoning code validation."""
        validator = ZoningValidator(sample_ruleset)
        
        report = validator.validate_zoning_compliance(
            zoning_code="UNKNOWN",
            land_area_sqm=1000,
            far=1.5,
            coverage=0.4,
            max_floors=3
        )
        
        assert report.is_valid == False
        assert len(report.errors) == 1
        assert report.errors[0].code == "ZONING_NOT_FOUND"
        assert report.errors[0].field == "zoning"
    
    def test_far_warning_threshold(self, sample_ruleset):
        """Test FAR warning threshold."""
        validator = ZoningValidator(sample_ruleset)
        
        report = validator.validate_zoning_compliance(
            zoning_code="R1",
            land_area_sqm=1000,
            far=1.9,  # 95% of 2.0 limit (triggers warning at 90%)
            coverage=0.4,
            max_floors=3
        )
        
        assert report.is_valid == True
        assert len(report.warnings) == 1
        assert report.warnings[0].code == "FAR_HIGH"


class TestPermitValidator:
    """Test permit validation functionality."""
    
    @pytest.fixture
    def sample_ruleset(self, temp_config_dir):
        """Create sample ruleset for testing."""
        registry = ConfigRegistry(temp_config_dir)
        return registry.get_ruleset("TEST")
    
    def test_basic_permit_requirements(self, sample_ruleset):
        """Test basic permit requirement validation."""
        validator = PermitValidator(sample_ruleset)
        
        report = validator.validate_permit_requirements(
            gross_buildable_sqm=1500,
            floors=3,
            foreign_ownership=False
        )
        
        assert report.is_valid == True
        # Should have info messages for various requirements
        info_codes = [issue.code for issue in report.issues if issue.severity == ValidationSeverity.INFO]
        assert "BUILDING_PERMIT_REQUIRED" in info_codes
        assert "FIRE_SAFETY_APPROVAL_REQUIRED" in info_codes
    
    def test_foreign_ownership_allowed(self, sample_ruleset):
        """Test foreign ownership validation when allowed."""
        validator = PermitValidator(sample_ruleset)
        
        report = validator.validate_permit_requirements(
            gross_buildable_sqm=1000,
            floors=2,
            foreign_ownership=True
        )
        
        assert report.is_valid == True
        # Should not have foreign ownership errors since it's allowed
        error_codes = [issue.code for issue in report.errors]
        assert "FOREIGN_OWNERSHIP_RESTRICTED" not in error_codes
    
    def test_elevator_requirement(self, sample_ruleset):
        """Test elevator requirement for tall buildings."""
        validator = PermitValidator(sample_ruleset)
        
        report = validator.validate_permit_requirements(
            gross_buildable_sqm=1000,
            floors=5,  # >= 4 floors requires elevator
            foreign_ownership=False
        )
        
        assert report.is_valid == True
        info_codes = [issue.code for issue in report.issues if issue.severity == ValidationSeverity.INFO]
        assert "ELEVATOR_REQUIRED" in info_codes
    
    def test_environmental_clearance_requirement(self, sample_ruleset):
        """Test environmental clearance for large developments."""
        validator = PermitValidator(sample_ruleset)
        
        report = validator.validate_permit_requirements(
            gross_buildable_sqm=1500,  # > 1000 sqm threshold
            floors=3,
            foreign_ownership=False
        )
        
        assert report.is_valid == True
        info_codes = [issue.code for issue in report.issues if issue.severity == ValidationSeverity.INFO]
        assert "ENVIRONMENTAL_CLEARANCE_REQUIRED" in info_codes


class TestFinancingValidator:
    """Test financing validation functionality."""
    
    @pytest.fixture
    def sample_ruleset(self, temp_config_dir):
        """Create sample ruleset for testing."""
        registry = ConfigRegistry(temp_config_dir)
        return registry.get_ruleset("TEST")
    
    def test_valid_financing_parameters(self, sample_ruleset):
        """Test validation of valid financing parameters."""
        validator = FinancingValidator(sample_ruleset)
        
        report = validator.validate_financing_feasibility(
            equity_pct=0.30,  # Above 25% minimum
            ltv_ratio=0.70,  # Below 75% maximum
            foreign_buyer=False
        )
        
        assert report.is_valid == True
        assert len(report.errors) == 0
    
    def test_ltv_exceeded_error(self, sample_ruleset):
        """Test LTV exceeded validation."""
        validator = FinancingValidator(sample_ruleset)
        
        report = validator.validate_financing_feasibility(
            equity_pct=0.20,
            ltv_ratio=0.80,  # Exceeds 75% limit
            foreign_buyer=False
        )
        
        assert report.is_valid == False
        assert len(report.errors) == 1
        assert report.errors[0].code == "LTV_EXCEEDED"
    
    def test_insufficient_equity_error(self, sample_ruleset):
        """Test insufficient equity validation."""
        validator = FinancingValidator(sample_ruleset)
        
        report = validator.validate_financing_feasibility(
            equity_pct=0.20,  # Below 25% minimum
            ltv_ratio=0.70,
            foreign_buyer=False
        )
        
        assert report.is_valid == False
        assert len(report.errors) == 1
        assert report.errors[0].code == "INSUFFICIENT_EQUITY"


class TestComprehensiveValidation:
    """Test comprehensive deal validation."""
    
    @pytest.fixture
    def sample_ruleset(self, temp_config_dir):
        """Create sample ruleset for testing."""
        registry = ConfigRegistry(temp_config_dir)
        return registry.get_ruleset("TEST")
    
    def test_comprehensive_validation_success(self, sample_ruleset):
        """Test comprehensive validation of valid deal."""
        deal_inputs = {
            "zoning": "R1",
            "land_area_sqm": 1000,
            "far": 1.5,
            "coverage": 0.4,
            "max_floors": 3,
            "ltv_ratio": 0.70,
            "foreign_ownership": False,
            "foreign_buyer": False
        }
        
        report = validate_deal_comprehensive(sample_ruleset, deal_inputs)
        
        assert report.is_valid == True
        # Should have some info messages but no errors
        assert len(report.errors) == 0
        assert len(report.issues) > 0  # Info messages about requirements
    
    def test_comprehensive_validation_multiple_errors(self, sample_ruleset):
        """Test comprehensive validation with multiple violations."""
        deal_inputs = {
            "zoning": "R1",
            "land_area_sqm": 1000,
            "far": 2.5,  # Exceeds zoning limit
            "coverage": 0.6,  # Exceeds zoning limit
            "max_floors": 3,
            "ltv_ratio": 0.85,  # Exceeds financing limit
            "foreign_ownership": False,
            "foreign_buyer": False
        }
        
        report = validate_deal_comprehensive(sample_ruleset, deal_inputs)
        
        assert report.is_valid == False
        assert len(report.errors) >= 3  # At least FAR, coverage, and LTV errors
        
        error_codes = [error.code for error in report.errors]
        assert "FAR_EXCEEDED" in error_codes
        assert "COVERAGE_EXCEEDED" in error_codes
        assert "LTV_EXCEEDED" in error_codes