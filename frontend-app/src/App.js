import React, { useState, useEffect } from "react";
import axios from "axios";
import { saveAs } from "file-saver";
import { Document, Packer, Paragraph, TextRun } from "docx";
import jsPDF from "jspdf";
import { marked } from "marked";
import DOMPurify from "dompurify";
import { htmlToText } from "html-to-text";
import "./App.css";

const renderer = new marked.Renderer();
renderer.link = function (href, title, text) {
  return `<a href="${href}" target="_blank" rel="noopener noreferrer">${text}</a>`;
};

function App() {
  const [currentConversation, setCurrentConversation] = useState({ id: Date.now(), messages: [] });
  const [conversationHistory, setConversationHistory] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  const [input, setInput] = useState("");
  const [fileContent, setFileContent] = useState("");
  const [listening, setListening] = useState(false);
  const recognition = window.SpeechRecognition || window.webkitSpeechRecognition
    ? new (window.SpeechRecognition || window.webkitSpeechRecognition)()
    : null;

  useEffect(() => {
    const savedHistory = localStorage.getItem("conversationHistory");
    if (savedHistory) setConversationHistory(JSON.parse(savedHistory));
  }, []);

  useEffect(() => {
    localStorage.setItem("conversationHistory", JSON.stringify(conversationHistory));
  }, [conversationHistory]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessage = { sender: "étudiant", text: input };
    const updatedMessages = [...currentConversation.messages, newMessage];

    setCurrentConversation((prev) => ({ ...prev, messages: updatedMessages }));
    setInput("");

    try {
      const res = await axios.post("http://localhost:8000/chat", {
        message: input,
        fileContent: fileContent,
        history: updatedMessages,
      });

      setCurrentConversation((prev) => ({
        ...prev,
        messages: [...updatedMessages, { sender: "assistant FLE", text: res.data.response }],
      }));
    } catch (error) {
      setCurrentConversation((prev) => ({
        ...prev,
        messages: [...updatedMessages, { sender: "assistant FLE", text: "❌ Erreur serveur." }],
      }));
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await axios.post("http://localhost:8000/analyze", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setFileContent(res.data.fileContent || "");
      setCurrentConversation((prev) => ({
        ...prev,
        messages: [
          ...prev.messages,
          { sender: "étudiant", text: `📄 Document importé : ${file.name}` },
          { sender: "assistant FLE", text: res.data.fileContent || "Document analysé." },
        ],
      }));
    } catch {
      alert("Erreur lors de l'analyse du document.");
    }
  };

  const startListening = () => {
    if (!recognition) return alert("Votre navigateur ne supporte pas la reconnaissance vocale.");
    setListening(true);
    recognition.lang = "fr-FR";
    recognition.start();
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInput(transcript);
      setListening(false);
    };
    recognition.onerror = () => {
      setListening(false);
    };
  };

  const closeConversation = () => {
    setConversationHistory([...conversationHistory, { ...currentConversation, timestamp: Date.now() }]);
    setCurrentConversation({ id: Date.now(), messages: [] });
  };

  const deleteConversation = (id) => {
    setConversationHistory(conversationHistory.filter((conv) => conv.id !== id));
  };

  const exportPDF = () => {
    const pdf = new jsPDF();
    let y = 20;
    pdf.setFontSize(16);
    pdf.setFont("helvetica", "bold");
    pdf.text("Conversation FLE", 10, y);
    y += 15;

    currentConversation.messages.forEach((msg) => {
      const isStudent = msg.sender === "étudiant";
      pdf.setFontSize(12);
      pdf.setFont("helvetica", isStudent ? "bold" : "normal");
      pdf.text(`${msg.sender} :`, 10, y);
      y += 8;

      let cleanedText = msg.text;
      if (msg.sender === "assistant FLE") {
        const html = marked.parse(cleanedText || "", { renderer });
        cleanedText = htmlToText(html, { wordwrap: 120, tags: { a: { format: "inline" } }, ignoreHref: true });
      }

      const lines = pdf.splitTextToSize(cleanedText, 170);
      lines.forEach((line) => {
        if (y > 280) {
          pdf.addPage();
          y = 20;
        }
        pdf.text(line, 20, y);
        y += 8;
      });
      y += 5;
    });

    pdf.save(`conversation_fle_${currentConversation.id}.pdf`);
  };

  const exportWord = async () => {
    const doc = new Document({
      sections: [
        {
          children: currentConversation.messages.map((msg) =>
            new Paragraph({
              children: [
                new TextRun(`${msg.sender} : ${msg.text.replace(/<br>/g, "\n")}`),
              ],
            })
          ),
        },
      ],
    });
    const blob = await Packer.toBlob(doc);
    saveAs(blob, `conversation_fle_${currentConversation.id}.docx`);
  };

  return (
    <div className={`app ${darkMode ? "dark-mode" : "light-mode"}`}>
      <div className="sidebar">
        <div className="theme-toggle">
          <button onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? "☀️ Mode clair" : "🌙 Mode sombre"}
          </button>
        </div>
        <h3>Historique des conversations</h3>
        <ul>
          {conversationHistory.map((conv) => (
            <li key={conv.id} onClick={() => setCurrentConversation(conv)}>
              {new Date(conv.timestamp).toLocaleDateString()}
              <button onClick={(e) => { e.stopPropagation(); deleteConversation(conv.id); }}>✖️</button>
            </li>
          ))}
        </ul>
        <button onClick={closeConversation}>Nouvelle conversation</button>
      </div>

      <div className="chat-container">
        <div className="chat-header">
          <h1>📘 Chatbot FLE</h1>
        </div>
        <div className="chat-box">
          {currentConversation.messages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender === "étudiant" ? "user" : "bot"}`}>
              <div dangerouslySetInnerHTML={{
                __html: msg.sender === "assistant FLE"
                  ? DOMPurify.sanitize(marked.parse(msg.text || "", { renderer }))
                  : `<strong>${msg.sender} :</strong> ${msg.text}`,
              }} />
            </div>
          ))}
        </div>
        <div className="input-area">
          <input
            type="text"
            placeholder="Posez une question ou saisissez une phrase..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && sendMessage()}
          />
          <button onClick={sendMessage}>Envoyer</button>
          <button onClick={startListening}>{listening ? "🎙️ Enregistrement..." : "🎤 Parler"}</button>
        </div>
        <div className="tools">
          <label className="btn-modern upload-btn">
            📂 Importer un document
            <input type="file" onChange={handleFileUpload} hidden />
          </label>
          <button className="btn-modern" onClick={exportPDF}>📄 PDF</button>
          <button className="btn-modern" onClick={exportWord}>📝 Word</button>
        </div>
      </div>
    </div>
  );
}

export default App;

