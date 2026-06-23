const niches = [
  "yapay zeka ile para kazanma",
  "YouTube Shorts otomasyonu",
  "telefonla içerik üretme",
  "AI video üretimi",
  "pasif gelir fikirleri",
  "dijital ürün satışı"
];

const videoSources = [
  "stok video",
  "ekran kaydı",
  "AI görsel animasyon",
  "altyazılı reels formatı"
];

export async function GET() {
  const now = new Date().toISOString();

  const niche = niches[Math.floor(Math.random() * niches.length)];
  const source = videoSources[Math.floor(Math.random() * videoSources.length)];

  const packageData = {
    success: true,
    system: "AiTube V1 Content Factory",
    status: "queued",
    createdAt: now,

    niche,
    title: `${niche} ile her gün içerik üretme sistemi`,
    hook: "Bunu kuran biri, her gün sıfırdan video fikri aramak zorunda kalmaz.",

    script: [
      "Bugün sana içerik üretimini otomatikleştirmenin en basit yolunu göstereceğim.",
      `Konu: ${niche}.`,
      "Önce konu seçilir, sonra kısa bir hook yazılır.",
      "Ardından 30 saniyelik ses metni hazırlanır.",
      "Sonra video, altyazı ve müzikle Shorts formatına çevrilir.",
      "Bu sistem düzenli çalışırsa her gün yeni içerik çıkarır."
    ],

    voiceText:
      `Bunu kuran biri, her gün sıfırdan video fikri aramak zorunda kalmaz. ` +
      `${niche} alanında önce konu seçilir, sonra dikkat çeken bir giriş yazılır. ` +
      `Ardından kısa ses metni, sahne planı, açıklama ve hashtag hazırlanır. ` +
      `AiTube V1 bunun ilk otomatik içerik fabrikasıdır.`,

    videoPlan: {
      format: "YouTube Shorts 9:16",
      duration: "30-45 saniye",
      source,
      scenes: [
        "0-3 sn: güçlü giriş",
        "3-10 sn: problem göster",
        "10-25 sn: çözüm anlat",
        "25-35 sn: sistem fikrini göster",
        "35-45 sn: takip ve yorum çağrısı"
      ]
    },

    description:
      `${niche} konusunda otomatik içerik üretim sistemi. AiTube V1 ile başlık, senaryo, ses metni ve Shorts planı otomatik hazırlanır.`,

    hashtags: [
      "#aitube",
      "#yapayzeka",
      "#shorts",
      "#otomasyon",
      "#dijitalgelir"
    ],

    publishPlan: {
      platform: "YouTube Shorts",
      uploadStatus: "youtube_api_not_connected",
      nextStep: "video_render"
    }
  };const version = "V2";

  console.log("AITUBE V1 PACKAGE:", packageData);
  

return Response.json(packageData)
}  

