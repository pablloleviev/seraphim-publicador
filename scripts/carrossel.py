"""
Gerador de carrossel da Seraphim.

Uso:
    python scripts/carrossel.py entrada/meu-carrossel.json

O JSON descreve os slides (veja exemplos/carrossel-exemplo.json).
Os PNGs (1080x1350) saem em entrega/carrosseis/<nome>/.

Marcação de texto:
    *palavra*  -> fica dourada
    **palavra** -> fica em negrito branco (no texto de apoio)
    |          -> quebra de linha no título
"""
import asyncio, json, re, sys
from pathlib import Path
from playwright.async_api import async_playwright

RAIZ = Path(__file__).resolve().parent.parent
FONTES = (RAIZ / "carrossel" / "fontes").as_uri()
SERA = (RAIZ / "carrossel" / "sera").as_uri()
ICONE = (RAIZ / "carrossel" / "marca" / "icone.png").as_uri()

CSS = f"""
@font-face{{font-family:Anton;src:url({FONTES}/anton.ttf)}}
@font-face{{font-family:Inter;font-weight:500;src:url({FONTES}/inter500.ttf)}}
@font-face{{font-family:Inter;font-weight:800;src:url({FONTES}/inter800.ttf)}}
*{{margin:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;background:#0A0A0C;color:#F5F5F7;font-family:Inter;font-weight:500;position:relative;overflow:hidden}}
.bg{{position:absolute;inset:0;background:radial-gradient(circle at 80% 15%,rgba(245,166,35,.16),transparent 45%),radial-gradient(circle at 10% 95%,rgba(245,166,35,.07),transparent 40%)}}
.dots{{position:absolute;right:-60px;top:-60px;width:520px;height:520px;background-image:radial-gradient(rgba(255,255,255,.13) 2px,transparent 2.4px);background-size:22px 22px;-webkit-mask-image:radial-gradient(circle,#000 20%,transparent 70%)}}
.wrap{{position:absolute;left:80px;right:80px;top:110px}}
.tag{{display:inline-block;font-weight:800;font-size:24px;letter-spacing:6px;color:#F5A623;text-transform:uppercase;margin-bottom:34px}}
h1{{font-family:Anton;font-weight:400;text-transform:uppercase;line-height:1.02;letter-spacing:1px;font-size:92px}}
.capa h1{{font-size:132px}}
.gold{{color:#F5A623}}
p{{font-size:38px;line-height:1.38;color:#A1A1AA;margin-top:36px;max-width:820px}}
p b{{color:#F5F5F7;font-weight:800}}
.num{{font-family:Anton;font-size:230px;line-height:1;color:transparent;-webkit-text-stroke:3px #F5A623;margin-bottom:10px}}
.line{{width:120px;height:6px;background:#F5A623;margin:40px 0 0}}
.sera{{position:absolute;right:30px;bottom:150px;width:470px}}
.card{{margin-top:48px;border:1px solid rgba(245,166,35,.35);background:rgba(245,166,35,.06);border-radius:28px;padding:34px 38px;font-size:36px;line-height:1.4;max-width:860px;display:inline-block}}
.card b{{color:#F5A623}}
.foot{{position:absolute;left:80px;right:80px;bottom:56px;display:flex;align-items:center;justify-content:space-between;font-size:26px;color:#A1A1AA}}
.foot .l{{display:flex;align-items:center;gap:16px}}
.foot img{{width:46px;height:46px;border-radius:50%}}
.foot .r{{letter-spacing:3px}}
.swipe{{color:#F5A623;font-weight:800;margin-left:14px}}
.branco{{background:#F5F5F7;color:#0A0A0C}}.branco p{{color:#3f3f46}}.branco p b{{color:#0A0A0C}}.branco .foot{{color:#52525b}}.branco .card{{color:#0A0A0C}}
"""


def fmt(t: str) -> str:
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t or "")
    t = re.sub(r"\*(.+?)\*", r'<span class="gold">\1</span>', t)
    return t.replace("|", "<br>")


def slide_html(s: dict, i: int, n: int, arroba: str) -> str:
    tipo = s.get("tipo", "texto")
    corpo = ""
    if s.get("tag"):
        corpo += f'<div class="tag">{s["tag"]}</div>'
    if s.get("numero"):
        corpo += f'<div class="num">{s["numero"]}</div>'
    if s.get("titulo"):
        corpo += f'<h1>{fmt(s["titulo"])}</h1>'
    if tipo == "texto" and s.get("linha", False):
        corpo += '<div class="line"></div>'
    if s.get("texto"):
        corpo += f'<p>{fmt(s["texto"])}</p>'
    if s.get("card"):
        corpo += f'<div class="card">{fmt(s["card"])}</div>'
    sera = f'<img class="sera" src="{SERA}/{s["sera"]}.png">' if s.get("sera") else ""
    cls = ("capa " if tipo == "capa" else "") + ("branco" if s.get("fundo") == "branco" else "")
    swipe = '<span class="swipe">ARRASTA →</span>' if i < n else ""
    return f"""<html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body class="{cls}"><div class="bg"></div><div class="dots"></div>{sera}
<div class="wrap">{corpo}</div>
<div class="foot"><div class="l"><img src="{ICONE}">{arroba}</div><div class="r">{i}/{n}{swipe}</div></div>
</body></html>"""


async def main(caminho: str, saida_dir: str = None):
    spec = json.loads(Path(caminho).read_text(encoding="utf-8"))
    nome = spec.get("nome", Path(caminho).stem)
    arroba = spec.get("arroba", "@seraphimtech_")
    slides = spec["slides"]
    saida = Path(saida_dir) if saida_dir else RAIZ / "entrega" / "carrosseis" / nome
    saida.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        nav = await p.chromium.launch()
        pg = await nav.new_page(viewport={"width": 1080, "height": 1350})
        tmp = saida / "_tmp.html"
        for i, s in enumerate(slides, 1):
            tmp.write_text(slide_html(s, i, len(slides), arroba), encoding="utf-8")
            await pg.goto(tmp.as_uri())
            await pg.wait_for_timeout(250)
            await pg.screenshot(path=str(saida / f"slide-{i:02d}.png"))
        tmp.unlink()
        await nav.close()
    if spec.get("legenda"):
        (saida / "legenda.txt").write_text(spec["legenda"], encoding="utf-8")
    print(f"Pronto: {len(slides)} slides em {saida}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/carrossel.py entrada/arquivo.json")
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
