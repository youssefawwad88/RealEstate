import streamlit as st
import pandas as pd
import os
import sys
from pathlib import Path

# Add project root to path - safe sys.path injection  
ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = str(Path(ROOT).parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.market_loader import load_market_benchmarks, filter_allowed_markets

st.header("📊 Benchmarks")

bench = load_market_benchmarks()
if bench.empty:
    st.warning(
        "Market research data not found.\n\n"
        "Expected file: `data/reference/market_research.csv`"
    )
else:
    # default to our three focus markets; allow user override
    all_cities = sorted(bench["city_key"].dropna().unique().tolist())
    default = [c for c in ["dubai","greece","cyprus"] if c in all_cities] or all_cities[:3]
    selected = st.multiselect("Choose markets", all_cities, default=default)
    view = filter_allowed_markets(bench, allowed=tuple(selected))
    if view.empty:
        st.info("No rows match your selection.")
    else:
        st.dataframe(view, use_container_width=True)

        # "3adi charts msh code": simple Streamlit charts (no custom styling)
        st.subheader("Market Comparison")
        st.bar_chart(view.set_index("city_key")[["sale_price_avg","construction_cost_avg"]])
        st.line_chart(view.set_index("city_key")[["absorption_rate"]])

