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
    expected_sale_price_per_sqm = st.number_input("Expected Sale Price/sqm", value=4200.0, min_value=0.0)
    construction_cost_per_sqm = st.number_input("Construction Cost/sqm", value=2100.0, min_value=0.0)
    
    st.markdown("**Project Parameters**")
    soft_cost_pct = st.number_input("Soft Cost %", value=0.16, min_value=0.0, max_value=1.0, format="%.3f")
    profit_target_pct = st.number_input("Profit Target %", value=0.18, min_value=0.0, max_value=1.0, format="%.3f")
    months_to_sell = st.number_input("Months to Sell (optional)", value=18.0, min_value=0.0)

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
    st.subheader("📊 Analysis Results")
    
    # Headline metrics
    st.markdown("**💰 Key Financial Metrics**")
    metric_cols = st.columns(6)
    
    with metric_cols[0]:
        st.metric("GDV", f"${outputs.gdv:,.0f}")
    with metric_cols[1]:
        st.metric("Total Dev Cost", f"${outputs.total_dev_cost:,.0f}")
    with metric_cols[2]:
        st.metric("Residual Land Value", f"${outputs.residual_land_value:,.0f}")
    with metric_cols[3]:
        st.metric("Land % of GDV", f"{outputs.land_pct_of_gdv:.1%}")
    with metric_cols[4]:
        st.metric("Breakeven $/sqm", f"${outputs.breakeven_price_per_sqm:,.0f}")
    with metric_cols[5]:
        st.metric("Score", outputs.overall_score)
    
    st.markdown("---")
    
    # KPIs grid
    st.markdown("**📐 Development KPIs**")
    kpi_cols = st.columns(4)
    
    with kpi_cols[0]:
        st.metric("NSA (sqm)", f"{outputs.nsa_sqm:,.0f}")
        st.metric("GFA (sqm)", f"{outputs.gfa_sqm:,.0f}")
    
    with kpi_cols[1]:
        st.metric("Acquisition Total", f"${outputs.acq_total_cost:,.0f}")
        st.metric("Acq $/Land sqm", f"${outputs.acq_cost_per_total_area:,.0f}")
    
    with kpi_cols[2]:
        st.metric("Acq $/GFA sqm", f"${outputs.acq_cost_per_buildable_area:,.0f}")
        st.metric("Land $/NSA sqm", f"${outputs.land_cost_per_nsa:,.0f}")
    
    with kpi_cols[3]:
        st.metric("Est. Months", f"{outputs.est_absorption_months:.1f}")
        st.metric("Absorption / mo", f"{outputs.est_absorption_rate_per_month:,.0f} sqm")
    
    # Market data info
    if market_row:
        with st.expander("📈 Market Data Used"):
            st.json(market_row)
else:
    st.info("👆 Click 'Analyze Deal' to see results")