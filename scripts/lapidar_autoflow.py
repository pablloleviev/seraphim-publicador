"""Lapida os vídeos AutoFlow V2/V3: monta o som do zero (narração nova + trilha + efeitos sincronizados + música da marca)
e gera o JSON de props da composição Remotion (AFLapV2 / AFLapV3).
Uso: python scripts/lapidar_autoflow.py v2|v3 [pasta_de_trabalho]"""
import json, subprocess, sys, math
from pathlib import Path
import numpy as np
from scipy import signal

R = Path(__file__).resolve().parent.parent
SR = 44100
SFX = R / "motor/public/sfx"
MUS = R / "musica"
rng = np.random.default_rng(7)


# ---------------------------------------------------------------- utilidades de áudio
def ff_load(path, ss=0.0, t=None, af=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss)]
    if t: cmd += ["-t", str(t)]
    cmd += ["-i", str(path)]
    if af: cmd += ["-af", af]
    cmd += ["-f", "f32le", "-ac", "2", "-ar", str(SR), "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def mono2st(x):
    return np.stack([x, x], 1).astype(np.float32)


def env_fade(n, a=0.0, b=0.0):
    e = np.ones(n, np.float32)
    na, nb = int(a * SR), int(b * SR)
    if na: e[:na] = np.linspace(0, 1, na) ** 1.5
    if nb: e[-nb:] *= np.linspace(1, 0, nb) ** 1.5
    return e[:, None]


class Pista:
    def __init__(self, dur):
        self.n = int(dur * SR) + SR
        self.a = np.zeros((self.n, 2), np.float32)

    def put(self, x, t, g=1.0, pan=0.0):
        i = int(round(t * SR))
        if i < 0:
            x = x[-i:]; i = 0
        j = min(self.n, i + len(x))
        if j <= i: return
        gl = g * (1 - max(0, pan)); gr = g * (1 + min(0, pan))
        self.a[i:j, 0] += x[: j - i, 0] * gl
        self.a[i:j, 1] += x[: j - i, 1] * gr


def pitch(x, r):
    """muda velocidade+tom por reamostragem (r>1 = mais agudo e curto)."""
    n = int(len(x) / r)
    idx = np.linspace(0, len(x) - 1, n)
    return np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in range(2)], 1).astype(np.float32)


def lp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), "low"); return signal.lfilter(b, a, x, axis=0).astype(np.float32)


def hp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), "high"); return signal.lfilter(b, a, x, axis=0).astype(np.float32)


def bp(x, f1, f2, order=2):
    b, a = signal.butter(order, [f1 / (SR / 2), f2 / (SR / 2)], "band"); return signal.lfilter(b, a, x, axis=0).astype(np.float32)


# ---------------------------------------------------------------- sons sintetizados (do zero)
def noise(dur): return rng.standard_normal((int(dur * SR), 2)).astype(np.float32)


def boom(dur=2.2, f0=78, f1=34):
    t = np.arange(int(dur * SR)) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 5)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 1.9)
    thump = lp(noise(dur), 220)[:, 0] * np.exp(-t * 14) * 1.4
    click = hp(noise(0.05), 2000)[:, 0]; click = np.pad(click, (0, len(t) - len(click))) * np.exp(-t * 60) * 0.5
    x = (body + thump + click) * 0.9
    return mono2st(np.tanh(x * 1.3))


