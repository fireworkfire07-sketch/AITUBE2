// app/api/health/route.ts
// BAKIM-ONARIM ÜNİTESİ
// Sistemin tüm parçalarını denetler, JSON rapor döndürür.

export const dynamic = "force-dynamic";
export const maxDuration = 60;

type Check = {
  name: string;
  ok: boolean;
  detail: string;
};

async function ping(
  name: string,
  url: string,
  headers: Record<string, string> = {}
): Promise<Check> {
  try {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), 8000);
    const res = await fetch(url, { headers, signal: ctrl.signal });
    clearTimeout(t);
    return {
      name,
      ok: res.ok,
      detail: res.ok ? "Çalışıyor" : `HTTP ${res.status}`,
    };
  } catch (e: any) {
    return { name, ok: false, detail: e?.message || "Bağlantı hatası" };
  }
}

export async function GET(req: Request) {
  const checks: Check[] = [];

  const requiredEnvs = ["OPENAI_API_KEY", "JSON2VIDEO_API_KEY"];
  for (const key of requiredEnvs) {
    checks.push({
      name: `env:${key}`,
      ok: !!process.env[key],
      detail: process.env[key] ? "Tanımlı" : "EKSİK — Vercel ayarlarına ekle",
    });
  }

  if (process.env.OPENAI_API_KEY) {
    checks.push(
      await ping("openai", "https://api.openai.com/v1/models", {
        Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
      })
    );
  }

  const base = process.env.NEXT_PUBLIC_BASE_URL || new URL(req.url).origin;
  const internal = (process.env.PIPELINE_ENDPOINTS || "/api/create-video")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  for (const path of internal) {
    checks.push(await ping(`internal:${path}`, `${base}${path}`));
  }

  const allOk = checks.every((c) => c.ok);
  const report = {
    status: allOk ? "SAĞLIKLI" : "SORUN VAR",
    timestamp: new Date().toISOString(),
    checks,
  };

  if (!allOk && process.env.TELEGRAM_BOT_TOKEN && process.env.TELEGRAM_CHAT_ID) {
    const broken = checks
      .filter((c) => !c.ok)
      .map((c) => `❌ ${c.name}: ${c.detail}`)
      .join("\n");
    await fetch(
      `https://api.telegram.org/bot${process.env.TELEGRAM_BOT_TOKEN}/sendMessage`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: process.env.TELEGRAM_CHAT_ID,
          text: `🔧 AiTube Bakım Raporu\n\n${broken}`,
        }),
      }
    ).catch(() => {});
  }

  return Response.json(report, { status: allOk ? 200 : 503 });
}
