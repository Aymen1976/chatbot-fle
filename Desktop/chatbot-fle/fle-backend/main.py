import os
import fitz  # PyMuPDF
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
from typing import List
from search_engine import search_similar_passages

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama3-70b-8192"

class Message(BaseModel):
    sender: str
    text: str

class ChatRequest(BaseModel):
    message: str
    fileContent: str = ""
    history: List[Message] = []

@app.post("/chat")
async def chat(req: ChatRequest):
    user_message = req.message.strip()

    if not user_message:
        return {"response": "❌ Aucun message reçu."}

    user_message_lower = user_message.lower()
    if any(x in user_message_lower for x in ["écris un texte", "écrivez un article", "rédigez un texte"]):
        system_message = (
            "Tu es un assistant FLE. L'utilisateur demande un **texte structuré**, au format classique. "
            "Réponds uniquement en **français**, sous forme de **paragraphes clairs et bien séparés**. "
            "❌ N’utilise pas d’émojis. ❌ N’utilise pas de Markdown. "
            "Le style doit être fluide, adapté à un niveau B1/B2."
        )
    else:
        system_message = (
            "Tu es un assistant pédagogique spécialisé en FLE. "
            "Réponds toujours en **français clair**, avec une structure en **Markdown** :\n"
            "- Titres (###)\n"
            "- Listes à puces ou numérotées\n"
            "- Paragraphes bien séparés\n"
            "- ✅ Ajoute des émojis pédagogiques pour illustrer le contenu (📘, ✍️, 🧠, ✅, etc)."
        )

    messages = [
        {"role": "system", "content": system_message}
    ]

    for m in req.history:
        role = "user" if m.sender == "étudiant" else "assistant"
        messages.append({"role": role, "content": m.text})

    messages.append({"role": "user", "content": user_message})

    # 🔍 Intégration intelligente de la base PDF si mots-clés déclencheurs détectés
    rag_keywords = ["document", "pdf", "selon", "extrait", "basé sur"]
    use_rag = any(kw in user_message_lower for kw in rag_keywords)
    context_from_docs = ""

    if use_rag:
        try:
            search_results = search_similar_passages(user_message, top_k=4)
            context_from_docs = "\n\n".join([f"[Page {doc['page']}] {doc['text']}" for doc in search_results])
            context_intro = "Voici quelques extraits issus de documents pédagogiques à prendre en compte :\n"
            messages.insert(1, {"role": "user", "content": context_intro + context_from_docs})
            print("📚 RAG activé. Passages ajoutés au contexte.")
        except Exception as err:
            print("⚠️ Erreur RAG:", err)

    print("\n🔎 SYSTEM MESSAGE:", system_message)
    print("📝 MESSAGES:", messages)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        print("✅ GROQ RESPONSE:", content)
        return {"response": content}
    except Exception as e:
        print("❌ ERREUR GROQ:", str(e))
        return {"error": str(e)}

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    try:
        if file.filename.endswith(".pdf"):
            content = await file.read()
            temp_path = "temp_uploaded.pdf"
            with open(temp_path, "wb") as f:
                f.write(content)

            doc = fitz.open(temp_path)
            text = "\n".join([page.get_text() for page in doc])
            doc.close()
            os.remove(temp_path)
            return {"fileContent": text}

        content = await file.read()
        text = content.decode("utf-8", errors="ignore")
        return {"fileContent": text}
    except Exception as e:
        print("❌ ERREUR ANALYSE FICHIER:", str(e))
        return {"error": str(e)}
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API FLE en ligne 🚀"}

