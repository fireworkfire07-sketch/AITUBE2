import os
import google.generativeai as genai
from googleapiclient.discovery import build

# API Bağlantıları
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
youtube = build('youtube', 'v3', developerKey=os.environ["YOUTUBE_API_KEY"])

def get_latest_video():
    # En son videoyu doğrudan çek
    request = youtube.search().list(part="snippet", channelId="UCdM8w565v56jG6H-V3Y958g", maxResults=1, order="date", type="video")
    res = request.execute()
    item = res['items'][0]
    return f"Baslik: {item['snippet']['title']}"

def generate_script(video_info):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Solomon Wealth Code tarzında, Dijital Egemenlik üzerine bir senaryo yaz. Kaynak: {video_info}"
    return model.generate_content(prompt).text

if __name__ == "__main__":
    data = get_latest_video()
    print("--- SONUC ---")
    print(generate_script(data))
