import os
import google.generativeai as genai
import yt_dlp

# API Anahtarını al
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def get_latest_video_data(channel_url):
    ydl_opts = {'quiet': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        video = info['entries'][0]
        return f"Title: {video['title']}\nURL: {video['url']}"

def rewrite_with_solomon_dna(text):
    # 'gemini-1.5-flash' yerine daha stabil olan 'gemini-1.5-pro' kullanıyoruz
    model = genai.GenerativeModel('gemini-1.5-pro')
    prompt = f"The Solomon Wealth Code tarzında, özgün bir 'Dijital Egemenlik' manifestosu yaz. Veri: {text}"
    return model.generate_content(prompt).text

if __name__ == "__main__":
    channel_url = "https://youtube.com/@thesolomonwealthcode"
    raw_data = get_latest_video_data(channel_url)
    print(rewrite_with_solomon_dna(raw_data))
