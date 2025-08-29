"""
Test suite for calculator modules.
Tests pure calculation functions with no external dependencies.
"""

import pytest
from modules.calculators.residual import (
    calculate_development_capacity,
    calculate_gdv,
    calculate_development_costs,
    calculate_required_profit,
    calculate_residual_land_value,
    calculate_acquisition_metrics,
    calculate_comprehensive_residual,
    calculate_sensitivity_analysis,
    DevelopmentCapacity,
    FinancialResults,
    AcquisitionMetrics,
)

from modules.calculators.unitize import (
    AreaUnit,
    CurrencyUnit,
    convert_area,
    convert_currency,
    calculate_unit_metrics,
    standardize_deal_metrics,
    UnitMetrics,
)


class TestDevelopmentCapacityCalculation:
    """Test development capacity calculations."""
    
    def test_far_limited_development(self):
        """Test development limited by FAR."""
        capacity = calculate_development_capacity(
            land_area_sqm=1000,
            far=2.0,
            coverage=0.8,
            max_floors=10,
            efficiency_ratio=0.85
        )
        
        assert capacity.gross_buildable_sqm == 2000  # 1000 * 2.0
        assert capacity.net_sellable_sqm == 1700  # 2000 * 0.85
        assert capacity.limiting_factor == "far"
    
    def test_coverage_limited_development(self):
        """Test development limited by coverage."""
        capacity = calculate_development_capacity(
            land_area_sqm=1000,
            far=5.0,
            coverage=0.4,
            max_floors=3,
            efficiency_ratio=0.85
        )
        
        assert capacity.gross_buildable_sqm == 1200  # 1000 * 0.4 * 3
        assert capacity.net_sellable_sqm == 1020  # 1200 * 0.85
        assert capacity.limiting_factor == "coverage"
    
    def test_zero_efficiency_ratio(self):
        """Test with zero efficiency ratio."""
        capacity = calculate_development_capacity(
            land_area_sqm=1000,
            far=2.0,
            coverage=0.5,
            max_floors=4,
            efficiency_ratio=0.0
        )
        
        assert capacity.net_sellable_sqm == 0
        assert capacity.gross_buildable_sqm == 2000


class TestGDVCalculation:
    """Test Gross Development Value calculations."""
    
    def test_basic_gdv_calculation(self):
        """Test basic GDV calculation."""
        gdv = calculate_gdv(
            net_sellable_sqm=1000,
            sale_price_psm=4000
        )
        
        assert gdv == 4000000  # 1000 * 4000
    
    def test_zero_area_gdv(self):
        """Test GDV with zero area."""
        gdv = calculate_gdv(
            net_sellable_sqm=0,
            sale_price_psm=4000
        )
        
        assert gdv == 0


class TestDevelopmentCosts:
    """Test development cost calculations."""
    
    def test_basic_cost_calculation(self):
        """Test basic development cost calculation."""
        hard_costs, soft_costs, total_dev_cost = calculate_development_costs(
            gross_buildable_sqm=2000,
            construction_cost_psm=2000,
            soft_cost_pct=0.15,
            financing_cost=50000
        )
        
        assert hard_costs == 4000000  # 2000 * 2000
        assert soft_costs == 600000  # 4000000 * 0.15
        assert total_dev_cost == 4650000  # 4000000 + 600000 + 50000
    
    def test_zero_soft_costs(self):
        """Test with zero soft costs."""
        hard_costs, soft_costs, total_dev_cost = calculate_development_costs(
            gross_buildable_sqm=1000,
            construction_cost_psm=1500,
            soft_cost_pct=0.0,
            financing_cost=0
        )
        
        assert hard_costs == 1500000
        assert soft_costs == 0
        assert total_dev_cost == 1500000


class TestResidualCalculation:
    """Test residual land value calculations."""
    
    def test_positive_residual(self):
        """Test calculation with positive residual."""
        residual = calculate_residual_land_value(
            gdv=5000000,
            total_dev_cost=3000000,
            required_profit=1000000
        )
        
        assert residual == 1000000  # 5M - 3M - 1M
    
    def test_negative_residual(self):
        """Test calculation with negative residual."""
        residual = calculate_residual_land_value(
            gdv=3000000,
            total_dev_cost=3000000,
            required_profit=1000000
        )
        
        assert residual == -1000000  # 3M - 3M - 1M
    
    def test_zero_profit_residual(self):
        """Test calculation with zero profit."""
        residual = calculate_residual_land_value(
            gdv=4000000,
            total_dev_cost=2500000,
            required_profit=0
        )
        
        assert residual == 1500000  # 4M - 2.5M - 0


