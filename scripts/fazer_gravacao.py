"""
Gravação do Pabllo -> vídeo cinematográfico pronto, com legenda e edição da marca.

Pedido em gravacoes/<nome>.json:
{
  "video": "gravacoes/meu-video.mp4",        (o arquivo gravado no celular)
  "cenario": "cenarios/oficina-noite.jpg",    (imagem do cenário)
  "estilo": "dourado",
  "titulo": ["SUA OFICINA", "ESTÁ *PERDENDO*", "*DINHEIRO?*"],   (opcional, no topo)
  "insercoes": [                               (opcional: telas gráficas por cima, em segundos)
     {"inicio": 6.0, "fim": 8.5, "modelo": "numero", "numero": "01", "linhas": ["COBRA NO", "*ACHÔMETRO*"]}
  ],
  "quando": "2026-10-12 18:00",                (opcional; senão vai para aprovação na hora)
  "legenda": "texto do post"
}
"""
import json, shutil, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MOTOR = RAIZ / "motor"; JOB = MOTOR / "public" / "job"
BRT = timezone(timedelta(hours=-3))
sys.path.insert(0, str(RAIZ / "scripts"))


def transcrever(audio):
    import numpy as np
    from faster_whisper import WhisperModel
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(audio), "-f", "s16le", "-ac", "1", "-ar", "16000", "-"],
                         capture_output=True, check=True).stdout
    onda = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe(onda, language="pt", word_timestamps=True)
    return [{"w": w.word.strip(), "s": w.start, "e": w.end} for s in segs for w in s.words if w.word.strip()]


def duracao(v):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(v)],
                                capture_output=True, text=True).stdout.strip())


def processar(pedido: Path):
    spec = json.loads(pedido.read_text(encoding="utf-8"))
    nome = spec.get("nome", pedido.stem)
    bruto = RAIZ / spec["video"]
    shutil.rmtree(JOB, ignore_errors=True); JOB.mkdir(parents=True)
    tratado = JOB / "gravacao.mp4"
    print("1/3 tratamento cinematográfico...", flush=True)
    subprocess.run([sys.executable, str(RAIZ / "scripts" / "cinema.py"), str(bruto), str(RAIZ / spec["cenario"]),
                    str(tratado), "--estilo", spec.get("estilo", "dourado")], check=True)
    dur = duracao(tratado)
    palavras = transcrever(tratado)
    cenas = []
    ins = sorted(spec.get("insercoes", []), key=lambda c: c["inicio"])
    t = 0.0
    for i, c in enumerate(ins):
        if c["inicio"] > t:
            cenas.append({"inicio": t, "fim": c["inicio"], "modelo": "gravacao"})
        cenas.append(c); t = c["fim"]
    if t < dur:
        cenas.append({"inicio": t, "fim": dur, "modelo": "gravacao"})
    if spec.get("titulo") and cenas and cenas[0]["modelo"] == "gravacao":
        cenas[0]["linhas"] = spec["titulo"]
    props = {"fps": 30, "duracao": dur, "arroba": spec.get("arroba", "@seraphimtech_"), "audio": None,
             "video": "job/gravacao.mp4", "batida": "sfx/batida.mp3", "sfx": bool(ins), "palavras": palavras, "cenas": cenas}
    (JOB / "props.json").write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")

    amostra = spec.get("amostra", False)
    quando = datetime.strptime(spec["quando"], "%Y-%m-%d %H:%M") if spec.get("quando") else datetime.now(BRT).replace(tzinfo=None)
    destino = (RAIZ / "amostras" / nome) if amostra else RAIZ / "fila" / f"{quando:%Y-%m-%d_%H%M}_{nome}"
    destino.mkdir(parents=True, exist_ok=True)
    subprocess.run(f'npx remotion render src/index.ts Seraphim "{destino / "video.mp4"}" --props=public/job/props.json '
                   f'--log=error --codec=h264 --crf=14 --jpeg-quality=95 --pixel-format=yuv420p --audio-bitrate=192k',
                   cwd=MOTOR, shell=True, check=True)
    if not amostra:
        (destino / "item.json").write_text(json.dumps({"tipo": "reels", "legenda": spec.get("legenda", ""),
            "quando": quando.strftime("%Y-%m-%dT%H:%M:00-03:00")}, ensure_ascii=False, indent=2), encoding="utf-8")
    pedido.unlink()
    if bruto.exists(): bruto.unlink()   # o bruto pesa; não precisa ficar no repositório
    print(f"Pronto: {destino}")


if __name__ == "__main__":
    for p in sorted((RAIZ / "gravacoes").glob("*.json")):
        try:
            processar(p)
        except Exception:
            import traceback; traceback.print_exc()
