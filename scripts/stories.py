"""Stories (1080x1920) no padrão Seraphim — cada um com composição própria.
Zonas seguras: topo 250px (barra do Instagram) e base 340px (campo de resposta).
"vazio_sticker": área deixada LIVRE para o adesivo interativo (enquete, perguntas, quiz) que é colocado no app;
na prévia "guia" essa área aparece tracejada só para orientar — a arte final sai limpa.
Uso: python scripts/stories.py 2026-10-19   -> stories/<data>/<n>-<nome>.jpg (+ _guia.jpg)
"""
import asyncio, io, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import estilo_ref as E
from estilo_ref import tit, neg, icone, moeda

R = E.RAIZ
EU = (R / "assets/pessoas/pabllo_recorte.png").as_uri()
SERA = {p: (R / f"motor/public/sera/{p}.png").as_uri() for p in ("confiante", "pensando", "feliz", "surpreso")}
LOGO = (R / "carrossel" / "marca" / "icone.png").as_uri()


def guia(x, y, w, h, rotulo):
    return (f'<div class="guia" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border:4px dashed rgba(255,255,255,.55);'
            f'border-radius:28px;display:flex;align-items:center;justify-content:center;font:800 30px Man8;color:rgba(255,255,255,.7);'
            f'letter-spacing:2px;text-align:center;padding:20px">{rotulo}</div>')


def assinatura(claro=False):
    c = "#111" if claro else "#F5F5F7"
    return (f'<div style="position:absolute;left:72px;top:150px;display:flex;align-items:center;gap:18px">'
            f'<img src="{LOGO}" style="width:64px;height:64px;border-radius:16px">'
            f'<div style="font:800 28px/1 Man8;color:{c};letter-spacing:1px">SERAPHIM<div style="font:500 22px Man5;opacity:.6;margin-top:6px">{E.ARROBA}</div></div></div>')


# ---------- composições ----------
def s_enquete_dupla(d):
    """pergunta grande + duas 'portas' 3D que representam as opções; adesivo de enquete fica entre elas"""
    a, b = d["opcoes"]
    corpo = (f'{assinatura()}<div class="fumaca" style="left:100px;top:700px;width:900px;height:800px;opacity:.3"></div>'
             f'<div style="position:absolute;left:72px;right:72px;top:330px"><div style="font:800 28px Man8;letter-spacing:5px;color:var(--a2)">{d.get("rotulo","")}</div>'
             f'<div style="font:700 92px/1.04 Sora;letter-spacing:-3px;margin-top:22px">{tit(d["pergunta"])}</div></div>'
             f'{moeda(d["icones"][0], 250, 110, 1080, -12)}{moeda(d["icones"][1], 250, 720, 1080, 12)}'
             f'<div style="position:absolute;left:60px;width:360px;top:1350px;text-align:center;font:800 32px/1.2 Man8">{a}</div>'
             f'<div style="position:absolute;right:60px;width:360px;top:1350px;text-align:center;font:800 32px/1.2 Man8">{b}</div>')
    return "escuro", corpo, guia(190, 1460, 700, 150, "ADESIVO DE ENQUETE AQUI")


def s_post_no_feed(d):
    """relacionamento: frase + a capa REAL do post do feed, inclinada como um cartão físico"""
    corpo = (f'{assinatura(True)}<div style="position:absolute;left:72px;right:72px;top:300px">'
             f'<div style="font:800 28px Man8;letter-spacing:5px;color:var(--ae)">{d.get("rotulo","")}</div>'
             f'<div style="font:700 84px/1.06 Sora;letter-spacing:-3px;color:#111;margin-top:22px">{tit(d["titulo"])}</div>'
             f'<div style="font:500 36px/1.4 Man5;color:#444;margin-top:26px">{neg(d.get("texto",""))}</div></div>'
             f'<img src="{d["capa"]}" style="position:absolute;left:280px;top:720px;width:520px;border-radius:26px;'
             f'transform:perspective(1400px) rotateY(-14deg) rotateZ(4deg);box-shadow:0 60px 90px rgba(40,30,10,.45),0 0 0 2px rgba(0,0,0,.06)">'
             f'<div style="position:absolute;left:72px;right:72px;top:1450px;text-align:center;font:800 36px/1.3 Man8;color:#111">'
             f'{d.get("cta","")}</div>')
    return "claro", corpo, ""


