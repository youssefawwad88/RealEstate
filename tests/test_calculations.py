from core.calculations import calculate_deal_metrics

def test_calculations_outputs_have_nsa():
    out = calculate_deal_metrics(
        land_area_sqm=1500, far=1.8, efficiency_ratio=0.8,
        asking_price=750000, taxes_and_fees=37500,
        expected_sale_price_per_sqm=4200, construction_cost_per_sqm=2100,
        soft_cost_pct=0.16, profit_target_pct=0.18,
        months_to_sell=18, market_row={"absorption_rate": 18}
    )
    assert out.nsa_sqm > 0
    assert out.acq_cost_per_buildable_area > 0