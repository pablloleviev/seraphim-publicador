"""
Carrossel no estilo de referência (Blue Ocean), em preto + dourado. Custo zero de tokens: HTML -> Playwright.
Tipos de slide:
  capa      : pessoa recortada + blocos 3D de vidro com ícones + manchete condensada em 2 cores
  abertura  : título com destaque + texto com negritos + moedas 3D com ícones
  topico    : título com destaque + cartão 3D de vidro (número + curva) + parágrafos com negritos
  fecho     : título + texto + 2 cartões com borda
Fundos alternam escuro (preto/grafite com brilho dourado) e claro (papel off-white).
Texto: *palavra* = destaque dourado no título; **trecho** = negrito no corpo.
Uso: python scripts/estilo_ref.py exemplo   -> testes/estilo_ref/slide-NN.jpg (1080x1350) e tiktok/ (1080x1920)
"""
import asyncio, io, json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
F = (RAIZ / "carrossel" / "fontes").as_uri()
ICO = RAIZ / "carrossel" / "icones"
LOGO = (RAIZ / "carrossel" / "marca" / "icone.png").as_uri()
OURO, OURO2 = "#F5A623", "#FFD27A"
sys.path.insert(0, str(Path(__file__).parent))
try:
    from marca import ARROBA
except Exception:
    ARROBA = "@seraphimbr_"

CSS = f"""
@font-face{{font-family:Anton;src:url({F}/anton.ttf)}}
@font-face{{font-family:Sora;src:url({F}/sora-700.woff2)}}
@font-face{{font-family:Man5;src:url({F}/manrope-500.woff2)}}
@font-face{{font-family:Man8;src:url({F}/manrope-800.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;position:relative;overflow:hidden;font-family:Man5}}
.escuro{{background:radial-gradient(120% 70% at 85% 100%,#3a2606 0%,rgba(58,38,6,0) 55%),
        radial-gradient(90% 60% at 0% 0%,#1c1c22 0%,#08080a 70%);color:#F5F5F7}}
.claro{{background:radial-gradient(80% 60% at 50% 40%,#fbfaf7,#ecebe6);color:#111}}
.claro::after{{content:"";position:absolute;inset:0;opacity:.35;mix-blend-mode:multiply;
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence baseFrequency='.8' numOctaves='2'/></filter><rect width='100%' height='100%' filter='url(%23n)' opacity='.25'/></svg>")}}
.topo{{position:absolute;left:72px;right:72px;top:64px;display:flex;justify-content:space-between;align-items:center;z-index:5}}
.marca{{font:800 26px/0.95 Man8;letter-spacing:1px}}
.topo img{{width:58px;height:58px;border-radius:14px}}
.rodape{{position:absolute;left:72px;right:72px;bottom:56px;display:flex;justify-content:space-between;align-items:center;z-index:5;font:800 20px Man8;letter-spacing:1px}}
.pontos{{position:absolute;left:0;right:0;bottom:62px;display:flex;justify-content:center;gap:12px;z-index:5}}
.pontos i{{width:11px;height:11px;border-radius:50%;background:currentColor;opacity:.25}}
.pontos i.on{{opacity:.9}}
h1{{font:700 76px/1.08 Sora;letter-spacing:-1.5px}}
.d{{color:{OURO}}} .claro h1 .d{{color:#C77F00}}
.corpo p{{font:500 36px/1.38 Man5;margin-top:30px}}
.corpo b{{font-family:Man8;font-weight:800}}
.vidro{{position:relative;border-radius:34px;padding:34px 40px;overflow:hidden;
  background:linear-gradient(135deg,#2b2b31 0%,#141418 55%,#24180a 100%);
  box-shadow:0 40px 80px rgba(0,0,0,.55),inset 0 2px 0 rgba(255,255,255,.18),inset 0 -2px 0 rgba(0,0,0,.6);
  border:1.5px solid rgba(255,210,122,.35);transform:perspective(1200px) rotateX(10deg) rotateY(-8deg)}}
.vidro::before{{content:"";position:absolute;inset:-40% -10% auto -10%;height:70%;
  background:linear-gradient(180deg,rgba(255,255,255,.22),rgba(255,255,255,0));transform:rotate(-8deg)}}
.claro .vidro{{box-shadow:0 40px 70px rgba(80,60,20,.35),inset 0 2px 0 rgba(255,255,255,.25)}}
.num{{font:400 108px/1 Anton;color:#fff;letter-spacing:1px;position:relative;
  background:linear-gradient(180deg,#fff 30%,{OURO2});-webkit-background-clip:text;color:transparent}}
.rot{{font:800 22px Man8;color:{OURO2};letter-spacing:3px;position:relative}}
.moeda{{width:230px;height:230px;border-radius:50%;display:flex;align-items:center;justify-content:center;
  background:radial-gradient(circle at 32% 28%,#fff3cf 0%,{OURO2} 18%,{OURO} 45%,#8a5300 80%,#4a2c00 100%);
  box-shadow:0 30px 60px rgba(0,0,0,.6),inset -10px -14px 30px rgba(0,0,0,.45),inset 10px 12px 26px rgba(255,255,255,.5);
  position:absolute}}
.moeda svg{{filter:drop-shadow(0 4px 2px rgba(255,255,255,.4)) drop-shadow(0 -3px 2px rgba(0,0,0,.45))}}
.fumaca{{position:absolute;border-radius:50%;filter:blur(60px);background:{OURO};opacity:.18}}
.cartao{{flex:1;border:2.5px solid {OURO};border-radius:22px;padding:30px;background:rgba(245,166,35,.06);
  box-shadow:0 0 50px rgba(245,166,35,.18),inset 0 0 30px rgba(245,166,35,.08)}}
.cartao .bolinha{{width:30px;height:30px;border-radius:50%;border:3px solid {OURO};display:flex;align-items:center;justify-content:center;margin-bottom:22px}}
.cartao .bolinha:after{{content:"";width:14px;height:14px;border-radius:50%;background:{OURO}}}
.cartao div{{font:500 30px/1.35 Man5}} .cartao b{{font-family:Man8}}
"""


