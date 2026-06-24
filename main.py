import os
import sys
import google.generativeai as genai
import yt_dlp

# Çıktıları loglara zorla yazdır
sys.stdout.reconfigure(line_buffering=True)
print("--- MOTOR ATEŞLENDİ: Üretim başlıyor... ---")

# API Anahtarı kontrolü
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("HATA: GEMINI_API_KEY bulunamadı!")
    sys.exit(1)

genai.configure(api_key=api_key)

def get_latest_video_data(channel_url):
    print(f"Hedef kanal taranıyor: {channel_url}")
    ydl_opts = {
        'quiet': True, 
        'extract_flat': True,
        'user_agent': 'Mozilla/5.0'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        video = info['entries'][0]
        return f"Video Başlığı: {video['title']}\nURL: {video['url']}"

def rewrite_with_solomon_dna(text):
    print("Gemini beyin işliyor...")
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = f"""
    Sen 'The Solomon Wealth Code' kanalının otoriter, stoik ve minimalist vizyonunu temsil eden bir Quantum Sovereign içerik mimarısın.
    Aşağıdaki veri kaynağını analiz et ve bu içeriği kopyalamadan, tamamen özgün, teknik derinliği olan 
    ve izleyiciye 'Dijital Egemenlik' vizyonunu aşılayan bir video senaryosu yaz.
    
    Veri: {text}
    """
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    channel_url = "https://youtube.com/@thesolomonwealthcode"
    raw_data = get_latest_video_data(channel_url)
    sonuc = rewrite_with_solomon_dna(raw_data)
    
    print("\n--- İŞTE YENİ DİJİTAL EGEMENLİK SENARYON ---\n")
    print(sonuc)
