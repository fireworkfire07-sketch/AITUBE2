import os, json, re, random, hashlib, asyncio, subprocess
import requests
from pathlib import Path
import edge_tts

API_KEY        = os.environ["GROQ_API_KEY"]
OUTPUT_DIR     = Path("output")
PROCESSED_FILE = Path("islenmis.txt")
TOPICS_FILE    = Path("topics.txt")
OUTPUT_DIR.mkdir(exist_ok=True)

SYSTEM_PROMPT = """You are a scriptwriter for a faceless YouTube channel about King Solomon and ancient wealth wisdom.

OUTPUT ONLY a valid JSON object. No markdown, no backticks, no text outside the JSON.
No control characters inside string values.

{
  "title": "max 70 char curiosity-gap title",
  "hook": "1-2 spoken sentences for the first 3 seconds",
  "script": "1200 word narration, spoken style, second person, calm authoritative tone",
  "description": "3 sentence YouTube description then: #solomonwisdom #ancientwealth #biblicalmoney #kingsolomon #wealthtips",
  "tags": ["solomon","wealth","money","wisdom","ancient","biblical","finance","rich"],
  "thumbnail_text": "3 punchy words",
  "image_prompts": ["scene 1, ancient Jerusalem, warm gold light, painterly realism, 16:9, no text","scene 2, ancient Jerusalem, warm gold light, painterly realism, 16:9, no text","scene 3, ancient Jerusalem, warm gold light, painterly realism, 16:9, no text","scene 4, ancient Jerusalem, warm gold light, painterly realism, 16:9, no text","scene 5, ancient Jerusalem, warm gold light, painterly realism, 16:9, no text","scene 6, ancient Jerusalem, warm gold light, painterly realism, 16:9, no text","scene 7, ancient Jerusalem, warm gold light, painterly realism, 16:9, no text","scene 8, ancient Jerusalem, warm gold light, painterly realism, 16:9, no text"]
}"""

def pick_topic():
    processed = set(PROCESSED_FILE.read_text().splitlines()) if PROCESSED_FILE.exists() else set()
    topics = [t.strip() for t in TOPICS_FILE.read_text().splitlines() if t.strip()]
    remaining = [t for t in topics if t not in processed]
    if not remaining:
        print("All topics done."); return None
    return random.choice(remaining)

def mark_processed(topic):
    with open(PROCESSED_FILE, "a") as f:
        f.write(topic + "\n")

def generate_script(topic):
    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json",
                 "HTTP-Referer": "https://github.com/fireworkfire07-sketch/AITUBE2"},
        json={"model": "meta-llama/llama-3.3-70b-instruct", "temperature": 0.7, "max_tokens": 4096,
              "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                           {"role": "user", "content": f"Topic: {topic}"}]},
        timeout=120
    )
    r.raise_for_status()
    raw = r.json()["choices"][0]["message"]["content"]
    raw = re.sub(r"```json|```", "", raw).strip()
    s = raw.find("{"); e = raw.rfind("}") + 1
    raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', raw[s:e])
    return json.loads(raw)

def tts(text, out_path):
    async def _run():
        comm = edge_tts.Communicate(text, voice="en-US-ChristopherNeural", rate="-10%", pitch="-2Hz")
        await comm.save(str(out_path))
    asyncio.run(_run())

def get_duration(path):
    r = subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration",
                        "-of","default=noprint_wrappers=1:nokey=1", str(path)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())

def download_image(prompt, idx, folder):
    seed = int(hashlib.md5(prompt.encode()).hexdigest(), 16) % 99999
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1792&height=1008&seed={seed}&nologo=true"
    r = requests.get(url, timeout=60); r.raise_for_status()
    p = folder / f"img_{idx:02d}.jpg"; p.write_bytes(r.content)
    return p

def build_video(images, audio, out, duration):
    n = len(images)
    per = duration / n
    inputs = []
    for img in images:
        inputs += ["-loop","1","-t",str(per),"-i",str(img)]
    parts = []
    for i in range(n):
        parts.append(f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,fps=25[v{i}]")
    cin = "".join(f"[v{i}]" for i in range(n))
    parts.append(f"{cin}concat=n={n}:v=1:a=0[vout]")
    parts.append(f"[{n}:a]volume=1.0[aout]")
    subprocess.run(
        ["ffmpeg","-y"] + inputs + ["-i",str(audio),
         "-filter_complex",";".join(parts),
         "-map","[vout]","-map","[aout]",
         "-c:v","libx264","-preset","fast","-crf","23",
         "-c:a","aac","-b:a","192k","-r","25","-pix_fmt","yuv420p",
         str(out)], check=True)

def main():
    topic = pick_topic()
    if not topic: return
    print(f"Topic: {topic}")
    slug = topic[:40].replace(" ","_")
    work = OUTPUT_DIR / slug
    work.mkdir(exist_ok=True)

    print("Generating script...")
    data = generate_script(topic)
    (work/"data.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"Title: {data['title']}")

    print("TTS...")
    audio = work / "voice.mp3"
    tts(data["hook"] + "\n\n" + data["script"], audio)
    duration = get_duration(audio)
    print(f"Duration: {duration:.1f}s")

    print("Images...")
    img_folder = work / "images"
    img_folder.mkdir(exist_ok=True)
    images = []
    for i, prompt in enumerate(data["image_prompts"][:8]):
        print(f"  img {i+1}/8")
        images.append(download_image(prompt, i, img_folder))

    print("Rendering...")
    video = work / "final.mp4"
    build_video(images, audio, video, duration)
    (work/"meta.json").write_text(json.dumps({
        "title": data["title"],
        "description": data["description"],
        "tags": ",".join(data["tags"])
    }, ensure_ascii=False))
    mark_processed(topic)
    print(f"Done: {video}")

if __name__ == "__main__":
    main()
