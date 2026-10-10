"""Roda só o robô de comentários por alguns minutos (teste), sem publicar nada."""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import comentarios
from pathlib import Path
EST = Path(__file__).resolve().parent.parent / "estado.json"
estado = json.loads(EST.read_text())
fim = time.time() + int(os.environ.get("MINUTOS", "12")) * 60
while time.time() < fim:
    comentarios.verificar(estado)
    EST.write_text(json.dumps(estado, indent=2, ensure_ascii=False))
    time.sleep(30)
print("respondidos:", estado.get("respondidos"))
