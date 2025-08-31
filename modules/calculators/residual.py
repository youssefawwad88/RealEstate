"""
Pure functions for residual land value calculations.
No external dependencies, fully testable calculation logic.
"""

from typing import Tuple, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class DevelopmentCapacity:
    """Development capacity calculation results."""
    
    gross_buildable_sqm: float
    net_sellable_sqm: float
    limiting_factor: str  # "far" or "coverage"


@dataclass  
class FinancialResults:
    """Financial calculation results."""
    
    gdv: float
    hard_costs: float
    soft_costs: float
    total_dev_cost: float
    required_profit: float
    residual_land_value: float


@dataclass
class AcquisitionMetrics:
    """Land acquisition metrics."""
    
    total_acquisition_cost: float
    land_psm: float
    land_per_buildable: float
    land_pct_gdv: float
    asking_vs_residual: float
    breakeven_sale_price: float


def calculate_development_capacity(
    land_area_sqm: float,
    far: Optional[float],
    coverage: float,
    max_floors: int,
    efficiency_ratio: float
) -> DevelopmentCapacity:
    """
    Calculate maximum development capacity given site constraints.
    
    Args:
        land_area_sqm: Total land area in square meters
        far: Floor Area Ratio limit
        coverage: Maximum site coverage ratio (0-1)
        max_floors: Maximum number of floors
        efficiency_ratio: Net sellable / Gross area ratio (0-1)
    
    Returns:
        DevelopmentCapacity with buildable areas and limiting factor
    """
    # Calculate buildable area under different constraints
    buildable_by_coverage = land_area_sqm * coverage * max_floors
    
    if far is not None:
        buildable_by_far = land_area_sqm * far
        # Take the minimum (most restrictive)
        if buildable_by_far <= buildable_by_coverage:
            gross_buildable_sqm = buildable_by_far
            limiting_factor = "far"
        else:
            gross_buildable_sqm = buildable_by_coverage  
            limiting_factor = "coverage"
    else:
        # No FAR constraint, use coverage only
        gross_buildable_sqm = buildable_by_coverage  
        limiting_factor = "coverage"
    
    # Calculate net sellable area
    net_sellable_sqm = gross_buildable_sqm * efficiency_ratio
    
    return DevelopmentCapacity(
        gross_buildable_sqm=gross_buildable_sqm,
        net_sellable_sqm=net_sellable_sqm,
        limiting_factor=limiting_factor
    )


def calculate_gdv(net_sellable_sqm: float, sale_price_psm: float) -> float:
    """
    Calculate Gross Development Value.
    
    Args:
        net_sellable_sqm: Net sellable area in square meters
        sale_price_psm: Expected sale price per square meter
    
    Returns:
        Total GDV in currency units
    """
    return net_sellable_sqm * sale_price_psm


def calculate_development_costs(
    gross_buildable_sqm: float,
    construction_cost_psm: float,
    soft_cost_pct: float,
    financing_cost: float = 0.0
) -> Tuple[float, float, float]:
    """
    Calculate total development costs excluding land.
    
    Args:
        gross_buildable_sqm: Gross buildable area
        construction_cost_psm: Construction cost per square meter  
        soft_cost_pct: Soft costs as percentage of hard costs
        financing_cost: Additional financing costs
        
    Returns:
        Tuple of (hard_costs, soft_costs, total_dev_cost)
    """
    hard_costs = gross_buildable_sqm * construction_cost_psm
    soft_costs = hard_costs * soft_cost_pct
    total_dev_cost = hard_costs + soft_costs + financing_cost
    
    return hard_costs, soft_costs, total_dev_cost


def calculate_required_profit(gdv: float, profit_target_pct: float) -> float:
    """
    Calculate required developer profit.
    
    Args:
        gdv: Gross Development Value
        profit_target_pct: Target profit as percentage of GDV
        
    Returns:
        Required profit amount
    """
    return gdv * profit_target_pct


def calculate_residual_land_value(
    gdv: float,
    total_dev_cost: float,
    required_profit: float
) -> float:
    """
    Calculate residual land value using the residual method.
    
    Args:
        gdv: Gross Development Value
        total_dev_cost: Total development cost excluding land
        required_profit: Required developer profit
        
    Returns:
        Maximum affordable land price (residual value)
    """
    return gdv - total_dev_cost - required_profit


