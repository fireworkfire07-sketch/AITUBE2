import os
import google.generativeai as genai
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

def run():
    # Gemini yapılandırması
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    youtube = build('youtube', 'v3', developerKey=os.environ["YOUTUBE_API_KEY"])

    # Arama yerine kanalın uploads playlist'ine doğrudan erişim (Daha güvenilir)
    # Kanal ID'si: UCdM8w565v56jG6H-V3Y958g
    try:
        # 1. Kanalın yüklemeler listesini al
        channel_response = youtube.channels().list(id="UCdM8w565v56jG6H-V3Y958g", part="contentDetails").execute()
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # 2. Son videoyu çek
        playlist_response = youtube.playlistItems().list(playlistId=uploads_playlist_id, part="snippet", maxResults=1).execute()
        video_id = playlist_response['items'][0]['snippet']['resourceId']['videoId']
        title = playlist_response['items'][0]['snippet']['title']
        
        print(f"Tespit Edildi: {title} ({video_id})")

        # 3. Transkripti al
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en'])
            text = " ".join([t['text'] for t in transcript])
        except:
            text = "Transkript alınamadı."

        # 4. Manifesto Üret
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Video başlığı: {title}. Video metni: {text[:5000]}. Bu içeriği temel alarak stoik ve otoriter bir manifesto yaz."
        response = model.generate_content(prompt)
        
        print("\n--- MANİFESTO ---")
        print(response.text)

    except Exception as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    run()
ü
