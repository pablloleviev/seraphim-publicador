"""Gera narração linha a linha (Gemini Puck -> fallback edge-tts Antonio) para vídeos montados à mão.
Lê voz_pedidos/<nome>.json {"estilo": "...", "linhas": ["...", ...]} e grava voz_saida/<nome>/linha-NN.mp3.
Não toca na fila nem nas automações de publicação."""
import json, os, sys, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
RAIZ = Path(__file__).resolve().parent.parent
import fazer_video as F

for ped in sorted((RAIZ / "voz_pedidos").glob("*.json")):
    d = json.loads(ped.read_text(encoding="utf-8"))
    out = RAIZ / "voz_saida" / ped.stem
    if (out / "ok.json").exists():
        continue
    out.mkdir(parents=True, exist_ok=True)
    if d.get("estilo"):
        os.environ["GEMINI_ESTILO"] = d["estilo"]
    usados = []
    if d.get("voz"):  # "masculina" | "feminina" | nome de voz do Gemini
        F.GEMINI_VOZ_ATUAL = F.VOZES_GEMINI.get(d["voz"], d["voz"])
    for i, linha in enumerate(d["linhas"], 1):
        mp3 = out / f"linha-{i:02d}.mp3"
        motor = None
        for nome, fn in (("gemini", F.voz_gemini), ("edge", lambda t, m: F.voz_edge(t, m, d.get("edge_voz", "pt-BR-AntonioNeural")))):
            try:
                pal = fn(linha, mp3); motor = nome
                if pal: (out / f"linha-{i:02d}.json").write_text(json.dumps(pal, ensure_ascii=False), encoding="utf-8")
                break
            except Exception as e:
                print(f"[aviso] {nome} falhou na linha {i}: {str(e)[:200]}")
        usados.append(motor)
        print(i, motor, linha)
    (out / "ok.json").write_text(json.dumps({"motores": usados}, ensure_ascii=False), encoding="utf-8")
