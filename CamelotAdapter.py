import camelot
from pathlib import Path
from typing import Any,IO
from camelot.core import TableList
from BaseTableAdapter import BaseTableAdapter
from OpenPyxlAdapter import OpenPyxlAdapter
FilepathOrBuffer = str | Path | bytes | bytearray | memoryview | IO[bytes]

class CamelotAdapter(BaseTableAdapter):
    def __init__(self,**read_pdf_kwargs: Any) -> None:
        self.read_pdf_kwargs: dict[str, Any] = {**read_pdf_kwargs}

    def __enter__(self) -> 'CamelotAdapter':
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    def extract_tables(self,filepath:FilepathOrBuffer,min_columns:int = 5,min_accuracy:float = 95.0) -> list[list[Any]] | None :
        tables:TableList = camelot.read_pdf(filepath=filepath,**self.read_pdf_kwargs)
        if tables.n < 1:return None
        tables:TableList = tables.filter(min_columns=min_columns,min_accuracy=min_accuracy)
        tables:TableList = tables.stack_contiguous(match= "column_count",keep_first_header = True)
        cleaned_rows: list[list[Any]] = []
        for table in tables:
            table_data: list[list[Any]] = table.data
            for row in table_data:
                cleaned_row:list[Any] = [self.parse_value(cell) if cell else "" for cell in row]
                if any(cleaned_row):
                    cleaned_rows.append(cleaned_row)
        
        return self.remove_duplicates(cleaned_rows)

if __name__ == "__main__":
    read_pdf_kwargs: dict = {
                "pages":"all",
                "flavor": "hybrid", # 'lattice', 'stream', 'network', 'hybrid', 'ml' or 'auto'
                "engine": "combined", # combined or vector
                "process_background": False,
                "line_scale": 40,
                "strip_text": ",",
                "replace_text":{" \n": " "},
                "parallel": True,
        }
    filepath: str = "input/28-borderless.pdf"
    excel_path: str = "output/"+Path(filepath).stem+".xlsx"
    camelotAdapter = CamelotAdapter(**read_pdf_kwargs)
    with CamelotAdapter(**read_pdf_kwargs) as pdf:
        tables: list[list[Any]] | None = pdf.extract_tables(filepath=filepath)
        if not tables:
            print("Empty")
            exit()
    with OpenPyxlAdapter(excel_path, "Camelot") as excel:
        excel.write_rows(tables, freeze_header=True, bold_header=True, auto_fit=True)
    print("Success")

# def filter_best_tables_by_page(self) -> list[Table]:
#         best_confidence_by_page:dict[str,float] = {}
#         best_table_by_page:dict[str,Table] = {}

#         for table in self.page_table:
#             report = table.parsing_report
#             page:int = report.get("page",-1)
#             confidence:int = report.get("confidence",-1)

#             if page < 0 or confidence < 0:
#                 continue

#             key = f"page-{page}"
#             if best_confidence_by_page.get(key, float("-inf")) > confidence:
#                 continue

#             best_confidence_by_page[key] = confidence
#             best_table_by_page[key] = table

#         return list(best_table_by_page.values())