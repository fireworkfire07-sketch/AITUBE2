// app/api/create-video/route.ts
// TAM OTOMATİK VİDEO ÜRETİM HATTI
// Konu al → GPT senaryo yazar → JSON2Video render eder (AI görsel + ses) → YouTube'a yükler

export const dynamic = "force-dynamic";
export const maxDuration = 300;

export async function POST(req: Request) {
  const log: string[] = [];
  try {
    const { topic } = await req.json();
    if (!topic) return Response.json({ error: "topic gerekli" }, { status: 400 });
    log.push(`Konu: ${topic}`);

    // ADIM 1: GPT senaryo + sahneler üretir
    const scriptRes = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        response_format: { type: "json_object" },
        messages: [
          {
            role: "system",
            content: `Çocuklara yönelik eğitici video senaristisin. Verilen konu için kısa bir video senaryosu üret.
SADECE şu JSON formatında cevap ver:
{
  "title": "YouTube başlığı (ilgi çekici, max 90 karakter)",
  "description": "YouTube açıklaması (2-3 cümle + 3 hashtag)",
  "tags": ["etiket1","etiket2","etiket3","etiket4","etiket5"],
  "scenes": [
    {"text": "ekranda görünecek kısa metin", "voiceover": "anlatıcının okuyacağı 1-2 cümle", "imageQuery": "sahne görseli tarifi (İngilizce)"}
  ]
}
Kurallar: 4-6 sahne. Dil Türkçe (imageQuery hariç). Çocuk dostu, neşeli ton.`,
          },
          { role: "user", content: `Konu: ${topic}` },
        ],
      }),
    });
    const scriptData = await scriptRes.json();
    const script = JSON.parse(scriptData.choices?.[0]?.message?.content || "{}");
    if (!script.scenes?.length) throw new Error("GPT senaryo üretemedi");
    log.push(`Senaryo hazır: ${script.title} (${script.scenes.length} sahne)`);

    // ADIM 2: JSON2Video render (AI görsel + Türkçe seslendirme)
    const movie = {
      resolution: "full-hd",
      quality: "high",
      scenes: script.scenes.map((s: any) => ({
        comment: s.text,
        elements: [
          {
            type: "image",
            prompt: `Colorful children's book illustration of ${s.imageQuery}, bright cheerful colors, cute cartoon style, kids coloring theme`,
            model: "flux-schnell",
          },
          {
            type: "text",
            text: s.text,
            style: "003",
            settings: { "font-size": "56px", "font-family": "Nunito" },
            position: "center-center",
          },
          {
            type: "voice",
            text: s.voiceover,
            voice: "tr-TR-EmelNeural",
          },
        ],
      })),
    };

    const renderRes = await fetch("https://api.json2video.com/v2/movies", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": process.env.JSON2VIDEO_API_KEY!,
      },
      body: JSON.stringify(movie),
    });
    const renderData = await renderRes.json();
    const projectId = renderData?.project;
    if (!projectId) throw new Error(`Render başlatılamadı: ${JSON.stringify(renderData)}`);
    log.push(`Render başladı: ${projectId}`);

    // Render bitene kadar bekle (15 sn'de bir kontrol, max ~4 dk)
    let videoUrl = "";
    for (let i = 0; i < 16; i++) {
      await new Promise((r) => setTimeout(r, 15000));
      const st = await fetch(
        `https://api.json2video.com/v2/movies?project=${projectId}`,
        { headers: { "x-api-key": process.env.JSON2VIDEO_API_KEY! } }
      );
      const stData = await st.json();
      const status = stData?.movie?.status;
      if (status === "done") {
        videoUrl = stData.movie.url;
        break;
      }
      if (status === "error") throw new Error("Render hatası: " + JSON.stringify(stData.movie));
    }
    if (!videoUrl) throw new Error("Render zaman aşımına uğradı");
    log.push(`Video hazır: ${videoUrl}`);

    // ADIM 3: YouTube'a yükle
    const tokenRes = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        client_id: process.env.YT_CLIENT_ID!,
        client_secret: process.env.YT_CLIENT_SECRET!,
        refresh_token: process.env.YT_REFRESH_TOKEN!,
        grant_type: "refresh_token",
      }),
    });
    const tokenData = await tokenRes.json();
    const accessToken = tokenData.access_token;
    if (!accessToken) throw new Error("YouTube token alınamadı: " + JSON.stringify(tokenData));

    const videoFile = await fetch(videoUrl);
    const videoBuffer = await videoFile.arrayBuffer();
    log.push(`Video indirildi: ${(videoBuffer.byteLength / 1048576).toFixed(1)} MB`);

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
          Authorization: `Bearer ${accessToken}`,
          "Content-Type": "application/json",
          "X-Upload-Content-Type": "video/mp4",
          "X-Upload-Content-Length": String(videoBuffer.byteLength),
        },
        body: JSON.stringify(meta),
      }
    );
    const uploadUrl = initRes.headers.get("location");
    if (!uploadUrl) throw new Error("Upload başlatılamadı: " + (await initRes.text()));

    const upRes = await fetch(uploadUrl, {
      method: "PUT",
      headers: { "Content-Type": "video/mp4" },
      body: videoBuffer,
    });
    const upData = await upRes.json();
    if (!upData.id) throw new Error("Upload tamamlanamadı: " + JSON.stringify(upData));
    log.push(`YouTube'a yüklendi: https://youtube.com/watch?v=${upData.id}`);

    return Response.json({
      ok: true,
      title: script.title,
      youtubeLink: `https://youtube.com/watch?v=${upData.id}`,
      log,
    });
  } catch (e: any) {
    log.push("HATA: " + e?.message);
    return Response.json({ ok: false, error: e?.message, log }, { status: 500 });
  }
}

// Sağlık kontrolü + tarayıcıdan test:
// /api/create-video?topic=test yazarsan pipeline'ı çalıştırıp sonucu gösterir
export async function GET(req: Request) {
  const url = new URL(req.url);
  const topic = url.searchParams.get("topic");
  if (!topic) {
    return Response.json({ ok: true, service: "create-video", status: "hazır" });
  }
  return POST(
    new Request(req.url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ topic }),
    })
  );
}
