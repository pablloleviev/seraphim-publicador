"""Trilhas dos vídeos AutoFlow V2 e V3 (ffmpeg). Uso: python scripts/trilha_autoflow.py v2|v3"""
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

{"v2": v2, "v3": v3}[sys.argv[1]]()
print("ok", sys.argv[1])
