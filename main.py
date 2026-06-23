import os, re, json, time, asyncio, subprocess, shutil, urllib.parse
import requests, edge_tts
from groq import Groq
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ===================== AYARLAR =====================
SES          = "tr-TR-AhmetNeural"      # alternatif kadın ses: tr-TR-EmelNeural
GROQ_MODEL   = "openai/gpt-oss-120b"    # eski llama-3.3-70b-versatile kapandı
SAHNE_SAYISI = 7
FPS          = 30
GIZLILIK     = "public"                 # test için "private" yap
KATEGORI     = "22"                     # 22=Kişiler&Bloglar, 24=Eğlence, 27=Eğitim
TMP          = "calisma"
# ===================================================

client = Groq(api_key=os.environ["GROQ_API_KEY"])

def log(m): print(f"[AITUBE2] {m}", flush=True)

# ---- konu seçimi ----
def siradaki_konu():
    if not os.path.exists("konular.txt"):
        raise SystemExit("konular.txt yok. Her satıra bir konu yaz.")
    konular = [k.strip() for k in open("konular.txt", encoding="utf-8") if k.strip()]
    islenmis = []
    if os.path.exists("islenmis.txt"):
        islenmis = [k.strip() for k in open("islenmis.txt", encoding="utf-8") if k.strip()]
    for k in konular:
        if k not in islenmis:
            return k
    return None

# ---- senaryo (Groq) ----
def senaryo_uret(konu):
    sistem = ("Sen deneyimli bir YouTube belgesel/hikaye senaristisin. Akıcı, merak "
              "uyandıran, Türkçe anlatım yazarsın. Yanıtını YALNIZCA geçerli JSON ver; "
              "başına veya sonuna açıklama ya da kod bloğu işareti ekleme.")
    kullanici = f'''"{konu}" konusunu işleyen bir YouTube videosu hazırla.

Şu JSON yapısında döndür:
{{
  "baslik": "60 karakteri geçmeyen, merak uyandıran Türkçe başlık",
  "aciklama": "2-3 cümlelik Türkçe açıklama",
  "etiketler": ["etiket1","etiket2","etiket3","etiket4","etiket5"],
  "sahneler": [
    {{"anlatim":"2-3 cümlelik akıcı Türkçe anlatım","gorsel":"detailed cinematic English image prompt, atmospheric lighting"}}
  ]
}}

Kurallar:
- Tam {SAHNE_SAYISI} sahne üret.
- "anlatim" alanları birbirini takip eden bütünlüklü bir anlatı oluştursun.
- İlk sahne güçlü bir merak kancası (hook) ile başlasın.
- "gorsel" alanları İngilizce, sinematik, ayrıntılı olsun (ışık, atmosfer, kompozisyon).
- Sadece JSON döndür.'''
    r = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "system", "content": sistem},
                  {"role": "user", "content": kullanici}],
        temperature=0.8,
    )
    ham = r.choices[0].message.content
    s, e = ham.find("{"), ham.rfind("}")
    if s == -1 or e == -1:
        raise ValueError("Groq geçerli JSON döndürmedi:\n" + ham[:500])
    return json.loads(ham[s:e+1])

# ---- seslendirme (edge-tts) ----
def seslendir(metin, cikti):
    async def _go():
        c = edge_tts.Communicate(metin, SES)
        await c.save(cikti)
    for deneme in range(4):
        try:
            asyncio.run(_go())
            if os.path.getsize(cikti) > 1000:
                return
        except Exception as ex:
            log(f"TTS hata ({deneme+1}/4): {ex}")
        time.sleep(3 * (deneme + 1))
    raise RuntimeError("Seslendirme başarısız: " + metin[:60])

# ---- görsel (Pollinations) ----
def gorsel_uret(prompt, cikti):
    url = ("https://image.pollinations.ai/prompt/"
           + urllib.parse.quote(prompt)
           + "?width=1280&height=720&nologo=true&model=flux")
    for deneme in range(5):
        try:
            r = requests.get(url, timeout=120)
            if r.status_code == 200 and len(r.content) > 5000:
                with open(cikti, "wb") as f:
                    f.write(r.content)
                return True
        except Exception as ex:
            log(f"Görsel hata ({deneme+1}/5): {ex}")
        time.sleep(5 * (deneme + 1))
    return False

