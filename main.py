import os
import random
from google import genai

def run():
    print("Sistem baslatildi...")
    
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        print("Hata: GEMINI_API_KEY eksik!")
        return

    # 2026 Yeni Nesil Google GenAI istemcisi
    client = genai.Client(api_key=gemini_key)

    # Hedef kanalin en guclu video temalari
    video_themes = [
        {"title": "It's IMPOSSIBLE to Get Rich on a Salary Alone", "topic": "The trap of modern stability, multiple streams of income, dynamic vs linear wealth"},
        {"title": "The Unfair Advantage of Being Silent", "topic": "Stoic silence, emotional control, power dynamic through listening instead of talking"},
        {"title": "Why 99% of People Remain Poor", "topic": "Consumer mindset vs builder mindset, delayed gratification, ancient rules of money accumulation"}
    ]

    selected = random.choice(video_themes)
    print(f"Secilen Tema: {selected['title']}")

    try:
        print("Gemini'ye talimat gonderiliyor, manifesto uretiliyor...")
        prompt = (
            f"Analyze this concept. Title: {selected['title']}. Topic: {selected['topic']}. "
            f"Based on this concept, write a highly powerful, original, stoic, and authoritative video script manifesto in ENGLISH for a faceless YouTube channel. "
            f"It must be completely unique, intense, and ready for a professional voiceover narration."
        )
        
        # Yeni kütüphane formatinda model cagirisi
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        print("\n--- ENGLISH MANIFESTO OUTPUT ---\n")
        print(response.text)
        print("\n--- ISLEM TAMAMLANDI ---")

    except Exception as e:
        print(f"Sistem calisirken hata verdi: {str(e)}")

if __name__ == "__main__":
    run()
