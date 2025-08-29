"""
TerraFlow Streamlit Dashboard
Main dashboard for land acquisition analysis and deal evaluation.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    from modules.land_acquisition import load_historical_data, get_acquisition_summary
    from utils.scoring import get_color_indicator, format_currency
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Make sure you're running from the project root directory")

# Page config
st.set_page_config(
    page_title="TerraFlow - Real Estate Development System",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header
st.title("🏗️ TerraFlow - Real Estate Development System")
st.markdown("**Transforming land acquisition analysis into data-driven decisions**")

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Select Analysis",
    ["Dashboard", "Land Acquisition", "Deal Analysis", "Comparison"]
)

if page == "Dashboard":
    st.header("📊 Portfolio Overview")
    
    # Load historical data
    try:
        df = load_historical_data()
        
        if not df.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Sites", len(df))
            
            with col2:
                total_value = df['asking_price'].sum() if 'asking_price' in df.columns else 0
                st.metric("Total Value", format_currency(total_value))
            
            with col3:
                avg_psm = df['asking_price'].sum() / df['land_area_sqm'].sum() if len(df) > 0 else 0
                st.metric("Avg Price/sqm", format_currency(avg_psm))
            
            with col4:
                st.metric("Last Updated", "Today")
            
            # Recent sites table
            st.subheader("Recent Acquisitions")
            display_cols = ['site_name', 'land_area_sqm', 'asking_price', 'zoning']
            available_cols = [col for col in display_cols if col in df.columns]
            
            if available_cols:
                recent_df = df[available_cols].tail(5)
                st.dataframe(recent_df, use_container_width=True)
            else:
                st.info("No data columns available for display")
                
        else:
            st.info("No acquisition data found. Start by adding land acquisition data in the notebook.")
            
    except Exception as e:
        st.error(f"Error loading data: {e}")

elif page == "Land Acquisition":
    st.header("🏞️ Land Acquisition Input")
    
    with st.form("land_inputs"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Site Information")
            site_name = st.text_input("Site Name", "New Site")
            land_area = st.number_input("Land Area (sqm)", min_value=100.0, value=1000.0)
            asking_price = st.number_input("Asking Price ($)", min_value=1000.0, value=500000.0)
            
            st.subheader("Zoning & Development")
            zoning = st.selectbox("Zoning", ["Residential", "Mixed-use", "Commercial"])
            far = st.number_input("Floor Area Ratio (FAR)", min_value=0.1, max_value=5.0, value=1.2)
            coverage = st.slider("Site Coverage", 0.1, 0.8, 0.4)
            
        with col2:
            st.subheader("Market Assumptions")
            sale_price_psm = st.number_input("Expected Sale Price ($/sqm)", min_value=1000.0, value=3500.0)
            construction_cost_psm = st.number_input("Construction Cost ($/sqm)", min_value=500.0, value=1800.0)
            soft_cost_pct = st.slider("Soft Cost %", 0.05, 0.30, 0.15)
            profit_target = st.slider("Profit Target %", 0.10, 0.40, 0.20)
            
            st.subheader("Other Costs")
            taxes_fees = st.number_input("Taxes & Fees ($)", min_value=0.0, value=25000.0)
        
        submitted = st.form_submit_button("Analyze Site")
        
        if submitted:
            st.success("Site analysis would be performed here!")
            st.info("Connect to deal_model.py for full residual value calculations")

elif page == "Deal Analysis":
    st.header("💰 Deal Financial Analysis")
    st.info("This section will show:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Key Metrics")
        st.write("- Gross Buildable Area")
        st.write("- Net Sellable Area")
        st.write("- Gross Development Value (GDV)")
        st.write("- Total Development Cost")
        st.write("- Residual Land Value")
        
    with col2:
        st.subheader("Viability Indicators")
        st.write("✅ Residual > Asking Price")
        st.write("⚠️ Land % of GDV")
        st.write("❌ Breakeven Sale Price")
        
    # Placeholder chart
    st.subheader("Cost Breakdown")
    categories = ['Land', 'Construction', 'Soft Costs', 'Profit']
    values = [25, 50, 15, 20]
    
    fig = px.pie(values=values, names=categories, title="Development Cost Structure")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Comparison":
    st.header("⚖️ Site Comparison")
    st.info("Side-by-side comparison of multiple land opportunities")
    
    # Mock comparison table
    comparison_data = {
        'Site': ['Downtown A', 'Suburb B', 'Industrial C'],
        'Price/sqm': ['$500', '$350', '$200'],
        'Residual Value': ['$480K', '$290K', '$150K'],
        'Land % GDV': ['22%', '18%', '25%'],
        'Status': ['✅ Viable', '✅ Viable', '⚠️ Marginal']
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    st.table(comparison_df)

# Footer
st.markdown("---")
st.markdown(
    "**TerraFlow** - Built for real estate developers | "
    "🚀 Powered by Python, Streamlit & AI"
)