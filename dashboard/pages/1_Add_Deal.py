"""
Add Deal page for TerraFlow dashboard.
Allows users to input new land deals, analyze them, and save to CSV.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime
import os

# Add project root to path - safe sys.path injection
ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = str(Path(ROOT).parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from utils.market_loader import load_market_benchmarks, filter_allowed_markets
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Make sure you're running from the project root directory")

# Page config
st.set_page_config(layout="wide")

# Page header
st.header("🏞️ Add Deal")

# Market selection
col1, col2 = st.columns([1, 2])
with col1:
    market = st.selectbox("Market", ["dubai","greece","cyprus"], index=0)

with col2:
    if st.button("Show Market Summary"):
        try:
            # Load market data for selected city using new loader
            bench = load_market_benchmarks()
            bench = filter_allowed_markets(bench, allowed=(market,))
            city_data = bench
            
            if not city_data.empty:
                row = city_data.iloc[0]
                
                # Market summary card
                with st.container():
                    st.markdown(f"**📍 {market.title()} Market Summary**")
                    
                    # Key bullets
                    st.markdown(f"""
                    • **Sale Price**: ${row['sale_price_avg']:,.0f}/m² (${row['sale_price_min']:,.0f} - ${row['sale_price_max']:,.0f})
                    • **Construction**: ${row['construction_cost_avg']:,.0f}/m² typical
                    • **Absorption**: {row['absorption_rate']:.0f} months typical
                    """)
                    
                    # Mini comparison chart
                    import plotly.express as px
                    chart_data = {
                        'Sale Price': row['sale_price_avg'],
                        'Construction Cost': row['construction_cost_avg']
                    }
                    
                    fig = px.bar(
                        x=list(chart_data.keys()),
                        y=list(chart_data.values()),
                        title=f"{market.title()} - Price vs Cost",
                        color_discrete_sequence=["#2ca02c", "#ff7f0e"],
                        height=300
                    )
                    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No market data available for {market}")
        except Exception as e:
            st.error(f"Error loading market summary: {e}")

# Deal input form
with st.form("deal_input_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Site Information")
        site_name = st.text_input("Site Name", "New Site Analysis")
        land_area_sqm = st.number_input("Land Area (sqm)", min_value=100.0, value=1500.0)
        asking_price = st.number_input("Asking Price ($)", min_value=1000.0, value=750000.0)
        taxes_fees = st.number_input("Taxes & Fees ($)", min_value=0.0, value=37500.0)
        
        st.subheader("Zoning & Development")
        zoning = st.text_input("Zoning", "Residential")
        far = st.number_input("Floor Area Ratio (FAR)", min_value=0.1, max_value=5.0, value=1.8)
        coverage = st.slider("Site Coverage", 0.1, 0.8, 0.45)
        max_floors = st.number_input("Max Floors", min_value=1, max_value=20, value=5)
        efficiency_ratio = st.slider("Efficiency Ratio", 0.6, 0.95, 0.85)
        
    with col2:
        st.subheader("Market Assumptions")
        expected_sale_price_psm = st.number_input("Expected Sale Price ($/sqm)", min_value=1000.0, value=4200.0)
        construction_cost_psm = st.number_input("Construction Cost ($/sqm)", min_value=500.0, value=2100.0)
        soft_cost_pct = st.slider("Soft Cost %", 0.05, 0.30, 0.16)
        profit_target_pct = st.slider("Profit Target %", 0.10, 0.40, 0.20)
        
        st.subheader("Additional Costs")
        # Additional fields for completeness
        access_width_m = st.number_input("Access Width (m)", min_value=1.0, value=6.0)
        utilities = st.selectbox("Utilities Available", ["Full", "Partial", "None"])
        # Get default absorption from city data
        try:
            bench = load_market_benchmarks()
            bench = filter_allowed_markets(bench, allowed=(market,))
            if not bench.empty:
                default_absorption = bench.iloc[0]['absorption_rate']
            else:
                default_absorption = 18
        except Exception:
            default_absorption = 18
            
        months_to_sell = st.number_input("Months to Sell (Absorption)", 
                                       min_value=1, max_value=120, 
                                       value=int(default_absorption))
        
    submitted = st.form_submit_button("🔍 Analyze Deal", use_container_width=True)
    
    if submitted:
        # Create deal inputs dictionary
        deal_inputs = {
            'site_name': site_name,
            'land_area_sqm': float(land_area_sqm),
            'asking_price': float(asking_price),
            'taxes_fees': float(taxes_fees),
            'zoning': zoning,
            'far': float(far),
            'coverage': float(coverage),
            'max_floors': int(max_floors),
            'efficiency_ratio': float(efficiency_ratio),
            'expected_sale_price_psm': float(expected_sale_price_psm),
            'construction_cost_psm': float(construction_cost_psm),
            'soft_cost_pct': float(soft_cost_pct),
            'profit_target_pct': float(profit_target_pct),
            'financing_cost': 45000.0,  # Default value
            'holding_period_months': 30,  # Default value
            'access_width_m': float(access_width_m),
            'utilities': utilities,
            'months_to_sell': int(months_to_sell) if months_to_sell else None
        }
        
        try:
            # Load market benchmarks for the selected city
            bench = load_market_benchmarks()
            bench = filter_allowed_markets(bench, allowed=(market,))
            market_row = bench.iloc[0].to_dict() if not bench.empty else None

            # Analyze deal using new core calculations
            from core.calculations import calculate_deal_metrics
            out = calculate_deal_metrics(
                land_area_sqm=land_area_sqm,
                far=far,
                efficiency_ratio=efficiency_ratio,
                asking_price=asking_price,
                taxes_and_fees=taxes_fees,
                expected_sale_price_per_sqm=expected_sale_price_psm,
                construction_cost_per_sqm=construction_cost_psm,
                soft_cost_pct=soft_cost_pct,
                profit_target_pct=profit_target_pct,
                months_to_sell=months_to_sell,
                market_row=market_row
            )
            
            # Show analysis results
            st.success("✅ Analysis Complete!")
            
            # headline metrics (keep yours)
            c1, c2, c3 = st.columns(3)
            c1.metric("GDV", f"${out.gdv:,.0f}")
            c2.metric("Total Dev Cost", f"${out.total_dev_cost:,.0f}")
            c3.metric("Residual Land Value", f"${out.residual_land_value:,.0f}")

            c4, c5, c6 = st.columns(3)
            c4.metric("Land % of GDV", f"{out.land_pct_of_gdv*100:.1f}%")
            c5.metric("Breakeven $/sqm", f"${out.breakeven_price_per_sqm:,.0f}")
            c6.metric("Score", out.overall_score)

            st.subheader("📊 Additional KPIs")
            # NEW KPIs your team requested (with simple icons/emojis)
            k1, k2, k3 = st.columns(3)
            k1.metric("🏢 NSA (sqm)", f"{out.nsa_sqm:,.0f}")
            k2.metric("📐 GFA (sqm)", f"{out.gfa_sqm:,.0f}")
            k3.metric("💵 Acquisition Total", f"${out.acq_total_cost:,.0f}")

            k4, k5, k6 = st.columns(3)
            k4.metric("🏷️ Acq $/Land sqm", f"${out.acq_cost_per_total_area:,.0f}")
            k5.metric("🏷️ Acq $/GFA sqm", f"${out.acq_cost_per_buildable_area:,.0f}")
            k6.metric("🏷️ Land $/NSA sqm", f"${out.land_cost_per_nsa:,.0f}")

            k7, k8 = st.columns(2)
            k7.metric("⏳ Est. Months to Sell", f"{out.est_absorption_months:,.1f}")
            k8.metric("🚀 Absorption / mo (sqm)", f"{out.est_absorption_rate_per_month:,.0f}")
            
            # Only set session state after successful analysis
            st.session_state['deal'] = out
            st.session_state['deal_ready'] = True
            
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.info("Please check your inputs and try again.")
            # Clear deal session state on failure
            if 'deal' in st.session_state:
                del st.session_state['deal']
            if 'deal_ready' in st.session_state:
                del st.session_state['deal_ready']

# Save deal button (outside form)
if submitted and st.session_state.get('deal_ready', False):
    if st.button("💾 Save Deal", use_container_width=True):
        try:
            # Create deal record
            deal = st.session_state['deal']
            deal_record = {
                'site_name': site_name,
                'city_key': selected_city,
                'land_area_sqm': land_area_sqm,
                'asking_price': asking_price,
                'taxes_fees': taxes_fees,
                'zoning': zoning,
                'far': far,
                'coverage': coverage,
                'max_floors': max_floors,
                'efficiency_ratio': efficiency_ratio,
                'expected_sale_price_psm': expected_sale_price_psm,
                'construction_cost_psm': construction_cost_psm,
                'soft_cost_pct': soft_cost_pct,
                'profit_target_pct': profit_target_pct,
                'access_width_m': access_width_m,
                'utilities': utilities,
                'months_to_sell': months_to_sell,
                'date_analyzed': datetime.now().strftime('%Y-%m-%d'),
                # Analysis results
                'gross_buildable_sqm': deal.outputs.gross_buildable_sqm,
                'net_sellable_sqm': deal.outputs.net_sellable_sqm,
                'gdv': deal.outputs.gdv,
                'residual_land_value': deal.outputs.residual_land_value,
                'land_pct_gdv': deal.outputs.land_pct_gdv,
                'breakeven_sale_price': deal.outputs.breakeven_sale_price,
                'overall_score': deal.viability.overall_score,
                'overall_status': deal.viability.overall_status,
                # New KPIs
                'nsa_sqm': deal.outputs.net_sellable_sqm,
                'acq_cost_per_land_sqm': deal.outputs.acq_cost_per_land_sqm,
                'acq_cost_per_gfa_sqm': deal.outputs.acq_cost_per_gfa_sqm,
                'land_cost_per_nsa_sqm': deal.outputs.land_cost_per_nsa_sqm
            }
            
            # Load existing acquisitions or create new
            acquisitions_path = get_data_dir() / "processed" / "acquisitions.csv"
            
            if acquisitions_path.exists():
                existing_df = load_csv(acquisitions_path)
                # Append new deal
                new_df = pd.concat([existing_df, pd.DataFrame([deal_record])], ignore_index=True)
            else:
                new_df = pd.DataFrame([deal_record])
            
            # Save to CSV
            save_csv(new_df, acquisitions_path)
            
            st.success(f"✅ Deal '{site_name}' saved successfully!")
            st.info("Navigate to the Pipeline page to view all deals.")
            
        except Exception as e:
            st.error(f"Error saving deal: {e}")