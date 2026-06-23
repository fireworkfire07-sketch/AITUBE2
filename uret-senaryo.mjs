// uret-senaryo.mjs
import fs from "node:fs";

const MODEL = "gpt-4o";
const ARASTIRMA_MODEL = "gpt-4o-search-preview";
const API_KEY = process.env.OPENAI_API_KEY;
if (!API_KEY) { console.error("HATA: OPENAI_API_KEY tanimli degil."); process.exit(1); }

const bitkiler = fs.readFileSync("bitkiler.txt","utf8").split("\n").map(s=>s.trim()).filter(Boolean);
let islenmis=[];
if (fs.existsSync("islenmis.txt")) islenmis = fs.readFileSync("islenmis.txt","utf8").split("\n").map(s=>s.trim()).filter(Boolean);
const bitki = bitkiler.find(b=>!islenmis.includes(b));
if(!bitki){console.log("Tum bitkiler islendi.");process.exit(0);}
console.log("Secilen bitki:", bitki, `(${islenmis.length+1}/${bitkiler.length})`);

// Hassas konular icin guvenlik cercevesi (kenevir/kannabis vb.)
const HASSAS = /kenevir|kannabis|cannabis|esrar|marijuana|haşhaş|hashas|afyon/i.test(bitki);
const HASSAS_ARASTIRMA = HASSAS ? `
ONEMLI CERCEVE: Bu konu hassastir. SADECE tarihsel, botanik, endustriyel (lif, tekstil, kagit, halat, biyoplastik, tohum, yag), cevresel ve bilimsel/akademik arastirma boyutuyla ilgilen. Uyusturucu/keyif amacli kullanim, psikoaktif etki anlatimi, yetistirme/uretim/elde etme teknikleri KESINLIKLE KONU DISI. Yasal duzenlemeleri tarafsiz aktar (savunuculuk yok). Olgusal ve notr ol.` : "";
const HASSAS_YAZIM = HASSAS ? `
- HASSAS KONU KURALI: Tarafsizlik sart. Savunuculuk, ozendirme, keyif amacli kullanim, psikoaktif etki tarifi YOK. Yetistirme/uretim/elde etme tarifi YOK. Sadece tarih, bilim, sanayi (lif/tekstil/kagit), cevre ve kultur. Yasal gelismeleri notr aktar.` : "";

async function cagir(model, messages, opts={}){
  const res = await fetch("https://api.openai.com/v1/chat/completions",{
    method:"POST",
    headers:{"Content-Type":"application/json","Authorization":`Bearer ${API_KEY}`},
    body:JSON.stringify({model,messages,...opts})
  });
  if(!res.ok) throw new Error(`OpenAI ${res.status}: ${(await res.text()).slice(0,200)}`);
  return (await res.json()).choices?.[0]?.message?.content ?? "";
}
function jparse(t){ return JSON.parse(t.replace(/```json/gi,"").replace(/```/g,"").trim()); }

// 1) ARASTIRMA
async function arastir(){
  try{
    return await cagir(ARASTIRMA_MODEL,[
      {role:"user",content:`"${bitki}" hakkinda derin arastirma yap. SOMUT, az bilinen detaylar: botanik; tarih (hangi uygarlik, yuzyil, arkeolojik bulgu, efsane, ticaret yolu); bilim (etken madde kimyasal isimleriyle, calismalar, mekanizma); Anadolu kulturu (yore, gelenek, inanis); dunya mutfagi; sasirtici gercekler/hikayeler. Genel laf degil; SPESIFIK isim, tarih, yer, rakam ver. Turkce.${HASSAS_ARASTIRMA}`}
    ],{web_search_options:{}});
  }catch(e){console.log("Arastirma atlandi:",e.message);return "";}
}

// 2) KURGU
async function kurguYap(arastirma){
  const t = await cagir(MODEL,[
    {role:"system",content:"Sen National Geographic tarzi odullu bir belgesel yonetmenisin. Kuru bilgi degil, merak ve duygu uyandiran bir anlati kurarsin."},
    {role:"user",content:`Bitki: "${bitki}"
ARASTIRMA:
${arastirma.slice(0,7000)}

15-18 dakikalik belgeselin SAHNE PLANINI cikar. Toplam 32 sahne.
Carpici bir kanca ile basla; merakla ilerle; bilim-tarih-kultur katmanlarini or; guclu kapanis.
HER SAHNE FARKLI bir alt konuya odaklansin (tekrar yok).
Her sahne icin tek cumlelik plan.
SADECE JSON: { "plan": ["...","..."] }`}
  ],{temperature:0.85,max_tokens:3000,response_format:{type:"json_object"}});
  return jparse(t).plan || [];
}

