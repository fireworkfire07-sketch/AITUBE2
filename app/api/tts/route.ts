// TTS — metni Türkçe sese çevirir (OpenAI)
export const dynamic = "force-dynamic";
export const maxDuration = 60;

export async function GET(req: Request) {
  try {
    const text = new URL(req.url).searchParams.get("text");
    if (!text) return new Response("text parametresi gerekli", { status: 400 });

    const res = await fetch("https://api.openai.com/v1/audio/speech", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: "tts-1",
        voice: "nova",
        input: text,
        response_format: "mp3",
      }),
    });
    if (!res.ok) return new Response("TTS hatası: " + (await res.text()), { status: 500 });

    return new Response(res.body, {
      headers: {
        "Content-Type": "audio/mpeg",
        "Content-Disposition": 'attachment; filename="ses.mp3"',
      },
    });
  } catch (e: any) {
    return new Response("Hata: " + e?.message, { status: 500 });
  }
}
