"""Prévia do feed do Instagram (grade 3 colunas, mais recente no topo) para um intervalo de datas da fila.
Uso: python scripts/previa_feed.py 2026-10-19 2026-10-25 saida.jpg"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parent.parent
ini, fim, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
pastas = sorted(p for p in (R / "fila").iterdir() if p.is_dir() and ini <= p.name[:10] <= fim)
itens = []
for p in pastas:
    img = p / "slide-01.jpg" if (p / "slide-01.jpg").exists() else p / "capa.jpg"
    if img.exists():
        itens.append((p.name, img, (p / "video.mp4").exists()))
itens.reverse()  # o feed mostra o mais novo primeiro
W, H, G = 360, 450, 4
lin = (len(itens) + 2) // 3
tela = Image.new("RGB", (3 * W + 2 * G, lin * (H + G)), "#000")
d = ImageDraw.Draw(tela)
try:
    f = ImageFont.truetype(str(R / "carrossel/fontes/inter800.ttf"), 18)
except Exception:
    f = None
for i, (nome, img, video) in enumerate(itens):
    im = Image.open(img).convert("RGB")
    r = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1))
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
    x, y = (i % 3) * (W + G), (i // 3) * (H + G)
    tela.paste(im, (x, y))
    d.rectangle([x, y + H - 30, x + W, y + H], fill=(0, 0, 0))
    d.text((x + 8, y + H - 25), ("▶ " if video else "▦ ") + nome[5:10].replace("-", "/") + " " + nome[11:15], fill="#F5A623", font=f)
tela.save(out, quality=88)
print(len(itens), "peças ->", out)
