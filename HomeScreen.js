import React from "react";
import "./App.css";

function HomeScreen({ onStart }) {
  return (
    <div className="home-screen">
      <div className="home-content">
        <h1>👋 Bienvenue sur Chatbot FLE</h1>
        <p>
          Ce chatbot est votre assistant pédagogique en Français Langue Étrangère (FLE).
          Il vous aide à comprendre, enseigner, et apprendre le français de manière interactive.
          Vous pouvez poser des questions, importer des documents, et recevoir des réponses claires et pédagogiques.
        </p>
        <button className="start-button" onClick={onStart}>
          🚀 Commencer
        </button>
      </div>
    </div>
  );
}

export default HomeScreen;