def icone(nome, cor="#3a2300", tam=120, traco=1.8):
    f = ICO / f"{nome}.svg"
    if not f.exists():
        return ""
    s = f.read_text()
    return (s.replace('width="24"', f'width="{tam}"').replace('height="24"', f'height="{tam}"')
             .replace('stroke="currentColor"', f'stroke="{cor}"').replace('stroke-width="2"', f'stroke-width="{traco}"'))


def tit(t):
    return re.sub(r"\*(.+?)\*", r'<span class="d">\1</span>', t)


def neg(t):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


def moldura(corpo, n, total, tema):
    pts = "".join(f'<i class="{"on" if i == n - 1 else ""}"></i>' for i in range(total))
    return (f'<div class="topo"><div class="marca">SERA<br>PHIM</div><img src="{LOGO}"></div>{corpo}'
            f'<div class="pontos">{pts}</div><div class="rodape"><span>{ARROBA}</span><span>ARRASTE PARA O LADO ›</span></div>')


def curva():
    return ('<svg width="300" height="150" viewBox="0 0 300 150" style="position:absolute;right:26px;bottom:24px">'
            f'<defs><linearGradient id="g" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="{OURO}" stop-opacity=".45"/>'
            f'<stop offset="1" stop-color="{OURO}" stop-opacity="0"/></linearGradient></defs>'
            '<path d="M0 130 C70 128 110 110 150 80 S240 20 280 18 V150 H0Z" fill="url(#g)"/>'
            '<path d="M0 130 C70 128 110 110 150 80 S240 20 280 18" fill="none" stroke="#fff" stroke-width="5"/>'
            f'<circle cx="280" cy="18" r="13" fill="#111" stroke="#fff" stroke-width="5"/></svg>')


