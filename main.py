import os
import google.generativeai as genai
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

def run():
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    youtube = build('youtube', 'v3', developerKey=os.environ["YOUTUBE_API_KEY"])

    # Kanal ID'si üzerinden doğrudan "uploads" listesini çekme denemesi
    request = youtube.channels().list(part="contentDetails", id="UCdM8w565v56jG6H-V3Y958g")
    response = request.execute()
    
    if not response.get('items'):
        print("Kanal bulunamadı.")
        return

    uploads_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    # Uploads listesinden en son videoyu çek
    video_request = youtube.playlistItems().list(part="snippet,contentDetails", playlistId=uploads_id, maxResults=1)
    video_response = video_request.execute()
    
    video_id = video_response['items'][0]['contentDetails']['videoId']
    title = video_response['items'][0]['snippet']['title']
    
    print(f"Hedef Video: {title} ({video_id})")

    # İçerik üretimi
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en'])
        full_text = " ".join([i['text'] for i in transcript])
        context = full_text[:8000]
    except:
        context = f"Başlık: {title}. (Transkript çekilemedi.)"

    model = genai.GenerativeModel('gemini-1.5-flash')
    manifesto = model.generate_content(f"Video verisi: {context}. Bu içerikten stoik, otoriter ve etkileyici bir manifesto yaz.")
    
    print("\n--- TAM KAPSAMLI MANİFESTO ---")
    print(manifesto.text)

if __name__ == "__main__":
    run()
