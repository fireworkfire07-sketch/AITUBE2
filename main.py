import os
import google.generativeai as genai
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

def run():
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    
    # 1. Video ID'sini al
    video_id = "VİDEO_ID_BURAYA" # Buraya videonun linkindeki kod gelecek
    
    # 2. Transkripti çek
    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['tr', 'en'])
    full_text = " ".join([i['text'] for i in transcript])
    
    # 3. Gemini ile işle
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"Video metni: {full_text[:10000]}. Bu içeriği temel alarak 10 dakikalık bir videoya uygun, otoriter ve stoik bir manifesto yaz.")
    
    print("\n--- TAM KAPSAMLI MANİFESTO ---")
    print(response.text)

if __name__ == "__main__":
    run()
