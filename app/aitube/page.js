"use client";

import { useState } from "react";

const niches = [
  "yoga nefes egzersizi",
  "çocuklara masal",
  "mini belgesel",
  "motivasyon",
  "sağlıklı yaşam",
  "Antalya gezi videosu",
  "AI ile para kazanma",
  "uyku meditasyonu"
];

export default function AiTubePage() {
  const [idea, setIdea] = useState(null);

  function generateVideo() {
    const niche = niches[Math.floor(Math.random() * niches.length)];
    const number = Math.floor(Math.random() * 9999);

    setIdea({
      title: `${niche.toUpperCase()} #${number}`,
      hook: `İlk 3 saniyede izleyiciyi yakala: "${niche} hakkında kimsenin bilmediği basit yöntem..."`,
      script: `Bugün ${niche} konusunda kısa ama etkili bir içerik hazırlıyoruz. Önce dikkat çekici bir giriş yapıyoruz. Sonra 3 pratik bilgi veriyoruz. En sonda izleyiciye kaydetmesini ve takip etmesini söylüyoruz.`,
      prompt: `${niche}, cinematic, vertical 9:16, high quality, soft light, viral youtube shorts style`,
      status: "Yeni video fikri üretildi"
    });
  }

  return (
    <main style={{
      minHeight: "100vh",
      background: "#050505",
      color: "white",
      padding: "30px",
      fontFamily: "Arial"
    }}>
      <h1 style={{ fontSize: "36px" }}>🎬 AiTube Studio</h1>
      <p>Otomatik YouTube Shorts fikir + senaryo + görsel prompt üretici</p>

      <button
        onClick={generateVideo}
        style={{
          marginTop: "20px",
          padding: "16px 24px",
          borderRadius: "12px",
          border: "none",
          background: "white",
          color: "black",
          fontSize: "18px",
          fontWeight: "bold"
        }}
      >
        Yeni Video Üret
      </button>

      {idea && (
        <div style={{
          marginTop: "30px",
          background: "#151515",
          padding: "24px",
          borderRadius: "18px",
          maxWidth: "700px"
        }}>
          <h2>{idea.title}</h2>
          <p><b>Hook:</b> {idea.hook}</p>
          <p><b>Senaryo:</b> {idea.script}</p>
          <p><b>Görsel Prompt:</b> {idea.prompt}</p>
          <p><b>Durum:</b> {idea.status}</p>
        </div>
      )}
    </main>
  );
}
