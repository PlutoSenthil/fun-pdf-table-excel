import pandas as pd
import pdfplumber
print("pdfplumber.__version__", pdfplumber.__version__)

class pdfplumberAdapter:
    def __init__(self, pdf_path) -> None:
        self.pdf_path = pdf_path
        self.pdf = pdfplumber.open(pdf_path)
        self.pages = self.pdf.pages
    
    def __enter__(self) -> 'pdfplumberAdapter':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.pdf:
            self.pdf.close()

    @property
    def page_count(self) -> int:
        """Returns the total number of pages in the PDF."""
        return len(self.pages)

    @property
    def tables_count(self) -> int:
        """Returns the total number of tables found across all pages."""
        return len(self.extract_all_tables())

    @property
    def table_count(self) -> int:
        """Returns the total number of tables found across all pages."""
        return len(self.extract_all_table())
    
    @property
    def page_wise_table_counts(self) -> list[dict]:
        """Returns the table count for each individual page."""
        return [{"page": i, "count": len(p.extract_tables() or [])} 
                for i, p in enumerate(self.pages, start=1)]

    def extract_full_text(self, layout=True) -> str:
        """Returns the entire PDF text combined into a single string with page number separators."""
        return "\n".join([
            f"=== PAGE {i} ===\n{page.extract_text(layout=layout) or ''}" 
            for i, page in enumerate(self.pages, start=1)
        ])

    def extract_all_tables(self, table_settings={}) -> list[dict]:
        """Returns the text extracted from all tables found on the page."""
        return [{"page": i, "table": t} 
                for i, p in enumerate(self.pages, start=1) 
                for t in (p.extract_tables(table_settings=table_settings) or [])]

    def extract_all_table(self, table_settings={}) -> list[dict]:
        """Returns the text extracted from the largest table on the page."""
        return [{"page": i, "table": t} 
                for i, p in enumerate(self.pages, start=1) 
                for t in [p.extract_table(table_settings=table_settings)] 
                if t is not None]

    def find_tables(self, table_settings={}) -> list[dict]:
        """Returns a list of Table objects along with their page numbers."""
        return [{"page": i, "table": t} 
                for i, p in enumerate(self.pages, start=1) 
                for t in (p.find_tables(table_settings=table_settings) or [])]

    def find_table(self, table_settings={}) -> list[dict]:
        """Returns the largest table on the page as a Table object."""
        return [{"page": i, "table": t} 
                for i, p in enumerate(self.pages, start=1) 
                for t in [p.find_table(table_settings=table_settings)] 
                if t is not None]