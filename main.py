import os
import google.generativeai as genai
import yt_dlp
from googleapiclient.discovery import build

# API Yapılandırması
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def get_transcript(video_url):
    ydl_opts = {'writesubtitles': True, 'skip_download': True, 'subtitleslangs': ['en']}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info.get('description', '') # Basitlik için açıklama üzerinden gidiyoruz

def rewrite_with_solomon_dna(text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Sen bir 'Quantum Sovereign' içerik mimarısın. Aşağıdaki metni al ve onu 
    tamamen otoriter, minimalist, stoik-teknoloji felsefesiyle yeniden yaz. 
    Kopyalama yapma, sıfırdan bir 'Dijital Egemenlik' manifestosu çıkar.
    Metin: {text}
    """
    return model.generate_content(prompt).text

# Ana süreç
if __name__ == "__main__":
    url = "BURAYA_HEDEF_KANAL_URL_KOY" 
    raw_text = get_transcript(url)
    final_script = rewrite_with_solomon_dna(raw_text)
    print("--- Üretilen Özgün İçerik ---")
    print(final_script)
