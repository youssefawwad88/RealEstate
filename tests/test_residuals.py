"""
Test suite for residual land value calculations and deal modeling.
"""

import pytest
import pandas as pd
from modules.deal_model import LandInputs, CalculatedOutputs, LandDeal, create_deal_from_dict, batch_process_deals
from modules.market_lookup import load_market_data, validate_inputs_against_market


class TestLandInputs:
    """Test input validation and data model."""

    def test_valid_inputs(self):
        """Test creation of valid land inputs."""
        inputs = LandInputs(
            site_name="Test Site",
            land_area_sqm=1000.0,
            asking_price=500000.0,
            taxes_fees=25000.0,
            zoning="Residential",
            far=1.2,
            coverage=0.4,
            max_floors=3,
            efficiency_ratio=0.85,
            expected_sale_price_psm=3500.0,
            construction_cost_psm=1800.0,
            soft_cost_pct=0.15,
            profit_target_pct=0.20,
        )

        assert inputs.site_name == "Test Site"
        assert inputs.land_area_sqm == 1000.0
        assert inputs.asking_price == 500000.0
        assert inputs.efficiency_ratio == 0.85

    def test_invalid_efficiency_ratio(self):
        """Test validation of efficiency ratio bounds."""
        with pytest.raises(ValueError, match="Efficiency ratio should be between 60% and 95%"):
            LandInputs(
                site_name="Test Site",
                land_area_sqm=1000.0,
                asking_price=500000.0,
                far=1.2,
                coverage=0.4,
                max_floors=3,
                efficiency_ratio=0.5,  # Too low
                expected_sale_price_psm=3500.0,
                construction_cost_psm=1800.0,
                soft_cost_pct=0.15,
                profit_target_pct=0.20,
            )

    def test_invalid_profit_target(self):
        """Test validation of profit target bounds."""
        with pytest.raises(ValueError, match="Profit target should be between 5% and 50%"):
            LandInputs(
                site_name="Test Site",
                land_area_sqm=1000.0,
                asking_price=500000.0,
                far=1.2,
                coverage=0.4,
                max_floors=3,
                efficiency_ratio=0.85,
                expected_sale_price_psm=3500.0,
                construction_cost_psm=1800.0,
                soft_cost_pct=0.15,
                profit_target_pct=0.60,  # Too high
            )


class TestDealCalculations:
    """Test core deal calculation logic."""

    @pytest.fixture
    def sample_deal(self):
        """Create a sample deal for testing."""
        inputs = LandInputs(
            site_name="Sample Deal",
            land_area_sqm=1000.0,
            asking_price=400000.0,
            taxes_fees=20000.0,
            zoning="Mixed-use",
            far=1.5,
            coverage=0.4,
            max_floors=4,
            efficiency_ratio=0.85,
            expected_sale_price_psm=4000.0,
            construction_cost_psm=2000.0,
            soft_cost_pct=0.15,
            profit_target_pct=0.20,
            financing_cost=30000.0,
        )
        return LandDeal(inputs=inputs).compute_outputs()

    def test_buildable_area_calculation(self, sample_deal):
        """Test buildable area calculation with FAR and coverage constraints."""
        # FAR constraint: 1000 * 1.5 = 1500 sqm
        # Coverage constraint: 1000 * 0.4 * 4 = 1600 sqm
        # Should take minimum: 1500 sqm

        assert sample_deal.outputs.gross_buildable_sqm == 1500.0
        assert sample_deal.outputs.net_sellable_sqm == 1500.0 * 0.85

    def test_gdv_calculation(self, sample_deal):
        """Test Gross Development Value calculation."""
        expected_gdv = 1500.0 * 0.85 * 4000.0  # Net sellable * price per sqm
        assert sample_deal.outputs.gdv == expected_gdv

    def test_cost_calculations(self, sample_deal):
        """Test development cost calculations."""
        expected_hard_costs = 1500.0 * 2000.0  # Buildable area * cost per sqm
        expected_soft_costs = expected_hard_costs * 0.15
        expected_total_dev_cost = expected_hard_costs + expected_soft_costs + 30000.0

        assert sample_deal.outputs.hard_costs == expected_hard_costs
        assert sample_deal.outputs.soft_costs == expected_soft_costs
        assert sample_deal.outputs.total_dev_cost == expected_total_dev_cost

    def test_residual_calculation(self, sample_deal):
        """Test residual land value calculation."""
        gdv = sample_deal.outputs.gdv
        total_dev_cost = sample_deal.outputs.total_dev_cost
        required_profit = gdv * 0.20
        expected_residual = gdv - total_dev_cost - required_profit

        assert sample_deal.outputs.required_profit == required_profit
        assert sample_deal.outputs.residual_land_value == expected_residual

    def test_acquisition_metrics(self, sample_deal):
        """Test acquisition-related metrics."""
        expected_total_acq = 400000.0 + 20000.0  # asking + fees
        expected_land_psm = 400000.0 / 1000.0
        expected_land_per_buildable = 400000.0 / 1500.0
        expected_land_pct_gdv = (expected_total_acq / sample_deal.outputs.gdv) * 100

        assert sample_deal.outputs.total_acquisition_cost == expected_total_acq
        assert sample_deal.outputs.land_psm == expected_land_psm
        assert sample_deal.outputs.land_per_buildable == expected_land_per_buildable
        assert abs(sample_deal.outputs.land_pct_gdv - expected_land_pct_gdv) < 0.01


