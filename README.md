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

## Run Locally / Deploy

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/youssefawwad88/RealEstate.git
   cd RealEstate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r dev-requirements.txt
   ```

3. **Run the Streamlit dashboard:**
   ```bash
   streamlit run dashboard/streamlit_app.py
   ```

4. **Access the dashboard:**
   - Open your browser to `http://localhost:8501`
   - Use the sidebar to navigate between pages:
     - **Dashboard**: Overview and quick stats
     - **Add Deal**: Enter new land deals and analyze viability
     - **Pipeline**: View and filter your deal pipeline
     - **Benchmarks**: Explore market research and benchmarks
     - **Configs**: View configuration settings (optional)

---

## Run in Colab (with public URL)

You can run TerraFlow directly in Google Colab and make it publicly accessible:

### 1. Start Streamlit in headless mode:
```bash
!streamlit run dashboard/streamlit_app.py --server.headless true --server.port 8501 &
```

### 2. Create public tunnel with Cloudflared:
```bash
# Install cloudflared
!wget -q https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
!dpkg -i cloudflared-linux-amd64.deb

# Create tunnel (runs in background)
!cloudflared tunnel --url http://localhost:8501 --no-autoupdate &
```

The tunnel will provide a public `https://xxx.trycloudflare.com` URL that you can share.

**Alternative with LocalTunnel:**
```bash
!npm install -g localtunnel
!lt --port 8501 --subdomain myterraflow
```

*Note: LocalTunnel may require password authentication. Check the tunnel output for the password if prompted.*

**Runtime Requirements:**
Copy/paste works for a fresh Colab runtime with the requirements from `requirements.txt`.

---

### Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_dashboard.py -v

# Run with coverage
python -m pytest tests/ --cov=modules --cov=utils
```

### Deploy to Streamlit Cloud

1. Fork this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy from `dashboard/streamlit_app.py`
5. Set Python version to 3.9+ in advanced settings

### Deploy to Other Platforms

**Vercel:**
- Add `vercel.json` with Python runtime configuration
- Set build command to install dependencies
- Configure start command: `streamlit run dashboard/streamlit_app.py --server.port $PORT`

**Heroku:**
- Add `Procfile`: `web: streamlit run dashboard/streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
- Add `setup.sh` for Streamlit configuration
- Ensure Python version 3.9+ in `runtime.txt`

**Docker:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "dashboard/streamlit_app.py"]
```

---

## Dashboard Features

### 🏞️ Add Deal
- Enter site information (name, area, asking price, zoning)
- Configure development parameters (FAR, coverage, efficiency)
- Set market assumptions (sale price, construction costs, profit targets)
- Analyze deal viability with real-time calculations
- View color-coded viability flags:
  - 🟢 Green: Viable deals (good land % GDV, reasonable breakeven)
  - 🟡 Yellow: Marginal deals (need attention)
  - 🔴 Red: Not recommended (high risk)
- Save deals to pipeline

### 📊 Pipeline
- View all deals in filterable table
- Filter by city, date range, and viability score
- See portfolio metrics and deal distribution
- Download pipeline data as CSV
- Analyze deals with scatter plots and charts

### 📊 Benchmarks
- Explore market research data by city
- View pricing benchmarks (land, sale prices, construction costs)
- Compare market health indicators (demand, liquidity, volatility)
- Multi-city comparison charts
- Export market data for external analysis

### ⚙️ Configs Viewer
- View system configuration files (optional)
- Browse country-specific settings
- Explore zoning regulations and financial parameters
- Export configurations as JSON or YAML

---

---

## Troubleshooting

### Import Error
**Problem**: `ImportError` when running the application or "module not found" errors.

**Solution**: Make sure you run `streamlit run` from the repo root directory, and that `utils/market_loader.py` exists. If you changed folders, ensure `__init__.py` files exist in the `utils/` and `core/` directories.

```bash
# Make sure you're in the project root
cd /path/to/RealEstate
streamlit run dashboard/streamlit_app.py
```

### Benchmarks Empty
**Problem**: "Market research data not found" or benchmarks page shows no data.

**Solution**: Create or verify `data/reference/market_research.csv` exists with the correct format. Keep `city_key` values exactly as: `dubai`, `greece`, `cyprus`.

```csv
city_key,land_comp_min,land_comp_avg,land_comp_max,sale_price_min,sale_price_avg,sale_price_max,construction_cost_min,construction_cost_avg,construction_cost_max,soft_cost_pct_typical,absorption_rate,land_gdv_benchmark,profit_margin_benchmark,demand_score,liquidity_score,volatility_score,last_updated
dubai,300,500,900,4500,6000,8500,1800,2200,3000,0.16,18,22,18,5,5,3,2025-08-31
greece,120,250,400,2200,3200,4200,1200,1500,2000,0.14,24,20,15,4,3,3,2025-08-31
cyprus,150,280,450,2600,3600,4400,1300,1600,2100,0.15,22,20,15,3,3,2,2025-08-31
```

### KPIs Missing
**Problem**: UI crashes when analyzing deals, or missing NSA/acquisition cost KPIs.

**Solution**: The `CalculatedOutputs` must include `.nsa_sqm` and related fields. If the UI crashes, pull the latest version and ensure you're using the new `core/calculations.py` module.

### New KPI Definitions (Real Estate Guidance)

- **NSA (Net Sellable Area)** = GFA × Efficiency. GFA = Land Area × FAR. Efficiency typically 70–85% for residential (common areas, cores, etc.).
- **Acquisition cost per total area** = (Land price + taxes/fees) ÷ Land area.
- **Acquisition cost per buildable area** = (Land price + taxes/fees) ÷ GFA (this is the most compared metric across sites).
- **Land cost per NSA** = (Land price + taxes/fees) ÷ NSA (tighter lens on saleable economics).
- **Estimated absorption rate** = NSA ÷ months to sell (or use market benchmark months if you don't input it).

These five KPIs are essential to compare sites apples-to-apples in Dubai, Greece, and Cyprus.

### "Show Market Summary" Button Failed
**Problem**: The button crashes or shows no data.

**Solution**: This was caused by a missing `filter_allowed_markets` function. After implementing the tasks above and relaunching from the repo root, this button should work and show charts + a filtered table.

---

## Data Structure

### Input Data Files

**Market Research** (`data/processed/market_research.csv`):
```csv
city_key,land_comp_avg,sale_price_avg,construction_cost_avg,demand_score,liquidity_score,...
toronto,500,5200,2200,5,4,...
vancouver,400,6000,2400,5,3,...
```

**Acquisitions** (`data/processed/acquisitions.csv`):
- Populated automatically when deals are saved from Add Deal page
- Contains all deal inputs and calculated outputs
- Used by Pipeline page for filtering and analysis

### Configuration Files (Optional)

```
configs/
├── UAE/
│   ├── country.yml      # Country-specific settings
│   ├── finance.yml      # Lending and cost parameters  
│   ├── zoning.yml       # Zoning regulations
│   └── market.yml       # Market data sources
├── JO/
└── default/
    └── global.yml       # Global defaults
```

---

## Collaboration Rules
- Keep core logic in `/modules` & `/utils`
- Notebooks are orchestration only
- All new functions need type hints, docstrings, unit tests
- Data:
  - `/data/raw/` is ignored
  - `/data/processed/` is tracked