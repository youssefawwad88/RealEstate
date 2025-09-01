"""
Test core calculations functionality.
"""
from core.calculations import calculate_deal_metrics


def test_calculations_outputs_have_nsa():
    """Test that calculations output includes NSA and key metrics."""
    outputs = calculate_deal_metrics(
        land_area_sqm=1500, 
        far=1.8, 
        efficiency_ratio=0.8,
        asking_price=750000, 
        taxes_and_fees=37500,
        expected_sale_price_per_sqm=4200, 
        construction_cost_per_sqm=2100,
        soft_cost_pct=0.16, 
        profit_target_pct=0.18,
        months_to_sell=18, 
        market_row={"absorption_rate": 18}
    )
    
    # Test NSA and acquisition metrics exist and are positive
    assert outputs.nsa_sqm > 0
    assert outputs.acq_cost_per_buildable_area > 0
    assert outputs.acq_cost_per_total_area > 0
    
    # Test basic calculation correctness
    expected_gfa = 1500 * 1.8  # land_area * FAR
    expected_nsa = expected_gfa * 0.8  # GFA * efficiency_ratio
    
    assert outputs.gfa_sqm == expected_gfa
    assert outputs.nsa_sqm == expected_nsa
    
    # Test acquisition calculations
    expected_acq_total = 750000 + 37500
    assert outputs.acq_total_cost == expected_acq_total
    
    # Test positive values for all metrics
    assert outputs.gdv > 0
    assert outputs.total_dev_cost > 0
    assert outputs.est_absorption_months > 0
    assert outputs.est_absorption_rate_per_month > 0


def test_calculations_with_market_fallback():
    """Test calculations with market data fallback."""
    # Test with no months_to_sell - should use market data
    outputs = calculate_deal_metrics(
        land_area_sqm=1000,
        far=2.0,
        efficiency_ratio=0.85,
        asking_price=500000,
        taxes_and_fees=25000,
        expected_sale_price_per_sqm=5000,
        construction_cost_per_sqm=2500,
        soft_cost_pct=0.15,
        profit_target_pct=0.20,
        months_to_sell=None,
        market_row={"absorption_rate": 24}
    )
    
    assert outputs.est_absorption_months == 24.0  # From market data
    
    # Test with no market data - should use default
    outputs_no_market = calculate_deal_metrics(
        land_area_sqm=1000,
        far=2.0,
        efficiency_ratio=0.85,
        asking_price=500000,
        taxes_and_fees=25000,
        expected_sale_price_per_sqm=5000,
        construction_cost_per_sqm=2500,
        soft_cost_pct=0.15,
        profit_target_pct=0.20,
        months_to_sell=None,
        market_row=None
    )
    
    assert outputs_no_market.est_absorption_months == 18.0  # Default fallback


def test_overall_score_logic():
    """Test overall viability scoring."""
    # Test viable deal
    viable_outputs = calculate_deal_metrics(
        land_area_sqm=1000,
        far=2.0,
        efficiency_ratio=0.8,
        asking_price=400000,  # Lower cost
        taxes_and_fees=20000,
        expected_sale_price_per_sqm=6000,  # High revenue
        construction_cost_per_sqm=2000,
        soft_cost_pct=0.15,
        profit_target_pct=0.15,
        months_to_sell=12
    )
    
    assert "✅ Viable" in viable_outputs.overall_score
    
    # Test borderline deal
    borderline_outputs = calculate_deal_metrics(
        land_area_sqm=1000,
        far=2.0,
        efficiency_ratio=0.8,
        asking_price=800000,  # High cost
        taxes_and_fees=40000,
        expected_sale_price_per_sqm=4000,  # Lower revenue
        construction_cost_per_sqm=2500,
        soft_cost_pct=0.20,
        profit_target_pct=0.20,
        months_to_sell=24
    )
    
    assert "⚠️ Borderline" in borderline_outputs.overall_score