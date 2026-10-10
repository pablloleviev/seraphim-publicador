"""
Refaz agora a EDIÇÃO (visual/tema) dos vídeos da fila que estão com a voz reserva.
Tenta a voz do Gemini; se a cota acabou, usa a reserva (a mesma de antes — não piora nada).
Os que já têm voz do Gemini ficam para o revoz.py (que só aceita Gemini).
    python scripts/reeditar.py <parte> <total_de_partes>
"""
import json, shutil, subprocess, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
parte, total = int(sys.argv[1]), int(sys.argv[2])
estado = json.loads((RAIZ / "estado.json").read_text()).get("itens", {}) if (RAIZ / "estado.json").exists() else {}
specs = sorted((RAIZ / "revoz").glob("*.json"), key=lambda f: json.loads(f.read_text())["destino"])
for i, f in enumerate(specs):
    if i % total != parte:
        continue
    spec = json.loads(f.read_text(encoding="utf-8"))
    destino = RAIZ / spec["destino"]
    log = destino / "log.txt"
    st = estado.get(destino.name, {}).get("status")
    if not destino.exists() or st in ("publicado", "pulado") or (log.exists() and "Voz: gemini" in log.read_text()):
        continue
    tmp = RAIZ / "revoz" / f"{f.stem}.reedit.mp4"
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "fazer_video.py"), str(f), "--voz", "gemini", "--saida", str(tmp)],
                       capture_output=True, text=True)
    print(f.stem, r.returncode, r.stdout[-400:], r.stderr[-400:], flush=True)
    if r.returncode != 0 or not tmp.exists():
        continue
    shutil.move(str(tmp), destino / "video.mp4")
    log.write_text(r.stdout[-3000:], encoding="utf-8")
    if "Voz: gemini" in r.stdout:
        f.unlink()   # já saiu com a voz boa: não precisa mais do revoz
    print(f"{f.stem}: reeditado ✓", flush=True)