class TestAcquisitionMetrics:
    """Test acquisition metrics calculations."""
    
    def test_acquisition_metrics_calculation(self):
        """Test comprehensive acquisition metrics."""
        metrics = calculate_acquisition_metrics(
            asking_price=800000,
            taxes_fees=40000,
            land_area_sqm=1000,
            gross_buildable_sqm=2000,
            gdv=6000000,
            residual_land_value=1000000,
            total_dev_cost=4000000,
            net_sellable_sqm=1700
        )
        
        assert metrics.total_acquisition_cost == 840000  # 800K + 40K
        assert metrics.land_psm == 800  # 800K / 1000
        assert metrics.land_per_buildable == 400  # 800K / 2000
        assert abs(metrics.land_pct_gdv - 14.0) < 0.1  # 840K / 6M * 100
        assert metrics.asking_vs_residual == -200000  # 800K - 1M
        assert abs(metrics.breakeven_sale_price - 2847.06) < 0.01  # (4M + 840K) / 1700
    
    def test_zero_buildable_area(self):
        """Test with zero buildable area."""
        metrics = calculate_acquisition_metrics(
            asking_price=500000,
            taxes_fees=25000,
            land_area_sqm=1000,
            gross_buildable_sqm=0,
            gdv=0,
            residual_land_value=0,
            total_dev_cost=1000000,
            net_sellable_sqm=0
        )
        
        assert metrics.land_per_buildable == 0
        assert metrics.breakeven_sale_price == 0


class TestComprehensiveResidual:
    """Test comprehensive residual calculation."""
    
    def test_comprehensive_calculation(self):
        """Test complete residual analysis."""
        capacity, financial, metrics = calculate_comprehensive_residual(
            land_area_sqm=1000,
            asking_price=600000,
            taxes_fees=30000,
            far=2.0,
            coverage=0.6,
            max_floors=5,
            efficiency_ratio=0.85,
            sale_price_psm=4000,
            construction_cost_psm=2000,
            soft_cost_pct=0.15,
            profit_target_pct=0.20,
            financing_cost=100000
        )
        
        # Verify capacity calculation
        assert capacity.gross_buildable_sqm == 2000  # min(2000, 3000)
        assert capacity.limiting_factor == "far"
        assert capacity.net_sellable_sqm == 1700
        
        # Verify financial calculation
        assert financial.gdv == 6800000  # 1700 * 4000
        assert financial.hard_costs == 4000000  # 2000 * 2000
        assert financial.soft_costs == 600000  # 4M * 0.15
        assert financial.total_dev_cost == 4700000  # 4M + 600K + 100K
        assert financial.required_profit == 1360000  # 6.8M * 0.20
        assert financial.residual_land_value == 740000  # 6.8M - 4.7M - 1.36M
        
        # Verify metrics
        assert metrics.total_acquisition_cost == 630000
        assert metrics.asking_vs_residual == -140000  # 600K - 740K


class TestSensitivityAnalysis:
    """Test sensitivity analysis calculations."""
    
    def test_sensitivity_scenarios(self):
        """Test sensitivity analysis scenarios."""
        sensitivity = calculate_sensitivity_analysis(
            base_gdv=6000000,
            base_total_dev_cost=4000000,
            base_required_profit=1200000,
            net_sellable_sqm=1500,
            sale_price_psm=4000,
            hard_costs=3500000,
            soft_cost_pct=0.15,
            profit_target_pct=0.20,
            financing_cost=75000
        )
        
        # Base residual: 6M - 4M - 1.2M = 800K
        assert sensitivity["base_residual"] == 800000
        
        # Sales down 10%: 5.4M GDV, 1.08M profit
        # Residual: 5.4M - 4M - 1.08M = 320K
        assert abs(sensitivity["sales_down_10pct"] - 320000) < 1000
        
        # Costs up 10%: 3.85M hard costs, 577.5K soft costs, 75K financing = 4.5025M total
        # Residual: 6M - 4.5025M - 1.2M = 297.5K
        assert abs(sensitivity["costs_up_10pct"] - 297500) < 1000
        
        # Impact calculations
        assert abs(sensitivity["sales_impact"] - (320000 - 800000)) < 1000
        assert abs(sensitivity["costs_impact"] - (297500 - 800000)) < 1000


