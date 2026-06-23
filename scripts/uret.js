// AiTube v2.1 — GitHub Actions üretim hattı
const fs = require("fs");
const { execSync } = require("child_process");
console.log("DEBUG CLIENT_ID len:", process.env.YT_CLIENT_ID?.length, JSON.stringify(process.env.YT_CLIENT_ID?.slice(0,6)), JSON.stringify(process.env.YT_CLIENT_ID?.slice(-6)));
console.log("DEBUG SECRET len:", process.env.YT_CLIENT_SECRET?.length, JSON.stringify(process.env.YT_CLIENT_SECRET?.slice(0,4)));

const NISLER = [
  "sevimli dinozorlar", "uzay ve gezegenler", "tasitlar", "okyanus canlilari",
  "orman hayvanlari", "masal yaratiklari", "meyveler ve sebzeler",
  "evcil hayvanlar", "bocekler ve kelebekler", "mevsimler",
];

async function fetchRetry(url, opts = {}, deneme = 4) {
  for (let i = 1; i <= deneme; i++) {
    try {
      const r = await fetch(url, opts);
      if (r.ok) return r;
      console.log(`Deneme ${i}: HTTP ${r.status} — ${(await r.text()).slice(0, 300)}`);
    } catch (e) {
      console.log(`Deneme ${i}: ${e.message}`);
    }
    await new Promise((x) => setTimeout(x, 5000 * i));
  }
  throw new Error("Kaynak alınamadı: " + url.slice(0, 100));
}

function ffmpeg(cmd) {
  try {
    execSync(cmd, { stdio: "pipe" });
  } catch (e) {
    const hata = (e.stderr ? e.stderr.toString() : "") + (e.stdout ? e.stdout.toString() : "");
    console.log("FFMPEG HATASI:", hata.slice(-1000));
    throw new Error("ffmpeg başarısız");
  }
}

(async () => {
  fs.mkdirSync("is", { recursive: true });
  const nis = NISLER[(new Date().getDate() + new Date().getHours()) % NISLER.length];
  const ozelKonu = process.env.KONU;
  console.log("Niş:", nis);

  // 1) SENARYO
  const sRes = await fetchRetry("https://api.openai.com/v1/chat/completions", {
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
{"title":"YouTube başlığı (max 90 karakter)","description":"3-4 cümle + 5 hashtag","tags":["10 etiket"],
"scenes":[{"voiceover":"4-6 cümle, yavaş tempolu, çocuklara sorular soran sıcak anlatım","imageQuery":"detailed English illustration description"}]}
Kurallar: TAM 18 sahne (merak uyandıran giriş + 16 içerik + abone olmaya davet eden kapanış). Tutarlı görsel evren. Dil Türkçe (imageQuery hariç).`,
        },
        {
          role: "user",
          content: ozelKonu
            ? `Konu: ${ozelKonu}. Bu konuda senaryoyu yaz.`
            : `Niş: ${nis}. Bu nişten özgün bir konu seç ve senaryoyu yaz.`,
        },
      ],
    }),
  });
  const sData = await sRes.json();
  const script = JSON.parse(sData.choices[0].message.content);
  if (!script.scenes?.length) throw new Error("Senaryo üretilemedi");
  console.log(`Senaryo: ${script.title} (${script.scenes.length} sahne)`);

  // 2) HER SAHNE
  const parcalar = [];
  for (let i = 0; i < script.scenes.length; i++) {
    const sc = script.scenes[i];
    console.log(`Sahne ${i + 1}/${script.scenes.length}...`);

    // Görsel (OpenAI)
    const imgRes = await fetchRetry("https://api.openai.com/v1/images/generations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: "gpt-image-1-mini",
        prompt: `colorful children's book illustration, ${sc.imageQuery}, bright cheerful colors, cute cartoon style, kids coloring theme`,
        size: "1536x1024",
        quality: "low",
      }),
    });
    const imgData = await imgRes.json();
    fs.writeFileSync(`is/g${i}.png`, Buffer.from(imgData.data[0].b64_json, "base64"));

    // Ses (OpenAI TTS)
    const ttsRes = await fetchRetry("https://api.openai.com/v1/audio/speech", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      },
      body: JSON.stringify({ model: "tts-1", voice: "nova", input: sc.voiceover, response_format: "mp3" }),
    });
    fs.writeFileSync(`is/s${i}.mp3`, Buffer.from(await ttsRes.arrayBuffer()));

    // Görsel + ses → sahne videosu
    ffmpeg(
      `ffmpeg -y -loop 1 -i is/g${i}.png -i is/s${i}.mp3 ` +
      `-vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080" ` +
      `-c:v libx264 -preset veryfast -c:a aac -b:a 192k -pix_fmt yuv420p -shortest is/p${i}.mp4`
    );
    parcalar.push(`file 'p${i}.mp4'`);
  }

  // 3) BİRLEŞTİR
  fs.writeFileSync("is/liste.txt", parcalar.join("\n"));
  ffmpeg(`ffmpeg -y -f concat -safe 0 -i is/liste.txt -c copy is/final.mp4`);
  const boyut = fs.statSync("is/final.mp4").size;
  console.log(`Final video: ${(boyut / 1048576).toFixed(1)} MB`);

  // 4) YOUTUBE'A YÜKLE
  const tokenRes = await fetchRetry("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: process.env.YT_CLIENT_ID,
      client_secret: process.env.YT_CLIENT_SECRET,
      refresh_token: process.env.YT_REFRESH_TOKEN,
      grant_type: "refresh_token",
    }),
  });
  const { access_token } = await tokenRes.json();
  if (!access_token) throw new Error("YouTube token alınamadı");

  const meta = {
    snippet: {
      title: script.title,
      description: script.description,
      tags: script.tags,
      categoryId: "27",
    },
    status: {
      privacyStatus: process.env.YT_PRIVACY || "private",
      selfDeclaredMadeForKids: true,
    },
  };
  const initRes = await fetch(
    "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status",
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${access_token}`,
        "Content-Type": "application/json",
        "X-Upload-Content-Type": "video/mp4",
        "X-Upload-Content-Length": String(boyut),
      },
      body: JSON.stringify(meta),
    }
  );
  const uploadUrl = initRes.headers.get("location");
  if (!uploadUrl) throw new Error("Upload başlatılamadı: " + (await initRes.text()));

  const upRes = await fetch(uploadUrl, {
    method: "PUT",
    headers: { "Content-Type": "video/mp4" },
    body: fs.readFileSync("is/final.mp4"),
  });
  const upData = await upRes.json();
  if (!upData.id) throw new Error("Upload tamamlanamadı: " + JSON.stringify(upData).slice(0, 300));
  console.log(`✅ YAYINDA: https://youtube.com/watch?v=${upData.id}`);
})();