def riser(dur, g=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros(n, np.float32)
    for k in range(8):
        fc = 300 * (2 ** (4.9 * k / 7))
        band = bp(noise(dur), fc / 1.4, min(fc * 1.4, 18000))[:, 0]
        centro = (k / 7) * dur; larg = dur / 3.5
        x += band * np.exp(-((t - centro) / larg) ** 2)
    sweep = np.sin(2 * np.pi * np.cumsum(180 * (2 ** (3.2 * t / dur))) / SR) * 0.25
    amp = (t / dur) ** 2.0
    return mono2st((x * 0.9 + sweep) * amp * g * 0.55)


def step(g=1.0, pitch_=1.0):
    t = np.arange(int(0.22 * SR)) / SR
    th = np.sin(2 * np.pi * (90 * pitch_ - 40 * t * 4) * t) * np.exp(-t * 28)
    sc = lp(noise(0.22), 1800)[:, 0] * np.exp(-t * 38) * 0.9
    return mono2st((th + sc) * 0.9 * g)


def jingle(n=4, g=1.0):
    out = np.zeros((int(0.9 * SR), 2), np.float32)
    for k in range(n):
        t0 = int(k * rng.uniform(0.035, 0.07) * SR)
        for fr in rng.choice([2700, 3400, 4300, 5200, 6100, 7300], 3, replace=False):
            d = rng.uniform(0.10, 0.26); tt = np.arange(int(d * SR)) / SR
            s = np.sin(2 * np.pi * fr * tt) * np.exp(-tt * (22 / d / 6)) * rng.uniform(0.15, 0.3)
            out[t0:t0 + len(s)] += mono2st(s)[: len(out) - t0]
    return out * g


def buzz(g=1.0):
    t = np.arange(int(0.2 * SR)) / SR
    s = (np.sin(2 * np.pi * 168 * t) + 0.4 * np.sin(2 * np.pi * 336 * t)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 38 * t))) * np.hanning(len(t))
    return mono2st(s * 0.7 * g)


def rattle(dur, up=True, g=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    x = bp(noise(dur), 500, 3200)[:, 0]
    rate = (11 + 9 * t / dur) if up else (20 - 9 * t / dur)
    am = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * np.cumsum(rate) / SR))
    low = lp(noise(dur), 160)[:, 0] * 0.9
    env = np.hanning(n) ** 0.6
    return mono2st((x * am * 0.8 + low * 0.5) * env * g)


def engine(dur, g=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 46 + 12 * np.sin(2 * np.pi * 0.7 * t)
    ph = np.cumsum(2 * np.pi * f / SR)
    s = np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.25 * np.sin(3 * ph)
    s = s * (0.7 + 0.3 * np.sin(2 * np.pi * 23 * t)) + lp(noise(dur), 300)[:, 0] * 0.5
    return mono2st(s * np.hanning(n) ** 0.7 * 0.5 * g)


def ding(g=1.0):
    out = np.zeros((int(2.4 * SR), 2), np.float32); t = np.arange(len(out)) / SR
    for fr, a, d in [(1318.5, 1.0, 1.6), (1975.5, 0.55, 1.2), (2637, 0.35, 0.9), (3951, 0.18, 0.6)]:
        out += mono2st(np.sin(2 * np.pi * fr * t) * np.exp(-t / d * 3.2) * a * 0.35)
    return out * g


def room(dur, g=1.0):
    """ambiente de oficina bem baixo: rumor grave + fio de ar + compressor distante."""
    n = int(dur * SR); t = np.arange(n) / SR
    brown = np.cumsum(rng.standard_normal(n)); brown -= np.linspace(brown[0], brown[-1], n); brown /= np.abs(brown).max()
    low = lp(mono2st(brown), 220)
    air = bp(noise(dur), 900, 2400) * 0.05
    comp = mono2st(np.sin(2 * np.pi * 100 * t) * 0.03 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.11 * t)))
    return (low * 0.55 + air + comp) * g


def sfx_lib(name, r=1.0, g=1.0, trim=None):
    x = ff_load(SFX / name)
    if r != 1.0: x = pitch(x, r)
    return x * g


