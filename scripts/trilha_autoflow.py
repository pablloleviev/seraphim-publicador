"""Trilhas dos vídeos AutoFlow (ffmpeg). Uso: python scripts/trilha_autoflow.py v2|v3|v12|v13
V12 e V13 seguem o padrão do V1 aprovado: só música e efeitos (sem narração),
com a música recuando no preto que antecede cada revelação do produto."""
import subprocess, sys
from pathlib import Path
R = Path(__file__).resolve().parent.parent
SFX = R / "motor/public/sfx"; OUT = R / "motor/public/af"

def run(args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)

def v2():
    voz = R / "voz_saida/autoflow-v2"
    l5 = R / "voz_saida/autoflow-v2-l5/linha-01.mp3"
    linhas = [voz / f"linha-0{i}.mp3" for i in range(1, 8)]
    if l5.exists(): linhas[4] = l5
    inicios = [0.5, 5.6, 15.3, 19.9, 26.2, 32.2, 36.5]
    ins, fl = [], []
    for i, (f, t) in enumerate(zip(linhas, inicios)):
        ins += ["-i", str(f)]; ms = int(t * 1000)
        fl.append(f"[{i}]aresample=44100,aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{i}]")
    n = len(linhas)
    fl.append("".join(f"[v{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0,apad=whole_dur=42,highpass=f=80,acompressor=threshold=-20dB:ratio=3:attack=5:release=120,volume=1.6,asplit=2[voz][sc]")
    k = n
    ins += ["-ss", "40", "-t", "42", "-i", str(R / "musica/emocao/01.mp3")]; m = k; k += 1
    ins += ["-i", str(SFX / "whoosh.wav"), "-i", str(SFX / "clique.wav"), "-i", str(SFX / "impacto.wav")]
    fl.append(f"[{m}]aresample=44100,volume=0.55,afade=t=in:d=1.2,afade=t=out:st=39.5:d=2.5[mus]")
    fl.append("[mus][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[duck]")
    fl.append(f"[{k}]volume=0.25,adelay=16400|16400[w];[{k+1}]volume=0.3,adelay=17200|17200[c];[{k+2}]lowpass=f=1500,volume=0.35,aecho=0.8:0.6:140:0.2,adelay=36400|36400[h]")
    fl.append("[voz][duck][w][c][h]amix=inputs=5:normalize=0,atrim=0:42,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    run([*ins, "-filter_complex", ";".join(fl), "-map", "[out]", "-ar", "44100", "-ac", "2", str(OUT / "trilha_v2.wav")])

def v3():
    ins = ["-ss", "30", "-t", "45", "-i", str(R / "musica/inspira/02.mp3")]
    fl = ["[0]aresample=44100,volume=0.7,afade=t=in:d=1.5,afade=t=out:st=42:d=3[mus]"]
    ticks = [0.3, 15.3, 25.3, 35.3]; woos = [9.9, 19.9, 30.9]; j = 1; tags = ["[mus]"]
    for t in ticks:
        ins += ["-i", str(SFX / "tic.wav")]; ms = int(t * 1000); fl.append(f"[{j}]volume=0.35,adelay={ms}|{ms}[t{j}]"); tags.append(f"[t{j}]"); j += 1
    for t in woos:
        ins += ["-i", str(SFX / "whoosh.wav")]; ms = int(t * 1000); fl.append(f"[{j}]volume=0.2,adelay={ms}|{ms}[t{j}]"); tags.append(f"[t{j}]"); j += 1
    ins += ["-i", str(SFX / "impacto.wav")]; fl.append(f"[{j}]lowpass=f=1500,volume=0.35,aecho=0.8:0.6:140:0.2,adelay=40000|40000[t{j}]"); tags.append(f"[t{j}]"); j += 1
    fl.append("".join(tags) + f"amix=inputs={len(tags)}:normalize=0,atrim=0:45,loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    run([*ins, "-filter_complex", ";".join(fl), "-map", "[out]", "-ar", "44100", "-ac", "2", str(OUT / "trilha_v3.wav")])


def _dip(ini, fim, prof=0.07, r=0.55):
    """Música recua no preto antes da revelação (como no V1) e volta em seguida."""
    a, b, c, d = ini - r, ini, fim, fim + r
    return (f"volume=eval=frame:volume='if(lt(t,{a}),1,if(lt(t,{b}),1-(t-{a})/{r}*{1-prof:.2f},"
            f"if(lt(t,{c}),{prof},if(lt(t,{d}),{prof}+(t-{c})/{r}*{1-prof:.2f},1))))'")


def _trilha(saida, musica, ss, dur, dips, efeitos, vol=0.62):
    """musica = caminho; dips = [(ini, fim)]; efeitos = [(arquivo, segundo, volume, grave?)]"""
    ins = ["-ss", str(ss), "-t", str(dur), "-i", str(musica)]
    fl = [f"[0]aresample=44100,volume={vol},afade=t=in:d=1.3,afade=t=out:st={dur - 2.6:.2f}:d=2.6"
          + "".join("," + _dip(a, b) for a, b in dips) + "[mus]"]
    tags = ["[mus]"]
    for j, (arq, t, v, grave) in enumerate(efeitos, start=1):
        ins += ["-i", str(SFX / arq)]
        ms = int(t * 1000)
        grav = "lowpass=f=1500,aecho=0.8:0.6:140:0.2," if grave else ""
        fl.append(f"[{j}]{grav}volume={v},adelay={ms}|{ms}[e{j}]")
        tags.append(f"[e{j}]")
    fl.append("".join(tags) + f"amix=inputs={len(tags)}:normalize=0,atrim=0:{dur},loudnorm=I=-14:TP=-1.5:LRA=11[out]")
    run([*ins, "-filter_complex", ";".join(fl), "-map", "[out]", "-ar", "44100", "-ac", "2", str(OUT / saida)])


def v12():
    # 39 s: montagem (0-12) | preto 12-13 | produto 13-31 | oficina 31-34,2 | fecho 34,2-39
    _trilha("trilha_v12.wav", R / "musica/inspira/06.mp3", 56, 39, [(11.9, 12.95)], [
        ("whoosh.wav", 3.05, 0.18, False), ("whoosh.wav", 6.65, 0.18, False), ("whoosh.wav", 10.15, 0.2, False),
        ("impacto.wav", 13.0, 0.4, True), ("clique.wav", 22.2, 0.22, False), ("whoosh.wav", 30.95, 0.2, False),
        ("impacto.wav", 34.2, 0.35, True)])


def v13():
    # 44 s: manhã (0-9,9) | painel 10,8-20,2 | tarde 20,2-24,5 | nova OS + celular 25-35,4 | portão 35,4-39 | fecho 39-44
    _trilha("trilha_v13.wav", R / "musica/emocao/03.mp3", 77, 44, [(9.95, 10.75), (24.2, 24.95)], [
        ("tic.wav", 0.3, 0.3, False), ("whoosh.wav", 3.25, 0.18, False), ("whoosh.wav", 5.65, 0.18, False),
        ("impacto.wav", 10.8, 0.4, True), ("tic.wav", 20.2, 0.3, False), ("whoosh.wav", 22.55, 0.2, False),
        ("impacto.wav", 25.0, 0.38, True), ("whoosh.wav", 31.2, 0.18, False), ("tic.wav", 35.4, 0.28, False),
        ("impacto.wav", 39.0, 0.35, True)])


{"v2": v2, "v3": v3, "v12": v12, "v13": v13}[sys.argv[1]]()
print("ok", sys.argv[1])
