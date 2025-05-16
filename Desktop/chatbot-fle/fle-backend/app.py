# app.py
import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq
from search_engine import search_similar_passages  # si tu veux garder le RAG

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama3-70b-8192"

st.set_page_config(page_title="Chatbot FLE", page_icon="📘")

st.title("📘 Chatbot FLE")
st.markdown("Pose une question ou écris ta demande pédagogique en français.")

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("💬 Votre message")

if st.button("Envoyer") and user_input:
    messages = [{"role": "system", "content": "Tu es un assistant pédagogique en FLE. Réponds en français clair, structuré en Markdown avec emojis si besoin."}]
    
    for entry in st.session_state.history:
        messages.append({"role": "user", "content": entry["user"]})
        messages.append({"role": "assistant", "content": entry["bot"]})
    
    messages.append({"role": "user", "content": user_input})

    with st.spinner("🧠 Réflexion en cours..."):
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=0.7
            )
            answer = completion.choices[0].message.content.strip()
            st.session_state.history.append({"user": user_input, "bot": answer})
            st.markdown(answer)
        except Exception as e:
            st.error(f"Erreur : {str(e)}")

st.markdown("---")
st.subheader("🕘 Historique")
for i, entry in enumerate(st.session_state.history[::-1]):
    st.markdown(f"**Vous :** {entry['user']}")
    st.markdown(f"**Chatbot FLE :** {entry['bot']}")

