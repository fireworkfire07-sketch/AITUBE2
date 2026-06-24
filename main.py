import os
import google.generativeai as genai
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

def run():
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    youtube = build('youtube', 'v3', developerKey=os.environ["YOUTUBE_API_KEY"])

    # Kanalın ID'sini çözmek yerine direkt kanalın son videosunu alalım
    res = youtube.search().list(part="snippet", channelId="UCdM8w565v56jG6H-V3Y958g", maxResults=1, order="date", type="video").execute()
    
    if not res.get('items'):
        print("Video bulunamadı, kanal ID'sini kontrol et.")
        return

    video_info = res['items'][0]['snippet']
    video_id = res['items'][0]['id']['videoId']
    title = video_info['title']
    
    context = f"Başlık: {title}"
    
    try:
        # Transkripti dene
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en'])
        full_text = " ".join([i['text'] for i in transcript])
        context += f". Video İçeriği: {full_text[:5000]}"
    except:
        context += ". (Transkript kapalı, sadece başlığa göre analiz et.)"

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"{context}. Bu veriyi analiz et ve stoik, otoriter bir manifesto yaz.")
    
    print(f"\n--- {title} - ANALİZ ---")
    print(response.text)

if __name__ == "__main__":
    run()
