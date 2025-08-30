"""
TerraFlow Dashboard Home Page
Shows overview statistics and quick navigation.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from utils.io import load_csv, get_data_dir
    from utils.scoring import format_currency
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Make sure you're running from the project root directory")

st.title("TerraFlow – Land Acquisition")

st.markdown("""
### Welcome to TerraFlow

TerraFlow is your comprehensive land acquisition analysis platform. Use the navigation on the left to:

- **Add Deal**: Enter new land deals and analyze their viability
- **Pipeline**: View and manage your deal pipeline
- **Benchmarks**: Explore market research and benchmarks
- **Configs**: View configuration settings

Get started by adding a new deal or reviewing your existing pipeline.
""")

# Quick stats if data exists
try:
    acquisitions_path = get_data_dir() / "processed" / "acquisitions.csv"
    if acquisitions_path.exists():
        df = load_csv(acquisitions_path)
        
        st.subheader("📊 Quick Stats")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Deals", len(df))
        with col2:
            if 'asking_price' in df.columns:
                total_value = df['asking_price'].sum()
                st.metric("Total Value", format_currency(total_value))
        with col3:
            if 'site_name' in df.columns:
                st.metric("Active Sites", df['site_name'].nunique())
    else:
        st.info("No deals yet. Start by adding your first deal!")
        
except Exception as e:
    st.info("Welcome! Start by adding your first deal.")
    st.write(f"Debug: {e}")