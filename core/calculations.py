"""
Core calculation functions for TerraFlow v2.
Pure business logic with no UI dependencies.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class CalculatedOutputs:
    """Single result object with all calculated outputs."""
    gdv: float
    total_dev_cost: float
    residual_land_value: float
    land_pct_of_gdv: float
    breakeven_price_per_sqm: float
    overall_score: str
    
    # Area calculations
    gfa_sqm: float                 # Gross Floor Area = land_area * FAR
    nsa_sqm: float                 # Net Sellable Area = GFA * efficiency_ratio
    
    # Acquisition metrics
    acq_total_cost: float          # asking_price + taxes_fees
    acq_cost_per_total_area: float # acq_total_cost / land_area
    acq_cost_per_buildable_area: float  # acq_total_cost / gfa_sqm
    land_cost_per_nsa: float       # acq_total_cost / nsa_sqm
    
    # Absorption metrics
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
    """
    Calculate all deal metrics according to KPI formulas.
    
    KPI Formulas (source of truth):
    - GFA = land_area_sqm × FAR
    - NSA = GFA × efficiency_ratio
    - GDV = NSA × expected_sale_price_per_sqm
    - Hard costs = GFA × construction_cost_per_sqm
    - Soft costs = Hard × soft_cost_pct
    - Acquisition total = asking_price + taxes_and_fees
    - Total dev cost = Hard + Soft + Acquisition total
    - Breakeven $/sqm = Total dev cost / NSA
    - Residual land value = GDV - (Hard + Soft) - (GDV × profit_target_pct)
    - Land % of GDV = Acquisition total / GDV
    - Est. months = months_to_sell or market_row['absorption_rate'] or 18
    - Absorption / month (sqm) = NSA / Est. months
    """
    
    # Area calculations
    gfa_sqm = land_area_sqm * far
    nsa_sqm = gfa_sqm * efficiency_ratio
    
    # Revenue
    gdv = nsa_sqm * expected_sale_price_per_sqm
    
    # Costs
    hard_costs = gfa_sqm * construction_cost_per_sqm
    soft_costs = hard_costs * soft_cost_pct
    acq_total_cost = asking_price + taxes_and_fees
    total_dev_cost = hard_costs + soft_costs + acq_total_cost
    
    # Financial metrics
    breakeven_price_per_sqm = (total_dev_cost / nsa_sqm) if nsa_sqm > 0 else 0.0
    residual_land_value = gdv - (hard_costs + soft_costs) - (gdv * profit_target_pct)
    land_pct_of_gdv = (acq_total_cost / gdv) if gdv > 0 else 0.0
    
    # Acquisition metrics
    acq_cost_per_total_area = (acq_total_cost / land_area_sqm) if land_area_sqm > 0 else 0.0
    acq_cost_per_buildable_area = (acq_total_cost / gfa_sqm) if gfa_sqm > 0 else 0.0
    land_cost_per_nsa = (acq_total_cost / nsa_sqm) if nsa_sqm > 0 else 0.0
    
    # Absorption metrics
    if months_to_sell is not None:
        est_months = months_to_sell
    elif market_row and 'absorption_rate' in market_row:
        est_months = market_row['absorption_rate']
    else:
        est_months = 18.0  # default fallback
    
    est_abs_rate = (nsa_sqm / est_months) if est_months > 0 else 0.0
    
    # Overall viability score
    viable_threshold = total_dev_cost * (1 + profit_target_pct * 0.5)
    overall_score = "✅ Viable" if gdv > viable_threshold else "⚠️ Borderline"
    
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
        acq_cost_per_total_area=acq_cost_per_total_area,
        acq_cost_per_buildable_area=acq_cost_per_buildable_area,
        land_cost_per_nsa=land_cost_per_nsa,
        est_absorption_months=est_months,
        est_absorption_rate_per_month=est_abs_rate
    )