# TerraFlow v2 – Real Estate Development Analysis

🎯 **Minimal, Clean, Modular** - A streamlined approach to real estate development analysis.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run dashboard/streamlit_app.py
```

## Features

- **Add Deal**: Input deal parameters and analyze with market benchmarks
- **Benchmarks**: View and compare market research data
- **Markets**: Dubai, Greece, Cyprus (v1 scope)

## Architecture

Clean layered architecture with zero circular imports:

```
dashboard/     → Streamlit UI (entry point, two pages)
  ├── streamlit_app.py    # Main entry with sys.path setup
  └── pages/
      ├── 1_Add_Deal.py   # Deal analysis workflow
      └── 2_Benchmarks.py # Market data visualization

core/          → Pure business logic
  └── calculations.py     # KPI calculations, no UI dependencies

utils/         → Infrastructure helpers  
  └── market_loader.py    # CSV loading, market filtering

data/          → Reference data
  └── reference/
      └── market_research.csv  # Market benchmarks (D/G/C only)

tests/         → Minimal test coverage
  ├── test_calculations.py
  └── test_market_loader.py
```

## Data Contracts

### Market CSV Schema
Required headers: `city_key,land_comp_min,land_comp_avg,land_comp_max,sale_price_min,sale_price_avg,sale_price_max,construction_cost_min,construction_cost_avg,construction_cost_max,soft_cost_pct_typical,absorption_rate,land_gdv_benchmark,profit_margin_benchmark,demand_score,liquidity_score,volatility_score,last_updated`

### Key Calculations
- **GFA** = land_area × FAR
- **NSA** = GFA × efficiency_ratio  
- **GDV** = NSA × expected_sale_price_per_sqm
- **Total Dev Cost** = Hard + Soft + Acquisition costs
- **Viability**: "✅ Viable" if GDV > Total Dev Cost × (1 + profit_target × 0.5)

## Import Rules

✅ **Allowed**: `dashboard/ → core/ & utils/`  
❌ **Forbidden**: `core/utils/ → dashboard/`, re-exports in `__init__.py`

Direct imports only:
```python
from utils.market_loader import load_market_benchmarks, filter_allowed_markets
from core.calculations import calculate_deal_metrics
```

## Session State

Single key only: `st.session_state['analysis']` (CalculatedOutputs object)

## Testing

```bash
pytest tests/ -q
```

## Troubleshooting

### Benchmarks Empty
**Problem**: "Market research data not found"  
**Solution**: Verify `data/reference/market_research.csv` exists with correct schema and `city_key` values: `dubai`, `greece`, `cyprus`

### Import Errors  
**Problem**: Module not found  
**Solution**: Run from repository root, ensure no circular imports

---

**Version**: 2.0 (minimal)  
**Markets**: Dubai, Greece, Cyprus  
**Architecture**: Zero circular imports, deterministic loading