class TestUnitConversions:
    """Test unit conversion functions."""
    
    def test_area_conversions(self):
        """Test area unit conversions."""
        # SQM to SQFT
        sqft = convert_area(100, AreaUnit.SQM, AreaUnit.SQFT)
        assert abs(sqft - 1076.39) < 0.1
        
        # SQFT to SQM
        sqm = convert_area(1000, AreaUnit.SQFT, AreaUnit.SQM)
        assert abs(sqm - 92.90) < 0.1
        
        # Same unit conversion
        same = convert_area(500, AreaUnit.SQM, AreaUnit.SQM)
        assert same == 500
    
    def test_currency_conversion_with_rates(self):
        """Test currency conversion with exchange rates."""
        exchange_rates = {
            "EUR": 0.85,
            "JOD": 0.708,
            "AED": 3.673
        }
        
        # USD to EUR
        eur = convert_currency(1000, CurrencyUnit.USD, CurrencyUnit.EUR, exchange_rates)
        assert eur == 850
        
        # EUR to AED (via USD)
        aed = convert_currency(100, CurrencyUnit.EUR, CurrencyUnit.AED, exchange_rates)
        assert abs(aed - 432.12) < 0.1  # 100/0.85 * 3.673
    
    def test_currency_conversion_same_currency(self):
        """Test conversion between same currencies."""
        same = convert_currency(1000, CurrencyUnit.USD, CurrencyUnit.USD)
        assert same == 1000


class TestUnitMetrics:
    """Test unit metrics calculations."""
    
    def test_unit_metrics_calculation(self):
        """Test comprehensive unit metrics."""
        metrics = calculate_unit_metrics(
            land_area_sqm=1000,
            gross_buildable_sqm=2000,
            net_sellable_sqm=1700,
            asking_price=800000,
            construction_cost_total=4000000,
            gdv=6800000,
            profit=1360000,
            residual_land_value=740000
        )
        
        assert metrics.land_cost_per_sqm == 800  # 800K / 1000
        assert metrics.land_cost_per_buildable_sqm == 400  # 800K / 2000
        assert abs(metrics.land_cost_pct_gdv - 11.76) < 0.1  # 800K / 6.8M * 100
        assert metrics.construction_cost_per_sqm == 2000  # 4M / 2000
        assert metrics.gdv_per_sqm == 4000  # 6.8M / 1700
        assert metrics.profit_per_sqm == 800  # 1.36M / 1700
        assert abs(metrics.profit_margin_pct - 20.0) < 0.1  # 1.36M / 6.8M * 100
        assert metrics.residual_per_sqm == 740  # 740K / 1000
        assert metrics.buildable_ratio == 2.0  # 2000 / 1000
        assert abs(metrics.efficiency_ratio - 0.85) < 0.01  # 1700 / 2000
    
    def test_zero_area_metrics(self):
        """Test unit metrics with zero areas."""
        metrics = calculate_unit_metrics(
            land_area_sqm=0,
            gross_buildable_sqm=0,
            net_sellable_sqm=0,
            asking_price=500000,
            construction_cost_total=2000000,
            gdv=0,
            profit=0,
            residual_land_value=0
        )
        
        # Should handle division by zero gracefully
        assert metrics.land_cost_per_sqm == 0
        assert metrics.construction_cost_per_sqm == 0
        assert metrics.gdv_per_sqm == 0
        assert metrics.profit_per_sqm == 0
        assert metrics.residual_per_sqm == 0
        assert metrics.buildable_ratio == 0
        assert metrics.efficiency_ratio == 0


class TestDealStandardization:
    """Test deal standardization functions."""
    
    def test_standardize_deal_metrics(self):
        """Test deal metrics standardization."""
        deal_dict = {
            "land_area_sqm": 1000,
            "expected_sale_price_psm": 4000,
            "construction_cost_psm": 2000,
            "asking_price": 800000,
            "area_unit": "sqm",
            "currency_unit": "USD"
        }
        
        # Standardize to same units (should remain unchanged)
        standardized = standardize_deal_metrics(
            deal_dict,
            target_area_unit=AreaUnit.SQM,
            target_currency=CurrencyUnit.USD
        )
        
        assert standardized["land_area_sqm"] == 1000
        assert standardized["expected_sale_price_psm"] == 4000
        assert standardized["asking_price"] == 800000
    
    def test_standardize_area_units(self):
        """Test area unit standardization."""
        deal_dict = {
            "land_area_sqm": 10764,  # Actually sqft
            "expected_sale_price_psm": 372,  # Actually per sqft
            "area_unit": "sqft",
            "currency_unit": "USD"
        }
        
        # Convert to square meters
        standardized = standardize_deal_metrics(
            deal_dict,
            target_area_unit=AreaUnit.SQM,
            target_currency=CurrencyUnit.USD
        )
        
        # 10764 sqft ≈ 1000 sqm
        assert abs(standardized["land_area_sqm"] - 1000) < 1
        # $372/sqft ≈ $4000/sqm  
        assert abs(standardized["expected_sale_price_psm"] - 4000) < 50