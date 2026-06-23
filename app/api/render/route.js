import { NextResponse } from "next/server";
import { execFile } from "child_process";
import fs from "fs";
import path from "path";
import ffmpegPath from "ffmpeg-static";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

export async function GET() {
  const output = "/tmp/aitube-video.mp4";

  const args = [
    "-f", "lavfi",
    "-i", "color=c=black:s=1080x1920:d=8",
    "-vf",
    "drawtext=text='AITUBE VIDEO':fontcolor=white:fontsize=80:x=(w-text_w)/2:y=700,drawtext=text='Otomatik üretildi':fontcolor=white:fontsize=50:x=(w-text_w)/2:y=850",
    "-pix_fmt", "yuv420p",
    "-c:v", "libx264",
    "-y",
    output
  ];

  return new Promise((resolve) => {
    execFile(ffmpegPath, args, (error) => {
      if (error) {
        resolve(
          NextResponse.json({
            success: false,
            message: "MP4 üretilemedi",
            error: error.message,
          })
        );
        return;
      }

      const videoBuffer = fs.readFileSync(output);

      resolve(
        new NextResponse(videoBuffer, {
          headers: {
            "Content-Type": "video/mp4",
            "Content-Disposition": "inline; filename=aitube-video.mp4",
          },
        })
      );
    });
  });
}
