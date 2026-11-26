import re
from typing import Any
import playa
from playa.document import Document, PageList

class BaseTableAdapter:

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_pdf_page_count(filepath:str):
        buffer:bytes = open(filepath, "rb").read()
        pdf_document:Document = playa.parse(buffer=buffer)
        pdf_page_list:PageList = pdf_document.pages
        total_page_count:int = len(pdf_page_list)
        return total_page_count
    
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

    @staticmethod
    def parse_value(val) -> Any:
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return val

        val_str: str = str(val).replace("\n", " ").strip()
        if not val_str:
            return None

        cleaned_str = val_str.replace(",", "")
        cleaned_str = re.sub(r"(?i)\s*cr$", "", cleaned_str)

        try:
            if "." in cleaned_str:
                return float(cleaned_str)
            return int(cleaned_str)
        except ValueError:
            return val_str