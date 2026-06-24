import os
import google.generativeai as genai
import yt_dlp

# API Yapılandırması
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def get_latest_video_data(channel_url):
    # Kanalın en son videosunu bulur
    ydl_opts = {'quiet': True, 'extract_flat': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        video = info['entries'][0] # En son video
        return f"Title: {video['title']}\nURL: {video['url']}"

def rewrite_with_solomon_dna(text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Sen bir 'Quantum Sovereign' içerik mimarısın. Aşağıdaki veriyi (The Solomon Wealth Code kanalından) al. 
    Bu içeriğin temelindeki otoriter, minimalist ve stoik-teknoloji felsefesini analiz et.
    Bu videonun içeriğini kopyalama, ancak aynı frekansta, tamamen özgün, teknik derinliği olan 
    ve izleyiciye 'Sistem Kurucu' vizyonunu aşılayan yeni bir video senaryosu yaz.
    
    Veri: {text}
    """
    return model.generate_content(prompt).text

if __name__ == "__main__":
    # Kanal linki kodun içine sabitlendi
    channel_url = "https://youtube.com/@thesolomonwealthcode"
    print(f"Sistem başlatılıyor: {channel_url} taranıyor...")
    
    raw_data = get_latest_video_data(channel_url)
    final_script = rewrite_with_solomon_dna(raw_data)
    
    print("\n--- OTONOM OLARAK ÜRETİLEN ÖZGÜN İÇERİK ---\n")
    print(final_script)
