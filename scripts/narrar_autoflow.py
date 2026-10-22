"""Põe a narração (voz_saida/<pedido>/linha-NN.mp3) por cima do vídeo já renderizado do AutoFlow.

Não re-renderiza: refaz só o áudio (trilha com ducking + narração, loudnorm -14 LUFS / TP -1.5)
e remuxa com o vídeo original (-c:v copy). Uso:
    python scripts/narrar_autoflow.py V12 V13          -> previas/autoflow/<...>_NARRADO.mp4
"""
import json, subprocess, sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
SR = 48000

# (pedido, vídeo de origem, trilha, saída, [(nº da linha, segundo em que começa)])
VIDEOS = {
 "V12": dict(pedido="af-v12-caderno-masculina", video="previas/autoflow/AutoFlow_V2_Do_Caderno_Ao_Sistema_FINAL.mp4",
             trilha="motor/public/af/trilha_v2.wav", saida="previas/autoflow/AutoFlow_V12_Do_Caderno_Ao_Sistema_NARRADO.mp4",
             marcas=[(1, 0.6), (2, 5.7), (3, 15.3), (4, 20.2), (5, 26.4), (6, 31.8), (7, 37.1)]),
 "V13": dict(pedido="af-v13-dia-feminina", video="previas/autoflow/AutoFlow_V3_Um_Dia_Na_Oficina_FINAL.mp4",
             trilha="motor/public/af/trilha_v3.wav", saida="previas/autoflow/AutoFlow_V13_Um_Dia_Na_Oficina_NARRADO.mp4",
             marcas=[(1, 0.7), (2, 5.4), (3, 10.5), (4, 15.4), (5, 20.5), (6, 25.4), (7, 31.4), (8, 35.6), (9, 40.7)]),
}
VOZ = 1.0        # nível da narração
MUSICA = 0.92    # nível da trilha fora da fala
DUCK = 0.58      # quanto a trilha abaixa enquanto a voz fala


def ler(caminho: Path, canais: int) -> np.ndarray:
    """Decodifica qualquer áudio para float32 [amostras, canais] a 48 kHz."""
    crua = subprocess.run(["ffmpeg", "-v", "error", "-i", str(caminho), "-f", "f32le", "-ar", str(SR),
                           "-ac", str(canais), "-"], check=True, capture_output=True).stdout
    return np.frombuffer(crua, dtype=np.float32).reshape(-1, canais).copy()


def envelope(x: np.ndarray, ataque=0.06, saida=0.45) -> np.ndarray:
    """Presença da voz (0 a 1), com ataque rápido e saída lenta — para o ducking não 'bombear'."""
    nivel = np.abs(x).max(axis=1)
    janela = int(SR * 0.02)
    nivel = np.convolve(nivel, np.ones(janela) / janela, mode="same")
    nivel = (nivel > 0.004).astype(np.float32)
    ka, ks = np.exp(-1 / (SR * ataque)), np.exp(-1 / (SR * saida))
    fora = np.empty_like(nivel); v = 0.0
    for i, alvo in enumerate(nivel):
        k = ka if alvo > v else ks
        v = alvo + k * (v - alvo)
        fora[i] = v
    return fora


def montar(cfg: dict) -> Path:
    # a cama é o próprio áudio do vídeo já aprovado (trilha + efeitos), para não mudar nada além da voz
    trilha = ler(RAIZ / cfg["video"], 2)
    total = len(trilha)
    narr = np.zeros((total, 2), dtype=np.float32)
    voz_dir = RAIZ / "voz_saida" / cfg["pedido"]
    fim_anterior = 0.0
    for n, quando in cfg["marcas"]:
        mp3 = voz_dir / f"linha-{n:02d}.mp3"
        if not mp3.exists():
            raise SystemExit(f"falta {mp3}")
        linha = ler(mp3, 2)
        inicio = int(max(quando, fim_anterior + 0.12) * SR)
        corte = min(len(linha), total - inicio)
        if corte <= 0:
            raise SystemExit(f"linha {n} começa depois do fim do vídeo")
        if corte < len(linha):
            print(f"  [aviso] linha {n} cortada em {corte / SR:.1f}s (passava do fim)")
        narr[inicio:inicio + corte] += linha[:corte] * VOZ
        fim_anterior = (inicio + corte) / SR
        print(f"  linha {n}: {inicio / SR:5.1f}s -> {fim_anterior:5.1f}s")
    ganho = (1 - DUCK * envelope(narr))[:, None]
    mistura = trilha * ganho * MUSICA + narr
    pico = np.abs(mistura).max()
    if pico > 0.99:
        mistura *= 0.99 / pico
    wav = RAIZ / f"_narr_{cfg['pedido']}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_s16le", str(wav)], input=mistura.astype(np.float32).tobytes(), check=True)
    return wav


def medir(wav: Path) -> dict:
    p = subprocess.run(["ffmpeg", "-v", "info", "-i", str(wav), "-af",
                        "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    bruto = p.stderr[p.stderr.rindex("{"):]
    return json.loads(bruto[:bruto.index("}") + 1])


def fazer(chave: str):
    cfg = VIDEOS[chave]
    print(chave)
    wav = montar(cfg)
    m = medir(wav)
    filtro = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    saida = RAIZ / cfg["saida"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(RAIZ / cfg["video"]), "-i", str(wav),
                    "-map", "0:v:0", "-c:v", "copy", "-map", "1:a:0", "-af", filtro,
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(saida)], check=True)
    wav.unlink()
    print("  pronto:", saida.relative_to(RAIZ))


if __name__ == "__main__":
    for chave in (sys.argv[1:] or list(VIDEOS)):
        fazer(chave)
