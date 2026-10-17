"""Exporta as capas desenhadas no Figma (API oficial do Figma, com FIGMA_TOKEN) para a fila.
Mapa em relancamento/figma_capas.json: {"arquivo": key, "capas": {node_id: destino}}.
Depois refaz o video_tiktok.mp4 (capa no 1º quadro) de cada vídeo."""
import io, json, os, sys, urllib.request
from pathlib import Path
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
RAIZ = Path(__file__).resolve().parent.parent
cfg = json.loads((RAIZ / "relancamento" / "figma_capas.json").read_text())
tok = os.environ["FIGMA_TOKEN"]
ids = ",".join(cfg["capas"])
req = urllib.request.Request(f"https://api.figma.com/v1/images/{cfg['arquivo']}?ids={ids}&format=png&scale=1", headers={"X-Figma-Token": tok})
urls = json.loads(urllib.request.urlopen(req, timeout=120).read())["images"]
import capa_no_video
for nid, destino in cfg["capas"].items():
    if not urls.get(nid):
        print("sem imagem:", nid); continue
    dados = urllib.request.urlopen(urls[nid], timeout=120).read()
    d = RAIZ / destino
    Image.open(io.BytesIO(dados)).convert("RGB").save(d, quality=94)
    print("ok", nid, "->", destino)
    if d.name == "capa.jpg":
        capa_no_video.fazer(d.parent)
