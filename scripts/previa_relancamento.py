"""Prévia da grade do Instagram com as peças do relançamento já finalizadas (mais novo primeiro)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
R = Path(__file__).resolve().parent.parent
def corte(p, reels):
    im = Image.open(p).convert("RGB"); w, h = im.size
    if reels:
        t = (h - 1440) // 2; im = im.crop((0, t, 1080, t + 1440))
    else:
        nw = int(h * 3 / 4); l = (w - nw) // 2; im = im.crop((l, 0, l + nw, h))
    return im.resize((360, 480))
def gerar(pecas, titulo, saida):
    linhas = (len(pecas) + 2) // 3
    W = 3 * 360 + 4 * 6; H = linhas * 486 + 176
    m = Image.new("RGB", (W, H), "#000"); d = ImageDraw.Draw(m)
    f = ImageFont.truetype(str(R / "carrossel/fontes/inter800.ttf"), 30); g = ImageFont.truetype(str(R / "carrossel/fontes/inter500.ttf"), 22)
    d.text((24, 40), "seraphimbr_", fill="#fff", font=f); d.text((24, 90), titulo, fill="#9a9aa2", font=g)
    for i, (p, r, l) in enumerate(pecas):
        x = 6 + (i % 3) * 366; y = 170 + (i // 3) * 486
        m.paste(corte(R / p, r), (x, y)); d.rectangle((x + 8, y + 8, x + 160, y + 40), fill="#000"); d.text((x + 14, y + 12), l, fill="#F5A623", font=g)
    m.save(saida)
if __name__ == "__main__":
    gerar([("relancamento/V2/capa.jpg", True, "V2 · 19:30"), ("relancamento/C2/instagram/slide-01.jpg", False, "C2 · 17:30"),
           ("relancamento/V1/capa.jpg", True, "V1 · 12:30"), ("relancamento/C1/instagram/slide-01.jpg", False, "C1 · 09:00")],
          "Prévia da grade — segunda 19/10 (mais novo primeiro)", R / "relancamento/previa-feed-19-10.png")
