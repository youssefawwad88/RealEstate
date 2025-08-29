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
    from modules.deal_model import create_deal_from_dict, batch_process_deals, LandInputs
    from modules.market_lookup import load_market_data, get_available_cities, get_market_summary
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
    ["Dashboard", "Land Acquisition", "Deal Analysis", "Comparison", "Market Research"]
)

if page == "Dashboard":
    st.header("📊 Portfolio Overview")
    
    # Load historical data
    try:
        df = load_historical_data()
        
        if not df.empty:
            # Process deals if not already processed
            if 'overall_score' not in df.columns:
                with st.spinner("Processing deals..."):
                    df = batch_process_deals(df)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Sites", len(df))
            
            with col2:
                total_value = df['asking_price'].sum() if 'asking_price' in df.columns else 0
                st.metric("Total Value", format_currency(total_value))
            
            with col3:
                if 'residual_land_value_num' in df.columns:
                    avg_residual = df['residual_land_value_num'].mean()
                    st.metric("Avg Residual Value", format_currency(avg_residual))
                else:
                    st.metric("Avg Residual Value", "N/A")
            
            with col4:
                if 'overall_score' in df.columns:
                    viable_count = (df['overall_score'] == 'green').sum()
                    st.metric("Viable Deals", f"{viable_count}/{len(df)}")
                else:
                    st.metric("Viable Deals", "0/0")
            
            # Recent sites table with analysis results
            st.subheader("Recent Acquisitions")
            display_cols = ['site_name', 'asking_price', 'residual_land_value', 'land_pct_gdv', 'overall_status']
            available_cols = [col for col in display_cols if col in df.columns]
            
            if available_cols:
                recent_df = df[available_cols].tail(10)
                
                # Format the display
                if 'asking_price' in recent_df.columns:
                    recent_df['asking_price'] = recent_df['asking_price'].apply(lambda x: format_currency(x) if pd.notna(x) else 'N/A')
                if 'residual_land_value' in recent_df.columns:
                    recent_df['residual_land_value'] = recent_df['residual_land_value'].apply(lambda x: x if isinstance(x, str) else format_currency(float(x)) if pd.notna(x) else 'N/A')
                if 'land_pct_gdv' in recent_df.columns:
                    recent_df['land_pct_gdv'] = recent_df['land_pct_gdv'].apply(lambda x: f"{float(x):.1f}%" if pd.notna(x) and not isinstance(x, str) else x if isinstance(x, str) else 'N/A')
                
                st.dataframe(recent_df, use_container_width=True)
                
                # Portfolio visualization
                if 'overall_score' in df.columns:
                    st.subheader("Portfolio Health")
                    score_counts = df['overall_score'].value_counts()
                    
                    colors = {'green': '#00D4AA', 'yellow': '#FFD700', 'red': '#FF6B6B'}
                    fig = px.pie(
                        values=score_counts.values,
                        names=score_counts.index,
                        title="Deal Viability Distribution",
                        color=score_counts.index,
                        color_discrete_map=colors
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.info("No processed data columns available for display")
                
        else:
            st.info("No acquisition data found. Start by adding land acquisition data in the notebook.")
            
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Try running the land acquisition notebook first to generate data.")

elif page == "Land Acquisition":
    st.header("🏞️ Land Acquisition Input")
    
    # Market selection
    col1, col2 = st.columns([1, 2])
    with col1:
        available_cities = get_available_cities()
        selected_city = st.selectbox("Market", available_cities, index=0)
    
    with col2:
        if st.button("Show Market Summary"):
            market_summary = get_market_summary(selected_city)
            st.json(market_summary)
    
    with st.form("land_inputs"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Site Information")
            site_name = st.text_input("Site Name", "New Site Analysis")
            land_area = st.number_input("Land Area (sqm)", min_value=100.0, value=1500.0)
            asking_price = st.number_input("Asking Price ($)", min_value=1000.0, value=750000.0)
            taxes_fees = st.number_input("Taxes & Fees ($)", min_value=0.0, value=37500.0)
            
            st.subheader("Zoning & Development")
            zoning = st.selectbox("Zoning", ["Residential", "Mixed-use", "Commercial", "Industrial"])
            far = st.number_input("Floor Area Ratio (FAR)", min_value=0.1, max_value=5.0, value=1.8)
            coverage = st.slider("Site Coverage", 0.1, 0.8, 0.45)
            max_floors = st.number_input("Max Floors", min_value=1, max_value=20, value=5)
            efficiency_ratio = st.slider("Efficiency Ratio", 0.6, 0.95, 0.85)
            
        with col2:
            st.subheader("Market Assumptions")
            sale_price_psm = st.number_input("Expected Sale Price ($/sqm)", min_value=1000.0, value=4200.0)
            construction_cost_psm = st.number_input("Construction Cost ($/sqm)", min_value=500.0, value=2100.0)
            soft_cost_pct = st.slider("Soft Cost %", 0.05, 0.30, 0.16)
            profit_target = st.slider("Profit Target %", 0.10, 0.40, 0.20)
            
            st.subheader("Additional Costs")
            financing_cost = st.number_input("Financing Cost ($)", min_value=0.0, value=45000.0)
            holding_period = st.number_input("Holding Period (months)", min_value=1, max_value=60, value=30)
        
        submitted = st.form_submit_button("🔍 Analyze Deal", use_container_width=True)
        
        if submitted:
            # Create deal inputs
            deal_inputs = {
                'site_name': site_name,
                'land_area_sqm': float(land_area),
                'asking_price': float(asking_price),
                'taxes_fees': float(taxes_fees),
                'zoning': zoning,
                'far': float(far),
                'coverage': float(coverage),
                'max_floors': int(max_floors),
                'efficiency_ratio': float(efficiency_ratio),
                'expected_sale_price_psm': float(sale_price_psm),
                'construction_cost_psm': float(construction_cost_psm),
                'soft_cost_pct': float(soft_cost_pct),
                'profit_target_pct': float(profit_target),
                'financing_cost': float(financing_cost),
                'holding_period_months': int(holding_period)
            }
            
            try:
                # Analyze the deal
                deal = create_deal_from_dict(deal_inputs)
                
                # Show results
                st.success("✅ Analysis Complete!")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Residual Land Value", format_currency(deal.outputs.residual_land_value))
                    st.metric("Land % of GDV", f"{deal.outputs.land_pct_gdv:.1f}%")
                
                with col2:
                    st.metric("GDV", format_currency(deal.outputs.gdv))
                    st.metric("Total Dev Cost", format_currency(deal.outputs.total_dev_cost))
                
                with col3:
                    st.metric("Breakeven Price/sqm", format_currency(deal.outputs.breakeven_sale_price))
                    st.metric("Overall Score", f"{get_color_indicator(deal.viability.overall_score)} {deal.viability.overall_status}")
                
                # Detailed results
                with st.expander("📊 Detailed Analysis"):
                    st.json({
                        'Development Capacity': {
                            'Gross Buildable (sqm)': deal.outputs.gross_buildable_sqm,
                            'Net Sellable (sqm)': deal.outputs.net_sellable_sqm,
                        },
                        'Financial Metrics': {
                            'GDV': deal.outputs.gdv,
                            'Hard Costs': deal.outputs.hard_costs,
                            'Soft Costs': deal.outputs.soft_costs,
                            'Required Profit': deal.outputs.required_profit,
                        },
                        'Viability Scores': {
                            'Residual vs Asking': deal.viability.residual_status,
                            'Land % Score': deal.viability.land_pct_status,
                            'Breakeven Risk': deal.viability.breakeven_status,
                        },
                        'Sensitivity Analysis': {
                            'Base Case': deal.sensitivity.base_residual,
                            'Sales -10%': deal.sensitivity.sales_down_10pct,
                            'Costs +10%': deal.sensitivity.costs_up_10pct,
                        }
                    })
                
            except Exception as e:
                st.error(f"Analysis failed: {e}")

elif page == "Deal Analysis":
    st.header("💰 Deal Financial Analysis")
    
    # Load and display processed deals
    try:
        df = load_historical_data()
        
        if not df.empty:
            if 'overall_score' not in df.columns:
                with st.spinner("Processing deals..."):
                    df = batch_process_deals(df)
            
            # Deal selector
            if 'site_name' in df.columns:
                selected_site = st.selectbox("Select Deal", df['site_name'].tolist())
                
                if selected_site:
                    deal_row = df[df['site_name'] == selected_site].iloc[0]
                    
                    # Create deal for analysis
                    try:
                        deal_dict = deal_row.to_dict()
                        deal = create_deal_from_dict(deal_dict)
                        
                        # Financial breakdown chart
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Cost Breakdown")
                            categories = ['Land', 'Construction', 'Soft Costs', 'Profit']
                            values = [
                                deal.outputs.total_acquisition_cost,
                                deal.outputs.hard_costs,
                                deal.outputs.soft_costs,
                                deal.outputs.required_profit
                            ]
                            
                            fig = px.pie(
                                values=values, 
                                names=categories, 
                                title="Development Cost Structure"
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            st.subheader("Key Metrics")
                            
                            # Waterfall chart data
                            waterfall_data = {
                                'Metric': ['GDV', 'Hard Costs', 'Soft Costs', 'Profit', 'Residual Land Value'],
                                'Value': [
                                    deal.outputs.gdv,
                                    -deal.outputs.hard_costs,
                                    -deal.outputs.soft_costs,
                                    -deal.outputs.required_profit,
                                    deal.outputs.residual_land_value
                                ]
                            }
                            
                            fig = go.Figure(go.Waterfall(
                                name="Deal Analysis",
                                orientation="v",
                                measure=["absolute", "relative", "relative", "relative", "total"],
                                x=waterfall_data['Metric'],
                                y=waterfall_data['Value'],
                                text=[format_currency(v) for v in waterfall_data['Value']],
                                textposition="outside"
                            ))
                            
                            fig.update_layout(title="Financial Waterfall", showlegend=False)
                            st.plotly_chart(fig, use_container_width=True)
                        
                        # Sensitivity analysis
                        st.subheader("📈 Sensitivity Analysis")
                        
                        scenarios = ['Base Case', 'Sales -10%', 'Costs +10%']
                        residuals = [
                            deal.sensitivity.base_residual,
                            deal.sensitivity.sales_down_10pct,
                            deal.sensitivity.costs_up_10pct
                        ]
                        
                        fig = px.bar(
                            x=scenarios,
                            y=residuals,
                            title="Residual Land Value Scenarios",
                            labels={'x': 'Scenario', 'y': 'Residual Value ($)'}
                        )
                        
                        # Add asking price line
                        fig.add_hline(
                            y=deal.inputs.asking_price,
                            line_dash="dash",
                            line_color="red",
                            annotation_text="Asking Price"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                    except Exception as e:
                        st.error(f"Could not analyze deal: {e}")
            else:
                st.info("No deals found with site names")
        else:
            st.info("No deals available for analysis")
    
    except Exception as e:
        st.error(f"Error loading deals: {e}")

elif page == "Comparison":
    st.header("⚖️ Site Comparison")
    
    try:
        df = load_historical_data()
        
        if not df.empty:
            if 'overall_score' not in df.columns:
                with st.spinner("Processing deals for comparison..."):
                    df = batch_process_deals(df)
            
            # Comparison table
            comparison_cols = [
                'site_name', 'asking_price', 'residual_land_value_num', 
                'land_pct_gdv_num', 'overall_score', 'overall_status'
            ]
            
            available_cols = [col for col in comparison_cols if col in df.columns]
            
            if available_cols:
                comparison_df = df[available_cols].copy()
                
                # Format for display
                if 'asking_price' in comparison_df.columns:
                    comparison_df['Asking Price'] = comparison_df['asking_price'].apply(format_currency)
                if 'residual_land_value_num' in comparison_df.columns:
                    comparison_df['Residual Value'] = comparison_df['residual_land_value_num'].apply(format_currency)
                if 'land_pct_gdv_num' in comparison_df.columns:
                    comparison_df['Land % GDV'] = comparison_df['land_pct_gdv_num'].apply(lambda x: f"{x:.1f}%")
                if 'overall_score' in comparison_df.columns and 'overall_status' in comparison_df.columns:
                    comparison_df['Status'] = comparison_df.apply(
                        lambda row: f"{get_color_indicator(row['overall_score'])} {row['overall_status']}", axis=1
                    )
                
                # Select display columns
                display_cols = ['site_name', 'Asking Price', 'Residual Value', 'Land % GDV', 'Status']
                available_display = [col for col in display_cols if col in comparison_df.columns]
                
                if 'site_name' in comparison_df.columns:
                    available_display = ['site_name'] + [col for col in available_display if col != 'site_name']
                
                st.dataframe(comparison_df[available_display], use_container_width=True)
                
                # Scatter plot comparison
                if 'residual_land_value_num' in df.columns and 'land_pct_gdv_num' in df.columns:
                    st.subheader("📊 Residual Value vs Land % GDV")
                    
                    fig = px.scatter(
                        df,
                        x='land_pct_gdv_num',
                        y='residual_land_value_num',
                        color='overall_score',
                        hover_name='site_name',
                        title="Deal Comparison Matrix",
                        labels={
                            'land_pct_gdv_num': 'Land % of GDV',
                            'residual_land_value_num': 'Residual Land Value ($)'
                        }
                    )
                    
                    # Add benchmark lines
                    fig.add_vline(x=25, line_dash="dash", annotation_text="Land % Benchmark (25%)")
                    fig.add_hline(y=0, line_dash="dash", annotation_text="Break-even")
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.info("No comparison data available")
        
        else:
            st.info("No deals available for comparison")
    
    except Exception as e:
        st.error(f"Error loading comparison data: {e}")

elif page == "Market Research":
    st.header("🔍 Market Research")
    
    available_cities = get_available_cities()
    selected_city = st.selectbox("Select Market", available_cities)
    
    if selected_city:
        try:
            market_data = load_market_data(selected_city)
            market_summary = get_market_summary(selected_city)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"📍 {market_summary['city']} Market Overview")
                
                st.metric("Land Price Range", market_summary['land_price_range'])
                st.metric("Sale Price Range", market_summary['sale_price_range'])
                st.metric("Construction Cost", market_summary['construction_cost_avg'])
                st.metric("Absorption Rate", market_summary['absorption_rate'])
            
            with col2:
                st.subheader("🎯 Benchmarks")
                
                st.metric("Typical Land % GDV", market_summary['typical_land_gdv'])
                st.metric("Typical Profit Margin", market_summary['typical_profit'])
                st.metric("Market Strength", market_summary['market_strength'])
                st.metric("Last Updated", market_summary['last_updated'])
            
            # Market indicators chart
            st.subheader("📊 Market Indicators")
            
            indicators = {
                'Demand Score': market_data.market_indicators['demand_score'],
                'Liquidity Score': market_data.market_indicators['liquidity_score'],
                'Volatility Score': market_data.market_indicators['volatility_score']
            }
            
            fig = px.bar(
                x=list(indicators.keys()),
                y=list(indicators.values()),
                title="Market Health Indicators (1-5 Scale)"
            )
            fig.update_yaxis(range=[0, 5])
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed market data
            with st.expander("📋 Detailed Market Data"):
                st.json(market_data.to_dict())
        
        except Exception as e:
            st.error(f"Error loading market data: {e}")

# Footer
st.markdown("---")
st.markdown(
    "**TerraFlow** - Built for real estate developers | "
    "🚀 Powered by Python, Streamlit & AI"
)