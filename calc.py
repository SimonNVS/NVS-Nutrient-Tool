import streamlit as st
import pandas as pd

# --- APP CONFIGURATION ---
st.set_page_config(page_title="Nitrate Ventures | Nutrient Neutrality Calculator", layout="wide")

# --- STYLING ---
st.markdown("""
    <style>
    /* Background colors and metric boxes */
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .sidebar .sidebar-content { background-image: linear-gradient(#2e7bcf,#2e7bcf); color: white; }
    
    /* Logo styling: White buffer, grey trim, rounded corners */
    [data-testid="stSidebar"] img {
        padding: 20px; 
        background-color: #ffffff; 
        border: 2px solid #808080; 
        border-radius: 8px; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- ADAS MODELLING DATA ---
COEFFICIENTS = {
    "Cereals": 31.2, "Dairy": 36.2, "General cropping": 25.4, 
    "Horticulture": 29.2, "Pig farming": 70.4, "Lowland grazing": 13.0, 
    "Mixed farming": 28.3, "Poultry farming": 70.7, "Urban development": 14.3, 
    "Open space / greenfield": 5.0, "Woodland": 5.0, "Nature reserve": 5.0,
    "Community orchard": 5.0, "Catchment Average": 26.9
}

st.title("🧪 Nitrate Ventures: Nitrogen Load Calculator")
st.subheader("Professional Nutrient Neutrality Assessment Tool")

# --- SIDEBAR INPUTS ---
with st.sidebar:
    st.header("Project Parameters")
    st.image("logo.jpg", use_container_width=True)
    
    st.divider()
    dwellings = st.number_input("Number of Dwellings", min_value=0, value=20)
    occ_rate = st.number_input("Occupancy Rate (NE Standard)", value=2.4)
    water_use = st.number_input("Water Use (L/person/day)", value=110)
    
    st.divider()
    wwtw_permit = st.number_input("WwTW Permit Limit (mg/L)", value=10.0)
    buffer_toggle = st.checkbox("Apply 20% Precautionary Buffer", value=False)

# --- CALCULATIONS ---

# Step 1 & 2: Population & Wastewater
total_pop = dwellings * occ_rate
daily_flow = total_pop * water_use

# Step 3 & 4: WwTW Loading
# Formula: (Permit * 0.9 - 2mg/L natural background)
concentration = (wwtw_permit * 0.9) - 2
annual_wwtw_kg = (daily_flow * concentration / 1_000_000) * 365

# Step 5: Existing Land Use
st.header("Step 5 & 6: Land Use Assessment")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Existing Land Use (Hectares)")
    exist_cereal = st.number_input("Cereals", value=0.0, key="e1")
    exist_dairy = st.number_input("Dairy", value=0.0, key="e2")
    exist_urban = st.number_input("Existing Urban", value=0.5, key="e3")
    exist_woodland = st.number_input("Woodland/Greenfield", value=2.5, key="e4")
    
    exist_load = (exist_cereal * COEFFICIENTS["Cereals"] + 
                  exist_dairy * COEFFICIENTS["Dairy"] + 
                  exist_urban * COEFFICIENTS["Urban development"] + 
                  exist_woodland * COEFFICIENTS["Woodland"])

with col2:
    st.markdown("### Proposed Land Use (Hectares)")
    prop_urban = st.number_input("Proposed Urban", value=1.0, key="p1")
    prop_open = st.number_input("Open Space", value=1.0, key="p2")
    prop_reserve = st.number_input("Nature Reserve", value=1.0, key="p3")
    
    prop_load = (prop_urban * COEFFICIENTS["Urban development"] + 
                 prop_open * COEFFICIENTS["Open space / greenfield"] + 
                 prop_reserve * COEFFICIENTS["Nature reserve"])

# Step 7: Final Budget
st.divider()
st.header("Step 7: Final Nitrogen Budget")

net_land_change = prop_load - exist_load
final_budget = annual_wwtw_kg + net_land_change

if buffer_toggle:
    final_budget *= 1.2

# --- DASHBOARD DISPLAY ---
m1, m2, m3 = st.columns(3)
m1.metric("Wastewater Load", f"{annual_wwtw_kg:.2f} kg/yr")
m2.metric("Net Land Use Change", f"{net_land_change:.2f} kg/yr")

if final_budget <= 0:
    m3.metric("FINAL BUDGET", f"{final_budget:.2f} kg/yr", delta="NEUTRAL", delta_color="normal")
    st.success(f"✅ BOSH! This development is Nutrient Neutral. Credits required: 0")
else:
    m3.metric("FINAL BUDGET", f"{final_budget:.2f} kg/yr", delta="MITIGATION REQUIRED", delta_color="inverse")
    st.error(f"⚠️ Mitigation Required: You need to offset {final_budget:.2f} kg of Nitrogen per year.")

# --- REPORT GENERATION ---
if st.button("Generate Professional PDF Report"):
    st.info("Generating Branded Report...")

st.caption("Data based on ADAS Modelling and Natural England Framework.")