"""Cria video_tiktok.mp4: o mesmo vídeo com a CAPA como primeiro quadro (o TikTok usa o 1º quadro como capa).
São 2 quadros (~0,07 s), invisíveis no ritmo. Uso: python scripts/capa_no_video.py fila/<pasta> [...]"""
import subprocess, sys
from pathlib import Path


def fazer(pasta: Path) -> Path | None:
    v, c, out = pasta / "video.mp4", pasta / "capa.jpg", pasta / "video_tiktok.mp4"
    if not (v.exists() and c.exists()):
        return None
    if out.exists() and out.stat().st_mtime > max(v.stat().st_mtime, c.stat().st_mtime):
        return out
    filtro = ("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,format=yuv420p,trim=end_frame=2[c];"
              "[1:v]scale=1080:1920,setsar=1,fps=30,format=yuv420p[v];"
              "anullsrc=r=48000:cl=stereo,atrim=duration=0.0667[s];[1:a]aresample=48000[a];"
              "[c][s][v][a]concat=n=2:v=1:a=1[ov][oa]")
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(c), "-i", str(v), "-filter_complex", filtro,
                        "-map", "[ov]", "-map", "[oa]", "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-c:a", "aac", "-b:a", "192k",
                        "-movflags", "+faststart", str(out)], capture_output=True, text=True)
    if r.returncode:
        print("[aviso] capa no vídeo:", r.stderr[-300:]); return None
    return out


if __name__ == "__main__":
    for a in sys.argv[1:]:
        print(a, "->", fazer(Path(a)))
