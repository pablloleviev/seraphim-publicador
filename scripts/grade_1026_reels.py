"""Reels da grade 26/10–01/11 (SEG, QUI, SÁB): roteiro em cenas -> som desenhado (numpy) -> render Remotion "SinalVivo".
Uso: python scripts/grade_1026_reels.py [seg qui sab] [--quadros]   (--quadros: só 6 quadros de teste por vídeo)
"""
import json, os, subprocess, sys, wave
from pathlib import Path
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
MOTOR = RAIZ / "motor"
SAIDA = RAIZ / "previas" / "grade-2026-10-26"
FPS, SR = 30, 44100
INK, AZUL, ACIDO, LAV, MARFIM = "#0B0D12", "#2F6BFF", "#C7FF3D", "#B8A6FF", "#F5F0E6"
CHROME = os.environ.get("CHROME_PATH") or "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell"


def decrescente(total, a=14, b=4):
    d, s = [], 0
    while s < total:
        x = max(b, round(a - len(d) * 0.9)); x = min(x, total - s); d.append(x); s += x
    return d

REELS = {
 "seg": dict(pasta="2026-10-26_seg_reel", titulo="A oficina fecha", dur=25.0, cenas=[
   dict(capa_em=2.4, inicio=0, fim=3.6, tipo="foto", img="af/cena-07.png", cam="desacelera", texto="A oficina fechou.", y=1130, tam=100, atraso=16, pos="50% 55%", brilho=.85),
   dict(inicio=3.6, fim=6.4, tipo="colagem", itens=[dict(k=k, d=d) for k, d in zip(["notifs", "agenda", "papel", "notifs", "agenda", "papel", "notifs", "agenda", "papel", "notifs", "agenda", "notifs", "papel"], decrescente(84, 12, 4))],
        som=dict(pings=[4.0, 4.5, 5.0, 5.6])),
   dict(inicio=6.4, fim=9.4, tipo="texto", linhas=[dict(t="Mas a operação ainda está *aberta* na sua cabeça.", y=760, tam=100, atraso=22, entre=5, acento=ACIDO)], som=dict(mudo=(6.4, 7.2), hit=7.2)),
   dict(inicio=9.4, fim=11.8, tipo="foto", img="af/n-cliente-relogio.png", cam="deriva-esq", texto="Cliente aguardando resposta.", y=1200, tam=76, atraso=8, pos="50% 40%"),
   dict(inicio=11.8, fim=14.2, tipo="foto", img="af/cena-05.png", cam="sobe", texto="O histórico que precisa ser encontrado.", y=1200, tam=76, atraso=8),
   dict(inicio=14.2, fim=16.6, tipo="foto", img="af/n-mural.png", cam="deriva-dir", texto="A rotina de amanhã, sendo lembrada.", y=1200, tam=76, atraso=8),
   dict(inicio=16.6, fim=21.6, tipo="notebook", tela="gv/tela.png", texto="Gestão boa começa quando a rotina deixa de morar só na *memória.*", y=290, tam=70, atraso=12, som=dict(pad=True)),
   dict(inicio=21.6, fim=25.0, tipo="fecho", texto="Conheça o *AutoFlow.*", y=980, tam=84, som=dict(hit=21.6, pad=True)),
 ]),
 "qui": dict(pasta="2026-10-29_qui_reel", titulo="Mais uma aba aberta", dur=19.6, cenas=[
   dict(capa_em=1.7, inicio=0, fim=2.6, tipo="texto", linhas=[dict(t="Quantas *abas abertas* a sua operação exige?", y=740, tam=100, atraso=6, entre=4)], som=dict(abrir=True)),
   dict(inicio=2.6, fim=6.6, tipo="colagem", itens=[dict(k=k, d=d) for k, d in zip((["caderno", "planilha", "celular-desfoque", "postits", "notifs"] * 8), decrescente(120, 14, 4))], som=dict(rapido=True)),
   dict(inicio=6.6, fim=9.8, tipo="janelas", alinhaEm=58, som=dict(alinha=6.6 + 58 / 30)),
   dict(inicio=9.8, fim=12.8, tipo="notebook", tela="gv/tela.png", som=dict(silencio_total=True)),
   dict(inicio=12.8, fim=15.4, tipo="texto", fundo=MARFIM, brilho="rgba(47,107,255,.0)", linhas=[dict(t="A pergunta não é “qual *ferramenta* falta?”", y=760, tam=96, atraso=4, entre=4, acento=AZUL)]),
   dict(inicio=15.4, fim=19.6, tipo="fecho", texto="É “o que precisa parar de *ficar espalhado*?”", y=980, tam=66, som=dict(hit=15.4, pad=True)),
 ]),
 "sab": dict(pasta="2026-10-31_sab_reel", titulo="O verdadeiro terror da operação", dur=14.0, cenas=[
   dict(capa_em=1.7, inicio=0, fim=2.4, tipo="texto", linhas=[dict(t="O verdadeiro *terror* da operação?", y=760, tam=108, atraso=4, entre=4)], brilho="rgba(199,255,61,.10)", som=dict(seco=True)),
   dict(inicio=2.4, fim=5.1, tipo="flashes", itens=[dict(k="papel", d=24), dict(k="mensagem", d=27), dict(k="celular-desfoque", d=30)], som=dict(flashes=[2.4, 3.2, 4.1])),
   dict(inicio=5.1, fim=7.3, tipo="texto", linhas=[dict(t="Descobrir *tarde demais.*", y=760, tam=112, atraso=16, entre=6)], regua=1030, som=dict(mudo=(5.1, 5.6), hit=5.6)),
   dict(inicio=7.3, fim=10.8, tipo="texto", fundo=ACIDO, virada=9, linhas=[dict(t="Clareza não assusta. Ela evita *surpresa.*", y=760, tam=96, atraso=20, entre=5, acento=ACIDO)], som=dict(virada=7.3 + 9 / 30)),
   dict(inicio=10.8, fim=14.0, tipo="fecho", texto="Gestão mais simples para *oficinas.*", y=980, tam=74, som=dict(hit=10.8, pad=True)),
 ]),
}

