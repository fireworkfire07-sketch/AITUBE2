// video-olustur.mjs
// gorseller/ + sesler/ -> her gorsel kendi sesi kadar ekranda kalir -> video.mp4
// Gerekli: gorseller/, sesler/, senaryo.json, ffmpeg (workflow'da kurulur)

import fs from "node:fs";
import { execSync } from "child_process";

if (!fs.existsSync("senaryo.json")) { console.error("HATA: senaryo.json yok."); process.exit(1); }
const senaryo = JSON.parse(fs.readFileSync("senaryo.json", "utf8"));
const sahneler = senaryo.sahneler || [];
console.log(`${sahneler.length} sahne icin video olusturuluyor...`);

if (!fs.existsSync("parcalar")) fs.mkdirSync("parcalar");

// Bir ses dosyasinin suresini (saniye) ogren
function sesSuresi(dosya) {
  try {
    const out = execSync(
      `ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "${dosya}"`
    ).toString().trim();
    return parseFloat(out) || 4;
  } catch { return 4; }
}

// 1) Her sahne icin: gorsel + ses -> kisa mp4 parca (yavas zoom efektiyle)
const parcaListesi = [];
for (let i = 0; i < sahneler.length; i++) {
  const no = String(i + 1).padStart(2, "0");
  const gorsel = `gorseller/sahne_${no}.jpg`;
  const ses = `sesler/sahne_${no}.mp3`;
  if (!fs.existsSync(gorsel) || !fs.existsSync(ses)) {
    console.log(`Sahne ${no}: gorsel/ses eksik, atlandi.`);
    continue;
  }
  const sure = sesSuresi(ses);
  const parca = `parcalar/parca_${no}.mp4`;
  const kare = Math.max(1, Math.round(sure * 25)); // 25 fps
  process.stdout.write(`Parca ${no}/${sahneler.length} (${sure.toFixed(1)}s)... `);
  try {
    // Yavas zoom (Ken Burns) + ses; 1920x1080'e olcekle/pad
    execSync(
      `ffmpeg -y -loop 1 -i "${gorsel}" -i "${ses}" ` +
      `-filter_complex "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='min(zoom+0.0008,1.15)':d=${kare}:s=1920x1080:fps=25,format=yuv420p[v]" ` +
      `-map "[v]" -map 1:a -c:v libx264 -preset veryfast -c:a aac -b:a 128k -shortest "${parca}" 2>/dev/null`,
      { stdio: "pipe" }
    );
    parcaListesi.push(parca);
    console.log("tamam");
  } catch (e) {
    console.log("HATA: " + (e.stderr ? e.stderr.toString().slice(0, 120) : e.message));
  }
}

if (parcaListesi.length === 0) { console.error("Hic parca olusmadi!"); process.exit(1); }

// 2) Parcalari birlestir
const liste = parcaListesi.map(p => `file '${p}'`).join("\n");
fs.writeFileSync("birlestir.txt", liste, "utf8");

console.log("\nParcalar birlestiriliyor...");
try {
  execSync(`ffmpeg -y -f concat -safe 0 -i birlestir.txt -c copy video.mp4 2>/dev/null`, { stdio: "pipe" });
  console.log("VIDEO HAZIR: video.mp4");
} catch (e) {
  // copy basarisiz olursa yeniden encode et
  console.log("Birlestirme yeniden encode ile deneniyor...");
  execSync(`ffmpeg -y -f concat -safe 0 -i birlestir.txt -c:v libx264 -preset veryfast -c:a aac video.mp4 2>/dev/null`, { stdio: "pipe" });
  console.log("VIDEO HAZIR: video.mp4");
}
