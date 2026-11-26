import os
from typing import Any 
import openpyxl
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

class OpenPyxlAdapter:
    def __init__(self, filename: str, sheet_name: str = "Sheet 1") -> None:
        self.filename = filename

        if os.path.exists(filename):
            self.workbook = openpyxl.load_workbook(filename)
            if sheet_name in self.workbook.sheetnames:
                del self.workbook[sheet_name]
            self.worksheet = self.workbook.create_sheet(title=sheet_name)
        else:
            self.workbook = openpyxl.Workbook()
            assert self.workbook.active is not None
            self.worksheet = self.workbook.active
            self.worksheet.title = sheet_name
            
    def __enter__(self) -> 'OpenPyxlAdapter':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.workbook.save(self.filename)

    def write_row(self, row_data: list) -> None:
        self.worksheet.append(row_data)

    def write_rows(self, rows: list[list[Any]], freeze_header: bool = False, bold_header: bool = False, auto_fit: bool = False) -> None:
        for row in rows:
            self.write_row(row)
        if rows and freeze_header:
            self.freeze_first_row()
        if rows and bold_header:
            self.bold_first_row()
        if rows and auto_fit:
            self.maximize_columns()

    def freeze_first_row(self) -> None:
        self.worksheet.freeze_panes = "A2"

    def bold_first_row(self) -> None:
        for cell in self.worksheet[1]:
            cell.font = Font(bold=True)

    def maximize_columns(self) -> None:
        for col_idx in range(1, self.worksheet.max_column + 1):
            col_letter = get_column_letter(col_idx)
            max_len = max(
                len(str(self.worksheet.cell(row=row_idx, column=col_idx).value or '')) 
                for row_idx in range(1, self.worksheet.max_row + 1)
            )
            self.worksheet.column_dimensions[col_letter].width = max(max_len + 3, 10)