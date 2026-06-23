// YouTube bağlantı testi — anahtarları 1 saniyede doğrular
export const dynamic = "force-dynamic";

export async function GET() {
  const id = process.env.YT_CLIENT_ID || "";
  const secret = process.env.YT_CLIENT_SECRET || "";
  const token = process.env.YT_REFRESH_TOKEN || "";

  const res = await fetch("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: id,
      client_secret: secret,
      refresh_token: token,
      grant_type: "refresh_token",
    }),
  });
  const data = await res.json();

  return Response.json({
    sonuc: data.access_token ? "BAŞARILI — YouTube bağlantısı çalışıyor ✓" : "HATA",
    googleCevabi: data.access_token ? "token alındı" : data,
    kontrol: {
      clientId_uzunluk: id.length,
      clientId_dogru_bitiyor: id.endsWith(".apps.googleusercontent.com"),
      secret_uzunluk: secret.length,
      secret_dogru_basliyor: secret.startsWith("GOCSPX-"),
      refreshToken_uzunluk: token.length,
      refreshToken_dogru_basliyor: token.startsWith("1//"),
    },
  });
}
