import os
import tempfile
import streamlit as st
from pdfplumberAdapter import pdfplumberAdapter
from OpenPyxlAdapter import OpenPyxlAdapter

st.session_state.setdefault("key", 0)
st.session_state.setdefault("no_tables_found", False)

def reset():
    st.session_state.pop("excel_data", None)
    st.session_state["no_tables_found"] = False
    st.session_state["key"] += 1

st.title("PDF to Excel Table")
st.info(
    "**Note:** Only works with text-based PDFs and not scanned documents. "
    '(As Tabula explains, *"If you can click and drag to select text in your '
    'table in a PDF viewer, then your PDF is text-based."*)',
    icon="ℹ️",
)
if st.session_state["no_tables_found"]:
    st.warning(
        "**No tables were found in this PDF.**\n\n"
        "This usually happens when the file:\n"
        "1. Contains only plain text with no tables.\n"
        "2. Is a scanned document or image.\n"
        "3. Has layouts or spacing that are hard to detect as a table.\n\n"
        "Try uploading a different PDF."
    )
    st.button("Try Uploading Another PDF", on_click=reset, type="primary")

elif "excel_data" not in st.session_state:
    uploaded_file = st.file_uploader(
        "Upload Only One PDF", 
        type=["pdf"], 
        key=st.session_state["key"]
    )

    if uploaded_file and st.button("Extract Tables", type="primary", icon="📊"):
        with tempfile.TemporaryDirectory() as tmp:
            pdf_path = os.path.join(tmp, uploaded_file.name)
            excel_name = f"{os.path.splitext(uploaded_file.name)[0]}.xlsx"
            excel_path = os.path.join(tmp, excel_name)

            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            with pdfplumberAdapter(pdf_path) as pdf:
                tables = pdf.extract_tables()

            # Check if tables is empty (handles [] or [[]] depending on adapter implementation)
            if not tables or not any(tables):
                st.session_state["no_tables_found"] = True
                st.rerun()

            with OpenPyxlAdapter(excel_path, "OpenPyxl") as excel:
                excel.write_rows(tables, freeze_header=True, bold_header=True, auto_fit=True)

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
        on_click=reset,
        type="primary",
        icon="⬇️"
    )