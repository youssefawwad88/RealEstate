"""
Benchmarks page for TerraFlow dashboard.
Shows market research data filtered by city with benchmarks and comparisons.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from utils.io import load_csv, get_data_dir
    from utils.scoring import format_currency
    from utils.market_loader import load_market_data, get_available_cities
    from modules.market_lookup import get_market_summary
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Make sure you're running from the project root directory")

# Page config
st.set_page_config(layout="wide")

st.title("📊 Benchmarks")
st.markdown("Explore market research data and benchmarks by city.")

# Load market research data
try:
    from utils.market_loader import load_market_data, filter_allowed_markets
    market_df = load_market_data()
    market_df = filter_allowed_markets(market_df)
    if market_df.empty:
        st.error("Market research data not found.\n\nExpected file: `data/reference/market_research.csv`")
        st.stop()
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Make sure you're running from the project root directory")
    st.stop()
except Exception as e:
    st.error("Market research data not found.\n\nExpected file: `data/reference/market_research.csv`")
    st.stop()

# City selection
available_cities = sorted(market_df["city_key"].unique().tolist())
selected_city = st.selectbox("Select City", available_cities, index=0)

if selected_city:
    # Filter data for selected city
    city_data = market_df[market_df["city_key"] == selected_city].iloc[0]

    # Market overview cards
    st.subheader(f"📍 {selected_city.title().replace('_', ' ')} Market Overview")
    
    # Key metrics in cards
    col1, col2, col3 = st.columns(3)
    with col1: 
        st.metric("Avg Land $/sqm", f"${int(city_data['land_comp_avg']):,}")
    with col2: 
        st.metric("Avg Sale $/sqm", f"${int(city_data['sale_price_avg']):,}")
    with col3: 
        st.metric("Avg Const $/sqm", f"${int(city_data['construction_cost_avg']):,}")

    # Market indicators
    st.subheader("📈 Market Health Indicators")

    col1, col2, col3 = st.columns(3)

    with col1:
        # Create a simple gauge-like display
        demand_score = city_data["demand_score"]
        if demand_score >= 4:
            st.success(f"🟢 Demand Score: {demand_score}/5 (Strong)")
        elif demand_score >= 3:
            st.warning(f"🟡 Demand Score: {demand_score}/5 (Moderate)")
        else:
            st.error(f"🔴 Demand Score: {demand_score}/5 (Weak)")

    with col2:
        liquidity_score = city_data["liquidity_score"]
        if liquidity_score >= 4:
            st.success(f"🟢 Liquidity Score: {liquidity_score}/5 (High)")
        elif liquidity_score >= 3:
            st.warning(f"🟡 Liquidity Score: {liquidity_score}/5 (Moderate)")
        else:
            st.error(f"🔴 Liquidity Score: {liquidity_score}/5 (Low)")

    with col3:
        volatility_score = city_data["volatility_score"]
        if volatility_score <= 2:
            st.success(f"🟢 Volatility Score: {volatility_score}/5 (Stable)")
        elif volatility_score <= 3:
            st.warning(f"🟡 Volatility Score: {volatility_score}/5 (Moderate)")
        else:
            st.error(f"🔴 Volatility Score: {volatility_score}/5 (High)")

    # Detailed benchmarks
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💰 Pricing Benchmarks")

        # Land pricing
        st.markdown("**Land Comparables ($/sqm)**")
        land_data = {
            "Min": city_data["land_comp_min"],
            "Average": city_data["land_comp_avg"],
            "Max": city_data["land_comp_max"],
        }

        import plotly.express as px

        fig_land = px.bar(
            x=list(land_data.keys()),
            y=list(land_data.values()),
            title=f"{selected_city.title()} - Land Pricing",
            labels={"x": "Metric", "y": "Price ($/sqm)"},
            color_discrete_sequence=["#1f77b4"],
        )
        
        container = st.container()
        with container:
            st.plotly_chart(fig_land, use_container_width=True)

        # Sale pricing
        st.markdown("**Sale Price Comparables ($/sqm)**")
        sale_data = {
            "Min": city_data["sale_price_min"],
            "Average": city_data["sale_price_avg"],
            "Max": city_data["sale_price_max"],
        }

        fig_sale = px.bar(
            x=list(sale_data.keys()),
            y=list(sale_data.values()),
            title=f"{selected_city.title()} - Sale Pricing",
            labels={"x": "Metric", "y": "Price ($/sqm)"},
            color_discrete_sequence=["#2ca02c"],
        )
        
        container = st.container()
        with container:
            st.plotly_chart(fig_sale, use_container_width=True)

    with col2:
        st.subheader("🏗️ Cost Benchmarks")

        # Construction costs
        st.markdown("**Construction Costs ($/sqm)**")
        cost_data = {
            "Min": city_data["construction_cost_min"],
            "Average": city_data["construction_cost_avg"],
            "Max": city_data["construction_cost_max"],
        }

        fig_cost = px.bar(
            x=list(cost_data.keys()),
            y=list(cost_data.values()),
            title=f"{selected_city.title()} - Construction Costs",
            labels={"x": "Metric", "y": "Cost ($/sqm)"},
            color_discrete_sequence=["#ff7f0e"],
        )
        
        container = st.container()
        with container:
            st.plotly_chart(fig_cost, use_container_width=True)

        # Market metrics
        st.markdown("**Market Performance Metrics**")

        metrics_data = {
            "Absorption Rate": city_data["absorption_rate"],
            "Profit Margin %": city_data["profit_margin_benchmark"],
            "Soft Cost %": city_data["soft_cost_pct_typical"] * 100,
        }

        for metric, value in metrics_data.items():
            if "Rate" in metric:
                st.metric(metric, f"{value:.1f} units/month")
            elif "%" in metric:
                st.metric(metric, f"{value:.1f}%")
            else:
                st.metric(metric, f"{value:.2f}")

    # City comparison
    st.subheader("⚖️ City Comparison")

    if len(available_cities) > 1:
        compare_cities = st.multiselect(
            "Select cities to compare",
            available_cities,
            default=[selected_city],
        )

        if len(compare_cities) > 1:
            compare_df = market_df[
                market_df["city_key"].isin(compare_cities)
            ].copy()

            # Comparison metrics
            comparison_metrics = [
                "land_comp_avg",
                "sale_price_avg",
                "construction_cost_avg",
                "demand_score",
                "liquidity_score",
            ]

            # Create comparison chart
            fig_compare = px.bar(
                compare_df,
                x="city_key",
                y="sale_price_avg",
                title="Average Sale Price Comparison",
                labels={
                    "city_key": "City",
                    "sale_price_avg": "Sale Price ($/sqm)",
                },
                color="demand_score",
                color_continuous_scale="Viridis",
            )
            
            container = st.container()
            with container:
                st.plotly_chart(fig_compare, use_container_width=True)

            # Comparison table
            display_cols = [
                "city_key",
                "land_comp_avg",
                "sale_price_avg",
                "construction_cost_avg",
                "demand_score",
                "liquidity_score",
                "last_updated",
            ]

            comparison_display = compare_df[display_cols].copy()
            comparison_display.columns = [
                "City",
                "Land Price Avg",
                "Sale Price Avg",
                "Construction Cost Avg",
                "Demand Score",
                "Liquidity Score",
                "Last Updated",
            ]

            # Format currency columns
            for col in [
                "Land Price Avg",
                "Sale Price Avg",
                "Construction Cost Avg",
            ]:
                comparison_display[col] = comparison_display[col].apply(
                    format_currency
                )

            st.dataframe(comparison_display, width="stretch", hide_index=True)

# Market research data export
st.subheader("📥 Export Market Data")

if selected_city:
    # Create detailed export data
    export_data = city_data.to_dict()
    export_df = pd.DataFrame([export_data])

    csv = export_df.to_csv(index=False)
    st.download_button(
        label=f"Download {selected_city} Market Data",
        data=csv,
        file_name=f"{selected_city}_market_data.csv",
        mime="text/csv",
    )

    # Raw data view
    with st.expander("📋 Raw Market Data"):
        st.json(export_data)

# Footer with helpful info
st.markdown("---")
st.markdown(
    """
**Benchmark Tips:**
- Use these benchmarks to validate your deal assumptions
- Compare multiple cities to identify opportunities
- Demand and liquidity scores help assess market strength
- Update market data regularly for accurate analysis
"""
)
