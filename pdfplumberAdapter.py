import pdfplumber
from BaseTableAdapter import BaseTableAdapter

class pdfplumberAdapter(BaseTableAdapter):
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
                    cleaned_row = [self.parse_value(cell) if cell else "" for cell in row]
                    if any(cleaned_row):
                        cleaned_rows.append(cleaned_row)
                        
        return self.remove_duplicates(cleaned_rows)