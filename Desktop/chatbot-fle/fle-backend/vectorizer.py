import faiss
import os
import pickle
from sentence_transformers import SentenceTransformer
from pdf_loader import load_all_pdfs

INDEX_FOLDER = "index"
MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)

def create_index(documents):
    texts = [doc["text"] for doc in documents]
    embeddings = model.encode(texts, show_progress_bar=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    if not os.path.exists(INDEX_FOLDER):
        os.makedirs(INDEX_FOLDER)

    faiss.write_index(index, os.path.join(INDEX_FOLDER, "faiss.index"))
    with open(os.path.join(INDEX_FOLDER, "docs.pkl"), "wb") as f:
        pickle.dump(documents, f)

def build_pdf_vector_index():
    docs = load_all_pdfs()
    if docs:
        print("📄 Documents trouvés :", len(docs))
        create_index(docs)
        print("✅ Index FAISS créé avec", len(docs), "passages.")
    else:
        print("⚠️ Aucun texte trouvé dans les PDFs.")

# ✅ Appel direct si lancé comme script
if __name__ == "__main__":
    build_pdf_vector_index()
