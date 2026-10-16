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
import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from marca import ARROBA, USUARIO, INSTAGRAM_URL
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
    topo, rod = _chrome(i, n, arroba)
    rot = f'<div style="position:absolute;left:70px;bottom:{(560 if len(s.get("titulo","")) > 40 else 500)}px;z-index:5"><div class="selon">{s["rotulo"]}</div></div>' if s.get("rotulo") else ""
    return f"""<html><head><meta charset="utf-8"><style>{CSS}{CSS_EXTRA}{CSS_V2}</style></head>
<body class="v2">{fundo}{topo}{rot}<div class="manchete" style="text-align:left;font-size:92px;left:70px;right:70px;bottom:170px;z-index:4">{fmt(s.get("titulo", ""))}</div>{rod}</body></html>"""



# ---------------- layouts "nível Blue Ocean / Gene" (15/10/2026) ----------------
CSS_V2 = f"""
.v2 .wrap,.v2 .foot,.v2 .tag{{display:none}}
.v2 .topo{{position:absolute;left:70px;right:70px;top:54px;display:flex;align-items:center;justify-content:space-between;z-index:5}}
.v2 .marca{{display:flex;align-items:center;gap:14px;font:800 24px Inter;letter-spacing:5px;color:#F5F5F7}}
.v2 .marca img{{width:42px;height:42px;border-radius:50%;box-shadow:0 0 0 3px #F5A623}}
.v2 .dots2{{display:flex;gap:10px}} .v2 .dots2 i{{width:14px;height:14px;border-radius:50%;background:rgba(255,255,255,.22)}}
.v2 .dots2 i.on{{background:#F5A623;width:38px;border-radius:8px}}
.v2 .rodape{{position:absolute;left:70px;right:70px;bottom:52px;display:flex;align-items:center;justify-content:space-between;font:500 26px Inter;color:#A1A1AA;z-index:5}}
.v2 .seta{{width:84px;height:84px;border-radius:50%;background:#F5A623;color:#0A0A0C;display:flex;align-items:center;justify-content:center;font:800 44px Inter;box-shadow:0 10px 30px rgba(245,166,35,.35)}}
.v2.light{{background:#F4F1EA;color:#0A0A0C}} .v2.light .marca{{color:#0A0A0C}} .v2.light .rodape{{color:#55555c}}
.v2.light .dots2 i{{background:rgba(0,0,0,.18)}} .v2.light .bg{{background:radial-gradient(circle at 85% 10%,rgba(245,166,35,.22),transparent 45%)}} .v2.light .dots{{opacity:.25}}
.v2 .corpo{{position:absolute;left:70px;right:70px;top:170px;z-index:4}}
.v2 .corpo.c{{top:140px;bottom:150px;display:flex;flex-direction:column;justify-content:center}}
.v2 .rot{{font:800 28px Inter;letter-spacing:5px;color:#F5A623;text-transform:uppercase;margin-bottom:22px}}
.v2.light .rot{{color:#B86E00}}
.v2 h2{{font-family:Anton;font-weight:400;text-transform:uppercase;font-size:98px;line-height:1.03;letter-spacing:1px}}
.v2 h2 .gold{{color:#F5A623}} .v2.light h2 .gold{{color:#B86E00}}
.v2 .sub{{font:500 38px/1.4 Inter;color:#A1A1AA;margin-top:26px;max-width:900px}} .v2.light .sub{{color:#4a4a52}} .v2 .sub b{{color:#fff}} .v2.light .sub b{{color:#0A0A0C}}
/* pílulas */
.pil{{display:flex;align-items:center;gap:26px;background:#15151a;border:2px solid rgba(245,166,35,.35);border-radius:80px;padding:28px 44px 28px 28px;margin-top:28px;box-shadow:0 18px 50px rgba(0,0,0,.45);font:800 44px/1.2 Inter}}
.pil .n{{flex:0 0 96px;height:96px;border-radius:50%;background:#F5A623;color:#0A0A0C;display:flex;align-items:center;justify-content:center;font:400 46px Anton}}
.light .pil{{background:#fff;border-color:rgba(10,10,12,.12);box-shadow:0 18px 50px rgba(0,0,0,.12)}}
/* card de produto */
.cardp{{background:#16161b;border:2px solid #2a2a31;border-radius:44px;padding:48px;margin-top:40px;box-shadow:0 40px 100px rgba(0,0,0,.55)}}
.light .cardp{{background:#fff;border-color:#e4e0d6;box-shadow:0 30px 80px rgba(0,0,0,.14)}}
.cardp .ic{{width:120px;height:120px;border-radius:32px;background:#F5A623;display:flex;align-items:center;justify-content:center;font-size:68px;margin-bottom:30px}}
.cardp h3{{font:800 54px/1.12 Inter;margin-bottom:18px}} .cardp p{{font:500 38px/1.42 Inter;color:#A1A1AA;margin:0;max-width:none}} .light .cardp p{{color:#4a4a52}}
.chips{{display:flex;flex-wrap:wrap;gap:16px;margin-top:30px}} .chips span{{font:800 30px Inter;padding:14px 28px;border-radius:40px;background:rgba(245,166,35,.14);color:#F5A623;border:2px solid rgba(245,166,35,.4)}}
.light .chips span{{color:#8a5200;background:rgba(245,166,35,.2)}}
/* celular + whatsapp */
.cel{{position:absolute;left:50%;transform:translateX(-50%);top:440px;width:640px;height:730px;border-radius:70px 70px 0 0;background:#0b0b0e;border:10px solid #2b2b31;border-bottom:none;overflow:hidden;box-shadow:0 40px 120px rgba(0,0,0,.6)}}
.cel .cab{{height:110px;background:#1f2c34;display:flex;align-items:center;gap:20px;padding:0 30px;color:#fff;font:800 32px Inter}}
.cel .cab i{{width:64px;height:64px;border-radius:50%;background:#F5A623;display:inline-block}}
.cel .chat{{padding:26px 24px;background:#0b141a;height:620px;display:flex;flex-direction:column;gap:18px}}
.bol{{max-width:78%;padding:18px 24px;border-radius:26px;font:500 33px/1.32 Inter;color:#e9edef}}
.bol.c{{align-self:flex-start;background:#202c33;border-top-left-radius:6px}} .bol.e{{align-self:flex-end;background:#005c4b;border-top-right-radius:6px}}
.bol small{{display:block;text-align:right;font-size:22px;color:rgba(255,255,255,.5);margin-top:6px}}
/* comparação */
.cmp{{display:flex;gap:26px;margin-top:44px}}
.cmp .col{{flex:1;border-radius:40px;padding:40px 34px;box-shadow:0 30px 80px rgba(0,0,0,.45)}}
.cmp .ruim{{background:#1a1114;border:2px solid rgba(229,72,77,.5)}} .cmp .bom{{background:#171309;border:2px solid rgba(245,166,35,.6)}}
.light .cmp .ruim{{background:#fff1f1}} .light .cmp .bom{{background:#fff7e6}}
.cmp h4{{font:800 30px Inter;letter-spacing:4px;text-transform:uppercase;margin-bottom:26px}} .cmp .ruim h4{{color:#ff6b6f}} .cmp .bom h4{{color:#F5A623}} .light .cmp .bom h4{{color:#B86E00}}
.cmp li{{list-style:none;font:500 40px/1.3 Inter;padding:24px 0 24px 62px;position:relative;border-top:1px solid rgba(255,255,255,.1)}} .light .cmp li{{border-color:rgba(0,0,0,.1)}}
.cmp li:first-of-type{{border-top:none}}
.cmp .ruim li:before{{content:"✕";position:absolute;left:0;color:#ff6b6f;font-weight:800}} .cmp .bom li:before{{content:"✓";position:absolute;left:0;color:#F5A623;font-weight:800}}
.light .cmp .bom li:before{{color:#B86E00}}
/* passos */
.pas{{position:relative;margin-top:36px;padding-left:130px}}
.pas:before{{content:"";position:absolute;left:49px;top:30px;bottom:30px;width:6px;background:linear-gradient(#F5A623,rgba(245,166,35,.15));border-radius:4px}}
.pas .p{{position:relative;margin-bottom:46px;font:500 42px/1.3 Inter}} .pas .p b{{display:block;font:800 54px/1.15 Inter;margin-bottom:6px}}
.pas .p i{{position:absolute;left:-130px;top:-4px;width:104px;height:104px;border-radius:50%;background:#0A0A0C;border:6px solid #F5A623;color:#F5A623;display:flex;align-items:center;justify-content:center;font:400 52px Anton;font-style:normal}}
.light .pas .p i{{background:#F4F1EA;color:#B86E00;border-color:#B86E00}}
/* citação */
.asp{{font:400 520px/0.7 Anton;color:#F5A623;opacity:.9;margin:20px 0 -30px}}
.cit{{font:800 74px/1.14 Inter;letter-spacing:-1px}} .cit .gold{{color:#F5A623}} .light .cit .gold{{color:#B86E00}}
/* notícia */
.selon{{display:inline-block;background:#F5A623;color:#0A0A0C;font:800 30px Inter;letter-spacing:3px;padding:14px 28px;border-radius:12px;text-transform:uppercase}}
.rec{{position:absolute;left:70px;right:70px;background:#F4F1EA;color:#0A0A0C;border-radius:14px;padding:26px 32px;box-shadow:0 24px 60px rgba(0,0,0,.55);font:800 38px/1.18 Inter}}
.rec small{{display:block;font:600 24px Inter;color:#6a6a72;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px}}
/* perfil */
.perf{{background:#fff;color:#0A0A0C;border-radius:44px;padding:46px;margin-top:44px;box-shadow:0 40px 110px rgba(0,0,0,.55)}}
.perf .l1{{display:flex;align-items:center;gap:30px}} .perf .av{{width:150px;height:150px;border-radius:50%;box-shadow:0 0 0 6px #F5A623;background:#0A0A0C}}
.perf .nm{{font:800 44px Inter}} .perf .bio{{font:500 33px/1.35 Inter;color:#3a3a40;margin-top:26px}}
.perf .lnk{{margin-top:26px;display:inline-block;font:800 36px Inter;color:#0A56D6;background:rgba(10,86,214,.1);padding:14px 26px;border-radius:16px;outline:4px solid #F5A623}}
.btn{{margin-top:44px;background:#F5A623;color:#0A0A0C;border-radius:80px;text-align:center;font:800 46px Inter;padding:34px;box-shadow:0 20px 60px rgba(245,166,35,.35)}}
"""

