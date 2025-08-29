"""
Scoring and evaluation utility functions for TerraFlow system.
Handles deal scoring, risk assessment, and viability calculations.
"""

from typing import Dict, Any, Literal
import pandas as pd


def score_deal_viability(
    residual_land_value: float,
    asking_price: float,
    land_pct_gdv: float,
    breakeven_pct_market: float
) -> Dict[str, Any]:
    """
    Score deal viability based on key metrics.
    
    Args:
        residual_land_value: Calculated residual land value
        asking_price: Land asking price
        land_pct_gdv: Land cost as percentage of GDV
        breakeven_pct_market: Breakeven sale price as percentage of market
        
    Returns:
        Dictionary with scoring results and color coding
    """
    scores = {}
    
    # Score residual vs asking
    if residual_land_value > asking_price * 1.1:  # 10% buffer
        scores['residual_score'] = 'green'
        scores['residual_status'] = 'Healthy margin'
    elif residual_land_value > asking_price:
        scores['residual_score'] = 'yellow'  
        scores['residual_status'] = 'Marginal'
    else:
        scores['residual_score'] = 'red'
        scores['residual_status'] = 'Over budget'
    
    # Score land % of GDV (typical range 15-25%)
    if 15 <= land_pct_gdv <= 25:
        scores['land_pct_score'] = 'green'
        scores['land_pct_status'] = 'Within norms'
    elif 25 < land_pct_gdv <= 30:
        scores['land_pct_score'] = 'yellow'
        scores['land_pct_status'] = 'Above average'
    else:
        scores['land_pct_score'] = 'red'
        scores['land_pct_status'] = 'Too high'
    
    # Score breakeven vs market
    if breakeven_pct_market < 80:
        scores['breakeven_score'] = 'green'
        scores['breakeven_status'] = 'Good buffer'
    elif breakeven_pct_market < 85:
        scores['breakeven_score'] = 'yellow'
        scores['breakeven_status'] = 'Tight margin'
    else:
        scores['breakeven_score'] = 'red'
        scores['breakeven_status'] = 'High risk'
    
    # Overall score
    red_flags = sum(1 for s in scores.values() if s == 'red')
    yellow_flags = sum(1 for s in scores.values() if s == 'yellow')
    
    if red_flags == 0 and yellow_flags <= 1:
        scores['overall_score'] = 'green'
        scores['overall_status'] = 'Viable'
    elif red_flags == 0:
        scores['overall_score'] = 'yellow'
        scores['overall_status'] = 'Caution'
    else:
        scores['overall_score'] = 'red' 
        scores['overall_status'] = 'High risk'
    
    return scores


def get_color_indicator(score: Literal['green', 'yellow', 'red']) -> str:
    """
    Get emoji indicator for score color.
    
    Args:
        score: Color score ('green', 'yellow', 'red')
        
    Returns:
        Emoji string
    """
    color_map = {
        'green': '✅',
        'yellow': '⚠️',
        'red': '❌'
    }
    return color_map.get(score, '❓')


def calculate_sensitivity(
    base_value: float,
    sales_down_10pct: float = None,
    costs_up_10pct: float = None
) -> Dict[str, float]:
    """
    Calculate sensitivity scenarios.
    
    Args:
        base_value: Base residual land value
        sales_down_10pct: Optional pre-calculated sales down scenario
        costs_up_10pct: Optional pre-calculated costs up scenario
        
    Returns:
        Dictionary with sensitivity values
    """
    sensitivity = {'base': base_value}
    
    if sales_down_10pct is not None:
        sensitivity['sales_down_10pct'] = sales_down_10pct
        sensitivity['sales_impact'] = sales_down_10pct - base_value
        
    if costs_up_10pct is not None:
        sensitivity['costs_up_10pct'] = costs_up_10pct
        sensitivity['costs_impact'] = costs_up_10pct - base_value
        
    return sensitivity


def format_currency(amount: float, currency: str = '$') -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Numeric amount
        currency: Currency symbol
        
    Returns:
        Formatted currency string
    """
    if abs(amount) >= 1_000_000:
        return f"{currency}{amount/1_000_000:.1f}M"
    elif abs(amount) >= 1_000:
        return f"{currency}{amount/1_000:.0f}K"
    else:
        return f"{currency}{amount:,.0f}"