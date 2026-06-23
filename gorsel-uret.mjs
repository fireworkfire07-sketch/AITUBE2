// gorsel-uret.mjs
// senaryo.json'daki her sahne icin OpenAI ile gorsel uretir
// Gerekli: OPENAI_API_KEY + senaryo.json

import fs from "node:fs";

const API_KEY = process.env.OPENAI_API_KEY;
const MODEL = "gpt-image-1-mini";   // en ucuz; "gpt-image-2" daha kaliteli ama pahali
const SIZE = "1536x1024";           // 16:9'a yakin yatay
const QUALITY = "medium";           // "low" daha ucuz, "high" daha kaliteli

if (!API_KEY) {
  console.error("HATA: OPENAI_API_KEY tanimli degil.");
  process.exit(1);
}
if (!fs.existsSync("senaryo.json")) {
  console.error("HATA: senaryo.json yok.");
  process.exit(1);
}

const senaryo = JSON.parse(fs.readFileSync("senaryo.json", "utf8"));
const sahneler = senaryo.sahneler || [];
console.log(`${sahneler.length} sahne icin gorsel uretilecek.`);

if (!fs.existsSync("gorseller")) fs.mkdirSync("gorseller");

const bekle = (ms) => new Promise(r => setTimeout(r, ms));

async function gorselUret(prompt, dosyaYolu, deneme = 1) {
  try {
    const res = await fetch("https://api.openai.com/v1/images/generations", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${API_KEY}`
      },
      body: JSON.stringify({
        model: MODEL,
        prompt: prompt,
        size: SIZE,
        quality: QUALITY,
        output_format: "jpeg",
        n: 1
      })
    });

    if ((res.status === 429 || res.status >= 500) && deneme <= 4) {
      const s = deneme * 15;
      console.log(`  Limit/hata ${res.status}, ${s}sn sonra tekrar...`);
      await bekle(s * 1000);
      return gorselUret(prompt, dosyaYolu, deneme + 1);
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${(await res.text()).slice(0, 200)}`);

    const data = await res.json();
    const b64 = data.data?.[0]?.b64_json;
    if (!b64) throw new Error("b64_json bos dondu");
    fs.writeFileSync(dosyaYolu, Buffer.from(b64, "base64"));
    return true;
  } catch (e) {
    if (deneme <= 4) {
      const s = deneme * 15;
      console.log(`  Hata (${e.message}), ${s}sn sonra tekrar...`);
      await bekle(s * 1000);
      return gorselUret(prompt, dosyaYolu, deneme + 1);
    }
    console.error(`  BASARISIZ: ${dosyaYolu} -> ${e.message}`);
    return false;
  }
}

(async () => {
  let basarili = 0, basarisiz = [];
  for (let i = 0; i < sahneler.length; i++) {
    const no = String(i + 1).padStart(2, "0");
    const dosya = `gorseller/sahne_${no}.jpg`;
    const prompt = sahneler[i].gorsel || "cinematic documentary scene, warm light";
    process.stdout.write(`Sahne ${no}/${sahneler.length}... `);
    const ok = await gorselUret(prompt, dosya);
    if (ok) { basarili++; console.log("tamam"); }
    else basarisiz.push(no);
    await bekle(1500);
  }
  console.log(`\nBitti! ${basarili}/${sahneler.length} gorsel uretildi.`);
  if (basarisiz.length) console.log("Basarisiz sahneler:", basarisiz.join(", "));
})();
