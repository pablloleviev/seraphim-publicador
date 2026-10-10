"""
Baixa carrosséis exportados do Canva (links assinados) e coloca na fila de publicação.
Cada pedido: canva/baixar/<nome>.json
  {"destino": "fila/2026-10-10_1800_nome", "ordem": [8,7,6,5,4,3,2], "urls": [...],
   "item": {"tipo": "carrossel", "legenda": "...", "quando": "2026-10-10T18:00:00-03:00"}}
"ordem" = números das páginas do Canva na ordem em que devem aparecer no post.
"""
import json, re, shutil, urllib.request
from pathlib import Path
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
for ped in sorted((RAIZ / "canva" / "baixar").glob("*.json")):
    d = json.loads(ped.read_text(encoding="utf-8"))
    por_pag = {}
    for u in d["urls"]:
        m = re.search(r"/(\d{4})-[^/]*\.(?:png|jpg)", u)
        por_pag[int(m.group(1)) if m else len(por_pag) + 1] = u
    ordem = d.get("ordem") or sorted(por_pag)
    dest = RAIZ / d["destino"]
    tmp = dest.with_name(dest.name + ".tmp")
    shutil.rmtree(tmp, ignore_errors=True); tmp.mkdir(parents=True)
    try:
        for i, pag in enumerate(ordem, 1):
            arq = tmp / f"baixado-{i}"
            req = urllib.request.Request(por_pag[pag], headers={"User-Agent": "Mozilla/5.0"})
            arq.write_bytes(urllib.request.urlopen(req, timeout=120).read())
            Image.open(arq).convert("RGB").save(tmp / f"slide-{i:02d}.jpg", quality=92)
            arq.unlink()
    except Exception as e:
        print(f"[erro] {ped.name}: {e}"); shutil.rmtree(tmp, ignore_errors=True); continue
    if dest.exists():
        for old in dest.glob("slide-*"):
            old.unlink()
    dest.mkdir(parents=True, exist_ok=True)
    for f in tmp.iterdir():
        shutil.move(str(f), dest / f.name)
    tmp.rmdir()
    meta_arq = dest / "item.json"
    meta = json.loads(meta_arq.read_text(encoding="utf-8")) if meta_arq.exists() else {}
    meta.update(d.get("item", {})); meta["fonte"] = "canva"
    meta_arq.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    ped.unlink()
    print(f"OK: {dest.name} ({len(ordem)} slides do Canva)")
