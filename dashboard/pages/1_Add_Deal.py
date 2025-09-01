"""
Add Deal Page - TerraFlow v2
Input deal parameters and analyze with market data.
"""
import streamlit as st
from utils.market_loader import load_market_benchmarks, filter_allowed_markets
from core.calculations import calculate_deal_metrics

st.set_page_config(page_title="Add Deal - TerraFlow v2", page_icon="🏗️")
st.title("🏗️ Add Deal")

# Market selector
st.subheader("📍 Market Selection")
market_options = ["dubai", "greece", "cyprus"]
selected_market = st.selectbox(
    "Select Market", 
    market_options,
    help="Choose the market for this deal analysis"
)

# Load market data for defaults
try:
    df = load_market_benchmarks()
    filtered_df = filter_allowed_markets(df)
    
    # Get market row for defaults
    market_defaults = None
    if not filtered_df.empty:
        market_matches = filtered_df[filtered_df['city_key'].str.lower() == selected_market.lower()]
        if not market_matches.empty:
            market_defaults = market_matches.iloc[0].to_dict()
            st.info(f"📊 Using {selected_market.title()} market defaults: Sale ${market_defaults.get('sale_price_avg', 'N/A'):,}/sqm, Construction ${market_defaults.get('construction_cost_avg', 'N/A'):,}/sqm, Soft Cost {market_defaults.get('soft_cost_pct_typical', 'N/A'):.1%}")
            
except Exception:
    market_defaults = None
    st.warning("⚠️ Could not load market defaults, using standard values")

st.markdown("---")

# Input form
st.subheader("📊 Deal Parameters")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Land & Development**")
    land_area_sqm = st.number_input("Land Area (sqm)", value=1500.0, min_value=1.0)
    far = st.number_input("FAR (Floor Area Ratio)", value=1.8, min_value=0.1, max_value=10.0)
    efficiency_ratio = st.number_input("Efficiency Ratio", value=0.80, min_value=0.1, max_value=1.0)
    
    st.markdown("**Financial Assumptions**")
    asking_price = st.number_input("Asking Price", value=750000.0, min_value=0.0)
    taxes_and_fees = st.number_input("Taxes & Fees", value=37500.0, min_value=0.0)

with col2:
    st.markdown("**Market Assumptions**")
    
    # Use market defaults if available
    default_sale_price = market_defaults.get('sale_price_avg', 4200.0) if market_defaults else 4200.0
    default_construction_cost = market_defaults.get('construction_cost_avg', 2100.0) if market_defaults else 2100.0
    
    expected_sale_price_per_sqm = st.number_input("Expected Sale Price/sqm", value=float(default_sale_price), min_value=0.0)
    construction_cost_per_sqm = st.number_input("Construction Cost/sqm", value=float(default_construction_cost), min_value=0.0)
    
    st.markdown("**Project Parameters**")
    
    # Use market defaults for soft cost % and default absorption months
    default_soft_cost = market_defaults.get('soft_cost_pct_typical', 0.16) if market_defaults else 0.16
    default_absorption = market_defaults.get('absorption_rate', 18.0) if market_defaults else 18.0
    
    soft_cost_pct = st.number_input("Soft Cost %", value=float(default_soft_cost), min_value=0.0, max_value=1.0, format="%.3f")
    profit_target_pct = st.number_input("Profit Target %", value=0.18, min_value=0.0, max_value=1.0, format="%.3f")
    months_to_sell = st.number_input("Months to Sell (optional)", value=float(default_absorption), min_value=0.0)

st.markdown("---")

