import os
import google.generativeai as genai
from googleapiclient.discovery import build

def run():
    print("Sistem baslatildi...")
    
    # API baglantilari
    gemini_key = os.environ.get("GEMINI_API_KEY")
    youtube_key = os.environ.get("YOUTUBE_API_KEY")
    
    if not gemini_key or not youtube_key:
        print("Hata: API anahtarlari eksik!")
        return

    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    youtube = build('youtube', 'v3', developerKey=youtube_key)

    # Kanal ID'sinin basindaki 'UC'yi 'UU' yaparak doğrudan yuklenenler listesine ulasiyoruz (Kotayi harcamaz)
    uploads_playlist_id = "UUdM8w565v56jG6H-V3Y958g"
    print(f"Oynatma listesinden en son video cekiliyor: {uploads_playlist_id}")
    
    try:
        # Arama (search) yerine doğrudan playlistItems kullanıyoruz
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=1
        )
        res = request.execute()
        
        if not res.get('items'):
            print("YouTube Playlist Yaniti Bos. Lutfen kanal ID'sini kontrol edin.")
            return

        video_id = res['items'][0]['snippet']['resourceId']['videoId']
        title = res['items'][0]['snippet']['title']
        print(f"Basariyla Yakalandi -> Video ID: {video_id} | Baslik: {title}")

        # Manifesto Uretimi
        print("Gemini'ye talimat gonderiliyor, manifesto uretiliyor...")
        prompt = (
            f"Analyze this video theme. Title: {title}. "
            f"Based on this concept, write a highly powerful, original, stoic, and authoritative video script manifesto in ENGLISH. "
            f"It must be completely unique, engaging for a faceless YouTube video, and optimized for a strong voiceover narration."
        )
        
        response = model.generate_content(prompt)
        
        print("\n--- ENGLISH MANIFESTO OUTPUT ---\n")
        print(response.text)
        print("\n--- ISLEM TAMAMLANDI ---")

    except Exception as e:
        print(f"Sistem calisirken bir hata olustu: {str(e)}")

if __name__ == "__main__":
    run()
