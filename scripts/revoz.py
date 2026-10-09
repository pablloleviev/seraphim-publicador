"""
Refaz, com a voz do Gemini, os vídeos que saíram com a voz reserva (cota grátis do Gemini acabou).
Roda todo dia logo depois da cota renovar. Começa pelos que vão ao ar primeiro e para quando a cota acabar.
"""
import json, shutil, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BRT = timezone(timedelta(hours=-3))
estado = json.loads((RAIZ / "estado.json").read_text()) if (RAIZ / "estado.json").exists() else {"itens": {}}
pend = []
for f in (RAIZ / "revoz").glob("*.json"):
    spec = json.loads(f.read_text(encoding="utf-8"))
    pend.append((spec.get("quando", "9999"), f, spec))
for quando, f, spec in sorted(pend, key=lambda x: x[0]):
    destino = RAIZ / spec["destino"]
    if not destino.exists() or destino.name in estado.get("itens", {}):
        f.unlink(); print(f"{f.stem}: já enviado ou removido, ignorando"); continue
    tmp = RAIZ / "revoz" / f"{f.stem}.mp4"
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "fazer_video.py"), str(f), "--voz", "gemini-so", "--saida", str(tmp)],
                       capture_output=True, text=True)
    print(r.stdout[-800:], r.stderr[-800:])
    if r.returncode == 3 or not tmp.exists():
        print("Cota do Gemini acabou por hoje. Continua amanhã."); break
    shutil.move(str(tmp), destino / "video.mp4")
    f.unlink()
    print(f"{f.stem}: refeito com Gemini ✓")
