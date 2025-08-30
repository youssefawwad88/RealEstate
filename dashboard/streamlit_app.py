"""
TerraFlow Streamlit Dashboard
Main entry point for the TerraFlow land acquisition dashboard.
"""

import streamlit as st
from pathlib import Path

# Page config
st.set_page_config(
    page_title="TerraFlow – Land Acquisition",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Navigation with absolute paths
pages = [
    st.Page(str(Path(__file__).parent/"pages"/"0_Home.py"), title="Dashboard", icon="🏠"),
    st.Page(str(Path(__file__).parent/"pages"/"1_Add_Deal.py"), title="Add Deal", icon="📝"),
    st.Page(str(Path(__file__).parent/"pages"/"2_Pipeline.py"), title="Pipeline", icon="📊"),
    st.Page(str(Path(__file__).parent/"pages"/"3_Benchmarks.py"), title="Benchmarks", icon="📈"),
    st.Page(str(Path(__file__).parent/"pages"/"4_Configs_Viewer.py"), title="Configs", icon="⚙️"),
]
nav = st.navigation(pages)
nav.run()

# Main content will be provided by the selected page