def s_capa(d, n, T):
    tiles = ""
    for (ic, x, y, r, s) in d.get("blocos", [("workflow", 40, 300, -14, 230), ("message-circle", 800, 220, 12, 210), ("bar-chart-3", 820, 640, -8, 170)]):
        tiles += (f'<div class="vidro" style="position:absolute;left:{x}px;top:{y}px;width:{s}px;height:{s}px;padding:0;display:flex;'
                  f'align-items:center;justify-content:center;transform:perspective(900px) rotate({r}deg) rotateY({-r * 2}deg);z-index:3">'
                  f'{icone(ic, OURO2, int(s * .5), 1.6)}</div>')
    corpo = (f'<div class="fumaca" style="left:200px;top:260px;width:700px;height:700px;opacity:.28"></div>'
             f'<img src="{d["foto"]}" style="position:absolute;left:50%;transform:translateX(-50%);bottom:250px;height:1000px;z-index:2">'
             f'{tiles}<div style="position:absolute;left:0;right:0;bottom:0;height:620px;z-index:4;'
             f'background:linear-gradient(180deg,rgba(8,8,10,0),#08080a 55%)"></div>'
             f'<div style="position:absolute;left:60px;right:60px;bottom:150px;z-index:5;text-align:center">'
             f'<div style="font:800 34px Man8;letter-spacing:2px;margin-bottom:14px">{d["linha"]}</div>'
             f'<div style="font:400 118px/0.98 Anton;text-transform:uppercase">{tit(d["titulo"]).replace("<br>", "<br>")}</div></div>')
    return "escuro", moldura(corpo, n, T, "escuro")


def s_abertura(d, n, T):
    ps = "".join(f"<p>{neg(p)}</p>" for p in d["textos"])
    moedas = ""
    for i, ic in enumerate(d.get("icones", ["brain", "shield-check", "trending-up", "database"])):
        x, y = [(150, 900), (420, 960), (690, 900), (300, 1120)][i % 4]
        moedas += f'<div class="moeda" style="left:{x}px;top:{y}px;transform:perspective(700px) rotateX(18deg) rotate({[-10, 6, 12, -4][i % 4]}deg)">{icone(ic, "#3a2300", 110, 1.8)}</div>'
    corpo = (f'<div class="fumaca" style="left:250px;top:850px;width:600px;height:500px"></div>'
             f'<div style="position:absolute;left:72px;right:72px;top:210px"><h1>{tit(d["titulo"])}</h1><div class="corpo">{ps}</div></div>{moedas}')
    return d.get("fundo", "escuro"), moldura(corpo, n, T, "")


def s_topico(d, n, T):
    ps = "".join(f"<p>{neg(p)}</p>" for p in d["textos"])
    corpo = (f'<div style="position:absolute;left:72px;right:72px;top:200px"><h1>{tit(d["titulo"])}</h1>'
             f'<div class="vidro" style="width:640px;height:250px;margin:44px auto 10px">'
             f'<div class="rot">{d["rotulo"]}</div><div class="num" style="margin-top:14px">{d["numero"]}</div>{curva()}</div>'
             f'<div class="corpo">{ps}</div></div>')
    return d.get("fundo", "claro"), moldura(corpo, n, T, "")


def s_fecho(d, n, T):
    ps = "".join(f"<p>{neg(p)}</p>" for p in d["textos"])
    cs = "".join(f'<div class="cartao"><div class="bolinha"></div><div>{neg(c)}</div></div>' for c in d["cartoes"])
    corpo = (f'<div style="position:absolute;left:72px;right:72px;top:300px"><h1 style="font-size:66px">{tit(d["titulo"])}</h1>'
             f'<div class="corpo">{ps}</div><div style="display:flex;gap:30px;margin-top:70px">{cs}</div></div>')
    return d.get("fundo", "escuro"), moldura(corpo, n, T, "")




def moeda(ic, tam=230, x=0, y=0, r=0):
    return (f'<div class="moeda" style="left:{x}px;top:{y}px;width:{tam}px;height:{tam}px;transform:perspective(700px) rotateX(16deg) rotate({r}deg)">'
            f'{icone(ic, "#3a2300", int(tam * .48), 1.8)}</div>')