# Analysis button
if st.button("📈 Analyze Deal", type="primary"):
    try:
        with st.spinner("Loading market data and calculating..."):
            # Load and filter market data
            df = load_market_benchmarks()
            filtered_df = filter_allowed_markets(df)
            
            # Get market row for selected market (if available)
            market_row = None
            if not filtered_df.empty:
                market_matches = filtered_df[filtered_df['city_key'].str.lower() == selected_market.lower()]
                if not market_matches.empty:
                    market_row = market_matches.iloc[0].to_dict()
            
            # Calculate metrics
            outputs = calculate_deal_metrics(
                land_area_sqm=land_area_sqm,
                far=far,
                efficiency_ratio=efficiency_ratio,
                asking_price=asking_price,
                taxes_and_fees=taxes_and_fees,
                expected_sale_price_per_sqm=expected_sale_price_per_sqm,
                construction_cost_per_sqm=construction_cost_per_sqm,
                soft_cost_pct=soft_cost_pct,
                profit_target_pct=profit_target_pct,
                months_to_sell=months_to_sell if months_to_sell > 0 else None,
                market_row=market_row
            )
            
            # Store in session state (single key 'analysis')
            st.session_state['analysis'] = outputs
            
        st.success("✅ Analysis completed successfully!")
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {e}")
        # Do not write to session state on error

