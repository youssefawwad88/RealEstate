"""
Pipeline page for TerraFlow dashboard.
Shows deals from acquisitions.csv with filters and conditional coloring.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from utils.io import load_csv, get_data_dir
    from utils.scoring import get_color_indicator, format_currency
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Make sure you're running from the project root directory")

st.title("📊 Pipeline")
st.markdown("View and filter your land acquisition deal pipeline.")

# Load acquisitions data
try:
    acquisitions_path = get_data_dir() / "processed" / "acquisitions.csv"
    
    if acquisitions_path.exists():
        df = load_csv(acquisitions_path)
        
        if not df.empty:
            st.success(f"Loaded {len(df)} deals from pipeline.")
            
            # Filters
            st.subheader("🔍 Filters")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # City filter
                if 'city_key' in df.columns:
                    available_cities = ['All'] + sorted(df['city_key'].unique().tolist())
                    selected_city = st.selectbox("City", available_cities)
                    
                    if selected_city != 'All':
                        df = df[df['city_key'] == selected_city]
                
            with col2:
                # Date range filter
                if 'date_analyzed' in df.columns:
                    # Convert date column to datetime
                    df['date_analyzed'] = pd.to_datetime(df['date_analyzed'], errors='coerce')
                    
                    min_date = df['date_analyzed'].min().date()
                    max_date = df['date_analyzed'].max().date()
                    
                    date_range = st.date_input(
                        "Date Range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date
                    )
                    
                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        df = df[
                            (df['date_analyzed'].dt.date >= start_date) &
                            (df['date_analyzed'].dt.date <= end_date)
                        ]
            
            with col3:
                # Viability score filter
                if 'overall_score' in df.columns:
                    score_options = ['All'] + sorted(df['overall_score'].unique().tolist())
                    selected_score = st.selectbox("Viability Score", score_options)
                    
                    if selected_score != 'All':
                        df = df[df['overall_score'] == selected_score]
            
            # Pipeline summary metrics
            if not df.empty:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Deals", len(df))
                
                with col2:
                    if 'asking_price' in df.columns:
                        total_value = df['asking_price'].sum()
                        st.metric("Total Value", format_currency(total_value))
                
                with col3:
                    if 'overall_score' in df.columns:
                        green_count = (df['overall_score'] == 'green').sum()
                        st.metric("Viable Deals", f"{green_count}/{len(df)}")
                
                with col4:
                    if 'residual_land_value' in df.columns:
                        avg_residual = df['residual_land_value'].mean()
                        st.metric("Avg Residual", format_currency(avg_residual))
            
            # Pipeline table
            st.subheader("📋 Deal Pipeline")
            
            # Prepare display columns
            display_cols = [
                'site_name', 'city_key', 'date_analyzed', 'asking_price', 
                'residual_land_value', 'land_pct_gdv', 'overall_score', 'overall_status'
            ]
            
            available_cols = [col for col in display_cols if col in df.columns]
            
            if available_cols:
                # Create a copy for display formatting
                display_df = df[available_cols].copy()
                
                # Format columns for better display
                if 'asking_price' in display_df.columns:
                    display_df['Asking Price'] = display_df['asking_price'].apply(
                        lambda x: format_currency(x) if pd.notnull(x) else 'N/A'
                    )
                
                if 'residual_land_value' in display_df.columns:
                    display_df['Residual Value'] = display_df['residual_land_value'].apply(
                        lambda x: format_currency(x) if pd.notnull(x) else 'N/A'
                    )
                
                if 'land_pct_gdv' in display_df.columns:
                    display_df['Land % GDV'] = display_df['land_pct_gdv'].apply(
                        lambda x: f"{x:.1f}%" if pd.notnull(x) else 'N/A'
                    )
                
                if 'date_analyzed' in display_df.columns:
                    display_df['Date'] = display_df['date_analyzed'].dt.strftime('%Y-%m-%d')
                
                # Create status column with color indicators
                if 'overall_score' in display_df.columns and 'overall_status' in display_df.columns:
                    display_df['Status'] = display_df.apply(
                        lambda row: f"{get_color_indicator(row['overall_score'])} {row['overall_status']}" 
                        if pd.notnull(row['overall_score']) and pd.notnull(row['overall_status'])
                        else 'N/A', 
                        axis=1
                    )
                
                # Select final display columns
                final_cols = ['site_name', 'city_key']
                if 'Date' in display_df.columns:
                    final_cols.append('Date')
                if 'Asking Price' in display_df.columns:
                    final_cols.append('Asking Price')
                if 'Residual Value' in display_df.columns:
                    final_cols.append('Residual Value')
                if 'Land % GDV' in display_df.columns:
                    final_cols.append('Land % GDV')
                if 'Status' in display_df.columns:
                    final_cols.append('Status')
                
                # Rename columns for display
                column_mapping = {
                    'site_name': 'Site Name',
                    'city_key': 'City'
                }
                
                display_df = display_df.rename(columns=column_mapping)
                final_display_cols = [column_mapping.get(col, col) for col in final_cols]
                
                # Show the table
                st.dataframe(
                    display_df[final_display_cols], 
                    use_container_width=True,
                    hide_index=True
                )
                
                # Deal distribution chart
                if 'overall_score' in df.columns:
                    st.subheader("📈 Deal Viability Distribution")
                    
                    score_counts = df['overall_score'].value_counts()
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Pie chart
                        import plotly.express as px
                        colors = {'green': '#00D4AA', 'yellow': '#FFD700', 'red': '#FF6B6B'}
                        
                        fig = px.pie(
                            values=score_counts.values,
                            names=score_counts.index,
                            title="Deal Viability Distribution",
                            color=score_counts.index,
                            color_discrete_map=colors
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Bar chart
                        fig_bar = px.bar(
                            x=score_counts.index,
                            y=score_counts.values,
                            title="Deal Count by Score",
                            color=score_counts.index,
                            color_discrete_map=colors,
                            labels={'x': 'Viability Score', 'y': 'Count'}
                        )
                        st.plotly_chart(fig_bar, use_container_width=True)
                
                # Land % GDV vs Residual scatter plot
                if 'land_pct_gdv' in df.columns and 'residual_land_value' in df.columns:
                    st.subheader("🎯 Deal Analysis Matrix")
                    
                    fig_scatter = px.scatter(
                        df,
                        x='land_pct_gdv',
                        y='residual_land_value',
                        color='overall_score' if 'overall_score' in df.columns else None,
                        hover_name='site_name',
                        title="Land % GDV vs Residual Land Value",
                        labels={
                            'land_pct_gdv': 'Land % of GDV',
                            'residual_land_value': 'Residual Land Value ($)'
                        },
                        color_discrete_map={'green': '#00D4AA', 'yellow': '#FFD700', 'red': '#FF6B6B'}
                    )
                    
                    # Add benchmark lines
                    fig_scatter.add_hline(y=0, line_dash="dash", annotation_text="Break-even", line_color="red")
                    fig_scatter.add_vline(x=15, line_dash="dash", annotation_text="Min Land % (15%)", line_color="gray")
                    fig_scatter.add_vline(x=30, line_dash="dash", annotation_text="Max Land % (30%)", line_color="gray")
                    
                    st.plotly_chart(fig_scatter, use_container_width=True)
                
                # Download CSV button
                st.subheader("📥 Export Data")
                
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="Download Pipeline as CSV",
                    data=csv,
                    file_name=f"pipeline_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                
            else:
                st.warning("No displayable columns found in the data.")
        
        else:
            st.info("No deals found in the pipeline.")
            st.markdown("**Get started by adding your first deal!**")
            st.page_link("pages/1_Add_Deal.py", label="➕ Add Deal")
    
    else:
        st.info("No acquisitions data found.")
        st.markdown("**Get started by adding your first deal!**")
        st.page_link("pages/1_Add_Deal.py", label="➕ Add Deal")

except Exception as e:
    st.error(f"Error loading pipeline data: {e}")
    st.info("Please check your data files and try again.")

# Footer with helpful info
st.markdown("---")
st.markdown("""
**Pipeline Tips:**
- Use filters to narrow down your deal analysis
- Green deals are viable, yellow need attention, red are not recommended
- Target land % of GDV between 15-30% for healthy deals
- Download the CSV for external analysis
""")