# ---------------------------------------------------------------- voz
def voz_linha(pasta, i, vel, lead_min=0.02):
    mp3 = pasta / f"linha-{i:02d}.mp3"
    af = (f"atempo={vel},highpass=f=85,equalizer=f=220:t=q:w=1:g=-1.5,equalizer=f=3200:t=q:w=1.2:g=3,"
          "equalizer=f=9500:t=h:w=1:g=1.5,acompressor=threshold=-19dB:ratio=3:attack=6:release=90:makeup=3")
    x = ff_load(mp3, af=af)
    mono = np.abs(x[:, 0]); k = np.argmax(mono > 0.03)
    lead = k / SR
    pal = json.load(open(pasta / f"linha-{i:02d}.json", encoding="utf-8"))
    # fim da fala (último ponto acima do limiar)
    acima = np.where(mono > 0.03)[0]; fim = (acima[-1] / SR) if len(acima) else len(x) / SR
    return x, lead, fim, pal


def duck_env(voz_arr, n, atk=0.03, rel=0.35, prof=0.62):
    e = np.abs(voz_arr[:n, 0]); win = int(0.05 * SR)
    e = np.convolve(e, np.ones(win) / win, "same")
    e = np.clip(e / 0.12, 0, 1)
    out = np.zeros_like(e); a = 1 - math.exp(-1 / (atk * SR)); r = 1 - math.exp(-1 / (rel * SR)); y = 0
    # suavização por blocos de 64 amostras (rápido)
    blk = 64
    for i in range(0, len(e), blk):
        v = e[i:i + blk].max()
        y += (v - y) * (a * blk if v > y else r * blk)
        y = min(max(y, 0), 1)
        out[i:i + blk] = y
    return (1 - prof * out)[:, None].astype(np.float32)


# ---------------------------------------------------------------- configuração por vídeo
def cfg_v2():
    K = 15.0 / 13.47

    def o(s): return s * K if s < 13.47 else s + (15.0 - 13.47)
    fim_out = o(29.6)
    cuts = [(3.4, 'whip', 1), (4.7, 'whip', -1), (5.9, 'flash', 1), (6.9, 'whip', 1), (8.5, 'zoom', 1), (9.67, 'whip', -1), (11.2, 'flash', 1),
            (13.47, 'luz', 1), (15.8, 'zoom', 1), (17.4, 'zoom', 1), (18.5, 'whip', -1), (20.4, 'flash', 1), (23.8, 'whip', 1), (25.6, 'whip', -1),
            (27.7, 'zoom', 1), (29.6, 'luz', 1)]
    kinds = ['foot', 'foot', 'foot', 'foot', 'card', 'foot', 'foot', 'ui', 'ui', 'ui', 'ui', 'ui', 'foot', 'foot', 'card', 'fim']
    bord = [0.0] + [c[0] for c in cuts] + [35.5]
    shots = [{'a': 0.0, 'b': 3.4, 'o': 0.0, 'kind': 'foot', 'trans': 'corte', 'dir': 1}]
    for i, (c, tr, d) in enumerate(cuts):
        b = bord[i + 2]
        shots.append({'a': c, 'b': b, 'o': round(o(c), 3), 'kind': kinds[i], 'trans': tr, 'dir': d})
    dur = o(35.5)
    voz = [(0.55, 1), (4.0, 2), (9.55, 3), (10.95, 4), (15.15, 5), (17.45, 6), (20.15, 7), (22.2, 8), (25.5, 9), (31.55, 10)]
    destaque = {'AutoFlow', 'AutoFlow.', 'ordens,', 'quadro.', 'placa.', 'histórico,', 'registrado,', 'experiência.', 'memória,', 'simples.', 'acompanhar.', 'perguntar', 'seguiu.', 'resposta.', 'carro,'}
    return dict(nome='v2', o=o, K=K, shots=shots, dur=dur, fim=fim_out, voz=voz, vel=1.15, pasta=R / 'voz_saida/af-v2-lapidado',
                destaque=destaque, music=dict(path=MUS / 'tensao/04.mp3', ss=27.0, vol=0.34), cuts=cuts)


