import xlsxwriter

class XlsxWriterAdapter:
    def __init__(self, filename: str, sheet_name: str = "Sheet 1") -> None:
        self.workbook = xlsxwriter.Workbook(filename)
        self.worksheet = self.workbook.add_worksheet(sheet_name)
        self.current_row = 0

    def __enter__(self) -> 'XlsxWriterAdapter':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.workbook.close()

    def write_row(self, row_data: list) -> None:
        self.worksheet.write_row(self.current_row, 0, row_data)
        self.current_row += 1

    def write_rows(self, rows: list[list]) -> None:
        for row in rows:
            self.write_row(row)