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

# mesmos temas dos vídeos (motor/src/Video.tsx): cada post com identidade própria, a marca aparece sutil (fio/ícone dourado)
OURO = "#F5A623"
TEMAS = {
 "noir": dict(bg="#0A0A0C", texto="#F5F5F7", dest=OURO, apoio="#A1A1AA", brilho="245,166,35", marca=OURO, fonte="Anton", peso=400, caixa=True, k=1.0,
              alt=("#F5F5F7", "#0A0A0C", "#B86E00", "#3f3f46")),
 "editorial": dict(bg="#F1ECE3", texto="#161412", dest="#B5651D", apoio="#5b544c", brilho="226,182,107", marca="#C08A2E", fonte="DMSerif", peso=400, caixa=False, k=0.9,
              alt=("#161412", "#F1ECE3", "#E2B66B", "#a8a196")),
 "terminal": dict(bg="#06110C", texto="#E6FFF1", dest="#3DFFA8", apoio="#7FA897", brilho="61,255,168", marca=OURO, fonte="Jet", peso=800, caixa=True, k=0.72,
              alt=("#E6FFF1", "#06110C", "#00895A", "#2f5546")),
 "meianoite": dict(bg="#0A1430", texto="#F2F6FF", dest="#7CC4FF", apoio="#93A3C8", brilho="61,107,255", marca=OURO, fonte="Space", peso=700, caixa=True, k=0.8,
              alt=("#F2F6FF", "#0A1430", "#1F5FD6", "#43507a")),
 "brutal": dict(bg="#FFD43B", texto="#0A0A0C", dest="#0A0A0C", apoio="#2a2a2a", brilho="255,255,255", marca="#0A0A0C", fonte="Archivo", peso=400, caixa=True, k=0.7,
              alt=("#0A0A0C", "#FFD43B", "#FFFFFF", "#cfcfcf"), sublinhar=True),
 "vinho": dict(bg="#250B12", texto="#F7ECDF", dest="#E8B77A", apoio="#B99A90", brilho="122,30,48", marca="#E8B77A", fonte="Playfair", peso=900, caixa=False, k=0.85,
              alt=("#F7ECDF", "#250B12", "#8A2A3C", "#6b4e47")),
 "eletrico": dict(bg="#FAFAFA", texto="#0A0A0C", dest="#2F5BFF", apoio="#55555c", brilho="47,91,255", marca=OURO, fonte="Montserrat", peso=900, caixa=True, k=0.72,
              alt=("#2F5BFF", "#FFFFFF", "#FFD43B", "#dfe6ff")),
 "grafite": dict(bg="#1B1B1E", texto="#F5F5F7", dest="#FF6A3D", apoio="#9a9aa2", brilho="255,106,61", marca=OURO, fonte="Bebas", peso=400, caixa=True, k=1.1,
              alt=("#F5F5F7", "#1B1B1E", "#E0461A", "#52525b")),
 "ultravioleta": dict(bg="#120A26", texto="#F4F0FF", dest="#B69CFF", apoio="#9b91bd", brilho="123,77,255", marca=OURO, fonte="Space", peso=700, caixa=True, k=0.8,
              alt=("#F4F0FF", "#120A26", "#6A3DF0", "#4d4470")),
}
ARQ_FONTE = {"Bebas": "bebas.ttf", "Archivo": "archivo.ttf", "DMSerif": "dmserif.ttf", "Space": "spacegrotesk.ttf",
             "Jet": "jetbrains.ttf", "Playfair": "playfair.ttf", "Montserrat": "montserrat.ttf"}


def css_tema(nome):
    t = TEMAS.get(nome or "noir", TEMAS["noir"])
    if nome in (None, "", "noir"):
        return ""
    ff = f"@font-face{{font-family:{t['fonte']};src:url({FONTES}/{ARQ_FONTE[t['fonte']]})}}" if t["fonte"] in ARQ_FONTE else ""
    ab, at, ad, aa = t["alt"]
    claro = int(t["bg"][1:3], 16) * .299 + int(t["bg"][3:5], 16) * .587 + int(t["bg"][5:7], 16) * .114 > 150
    tinta = "10,10,12" if claro else "255,255,255"
    sera_claro = (f".sera{{width:430px;height:430px;object-fit:contain;padding:30px;border-radius:50%;background:radial-gradient(circle,#1a1a1e,#0A0A0C 70%);box-shadow:0 0 0 6px {t['marca']}}}" if claro else "")
    return ff + f"""
body{{background:{t['bg']};color:{t['texto']}}}
.bg{{background:radial-gradient(circle at 80% 15%,rgba({t['brilho']},.18),transparent 45%),radial-gradient(circle at 10% 95%,rgba({t['brilho']},.08),transparent 40%)}}
.dots{{background-image:radial-gradient(rgba({tinta},.13) 2px,transparent 2.4px)}}
h1{{font-family:{t['fonte']};font-weight:{t['peso']};text-transform:{'uppercase' if t['caixa'] else 'none'};font-size:{int(92*t['k'])}px;line-height:1.08}}
.capa h1{{font-size:{int(132*t['k'])}px}}
.gold{{color:{t['dest']};{'text-decoration:underline;text-decoration-color:'+OURO+';text-decoration-thickness:8px;text-underline-offset:10px;' if t.get('sublinhar') else ''}}}
.tag,.swipe,.card b{{color:{t['marca'] if t['marca']!=t['texto'] else t['dest']}}}
p{{color:{t['apoio']}}} p b{{color:{t['texto']}}}
.num{{font-family:{t['fonte'] if t['fonte'] in ('DMSerif','Playfair','Jet') else 'Anton'};font-weight:{t['peso']};color:{t['dest']};-webkit-text-stroke:0}}
.line{{background:{t['marca']}}}
.card{{border-color:rgba({t['brilho']},.45);background:rgba({t['brilho']},.08)}}
.foot{{color:{t['apoio']}}} .foot img{{box-shadow:0 0 0 3px {OURO}}}
{sera_claro}
.branco{{background:{ab};color:{at}}} .branco .gold{{color:{ad}}} .branco p{{color:{aa}}} .branco p b{{color:{at}}} .branco .foot{{color:{aa}}} .branco .card{{color:{at}}}
"""


