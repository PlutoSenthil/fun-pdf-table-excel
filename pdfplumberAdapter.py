import pdfplumber
import re 

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

    @staticmethod
    def remove_duplicates(rows):
        seen = set()
        unique_rows = []
        for row in rows:
            t = tuple(row)
            if t not in seen:
                seen.add(t)
                unique_rows.append(row)
        return unique_rows
         
    def _parse_value(self, val):
        if val is None:return None
        if isinstance(val, (int, float)):return val
        
        val_str = str(val).replace('\n', ' ').strip()
        if not val_str:return None
        
        cleaned_str = val_str.replace(',', '')
        cleaned_str = re.sub(r'(?i)\s*cr$', '', cleaned_str)
        
        try:
            if '.' in cleaned_str:return float(cleaned_str)
            else:return int(cleaned_str)
        except ValueError:
            return val_str
            
    def extract_tables(self, table_settings=None) -> list[list[str]]:
        settings = table_settings or {}
        cleaned_rows = []
        for page in self.pages:
            for table in (page.extract_tables(table_settings=settings) or []):
                for row in table:
                    cleaned_row = [self._parse_value(cell) if cell else "" for cell in row]
                    if any(cleaned_row):
                        cleaned_rows.append(cleaned_row)
                        
        return self.remove_duplicates(cleaned_rows)