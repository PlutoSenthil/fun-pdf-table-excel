import pdfplumber

class pdfplumberAdapter:
    def __init__(self, pdf_path: str) -> None:
        self.pdf = pdfplumber.open(pdf_path)
        self.pages = self.pdf.pages
    
    def __enter__(self) -> 'pdfplumberAdapter':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.pdf.close()

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def tables_count(self) -> int:
        return len(self.extract_tables())

    def extract_tables(self, table_settings=None) -> list[list[str]]:
        settings = table_settings or {}
        cleaned_rows = []
        for page in self.pages:
            for table in (page.extract_tables(table_settings=settings) or []):
                for row in table:
                    cleaned_rows.append([cell.replace("\n", " ").strip() if cell else "" for cell in row])
        return cleaned_rows