def dolgu_gorsel(cikti):
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi",
                    "-i", "color=c=0x101820:s=1280x720",
                    "-frames:v", "1", cikti], check=True)

# ---- süre ölçümü ----
def sure(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True)
    return float(out.stdout.strip())

# ---- tek sahne klibi (Ken Burns + ses) ----
def sahne_klibi(gorsel, ses, cikti):
    d = sure(ses)
    frames = int((d + 1) * FPS)
    vf = (f"scale=2560:1440:force_original_aspect_ratio=increase,crop=2560:1440,"
          f"zoompan=z='min(zoom+0.0010,1.25)':d={frames}:"
          f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':fps={FPS}:s=1920x1080,"
          f"setsar=1,format=yuv420p")
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-i", gorsel, "-i", ses,
        "-vf", vf, "-c:v", "libx264", "-preset", "medium",
        "-c:a", "aac", "-b:a", "192k", "-r", str(FPS),
        "-pix_fmt", "yuv420p", "-shortest", cikti
    ], check=True)

# ---- YouTube yükleme ----
def youtube_yukle(dosya, baslik, aciklama, etiketler):
    creds = Credentials(
        None,
        refresh_token=os.environ["YT2_REFRESH_TOKEN"],
        client_id=os.environ["YT2_CLIENT_ID"],
        client_secret=os.environ["YT2_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
    )
    creds.refresh(Request())  # token'ı erken doğrula
    yt = build("youtube", "v3", credentials=creds)
    govde = {
        "snippet": {
            "title": baslik[:95],
            "description": aciklama,
            "tags": etiketler,
            "categoryId": KATEGORI,
        },
        "status": {
            "privacyStatus": GIZLILIK,
            "selfDeclaredMadeForKids": False,
        },
    }
    medya = MediaFileUpload(dosya, chunksize=-1, resumable=True)
    istek = yt.videos().insert(part="snippet,status", body=govde, media_body=medya)
    yanit = None
    while yanit is None:
        _, yanit = istek.next_chunk()
    log(f"Yüklendi: https://youtu.be/{yanit['id']}")
    return yanit["id"]

# ===================== ANA AKIŞ =====================
def main():
    konu = siradaki_konu()
    if not konu:
        log("İşlenecek yeni konu yok. konular.txt'ye ekleme yap.")
        return
    log(f"Konu: {konu}")

    if os.path.exists(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP)

    veri = senaryo_uret(konu)
    sahneler = veri["sahneler"]
    log(f"{len(sahneler)} sahne üretildi.")

    klipler = []
    son_iyi_gorsel = None
    for i, sahne in enumerate(sahneler):
        g = os.path.join(TMP, f"gorsel_{i}.jpg")
        a = os.path.join(TMP, f"ses_{i}.mp3")
        k = os.path.join(TMP, f"klip_{i}.mp4")

        if gorsel_uret(sahne["gorsel"], g):
            son_iyi_gorsel = g
        elif son_iyi_gorsel:
            shutil.copy(son_iyi_gorsel, g)
        else:
            dolgu_gorsel(g)

        seslendir(sahne["anlatim"], a)
        sahne_klibi(g, a, k)
        klipler.append(os.path.abspath(k))
        log(f"Sahne {i+1}/{len(sahneler)} tamam.")

    # birleştir
    liste = os.path.join(TMP, "liste.txt")
    with open(liste, "w", encoding="utf-8") as f:
        for k in klipler:
            f.write(f"file '{k}'\n")
    final = os.path.join(TMP, "final.mp4")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", os.path.abspath(liste), "-c", "copy", final], check=True)

    # açıklama + AI bildirimi
    etiketler = veri.get("etiketler", [])
    hashtagler = " ".join("#" + re.sub(r"\s+", "", t) for t in etiketler[:5])
    aciklama = (veri["aciklama"] + "\n\n" + hashtagler +
                "\n\nBu video yapay zekâ araçları kullanılarak hazırlanmıştır.")

    youtube_yukle(final, veri["baslik"], aciklama, etiketler)

    # KRİTİK: konuyu işlenmiş olarak işaretle (eski hata buydu)
    with open("islenmis.txt", "a", encoding="utf-8") as f:
        f.write(konu + "\n")
    log("islenmis.txt güncellendi.")

if __name__ == "__main__":
    main()
