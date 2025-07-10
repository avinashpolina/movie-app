// frontend/src/app/page.js
"use client";

import { useEffect, useState } from "react";
import styles from "../styles/page.module.css";  // optional CSS-Module

export default function Home() {
  const [movies, setMovies]     = useState([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer]     = useState("");

  // load first 10 movies on mount
  useEffect(() => {
    fetch("http://127.0.0.1:8000/movies")
      .then((res) => res.json())
      .then(setMovies)
      .catch(console.error);
  }, []);

  const handleSend = async () => {
    if (!question.trim()) return;
    try {
      const res = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      setAnswer(data.answer);
    } catch (err) {
      console.error(err);
      setAnswer("Error communicating with chatbot.");
    }
  };

  return (
    <main className={styles.container}>
      <h1>Movie List</h1>
      <ul className={styles.list}>
        {movies.map((m, i) => (
          <li key={i} className={styles.card}>
            <h2>{m.title}</h2>
            <p>{m.description}</p>
          </li>
        ))}
      </ul>

      <section className={styles.chatSection}>
        <h2>Ask the Movie Bot</h2>
        <div className={styles.chatInput}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask me about a movie…"
          />
          <button onClick={handleSend}>Send</button>
        </div>
        {answer && <div className={styles.answer}>{answer}</div>}
      </section>
    </main>
  );
}