import os
import google.generativeai as genai
from googleapiclient.discovery import build

def run():
    print("Sistem baslatildi...")
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    youtube_key = os.environ.get("YOUTUBE_API_KEY")
    
    if not gemini_key or not youtube_key:
        print("Hata: API anahtarlari eksik!")
        return

    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    youtube = build('youtube', 'v3', developerKey=youtube_key)

    # Gercek dogrulanmis Playlist ID (Kanal ID'sinin UC kismi UU yapildi)
    uploads_playlist_id = "UU7fA_oT_U9E_I2RkXWwXmZQ"
    print(f"Oynatma listesinden en son video cekiliyor: {uploads_playlist_id}")
    
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
        print(f"Basariyla Yakalandi -> Video ID: {video_id} | Baslik: {title}")

        # Manifesto Uretimi
        print("Gemini'ye talimat gonderiliyor, manifesto uretiliyor...")
        prompt = (
            f"Analyze this video concept. Title: {title}. "
            f"Based on this, write a highly powerful, original, stoic, and authoritative video script manifesto in ENGLISH for a faceless YouTube channel. "
            f"It must be unique, compelling, and ready for a professional voiceover narration."
        )
        
        response = model.generate_content(prompt)
        
        print("\n--- ENGLISH MANIFESTO OUTPUT ---\n")
        print(response.text)
        print("\n--- ISLEM TAMAMLANDI ---")

    except Exception as e:
        print(f"Sistem calisirken hata verdi: {str(e)}")

if __name__ == "__main__":
    run()