def eventos_v2(c, P, voz_arr):
    o = c['o']; sfx = P['sfx']; amb = P['amb']
    # ambiente de oficina só nos planos filmados, some quando o sistema aparece
    a = room(o(13.47) + 0.8) * 0.9 * env_fade(int((o(13.47) + 0.8) * SR), 1.5, 0.9)
    amb.put(a, 0.0, 0.5)
    # chicotes em todos os cortes (pico do whoosh um pouco antes do corte)
    for k, (cs, tr, d) in enumerate(c['cuts']):
        t = o(cs)
        if tr == 'whip': sfx.put(sfx_lib('whoosh.wav', 0.9 + 0.1 * (k % 3), 0.55), t - 0.22, 0.7, pan=0.25 * d)
        elif tr == 'zoom': sfx.put(sfx_lib('whoosh.wav', 0.75, 0.6), t - 0.25, 0.65)
        elif tr == 'flash': sfx.put(sfx_lib('impacto.wav', 1.4, 0.4), t - 0.02, 0.5)
    # passos no primeiro plano e no plano que sai do sistema
    for k, t in enumerate([0.50, 1.20, 1.90, 2.60, 3.30]): sfx.put(step(0.7, 1.0 + 0.1 * (k % 2)), t, 0.8, pan=-0.1 + 0.2 * (k % 2))
    t0 = o(23.8)
    for k, t in enumerate([t0 + 0.3, t0 + 1.0, t0 + 1.7]): sfx.put(step(0.6, 1.0 + 0.1 * (k % 2)), t, 0.7)
    # carro chegando
    sfx.put(engine(2.4, 0.9), o(3.4) - 0.1, 0.55)
    # chaves
    for t in [o(4.7) + 0.2, o(4.7) + 0.9, o(11.2) + 0.2, o(11.2) + 1.2, o(25.6) + 0.3, o(25.6) + 1.3]: sfx.put(jingle(4, 0.7), t, 0.55)
    # teclado do monitor
    for k in range(9): sfx.put(sfx_lib('clique.wav', 0.9 + 0.2 * rng.random(), 0.7), o(5.9) + 0.15 + 0.1 * k + 0.03 * rng.random(), 0.28)
    # telefone vibrando
    for t in [o(6.9) + 0.1, o(6.9) + 0.55, o(6.9) + 1.0]: sfx.put(buzz(0.9), t, 0.55)
    # cartão "O dia seguiu."  ->  grave desce e some
    sfx.put(boom(1.8, 60, 30), o(8.5) + 0.55, 0.55)
    # sobe tensão até a revelação (silêncio de 0.18s antes do golpe)
    rev = o(13.47)
    t_r0 = o(11.2) + 0.7
    sfx.put(riser(rev - 0.18 - t_r0, 1.0), t_r0, 0.75)
    sfx.put(boom(2.6, 80, 34), rev, 1.0)
    sfx.put(sfx_lib('impacto.wav', 0.8, 1.0), rev, 0.8)
    sfx.put(sfx_lib('whoosh.wav', 0.7, 0.9), rev - 0.15, 0.7)
    # interface: pops nos títulos e cliques no quadro / histórico
    for cs in [13.47, 15.8, 18.5, 20.4]: sfx.put(sfx_lib('pop.wav', 1.0, 0.9), o(cs) + 0.3, 0.55)
    for t in [o(15.8) + 0.9, o(15.8) + 1.4, o(17.4) + 0.5, o(18.5) + 0.9, o(18.5) + 1.5, o(20.4) + 1.0, o(20.4) + 1.6, o(20.4) + 2.2]:
        sfx.put(sfx_lib('clique.wav', 1.0 + 0.15 * rng.random(), 0.9), t, 0.5)
    sfx.put(sfx_lib('pop.wav', 0.8, 0.9), o(27.7) + 0.4, 0.5)
    # fim: pré-golpe, golpe da marca, brilho
    f = c['fim']
    sfx.put(riser(0.7, 1.0), f - 0.72, 0.8)
    sfx.put(boom(3.0, 84, 32), f, 1.0)
    sfx.put(sfx_lib('impacto.wav', 0.7, 1.0), f, 0.9)
    sfx.put(ding(1.0), f + 0.18, 0.55)
    return dict(hits=[o(13.47), f], vazamentos=[])


