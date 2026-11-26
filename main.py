import os
import tempfile
import streamlit as st
from typing import Any
from CamelotAdapter import CamelotAdapter,FLAVOR_CONFIGS
from OpenPyxlAdapter import OpenPyxlAdapter

st.session_state.setdefault("key", 0)
st.session_state.setdefault("no_tables_found", False)

def reset():
    st.session_state.pop("excel_data", None)
    st.session_state["no_tables_found"] = False
    st.session_state["key"] += 1

st.title("Camelot PDF to Excel Table")

if st.session_state["no_tables_found"]:
    st.warning(
        "**No tables were found in this PDF across any Camelot flavor.**\n\n"
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
        key=st.session_state["key"],
    )

    if uploaded_file and st.button("Extract Tables", type="primary", icon="📊"):
        with tempfile.TemporaryDirectory() as tmp:
            pdf_path = os.path.join(tmp, uploaded_file.name)
            excel_name = f"{os.path.splitext(uploaded_file.name)[0]}.xlsx"
            excel_path = os.path.join(tmp, excel_name)

            with open(pdf_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            has_any_data = False

            for sheet_name, kwargs in FLAVOR_CONFIGS.items():
                try:
                    with CamelotAdapter(**kwargs) as pdf:
                        tables: list[list[Any]] | None = pdf.extract_tables(filepath=pdf_path)
                except Exception as e:
                    continue

                if tables and any(tables):
                    has_any_data = True
                    with OpenPyxlAdapter(excel_path, sheet_name) as excel:
                        excel.write_rows(
                            tables,
                            freeze_header=True,
                            bold_header=True,
                            auto_fit=True,
                        )

            if not has_any_data:
                st.session_state["no_tables_found"] = True
                st.rerun()

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
        icon="⬇️",
    )