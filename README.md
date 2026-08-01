# AITUBE2

## Ne işe yarar

King Solomon / kadim zenginlik bilgeliği temalı, el çizimi kara-mürekkep çöp adam (stick figure) animasyonlu faceless YouTube kanalı için video üreten ve yayınlayan otomasyon. Konuyu ya `shp-engine` reposu yollar ya da `topics.txt`'ten rastgele seçilir; script, seslendirme, görsel, altyazı, thumbnail ve YouTube upload'ı bu repo tek başına yapar.

## Pipeline akışı

```
Konu (repository_dispatch new_topic'ten VEYA topics.txt'ten rastgele, islenmis.txt'tekiler haric)
   → generate()   [Groq: llama-3.3-70b-versatile]
        title, hook, script (~2200 kelime), description, tags,
        image_scenes (10 metafor sahnesi), pinned_comment uretir
   → tts()          [edge-tts, en-US-ChristopherNeural]         → voice.mp3
   → make_subs()     [faster-whisper, opsiyonel/best-effort]    → subs.ass
        (whisper kurulu degilse veya hata verirse sessizce atlanir, altyazisiz devam eder)
   → get_image() x10 [pollinations.ai, cop-adam/parsomen stili] → img_00..09.jpg
   → build()         [ffmpeg: goruntuler+ses+altyazi]           → final.mp4
   → thumbnail_metni()+make_thumbnail() [pollinations.ai + Pillow] → thumbnail.jpg
   → (UPLOAD_ENABLED ise) upload() [YouTube Data API v3]
        → final.mp4 upload + thumbnails().set(thumbnail.jpg)
        → status.containsSyntheticMedia = true
   → topic, islenmis.txt'e eklenir (tekrar uretilmesin diye)
```

Görsel/ses üretimi tamamen ücretsiz araçlarla (edge-tts, pollinations.ai, faster-whisper) yapılır — ücretli bir API'ye geçilmez.

## Workflow'lar

| Dosya | Ne yapar | Nasıl tetiklenir |
|---|---|---|
| `solomon_daily.yml` (Engine) | Yukarıdaki tüm üretim zincirini çalıştırır, `topics.txt`/`islenmis.txt`'i günceller | `repository_dispatch` (`new_topic`, `shp-engine`'den — konuyu `topics.txt`'e ekler, upload otomatik açılır) **veya** manuel (`upload_enabled` girdisiyle, konu `topics.txt`'ten rastgele seçilir) |

`timeout-minutes: 60` var — özellikle `faster-whisper` transkripsiyon adımı uzun sürebildiği için takılı kalan bir run'ı otomatik durdurur.

## Gerekli secret'lar

Değerler burada **asla** yazılmaz — sadece isim ve amaç. Repo → Settings → Secrets and variables → Actions.

| Secret | Ne işe yarar | Zorunlu mu |
|---|---|---|
| `GROQ_API_KEY` | `main.py` — script/meta üretimi | Evet |
| `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` | `main.py` — YouTube OAuth, video + thumbnail upload | Yalnızca upload açıksa |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Workflow başarısız olunca bildirim | Opsiyonel — yoksa adım sessizce atlanır |

**Uyarı:** Google Cloud OAuth consent screen **"In production"** olmalı. "Testing" modunda refresh token 7 günde geçersiz olur ve upload sessizce başarısız olur.

## Manuel çalıştırma

GitHub'da **Actions** → **Engine** → **Run workflow** → gerçekten YouTube'a yüklensin istiyorsan `upload_enabled` kutusunu işaretle. Konu elle girilmez — `topics.txt`'ten `islenmis.txt`'te olmayan rastgele bir satır seçilir.

> **Not:** "Re-run" o an `main` branch'inde olan kodu çalıştırır, workflow'un ilk çalıştığı tarihteki kodu değil.

`upload_enabled: false` ile çalıştırırsan hiçbir şey YouTube'a gitmez; script+ses+görsel+altyazı+render+thumbnail yine de üretilir ve Actions run'ının "Artifacts" bölümünden indirilebilir. Not: bu modda bile üretilen konu `islenmis.txt`'e yazılıp commit'lenir — yani aynı konuyla tekrar test etmek için `topics.txt`'e yeni bir satır eklemen veya `islenmis.txt`'ten o satırı silmen gerekir.

## Bilinen notlar / sorunlar

- `README.md` bu incelemeden önce hiç yoktu — ilk kez oluşturuldu.
- `requirements.txt` bu ay eklendi (öncesinde bağımlılıklar workflow dosyasına gömülüydü); `main.py`'nin import ettiği her paket listede.
- `make_subs()` best-effort: `faster-whisper` import edilemezse (kurulu değilse) altyazı adımı sessizce atlanır, video yine de üretilir.
- Bu repo bugün uçtan uca test edildi (`upload_enabled: false`) ve **tamamen başarılı** oldu — script, ses, altyazı, görsel, render ve thumbnail üretimi çalışıyor.
- Gerçek bir YouTube upload'ı veya `thumbnails().set()` çağrısı bu incelemede test edilmedi (upload her zaman kapalı test edildi).