def s_capa_objeto(d, n, T):
    """capa sem pessoa: objeto 3D gigante (moeda/vidro) com anel de luz e fumaça"""
    ic = d.get("icone", "zap")
    if d.get("material") == "vidro":
        obj = (f'<div class="vidro" style="position:absolute;left:290px;top:190px;width:500px;height:500px;border-radius:110px;padding:0;display:flex;'
               f'align-items:center;justify-content:center;transform:perspective(900px) rotateY(-16deg) rotateX(10deg)">{icone(ic, OURO2, 270, 1.4)}</div>')
    else:
        obj = moeda(ic, 500, 290, 180, -8)
    corpo = (f'<div class="fumaca" style="left:140px;top:200px;width:800px;height:700px;opacity:.32"></div>'
             f'<div style="position:absolute;left:190px;top:600px;width:700px;height:200px;border-radius:50%;border:3px solid rgba(245,166,35,.45);'
             f'box-shadow:0 0 90px rgba(245,166,35,.45);transform:rotateX(60deg)"></div>{obj}'
             f'<div style="position:absolute;left:60px;right:60px;bottom:150px;text-align:center">'
             f'<div style="font:800 34px Man8;letter-spacing:4px;margin-bottom:16px;color:{OURO2}">{d.get("linha", "")}</div>'
             f'<div style="font:400 120px/0.98 Anton;text-transform:uppercase">{tit(d["titulo"])}</div></div>')
    return "escuro", moldura(corpo, n, T, "")


def s_capa_numero(d, n, T):
    corpo = (f'<div class="fumaca" style="left:200px;top:300px;width:700px;height:600px;opacity:.3"></div>'
             f'<div style="position:absolute;left:0;right:0;top:170px;text-align:center;font:400 620px/1 Anton;'
             f'background:linear-gradient(180deg,#fff 15%,{OURO2} 55%,{OURO});-webkit-background-clip:text;color:transparent;'
             f'filter:drop-shadow(0 0 70px rgba(245,166,35,.4))">{d["numero"]}</div>'
             f'<div style="position:absolute;left:60px;right:60px;bottom:160px;text-align:center">'
             f'<div style="font:400 104px/1 Anton;text-transform:uppercase">{tit(d["titulo"])}</div></div>')
    return "escuro", moldura(corpo, n, T, "")


def s_verbete(d, n, T):
    """objeto 3D + palavra + definição + exemplo num cartão de vidro"""
    corpo = (f'<div class="fumaca" style="left:450px;top:700px;width:600px;height:600px"></div>'
             f'{moeda(d.get("icone", "book"), 400, 600, 830, 10)}'
             f'<div style="position:absolute;left:72px;right:72px;top:210px">'
             f'<div style="font:800 26px Man8;letter-spacing:5px;opacity:.6">{d.get("rotulo", "")}</div>'
             f'<h1 style="font-size:120px;margin-top:20px">{tit(d["titulo"])}</h1>'
             f'<div class="corpo"><p style="font-size:44px;max-width:640px">{neg(d["texto"])}</p></div>'
             f'<div class="vidro" style="margin-top:70px;transform:perspective(1200px) rotateX(6deg) rotateY(-4deg)">'
             f'<div class="rot">NA PRÁTICA</div><div style="position:relative;font:500 38px/1.35 Man5;color:#fff;margin-top:14px">{neg(d["exemplo"])}</div></div></div>')
    return d.get("fundo", "escuro"), moldura(corpo, n, T, "")


def s_lista(d, n, T):
    itens = ""
    for i, it in enumerate(d["itens"]):
        t, x = (it if isinstance(it, (list, tuple)) else (it, ""))
        itens += (f'<div class="vidro" style="display:flex;gap:34px;align-items:center;margin-top:28px;padding:30px 40px;'
                  f'transform:perspective(1200px) rotateY({-5 if i % 2 else 5}deg)">'
                  f'<div style="position:relative;font:400 84px/1 Anton;color:{OURO};width:70px">{d.get("marcador") or i + 1}</div>'
                  f'<div style="position:relative"><div style="font:800 42px/1.15 Man8;color:#fff">{t}</div>'
                  f'{f"<div style=font:500 30px/1.35 Man5;color:#cfcfd4;margin-top:8px>{x}</div>" if x else ""}</div></div>')
    corpo = (f'<div style="position:absolute;left:72px;right:72px;top:200px"><div style="font:800 26px Man8;letter-spacing:5px;opacity:.6">{d.get("rotulo", "")}</div>'
             f'<h1 style="margin:16px 0 30px">{tit(d["titulo"])}</h1>{itens}</div>')
    return d.get("fundo", "escuro"), moldura(corpo, n, T, "")