def fmt(t: str) -> str:
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t or "")
    t = re.sub(r"\*(.+?)\*", r'<span class="gold">\1</span>', t)
    return t.replace("|", "<br>")


CSS_EXTRA = f"""
@font-face{{font-family:Mont;font-weight:900;src:url({FONTES}/montserrat.ttf)}}
.foto{{position:absolute;inset:0;background-size:cover;background-position:center 25%}}
.foto:after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,10,12,0) 35%,rgba(10,10,12,.82) 68%,#0A0A0C 92%)}}
.seragrande{{position:absolute;left:50%;top:70px;transform:translateX(-50%);height:820px}}
.manchete{{position:absolute;left:70px;right:70px;bottom:150px;text-align:center;font-family:Mont;font-weight:900;font-size:84px;line-height:1.04;
  text-transform:uppercase;color:#fff;letter-spacing:-1px;text-shadow:0 6px 30px rgba(0,0,0,.6)}}
.manchete .gold{{color:#F5A623}}
.selo{{position:absolute;left:70px;top:60px;font:600 26px Inter;color:rgba(255,255,255,.75);letter-spacing:2px}}
.cont{{position:absolute;right:60px;top:52px;background:rgba(0,0,0,.45);color:#fff;font:700 24px Inter;padding:8px 16px;border-radius:20px}}
.simples .wrap{{top:170px}} .simples h1{{font-family:Mont;font-weight:900;font-size:74px;text-transform:none;letter-spacing:-1.5px;line-height:1.08}}
.simples p{{font-size:42px;line-height:1.45;color:#C9C9D0;margin-top:34px}} .simples.branco p{{color:#3a3a40}}
.simples .rot{{font:800 30px Inter;color:#F5A623;letter-spacing:4px;margin-bottom:26px;text-transform:uppercase}}
"""


def slide_capa_foto(s, i, n, arroba):
    img = s.get("imagem")
    fundo = f'<div class="foto" style="background-image:url({img})"></div>' if img else \
        f'<div class="bg"></div><img class="seragrande" src="{SERA}/{s.get("sera", "confiante")}.png">'
    return f"""<html><head><meta charset="utf-8"><style>{CSS}{CSS_EXTRA}</style></head>
<body>{fundo}<div class="selo">{arroba}</div><div class="cont">{i}/{n}</div>
<div class="manchete">{fmt(s.get("titulo", ""))}</div>
<div class="foot" style="justify-content:center"><div class="r"><span class="swipe">ARRASTA →</span></div></div></body></html>"""


def slide_html(s: dict, i: int, n: int, arroba: str, tema: str = None) -> str:
    tipo = s.get("tipo", "texto")
    if tipo == "capa_foto":
        return slide_capa_foto(s, i, n, arroba)
    if tipo == "simples":
        rot = f'<div class="rot">{s["rotulo"]}</div>' if s.get("rotulo") else ""
        cls = "simples" + (" branco" if s.get("fundo") == "branco" else "")
        swipe = '<span class="swipe">ARRASTA →</span>' if i < n else ""
        return f"""<html><head><meta charset="utf-8"><style>{CSS}{CSS_EXTRA}{css_tema(tema)}</style></head>
<body class="{cls}"><div class="bg"></div><div class="wrap">{rot}<h1>{fmt(s.get("titulo", ""))}</h1>{('<p>' + fmt(s["texto"]) + '</p>') if s.get("texto") else ''}</div>
<div class="foot"><div class="l"><img src="{ICONE}">{arroba}</div><div class="r">{i}/{n}{swipe}</div></div></body></html>"""
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
    return f"""<html><head><meta charset="utf-8"><style>{CSS}{css_tema(tema)}</style></head>
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
            tmp.write_text(slide_html(s, i, len(slides), arroba, spec.get("tema")), encoding="utf-8")
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
