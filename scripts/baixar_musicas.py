"""Baixa a biblioteca de trilhas (Pixabay) e analisa a energia de cada faixa (para achar o "drop" e as partes calmas)."""
import json, subprocess, urllib.request
from pathlib import Path
import numpy as np

R = Path(__file__).resolve().parent.parent / "musica"
F = json.loads((R / "fontes.json").read_text())
indice = {}
for clima, lista in F["faixas"].items():
    (R / clima).mkdir(exist_ok=True)
    for i, rel in enumerate(lista, 1):
        dest = R / clima / f"{i:02d}.mp3"
        if not dest.exists():
            tmp = dest.with_suffix(".orig.mp3")
            req = urllib.request.Request(F["base"] + rel, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://pixabay.com/"})
            try:
                tmp.write_bytes(urllib.request.urlopen(req, timeout=120).read())
            except Exception as e:
                print("falhou", clima, i, e); continue
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-t", "150", "-ac", "2", "-ar", "44100", "-b:a", "128k", str(dest)], check=True)
            tmp.unlink()
        pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(dest), "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout
        a = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
        win = 4000  # 0,5 s
        rms = np.array([np.sqrt(np.mean(a[j:j + win] ** 2)) for j in range(0, len(a) - win, win)])
        if not len(rms):
            continue
        rmsn = (rms / (rms.max() + 1e-9)).round(3)
        sm = np.convolve(rmsn, np.ones(8) / 8, mode="same")  # média de 4 s
        pico = int(np.argmax(sm[:max(1, len(sm) - 16)]))
        # "drop": maior salto de energia (de calmo para forte)
        salto = np.array([sm[min(len(sm) - 1, j + 4)] - sm[j] for j in range(len(sm))])
        drop = int(np.argmax(salto[:max(1, len(salto) - 16)])) + 4
        calmo = int(np.argmin(sm[:max(1, len(sm) - 20)]))
        indice[f"{clima}/{i:02d}"] = {"dur": round(len(a) / 8000, 1), "pico": pico * 0.5, "drop": drop * 0.5, "calmo": calmo * 0.5,
                                      "energia_media": round(float(rmsn.mean()), 3)}
        print(clima, i, indice[f"{clima}/{i:02d}"])
(R / "indice.json").write_text(json.dumps(indice, indent=1))
