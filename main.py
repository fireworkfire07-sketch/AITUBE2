import os
import google.generativeai as genai
import yt_dlp

# API Yapılandırması
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY ortam değişkeni bulunamadı!")

genai.configure(api_key=api_key)

def get_latest_video_data(channel_url):
    print(f"Veri çekiliyor: {channel_url}")
    ydl_opts = {'quiet': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        # Kanalın en son videosunu al
        video = info['entries'][0]
        return f"Title: {video['title']}\nURL: {video['url']}"

def rewrite_with_solomon_dna(text):
    print("Gemini ile içerik işleniyor...")
    # Modele erişim için en standart tanımlama
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Sen bir 'Quantum Sovereign' içerik mimarısın. 
    The Solomon Wealth Code kanalının ruhunu ve otoritesini yansıtan bir içerik üretmen gerekiyor.
    Aşağıdaki veri kaynağını analiz et ve bu içeriği kopyalamadan, tamamen özgün, stoik, 
    minimalist ve 'Dijital Egemenlik' odaklı yeni bir video senaryosu yaz.
    
    Veri: {text}
    """
    response = model.generate_content(prompt)
    return response.text

if __name__ == "__main__":
    channel_url = "https://youtube.com/@thesolomonwealthcode"
    
    try:
        raw_data = get_latest_video_data(channel_url)
        final_script = rewrite_with_solomon_dna(raw_data)
        
        print("\n--- OTONOM OLARAK ÜRETİLEN ÖZGÜN İÇERİK ---\n")
        print(final_script)
        
    except Exception as e:
        print(f"Hata oluştu: {e}")
