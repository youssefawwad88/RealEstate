"""
Add Deal page for TerraFlow dashboard.
Allows users to input new land deals, analyze them, and save to CSV.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from modules.deal_model import create_deal_from_dict
    from modules.market_lookup import get_market_summary
    from utils.scoring import get_color_indicator, format_currency
    from utils.io import load_csv, save_csv, get_data_dir
    from utils.market_loader import load_market_data, get_available_cities
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Make sure you're running from the project root directory")

st.title("🏞️ Add Deal")
st.markdown("Enter new land acquisition deals and analyze their viability.")

# City selection from market research data
try:
    available_cities = get_available_cities()
except Exception:
    available_cities = ["toronto", "vancouver", "dubai_downtown", "default"]

# Market selection
col1, col2 = st.columns([1, 2])
with col1:
    selected_city = st.selectbox("Market", available_cities, index=0)

with col2:
    if st.button("Show Market Summary"):
        try:
            market_summary = get_market_summary(selected_city)
            st.json(market_summary)
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
        months_to_sell = st.number_input("Months to Sell (Absorption)", min_value=1, max_value=120, value=18)
        
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
            # Analyze the deal using existing modules
            deal = create_deal_from_dict(deal_inputs)
            
            # Show analysis results
            st.success("✅ Analysis Complete!")
            
            # Key metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("GDV", format_currency(deal.outputs.gdv))
                st.metric("Residual Land Value", format_currency(deal.outputs.residual_land_value))
                
            with col2:
                st.metric("Total Dev Cost", format_currency(deal.outputs.total_dev_cost))
                st.metric("Land % of GDV", f"{deal.outputs.land_pct_gdv:.1f}%")
                
            with col3:
                st.metric("Breakeven Price/sqm", format_currency(deal.outputs.breakeven_sale_price))
                st.metric("Overall Score", f"{get_color_indicator(deal.viability.overall_score)} {deal.viability.overall_status}")
            
            # New KPI metrics in a 2x3 grid
            st.subheader("📊 Additional KPIs")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Areas
                st.metric(
                    "Net Sellable Area (NSA)", 
                    f"{deal.outputs.net_sellable_sqm:,.0f} m²",
                    help="Net sellable area = GFA × efficiency ratio"
                )
                
                # Cost metrics
                if deal.outputs.acq_cost_per_land_sqm:
                    st.metric(
                        "Acquisition cost / total area", 
                        f"{deal.outputs.acq_cost_per_land_sqm:,.0f} $/m²",
                        help="Land asking price ÷ total land area"
                    )
                
                if deal.outputs.acq_cost_per_gfa_sqm:
                    st.metric(
                        "Acquisition cost / buildable area", 
                        f"{deal.outputs.acq_cost_per_gfa_sqm:,.0f} $/m²",
                        help="Land asking price ÷ gross buildable area"
                    )
            
            with col2:
                if deal.outputs.land_cost_per_nsa_sqm:
                    st.metric(
                        "Land cost / NSA", 
                        f"{deal.outputs.land_cost_per_nsa_sqm:,.0f} $/m²",
                        help="Land asking price ÷ net sellable area"
                    )
                
                # Absorption
                if deal.outputs.monthly_absorption_rate and months_to_sell:
                    st.metric(
                        "Months to Sell (Absorption)", 
                        f"{months_to_sell:.0f} months",
                        help=f"Monthly absorption rate: {deal.outputs.monthly_absorption_rate:.1%}"
                    )
                    
                    # Simple absorption schedule preview
                    st.markdown("**Absorption Schedule Preview:**")
                    preview_data = []
                    for month in [1, 3, 6, 12, months_to_sell]:
                        if month <= months_to_sell:
                            pct_sold = min((month * deal.outputs.monthly_absorption_rate * 100), 100)
                            remaining_nsa = deal.outputs.net_sellable_sqm * (1 - pct_sold/100)
                            preview_data.append({
                                "Month": month,
                                "% Sold": f"{pct_sold:.1f}%",
                                "Remaining NSA (m²)": f"{remaining_nsa:,.0f}"
                            })
                    
                    if preview_data:
                        st.dataframe(pd.DataFrame(preview_data), width="stretch", hide_index=True)
            
            # Color-coded badges for key metrics
            st.subheader("🚦 Viability Flags")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Land % of GDV flag (target 15-30%)
                land_pct = deal.outputs.land_pct_gdv
                if 15 <= land_pct <= 30:
                    st.success(f"🟢 Land % GDV: {land_pct:.1f}% (Good)")
                elif land_pct < 15:
                    st.warning(f"🟡 Land % GDV: {land_pct:.1f}% (Low)")
                else:
                    st.error(f"🔴 Land % GDV: {land_pct:.1f}% (High)")
            
            with col2:
                # Breakeven vs market check (target >85% of market avg)
                try:
                    market_df = load_market_data()
                    market_row = market_df[market_df['city_key'] == selected_city]
                    if not market_row.empty:
                        market_avg = market_row.iloc[0]['sale_price_avg']
                        breakeven_ratio = deal.outputs.breakeven_sale_price / market_avg
                        if breakeven_ratio <= 0.85:
                            st.success(f"🟢 Breakeven Risk: {breakeven_ratio:.1%} of market (Good)")
                        elif breakeven_ratio <= 0.95:
                            st.warning(f"🟡 Breakeven Risk: {breakeven_ratio:.1%} of market (Medium)")
                        else:
                            st.error(f"🔴 Breakeven Risk: {breakeven_ratio:.1%} of market (High)")
                    else:
                        st.info("No market data for comparison")
                except Exception:
                    st.info("Market comparison unavailable")
            
            with col3:
                # Asking vs residual comparison
                asking_vs_residual = deal.outputs.asking_vs_residual
                if asking_vs_residual <= 1.0:
                    st.success(f"🟢 Price vs Value: {asking_vs_residual:.1%} (Good)")
                elif asking_vs_residual <= 1.2:
                    st.warning(f"🟡 Price vs Value: {asking_vs_residual:.1%} (Fair)")
                else:
                    st.error(f"🔴 Price vs Value: {asking_vs_residual:.1%} (Expensive)")
            
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
            st.info("Please check your inputs and try again.")
            st.session_state['deal_ready'] = False
            if 'deal' in st.session_state:
                del st.session_state['deal']
        else:
            st.session_state['deal_ready'] = True
            st.session_state['deal'] = deal

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