from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class CalculatedOutputs:
    gdv: float
    total_dev_cost: float
    residual_land_value: float
    land_pct_of_gdv: float
    breakeven_price_per_sqm: float
    overall_score: str
    # NEW fields required by UI / business
    gfa_sqm: float                 # Gross Floor Area = land_area * FAR
    nsa_sqm: float                 # Net Sellable Area = GFA * efficiency_ratio
    acq_total_cost: float          # asking_price + taxes_fees (simplified)
    acq_cost_per_total_area: float # acq_total_cost / land_area
    acq_cost_per_buildable_area: float  # acq_total_cost / gfa_sqm
    land_cost_per_nsa: float       # acq_total_cost / nsa_sqm
    est_absorption_months: float   # from inputs; fallback to market benchmark
    est_absorption_rate_per_month: float  # nsa_sqm / months

def calculate_deal_metrics(
    *,
    land_area_sqm: float,
    far: float,
    efficiency_ratio: float,  # e.g., 0.80
    asking_price: float,
    taxes_and_fees: float,
    expected_sale_price_per_sqm: float,
    construction_cost_per_sqm: float,
    soft_cost_pct: float,     # e.g., 0.16
    profit_target_pct: float, # e.g., 0.18
    months_to_sell: Optional[float],
    market_row: Optional[Dict] = None
) -> CalculatedOutputs:
    # areas
    gfa_sqm = max(0.0, land_area_sqm * far)
    nsa_sqm = max(0.0, gfa_sqm * efficiency_ratio)

    # revenue (GDV)
    gdv = nsa_sqm * expected_sale_price_per_sqm

    # costs
    hard_costs = gfa_sqm * construction_cost_per_sqm
    soft_costs = hard_costs * soft_cost_pct
    acq_total_cost = asking_price + taxes_and_fees
    total_dev_cost = hard_costs + soft_costs + acq_total_cost

    # targets / breakeven
    breakeven_price_per_sqm = (total_dev_cost / nsa_sqm) if nsa_sqm > 0 else 0.0
    residual_land_value = gdv - (hard_costs + soft_costs) - (gdv * profit_target_pct)
    land_pct_of_gdv = (acq_total_cost / gdv) if gdv > 0 else 0.0

    # absorption
    bench_months = None
    if market_row and "absorption_rate" in market_row and market_row["absorption_rate"] is not None:
        # CSV stores "absorption_rate" (months to sell) or rate; assume "months" as per your form
        bench_months = float(market_row["absorption_rate"])
    est_months = float(months_to_sell) if months_to_sell else (bench_months or 18.0)
    est_abs_rate = (nsa_sqm / est_months) if est_months > 0 else 0.0

    # simple viability flag (keep your real logic if you had it)
    overall_score = "✅ Viable" if gdv > total_dev_cost * (1 + profit_target_pct * 0.5) else "⚠️ Borderline"

    return CalculatedOutputs(
        gdv=gdv,
        total_dev_cost=total_dev_cost,
        residual_land_value=residual_land_value,
        land_pct_of_gdv=land_pct_of_gdv,
        breakeven_price_per_sqm=breakeven_price_per_sqm,
        overall_score=overall_score,
        gfa_sqm=gfa_sqm,
        nsa_sqm=nsa_sqm,
        acq_total_cost=acq_total_cost,
        acq_cost_per_total_area=(acq_total_cost / land_area_sqm) if land_area_sqm > 0 else 0.0,
        acq_cost_per_buildable_area=(acq_total_cost / gfa_sqm) if gfa_sqm > 0 else 0.0,
        land_cost_per_nsa=(acq_total_cost / nsa_sqm) if nsa_sqm > 0 else 0.0,
        est_absorption_months=est_months,
        est_absorption_rate_per_month=est_abs_rate
    )