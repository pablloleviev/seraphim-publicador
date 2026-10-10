"""
Trilha sonora emocional dos cortes (estilo trailer).

A trilha é montada por TRECHOS, seguindo o clima de cada cena:
  - gancho (primeiros ~3 s): impacto/riser + música épica já no "drop" (parte mais forte)
  - problema (contador, pergunta, foto vermelha, painel): tensão / sombrio
  - virada (frase, serifa, sera): emoção (piano/cordas)
  - solução (diagrama, cards, níveis, digitando): energia / inspiração
  - pausa de respiro (silêncio curto) e chamada final em clímax épico
Trocas com crossfade no corte da cena; a música abaixa sozinha quando a voz fala (sidechain)
e volta nas pausas. Saída: job/trilha.wav (já mixada, sem a voz).
"""
import hashlib, json, random, subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MUS = RAIZ / "musica"

CLIMA_PADRAO = {
    "palavra": "epico", "frase": "emocao", "contador": "tensao", "foto": "tensao", "pergunta": "tensao",
    "digitando": "energia", "diagrama": "energia", "cards": "inspira", "parede": "sombrio", "sera": "emocao",
    "painel": "tensao", "niveis": "inspira", "serifa": "emocao", "cta": "epico",
}
# onde começar a tocar cada faixa, conforme o clima
# (antes as calmas começavam no trecho mais baixo da faixa e quase não se ouviam: agora entram no "corpo", já cheio)
PONTO = {"epico": "drop", "energia": "drop", "tensao": "corpo", "sombrio": "corpo", "emocao": "corpo", "inspira": "corpo"}
# volume percebido de cada clima (LUFS) antes de ir para baixo da voz: todas niveladas, as épicas um pouco acima
ALVO = {"epico": -13.5, "energia": -14.0, "tensao": -15.0, "sombrio": -15.5, "emocao": -15.0, "inspira": -14.5, "hook": -13.0}
VOLUME = ALVO  # compatibilidade
BUS_DB = -2.0      # nível geral da música em relação à voz (voz fica em -14 LUFS)


def ganho(info, clima, extra_db=0.0):
    """Ganho linear para levar a faixa ao volume-alvo do clima (nivelamento entre músicas diferentes)."""
    medido = info.get("lufs")
    db = (ALVO[clima] - medido) if medido is not None else 0.0
    db = max(-12.0, min(12.0, db)) + extra_db
    return round(10 ** (db / 20), 3)


def _faixas(clima):
    return sorted((MUS / clima).glob("*.mp3")) if (MUS / clima).exists() else []


def clima_da_cena(c):
    if c.get("clima") in ALVO and c.get("clima") != "hook":
        return c["clima"]
    t = c.get("tipo", "frase")
    if t == "foto" and c.get("tom") in ("dourado", "normal"):
        return "inspira"
    return CLIMA_PADRAO.get(t, "emocao")


def trechos(cenas):
    """Agrupa cenas seguidas de mesmo clima; força o gancho épico e o clímax final."""
    out = []
    for i, c in enumerate(cenas):
        cl = "epico" if i == 0 else clima_da_cena(c)
        if c.get("tipo") == "cta":
            cl = "epico"
        if out and out[-1]["clima"] == cl and c.get("tipo") != "cta":
            out[-1]["fim"] = c["fim"]
        else:
            out.append({"clima": cl, "inicio": c["inicio"], "fim": c["fim"], "cta": c.get("tipo") == "cta"})
    # evita trechos muito curtos (< 2,5 s) no meio: junta com o anterior
    final = []
    for t in out:
        if final and not t["cta"] and (t["fim"] - t["inicio"]) < 2.5 and len(final) > 0:
            final[-1]["fim"] = t["fim"]
        else:
            final.append(t)
    return final


