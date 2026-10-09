"""
Transforma uma gravação simples de celular em um plano cinematográfico.

    python scripts/cinema.py entrada.mp4 cenario.jpg saida.mp4 [--estilo dourado]

Etapas (tudo grátis, roda em CPU):
 1. Recorte da pessoa fio a fio (RobustVideoMatting)
 2. Cenário com profundidade: desfoque de lente + leve movimento de câmera (push-in)
 3. Integração: cor da pessoa puxada para a luz do cenário + "light wrap" nas bordas
 4. Acabamento: curva de contraste, gradação dourada da marca, vinheta, granulação de filme
O áudio original é mantido.
"""
import argparse, json, subprocess, sys
from pathlib import Path

import cv2
import numpy as np
import torch

W, H = 1080, 1920


def info(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height,r_frame_rate,nb_frames:format=duration", "-of", "json", video],
                         capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    s = d["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    fps = float(num) / float(den)
    return fps, float(d["format"]["duration"])


def cobrir(img, w, h, escala=1.0):
    ih, iw = img.shape[:2]
    k = max(w / iw, h / ih) * escala
    nw, nh = int(iw * k + 0.5), int(ih * k + 0.5)
    r = cv2.resize(img, (nw, nh), interpolation=cv2.INTER_AREA if k < 1 else cv2.INTER_CUBIC)
    x, y = (nw - w) // 2, (nh - h) // 2
    return r[y:y + h, x:x + w]


def curva_s(x, forca=0.18):
    # contraste suave em S (x em 0..1)
    return np.clip(x + forca * (x - 0.5) * (1 - np.abs(2 * x - 1)) * 2, 0, 1)


ESTILOS = {
    # sombras frias/escuras, altas luzes douradas (marca Seraphim #F5A623)
    "dourado": dict(sombra=(0.02, 0.025, 0.04), luz=(1.0, 0.82, 0.55), satur=0.9, contraste=0.22),
    "neutro": dict(sombra=(0.0, 0.0, 0.0), luz=(1.0, 1.0, 1.0), satur=1.0, contraste=0.15),
}


def gradar(rgb, est, vinheta, grao_rng):
    x = curva_s(rgb, est["contraste"])
    lum = (x @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    x = lum + (x - lum) * est["satur"]                       # saturação
    sombra = np.array(est["sombra"], np.float32); luz = np.array(est["luz"], np.float32)
    peso = np.clip(lum, 0, 1)
    x = x * (1 - peso * (1 - luz) * 0.35) + sombra * (1 - peso)  # split-toning
    x = x * vinheta
    grao = grao_rng.normal(0, 0.018, x.shape[:2]).astype(np.float32)[..., None]
    return np.clip(x + grao, 0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada"); ap.add_argument("cenario"); ap.add_argument("saida")
    ap.add_argument("--estilo", default="dourado", choices=list(ESTILOS))
    ap.add_argument("--desfoque", type=float, default=7.0, help="desfoque de lente do fundo")
    ap.add_argument("--zoom", type=float, default=0.06, help="quanto a câmera avança no fundo")
    ap.add_argument("--escala-pessoa", type=float, default=1.0)
    a = ap.parse_args()
    est = ESTILOS[a.estilo]

    fps, dur = info(a.entrada)
    total = max(1, int(dur * fps))
    modelo = torch.hub.load("PeterL1n/RobustVideoMatting", "mobilenetv3", trust_repo=True).eval()
    torch.set_num_threads(max(1, torch.get_num_threads()))

    fundo_base = cv2.cvtColor(cv2.imread(a.cenario), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    fundo_base = cobrir(fundo_base, int(W * 1.2), int(H * 1.2))
    media_fundo = cv2.cvtColor(cobrir(fundo_base, W, H), cv2.COLOR_RGB2LAB).reshape(-1, 3).mean(0)

    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dist = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    vinheta = np.clip(1.08 - 0.42 * dist ** 1.8, 0.45, 1)[..., None].astype(np.float32)
    rng = np.random.default_rng(7)

    ler = subprocess.Popen(["ffmpeg", "-v", "error", "-i", a.entrada, "-vf",
                            f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    tmp = Path(a.saida).with_suffix(".sem_audio.mp4")
    gravar = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                               "-s", f"{W}x{H}", "-r", f"{fps}", "-i", "-", "-c:v", "libx264", "-crf", "16",
                               "-preset", "slow", "-pix_fmt", "yuv420p", str(tmp)], stdin=subprocess.PIPE)
    rec = [None] * 4
    n = 0
    with torch.no_grad():
        while True:
            buf = ler.stdout.read(W * H * 3)
            if len(buf) < W * H * 3:
                break
            frame = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.float32) / 255
            src = torch.from_numpy(frame).permute(2, 0, 1)[None]
            fgr, pha, *rec = modelo(src, *rec, downsample_ratio=0.25)
            alpha = pha[0, 0].numpy()[..., None]
            pessoa = fgr[0].permute(1, 2, 0).numpy()

            # fundo: push-in lento + desfoque de lente
            t = n / total
            k = 1.0 + a.zoom * t
            fw, fh = int(W * k), int(H * k)
            fb = cv2.resize(fundo_base, (int(W * 1.2), int(H * 1.2)))
            x0 = (fb.shape[1] - fw) // 2; y0 = (fb.shape[0] - fh) // 2
            fundo = cv2.resize(fb[y0:y0 + fh, x0:x0 + fw], (W, H), interpolation=cv2.INTER_AREA)
            if a.desfoque > 0:
                fundo = cv2.GaussianBlur(fundo, (0, 0), a.desfoque)

            # integração de cor: puxa a pessoa 35% para a luz média do cenário
            lab = cv2.cvtColor(np.clip(pessoa, 0, 1), cv2.COLOR_RGB2LAB)
            m = lab[alpha[..., 0] > 0.5].mean(0) if (alpha > 0.5).any() else lab.reshape(-1, 3).mean(0)
            lab[..., 1:] += (media_fundo[1:] - m[1:]) * 0.35
            lab[..., 0] += (media_fundo[0] - m[0]) * 0.15
            pessoa = np.clip(cv2.cvtColor(lab, cv2.COLOR_LAB2RGB), 0, 1)

            # light wrap: a luz do fundo "abraça" as bordas da pessoa
            borda = np.clip(cv2.GaussianBlur(alpha[..., 0], (0, 0), 12), 0, 1)[..., None]
            wrap = (1 - borda) * alpha * 0.55
            fundo_luz = cv2.GaussianBlur(fundo, (0, 0), 18)
            pessoa = pessoa * (1 - wrap) + np.maximum(pessoa, fundo_luz) * wrap

            comp = pessoa * alpha + fundo * (1 - alpha)
            final = gradar(comp, est, vinheta, rng)
            gravar.stdin.write((final * 255 + 0.5).astype(np.uint8).tobytes())
            n += 1
            if n % 60 == 0:
                print(f"  {n}/{total} quadros", flush=True)
    ler.wait(); gravar.stdin.close(); gravar.wait()

    # junta o áudio original
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-i", a.entrada, "-map", "0:v", "-map", "1:a?",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", a.saida], check=True)
    tmp.unlink()
    print(f"Pronto: {a.saida} ({n} quadros)")


if __name__ == "__main__":
    main()
