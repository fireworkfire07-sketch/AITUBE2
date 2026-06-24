import os
import google.generativeai as genai
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

def run():
    # 1. API Ayarları
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    youtube = build('youtube', 'v3', developerKey=os.environ["YOUTUBE_API_KEY"])

    # 2. Kanalı tarama (En son videoyu garantili bulma)
    search_response = youtube.search().list(
        channelId="UCdM8w565v56jG6H-V3Y958g",
        order="date",
        part="snippet",
        maxResults=1,
        type="video"
    ).execute()

    if not search_response.get('items'):
        print("Video bulunamadı.")
        return

    item = search_response['items'][0]
    video_id = item['id']['videoId']
    title = item['snippet']['title']
    print(f"Tespit edilen video: {title} ({video_id})")

    # 3. Transkripti çekme veya Başlık kullanımı
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en', 'en-US'])
        full_text = " ".join([i['text'] for i in transcript])
        context = full_text[:8000]
    except:
        context = f"Başlık: {title}. (Transkript çekilemedi, sadece başlık analizi yapılacak.)"

    # 4. Gemini Analizi
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"Video verisi: {context}. Bu içerikten stoik, otoriter ve etkileyici bir manifesto yaz.")
    
    print("\n--- TAM KAPSAMLI MANİFESTO ---")
    print(response.text)

if __name__ == "__main__":
    run()
