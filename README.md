# AITUBE2

## Kurulum

GitHub Actions çalışması için repo **Settings → Secrets and variables → Actions** altında şu secret'lar tanımlı olmalı:

| Secret | Kullanıldığı yer | Zorunlu mu |
|---|---|---|
| `GROQ_API_KEY` | `main.py` — script + meta üretimi (ücretsiz Groq modeli) | Evet |
| `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN` | `main.py` — YouTube'a video ve thumbnail yükleme | Yalnızca `upload_enabled` açıksa |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Workflow hata bildirimi | Opsiyonel — yoksa bildirim adımı sessizce atlanır |

**Uyarı:** Google Cloud OAuth consent screen **"In production"** olmalı. "Testing" modunda refresh token 7 günde geçersiz olur ve upload sessizce başarısız olur.
