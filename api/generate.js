import OpenAI from "openai";

const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Sadece POST desteklenir" });
  }

  const { prompt } = req.body;

  if (!prompt) {
    return res.status(400).json({ error: "Prompt boş olamaz" });
  }

  try {
    const response = await client.chat.completions.create({
      model: "gpt-4o-mini",
      max_tokens: 2000,
      messages: [
        {
          role: "system",
          content: "Sen profesyonel bir YouTube içerik stratejistisin. Viral, SEO uyumlu içerikler üretiyorsun."
        },
        { role: "user", content: prompt }
      ],
    });

    return res.status(200).json({
      result: response.choices[0].message.content,
    });

  } catch (error) {
    return res.status(500).json({ error: error.message });
  }
}
