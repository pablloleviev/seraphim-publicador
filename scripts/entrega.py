"""
Acabamento final do vídeo para as redes (TikTok/Instagram recomprimem tudo; aqui entregamos no formato
que elas preservam melhor):
  - cores no padrão de vídeo (BT.709, faixa limitada). O Remotion sai em faixa "cheia" + BT.601, que as redes
    convertem errado (fica lavado/escuro e com blocos nos degradês)
  - H.264 High 4.2, 30 fps, keyframe a cada 2 s, bitrate alto (as redes cortam menos quando a fonte é limpa)
  - AAC 48 kHz 256k, moov no início (faststart)
    python scripts/entrega.py fila/*/video.mp4
"""
import shutil, subprocess, sys
from pathlib import Path


def finalizar(video: Path):
    video = Path(video)
    tmp = video.with_name(video.stem + ".final.mp4")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(video),
           "-vf", "scale=in_color_matrix=bt601:out_color_matrix=bt709:in_range=full:out_range=tv:flags=lanczos+accurate_rnd+full_chroma_int,format=yuv420p",
           "-c:v", "libx264", "-profile:v", "high", "-level", "4.2", "-preset", "slow", "-crf", "16",
           "-maxrate", "16M", "-bufsize", "32M", "-r", "30", "-g", "60", "-tune", "animation",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
           "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-movflags", "+faststart", str(tmp)]
    subprocess.run(cmd, check=True)
    shutil.move(str(tmp), str(video))


if __name__ == "__main__":
    for v in sys.argv[1:]:
        finalizar(Path(v)); print("ok:", v)
