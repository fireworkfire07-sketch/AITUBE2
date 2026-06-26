import os, json, re, random, hashlib, asyncio, subprocess
import requests
from pathlib import Path
import edge_tts

API_KEY = os.environ["GROQ_API_KEY"]
OUTPUT  = Path("output"); OUTPUT.mkdir(exist_ok=True)
PROCESSED = Path("islenmis.txt")
TOPICS    = Path("topics.txt")

STYLE = "minimalist black ink stick figure line drawing on aged cream parchment paper, hand-drawn doodle style, simple, no color, vintage textured background, lots of empty space, 16:9, no text"

SYSTEM = """You are a scriptwriter for a faceless YouTube channel about King Solomon and ancient wealth wisdom. The channel uses simple hand-drawn black-ink STICK FIGURE animations on aged parchment paper. Every visual is a VISUAL METAPHOR of the idea being narrated (e.g. a stick figure stacking blocks into a tower = building wealth; a stick figure running from a crowd = breaking from the herd).

OUTPUT ONLY valid JSON. No markdown, no backticks, no control characters in strings.
{
 "title": "max 70 char curiosity-gap title",
 "hook": "1-2 spoken sentences for the first 3 seconds",
 "script": "2200 word narration in spoken style, second person, calm authoritative tone, smooth transitions, no repetition, building to a strong conclusion",
 "description": "3 sentences then: #solomonwisdom #ancientwealth #wealthmindset #kingsolomon #money",
 "tags": ["solomon","wealth","money","wisdom","ancient","mindset","rich","success"],
 "image_scenes": ["plain description of ONE stick-figure metaphor scene for beat 1, NO style words","scene 2 metaphor","scene 3 metaphor","scene 4 metaphor","scene 5 metaphor","scene 6 metaphor","scene 7 metaphor","scene 8 metaphor","scene 9 metaphor","scene 10 metaphor"],
 "pinned_comment": "engaging question to drive comments"
}"""

def pick_topic():
    done = set(PROCESSED.read_text().splitlines()) if PROCESSED.exists() else set()
    topics = [t.strip() for t in TOPICS.read_text().splitlines() if t.strip()]
    rem = [t for t in topics if t not in done]
    return random.choice(rem) if rem else None

def generate(topic):
    r = requests.post("https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type":"application/json"},
        json={"model":"meta-llama/llama-3.3-70b-instruct","temperature":0.7,"max_tokens":8000,
              "messages":[{"role":"system","content":SYSTEM},{"role":"user","content":f"Topic: {topic}"}]},
        timeout=180)
    r.raise_for_status()
    raw = r.json()["choices"][0]["message"]["content"]
    raw = re.sub(r"```json|```","",raw)
    s, e = raw.find("{"), raw.rfind("}")+1
    raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]','',raw[s:e])
    return json.loads(raw)

def tts(text, out):
    async def _r():
        c = edge_tts.Communicate(text, voice="en-US-ChristopherNeural", rate="-10%", pitch="-2Hz")
        await c.save(str(out))
    asyncio.run(_r())

def duration(p):
    r = subprocess.run(["ffprobe","-v","quiet","-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",str(p)], capture_output=True, text=True, check=True)
    return float(r.stdout.strip())