def s_contraste(d, n, T):
    a, b = d["antes"], d["depois"]
    corpo = (f'<div style="position:absolute;left:0;right:0;top:0;height:660px;background:#ecebe6;color:#222">'
             f'<div style="position:absolute;left:72px;top:200px;font:800 26px Man8;letter-spacing:5px;color:#8a857a">{d.get("rotulo_a", "ANTES")}</div>'
             f'<div style="position:absolute;left:72px;right:72px;top:250px;font:700 66px/1.12 Sora;text-decoration:line-through;text-decoration-color:{OURO};text-decoration-thickness:6px">{a}</div></div>'
             f'<div style="position:absolute;left:0;right:0;top:655px;height:10px;background:{OURO};box-shadow:0 0 40px {OURO}"></div>'
             f'<div style="position:absolute;left:72px;right:72px;top:740px"><div style="font:800 26px Man8;letter-spacing:5px;color:{OURO2}">{d.get("rotulo_b", "DEPOIS")}</div>'
             f'<h1 style="margin-top:20px">{tit(b)}</h1><div class="corpo"><p>{neg(d.get("texto", ""))}</p></div></div>')
    return "escuro", moldura(corpo, n, T, "")


def s_citacao(d, n, T):
    corpo = (f'<div class="fumaca" style="left:0;top:300px;width:600px;height:600px"></div>'
             f'<div style="position:absolute;left:72px;right:72px;top:50%;transform:translateY(-55%)"><div style="font:400 300px/0.6 Anton;color:{OURO};opacity:.4">“</div>'
             f'<h1 style="font-size:96px;margin-top:40px">{tit(d["titulo"])}</h1>'
             f'<div style="width:140px;height:5px;background:{OURO};margin:50px 0 30px"></div>'
             f'<div style="font:500 34px Man5;opacity:.75">{neg(d.get("texto", ""))}</div></div>')
    return d.get("fundo", "escuro"), moldura(corpo, n, T, "")


def s_cta(d, n, T):
    foto = d.get("foto")
    img = (f'<img src="{foto}" style="position:absolute;right:-60px;bottom:0;height:900px;z-index:1">'
           f'<div style="position:absolute;left:0;right:0;bottom:0;height:500px;z-index:2;background:linear-gradient(180deg,rgba(8,8,10,0),#08080a 70%)"></div>') if foto else ""
    corpo = (f'<div class="fumaca" style="left:400px;top:500px;width:700px;height:700px;opacity:.28"></div>{img}'
             f'<div style="position:absolute;left:72px;right:{380 if foto else 72}px;top:260px;z-index:3"><h1 style="font-size:84px">{tit(d["titulo"])}</h1>'
             f'<div class="corpo"><p>{neg(d.get("texto", ""))}</p></div>'
             f'<div style="display:inline-block;margin-top:60px;padding:24px 38px;border-radius:999px;background:{OURO};color:#111;font:800 34px Man8;'
             f'box-shadow:0 0 50px rgba(245,166,35,.5)">{d.get("botao", "SIGA " + ARROBA.upper())}</div></div>')
    return "escuro", moldura(corpo, n, T, "")


TIPOS = {"capa": s_capa, "abertura": s_abertura, "topico": s_topico, "fecho": s_fecho, "capa_objeto": s_capa_objeto,
         "capa_numero": s_capa_numero, "verbete": s_verbete, "lista": s_lista, "contraste": s_contraste, "citacao": s_citacao, "cta": s_cta}