def _chrome(i, n, arroba, light=False, ultimo=False):
    dots = "".join(f'<i class="{"on" if k == i else ""}"></i>' for k in range(1, n + 1)) if n <= 10 else f"{i}/{n}"
    topo = f'<div class="topo"><div class="marca"><img src="{ICONE}">SERAPHIM</div><div class="dots2">{dots}</div></div>'
    rod = f'<div class="rodape"><span>{arroba}</span>' + ('' if ultimo else '<div class="seta">→</div>') + '</div>'
    return topo, rod


def _pag(corpo, i, n, arroba, light=False, extra="", ultimo=False):
    topo, rod = _chrome(i, n, arroba, light, ultimo)
    return f"""<html><head><meta charset="utf-8"><style>{CSS}{CSS_EXTRA}{CSS_V2}</style></head>
<body class="v2{' light' if light else ''}"><div class="bg"></div><div class="dots"></div>{extra}{topo}{corpo}{rod}</body></html>"""


def _cab(s):
    r = f'<div class="rot">{s["rotulo"]}</div>' if s.get("rotulo") else ""
    return r + f'<h2>{fmt(s.get("titulo", ""))}</h2>' + (f'<div class="sub">{fmt(s["texto"])}</div>' if s.get("texto") else "")


def slide_v2(s, i, n, arroba):
    t = s.get("tipo"); light = s.get("fundo") == "branco"; ult = i == n
    if t == "pilulas":
        its = "".join(f'<div class="pil"><div class="n">{k}</div><div>{fmt(x if isinstance(x, str) else x.get("texto", ""))}</div></div>' for k, x in enumerate(s.get("itens", [])[:5], 1))
        return _pag(f'<div class="corpo c">{_cab(s)}<div style="margin-top:30px">{its}</div></div>', i, n, arroba, light, ultimo=ult)
    if t == "card":
        chips = "".join(f"<span>{c}</span>" for c in s.get("chips", [])[:4])
        c = s.get("card") or s.get("texto", "")
        return _pag(f'<div class="corpo c">{_cab({"rotulo": s.get("rotulo"), "titulo": s.get("titulo")})}<div class="cardp"><div class="ic">{s.get("icone", "⚙️")}</div>'
                    f'<h3>{fmt(s.get("subtitulo", ""))}</h3><p>{fmt(c)}</p>{("<div class=chips>" + chips + "</div>") if chips else ""}</div></div>', i, n, arroba, light, ultimo=ult)
    if t == "whatsapp":
        bs = "".join(f'<div class="bol {"c" if m.get("de", "cliente") == "cliente" else "e"}">{m.get("texto", "")}<small>{m.get("hora", "")}</small></div>' for m in s.get("mensagens", [])[:6])
        return _pag(f'<div class="corpo">{_cab(s)}</div><div class="cel"><div class="cab"><i></i>{s.get("contato", "Cliente")}</div><div class="chat">{bs}</div></div>', i, n, arroba, light, ultimo=ult)
    if t == "comparacao":
        def col(c, cls):
            return f'<div class="col {cls}"><h4>{c.get("rotulo", "")}</h4><ul style="padding:0;margin:0">' + "".join(f"<li>{fmt(x)}</li>" for x in c.get("itens", [])[:4]) + "</ul></div>"
        return _pag(f'<div class="corpo c">{_cab({"rotulo": s.get("rotulo"), "titulo": s.get("titulo")})}<div class="cmp">{col(s.get("esquerda", {}), "ruim")}{col(s.get("direita", {}), "bom")}</div>'
                    f'{("<div class=sub>" + fmt(s["texto"]) + "</div>") if s.get("texto") else ""}</div>', i, n, arroba, light, ultimo=ult)
    if t == "passos":
        ps = "".join(f'<div class="p"><i>{k}</i><b>{fmt(x.get("titulo", "") if isinstance(x, dict) else x)}</b>{fmt(x.get("texto", "")) if isinstance(x, dict) else ""}</div>' for k, x in enumerate(s.get("itens", [])[:4], 1))
        return _pag(f'<div class="corpo c">{_cab({"rotulo": s.get("rotulo"), "titulo": s.get("titulo")})}<div class="pas">{ps}</div></div>', i, n, arroba, light, ultimo=ult)
    if t == "citacao":
        return _pag(f'<div class="corpo c"><div class="asp">“</div><div class="cit">{fmt(s.get("titulo", ""))}</div>'
                    f'{("<div class=sub>" + fmt(s["texto"]) + "</div>") if s.get("texto") else ""}</div>', i, n, arroba, light, ultimo=ult)
    if t == "perfil_cta":
        corpo = (f'<div class="corpo c">{_cab({"titulo": s.get("titulo")})}<div class="perf"><div class="l1"><img class="av" src="{ICONE}"><div><div class="nm">{arroba}</div>'
                 f'<div style="font:500 30px Inter;color:#6a6a72">Seraphim • IA e automação</div></div></div>'
                 f'<div class="bio">{fmt(s.get("bio", "Tecnologia, IA e automação para pequenas empresas crescerem sem complicação."))}</div>'
                 f'<div class="lnk">🔗 {s.get("link", "link na bio")}</div></div><div class="btn">{s.get("botao", "Clique no link da bio")}</div>'
                 f'{("<div class=sub style=text-align:center>" + fmt(s["texto"]) + "</div>") if s.get("texto") else ""}</div>')
        return _pag(corpo, i, n, arroba, light, ultimo=True)
    if t == "capa_noticia":
        rec = ""
        for k, r in enumerate(s.get("recortes", [])[:3]):
            rec += f'<div class="rec" style="top:{700 + k * 165}px;transform:rotate({[-2.2, 1.6, -1.2][k]}deg)"><small>{r.get("fonte", "")}</small>{r.get("texto", "")}</div>'
        selo = f'<div class="selon">{s.get("selo", "ESTA SEMANA")}</div>'
        return _pag(f'<div class="corpo" style="top:170px">{selo}<h2 style="margin-top:34px;font-size:112px">{fmt(s.get("titulo", ""))}</h2></div>{rec}', i, n, arroba, False, ultimo=False)
    return None


