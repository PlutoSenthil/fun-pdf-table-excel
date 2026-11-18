from pdfplumberAdapter import pdfplumberAdapter
from OpenPyxlAdapter import OpenPyxlAdapter
import os
os.makedirs("input", exist_ok=True)
os.makedirs("output", exist_ok=True)

pdf_filename = "Axis - Prime Bio 915020021859161-01-04-2023to31-03-2024.pdf"
pdf_path = os.path.join("input", pdf_filename)
excel_filename = os.path.splitext(pdf_filename)[0] + ".xlsx"
excel_path = os.path.join("output", excel_filename)
sheet_name = "OpenPyxl"

with OpenPyxlAdapter(excel_path, sheet_name) as excel, pdfplumberAdapter(pdf_path) as pdf:
    excel.write_rows(pdf.extract_tables(), freeze_header=True, bold_header=True,auto_fit=True)