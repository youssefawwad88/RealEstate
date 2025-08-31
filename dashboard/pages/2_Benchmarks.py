"""
Benchmarks Page - TerraFlow v2
Display market research data with charts.
"""
import streamlit as st
import pandas as pd
from utils.market_loader import load_market_benchmarks, filter_allowed_markets, REFERENCE_PATH

st.set_page_config(page_title="Benchmarks - TerraFlow v2", page_icon="📊")
st.title("📊 Market Benchmarks")

# Load market data
try:
    df = load_market_benchmarks()
    filtered_df = filter_allowed_markets(df)
    
    if filtered_df.empty:
        st.warning(f"""
        ⚠️ **Market research data not found or empty**
        
        Expected file: `{REFERENCE_PATH}`
        
        Please ensure the file exists with the correct format and contains data for:
        dubai, greece, cyprus
        """)
        st.stop()
        
except Exception as e:
    st.error(f"❌ Error loading market data: {e}")
    st.stop()

# Market selection
available_markets = filtered_df['city_key'].str.lower().unique()
default_selection = [market for market in available_markets if market in ['dubai', 'greece', 'cyprus']]

selected_markets = st.multiselect(
    "Select Markets to Display",
    options=list(available_markets),
    default=default_selection,
    help="Choose which markets to include in the analysis"
)

if not selected_markets:
    st.warning("Please select at least one market to display.")
    st.stop()

# Filter to selected markets
display_df = filtered_df[filtered_df['city_key'].str.lower().isin(selected_markets)].copy()

st.markdown("---")

# Display market data table
st.subheader("🗂️ Market Data Table")
st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# Charts section
st.subheader("📈 Market Analysis Charts")

if len(display_df) > 0:
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown("**💰 Sale Price vs Construction Cost**")
        
        # Prepare data for bar chart
        chart_data = pd.DataFrame({
            'Market': display_df['city_key'],
            'Sale Price Avg': display_df['sale_price_avg'],
            'Construction Cost Avg': display_df['construction_cost_avg']
        })
        
        st.bar_chart(
            chart_data.set_index('Market'),
            height=400
        )
    
    with chart_col2:
        st.markdown("**⏱️ Absorption Rate by Market**")
        
        # Prepare data for line chart
        absorption_data = pd.DataFrame({
            'Market': display_df['city_key'],
            'Absorption Rate (months)': display_df['absorption_rate']
        })
        
        st.line_chart(
            absorption_data.set_index('Market'),
            height=400
        )

    st.markdown("---")
    
    # Summary statistics
    st.subheader("📊 Market Summary")
    
    summary_cols = st.columns(3)
    
    with summary_cols[0]:
        st.markdown("**🏠 Average Sale Prices**")
        for _, row in display_df.iterrows():
            st.write(f"**{row['city_key'].title()}:** ${row['sale_price_avg']:,.0f}/sqm")
    
    with summary_cols[1]:
        st.markdown("**🔨 Average Construction Costs**")
        for _, row in display_df.iterrows():
            st.write(f"**{row['city_key'].title()}:** ${row['construction_cost_avg']:,.0f}/sqm")
    
    with summary_cols[2]:
        st.markdown("**⏰ Absorption Rates**")
        for _, row in display_df.iterrows():
            st.write(f"**{row['city_key'].title()}:** {row['absorption_rate']:.1f} months")

else:
    st.warning("No data available for the selected markets.")

# Raw data expander
with st.expander("🔍 Raw Market Data"):
    st.markdown("**Complete dataset:**")
    st.json(display_df.to_dict(orient='records'))