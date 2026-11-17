import json
from pdfplumberAdapter import pdfplumberAdapter

pdf_path = "data/Axis - Prime Bio 915020021859161-01-04-2023to31-03-2024.pdf"

# Using the context manager (__enter__ and __exit__) safely opens and closes the PDF
with pdfplumberAdapter(pdf_path) as adapter:
    
    # 1. Print the new properties
    print(f"--- PDF Statistics ---")
    print(f"Total Pages: {adapter.page_count}")
    print(f"Total Tables Found: {adapter.table_count}")
    
    print("\nPage-wise Table Counts:")
    for entry in adapter.page_wise_table_counts:
        print(f"  Page {entry['page']}: {entry['count']} table(s)")
    print("-" * 25)

    # 2. Extract and save full text
    print("\nExtracting full text...")
    full_text = adapter.extract_full_text(layout=True)
    with open("extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(full_text)
    print("Saved to extracted_text.txt")

    # 3. Extract and save all tables
    print("Extracting all tables...")
    tables_data = adapter.extract_all_tables()
    with open("extracted_tables.json", "w", encoding="utf-8") as f:
        json.dump(tables_data, f, ensure_ascii=False, indent=4)
    print("Saved to extracted_tables.json")

    # 4. Extract and save the largest table per page
    print("Extracting largest tables...")
    table_data = adapter.extract_all_table()
    with open("extracted_table.json", "w", encoding="utf-8") as f:
        json.dump(table_data, f, ensure_ascii=False, indent=4)
    print("Saved to extracted_table.json")