# ---------------- som ----------------
def env(n, a, r):
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / max(r, 1e-4))

def tick(vol=.5, f0=2100):
    n = int(.05 * SR); t = np.arange(n) / SR
    return vol * (np.sin(2 * np.pi * f0 * t) * np.exp(-t * 120) * .7 + np.random.randn(n) * np.exp(-t * 400) * .5)

def hit(vol=.9):
    n = int(.9 * SR); t = np.arange(n) / SR
    return vol * (np.sin(2 * np.pi * (52 + 40 * np.exp(-t * 14)) * t) * np.exp(-t * 4.5) + np.random.randn(n) * np.exp(-t * 30) * .25)

def whoosh(dur=.5, vol=.35, sobe=True):
    n = int(dur * SR); x = np.random.randn(n); y = np.zeros(n); a = 0.0
    for i in range(n):
        p = i / n; c = (0.02 + 0.5 * (p if sobe else 1 - p) ** 2)
        a += c * (x[i] - a); y[i] = a
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
    return vol * y / (np.abs(y).max() + 1e-9) * e

def ping(f=1320, vol=.22):
    n = int(.5 * SR); t = np.arange(n) / SR
    return vol * (np.sin(2 * np.pi * f * t) + .35 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 9)

def pad(dur, vol=.12):
    n = int(dur * SR); t = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate([146.8, 185.0, 220.0, 293.7]))
    e = np.minimum(t / .6, 1) * np.minimum((dur - t) / .8, 1)
    return vol * y / 4 * e

def drone(dur, vol=.07):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * 55 * t) + .5 * np.sin(2 * np.pi * 110.4 * t + 1) + .25 * np.sin(2 * np.pi * 164.8 * t)
    return vol * y * (0.75 + 0.25 * np.sin(2 * np.pi * .18 * t))

def paper(vol=.25):
    n = int(.35 * SR); x = np.random.randn(n); y = np.convolve(x, np.ones(6) / 6, "same")
    return vol * y * np.sin(np.pi * np.linspace(0, 1, n)) ** 2

def somar(buf, x, t):
    i = int(t * SR)
    if i < 0 or i >= len(buf): return
    j = min(len(buf), i + len(x)); buf[i:j] += x[: j - i]

def palavras_t(c):
    ts = []
    if c["tipo"] == "texto":
        for l in c["linhas"]:
            n = len(l["t"].replace("*", "").split()); a = l.get("atraso", 0); e = l.get("entre", 4)
            ts += [c["inicio"] + (a + i * e) / FPS for i in range(n)]
    elif c["tipo"] in ("foto", "fecho", "notebook") and c.get("texto"):
        n = len(c["texto"].replace("*", "").split()); a = c.get("atraso", 14 if c["tipo"] == "fecho" else 6); e = 3
        ts = [c["inicio"] + (a + i * e) / FPS for i in range(n)]
    return ts

