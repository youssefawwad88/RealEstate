# dashboard/pages/0_Home.py
import streamlit as st

st.title("🏗️ TerraFlow – Real Estate Development System")
st.caption("Transforming land acquisition analysis into data-driven decisions")

st.markdown("""
### Quick start
- **Add Deal:** Input a site to compute GDV, residual value, breakeven land price, and viability flags.
- **Pipeline:** Review saved deals, filter by city/date, and explore portfolio charts.
- **Benchmarks:** Compare city-level prices, costs, and health indicators.
""")

with st.expander("Health check", expanded=False):
    st.markdown("- Market data present: ✅ if `data/reference/market_research.csv` exists")
    st.markdown("- Writeable pipeline: ✅ if `data/processed/` is created at runtime")