// 3) YAZIM
async function sahneYaz(planGrup, arastirma, islenenKonular, baslangicNo){
  const liste = planGrup.map((p,i)=>`${baslangicNo+i}. ${p}`).join("\n");
  const t = await cagir(MODEL,[
    {role:"system",content:`Sen National Geographic belgesellerinin bas senaristisin. Yazimin: sinematik, surukleyici, ZENGIN kelime hazineli.
KESIN KURALLAR:
- Her sahne CARPICI bir kanca ile baslar (soru, gerilim, sasirtici goruntu veya olgu).
- AYNI kelimeyi/kalibi TEKRAR ETME. Bitki adini her cumlede soyleme; es anlamli, dolayli anlat.
- Klise YASAK: "yuzyillar boyunca", "bereketli topraklar", "essiz bitki", "Anadolu'nun..." gibi kaliplar.
- Cumle ritmi degissin: kisa-vurucu ve uzun-akici cumleleri karistir.
- Duyusal detay kullan (koku, doku, renk, ses, isik).
- Arastirmadaki SOMUT olgulari (isim, tarih, yer, rakam, kimyasal) isle; genel dolgu YASAK.
- Saglik dili: "tedavi/sifa" kesin iddia YOK; "calismalar gosteriyor, destekleyebilir".${HASSAS_YAZIM}`},
    {role:"user",content:`Bitki: "${bitki}"
ARASTIRMA (tek gercek kaynagin):
${arastirma.slice(0,5000)}
${islenenKonular?`\nBU KONULAR ZATEN ISLENDI, TEKRAR ETME: ${islenenKonular}`:""}

Su planlari DOLU belgesel sahnelerine donustur:
${liste}

Her sahne icin:
- "anlatim": 100-130 kelime, sinematik Turkce anlati. Kanca ile basla, somut detay/isim/tarih kullan, surukleyici.
- "gorsel": INGILIZCE, cok detayli sinematik image prompt (isik, atmosfer, kompozisyon, lens). Yazi/metin olmasin.
SADECE JSON: { "sahneler":[{"anlatim":"...","gorsel":"..."}] }`}
  ],{temperature:0.9,max_tokens:4096,response_format:{type:"json_object"}});
  return jparse(t).sahneler || [];
}

// 4) EDITOR (tekrar yok et, zenginlestir)
async function editle(sahneGrup){
  const liste = sahneGrup.map((s,i)=>`${i+1}. ${s.anlatim}`).join("\n\n");
  try{
    const t = await cagir(MODEL,[
      {role:"system",content:"Sen titiz bir belgesel kurgu editorusun. Metni daha surukleyici ve zengin kelime hazineli yaparsin."},
      {role:"user",content:`Asagidaki belgesel sahnelerini DUZELT:
- Kelime/kalip TEKRARLARINI yok et, kelime hazinesini zenginlestir (es anlamlilar, cesitli fiiller).
- Her sahnenin ACILISINI daha carpici yap.
- Klise ve dolgu cumleleri at; gerilim ve merak ekle.
- ANLAMI ve yaklasik uzunlugu (100-130 kelime) KORU. Sahne sayisini KORU.
- Saglik dilini koru ("destekleyebilir", kesin iddia yok).

SAHNELER:
${liste}

SADECE JSON: { "anlatimlar": ["duzeltilmis 1","duzeltilmis 2"] } (sira ayni)`}
    ],{temperature:0.7,max_tokens:4096,response_format:{type:"json_object"}});
    const arr = jparse(t).anlatimlar || [];
    return sahneGrup.map((s,i)=> arr[i]? {...s, anlatim: arr[i]} : s);
  }catch(e){ console.log("  Editor atlandi (orijinal korundu):", e.message); return sahneGrup; }
}

(async()=>{
  console.log("1/4 Derin arastirma...");
  const arastirma = await arastir();
  console.log("  Arastirma:", arastirma.length, "karakter");

  console.log("2/4 Hikaye kurgusu...");
  const plan = await kurguYap(arastirma);
  console.log("  Plan:", plan.length, "sahne");

  console.log("3/4 Sinematik yazim...");
  let tumSahneler=[], islenen="";
  const GRUP=8;
  for(let i=0;i<plan.length;i+=GRUP){
    const grup=plan.slice(i,i+GRUP);
    const sahneler=await sahneYaz(grup,arastirma,islenen,i+1);
    tumSahneler=tumSahneler.concat(sahneler);
    islenen += grup.join("; ")+"; ";
    console.log(`  Sahne ${i+1}-${i+grup.length} yazildi (${sahneler.length})`);
  }

  console.log("4/4 Editor (tekrar temizleme + zenginlestirme)...");
  let edited=[];
  for(let i=0;i<tumSahneler.length;i+=GRUP){
    const grup=tumSahneler.slice(i,i+GRUP);
    edited=edited.concat(await editle(grup));
    console.log(`  Duzeltildi ${i+1}-${i+grup.length}`);
  }
  tumSahneler=edited;

  const baslik=(await cagir(MODEL,[{role:"user",content:`"${bitki}" uzerine National Geographic tarzi belgesel icin merak uyandiran sik bir Turkce YouTube basligi yaz. SADECE basligi yaz, tirnak yok.`}],{temperature:0.9,max_tokens:60})).trim().replace(/^"|"$/g,"");

  fs.writeFileSync("senaryo.json",JSON.stringify({baslik,bitki,arastirma,sahneler:tumSahneler},null,2),"utf8");
  fs.appendFileSync("islenmis.txt", bitki + "\n", "utf8");
  console.log(`\nTamam! TOPLAM ${tumSahneler.length} sahne. Baslik: ${baslik}`);
  console.log(`islenmis.txt guncellendi: "${bitki}" eklendi.`);
})();
