"""
Configs Viewer page for TerraFlow dashboard.
Shows configuration files if they exist (optional MVP feature).
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import yaml
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    from utils.io import get_project_root
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Make sure you're running from the project root directory")

st.title("⚙️ Configs Viewer")
st.markdown("View system configuration files and settings.")

# Check for configs directory
try:
    configs_path = get_project_root() / "configs"
    
    if configs_path.exists() and configs_path.is_dir():
        # List available config directories (ISO codes)
        iso_dirs = [d for d in configs_path.iterdir() if d.is_dir() and d.name != '__pycache__']
        
        if iso_dirs:
            st.success(f"Found {len(iso_dirs)} configuration directories.")
            
            # ISO/Country selection
            iso_names = [d.name for d in iso_dirs]
            selected_iso = st.selectbox("Select Country/Region", iso_names)
            
            if selected_iso:
                iso_path = configs_path / selected_iso
                
                # Look for standard config files
                standard_configs = ['country.yml', 'finance.yml', 'zoning.yml', 'market.yml', 'global.yml']
                
                st.subheader(f"📁 {selected_iso} Configuration Files")
                
                # Check which config files exist
                existing_configs = []
                for config_file in standard_configs:
                    config_path = iso_path / config_file
                    if config_path.exists():
                        existing_configs.append(config_file)
                
                # Also check for any other YAML files
                other_configs = [f.name for f in iso_path.glob("*.yml") if f.name not in standard_configs]
                other_configs.extend([f.name for f in iso_path.glob("*.yaml") if f.name.replace('.yaml', '.yml') not in standard_configs])
                
                all_configs = existing_configs + other_configs
                
                if all_configs:
                    selected_config = st.selectbox("Select Configuration File", all_configs)
                    
                    if selected_config:
                        config_file_path = iso_path / selected_config
                        
                        try:
                            # Read and display the configuration file
                            with open(config_file_path, 'r', encoding='utf-8') as f:
                                config_content = f.read()
                                config_data = yaml.safe_load(config_content)
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("📋 Configuration Data")
                                
                                # Display as JSON for better formatting
                                st.json(config_data)
                            
                            with col2:
                                st.subheader("📄 Raw YAML Content")
                                st.code(config_content, language='yaml')
                            
                            # Configuration summary based on file type
                            st.subheader("📊 Configuration Summary")
                            
                            if selected_config == 'country.yml':
                                st.markdown("**Country-Specific Settings**")
                                if 'country' in config_data:
                                    country_info = config_data['country']
                                    col1, col2, col3 = st.columns(3)
                                    
                                    with col1:
                                        st.metric("Country", country_info.get('name', 'N/A'))
                                        st.metric("Currency", country_info.get('currency', 'N/A'))
                                    
                                    with col2:
                                        st.metric("Language", country_info.get('language', 'N/A'))
                                        st.metric("Timezone", country_info.get('timezone', 'N/A'))
                                    
                                    with col3:
                                        if 'tax_rates' in country_info:
                                            tax_info = country_info['tax_rates']
                                            st.metric("VAT Rate", f"{tax_info.get('vat', 0) * 100:.1f}%")
                                            st.metric("Capital Gains", f"{tax_info.get('capital_gains', 0) * 100:.1f}%")
                            
                            elif selected_config == 'finance.yml':
                                st.markdown("**Financial Parameters**")
                                if 'finance' in config_data:
                                    finance_info = config_data['finance']
                                    
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        if 'lending' in finance_info:
                                            lending = finance_info['lending']
                                            st.metric("Max LTV", f"{lending.get('max_ltv', 0) * 100:.0f}%")
                                            st.metric("Interest Rate", f"{lending.get('base_rate', 0) * 100:.2f}%")
                                    
                                    with col2:
                                        if 'costs' in finance_info:
                                            costs = finance_info['costs']
                                            st.metric("Legal Fees", f"{costs.get('legal_fees_pct', 0) * 100:.1f}%")
                                            st.metric("Due Diligence", f"${costs.get('due_diligence_cost', 0):,}")
                            
                            elif selected_config == 'zoning.yml':
                                st.markdown("**Zoning Regulations**")
                                if 'zoning' in config_data:
                                    zoning_info = config_data['zoning']
                                    
                                    if 'zones' in zoning_info:
                                        zones = zoning_info['zones']
                                        zone_names = list(zones.keys())
                                        
                                        selected_zone = st.selectbox("Select Zoning Type", zone_names)
                                        
                                        if selected_zone and selected_zone in zones:
                                            zone_data = zones[selected_zone]
                                            
                                            col1, col2, col3 = st.columns(3)
                                            
                                            with col1:
                                                st.metric("Max FAR", zone_data.get('max_far', 'N/A'))
                                                st.metric("Max Coverage", f"{zone_data.get('max_coverage', 0) * 100:.0f}%")
                                            
                                            with col2:
                                                st.metric("Max Height", f"{zone_data.get('max_height_m', 'N/A')} m")
                                                st.metric("Max Floors", zone_data.get('max_floors', 'N/A'))
                                            
                                            with col3:
                                                if 'setbacks' in zone_data:
                                                    setbacks = zone_data['setbacks']
                                                    st.metric("Front Setback", f"{setbacks.get('front_m', 'N/A')} m")
                                                    st.metric("Side Setback", f"{setbacks.get('side_m', 'N/A')} m")
                            
                            elif selected_config == 'market.yml':
                                st.markdown("**Market Configuration**")
                                if 'market' in config_data:
                                    market_info = config_data['market']
                                    
                                    if 'locations' in market_info:
                                        locations = market_info['locations']
                                        st.metric("Market Locations", len(locations))
                                        
                                        # Show location summary
                                        location_data = []
                                        for loc_key, loc_data in locations.items():
                                            location_data.append({
                                                'Location': loc_data.get('name', loc_key),
                                                'Tier': loc_data.get('tier', 'N/A'),
                                                'Demand Score': loc_data.get('demand_score', 'N/A'),
                                                'Liquidity Score': loc_data.get('liquidity_score', 'N/A')
                                            })
                                        
                                        if location_data:
                                            locations_df = pd.DataFrame(location_data)
                                            st.dataframe(locations_df, hide_index=True, width="stretch")
                            
                            # Export functionality
                            st.subheader("📥 Export Configuration")
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                # Download as JSON
                                json_data = json.dumps(config_data, indent=2)
                                st.download_button(
                                    label="Download as JSON",
                                    data=json_data,
                                    file_name=f"{selected_iso}_{selected_config.replace('.yml', '.json')}",
                                    mime="application/json"
                                )
                            
                            with col2:
                                # Download original YAML
                                st.download_button(
                                    label="Download as YAML",
                                    data=config_content,
                                    file_name=f"{selected_iso}_{selected_config}",
                                    mime="text/yaml"
                                )
                        
                        except Exception as e:
                            st.error(f"Error reading configuration file: {e}")
                            st.info("The file may be corrupted or have invalid YAML syntax.")
                
                else:
                    st.warning(f"No configuration files found in {selected_iso}/")
                    st.info("Expected files: country.yml, finance.yml, zoning.yml, market.yml")
                
                # Show all files in directory
                all_files = list(iso_path.glob("*"))
                if all_files:
                    st.subheader("📂 All Files in Directory")
                    
                    file_info = []
                    for file_path in all_files:
                        if file_path.is_file():
                            file_info.append({
                                'File': file_path.name,
                                'Size': f"{file_path.stat().st_size} bytes",
                                'Type': file_path.suffix or 'No extension'
                            })
                    
                    if file_info:
                        files_df = pd.DataFrame(file_info)
                        st.dataframe(files_df, hide_index=True, width="stretch")
        
        else:
            st.info("No configuration directories found.")
            st.markdown("""
            **Expected structure:**
            ```
            configs/
            ├── UAE/
            │   ├── country.yml
            │   ├── finance.yml
            │   ├── zoning.yml
            │   └── market.yml
            ├── JO/
            │   └── country.yml
            └── default/
                └── global.yml
            ```
            """)
    
    else:
        st.info("No configs directory found.")
        st.markdown("**Configuration files are optional in the MVP.**")
        
        # Show example configuration
        st.subheader("📋 Example Configuration Structure")
        
        example_config = {
            "country": {
                "name": "United Arab Emirates",
                "code": "AE",
                "currency": "AED",
                "language": "en",
                "timezone": "Asia/Dubai"
            },
            "zoning": {
                "zones": {
                    "residential": {
                        "max_far": 2.0,
                        "max_coverage": 0.6,
                        "max_height_m": 45,
                        "max_floors": 15
                    }
                }
            },
            "finance": {
                "lending": {
                    "max_ltv": 0.75,
                    "base_rate": 0.045
                }
            }
        }
        
        st.json(example_config)

except Exception as e:
    st.error(f"Error accessing configurations: {e}")
    st.info("Please check your file permissions and try again.")

# Footer
st.markdown("---")
st.markdown("""
**Configuration Notes:**
- Configuration files are optional in this MVP
- Configurations can override default system parameters
- YAML format is used for easy editing and version control
- Each country/region can have its own specific settings
""")