def som(spec, destino):
    np.random.seed(7)
    n = int(spec["dur"] * SR); L = np.zeros(n); R = np.zeros(n)
    buf = np.zeros(n)
    somar(buf, drone(spec["dur"]), 0)
    mudas = []
    for c in spec["cenas"]:
        s = c.get("som", {})
        if "mudo" in s: mudas.append(s["mudo"])
        if s.get("silencio_total"): mudas.append((c["inicio"], c["fim"]))
        if c["tipo"] in ("texto", "foto", "fecho", "notebook"):
            for t in palavras_t(c): somar(buf, tick(.32), t)
        if c["inicio"] > 0 and not s.get("silencio_total"):
            somar(buf, whoosh(.45, .30), c["inicio"] - .08)
        if "hit" in s: somar(buf, hit(.85), s["hit"])
        if s.get("pad"): somar(buf, pad(c["fim"] - c["inicio"] + .4), c["inicio"])
        for p in s.get("pings", []): somar(buf, ping(1320 + 90 * (int(p * 10) % 3)), p)
        if s.get("rapido") or c["tipo"] == "colagem":
            acc = c["inicio"]
            for it in c["itens"]:
                somar(buf, tick(.38, 1500 + 700 * ((int(acc * 30)) % 3)), acc); somar(buf, paper(.12), acc); acc += it["d"] / FPS
        if "flashes" in s:
            for t in s["flashes"]: somar(buf, hit(.5), t); somar(buf, tick(.6, 900), t)
        if "alinha" in s:
            somar(buf, hit(.55), s["alinha"]); somar(buf, ping(880, .18), s["alinha"] + .03)
            for k in range(8): somar(buf, tick(.25, 1200 + 90 * k), c["inicio"] + .1 + k * .1)
        if s.get("seco"): somar(buf, hit(.7), c["inicio"] + .12)
        if "virada" in s: somar(buf, whoosh(.35, .5, True), s["virada"] - .1); somar(buf, hit(.7), s["virada"] + .1)
    # silêncios: derruba tudo (com rampa curta) nas janelas "mudo"
    g = np.ones(n)
    for a, b in mudas:
        ia, ib = int(a * SR), int(b * SR); g[ia:ib] = 0
        r = int(.04 * SR); g[max(0, ia - r):ia] = np.linspace(1, 0, ia - max(0, ia - r)); g[ib:ib + r] = np.linspace(0, 1, len(g[ib:ib + r]))
    buf *= g
    buf = np.tanh(buf * 1.3) * .85
    # leve largura estéreo
    d = int(.012 * SR)
    L[:] = buf; R[d:] = buf[:-d]; R[:d] = 0; R = R * .9 + buf * .1
    st = np.stack([L, R], 1)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destino), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(st, -1, 1) * 32767).astype("<i2").tobytes())

# ---------------- render ----------------
def montar(nome, so_quadros=False):
    spec = REELS[nome]
    (MOTOR / "public/gv").mkdir(exist_ok=True)
    wav = MOTOR / f"public/gv/audio_{nome}.wav"
    som(spec, wav)
    props = {"fps": FPS, "duracao": spec["dur"], "arroba": "@seraphimbr_", "audio": f"gv/audio_{nome}.wav", "cenas": spec["cenas"]}
    pj = MOTOR / f"public/gv/props_{nome}.json"
    pj.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
    pasta = SAIDA / spec["pasta"]; pasta.mkdir(parents=True, exist_ok=True)
    base = f'npx remotion {{}} src/index.ts SinalVivo {{}} --props=public/gv/props_{nome}.json --log=error --browser-executable="{CHROME}" --chrome-mode=headless-shell'
    if so_quadros:
        tmp = SAIDA / "_trabalho" / f"quadros_{nome}"; tmp.mkdir(parents=True, exist_ok=True)
        for c in spec["cenas"]:
            fr = int(((c["inicio"] + c["fim"]) / 2) * FPS) if c["tipo"] not in ("fecho",) else int((c["fim"] - .5) * FPS)
            subprocess.run(base.format("still", f'"{tmp}/q_{int(c["inicio"]*10):03d}.png"') + f" --frame={fr}", cwd=MOTOR, shell=True, check=True)
        return tmp
    bruto = pasta / "_bruto.mp4"
    subprocess.run(base.format("render", f'"{bruto}"') + " --codec=h264 --crf=18 --jpeg-quality=100 --x264-preset=slow --pixel-format=yuv420p --audio-bitrate=192k", cwd=MOTOR, shell=True, check=True)
    sys.path.insert(0, str(Path(__file__).parent))
    import shutil
    try:
        import entrega
        shutil.copy(bruto, pasta / "video.mp4"); entrega.finalizar(pasta / "video.mp4")
    except Exception as e:
        print("[aviso] acabamento:", e); shutil.copy(bruto, pasta / "video.mp4")
    bruto.unlink()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(spec["cenas"][0].get("capa_em", .9)), "-i", str(pasta / "video.mp4"), "-frames:v", "1", "-q:v", "2", str(pasta / "capa.jpg")], check=True)
    return pasta

if __name__ == "__main__":
    nomes = [a for a in sys.argv[1:] if a in REELS] or list(REELS)
    for n in nomes:
        print("->", n, montar(n, "--quadros" in sys.argv))
