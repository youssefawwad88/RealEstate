# Land Evaluation Summary - TerraFlow System

## Overview
This document provides a comprehensive summary of the land evaluation inputs, outputs, and formulas used in the TerraFlow real estate development system for land acquisition analysis.

## Manual Inputs (Developer Provided)

### Site Physical Characteristics
| Input | Description | Unit | Example |
|-------|-------------|------|---------|
| `land_area_sqm` | Total land area | Square meters | 1,200 |
| `site_shape` | Regular/Irregular/Corner | Text | "Regular" |
| `frontage` | Street frontage width | Meters | 30 |
| `topography` | Flat/Sloped/Irregular | Text | "Flat" |
| `access` | Road access quality | Scale 1-5 | 4 |
| `visibility` | Site visibility rating | Scale 1-5 | 3 |

### Legal and Zoning Parameters
| Input | Description | Unit | Example |
|-------|-------------|------|---------|
| `ownership_type` | Freehold/Leasehold | Text | "Freehold" |
| `zoning` | Zoning classification | Text | "Mixed-use Residential" |
| `far` | Floor Area Ratio | Ratio | 1.5 |
| `coverage` | Maximum site coverage | Ratio | 0.4 |
| `height_limit` | Maximum building height | Floors | 4 |
| `setbacks_front` | Front setback requirement | Meters | 3 |
| `setbacks_side` | Side setback requirement | Meters | 2 |
| `parking_ratio` | Required parking spaces/unit | Ratio | 1.2 |
| `restrictions` | Additional zoning restrictions | Text | "None" |

### Market and Financial Assumptions
| Input | Description | Unit | Example |
|-------|-------------|------|---------|
| `efficiency_ratio` | Net sellable area / Gross area | Ratio | 0.85 |
| `product_type` | Apartment/Condo/Mixed | Text | "Condo" |
| `expected_sale_price_psm` | Expected sale price per sqm | $/sqm | 4,000 |
| `construction_cost_psm` | Construction cost per sqm | $/sqm | 2,000 |
| `soft_cost_pct` | Soft costs as % of hard costs | Percentage | 15% |
| `profit_target_pct` | Developer profit target | Percentage | 20% |

### Acquisition Terms
| Input | Description | Unit | Example |
|-------|-------------|------|---------|
| `asking_price` | Land asking price | $ | 600,000 |
| `taxes_fees` | Transfer taxes and fees | $ | 30,000 |
| `financing_cost` | Interest during construction | $ | 50,000 |
| `holding_period` | Development timeline | Months | 24 |

### Risk Assessment Factors
| Input | Description | Scale | Example |
|-------|-------------|-------|---------|
| `title_risk` | Title complexity risk | 1-5 | 2 |
| `rezoning_required` | Need for rezoning | Yes/No | No |
| `phasing_feasible` | Can be developed in phases | Yes/No | Yes |
| `exit_strategy` | Alternative exit options | Text | "Rental conversion possible" |

## Auto Inputs (System Retrieved)

### Market Comparables
| Data Source | Description | Update Frequency |
|-------------|-------------|------------------|
| `land_comps_psm` | Recent land sales per sqm | Monthly |
| `land_comps_buildable` | Land sales per buildable sqm | Monthly |
| `absorption_rate` | Sales velocity (units/month) | Quarterly |
| `market_sale_price_min` | Minimum recent sale price | Monthly |
| `market_sale_price_avg` | Average recent sale price | Monthly |
| `market_sale_price_max` | Maximum recent sale price | Monthly |

### Benchmarks and Standards
| Benchmark | Description | Industry Standard |
|-----------|-------------|-------------------|
| `construction_cost_benchmark` | Regional construction costs | Local data |
| `soft_cost_benchmark` | Typical soft cost percentage | 12-18% |
| `land_gdv_benchmark` | Normal land % of GDV | 15-25% |
| `profit_margin_benchmark` | Typical developer profit | 15-25% |

### Market Intelligence
| Data | Description | Source |
|------|-------------|--------|
| `demand_drivers` | Market demand factors | Market research |
| `liquidity_rating` | Market liquidity assessment | Historical data |
| `volatility_score` | Price volatility indicator | Statistical analysis |
| `competition_level` | Competitive environment | Market survey |

## Calculated Outputs

### Development Capacity
| Output | Formula | Description |
|--------|---------|-------------|
| `gross_buildable_sqm` | `min(land_area * FAR, land_area * coverage * max_floors)` | Maximum buildable area |
| `net_sellable_sqm` | `gross_buildable_sqm * efficiency_ratio` | Sellable area to customers |
| `total_units` | `net_sellable_sqm / avg_unit_size` | Estimated unit count |
| `parking_required` | `total_units * parking_ratio` | Required parking spaces |

