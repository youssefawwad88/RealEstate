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

# --- Navigation (robust + relative-to-app) ---
APP_DIR = Path(__file__).parent              # /.../dashboard
PAGES_DIR = APP_DIR / "pages"                # /.../dashboard/pages

# For diagnostics in cloud logs - only show in debug mode
DEBUG = False  # must be False in prod
if DEBUG:
    st.write(f"[Nav] APP_DIR={APP_DIR} | PAGES_DIR exists={PAGES_DIR.exists()} | Files={sorted([p.name for p in PAGES_DIR.glob('*.py')])}")

def add_page(filename: str, title: str, icon: str):
    """
    Register a page using a RELATIVE path (from the app file) to avoid
    Streamlit Cloud path resolution quirks.
    """
    rel_path = Path("pages") / filename          # e.g. "pages/0_Home.py"
    abs_path = PAGES_DIR / filename              # e.g. "/.../dashboard/pages/0_Home.py"
    if abs_path.exists():
        try:
            # IMPORTANT: give Streamlit the RELATIVE string
            pages.append(st.Page(str(rel_path), title=title, icon=icon))
            found.append(filename)
        except Exception as e:
            missing.append(f"{filename} (registration failed: {e})")
    else:
        missing.append(f"{filename} (not on disk)")

pages, found, missing = [], [], []

# Register pages (these filenames must match case-sensitively)
add_page("0_Home.py", "Dashboard", "🏠")
add_page("1_Add_Deal.py", "Add Deal", "📝")
add_page("2_Pipeline.py", "Pipeline", "📊")
add_page("3_Benchmarks.py", "Benchmarks", "📈")
add_page("4_Configs_Viewer.py", "Configs", "🗂️")

# Final navigation
nav = st.navigation(pages)
nav.run()

# Developer diagnostics (only visible to you)
if missing:
    with st.expander("⚠️ Navigation diagnostics"):
        st.write("Missing or failed:", missing)
        st.write("Found:", found)

# Main content will be provided by the selected page