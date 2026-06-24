import os
import sys
import google.generativeai as genai
from googleapiclient.discovery import build

# Logları anlık görebilmemiz için yapılandırma
sys.stdout.reconfigure(line_buffering=True)
print("--- MOTOR ATEŞLENDİ ---")

# API Anahtarlarını al
gemini_key = os.environ.get("GEMINI_API_KEY")
youtube_key = os.environ.get("YOUTUBE_API_KEY")

# Anahtar kontrolü
if not gemini_key or not youtube_key:
    print("HATA: API Anahtarları eksik! GitHub Secrets ayarlarını kontrol et.")
    sys.exit(1)

# Bağlantıları kur
genai.configure(api_key=gemini_key)
# DÜZELTİLMİŞ YETKİLENDİRME SATIRI:
youtube = build('youtube', 'v3', developerKey=youtube_key)

def get_latest_video():
    print("YouTube'dan veri çekiliyor...")
    request = youtube.search().list(
        part="snippet", 
        channelId="UCdM8w565v56jG6H-V3Y958g", 
        maxResults=1, 
        order="date", 
        type="video"
    )
    res = request.execute()
    item = res['items'][0]
    return f"Başlık: {item['snippet']['title']}"

def generate_script(video_info):
    print("Gemini mimarisi çalışıyor...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Solomon Wealth Code kanalının tarzında, Dijital Egemenlik üzerine bir senaryo yaz. Kaynak: {video_info}"
    return model.generate_content(prompt).text

if __name__ == "__main__":
    try:
        data = get_latest_video()
        script = generate_script(data)
        print("\n--- SONUÇ ---")
        print(script)
    except Exception as e:
        print(f"KRİTİK HATA: {e}")
