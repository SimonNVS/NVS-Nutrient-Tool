import streamlit as st
from fpdf import FPDF

# --- 1. THE APP SETUP ---
st.set_page_config(page_title="Nitrate Ventures | Calculator", layout="wide")

st.title("💧 Nitrate Ventures: Nutrient Assessment")

# --- 2. ALL YOUR INPUTS ARE BACK ---
with st.sidebar:
    st.header("Project Details")
    dwellings = st.number_input("Number of Dwellings", min_value=1, value=20)
    occ_rate = st.number_input("Occupancy Rate", value=2.4)
    wwtw_permit = st.number_input("WwTW Permit (mg/L)", value=10.0)
    st.divider()
    credit_price = st.number_input("Credit Price (£/kg)", value=3500)

# --- 3. THE MATH (Stour Catchment Logic) ---
total_pop = dwellings * occ_rate
concentration = (wwtw_permit * 0.9) - 2
annual_wwtw_kg = ((total_pop * 110) * concentration / 1_000_000) * 365

# Simple Land Use Change
net_land_change = (dwellings * 0.03 * 14.3) - (dwellings * 0.03 * 5.0)
final_budget = (annual_wwtw_kg + net_land_change) * 1.2 # 20% Buffer
revenue = abs(final_budget) * credit_price

# --- 4. DISPLAY THE DASHBOARD ---
col1, col2, col3 = st.columns(3)
col1.metric("Nitrogen Load", f"{annual_wwtw_kg:.2f} kg/yr")
col2.metric("Land Change", f"{net_land_change:.2f} kg/yr")
col3.metric("Total Budget", f"{final_budget:.2f} kg/yr")

st.divider()

if final_budget > 0:
    st.error(f"⚠️ Mitigation Required: £{revenue:,.2f}")
else:
    st.success(f"✅ Potential Credit Revenue: £{revenue:,.2f}")

# --- 5. THE PDF GENERATOR (The "Secret Sauce") ---
def create_pdf(b_val, r_val, d_val):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 20, "NITRATE VENTURES", ln=True, align="C")
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Nutrient Neutrality Assessment Report", ln=True, align="C")
    pdf.ln(10)
    
    # Data Rows
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Project Size: {d_val} Dwellings", ln=True)
    pdf.cell(0, 10, f"Total Nitrogen Budget: {b_val:.2f} kg/year", ln=True)
    pdf.cell(0, 10, f"Total Financial Forecast: GBP {r_val:,.2f}", ln=True)
    
    pdf.ln(20)
    pdf.set_font("Arial", 'I', 10)
    pdf.multi_cell(0, 10, "Disclaimer: This report is generated based on ADAS coefficients and the 20% precautionary buffer required for the Stour Catchment.")
    
    # Return the PDF as bytes
    return pdf.output(dest='S').encode('latin-1')

# --- 6. THE DOWNLOAD BUTTON ---
st.divider()
st.subheader("Final NVS Documentation")

# We pre-calculate the PDF data here
pdf_data = create_pdf(final_budget, revenue, dwellings)

st.download_button(
    label="📥 Download Official NVS Assessment (PDF)",
    data=pdf_data,
    file_name="Nitrate_Ventures_Report.pdf",
    mime="application/pdf"
)
