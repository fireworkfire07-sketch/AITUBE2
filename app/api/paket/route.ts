// PAKET ÜRETİCİ — 10 dk'lık video için hammadde hazırlar
// Kullanım: /api/paket  veya  /api/paket?topic=istedigin-konu

export const dynamic = "force-dynamic";
export const maxDuration = 120;

const NISLER = [
  "sevimli dinozorlar", "uzay ve gezegenler", "taşıtlar", "okyanus canlıları",
  "orman hayvanları", "masal yaratıkları", "meyveler ve sebzeler",
  "evcil hayvanlar", "böcekler ve kelebekler", "mevsimler",
];

export async function GET(req: Request) {
  try {
    const url = new URL(req.url);
    let topic = url.searchParams.get("topic");
    const simdi = new Date();
    const nis = NISLER[(simdi.getDate() + simdi.getHours()) % NISLER.length];
    if (!topic) topic = `${nis} temalı boyama macerası`;

    const aiRes = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        response_format: { type: "json_object" },
        max_tokens: 8000,
        messages: [
          {
            role: "system",
            content: `Çocuklara (3-7 yaş) yönelik 10 DAKİKALIK eğitici boyama videosu senaristisin.
SADECE şu JSON formatında cevap ver:
{"title":"YouTube başlığı","description":"açıklama + 5 hashtag","tags":["10 etiket"],
"scenes":[{"text":"ekran metni","voiceover":"4-6 cümle, yavaş tempolu, sorularla dolu anlatım","imageQuery":"detailed English image description"}]}
Kurallar: TAM 18 sahne (giriş + 16 içerik + abone kapanışı). Her voiceover 4-6 cümle. Tutarlı görsel evren. Dil Türkçe (imageQuery hariç).`,
          },
          { role: "user", content: `Konu: ${topic}` },
        ],
      }),
    });
    const aiData = await aiRes.json();
    const s = JSON.parse(aiData.choices?.[0]?.message?.content || "{}");
    if (!s.scenes?.length) throw new Error("Senaryo üretilemedi, sayfayı yenile");

    const sahneler = s.scenes
      .map((sc: any, i: number) => {
        const imgPrompt = encodeURIComponent(
          `colorful children's book illustration, ${sc.imageQuery}, bright cheerful colors, cute cartoon style`
        );
        const imgUrl = `https://image.pollinations.ai/prompt/${imgPrompt}?width=1920&height=1080&nologo=true&seed=${i + 7}`;
        const ttsUrl = `/api/tts?text=${encodeURIComponent(sc.voiceover)}`;
        return `
<div class="sahne">
  <h3>Sahne ${i + 1}: ${sc.text}</h3>
  <img src="${imgUrl}" loading="lazy" />
  <p class="ipucu">Görsele uzun bas → Fotoğraflara Kaydet</p>
  <p><b>Anlatım:</b> ${sc.voiceover}</p>
  <a class="btn" href="${ttsUrl}" download="sahne-${i + 1}.mp3">🔊 Sesi indir (sahne ${i + 1})</a>
</div>`;
      })
      .join("");

    const html = `<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${s.title} — Paket</title>
<style>
body{font-family:-apple-system,sans-serif;margin:0;padding:16px;background:#0f1320;color:#eee}
h1{font-size:1.3em}h3{margin:8px 0;color:#ffd166}
.kutu{background:#1b2133;border-radius:12px;padding:14px;margin:12px 0}
.sahne img{width:100%;border-radius:10px;margin:8px 0}
.btn{display:inline-block;background:#e63946;color:#fff;padding:10px 16px;border-radius:10px;text-decoration:none;margin:6px 0}
.ipucu{color:#8a93b2;font-size:.85em;margin:2px 0}
textarea{width:100%;background:#0f1320;color:#eee;border:1px solid #333;border-radius:8px;padding:8px;font-size:.9em}
</style></head><body>
<h1>🎬 ${s.title}</h1>
<div class="kutu"><h3>📋 YouTube Bilgileri (kopyala)</h3>
<p><b>Başlık:</b></p><textarea rows="2">${s.title}</textarea>
<p><b>Açıklama:</b></p><textarea rows="4">${s.description}</textarea>
<p><b>Etiketler:</b></p><textarea rows="2">${(s.tags || []).join(", ")}</textarea></div>
<div class="kutu"><h3>🛠 Nasıl kullanılır?</h3>
<p>1) Her sahnenin görselini kaydet, sesini indir.<br>2) CapCut/iMovie'de sırayla diz: görsel + üstüne kendi sesi.<br>3) Bitmiş videoyu YouTube-Kuyruk klasörüne at (veya elle yükle).</p></div>
${sahneler}
</body></html>`;

    return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8" } });
  } catch (e: any) {
    return new Response("Hata: " + e?.message, { status: 500 });
  }
}
