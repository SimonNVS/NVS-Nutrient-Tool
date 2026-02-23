import streamlit as st
from fpdf import FPDF

st.title("Nitrate Ventures Calculator")

# Inputs
dwellings = st.number_input("Number of Dwellings", value=20)
budget = dwellings * 1.5 # Simple placeholder math

st.write(f"Final Budget: {budget} kg/yr")

# PDF Function - Simplified
def create_pdf(val):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(40, 10, "NITRATE VENTURES REPORT")
    pdf.ln(20)
    pdf.set_font("Arial", size=12)
    pdf.cell(40, 10, f"Total Dwellings: {dwellings}")
    pdf.ln(10)
    pdf.cell(40, 10, f"Total Nitrogen Budget: {val} kg/yr")
    return pdf.output(dest='S').encode('latin-1')

# The Button
if st.button("Generate Report"):
    pdf_data = create_pdf(budget)
    st.download_button(
        label="Download PDF Now",
        data=pdf_data,
        file_name="Nitrate_Report.pdf",
        mime="application/pdf"
    )