# Display results if analysis exists
if 'analysis' in st.session_state:
    outputs = st.session_state['analysis']
    
    st.markdown("---")
    st.subheader("✅ Analysis")
    
    # Headline metrics in 3x2 grid
    st.markdown("**💰 Key Financial Metrics**")
    
    # First row of headline metrics
    headline_cols1 = st.columns(3)
    with headline_cols1[0]:
        st.metric("GDV", f"${outputs.gdv:,.0f}")
    with headline_cols1[1]:
        st.metric("Total Dev Cost", f"${outputs.total_dev_cost:,.0f}")
    with headline_cols1[2]:
        st.metric("Residual Land Value", f"${outputs.residual_land_value:,.0f}")
    
    # Second row of headline metrics  
    headline_cols2 = st.columns(3)
    with headline_cols2[0]:
        st.metric("Land % of GDV", f"{outputs.land_pct_of_gdv:.1%}")
    with headline_cols2[1]:
        st.metric("Breakeven $/sqm", f"${outputs.breakeven_price_per_sqm:,.0f}")
    with headline_cols2[2]:
        st.metric("Score", outputs.overall_score)
    
    st.markdown("---")
    
    # NSA + Acquisition KPIs in 4x2 grid
    st.markdown("**📐 Development KPIs**")
    
    # First row of KPIs
    kpi_cols1 = st.columns(4)
    with kpi_cols1[0]:
        st.metric("NSA (sqm)", f"{outputs.nsa_sqm:,.0f}")
    with kpi_cols1[1]:
        st.metric("GFA (sqm)", f"{outputs.gfa_sqm:,.0f}")
    with kpi_cols1[2]:
        st.metric("Acq $ / Land sqm", f"${outputs.acq_cost_per_total_area:,.0f}")
    with kpi_cols1[3]:
        st.metric("Acq $ / GFA sqm", f"${outputs.acq_cost_per_buildable_area:,.0f}")
    
    # Second row of KPIs
    kpi_cols2 = st.columns(4)
    with kpi_cols2[0]:
        st.metric("Land $ / NSA sqm", f"${outputs.land_cost_per_nsa:,.0f}")
    with kpi_cols2[1]:
        st.metric("Est. Months", f"{outputs.est_absorption_months:.1f}")
    with kpi_cols2[2]:
        st.metric("Absorption / mo (sqm)", f"{outputs.est_absorption_rate_per_month:,.0f}")
    with kpi_cols2[3]:
        # Negotiation delta: Residual - Asking (incl. fees)
        negotiation_delta = outputs.residual_land_value - outputs.acq_total_cost
        if negotiation_delta >= 0:
            st.metric("Negotiation Delta", f"${negotiation_delta:,.0f}", delta=f"${negotiation_delta:,.0f}")
        else:
            st.metric("Price Must Drop", f"${abs(negotiation_delta):,.0f}", delta=f"-${abs(negotiation_delta):,.0f}")
    
    st.markdown("---")
    
    # Safety flags
    st.markdown("**🚨 Safety Flags**")
    flag_cols = st.columns(3)
    
    with flag_cols[0]:
        # Land % of GDV band
        land_pct = outputs.land_pct_of_gdv * 100
        if 15 <= land_pct <= 30:
            st.success(f"🟢 Land % of GDV: {land_pct:.1f}% (Good)")
        elif land_pct < 15 or (30 < land_pct <= 35):
            st.warning(f"🟡 Land % of GDV: {land_pct:.1f}% (Watch)")
        else:
            st.error(f"🔴 Land % of GDV: {land_pct:.1f}% (Risk)")
    
    with flag_cols[1]:
        # Breakeven vs market comparison
        if market_row and 'sale_price_avg' in market_row:
            market_price = market_row['sale_price_avg']
            breakeven_ratio = outputs.breakeven_price_per_sqm / market_price
            if breakeven_ratio <= 0.85:
                st.success(f"🟢 Breakeven: {breakeven_ratio:.0%} of market (Good)")
            elif breakeven_ratio <= 0.95:
                st.warning(f"🟡 Breakeven: {breakeven_ratio:.0%} of market (Watch)")
            else:
                st.error(f"🔴 Breakeven: {breakeven_ratio:.0%} of market (Risk)")
        else:
            st.info("🔵 Market data unavailable")
    
    with flag_cols[2]:
        # Asking vs residual comparison
        if outputs.residual_land_value >= outputs.acq_total_cost:
            st.success("🟢 Asking ≤ Residual (Good)")
        else:
            overage_pct = (outputs.acq_total_cost / outputs.residual_land_value - 1) * 100
            st.error(f"🔴 {overage_pct:.1f}% overage (Negotiate)")
    
    st.markdown("---")
    
    # Sensitivity analysis
    st.markdown("**📊 Sensitivity Analysis**")
    sens_cols = st.columns(2)
    
    with sens_cols[0]:
        # Residual if Sales -10%
        gdv_down = outputs.gdv * 0.9
        residual_sales_down = gdv_down - (outputs.total_dev_cost - outputs.acq_total_cost) - (gdv_down * profit_target_pct)
        st.metric("Residual if Sales -10%", f"${residual_sales_down:,.0f}")
    
    with sens_cols[1]:
        # Residual if Costs +10% 
        total_costs_up = outputs.total_dev_cost * 1.1
        residual_costs_up = outputs.gdv - (total_costs_up - outputs.acq_total_cost) - (outputs.gdv * profit_target_pct)
        st.metric("Residual if Costs +10%", f"${residual_costs_up:,.0f}")
    
    st.markdown("---")
    
    # Assumptions summary
    if market_row:
        st.markdown("**📋 Assumptions Summary**")
        st.markdown(f"""
        **Market assumptions used:**
        - Soft Cost %: {soft_cost_pct:.1%}
        - Absorption Months: {outputs.est_absorption_months:.1f} months
        - Market Sale Price: ${market_row.get('sale_price_avg', 'N/A'):,}/sqm
        - Market Construction Cost: ${market_row.get('construction_cost_avg', 'N/A'):,}/sqm
        """)
    
    st.markdown("---")
    
    st.markdown("---")
    
    # Save snapshot
    st.markdown("**💾 Save Deal**")
    if st.button("Save deal to CSV", help="Save this analysis to a CSV file"):
        import pandas as pd
        from datetime import datetime
        
        # Prepare data for CSV
        deal_data = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'market': selected_market,
            'land_area_sqm': land_area_sqm,
            'far': far,
            'efficiency_ratio': efficiency_ratio,
            'asking_price': asking_price,
            'taxes_and_fees': taxes_and_fees,
            'gdv': outputs.gdv,
            'total_dev_cost': outputs.total_dev_cost,
            'residual_land_value': outputs.residual_land_value,
            'land_pct_of_gdv': outputs.land_pct_of_gdv,
            'breakeven_price_per_sqm': outputs.breakeven_price_per_sqm,
            'overall_score': outputs.overall_score,
            'nsa_sqm': outputs.nsa_sqm,
            'gfa_sqm': outputs.gfa_sqm,
            'negotiation_delta': outputs.residual_land_value - outputs.acq_total_cost
        }
        
        df_save = pd.DataFrame([deal_data])
        csv = df_save.to_csv(index=False)
        
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"terraflow_deal_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
        st.success("Deal data prepared for download!")
    
    # Market data info
    if market_row:
        with st.expander("📈 Market Data Used"):
            st.json(market_row)
else:
    st.info("👆 Click 'Analyze Deal' to see results")