class TestViabilityScoring:
    """Test viability scoring and risk assessment."""

    def test_viable_deal_scoring(self):
        """Test scoring for a viable deal."""
        # Create a healthy deal
        inputs = LandInputs(
            site_name="Viable Deal",
            land_area_sqm=1000.0,
            asking_price=300000.0,  # Low asking price
            taxes_fees=15000.0,
            far=1.5,
            coverage=0.4,
            max_floors=4,
            efficiency_ratio=0.85,
            expected_sale_price_psm=4500.0,  # High sale price
            construction_cost_psm=1800.0,  # Low construction cost
            soft_cost_pct=0.12,
            profit_target_pct=0.18,
        )

        deal = LandDeal(inputs=inputs).compute_outputs()

        # Should have good scores
        assert deal.viability.overall_score == "green"
        assert deal.viability.residual_score == "green"
        assert deal.outputs.land_pct_gdv < 25  # Should be within norms

    def test_marginal_deal_scoring(self):
        """Test scoring for a marginal deal."""
        # Create a marginal deal
        inputs = LandInputs(
            site_name="Marginal Deal",
            land_area_sqm=1000.0,
            asking_price=450000.0,  # Higher asking price
            taxes_fees=25000.0,
            far=1.2,
            coverage=0.35,
            max_floors=3,
            efficiency_ratio=0.85,
            expected_sale_price_psm=3800.0,
            construction_cost_psm=2100.0,  # Higher construction cost
            soft_cost_pct=0.18,
            profit_target_pct=0.22,
        )

        deal = LandDeal(inputs=inputs).compute_outputs()

        # Should have yellow or red flags
        assert deal.viability.overall_score in ["yellow", "red"]

    def test_unviable_deal_scoring(self):
        """Test scoring for an unviable deal."""
        # Create a poor deal
        inputs = LandInputs(
            site_name="Poor Deal",
            land_area_sqm=800.0,
            asking_price=600000.0,  # Very high asking price
            taxes_fees=35000.0,
            far=0.8,  # Low FAR
            coverage=0.3,
            max_floors=2,
            efficiency_ratio=0.80,
            expected_sale_price_psm=3200.0,  # Low sale price
            construction_cost_psm=2500.0,  # High construction cost
            soft_cost_pct=0.20,
            profit_target_pct=0.25,
        )

        deal = LandDeal(inputs=inputs).compute_outputs()

        # Should have poor overall score
        assert deal.viability.overall_score == "red"
        assert deal.outputs.residual_land_value < deal.inputs.asking_price


class TestSensitivityAnalysis:
    """Test sensitivity analysis calculations."""

    def test_sales_down_sensitivity(self):
        """Test sales price reduction scenario."""
        inputs = LandInputs(
            site_name="Sensitivity Test",
            land_area_sqm=1000.0,
            asking_price=400000.0,
            far=1.5,
            coverage=0.4,
            max_floors=4,
            efficiency_ratio=0.85,
            expected_sale_price_psm=4000.0,
            construction_cost_psm=2000.0,
            soft_cost_pct=0.15,
            profit_target_pct=0.20,
        )

        deal = LandDeal(inputs=inputs).compute_outputs()

        # Sales down scenario should reduce residual value
        assert deal.sensitivity.sales_down_10pct < deal.sensitivity.base_residual
        assert deal.sensitivity.sales_impact < 0  # Negative impact

    def test_costs_up_sensitivity(self):
        """Test construction cost increase scenario."""
        inputs = LandInputs(
            site_name="Cost Sensitivity Test",
            land_area_sqm=1000.0,
            asking_price=400000.0,
            far=1.5,
            coverage=0.4,
            max_floors=4,
            efficiency_ratio=0.85,
            expected_sale_price_psm=4000.0,
            construction_cost_psm=2000.0,
            soft_cost_pct=0.15,
            profit_target_pct=0.20,
        )

        deal = LandDeal(inputs=inputs).compute_outputs()

        # Cost increase scenario should reduce residual value
        assert deal.sensitivity.costs_up_10pct < deal.sensitivity.base_residual
        assert deal.sensitivity.costs_impact < 0  # Negative impact


