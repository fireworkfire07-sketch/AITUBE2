def get_latest_video_data(channel_url):
    ydl_opts = {
        'quiet': True, 
        'extract_flat': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        video = info['entries'][0]
        return f"Title: {video['title']}\nURL: {video['url']}"