### Financial Calculations
| Output | Formula | Description |
|--------|---------|-------------|
| `gdv` | `net_sellable_sqm * expected_sale_price_psm` | Gross Development Value |
| `hard_costs` | `gross_buildable_sqm * construction_cost_psm` | Construction costs |
| `soft_costs` | `hard_costs * soft_cost_pct` | Professional fees, permits |
| `total_dev_cost` | `hard_costs + soft_costs` | Total development cost excl. land |
| `required_profit` | `gdv * profit_target_pct` | Target developer profit |
| `residual_land_value` | `gdv - total_dev_cost - required_profit` | Maximum affordable land price |

### Acquisition Metrics
| Output | Formula | Description |
|--------|---------|-------------|
| `total_acquisition_cost` | `asking_price + taxes_fees + financing_cost` | Total land acquisition cost |
| `land_psm` | `asking_price / land_area_sqm` | Land price per square meter |
| `land_per_buildable` | `asking_price / gross_buildable_sqm` | Land cost per buildable sqm |
| `land_pct_gdv` | `total_acquisition_cost / gdv * 100` | Land as percentage of GDV |
| `asking_vs_residual` | `asking_price - residual_land_value` | Asking vs calculated value |

### Viability Indicators
| Output | Formula/Logic | Meaning |
|--------|---------------|---------|
| `breakeven_sale_price` | `(total_dev_cost + asking_price) / net_sellable_sqm` | Required sale price to break even |
| `breakeven_vs_market` | `breakeven_sale_price / market_sale_price_avg * 100` | Breakeven as % of market |
| `margin_of_safety` | `(market_sale_price_avg - breakeven_sale_price) / market_sale_price_avg` | Price cushion available |

## Risk Flags and Scoring

### Automated Flags
| Flag | Condition | Risk Level |
|------|-----------|------------|
| `overpaid_flag` | `asking_price > residual_land_value` | ❌ High |
| `land_pct_high` | `land_pct_gdv > 25%` | ⚠️ Medium |
| `tight_margins` | `breakeven_vs_market >= 85%` | ⚠️ Medium |
| `low_absorption` | `absorption_rate < market_avg` | ⚠️ Medium |
| `market_peak` | `current_prices > 95% of 5yr_max` | ⚠️ Medium |

### Color Coding System
| Color | Symbol | Criteria | Action |
|-------|---------|----------|--------|
| Green | ✅ | All metrics healthy | Proceed with confidence |
| Yellow | ⚠️ | 1-2 caution flags | Investigate further |
| Red | ❌ | Major red flags | High risk - reconsider |

## Sensitivity Analysis

### Key Scenarios
| Scenario | Impact On | Typical Range |
|----------|-----------|---------------|
| Sales price -10% | Residual land value | -15% to -25% |
| Construction cost +10% | Residual land value | -10% to -15% |
| Absorption -20% | Holding costs | +5% to +10% |
| Interest rate +2% | Financing cost | +3% to +8% |

### Stress Testing
| Test | Description | Pass/Fail Criteria |
|------|-------------|-------------------|
| Market downturn | Sales price -15%, costs +5% | Positive residual value |
| Construction overrun | Hard costs +20% | Margin of safety >10% |
| Extended timeline | Holding period +50% | Breakeven <90% market |

## Data Validation Rules

### Input Validation
| Field | Validation Rule | Error Message |
|-------|-----------------|---------------|
| `land_area_sqm` | > 0 | "Land area must be positive" |
| `far` | 0.1 to 10.0 | "FAR must be between 0.1 and 10.0" |
| `coverage` | 0.1 to 0.9 | "Coverage must be between 10% and 90%" |
| `efficiency_ratio` | 0.6 to 0.95 | "Efficiency ratio must be between 60% and 95%" |
| `profit_target_pct` | 0.05 to 0.50 | "Profit target must be between 5% and 50%" |

### Calculation Checks
| Check | Description | Warning Threshold |
|-------|-------------|-------------------|
| Buildable area | Verify FAR vs coverage constraints | Difference > 10% |
| Market prices | Compare to regional benchmarks | Deviation > 20% |
| Cost estimates | Validate against recent projects | Variance > 15% |

## Report Outputs

### Executive Summary
- Site viability rating (Green/Yellow/Red)
- Key financial metrics (GDV, residual value, land %)
- Primary risk factors
- Recommendation (Proceed/Caution/Pass)

### Detailed Analysis
- Full financial pro forma
- Sensitivity analysis table
- Comparable sales analysis
- Risk assessment matrix
- Timeline and milestone assumptions

### Supporting Data
- Market research summary
- Zoning compliance checklist
- Cost estimation breakdown
- Exit strategy options

This comprehensive system transforms scattered spreadsheet analysis into a structured, repeatable process that reduces risk and improves decision-making quality in land acquisition.