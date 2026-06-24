import os
import requests
from googleapiclient.discovery import build
import google.generativeai as genai

# 1. API Ayarları
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
youtube = build('youtube', 'v3', developerKey=os.environ["YOUTUBE_API_KEY"])
ELEVEN_KEY = os.environ["ELEVENLABS_API_KEY"]

# 2. Videoyu çek ve Metni yaz
def get_content():
    res = youtube.search().list(part="snippet", channelId="UCdM8w565v56jG6H-V3Y958g", maxResults=1, order="date", type="video").execute()
    title = res['items'][0]['snippet']['title']
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model.generate_content(f"Başlık: {title}. Otoriter bir manifesto yaz.").text

# 3. ElevenLabs ile Sese çevir
def text_to_speech(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/9BWtsMINqrJLrMRo9Q3j" # Örnek ses ID
    headers = {"xi-api-key": ELEVEN_KEY, "Content-Type": "application/json"}
    data = {"text": text, "model_id": "eleven_multilingual_v2"}
    response = requests.post(url, json=data, headers=headers)
    with open("output.mp3", "wb") as f:
        f.write(response.content)
    print("--- SES DOSYASI OLUŞTURULDU: output.mp3 ---")

if __name__ == "__main__":
    manifesto = get_content()
    print(manifesto)
    text_to_speech(manifesto)