def calculate_acquisition_metrics(
    asking_price: float,
    taxes_fees: float,
    land_area_sqm: float,
    gross_buildable_sqm: float,
    gdv: float,
    residual_land_value: float,
    total_dev_cost: float,
    net_sellable_sqm: float
) -> AcquisitionMetrics:
    """
    Calculate land acquisition metrics and viability indicators.
    
    Args:
        asking_price: Land asking price
        taxes_fees: Transfer taxes and fees
        land_area_sqm: Total land area
        gross_buildable_sqm: Gross buildable area
        gdv: Gross Development Value
        residual_land_value: Calculated residual land value
        total_dev_cost: Total development cost
        net_sellable_sqm: Net sellable area
        
    Returns:
        AcquisitionMetrics with all calculated metrics
    """
    total_acquisition_cost = asking_price + taxes_fees
    land_psm = asking_price / land_area_sqm
    land_per_buildable = asking_price / gross_buildable_sqm if gross_buildable_sqm > 0 else 0
    land_pct_gdv = (total_acquisition_cost / gdv * 100) if gdv > 0 else 0
    asking_vs_residual = asking_price - residual_land_value
    breakeven_sale_price = (total_dev_cost + total_acquisition_cost) / net_sellable_sqm if net_sellable_sqm > 0 else 0
    
    return AcquisitionMetrics(
        total_acquisition_cost=total_acquisition_cost,
        land_psm=land_psm,
        land_per_buildable=land_per_buildable,
        land_pct_gdv=land_pct_gdv,
        asking_vs_residual=asking_vs_residual,
        breakeven_sale_price=breakeven_sale_price
    )


def calculate_comprehensive_residual(
    land_area_sqm: float,
    asking_price: float,
    taxes_fees: float,
    far: float,
    coverage: float,
    max_floors: int,
    efficiency_ratio: float,
    sale_price_psm: float,
    construction_cost_psm: float,
    soft_cost_pct: float,
    profit_target_pct: float,
    financing_cost: float = 0.0
) -> Tuple[DevelopmentCapacity, FinancialResults, AcquisitionMetrics]:
    """
    Comprehensive residual land value calculation with all metrics.
    
    This function combines all calculation steps into a single comprehensive analysis.
    
    Returns:
        Tuple of (DevelopmentCapacity, FinancialResults, AcquisitionMetrics)
    """
    # Step 1: Calculate development capacity
    capacity = calculate_development_capacity(
        land_area_sqm, far, coverage, max_floors, efficiency_ratio
    )
    
    # Step 2: Calculate GDV
    gdv = calculate_gdv(capacity.net_sellable_sqm, sale_price_psm)
    
    # Step 3: Calculate development costs
    hard_costs, soft_costs, total_dev_cost = calculate_development_costs(
        capacity.gross_buildable_sqm, construction_cost_psm, soft_cost_pct, financing_cost
    )
    
    # Step 4: Calculate required profit
    required_profit = calculate_required_profit(gdv, profit_target_pct)
    
    # Step 5: Calculate residual land value
    residual_land_value = calculate_residual_land_value(gdv, total_dev_cost, required_profit)
    
    # Step 6: Calculate acquisition metrics
    metrics = calculate_acquisition_metrics(
        asking_price, taxes_fees, land_area_sqm, capacity.gross_buildable_sqm,
        gdv, residual_land_value, total_dev_cost, capacity.net_sellable_sqm
    )
    
    # Package results
    financial_results = FinancialResults(
        gdv=gdv,
        hard_costs=hard_costs,
        soft_costs=soft_costs,
        total_dev_cost=total_dev_cost,
        required_profit=required_profit,
        residual_land_value=residual_land_value
    )
    
    return capacity, financial_results, metrics


def calculate_sensitivity_analysis(
    base_gdv: float,
    base_total_dev_cost: float,
    base_required_profit: float,
    net_sellable_sqm: float,
    sale_price_psm: float,
    hard_costs: float,
    soft_cost_pct: float,
    profit_target_pct: float,
    financing_cost: float = 0.0
) -> Dict[str, float]:
    """
    Calculate sensitivity analysis scenarios.
    
    Args:
        base_gdv: Base case GDV
        base_total_dev_cost: Base case total development cost
        base_required_profit: Base case required profit
        net_sellable_sqm: Net sellable area
        sale_price_psm: Base case sale price per sqm
        hard_costs: Base case hard costs
        soft_cost_pct: Soft cost percentage
        profit_target_pct: Profit target percentage
        financing_cost: Financing cost
        
    Returns:
        Dictionary with sensitivity scenario results
    """
    base_residual = base_gdv - base_total_dev_cost - base_required_profit
    
    # Sales price -10% scenario
    reduced_gdv = net_sellable_sqm * (sale_price_psm * 0.9)
    reduced_profit = reduced_gdv * profit_target_pct
    sales_down_residual = reduced_gdv - base_total_dev_cost - reduced_profit
    
    # Construction cost +10% scenario
    increased_hard_costs = hard_costs * 1.1
    increased_soft_costs = increased_hard_costs * soft_cost_pct
    increased_total_cost = increased_hard_costs + increased_soft_costs + financing_cost
    costs_up_residual = base_gdv - increased_total_cost - base_required_profit
    
    return {
        "base_residual": base_residual,
        "sales_down_10pct": sales_down_residual,
        "costs_up_10pct": costs_up_residual,
        "sales_impact": sales_down_residual - base_residual,
        "costs_impact": costs_up_residual - base_residual,
    }