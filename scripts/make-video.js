const fs = require("fs");
const path = require("path");

const outputDir = path.join(process.cwd(), "public");
const outputFile = path.join(outputDir, "aitube-video.txt");

if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir);
}

const content = `
AITUBE VIDEO ÜRETİLDİ

Başlık:
Antalya’da Kimsenin Bilmediği 3 Gizli Yer

Senaryo:
Antalya sadece deniz ve otellerden ibaret değil.
Bugün sana çoğu turistin bilmediği üç gizli yeri göstereceğim.

Sahneler:
1. Sahil açılışı
2. Gizli koy
3. Kaleiçi sokakları
4. Gün batımı
5. Takip et çağrısı
`;

fs.writeFileSync(outputFile, content);

console.log("Video dosyası hazır:", outputFile);
