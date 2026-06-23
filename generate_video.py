
import os
import json
import random
import hashlib
import requests
import subprocess
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
API_KEY        = os.environ["GROQ_API_KEY"]   # OpenRouter key buraya geliyor
OUTPUT_DIR     = Path("output")
PROCESSED_FILE = Path("islenmis.txt")
TOPICS_FILE    = Path("topics.txt")
MUSIC_FILE     = Path("assets/bgmusic.mp3")

OUTPUT_DIR.mkdir(exist_ok=True)

SYSTEM_PROMPT = """You are the head scriptwriter for a faceless YouTube channel about ancient wealth wisdom — King Solomon, biblical money principles, timeless financial secrets.

HARD RULES:
- Output ONLY a single valid JSON object. No markdown, no backticks, no extra text.
- 100% original content. Never copy any existing channel's scripts or phrasing.
- Do NOT quote scripture verbatim beyond ~10 words. Paraphrase everything.
- No financial guarantees or get-rich-quick claims.
- Write narration to be SPOKEN: short sentences, second person, calm, authoritative, lightly reverent rhythm.
- Vary the opening line between videos. Do not start every script the same way.

OUTPUT — exactly this JSON:
{
  "title": "primary title, curiosity-gap, max 70 chars",
  "alt_titles": ["two alternative titles"],
  "hook": "1-2 sentences for the first 3 seconds",
  "script": "full narration ~1400 words. Arc: hook -> Solomon's authority -> ONE principle -> why most people get it wrong -> how to apply it today in concrete steps -> reflective close -> soft subscribe CTA. Spoken style only.",
  "description": "YouTube description: 2-line hook, short paragraph, 3-5 lowercase hashtags, then this exact line on its own: This video uses AI-assisted narration and visuals.",
  "tags": ["8 relevant tags"],
  "thumbnail_text": "2-4 punchy words",
  "image_prompts": ["10 prompts, one per visual beat, each ending with: cinematic, warm gold and deep amber palette, ancient Jerusalem and royal opulence, volumetric golden light, painterly realism, 16:9, no on-screen text"],
  "pinned_comment": "engaging question to drive comments"
}"""

# ── Helpers ──────────────────────────────────────────────────────────────────

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
        print("All topics processed. Add more to topics.txt")
        return None
    return random.choice(remaining)

