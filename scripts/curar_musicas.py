"""
Curadoria automática da biblioteca de trilhas (roda no GitHub Actions).

Baixa todas as candidatas de musica/candidatas.json (Pixabay, uso comercial grátis), mede a qualidade
de cada uma e fica só com as melhores por clima:
  - qualidade do arquivo: taxa de bits e "brilho" (até onde vão os agudos; faixa abafada = descartada)
  - volume percebido (LUFS) para nivelar as músicas entre si na montagem
  - mapa de energia: pico, drop (salto de calmo para forte), "corpo" (primeiro trecho já cheio)
Guarda o arquivo ORIGINAL (só corta em 150 s, sem recomprimir) em musica/<clima>/NN.mp3
e o relatório em musica/indice.json + musica/curadoria.txt.
"""
import json, re, shutil, subprocess, urllib.request
from pathlib import Path
import numpy as np

R = Path(__file__).resolve().parent.parent / "musica"
C = json.loads((R / "candidatas.json").read_text())
QUANTAS = {"hook": 6}
PADRAO = 8
TMP = R / "_cand"
TMP.mkdir(exist_ok=True)


def baixar(rel):
    dest = TMP / rel.replace("/", "_")
    if not dest.exists():
        req = urllib.request.Request(C["base"] + rel, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://pixabay.com/"})
        dest.write_bytes(urllib.request.urlopen(req, timeout=120).read())
    return dest


def pcm(f, sr, ini=0, dur=None, mono=True):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ini)] + (["-t", str(dur)] if dur else []) + ["-i", str(f)]
    cmd += ["-ac", "1" if mono else "2", "-ar", str(sr), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32)


def lufs(f, ini=0, dur=None):
    cmd = ["ffmpeg", "-hide_banner", "-ss", str(ini)] + (["-t", str(dur)] if dur else []) + ["-i", str(f),
           "-af", "loudnorm=print_format=json", "-f", "null", "-"]
    err = subprocess.run(cmd, capture_output=True, text=True).stderr
    m = re.search(r'"input_i"\s*:\s*"(-?[\d.]+|-inf)"', err)
    return float(m.group(1)) if m and m.group(1) != "-inf" else -70.0


def analisar(f):
    br = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=bit_rate,duration", "-of", "json", str(f)],
                        capture_output=True, text=True)
    fmt = json.loads(br.stdout).get("format", {})
    dur = float(fmt.get("duration", 0)); kbps = int(float(fmt.get("bit_rate", 0)) / 1000)
    a = pcm(f, 8000)
    win = 4000
    rms = np.array([np.sqrt(np.mean(a[j:j + win] ** 2)) for j in range(0, len(a) - win, win)])
    if len(rms) < 20:
        return None
    rmsn = rms / (rms.max() + 1e-9)
    sm = np.convolve(rmsn, np.ones(8) / 8, mode="same")
    lim = max(1, len(sm) - 16)
    pico = int(np.argmax(sm[:lim]))
    salto = np.array([sm[min(len(sm) - 1, j + 4)] - sm[j] for j in range(len(sm))])
    drop = int(np.argmax(salto[:lim])) + 4
    calmo = int(np.argmin(sm[:max(1, len(sm) - 20)]))
    cheio = np.where(sm[:lim] >= 0.6 * sm.max())[0]
    corpo = int(cheio[0]) if len(cheio) else pico
    # brilho: espectro médio de 20 s a partir do trecho cheio
    x = pcm(f, 44100, ini=corpo * 0.5, dur=20)
    n = 4096
    if len(x) < n * 4:
        return None
    frames = np.stack([x[i:i + n] * np.hanning(n) for i in range(0, len(x) - n, n // 2)])
    esp = (np.abs(np.fft.rfft(frames, axis=1)) ** 2).mean(axis=0)
    fr = np.fft.rfftfreq(n, 1 / 44100)
    db = 10 * np.log10(esp / esp.max() + 1e-14)
    corte = float(fr[np.where(db > -75)[0].max()])
    agudos = float(10 * np.log10(esp[fr > 8000].sum() / esp.sum() + 1e-14))   # energia acima de 8 kHz (dB)
    return {"dur": round(dur, 1), "kbps": kbps, "corte": int(corte), "agudos": round(agudos, 1),
            "lufs": round(lufs(f, corpo * 0.5, 30), 1), "pico": pico * 0.5, "drop": drop * 0.5, "calmo": calmo * 0.5,
            "corpo": corpo * 0.5, "energia_media": round(float(rmsn.mean()), 3)}


def nota(info, clima):
    """Quanto maior melhor. Abafada/comprimida demais perde muito."""
    s = 0.0
    s += min(info["corte"], 17000) / 1000            # brilho (até 17)
    s += min(info["kbps"], 256) / 64                 # taxa de bits (até 4)
    s += max(-12, min(0, info["agudos"] + 25)) / 3   # pouca energia nos agudos = som "fechado"
    if info["corte"] < 12000 and clima != "hook":
        s -= 10
    return round(s, 2)


relatorio, indice, usadas = [], {}, set()
for clima, lista in C["candidatas"].items():
    avaliadas = []
    for ordem, rel in enumerate(lista):
        if rel in usadas:
            continue
        try:
            f = baixar(rel); info = analisar(f)
        except Exception as e:
            relatorio.append(f"{clima} {rel} falhou: {e}"); continue
        if not info:
            continue
        info["fonte"] = rel
        info["nota"] = nota(info, clima) - ordem * 0.08          # popularidade desempata
        avaliadas.append((info["nota"], rel, f, info))
        relatorio.append(f"{clima} {rel} nota={info['nota']:.2f} corte={info['corte']} kbps={info['kbps']} agudos={info['agudos']} lufs={info['lufs']}")
    avaliadas.sort(key=lambda x: -x[0])
    escolhidas = avaliadas[:QUANTAS.get(clima, PADRAO)]
    pasta = R / clima
    if escolhidas:
        shutil.rmtree(pasta, ignore_errors=True); pasta.mkdir()
    for i, (_, rel, f, info) in enumerate(escolhidas, 1):
        dest = pasta / f"{i:02d}.mp3"
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(f), "-t", "150", "-map", "0:a", "-c:a", "copy", str(dest)])
        if r.returncode != 0:
            shutil.copy(f, dest)
        usadas.add(rel)
        indice[f"{clima}/{i:02d}"] = info
    relatorio.append(f"== {clima}: escolhidas " + ", ".join(e[1] for e in escolhidas))

(R / "indice.json").write_text(json.dumps(indice, indent=1))
(R / "curadoria.txt").write_text("\n".join(relatorio))
shutil.rmtree(TMP, ignore_errors=True)
print("\n".join(relatorio))
