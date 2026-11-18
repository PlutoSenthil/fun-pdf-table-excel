import os
import tempfile
import streamlit as st
from pdfplumberAdapter import pdfplumberAdapter
from OpenPyxlAdapter import OpenPyxlAdapter

st.session_state.setdefault("key", 0)

def reset():
    st.session_state.pop("excel_data", None)
    st.session_state["key"] += 1

st.title("PDF to Excel Table Extractor")

if "excel_data" not in st.session_state:
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], key=st.session_state["key"])

    if uploaded_file and st.button("Extract Tables"):
        with tempfile.TemporaryDirectory() as tmp:
            pdf_path = os.path.join(tmp, uploaded_file.name)
            excel_name = f"{os.path.splitext(uploaded_file.name)[0]}.xlsx"
            excel_path = os.path.join(tmp, excel_name)

            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with pdfplumberAdapter(pdf_path) as pdf, OpenPyxlAdapter(excel_path, "OpenPyxl") as excel:
                excel.write_rows(pdf.extract_tables(), freeze_header=True, bold_header=True, auto_fit=True)

            with open(excel_path, "rb") as f:
                st.session_state["excel_data"] = (excel_name, f.read())
        st.rerun()
else:
    excel_name, excel_bytes = st.session_state["excel_data"]
    st.success(f"Ready: {excel_name}")
    st.download_button(
        "Download Excel",
        data=excel_bytes,
        file_name=excel_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        on_click=reset
    )