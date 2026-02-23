import streamlit as st
import pandas as pd
from fpdf import FPDF

def create_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="Nitrogen Load Calculator Report", ln=True, align='C')
    pdf.ln(5)

    # We will iterate through the rows of the Excel sheet.
    # Based on the uploaded sheet, Column index 1 is 'Step', index 2 is 'Description', index 3 is 'Value'
    for index, row in dataframe.iterrows():
        # Clean up NaN values
        col_step = str(row.iloc[1]) if pd.notna(row.iloc[1]) else ""
        col_desc = str(row.iloc[2]) if pd.notna(row.iloc[2]) else ""
        col_val  = str(row.iloc[3]) if pd.notna(row.iloc[3]) else ""
        col_stat = str(row.iloc[4]) if pd.notna(row.iloc[4]) else ""

        # Skip completely blank rows
        if not col_step and not col_desc and not col_val:
            continue

        # If it's a "Step" header (e.g., "Step 1", "Step 2")
        if str(col_step).strip().startswith("Step"):
            pdf.ln(5) # Add a line break before new steps
            pdf.set_font("Arial", 'B', 12)
            pdf.multi_cell(0, 8, txt=f"{col_step}: {col_desc}")
            pdf.set_font("Arial", '', 10) # Reset font for the items under the step
            
        # If it's a data row (Description + Value)
        elif col_desc:
            line_text = f"- {col_desc}"
            if col_val:
                line_text += f": {col_val}"
            if col_stat and col_stat.isupper(): # Picks up tags like "SELECTED"
                line_text += f" [{col_stat}]"
                
            pdf.multi_cell(0, 6, txt=line_text)

    # Return PDF as bytes
    # We use 'replace' to ensure special characters don't crash standard FPDF
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- STREAMLIT APP UI ---
st.set_page_config(page_title="Nitrogen Load to PDF", page_icon="🌱")

st.title("🌱 Nitrogen Load Report Generator")
st.write("Upload your **Nitrogen Load Calculator** Excel file to generate a downloadable PDF summary.")

uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type=['xlsx'])

if uploaded_file:
    try:
        # Read the 'Calculator' sheet specifically, with no headers so we catch the raw grid
        df = pd.read_excel(uploaded_file, sheet_name='Calculator', header=None)
        
        st.success("File successfully loaded!")
        
        # Show a quick preview of the raw data that was extracted
        with st.expander("Preview Raw Data"):
            st.dataframe(df.head(15))
            
        st.markdown("### Ready to Export")
        
        # Generate the PDF in memory
        pdf_bytes = create_pdf(df)
        
        # Streamlit Download Button
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name="Nitrogen_Load_Report.pdf",
            mime="application/pdf"
        )
        
    except Exception as e:
        st.error(f"Error reading the file. Ensure the Excel file has a sheet named 'Calculator'.\nDetails: {e}")
