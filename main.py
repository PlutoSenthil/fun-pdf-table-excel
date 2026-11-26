import os
import tempfile
from typing import Any
import streamlit as st
from CamelotAdapter import CamelotAdapter, FLAVOR_CONFIGS
from OpenPyxlAdapter import OpenPyxlAdapter
from pdfplumberAdapter import pdfplumberAdapter

st.session_state.setdefault("key", 0)
st.session_state.setdefault("no_tables_found", False)


def reset() -> None:
    st.session_state.pop("excel_data", None)
    st.session_state["no_tables_found"] = False
    st.session_state["key"] += 1


def has_rows(tables: list[list[Any]] | None) -> bool:
    return bool(tables and any(tables))


st.title("PDF to Excel Table")
st.info(
    "**Note:** Only works with text-based PDFs and not scanned documents. "
    '(As Tabula explains, *"If you can click and drag to select text in your '
    'table in a PDF viewer, then your PDF is text-based."*)',
    icon="ℹ️",
)

if st.session_state["no_tables_found"]:
    st.warning(
        "**No tables were found in this PDF using pdfplumber or any Camelot flavor.**\n\n"
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

            # 1. Default: try pdfplumber first
            status = st.status("Extracting tables...pdfplumber", expanded=False)
            try:
                with pdfplumberAdapter(pdf_path) as pdf:
                    plumber_tables:list[list[Any]] = pdf.extract_tables()
            except Exception:
                plumber_tables = []

            if has_rows(plumber_tables):
                status.update(label="Extracted tables with pdfplumber", state="complete")
                has_any_data = True
                with OpenPyxlAdapter(excel_path, "pdfplumber") as excel:
                    excel.write_rows(
                        plumber_tables,
                        freeze_header=True,
                        bold_header=True,
                        auto_fit=True,
                    )
            else:
                # 2. Fallback: try Camelot flavors when pdfplumber returns empty
                status.update(label="Extracting tables... Camelot...", state="running")
                for sheet_name, kwargs in FLAVOR_CONFIGS.items():
                    try:
                        with CamelotAdapter(**kwargs) as pdf:
                            camelot_tables: list[list[Any]]  = pdf.extract_tables(
                                filepath=pdf_path
                            )
                    except Exception:
                        camelot_tables = []

                    if has_rows(camelot_tables):
                        has_any_data = True
                        with OpenPyxlAdapter(excel_path, sheet_name) as excel:
                            excel.write_rows(
                                camelot_tables,
                                freeze_header=True,
                                bold_header=True,
                                auto_fit=True,
                            )
                        status.update(label="Extracted tables with Camelot", state="complete")

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