def s_caixa_pergunta(d):
    """pessoa + pergunta aberta; adesivo de perguntas embaixo"""
    corpo = (f'{assinatura()}<img src="{d.get("foto", EU)}" style="position:absolute;right:-140px;top:330px;height:1000px;opacity:.95">'
             f'<div style="position:absolute;left:0;right:0;top:900px;height:600px;background:linear-gradient(180deg,transparent,#08080a 55%)"></div>'
             f'<div style="position:absolute;left:72px;width:600px;top:420px"><div style="font:800 28px Man8;letter-spacing:5px;color:var(--a2)">{d.get("rotulo","")}</div>'
             f'<div style="font:700 84px/1.06 Sora;letter-spacing:-3px;margin-top:22px">{tit(d["pergunta"])}</div></div>')
    return "escuro", corpo, guia(140, 1180, 800, 300, "ADESIVO DE PERGUNTAS AQUI")


def s_quiz(d):
    corpo = (f'{assinatura()}<div class="fumaca" style="left:300px;top:500px;width:600px;height:600px;opacity:.3"></div>'
             f'<div style="position:absolute;left:0;right:0;top:330px;text-align:center;font:400 300px/1 Anton;color:var(--a)">?</div>'
             f'<div style="position:absolute;left:72px;right:72px;top:700px;text-align:center"><div style="font:800 28px Man8;letter-spacing:5px;color:var(--a2)">QUIZ</div>'
             f'<div style="font:700 76px/1.08 Sora;letter-spacing:-2px;margin-top:20px">{tit(d["pergunta"])}</div></div>')
    return "escuro", corpo, guia(140, 1150, 800, 380, "ADESIVO DE QUIZ AQUI")


def s_responda(d):
    """sem adesivo: CTA nativo 'responder ao story' (funciona em qualquer story, inclusive publicado pela API)"""
    corpo = (f'{assinatura(True)}<div style="position:absolute;left:72px;right:72px;top:420px">'
             f'<div style="font:800 28px Man8;letter-spacing:5px;color:var(--ae)">{d.get("rotulo","")}</div>'
             f'<div style="font:700 104px/1.0 Sora;letter-spacing:-4px;color:#111;margin-top:26px">{tit(d["titulo"])}</div>'
             f'<div style="font:500 38px/1.45 Man5;color:#444;margin-top:34px">{neg(d.get("texto",""))}</div></div>'
             f'<div style="position:absolute;left:72px;right:72px;bottom:380px;display:flex;align-items:center;gap:20px;font:800 34px Man8;color:#111">'
             f'<div style="width:70px;height:70px;border-radius:50%;background:var(--a);display:flex;align-items:center;justify-content:center">{icone("send", "#111", 36, 2.2)}</div>'
             f'{d.get("cta","Responde aqui embaixo")} ↓</div>')
    return "claro", corpo, ""


TIPOS = {"enquete_dupla": s_enquete_dupla, "post_no_feed": s_post_no_feed, "caixa_pergunta": s_caixa_pergunta, "quiz": s_quiz, "responda": s_responda}


def html(fundo, corpo, extra, paleta):
    pal = E.PALETAS.get(paleta, E.PALETAS["ouro"])
    css = E.CSS + ":root{--a:%s;--a2:%s;--ae:%s} body{height:1920px}" % (pal["a"], pal["a2"], pal["ae"])
    return f'<html><head><meta charset="utf-8"><style>{css}</style></head><body class="{fundo}">{corpo}{extra}</body></html>'


async def render(stories, out: Path):
    from playwright.async_api import async_playwright
    from PIL import Image
    out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        nav = await p.chromium.launch()
        for d in stories:
            fundo, corpo, g = TIPOS[d["tipo"]](d)
            for sufixo, extra in (("", ""), ("_guia", g)):
                if sufixo and not g:
                    continue
                pg = await nav.new_page(viewport={"width": 1080, "height": 1920})
                tmp = out / "_tmp.html"; tmp.write_text(html(fundo, corpo, extra, d.get("paleta", "ouro")), encoding="utf-8")
                await pg.goto(tmp.as_uri()); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(250)
                Image.open(io.BytesIO(await pg.screenshot())).convert("RGB").save(out / f'{d["id"]}{sufixo}.jpg', quality=93)
                await pg.close(); tmp.unlink()
        await nav.close()


if __name__ == "__main__":
    dia = sys.argv[1]
    plano = json.loads((R / "stories" / "plano.json").read_text(encoding="utf-8"))
    sts = [s for s in plano["stories"] if s["dia"] == dia]
    for s in sts:
        if s.get("capa_post"):
            s["capa"] = (R / s["capa_post"]).as_uri()
        if s.get("foto") == "SERA_PENSANDO":
            s["foto"] = SERA["pensando"]
    asyncio.run(render(sts, R / "stories" / dia))
    print(len(sts), "stories ->", R / "stories" / dia)
