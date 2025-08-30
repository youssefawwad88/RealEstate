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

BASE_DIR = Path(__file__).parent
PAGES_DIR = BASE_DIR / "pages"

pages = []
found, missing = [], []

def add_page(filename: str, title: str, icon: str):
    path = PAGES_DIR / filename
    if path.exists():
        pages.append(st.Page(str(path), title=title, icon=icon))
        found.append(filename)
    else:
        missing.append(filename)

# Register pages
add_page("0_Home.py", "Dashboard", "🏠")        # recommended home
add_page("1_Add_Deal.py", "Add Deal", "📝")
add_page("2_Pipeline.py", "Pipeline", "📊")
add_page("3_Benchmarks.py", "Benchmarks", "📈")
add_page("4_Configs_Viewer.py", "Configs", "⚙️")  # optional

# Log diagnostics (shows up in Cloud logs)
print(f"[Nav] Found pages: {found} | Missing pages: {missing}")

# Visible in UI too, in case of partial nav
if missing:
    st.warning(f"Some pages are missing on deploy: {', '.join(missing)}")

nav = st.navigation(pages)
nav.run()

# Main content will be provided by the selected page