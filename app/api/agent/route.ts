// AI BEYİN v2 — Niş rotasyonlu kanal yöneticisi
export const dynamic = "force-dynamic";
export const maxDuration = 300;

const NISLER = [
  "sevimli dinozorlar",
  "uzay ve gezegenler",
  "taşıtlar (itfaiye, ekskavatör, tren)",
  "okyanus ve deniz canlıları",
  "orman hayvanları",
  "masal ve fantastik yaratıklar (ejderha, tek boynuzlu at)",
  "meyveler ve sebzeler",
  "evcil hayvanlar ve çiftlik",
  "böcekler ve kelebekler",
  "mevsimler ve doğa olayları",
];

export async function GET(req: Request) {
  const base = process.env.NEXT_PUBLIC_BASE_URL || new URL(req.url).origin;
  const log: string[] = [];

  try {
    const healthRes = await fetch(`${base}/api/health`);
    const health = await healthRes.json();
    log.push(`Sağlık: ${health.status}`);
    if (health.status !== "SAĞLIKLI") {
      await notify(`⚠️ Agent durdu: sistem sağlıksız.`);
      return Response.json({ decision: "BAKIM_GEREKLI", health, log });
    }

    // Güne göre niş seç (her çalıştırmada farklı olsun diye saat de katılır)
    const simdi = new Date();
    const nisIndex = (simdi.getDate() + simdi.getHours()) % NISLER.length;
    const nis = NISLER[nisIndex];
    log.push(`Bugünün nişi: ${nis}`);

    const systemPrompt = `Sen çocuklara yönelik eğitici boyama videoları üreten profesyonel bir YouTube kanalının yöneticisisin.
Bugünün nişi: "${nis}"
Bu niş içinden, YouTube'da çocukların (3-7 yaş) ve ebeveynlerin arayacağı, özgün ve ilgi çekici BİR video konusu üret.
SADECE şu JSON formatında cevap ver:
{"action":"URET","topic":"video konusu (niş içinden, spesifik)","reason":"kısa Türkçe gerekçe"}`;

    const aiRes = await fetch("https://api.openai.com/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [
          { role: "system", content: systemPrompt },
          { role: "user", content: `Tarih: ${simdi.toISOString()}. Konu kararını ver.` },
        ],
        temperature: 1.0,
        response_format: { type: "json_object" },
      }),
    });
    const aiData = await aiRes.json();
    const decision = JSON.parse(aiData.choices?.[0]?.message?.content || "{}");
    log.push(`Karar: ${decision.topic}`);

    let pipelineResult: any = null;
    if (decision.action === "URET" && decision.topic) {
      const pipelinePath = process.env.VIDEO_PIPELINE_URL || "/api/create-video";
      const pRes = await fetch(`${base}${pipelinePath}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic: decision.topic, nis, source: "agent" }),
      });
      pipelineResult = { ok: pRes.ok, status: pRes.status };
      log.push(`Pipeline: ${pRes.ok ? "BAŞARILI" : "HATA " + pRes.status}`);
      if (!pRes.ok) {
        const retry = await fetch(`${base}${pipelinePath}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ topic: decision.topic, nis, source: "agent-retry" }),
        });
        pipelineResult.retried = true;
        pipelineResult.retryOk = retry.ok;
        log.push(`Tekrar deneme: ${retry.ok ? "BAŞARILI" : "YİNE HATA"}`);
      }
    }

    await notify(`🤖 AiTube Raporu\n📂 Niş: ${nis}\n📌 Konu: ${decision.topic}\n📋 ${log.join("\n")}`);
    return Response.json({ decision, nis, pipelineResult, log });
  } catch (e: any) {
    await notify(`🔴 Agent hatası: ${e?.message}`);
    return Response.json({ error: e?.message, log }, { status: 500 });
  }
}

async function notify(text: string) {
  if (!process.env.TELEGRAM_BOT_TOKEN || !process.env.TELEGRAM_CHAT_ID) return;
  await fetch(`https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: process.env.TELEGRAM_CHAT_ID, text }),
  }).catch(() => {});
}
