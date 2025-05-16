import faiss
import pickle
from sentence_transformers import SentenceTransformer

INDEX_FOLDER = "index"
MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)

def search_similar_passages(query, top_k=5):
    index = faiss.read_index(f"{INDEX_FOLDER}/faiss.index")
    with open(f"{INDEX_FOLDER}/docs.pkl", "rb") as f:
        documents = pickle.load(f)

    query_embedding = model.encode([query])
    D, I = index.search(query_embedding, top_k)

    results = [documents[i] for i in I[0] if i < len(documents)]
    return results
