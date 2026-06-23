const videos = [
  "https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4",
  "https://media.w3.org/2010/05/sintel/trailer.mp4",
  "https://media.w3.org/2010/05/bunny/trailer.mp4"
];

const topics = [
  "Yapay zeka ile para kazanma",
  "YouTube Shorts otomasyonu",
  "Günde 1 saatle dijital gelir",
  "AI video üretim sistemi",
  "Telefonla içerik üretme",
  "Kendi kendine çalışan YouTube kanalı"
];

export async function POST() {
  const topic = topics[Math.floor(Math.random() * topics.length)];
  const videoUrl = videos[Math.floor(Math.random() * videos.length)];

  return Response.json({
    title: `${topic} artık düşündüğünden daha kolay`,
    hook: "Bunu bugün kuranlar yarın içerik üretmeye başlamış olacak.",
    scenes: [
      "0-3 sn: güçlü hook",
      "3-12 sn: problemi göster",
      "12-25 sn: çözümü anlat",
      "25-35 sn: takip çağrısı"
    ],
    voiceText: `${topic} konusunda en büyük hata, sistemi kurmadan sürekli araç aramaktır. Doğru kurulan bir otomasyon, her basışta yeni fikir çıkarır, senaryo hazırlar ve video üretim sürecini başlatır.`,
    hashtags: ["#aitube", "#yapayzeka", "#shorts", "#otomasyon"],
    videoUrl,
    status: "ok"
  });
}
