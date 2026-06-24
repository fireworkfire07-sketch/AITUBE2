import os
import google.generativeai as genai
from googleapiclient.discovery import build

# API Bağlantıları
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
youtube = build('youtube', 'v3', developerKey=os.environ["YOUTUBE_API_KEY"])

# Veriyi çek ve üret
request = youtube.search().list(part="snippet", channelId="UCdM8w565v56jG6H-V3Y958g", maxResults=1, order="date", type="video")
video = request.execute()['items'][0]
model = genai.GenerativeModel('gemini-1.5-flash')
print("--- SONUÇ ---")
print(model.generate_content(f"Video başlığı: {video['snippet']['title']}. Hakkında bir manifesto yaz.").text)
