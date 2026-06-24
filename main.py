import os
import google.generativeai as genai
from googleapiclient.discovery import build

def run():
    # 1. Bağlantıları kur
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    youtube = build('youtube', 'v3', developerKey=os.environ["YOUTUBE_API_KEY"])

    # 2. Videoyu çek
    request = youtube.search().list(
        part="snippet", 
        channelId="UCdM8w565v56jG6H-V3Y958g", 
        maxResults=1, 
        order="date", 
        type="video"
    )
    res = request.execute()
    
    if not res.get('items'):
        print("Kanalda video bulunamadı.")
        return

    video_title = res['items'][0]['snippet']['title']
    
    # 3. İçeriği üret
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"Video başlığı: {video_title}. Bu başlık için stoik ve otoriter bir manifesto yaz.")
    
    print("\n--- MANİFESTO ---")
    print(response.text)

if __name__ == "__main__":
    run()
