// youtube-yukle.mjs
import fs from "fs";
import { google } from "googleapis";

const {
  YT_CLIENT_ID,
  YT_CLIENT_SECRET,
  YT_REFRESH_TOKEN,
  YT_PRIVACY,
} = process.env;

if (!YT_CLIENT_ID || !YT_CLIENT_SECRET || !YT_REFRESH_TOKEN) {
  console.error("HATA: YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN eksik (GitHub Secrets).");
  process.exit(1);
}

const VIDEO_PATH = "video.mp4";
if (!fs.existsSync(VIDEO_PATH)) {
  console.error(`HATA: ${VIDEO_PATH} bulunamadi. Video uretilmemis olabilir.`);
  process.exit(1);
}

let baslik = "Anadolu Bitkileri Belgeseli";
let aciklama = "Otomatik uretilmis belgesel video.";
let etiketler = ["belgesel", "bitki", "anadolu", "doga"];

try {
  if (fs.existsSync("senaryo.json")) {
    const s = JSON.parse(fs.readFileSync("senaryo.json", "utf8"));
    if (s.baslik) baslik = s.baslik;
    if (s.title) baslik = s.title;
    if (s.aciklama) aciklama = s.aciklama;
    if (s.description) aciklama = s.description;
    if (Array.isArray(s.etiketler)) etiketler = s.etiketler;
    if (Array.isArray(s.tags)) etiketler = s.tags;
  }
} catch (e) {
  console.warn("senaryo.json okunamadi, varsayilan baslik kullanilacak:", e.message);
}

baslik = String(baslik).slice(0, 100);
aciklama = String(aciklama).slice(0, 4900);

const privacyStatus = (YT_PRIVACY || "private").trim();

const oauth2 = new google.auth.OAuth2(YT_CLIENT_ID, YT_CLIENT_SECRET);
oauth2.setCredentials({ refresh_token: YT_REFRESH_TOKEN });

const youtube = google.youtube({ version: "v3", auth: oauth2 });

console.log("YouTube'a yukleniyor...");
console.log("  Baslik :", baslik);
console.log("  Gizlilik:", privacyStatus);

try {
  const res = await youtube.videos.insert({
    part: ["snippet", "status"],
    requestBody: {
      snippet: {
        title: baslik,
        description: aciklama,
        tags: etiketler,
        categoryId: "22",
      },
      status: {
        privacyStatus,
        selfDeclaredMadeForKids: false,
      },
    },
    media: {
      body: fs.createReadStream(VIDEO_PATH),
    },
  });

  const id = res.data.id;
  console.log("BASARILI! Video yuklendi.");
  console.log("  Video ID :", id);
  console.log("  Izle     : https://www.youtube.com/watch?v=" + id);
} catch (err) {
  console.error("YUKLEME HATASI:", err?.errors || err?.message || err);
  process.exit(1);
}