class TestBatchProcessing:
    """Test batch processing of multiple deals."""

    def test_batch_process_valid_deals(self):
        """Test processing multiple valid deals."""
        # Create test DataFrame
        test_data = pd.DataFrame(
            [
                {
                    "site_name": "Site A",
                    "land_area_sqm": 1000.0,
                    "asking_price": 400000.0,
                    "taxes_fees": 20000.0,
                    "far": 1.5,
                    "coverage": 0.4,
                    "max_floors": 4,
                    "efficiency_ratio": 0.85,
                    "expected_sale_price_psm": 4000.0,
                    "construction_cost_psm": 2000.0,
                    "soft_cost_pct": 0.15,
                    "profit_target_pct": 0.20,
                },
                {
                    "site_name": "Site B",
                    "land_area_sqm": 1200.0,
                    "asking_price": 480000.0,
                    "taxes_fees": 24000.0,
                    "far": 1.2,
                    "coverage": 0.35,
                    "max_floors": 3,
                    "efficiency_ratio": 0.87,
                    "expected_sale_price_psm": 3800.0,
                    "construction_cost_psm": 1900.0,
                    "soft_cost_pct": 0.14,
                    "profit_target_pct": 0.18,
                },
            ]
        )

        results = batch_process_deals(test_data)

        assert len(results) == 2
        assert "processing_status" in results.columns
        assert all(results["processing_status"] == "success")
        assert "overall_score" in results.columns
        assert "residual_land_value_num" in results.columns

    def test_batch_process_with_errors(self):
        """Test batch processing with invalid data."""
        # Create test DataFrame with invalid data
        test_data = pd.DataFrame(
            [
                {
                    "site_name": "Valid Site",
                    "land_area_sqm": 1000.0,
                    "asking_price": 400000.0,
                    "far": 1.5,
                    "coverage": 0.4,
                    "max_floors": 4,
                    "efficiency_ratio": 0.85,
                    "expected_sale_price_psm": 4000.0,
                    "construction_cost_psm": 2000.0,
                    "soft_cost_pct": 0.15,
                    "profit_target_pct": 0.20,
                },
                {
                    "site_name": "Invalid Site",
                    "land_area_sqm": -100.0,  # Invalid negative area
                    "asking_price": 400000.0,
                    "far": 1.5,
                    "coverage": 0.4,
                    "max_floors": 4,
                    "efficiency_ratio": 0.85,
                    "expected_sale_price_psm": 4000.0,
                    "construction_cost_psm": 2000.0,
                    "soft_cost_pct": 0.15,
                    "profit_target_pct": 0.20,
                },
            ]
        )

        results = batch_process_deals(test_data)

        assert len(results) == 2
        assert results.iloc[0]["processing_status"] == "success"
        assert "error:" in results.iloc[1]["processing_status"]
        assert results.iloc[1]["overall_score"] == "red"


class TestMarketIntegration:
    """Test market data integration and validation."""

    def test_market_data_loading(self):
        """Test loading market data for different cities."""
        toronto_data = load_market_data("toronto")
        assert toronto_data.city_key == "toronto"
        assert "land_comp_avg" in toronto_data.land_comps_psm
        assert "sale_price_avg" in toronto_data.sale_prices

        # Test fallback to default
        unknown_data = load_market_data("unknown_city")
        assert unknown_data.city_key == "default"

    def test_input_validation_against_market(self):
        """Test validation of inputs against market benchmarks."""
        test_inputs = {
            "expected_sale_price_psm": 3000.0,  # Below Toronto average
            "construction_cost_psm": 1500.0,  # Below Toronto average
            "soft_cost_pct": 0.25,  # High soft costs
        }

        warnings = validate_inputs_against_market(test_inputs, "toronto")

        # Should have warnings for out-of-range values
        assert len(warnings) > 0
        assert any("sale_price" in warning for warning in warnings.keys())


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_buildable_area(self):
        """Test deal with constraints resulting in zero buildable area."""
        inputs = LandInputs(
            site_name="Zero Buildable",
            land_area_sqm=100.0,  # Very small lot
            asking_price=100000.0,
            far=0.1,  # Very low FAR
            coverage=0.05,  # Very low coverage
            max_floors=1,
            efficiency_ratio=0.85,
            expected_sale_price_psm=4000.0,
            construction_cost_psm=2000.0,
            soft_cost_pct=0.15,
            profit_target_pct=0.20,
        )

        deal = LandDeal(inputs=inputs).compute_outputs()

        # Should handle gracefully without division by zero
        assert deal.outputs.gross_buildable_sqm >= 0
        assert deal.outputs.net_sellable_sqm >= 0

    def test_very_high_asking_price(self):
        """Test deal with asking price much higher than residual."""
        inputs = LandInputs(
            site_name="Overpriced Land",
            land_area_sqm=1000.0,
            asking_price=2000000.0,  # Very high asking price
            far=1.0,
            coverage=0.3,
            max_floors=3,
            efficiency_ratio=0.80,
            expected_sale_price_psm=3000.0,  # Low sale price
            construction_cost_psm=2500.0,  # High construction cost
            soft_cost_pct=0.20,
            profit_target_pct=0.25,
        )

        deal = LandDeal(inputs=inputs).compute_outputs()

        # Should be scored as unviable
        assert deal.viability.overall_score == "red"
        assert deal.viability.residual_score == "red"
        assert deal.outputs.asking_vs_residual > 0  # Asking exceeds residual


if __name__ == "__main__":
    pytest.main([__file__])