def make_subs(audio, ass_path):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("  no whisper, skipping subs"); return False
    model = WhisperModel("small", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(str(audio), word_timestamps=True)
    head = ["[Script Info]","ScriptType: v4.00+","PlayResX: 1920","PlayResY: 1080","",
        "[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding",
        "Style: Default,Arial,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,4,2,2,80,80,120,1","",
        "[Events]","Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text"]
    def ts(s):
        h=int(s//3600); m=int((s%3600)//60); sc=s%60
        return f"{h}:{m:02d}:{sc:05.2f}"
    lines=[]
    for seg in segments:
        words = getattr(seg,"words",None)
        if not words:
            lines.append(f"Dialogue: 0,{ts(seg.start)},{ts(seg.end)},Default,,0,0,0,,{seg.text.strip()}")
            continue
        for i in range(0,len(words),4):
            grp = words[i:i+4]
            txt = " ".join(w.word.strip() for w in grp)
            lines.append(f"Dialogue: 0,{ts(grp[0].start)},{ts(grp[-1].end)},Default,,0,0,0,,{txt}")
    Path(ass_path).write_text("\n".join(head+lines), encoding="utf-8")
    return True

def get_image(scene, idx, folder):
    prompt = f"{scene}, {STYLE}"
    seed = int(hashlib.md5(scene.encode()).hexdigest(),16)%99999
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1792&height=1008&seed={seed}&nologo=true"
    r = requests.get(url, timeout=60); r.raise_for_status()
    p = folder/f"img_{idx:02d}.jpg"; p.write_bytes(r.content); return p

def build(images, audio, ass_path, out, dur):
    n = len(images); per = dur/n; inp = []
    for img in images: inp += ["-loop","1","-t",str(per),"-i",str(img)]
    parts = [f"[{i}:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,fps=25[v{i}]" for i in range(n)]
    parts.append("".join(f"[v{i}]" for i in range(n))+f"concat=n={n}:v=1:a=0[cat]")
    if Path(ass_path).exists():
        parts.append(f"[cat]ass={ass_path}[vout]")
    else:
        parts.append("[cat]copy[vout]")
    parts.append(f"[{n}:a]volume=1.0[aout]")
    subprocess.run(["ffmpeg","-y"]+inp+["-i",str(audio),"-filter_complex",";".join(parts),
        "-map","[vout]","-map","[aout]","-c:v","libx264","-preset","fast","-crf","23",
        "-c:a","aac","-b:a","192k","-r","25","-pix_fmt","yuv420p",str(out)], check=True)

def upload(video, meta):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build as gbuild
    from googleapiclient.http import MediaFileUpload
    creds = Credentials(token=None,
        refresh_token=os.environ["YT_REFRESH_TOKEN"],
        client_id=os.environ["YT_CLIENT_ID"],
        client_secret=os.environ["YT_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.upload"])
    yt = gbuild("youtube","v3",credentials=creds)
    body = {"snippet":{"title":meta["title"],"description":meta["description"],
            "tags":meta["tags"].split(","),"categoryId":"27","defaultLanguage":"en"},
            "status":{"privacyStatus":"public","selfDeclaredMadeForKids":False,"containsSyntheticMedia":True}}
    media = MediaFileUpload(str(video), mimetype="video/mp4", resumable=True, chunksize=10*1024*1024)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status: print(f"  upload {int(status.progress()*100)}%")
    print(f"DONE: https://youtu.be/{resp['id']}")

def main():
    topic = pick_topic()
    if not topic: print("All topics done."); return
    print(f"Topic: {topic}")
    work = OUTPUT/topic[:40].replace(" ","_"); work.mkdir(exist_ok=True)

    print("Script..."); data = generate(topic)
    wc = len(data["script"].split())
    print(f"Title: {data['title']}  ({wc} words)")

    print("Voice..."); audio = work/"voice.mp3"
    tts(data["hook"]+"\n\n"+data["script"], audio)
    dur = duration(audio); print(f"  {dur:.0f}s ({dur/60:.1f} min)")

    print("Subtitles..."); ass = work/"subs.ass"
    make_subs(audio, ass)

    print("Images (stick-figure)..."); imgf = work/"img"; imgf.mkdir(exist_ok=True)
    scenes = data.get("image_scenes", [])[:10]
    images = [get_image(sc, i, imgf) for i, sc in enumerate(scenes)]

    print("Render..."); video = work/"final.mp4"
    build(images, audio, ass, video, dur)

    meta = {"title":data["title"],"description":data["description"],"tags":",".join(data["tags"])}
    print("Upload..."); upload(video, meta)

    with open(PROCESSED,"a") as f: f.write(topic+"\n")
    print("OK")

if __name__ == "__main__":
    main()
