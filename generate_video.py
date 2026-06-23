import os
import json
import re
import random
import hashlib
import requests
import subprocess
from pathlib import Path

API_KEY        = os.environ["GROQ_API_KEY"]
OUTPUT_DIR     = Path("output")
PROCESSED_FILE = Path("islenmis.txt")
TOPICS_FILE    = Path("topics.txt")
MUSIC_FILE     = Path("assets/bgmusic.mp3")

OUTPUT_DIR.mkdir(exist_ok=True)

SYSTEM_PROMPT = """You are the head scriptwriter for a faceless YouTube channel about ancient wealth wisdom — King Solomon, biblical money principles, timeless financial secrets.

HARD RULES:
- Output ONLY a single valid JSON object. No markdown, no backticks, no extra text before or after.
- No newlines or special control characters inside JSON string values. Use \\n only if needed.
- 100% original content. Never copy any existing channel scripts.
- Do NOT quote scripture verbatim beyond 10 words. Paraphrase everything.
- No financial guarantees or get-rich-quick claims.
- Write narration to be SPOKEN: short sentences, second person, calm and authoritative tone.

OUTPUT — exactly this JSON structure:
{
  "title": "curiosity-gap title, max 70 chars",
  "alt_titles": ["alternative title 1", "alternative title 2"],
  "hook": "1-2 sentences for the first 3 seconds",
  "script": "full narration 1200-1400 words, spoken style only",
  "description": "YouTube description 3-4 sentences then hashtags: #solomonwisdom #ancientwealth #biblicalmoney",
  "tags": ["solomon", "wealth", "money", "wisdom", "biblical", "ancient", "finance", "rich"],
  "thumbnail_text": "2-4 punchy words",
  "image_prompts": ["prompt 1 cinematic warm gold deep amber palette ancient Jerusalem volumetric golden light painterly realism 16:9 no text", "prompt 2 cinematic warm gold deep amber palette ancient Jerusalem volumetric golden light painterly realism 16:9 no text", "prompt 3 cinematic warm gold deep amber palette ancient Jerusalem volumetric golden light painterly realism 16:9 no text", "prompt 4 cinematic warm gold deep amber palette ancient Jerusalem volumetric golden light painterly realism 16:9 no text", "prompt 5 cinematic warm gold deep amber palette ancient Jerusalem volumetric golden light painterly realism 16:9 no text", "prompt 6 cinematic warm gold deep amber palette ancient Jerusalem volumetric golden light painterly realism 16:9 no text", "prompt 7 cinematic warm gold deep amber palette ancient Jerusalem volumetric golden light painterly realism 16:9 no text", "prompt 8 cinematic warm gold deep amber palette ancient Jerusalem volumetric golden light painterly realism 16:9 no text", "prompt 9 cinematic warm gold deep amber palette ancient Jerusalem volumetric golden light painterly realism 16:9 no text", "prompt 10 cinematic warm gold deep amber palette ancient Jerusalem volumetric golden light painterly realism 16:9 no text"],
  "pinned_comment": "engaging question to drive comments"
}"""

def load_processed():
    if PROCESSED_FILE.exists():
        return set(PROCESSED_FILE.read_text().splitlines())
    return set()

def mark_processed(topic):
    with open(PROCESSED_FILE, "a") as f:
        f.write(topic + "\n")

def pick_topic():
    processed = load_processed()
    topics = [t.strip() for t in TOPICS_FILE.read_text().splitlines() if t.strip()]
    remaining = [t for t in topics if t not in processed]
    if not remaining:
        print("All topics processed.")
        return None
    return random.choice(remaining)

def clean_json(raw):
    # Markdown fence temizle
    raw = re.sub(r"```json\s*", "", raw)
    raw = re.sub(r"```\s*", "", raw)
    raw = raw.strip()
    # JSON bloğunu bul
    start = raw.find("{")
    end   = raw.rfind("}") + 1
    if start >= 0 and end > start:
        raw = raw[start:end]
    # Bozuk kontrol karakterlerini temizle
    raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', raw)
    return raw

