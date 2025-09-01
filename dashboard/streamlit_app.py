"""
TerraFlow v2 - Streamlit Application Entry Point
Minimal, clean, modular architecture.
"""
import sys
import streamlit as st
from pathlib import Path

# Add repo root to sys.path once (deterministic imports)
repo_root = Path(__file__).parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# Page configuration
st.set_page_config(
    page_title="TerraFlow v2",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for wide layout and improved styling
st.markdown("""
<style>
/* widen the main block */
.block-container {max-width: 1500px; padding-top: 1rem; padding-bottom: 3rem;}
/* tighten vertical rhythm of forms */
.stTextInput, .stNumberInput, .stSelectbox {margin-bottom: 0.35rem;}
/* compact metrics */
[data-testid="stMetricValue"] {font-size: 1.4rem;}
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("TerraFlow v2")
st.sidebar.markdown("---")

pages = {
    "🏗️ Add Deal": "pages/1_Add_Deal.py", 
    "📊 Benchmarks": "pages/2_Benchmarks.py"
}

# Simple navigation info
st.sidebar.markdown("### Navigation")
st.sidebar.markdown("Use the pages above to:")
st.sidebar.markdown("- **Add Deal**: Input deal parameters and analyze")
st.sidebar.markdown("- **Benchmarks**: View market research data")

# Main content
st.title("🏗️ TerraFlow v2")
st.markdown("### Real Estate Development Analysis")

st.markdown("""
Welcome to TerraFlow v2 - a clean, minimal real estate development analysis tool.

**Available Markets:** Dubai, Greece, Cyprus

**Navigation:** Use the pages in the sidebar to get started.
""")

# System info
with st.expander("ℹ️ System Information"):
    st.code(f"""
Repository Root: {repo_root}
Python Path: {sys.path[0] if sys.path else 'Not set'}
Session State Keys: {list(st.session_state.keys())}
    """)