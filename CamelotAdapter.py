import camelot
from pathlib import Path
from typing import Any,IO
from camelot.core import TableList
from BaseTableAdapter import BaseTableAdapter
from OpenPyxlAdapter import OpenPyxlAdapter
FilepathOrBuffer = str | Path | bytes | bytearray | memoryview | IO[bytes]

FLAVOR_CONFIGS: dict[str, dict[str, Any]] = {
    "Lattice": {
        "pages": "all",
        "flavor": "lattice",
        "engine": "combined",
        "process_background": False,
        "line_scale": 40,
        "shift_text": [""],
        "split_text": False,
        "flag_size": False,
        "strip_text": ",",
        "replace_text": {"\n": " "},
        "parallel": True,
    },
    "Stream": {
        "pages": "all",
        "flavor": "stream",
        "edge_tol": 50,
        "row_tol": 2,
        "column_tol": 0,
        "split_text": True,
        "flag_size": False,
        "strip_text": ",",
        "replace_text": {"\n": " "},
        "parallel": True,
    },
    "Network": {
        "pages": "all",
        "flavor": "network",
        "edge_tol": 50,
        "row_tol": 2,
        "column_tol": 0,
        "split_text": True,
        "flag_size": False,
        "strip_text": ",",
        "replace_text": {"\n": " "},
        "parallel": True,
    },
    "Hybrid": {
        "pages": "all",
        "flavor": "hybrid",
        "engine": "combined",
        "process_background": False,
        "line_scale": 40,
        "edge_tol": 50,
        "row_tol": 2,
        "split_text": True,
        "flag_size": False,
        "strip_text": ",",
        "replace_text": {"\n": " "},
        "parallel": True,
    }
}

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
    filepath: str = "input/12-borderless.pdf"
    excel_path: str = "output/" + Path(filepath).stem + ".xlsx"

    # Remove old output file so stale sheets do not remain
    Path(excel_path).unlink(missing_ok=True)

    for sheet_name, kwargs in FLAVOR_CONFIGS.items():
        try:
            with CamelotAdapter(**kwargs) as pdf:
                tables = pdf.extract_tables(filepath=filepath)
        except Exception as e:
            print(f"[{sheet_name}] Failed: {e}")
            continue

        if not tables:
            print(f"[{sheet_name}] Empty")
            continue

        with OpenPyxlAdapter(excel_path, sheet_name) as excel:
            excel.write_rows(tables, freeze_header=True, bold_header=True, auto_fit=True)
        print(f"[{sheet_name}] Wrote {len(tables)} rows")