import os
import sys
import google.generativeai as genai
from googleapiclient.discovery import build

# Log akışını zorla aç
sys.stdout.reconfigure(line_buffering=True)

print("--- MOTOR ATEŞLENDİ: Üretim başlıyor... ---")

# API Anahtarlarını kontrol et
gemini_key = os.environ.get("GEMINI_API_KEY")
youtube_key = os.environ.get("YOUTUBE_API_KEY")

if not gemini_key or not youtube_key:
    print("HATA: API Anahtarları eksik! (GEMINI_API_KEY ve YOUTUBE_API_KEY kontrol edin)")
    sys.exit(1)

# API Kurulumları
genai.configure(api_key=gemini_key)
youtube = build('youtube', 'v3', developerKey=youtube_key)

def get_latest_video_data(channel_id):
    print(f"YouTube üzerinden kanal verisi çekiliyor: {channel_id}")
    request = youtube.search().list(
        part="snippet", 
        channelId=channel_id, 
        maxResults=1, 
        order="date", 
        type="video"
    )
    response = request.execute()
    
    if 'items' in response and len(response['items']) > 0:
        item = response['items'][0]
        title = item['snippet']['title']
        desc = item['snippet']['description']
        return f"Video Başlığı: {title}\nAçıklama: {desc}"
    else:
        return "Veri bulunamadı."

def rewrite_with_solomon_dna(text):
    print("Gemini içerik mimarisi çalıştırılıyor...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Sen bir 'Quantum Sovereign' içerik mimarısın.
    Aşağıdaki veri kaynağını (YouTube video başlığı ve açıklaması) analiz et ve 
    'The Solomon Wealth Code' kanalının stoik, otoriter ve minimalist tonunda,
    'Dijital Egemenlik' temalı özgün bir video senaryosu yaz.
    
    Kopyalama yapma, sadece temayı ve felsefeyi yansıt.
    
    Veri: {text}
    """
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    # The Solomon Wealth Code Kanal ID'si
    CHANNEL_ID = "UCdM8w565v56jG6H-V3Y958g"
    
    try:
        raw_data = get_latest_video_data(CHANNEL_ID)
        print("Veri başarıyla alındı.")
        
        sonuc = rewrite_with_solomon_dna(raw_data)
        
        print("\n" + "="*50)
        print("--- ÜRETİLEN MANİFESTO ---")
        print(sonuc)
        print("="*50 + "\n")
        
    except Exception as e:
        print(f"Kritik Hata: {e}")
