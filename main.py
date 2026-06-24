import os
import google.generativeai as genai
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

def run():
    # 1. Gemini Yapılandırması (Yeni kütüphane formatı)
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 2. YouTube Bağlantısı
    youtube = build('youtube', 'v3', developerKey=os.environ["YOUTUBE_API_KEY"])

    # 3. Son Videoyu Bul (ID yerine Kanal ID ile garanti arama)
    request = youtube.search().list(
        part="snippet",
        channelId="UCdM8w565v56jG6H-V3Y958g",
        maxResults=1,
        order="date",
        type="video"
    )
    res = request.execute()

    if not res.get('items'):
        print("Video bulunamadi.")
        return

    video_id = res['items'][0]['id']['videoId']
    title = res['items'][0]['snippet']['title']
    print(f"Tespit Edilen: {title}")

    # 4. Transkripti Al
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en'])
        full_text = " ".join([i['text'] for i in transcript])
        context = full_text[:5000]
    except:
        context = f"Video Basligi: {title}. (Transkript alinamadi.)"

    # 5. Manifesto Üret
    response = model.generate_content(f"Video verisi: {context}. Bu icerikten stoik ve otoriter bir manifesto yaz.")
    
    print("\n--- MANIFESTO ---\n")
    print(response.text)

if __name__ == "__main__":
    run()