def slide_html(s: dict, i: int, n: int, arroba: str, tema: str = None) -> str:
    tipo = s.get("tipo", "texto")
    v2 = slide_v2(s, i, n, arroba)
    if v2:
        return v2
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


def _foto_pixabay(busca, destino):
    import os, urllib.parse, urllib.request
    chave = os.environ.get("PIXABAY_API_KEY")
    if not chave or not busca:
        return None
    try:
        url = f"https://pixabay.com/api/?key={chave}&q={urllib.parse.quote(busca[:90])}&image_type=photo&orientation=vertical&safesearch=true&per_page=20&order=popular"
        hits = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()).get("hits", [])
        import random
        random.Random(busca).shuffle(hits)
        for h in hits[:6]:
            dados = urllib.request.urlopen(urllib.request.Request(h.get("largeImageURL") or h["webformatURL"], headers={"User-Agent": "Mozilla/5.0"}), timeout=90).read()
            if len(dados) > 30000:
                destino.write_bytes(dados); return destino
    except Exception as e:
        print(f"[aviso] foto do carrossel: {e}")
    return None


async def main(caminho: str, saida_dir: str = None):
    spec = json.loads(Path(caminho).read_text(encoding="utf-8"))
    nome = spec.get("nome", Path(caminho).stem)
    arroba = spec.get("arroba", ARROBA)
    slides = spec["slides"]
    saida = Path(saida_dir) if saida_dir else RAIZ / "entrega" / "carrosseis" / nome
    saida.mkdir(parents=True, exist_ok=True)
    for k, sl in enumerate(slides):
        if sl.get("tipo") == "capa_foto" and sl.get("busca") and not sl.get("imagem"):
            f = _foto_pixabay(sl["busca"], saida / f"_foto{k}.jpg")
            if f:
                sl["imagem"] = f.as_uri()
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
        for f in saida.glob('_foto*.jpg'):
            f.unlink()
        await nav.close()
    if spec.get("legenda"):
        (saida / "legenda.txt").write_text(spec["legenda"], encoding="utf-8")
    print(f"Pronto: {len(slides)} slides em {saida}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/carrossel.py entrada/arquivo.json")
        sys.exit(1)
    asyncio.run(main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
