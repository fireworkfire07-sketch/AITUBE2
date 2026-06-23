"use client";

import { useState } from "react";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  async function makeVideo() {
    setLoading(true);
    setResult(null);

    const res = await fetch("/api/make-video", { method: "POST" });
    const data = await res.json();

    setResult(data);
    setLoading(false);
  }

  return (
    <main style={{ minHeight: "100vh", background: "#000", color: "#fff", padding: 30 }}>
      <h1>AiTube</h1>

      <button
        onClick={makeVideo}
        disabled={loading}
        style={{
          padding: "16px 24px",
          borderRadius: 12,
          border: 0,
          background: "red",
          color: "white",
          fontSize: 18
        }}
      >
        {loading ? "Üretiliyor..." : "Video Üret"}
      </button>

      {result && (
        <div style={{ marginTop: 30 }}>
          <h2>{result.title}</h2>
          <h3>{result.hook}</h3>

          <video
            src={result.videoUrl}
            controls
            style={{ width: "100%", borderRadius: 16, marginTop: 20 }}
          />

          <h3>Sahneler</h3>
          <ul>
            {result.scenes.map((scene, index) => (
              <li key={index}>{scene}</li>
            ))}
          </ul>

          <h3>Ses Metni</h3>
          <p>{result.voiceText}</p>
        </div>
      )}
    </main>
  );
}
