import os
import google.generativeai as genai
from googleapiclient.discovery import build

def run():
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    youtube = build('youtube', 'v3', developerKey=os.environ["YOUTUBE_API_KEY"])

    # Arama yerine kanalın videolarını doğrudan listele (Daha güvenilir)
    print("Kanal videoları sorgulanıyor...")
    request = youtube.channels().list(part="contentDetails", id="UCdM8w565v56jG6H-V3Y958g")
    response = request.execute()
    
    print(f"API Yanıtı: {response}") # <--- Kanal doğru mu, burada göreceğiz.

    if 'items' not in response or not response['items']:
        print("HATA: Kanal bulunamadı veya yetkisiz!")
        return

    # Eğer buraya kadar gelirse kanal doğru demektir.
    print("Kanal bulundu. Başarı!")

if __name__ == "__main__":
    run()
