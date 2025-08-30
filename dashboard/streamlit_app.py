"""
TerraFlow Streamlit Dashboard
Main entry point for the TerraFlow land acquisition dashboard.
"""

import streamlit as st

# Page config
st.set_page_config(
    page_title="TerraFlow – Land Acquisition",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("TerraFlow")
st.sidebar.markdown("**Modules**")
st.sidebar.page_link("pages/1_Add_Deal.py", label="Add Deal")
st.sidebar.page_link("pages/2_Pipeline.py", label="Pipeline")
st.sidebar.page_link("pages/3_Benchmarks.py", label="Benchmarks")
st.sidebar.page_link("pages/4_Configs_Viewer.py", label="Configs")

# Main content
st.title("TerraFlow – Land Acquisition")
st.write("Use the sidebar to navigate.")

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
    import pandas as pd
    from pathlib import Path
    import sys
    
    # Add project root to path
    project_root = Path(__file__).parent.parent
    sys.path.append(str(project_root))
    
    from utils.io import load_csv, get_data_dir
    from utils.scoring import format_currency
    
    acquisitions_path = get_data_dir() / "processed" / "acquisitions.csv"
    if acquisitions_path.exists():
        df = load_csv(acquisitions_path)
        
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
        
except Exception:
    st.info("Welcome! Start by adding your first deal.")