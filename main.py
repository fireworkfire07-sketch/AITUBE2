import os
import google.generativeai as genai
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

def run():
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    youtube = build('youtube', 'v3', developerKey=os.environ["YOUTUBE_API_KEY"])

    # En son videoyu otomatik bul
    res = youtube.search().list(part="id", channelId="UCdM8w565v56jG6H-V3Y958g", maxResults=1, order="date", type="video").execute()
    video_id = res['items'][0]['id']['videoId']
    
    # Transkripti çek
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en'])
        full_text = " ".join([i['text'] for i in transcript])
        context = full_text[:10000] # Token sınırı için ilk 10k karakter
    except:
        context = "Transkript alınamadı."

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"Video metni: {context}. Bu içeriği analiz et ve derinlikli, stoik, otoriter bir manifesto yaz.")
    
    print("\n--- TAM KAPSAMLI MANİFESTO ---")
    print(response.text)

if __name__ == "__main__":
    run()
