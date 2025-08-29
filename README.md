# TerraFlow – Real Estate Development System

## Mission
TerraFlow is a modular, developer-grade system that transforms the **manual work of land acquisition analysis** into a structured, repeatable, data-driven workflow.  

Built by combining:
- 20+ years of professional land development experience
- Clean Python engineering (Colab + GitHub + Streamlit)

The system begins at **land acquisition** and will grow into a full development engine.

---

## Why This Exists
Developers often evaluate land with gut instinct or scattered spreadsheets.  
This leads to:
- Overpaying for land
- Missing zoning constraints
- Ignoring real costs & profit thresholds
- Poor comparability between sites

**This system fixes that.**

- Inputs: manual data from developer (site details, zoning, costs, sales price assumptions)  
- Auto-calculated: buildable area, GDV, costs, residual land value, breakeven sales price, land % of GDV, warning flags  
- Outputs: clear viability indicators, side-by-side land comparison

---

## Phase 1 – Land Acquisition Module
- **Manual Inputs (developer fills in):**
  - Land: area, shape, frontage, topography, access, visibility
  - Legal/zoning: ownership type, zoning category, FAR, coverage, height limits, setbacks, parking, restrictions
  - Market assumptions: efficiency ratio, product type, expected sales price/sqm, construction cost/sqm, soft cost %, developer profit target
  - Acquisition terms: asking price, taxes, fees, financing assumptions (if any)
  - Qualitative risks: title risks, rezoning need, phasing feasibility, exit strategies

- **AUTO Inputs (pulled from research db):**
  - Land comparables ($/sqm, $/buildable sqm)
  - Market sale price averages (min, max, average)
  - Absorption/sales velocity
  - Benchmarks (construction cost, soft cost %, land % of GDV norm)
  - Market notes (demand drivers, liquidity, volatility)

- **Outputs (system calculates):**
  - Gross buildable sqm = min(land_area*FAR, land_area*coverage*max_floors)
  - Net sellable sqm = GFA * efficiency
  - GDV = NSA * expected sale price
  - Costs (hard, soft, TDC excl. land)
  - Required profit (GDV * profit target %)
  - Residual land value = GDV – TDC excl. land – required profit
  - Acquisition totals: price + taxes + fees
  - Unit metrics: land_psm, acq_psm, per_buildable
  - Land % of GDV
  - Breakeven sale price vs market
  - Flags: asking > residual, land % out of norm, breakeven ≥ 85% of market
  - Sensitivities: residual if sales −10%, residual if costs +10%

- **Outputs should be color-coded in dashboard:**
  - ✅ Green if healthy
  - ⚠️ Yellow if marginal
  - ❌ Red if unviable

---

## Roadmap (Modules)
1. Land Acquisition ✅
2. Feasibility Analysis (financial modeling, risks)
3. Zoning & Permits (tracking approvals)
4. Development Planning (budget, vendors, schedule)
5. Marketing & Sales (CRM, listings, campaigns)
6. Asset Tracking (revenue, maintenance, resale)
7. Dashboard (end-to-end KPIs)

---

## Tech Stack
- Python 3.11 (Colab-friendly)
- Pydantic (data models)
- Pandas/Numpy (analysis)
- Streamlit (dashboard UI)
- GitHub (source control + Copilot Agent)
- Vercel/Streamlit Cloud (deployment)

---

## Collaboration Rules
- Keep core logic in `/modules` & `/utils`
- Notebooks are orchestration only
- All new functions need type hints, docstrings, unit tests
- Data:
  - `/data/raw/` is ignored
  - `/data/processed/` is tracked