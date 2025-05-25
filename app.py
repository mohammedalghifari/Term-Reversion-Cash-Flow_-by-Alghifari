import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="10-Year Term & Reversion Cash Flow", layout="centered")
st.title("🏢 Multi-Tenant Property Cash Flow Tool")
st.markdown("Upload lease data with year-wise rents, set valuation date, and generate a 10-year rent cash flow including reversion.")

# Generate sample data for download
sample_data = pd.DataFrame({
    "Tenant": ["Tenant A", "Tenant B"],
    "Lease Start": ["2023-01-01", "2024-06-01"],
    "Lease End": ["2027-12-31", "2029-05-31"],
    "Market Rent (AED/year)": [120000, 140000],
    "Passing Rent 2023": [100000, 0],
    "Passing Rent 2024": [102000, 120000],
    "Passing Rent 2025": [104000, 123000],
    "Passing Rent 2026": [106000, 126000],
    "Passing Rent 2027": [108000, 129000],
    "Passing Rent 2028": [0, 132000],
    "Passing Rent 2029": [0, 135000],
})

sample_output = BytesIO()
with pd.ExcelWriter(sample_output, engine='openpyxl') as writer:
    sample_data.to_excel(writer, index=False, sheet_name="Sample Data")
sample_output.seek(0)

st.download_button(
    label="⬇️ Download Sample Excel Format",
    data=sample_output,
    file_name="sample_lease_data.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Upload Excel file
uploaded_file = st.file_uploader("📁 Upload Lease Excel File", type=["xlsx"])

# Input valuation date
valuation_date_input = st.date_input("📅 Valuation Date", value=datetime.today())

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        st.success("✅ Lease data loaded successfully.")

        # Convert date columns to datetime
        df['Lease Start'] = pd.to_datetime(df['Lease Start'])
        df['Lease End'] = pd.to_datetime(df['Lease End'])

        # Get valuation year and list of relevant years from headers
        valuation_year = valuation_date_input.year
        all_years = sorted([int(col.split()[-1]) for col in df.columns if col.startswith("Passing Rent ")])
        selected_years = [y for y in all_years if valuation_year <= y < valuation_year + 10]

        # Build cash flow matrix
        cashflow_matrix = []
        for idx, row in df.iterrows():
            tenant_row = []
            for year in selected_years:
                col_name = f"Passing Rent {year}"
                start_of_year = pd.Timestamp(f"{year}-01-01")
                end_of_year = pd.Timestamp(f"{year}-12-31")

                if row['Lease End'] < start_of_year:
                    tenant_row.append(round(row['Market Rent (AED/year)'], 2))
                elif row['Lease Start'] > end_of_year:
                    tenant_row.append(0)
                else:
                    tenant_row.append(round(row.get(col_name, 0), 2))
            cashflow_matrix.append(tenant_row)

        cashflow_df = pd.DataFrame(cashflow_matrix, columns=[str(y) for y in selected_years])
        cashflow_df.insert(0, 'Tenant', df['Tenant'])

        st.subheader("💰 10-Year Term & Reversion Cash Flow")
        st.dataframe(cashflow_df)

        # Export to Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            cashflow_df.to_excel(writer, index=False, sheet_name="Cash Flow")
        output.seek(0)

        st.download_button(
            label="⬇️ Download Cash Flow Excel",
            data=output,
            file_name="10_year_cash_flow.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ Error: {e}")