def generate_script(topic):
    """OpenRouter API — llama-3.3-70b-versatile"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/fireworkfire07-sketch/A-TUBE2",
        "X-Title": "Solomon Wealth Channel"
    }
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct",
        "temperature": 0.85,
        "max_tokens": 4096,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps({
                "topic": topic, "lang": "en", "target_words": 1400
            })}
        ]
    }
    r = requests.post(url, headers=headers, json=payload, timeout=120)
    r.raise_for_status()
    raw = r.json()["choices"][0]["message"]["content"].strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)

def tts(text, out_path):
    cmd = [
        "edge-tts",
        "--voice", "en-US-ChristopherNeural",
        "--rate",  "-10%",
        "--pitch", "-2Hz",
        "--text",  text,
        "--write-media", str(out_path),
    ]
    subprocess.run(cmd, check=True)

def get_audio_duration(path):
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True
    )
    return float(result.stdout.strip())

def download_image(prompt, idx, folder):
    seed = int(hashlib.md5(prompt.encode()).hexdigest(), 16) % 99999
    url  = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1792&height=1008&seed={seed}&nologo=true&enhance=true"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    p = folder / f"img_{idx:02d}.jpg"
    p.write_bytes(r.content)
    return p

def make_ass(audio_path, ass_path):
    """faster-whisper ile kelime-kelime ASS altyazı"""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("faster-whisper not installed, skipping subtitles")
        return False

    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(audio_path), word_timestamps=True)

    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1920",
        "PlayResY: 1080",
        "",
        "[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
        "Style: Default,Arial,56,&H00D4A843,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,1,2,60,60,80,1",
        "",
        "[Events]",
        "Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text",
    ]

    def ts(s):
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sc = s % 60
        return f"{h}:{m:02d}:{sc:05.2f}"

    for seg in segments:
        lines.append(
            f"Dialogue: 0,{ts(seg.start)},{ts(seg.end)},Default,,0,0,0,,{seg.text.strip()}"
        )

    Path(ass_path).write_text("\n".join(lines), encoding="utf-8")
    return True

def build_video(images, audio_path, ass_path, out_path, duration):
    per_img = duration / len(images)
    inputs = []
    for img in images:
        inputs += ["-loop", "1", "-t", str(per_img), "-i", str(img)]

    has_music = MUSIC_FILE.exists()
    music_inputs = ["-stream_loop", "-1", "-i", str(MUSIC_FILE)] if has_music else []

    zooms = [
        "zoompan=z='min(zoom+0.0008,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
        "zoompan=z='if(lte(zoom,1.0),1.12,max(1.0,zoom-0.0008))':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
        "zoompan=z='min(zoom+0.0008,1.12)':x='min(iw*0.15,iw/2-(iw/zoom/2))':y='ih/2-(ih/zoom/2)'",
    ]

    filter_parts = []
    for i in range(len(images)):
        z = zooms[i % len(zooms)]
        filter_parts.append(
            f"[{i}:v]{z}:d={int(per_img*25)}:s=1920x1080:fps=25,setsar=1[v{i}]"
        )

    concat_in = "".join(f"[v{i}]" for i in range(len(images)))
    filter_parts.append(f"{concat_in}concat=n={len(images)}:v=1:a=0[base]")

    if Path(ass_path).exists():
        filter_parts.append(f"[base]ass={ass_path}[vout]")
        vout = "[vout]"
    else:
        vout = "[base]"

    filter_complex = ";".join(filter_parts)

    voice_idx = len(images)
    if has_music:
        music_idx = len(images) + 1
        filter_complex += (
            f";[{voice_idx}:a]volume=1.0[voice]"
            f";[{music_idx}:a]volume=0.10[music]"
            ";[voice][music]amix=inputs=2:duration=first[aout]"
        )
        aout = "[aout]"
    else:
        filter_complex += f";[{voice_idx}:a]volume=1.0[aout]"
        aout = "[aout]"

    cmd = (
        ["ffmpeg", "-y"]
        + inputs + music_inputs
        + ["-i", str(audio_path)]
        + ["-filter_complex", filter_complex]
        + ["-map", vout, "-map", aout]
        + ["-c:v", "libx264", "-preset", "fast", "-crf", "22"]
        + ["-c:a", "aac", "-b:a", "192k"]
        + ["-af", "loudnorm=I=-14:LRA=11:TP=-1.5"]
        + ["-r", "25", "-pix_fmt", "yuv420p"]
        + [str(out_path)]
    )
    subprocess.run(cmd, check=True)

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    topic = pick_topic()
    if not topic:
        return

    print(f"🎯 Topic: {topic}")
    slug = topic[:40].replace(" ", "_").replace("/", "-")
    work = OUTPUT_DIR / slug
    work.mkdir(exist_ok=True)

    print("📝 Generating script via OpenRouter...")
    data = generate_script(topic)
    (work / "data.json").write_text(json.dumps(data, indent=2, ensure_ascii=False))

    title       = data["title"]
    script_text = data["hook"] + "\n\n" + data["script"]
    image_prompts = data["image_prompts"]
    print(f"📺 Title: {title}")

    print("🎙️  Generating voice...")
    audio_path = work / "voice.mp3"
    tts(script_text, audio_path)
    duration = get_audio_duration(audio_path)
    print(f"⏱️  Duration: {duration:.1f}s")

    print("🖼️  Downloading images...")
    img_folder = work / "images"
    img_folder.mkdir(exist_ok=True)
    images = []
    for i, prompt in enumerate(image_prompts[:10]):
        print(f"   img {i+1}/10...")
        images.append(download_image(prompt, i, img_folder))

    print("💬 Generating subtitles...")
    ass_path = work / "subtitles.ass"
    make_ass(audio_path, ass_path)

    print("🎬 Rendering video...")
    video_path = work / "final.mp4"
    build_video(images, audio_path, str(ass_path), video_path, duration)

    meta = {
        "title":       title,
        "description": data["description"],
        "tags":        ",".join(data["tags"]),
    }
    (work / "meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    mark_processed(topic)

    print(f"✅ Done! → {video_path}")
    print(f"📌 Pinned comment: {data['pinned_comment']}")

if __name__ == "__main__":
    main()