EXEMPLO = [
    {"tipo": "capa", "foto": (RAIZ / "assets/pessoas/pabllo_recorte.png").as_uri(), "linha": "AS TAREFAS QUE",
     "titulo": "Roubam *horas*<br>da sua *empresa*"},
    {"tipo": "abertura", "titulo": "Toda empresa tem *trabalho invisível*",
     "textos": ["São tarefas que ninguém vê, mas que **todo mundo faz, todo dia**.",
                "Elas parecem pequenas. Somadas, viram **horas que não voltam**.",
                "Separamos **quatro delas** — e como a tecnologia resolve cada uma:"],
     "icones": ["repeat", "file-text", "message-circle", "alarm-clock"]},
    {"tipo": "topico", "fundo": "claro", "titulo": "*Copiar* dados entre sistemas", "rotulo": "DE 3 SISTEMAS PARA APENAS", "numero": "1 SISTEMA",
     "textos": ["O pedido entra no WhatsApp, vai para a planilha e depois para o financeiro. **Três vezes o mesmo dado.**",
                "Com **integração**, ele entra uma vez e aparece em todo lugar.",
                "Menos digitação, **menos erro**."]},
    {"tipo": "topico", "fundo": "escuro", "titulo": "Responder as *mesmas perguntas*", "rotulo": "ATENDIMENTO NO AR", "numero": "24 H",
     "textos": ["Horário, preço, endereço, status do pedido. **Sempre as mesmas dúvidas.**",
                "Um **atendimento automático** responde na hora — e passa para uma pessoa quando precisa.",
                "Sua equipe fica com o que **exige gente**."]},
    {"tipo": "topico", "fundo": "claro", "titulo": "Montar *relatório* na mão", "rotulo": "RELATÓRIO PRONTO EM", "numero": "1 CLIQUE",
     "textos": ["Toda sexta alguém junta números de vários lugares. **Uma tarde inteira perdida.**",
                "Com os dados conectados, o **painel se atualiza sozinho**.",
                "Você decide olhando o número **de hoje**, não o do mês passado."]},
    {"tipo": "fecho", "fundo": "escuro", "titulo": "Automatizar não é sobre *tecnologia*. É sobre *tempo*.",
     "textos": ["Antes de qualquer sistema, a pergunta certa é: **onde sua equipe perde mais tempo?**"],
     "cartoes": ["Mapear as tarefas que **se repetem todo dia**", "Resolver primeiro a que **mais custa caro**"]},
]


def html(fundo, corpo, alto):
    extra = "" if alto == 1350 else f"body{{height:{alto}px}} .wrap{{position:absolute;left:0;top:285px;width:1080px;height:1350px}}"
    inner = corpo if alto == 1350 else f'<div class="wrap">{corpo}</div>'
    return f'<html><head><meta charset="utf-8"><style>{CSS}{extra}</style></head><body class="{fundo}">{inner}</body></html>'


async def render(slides, out: Path):
    from playwright.async_api import async_playwright
    from PIL import Image
    T = len(slides)
    async with async_playwright() as p:
        nav = await p.chromium.launch()
        for rede, alto in (("instagram", 1350), ("tiktok", 1920)):
            (out / rede).mkdir(parents=True, exist_ok=True)
            for k, d in enumerate(slides):
                fundo, corpo = TIPOS[d["tipo"]](d, k + 1, T)
                pg = await nav.new_page(viewport={"width": 1080, "height": alto})
                tmp = out / "_tmp.html"; tmp.write_text(html(fundo, corpo, alto), encoding="utf-8")
                await pg.goto(tmp.as_uri()); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(250)
                Image.open(io.BytesIO(await pg.screenshot())).convert("RGB").save(out / rede / f"slide-{k + 1:02d}.jpg", quality=93)
                await pg.close(); tmp.unlink()
        await nav.close()


if __name__ == "__main__":
    if sys.argv[1:2] == ["exemplo"]:
        asyncio.run(render(EXEMPLO, RAIZ / "testes" / "estilo_ref"))
    elif len(sys.argv) == 3:
        asyncio.run(render(json.loads(Path(sys.argv[1]).read_text()), Path(sys.argv[2])))
