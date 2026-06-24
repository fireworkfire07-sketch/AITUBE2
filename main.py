import os
import google.generativeai as genai
from googleapiclient.discovery import build

def run():
    # 1. API Anahtarlarini Al
    gemini_key = os.environ.get("GEMINI_API_KEY")
    youtube_key = os.environ.get("YOUTUBE_API_KEY")
    
    if not gemini_key or not youtube_key:
        print("Hata: API anahtarlari eksik!")
        return

    # 2. Yapilandirma
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    youtube = build('youtube', 'v3', developerKey=youtube_key)

    # 3. Playlist Yontemiyle En Son Videoyu Bul (Kota dostu ve kesindir)
    # Kanal: @thesolomonwealthcode | ID: UCdM8w565v56jG6H-V3Y958g
    uploads_playlist_id = "UUdM8w565v56jG6H-V3Y958g"
    
    try:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=1
        )
        res = request.execute()
        
        if not res.get('items'):
            print("Hata: Kanal icerigi bos veya playlist bulunamadi.")
            return

        video_id = res['items'][0]['snippet']['resourceId']['videoId']
        title = res['items'][0]['snippet']['title']
        print(f"Tespit Edilen Video: {title} ({video_id})")

        # 4. Gemini ile Ozgun Ingilizce Manifesto Uretimi
        prompt = (
            f"Analyze this video concept. Title: {title}. "
            f"Write a highly powerful, original, stoic, and authoritative video script manifesto in ENGLISH for a faceless YouTube channel. "
            f"It must be unique, optimized for voiceover narration, and include an intense hook at the beginning."
        )
        
        response = model.generate_content(prompt)
        
        print("\n--- ENGLISH MANIFESTO OUTPUT ---\n")
        print(response.text)
        print("\n--- ISLEM TAMAMLANDI ---")

    except Exception as e:
        print(f"Sistem calisirken hata verdi: {str(e)}")

if __name__ == "__main__":
    run()
