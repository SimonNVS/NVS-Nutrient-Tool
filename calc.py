import streamlit as st
import pandas as pd
from fpdf import FPDF

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

# --- PDF GENERATOR FUNCTION ---
def create_pdf(report_data):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="Nitrate Ventures: Nitrogen Load Report", ln=True, align='C')
    pdf.ln(5)
    
    # Body
    pdf.set_font("Arial", '', 12)
    for key, value in report_data.items():
        # Add a little spacing and bold text for section headers if the value is empty
        if value == "HEADER":
            pdf.ln(4)
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 8, txt=key, ln=True)
            pdf.set_font("Arial", '', 12)
        else:
            pdf.cell(0, 8, txt=f"{key}: {value}", ln=True)
            
    # Output bytes
    return pdf.output(dest='S').encode('latin-1', 'replace')


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
    # Make sure you have a logo.jpg in your folder, or comment this out to test
    try:
        st.image("logo.jpg", use_container_width=True)
    except FileNotFoundError:
        pass # Skips if no logo is found
    
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
    mitigation_status = "Neutral (No credits required)"
else:
    m3.metric("FINAL BUDGET", f"{final_budget:.2f} kg/yr", delta="MITIGATION REQUIRED", delta_color="inverse")
    st.error(f"⚠️ Mitigation Required: You need to offset {final_budget:.2f} kg of Nitrogen per year.")
    mitigation_status = f"Mitigation Required ({final_budget:.2f} kg/yr)"

# --- REPORT GENERATION ---
st.divider()

# 1. Compile the data we want in the PDF
report_data = {
    "--- PROJECT PARAMETERS ---": "HEADER",
    "Number of Dwellings": dwellings,
    "Occupancy Rate": occ_rate,
    "Total Net Population": f"{total_pop:.1f}",
    "Water Use": f"{water_use} L/person/day",
    "WwTW Permit Limit": f"{wwtw_permit} mg/L",
    
    "--- CALCULATED LOADS ---": "HEADER",
    "Annual Wastewater Load": f"{annual_wwtw_kg:.2f} kg/yr",
    "Existing Land Use Load": f"{exist_load:.2f} kg/yr",
    "Proposed Land Use Load": f"{prop_load:.2f} kg/yr",
    "Net Land Use Change": f"{net_land_change:.2f} kg/yr",
    
    "--- FINAL BUDGET ---": "HEADER",
    "Precautionary Buffer Applied": "Yes (20%)" if buffer_toggle else "No",
    "Final Nitrogen Budget": f"{final_budget:.2f} kg/yr",
    "Mitigation Status": mitigation_status
}

# 2. Generate the PDF bytes
pdf_bytes = create_pdf(report_data)

# 3. Streamlit Download Button
st.download_button(
    label="📄 Download NVS PDF Report",
    data=pdf_bytes,
    file_name="Nitrate_Ventures_Report.pdf",
    mime="application/pdf",
    type="primary"
)

st.caption("Data based on ADAS Modelling and Natural England Framework.")