MARCA = dict(path=MUS / 'inspira/06.mp3', ss=27.4, hit=0.6)  # a mesma música da marca nos dois vídeos


def montar(c, evfun):
    dur = c['dur']
    P = dict(sfx=Pista(dur), amb=Pista(dur), voz=Pista(dur), mus=Pista(dur))
    ev = evfun(c, P, None)
    # ---- voz
    caps = []
    for t, i in c['voz']:
        x, lead, fim, pal = voz_linha(c['pasta'], i, c['vel'])
        ini = t - lead
        P['voz'].put(x, ini, 1.0)
        for k, w in enumerate(pal):
            s = ini + w['s'] / c['vel']; e = ini + w['e'] / c['vel']
            if k == 0: s = t
            caps.append({'w': w['w'].strip(), 's': round(s, 3), 'e': round(max(e, s + 0.12), 3), 'hi': w['w'] in c['destaque'] or w['w'].strip() in c['destaque'], 'fim': bool(t >= c['fim'] - 0.1)})
    # ---- trilha principal (cai antes do cartão final) e música da marca
    m = c['music']; f = c['fim']
    cut = f - 0.45
    mus = ff_load(m['path'], ss=m['ss'], t=cut + 0.6)
    mus = mus[: int(cut * SR)] * env_fade(int(cut * SR), 1.5, 0.35) if len(mus) >= int(cut * SR) else mus
    P['mus'].put(mus, 0.0, m['vol'])
    mk = ff_load(MARCA['path'], ss=MARCA['ss'], t=(c['dur'] - f) + MARCA['hit'] + 0.5)
    mk = mk * env_fade(len(mk), 0.0, 1.6)
    P['mus'].put(mk, f - MARCA['hit'], 0.72)
    # ---- ducking da trilha sob a voz
    n = P['mus'].n
    d = duck_env(P['voz'].a, n)
    P['mus'].a = P['mus'].a * d
    mix = P['voz'].a * 1.0 + P['mus'].a + P['sfx'].a * 0.9 + P['amb'].a * 0.5
    return mix, caps, ev


def salvar_wav(arr, path, dur):
    arr = arr[: int(dur * SR)]
    pk = np.abs(arr).max()
    if pk > 0.99: arr = arr / pk * 0.99
    raw = (arr * 32767).astype('<i2').tobytes()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-", str(path)], input=raw, check=True)


if __name__ == "__main__":
    which = sys.argv[1]; work = Path(sys.argv[2] if len(sys.argv) > 2 else "/tmp")
    work.mkdir(parents=True, exist_ok=True)
    if which == "v2":
        c = cfg_v2(); evf = eventos_v2
    else:
        from lap_v3 import cfg_v3, eventos_v3
        c = cfg_v3(sys.modules[__name__]); evf = eventos_v3
    mix, caps, ev = montar(c, evf)
    salvar_wav(mix, work / f"mix_{which}.wav", c['dur'])
    # loudnorm em duas passagens (-14 LUFS, pico real <= -1.5 dBTP)
    mw = str(work / f"mix_{which}.wav")
    r = subprocess.run(["ffmpeg", "-v", "info", "-y", "-i", mw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
          f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mw, "-af", ln, "-ar", "48000", "-ac", "2", str(work / f"audio_{which}.wav")], check=True)
    props = dict(video=f"lap/{which}_limpo.mp4", audio=f"lap/audio_{which}.wav", dur=int(round(c['dur'] * 30)), shots=c['shots'], caps=caps,
                 hits=ev['hits'], fimCard=round(c['fim'], 3), nome=which)
    (work / f"props_{which}.json").write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
    print("ok", which, "dur", round(c['dur'], 2), "palavras", len(caps))
