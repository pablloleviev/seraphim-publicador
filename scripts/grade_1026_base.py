"""Base visual da grade 26/10–01/11 ("Sinal Vivo"): cores, CSS, textura e renderização HTML->JPG (Playwright)."""
import asyncio
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "previas" / "grade-2026-10-26"
TRAB = SAIDA / "_trabalho"
FONTES = (RAIZ / "motor/public/fontes").as_uri()
LOGO = (RAIZ / "carrossel/marca/icone.png").as_uri()
SOCIO = (TRAB / "socio_recorte.png").as_uri()
PABLLO = (TRAB / "pabllo_recorte_final.png").as_uri()
AF_LOGO = (RAIZ / "assets/autoflow/logo-icone.png").as_uri()
ARROBA = "@seraphimbr_"
INK, AZUL, ACIDO, LAV, MARFIM, CINZA, PAINEL = "#0B0D12", "#2F6BFF", "#C7FF3D", "#B8A6FF", "#F5F0E6", "#7D8492", "#171B24"

GRAO = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400'><filter id='n'>"
        "<feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' seed='7'/><feColorMatrix values='0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .9 0'/></filter>"
        "<rect width='100%' height='100%' filter='url(%23n)'/></svg>")
PAPEL = ("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='600' height='600'><filter id='p'>"
         "<feTurbulence type='fractalNoise' baseFrequency='.035 .09' numOctaves='5' seed='3'/><feColorMatrix values='0 0 0 0 .35  0 0 0 0 .28  0 0 0 0 .2  0 0 0 .55 0'/></filter>"
         "<rect width='100%' height='100%' filter='url(%23p)'/></svg>")

CSS = f"""
@font-face{{font-family:SH;font-weight:700;src:url({FONTES}/stack-sans-headline-latin-700-normal.woff2)}}
@font-face{{font-family:SH;font-weight:600;src:url({FONTES}/stack-sans-headline-latin-600-normal.woff2)}}
@font-face{{font-family:ST;font-weight:400;src:url({FONTES}/stack-sans-text-latin-400-normal.woff2)}}
@font-face{{font-family:ST;font-weight:500;src:url({FONTES}/stack-sans-text-latin-500-normal.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;overflow:hidden}}
body{{position:relative;font-family:ST;color:{MARFIM};background:{INK}}}
.abs{{position:absolute}}
.grao{{position:absolute;inset:0;background:url("{GRAO}");opacity:.16;mix-blend-mode:overlay;pointer-events:none;z-index:50}}
.papel{{position:absolute;inset:0;background:url("{PAPEL}");opacity:.32;mix-blend-mode:multiply;pointer-events:none}}
.marca{{position:absolute;display:flex;align-items:center;gap:14px;font:700 26px/1 SH;letter-spacing:5px;z-index:40}}
.marca img{{width:46px;height:46px;border-radius:12px}}
.arr{{position:absolute;font:500 24px ST;letter-spacing:1px;opacity:.7;z-index:40}}
.sh{{font-family:SH;font-weight:700}} .st{{font-family:ST}}
.az{{color:{AZUL}}} .lv{{color:{LAV}}} .ac{{color:{ACIDO}}}
"""


def pagina(corpo, alto=1350, extra_css="", fundo=INK, cor=MARFIM):
    return (f"<!doctype html><meta charset=utf-8><style>{CSS}body{{height:{alto}px;background:{fundo};color:{cor}}}{extra_css}</style>"
            f"<body>{corpo}<div class='grao'></div></body>")


def marca(cor=MARFIM, x=72, y=64, nome="SERAPHIM"):
    return f"<div class='marca' style='left:{x}px;top:{y}px;color:{cor}'><img src='{LOGO}'>{nome}</div>"


def realce(t, cls="az"):
    """*texto* vira destaque colorido."""
    import re
    return re.sub(r"\*([^*]+)\*", lambda m: f"<span class='{cls}'>{m.group(1)}</span>", t).replace("\n", "<br>")


async def renderizar(itens, qualidade=94):
    """itens: lista de (caminho_saida, html, alto). Grava JPG."""
    from playwright.async_api import async_playwright
    TRAB.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for i, (saida, html, alto) in enumerate(itens):
            tmp = TRAB / f"_tmp_{i}.html"
            tmp.write_text(html, encoding="utf-8")
            pg = await b.new_page(viewport={"width": 1080, "height": alto})
            await pg.goto(tmp.as_uri())
            await pg.evaluate("document.fonts.ready")
            await pg.wait_for_timeout(350)
            Path(saida).parent.mkdir(parents=True, exist_ok=True)
            await pg.screenshot(path=str(saida), type="jpeg", quality=qualidade)
            await pg.close()
            tmp.unlink()
            print("ok", Path(saida).relative_to(RAIZ))
        await b.close()


def rodar(itens):
    asyncio.run(renderizar(itens))