def montar(cenas, voz, saida, semente="x", dur_total=None):
    if not (MUS / "indice.json").exists():
        return None
    idx = json.loads((MUS / "indice.json").read_text())
    rnd = random.Random(int(hashlib.md5(semente.encode()).hexdigest()[:8], 16))
    dur_total = dur_total or cenas[-1]["fim"]
    ts = trechos(cenas)
    entradas, filtros, rot = [], [], []
    usadas = set()
    for k, t in enumerate(ts):
        fs = [f for f in _faixas(t["clima"]) if f not in usadas] or _faixas(t["clima"])
        if not fs:
            continue
        f = rnd.choice(fs); usadas.add(f)
        info = idx.get(f"{t['clima']}/{f.stem}", {"dur": 120, "pico": 10, "drop": 10, "calmo": 0})
        ponto = info.get(PONTO[t["clima"]], info.get("pico", 0))
        ini = max(0.0, ponto - (0.4 if t["clima"] in ("epico", "energia") else 0))
        respiro = 0.35 if t["cta"] else 0.0               # silêncio curto antes do clímax final
        a, b = t["inicio"] + respiro, (dur_total if k == len(ts) - 1 else t["fim"] + 0.35)
        d = max(0.5, b - a)
        if ini + d > info["dur"] - 1:
            ini = max(0, info["dur"] - d - 1)
        n = sum(1 for x in entradas if x == "-i")
        entradas += ["-ss", f"{ini:.2f}", "-t", f"{d + 0.1:.2f}", "-i", str(f)]
        fin = 0.25 if k == 0 else 0.35
        filtros.append(f"[{n}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={ganho(info, t['clima'], 3.0 if k == 0 else 0.0)},"
                       f"afade=t=in:d={0.05 if k == 0 else fin},afade=t=out:st={max(0, d - 0.4):.2f}:d=0.4,"
                       f"adelay={int(a * 1000)}|{int(a * 1000)}[m{n}]")
        rot.append(f"[m{n}]")
    # impacto/riser no gancho (faixa "hook": trailer hit)
    hooks = _faixas("hook")
    if hooks:
        h = rnd.choice(hooks); n = sum(1 for x in entradas if x == "-i")
        hinfo = idx.get(f"hook/{h.stem}", {})
        entradas += ["-t", "3.5", "-i", str(h)]
        filtros.append(f"[{n}:a]aformat=sample_rates=44100:channel_layouts=stereo,volume={ganho(hinfo, 'hook', -2.0)},afade=t=out:st=2.6:d=0.9[m{n}]")
        rot.append(f"[m{n}]")
    if not rot:
        return None
    # índice da voz = número de entradas -i até agora
    nvoz = sum(1 for x in entradas if x == "-i")
    entradas += ["-i", str(voz)]
    filtros.append(f"{''.join(rot)}amix=inputs={len(rot)}:normalize=0:dropout_transition=0,"
                   # abre espaço para a voz (corta 2-4 kHz da música) em vez de só abaixar o volume
                   f"highpass=f=35,equalizer=f=2800:t=o:w=1.4:g=-4,equalizer=f=11000:t=h:w=1:g=1.5,"
                   f"volume={10 ** (BUS_DB / 20):.3f}[mus]")
    filtros.append(f"[{nvoz}:a]aformat=sample_rates=44100:channel_layouts=stereo,apad=whole_dur={dur_total:.2f},asplit=2[vsc][vx]")
    # sidechain: a música abaixa ~9 dB quando a voz fala e volta nas pausas
    filtros.append("[mus][vsc]sidechaincompress=threshold=0.04:ratio=3:attack=20:release=400:makeup=1[duck]")
    filtros.append(f"[duck]atrim=0:{dur_total:.2f},alimiter=limit=0.5:level=disabled[out]")
    filtros.append("[vx]anullsink")
    cmd = ["ffmpeg", "-v", "error", "-y", *entradas, "-filter_complex", ";".join(filtros), "-map", "[out]",
           "-ar", "44100", "-ac", "2", str(saida)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("[trilha] falhou:", r.stderr[-600:])
        return None
    print("[trilha] trechos:", " | ".join(f"{t['clima']} {t['inicio']:.1f}-{t['fim']:.1f}s" for t in ts))
    return saida
