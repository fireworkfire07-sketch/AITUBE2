// ses-uret.mjs
// senaryo.json'daki her sahnenin anlatimini edge-tts ile sese cevirir
// Gerekli: senaryo.json + edge-tts (workflow'da kurulur)

import fs from "node:fs";
import { execSync } from "child_process";

if (!fs.existsSync("senaryo.json")) {
  console.error("HATA: senaryo.json yok.");
  process.exit(1);
}

const senaryo = JSON.parse(fs.readFileSync("senaryo.json", "utf8"));
const sahneler = senaryo.sahneler || [];
console.log(`${sahneler.length} sahne icin ses uretilecek.`);

if (!fs.existsSync("sesler")) fs.mkdirSync("sesler");

let basarili = 0, basarisiz = [];
for (let i = 0; i < sahneler.length; i++) {
  const no = String(i + 1).padStart(2, "0");
  const dosya = `sesler/sahne_${no}.mp3`;
  const metin = (sahneler[i].anlatim || "").replace(/"/g, "'").replace(/\n/g, " ");
  process.stdout.write(`Sahne ${no}/${sahneler.length}... `);
  try {
    execSync(
      `edge-tts --voice tr-TR-AhmetNeural --rate=-5% --text "${metin}" --write-media "${dosya}"`,
      { stdio: "pipe" }
    );
    basarili++;
    console.log("tamam");
  } catch (e) {
    basarisiz.push(no);
    console.log("HATA: " + (e.stderr ? e.stderr.toString().slice(0, 120) : e.message));
  }
}

console.log(`\nBitti! ${basarili}/${sahneler.length} ses uretildi.`);
if (basarisiz.length) console.log("Basarisiz:", basarisiz.join(", "));
