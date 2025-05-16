import os
import fitz  # PyMuPDF

def load_all_pdfs(folder_path="base_pdfs"):
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            path = os.path.join(folder_path, filename)
            doc = fitz.open(path)
            for i, page in enumerate(doc):
                text = page.get_text().strip()
                if text:
                    documents.append({
                        "filename": filename,
                        "page": i + 1,
                        "text": text
                    })
            doc.close()
    return documents