def generate_script(topic):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/fireworkfire07-sketch/AITUBE2",
        "X-Title": "Solomon Wealth Channel"
    }
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct",
        "temperature": 0.75,
        "max_tokens": 4096,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Topic: {topic}"}
        ]
    }
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    raw = r.json()["choices"][0]["message"]["content"]
    raw = clean_json(raw)
    return json.loads(raw)

def tts(text, out_path):
    subprocess.run([
        "edge-tts",
        "--voice", "en-US-ChristopherNeural",
        "--rate",  "-10%",
        "--pitch", "-2Hz",
        "--text",  text,
        "--write-media", str(out_path),
    ], check=True)

def get_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True
    )
    return float(r.stdout.strip())

def download_image(prompt, idx, folder):
    seed = int(hashlib.md5(prompt.encode()).hexdigest(), 16) % 99999
    url  = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1792&height=1008&seed={seed}&nologo=true&enhance=true"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    p = folder / f"img_{idx:02d}.jpg"
    p.write_bytes(r.content)
    return p

def build_video(images, audio_path, out_path, duration):
    per_img = duration / len(images)
    inputs  = []
    for img in images:
        inputs += ["-loop", "1", "-t", str(per_img), "-i", str(img)]

    zooms = [
        "zoompan=z='min(zoom+0.0008,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
        "zoompan=z='if(lte(zoom,1.0),1.12,max(1.0,zoom-0.0008))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
        "zoompan=z='min(zoom+0.0008,1.12)':x='min(iw*0.15,iw/2-(iw/zoom/2))':y='ih/2-(ih/zoom/2)'",
    ]

    parts = []
    for i in range(len(images)):
        z = zooms[i % len(zooms)]
        parts.append(f"[{i}:v]{z}:d={int(per_img*25)}:s=1920x1080:fps=25,setsar=1[v{i}]")

    concat_in = "".join(f"[v{i}]" for i in range(len(images)))
    parts.append(f"{concat_in}concat=n={len(images)}:v=1:a=0[vout]")

    vi = len(images)
    parts.append(f"[{vi}:a]volume=1.0[aout]")

    fc = ";".join(parts)

    cmd = (
        ["ffmpeg", "-y"]
        + inputs
        + ["-i", str(audio_path)]
        + ["-filter_complex", fc]
        + ["-map", "[vout]", "-map", "[aout]"]
        + ["-c:v", "libx264", "-preset", "fast", "-crf", "22"]
        + ["-c:a", "aac", "-b:a", "192k"]
        + ["-af", "loudnorm=I=-14:LRA=11:TP=-1.5"]
        + ["-r", "25", "-pix_fmt", "yuv420p"]
        + [str(out_path)]
    )
    subprocess.run(cmd, check=True)

def main():
    topic = pick_topic()
    if not topic:
        return

    print(f"🎯 Topic: {topic}")
    slug = topic[:40].replace(" ", "_").replace("/", "-")
    work = OUTPUT_DIR / slug
    work.mkdir(exist_ok=True)

    print("📝 Generating script...")
    data = generate_script(topic)
    (work / "data.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))

    title         = data["title"]
    script_text   = data["hook"] + "\n\n" + data["script"]
    image_prompts = data["image_prompts"]
    print(f"📺 Title: {title}")

    print("🎙️  Voice...")
    audio_path = work / "voice.mp3"
    tts(script_text, audio_path)
    duration = get_duration(audio_path)
    print(f"⏱️  {duration:.1f}s")

    print("🖼️  Images...")
    img_folder = work / "images"
    img_folder.mkdir(exist_ok=True)
    images = []
    for i, prompt in enumerate(image_prompts[:10]):
        print(f"   {i+1}/10")
        images.append(download_image(prompt, i, img_folder))

    print("🎬 Rendering...")
    video_path = work / "final.mp4"
    build_video(images, audio_path, video_path, duration)

    meta = {
        "title":       title,
        "description": data["description"],
        "tags":        ",".join(data["tags"]),
    }
    (work / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    mark_processed(topic)

    print(f"✅ Done → {video_path}")

if __name__ == "__main__":
    main()
