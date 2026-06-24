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

    # Kanal verilerini zorla çek
    channel_id = "UCdM8w565v56jG6H-V3Y958g"
    print(f"Hedef kanal taraniyor: {channel_id}")
    
    try:
        request = youtube.search().list(
            part="snippet", 
            channelId=channel_id, 
            maxResults=1, 
            order="date", 
            type="video"
        )
        res = request.execute()
        
        if not res.get('items'):
            print("YouTube API Yaniti Bos: Bu kanalda video bulunamadi veya API kotasi dolu.")
            return

        video_id = res['items'][0]['id']['videoId']
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
