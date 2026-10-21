"""Carrosséis do AutoFlow (C11, C12, C13) — material oficial: telas reais, cenas de oficina, logo, Stack Sans, laranja #FF6A13 / #0E0E10.
Sem preço, sem banner de plano, sem cliente/resultado inventado.
Uso: python scripts/carrosseis_autoflow.py [previa|fila] [C11 C12 C13]
  previa -> testes/autoflow_carrosseis/<peca>/instagram|tiktok
  fila   -> grava em fila/<data_hora_nome>/ (slide-NN.jpg, tiktok/, item.json)"""
import asyncio, io, json, shutil, sys
from pathlib import Path
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
FONTES = (RAIZ / "motor/public/fontes").as_uri()
AF = RAIZ / "motor/public/af"
TELAS = RAIZ / "assets/autoflow/telas"
LOGO = (RAIZ / "assets/autoflow/logo-icone.png").as_uri()
LOGO_C = (RAIZ / "assets/autoflow/logo-icone-claro.png").as_uri()
ARROBA = "@seraphimbr_"

CSS = f"""
@font-face{{font-family:SH;font-weight:700;src:url({FONTES}/stack-sans-headline-latin-700-normal.woff2)}}
@font-face{{font-family:SH;font-weight:600;src:url({FONTES}/stack-sans-headline-latin-600-normal.woff2)}}
@font-face{{font-family:ST;font-weight:400;src:url({FONTES}/stack-sans-text-latin-400-normal.woff2)}}
@font-face{{font-family:ST;font-weight:500;src:url({FONTES}/stack-sans-text-latin-500-normal.woff2)}}
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{--o:#FF6A13;--bg:#0E0E10}}
body{{width:1080px;position:relative;overflow:hidden;font-family:ST;background:var(--bg);color:#F5F5F7}}
.claro{{background:#F4F1EC;color:#0E0E10}}
.glow{{position:absolute;inset:0;background:radial-gradient(90% 55% at 90% 100%,rgba(255,106,19,.22),transparent 60%),radial-gradient(70% 40% at 0% 0%,#1d1d22,transparent 70%)}}
.claro .glow{{background:radial-gradient(80% 50% at 90% 0%,rgba(255,106,19,.18),transparent 60%)}}
.topo{{position:absolute;left:72px;right:72px;top:64px;display:flex;justify-content:space-between;align-items:center;z-index:6}}
.marca{{display:flex;align-items:center;gap:14px;font:700 28px SH;letter-spacing:.5px}} .marca img{{width:54px;height:54px;border-radius:14px}}
.pts{{display:flex;gap:10px}} .pts i{{width:12px;height:12px;border-radius:50%;background:currentColor;opacity:.25}} .pts i.on{{opacity:1;background:var(--o);width:34px;border-radius:8px}}
.rod{{position:absolute;left:72px;right:72px;display:flex;justify-content:space-between;align-items:center;font:500 24px ST;opacity:.75;z-index:6}}
.rot{{font:700 24px SH;letter-spacing:4px;color:var(--o);text-transform:uppercase;margin-bottom:22px}}
h1{{font:700 92px/1.02 SH;letter-spacing:-2px}} h2{{font:700 78px/1.06 SH;letter-spacing:-1.5px}}
.d{{color:var(--o)}}
p.s{{font:400 38px/1.4 ST;color:#B4B4BC;margin-top:28px}} .claro p.s{{color:#4a4a52}} p.s b{{color:#fff;font-weight:500}} .claro p.s b{{color:#0E0E10}}
.foto{{position:absolute;inset:0;background-size:cover;background-position:center}}
.veu{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(14,14,16,.55) 0%,rgba(14,14,16,.1) 30%,rgba(14,14,16,.85) 68%,#0E0E10 100%)}}
.tela{{position:absolute;left:72px;right:72px;border-radius:28px;overflow:hidden;border:2px solid rgba(255,255,255,.12);box-shadow:0 40px 90px rgba(0,0,0,.6),0 0 0 8px rgba(255,106,19,.10)}}
.tela img{{width:100%;display:block}}
.cel{{position:absolute;border-radius:56px;overflow:hidden;border:10px solid #2b2b31;box-shadow:0 40px 100px rgba(0,0,0,.65)}} .cel img{{width:100%;display:block}}
.card{{border:2px solid rgba(255,255,255,.12);background:#17171b;border-radius:36px;padding:44px 48px;margin-top:34px}}
.claro .card{{background:#fff;border-color:#e2ddd3}}
.q{{font:700 40px/1.2 SH;color:var(--o)}}
.btn{{display:inline-block;background:var(--o);color:#0E0E10;font:700 40px SH;padding:30px 50px;border-radius:70px;margin-top:40px;box-shadow:0 20px 60px rgba(255,106,19,.35)}}
.logo-g{{width:150px;height:150px;border-radius:36px;box-shadow:0 20px 60px rgba(255,106,19,.35)}}
"""


def fmt(t):
    import re
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"\*(.+?)\*", r'<span class="d">\1</span>', t).replace("|", "<br>")


def moldura(n, T, claro, alto, corpo, extra=""):
    pts = "".join(f'<i class="{"on" if i == n else ""}"></i>' for i in range(1, T + 1))
    seta = "" if n == T else "<span>ARRASTE →</span>"
    off = (alto - 1350) // 2
    return (f'<html><head><meta charset="utf-8"><style>{CSS}body{{height:{alto}px}}.w{{position:absolute;left:0;top:{off}px;width:1080px;height:1350px}}</style></head>'
            f'<body class="{"claro" if claro else ""}"><div class="glow"></div>{extra}<div class="w">'
            f'<div class="topo"><div class="marca"><img src="{LOGO_C if claro else LOGO}">AutoFlow</div><div class="pts">{pts}</div></div>{corpo}'
            f'<div class="rod" style="bottom:56px"><span>{ARROBA}</span>{seta}</div></div></body></html>')


def S_capa(d, n, T, alto):
    img = (AF / d["foto"]).as_uri()
    extra = f'<div class="foto" style="background-image:url({img});background-position:{d.get("pos","center 30%")}"></div><div class="veu"></div>'
    corpo = f'<div style="position:absolute;left:72px;right:72px;bottom:160px"><div class="rot">{d["rotulo"]}</div><h1>{fmt(d["titulo"])}</h1></div>'
    return moldura(n, T, False, alto, corpo, extra)


def S_texto(d, n, T, alto):
    corpo = (f'<div style="position:absolute;left:72px;right:72px;top:210px;bottom:140px;display:flex;flex-direction:column;justify-content:center">'
             f'{("<div class=rot>" + d["rotulo"] + "</div>") if d.get("rotulo") else ""}<h2>{fmt(d["titulo"])}</h2>'
             f'{("<p class=s>" + fmt(d["texto"]) + "</p>") if d.get("texto") else ""}</div>')
    return moldura(n, T, d.get("claro"), alto, corpo)


def S_tela(d, n, T, alto):
    img = (TELAS / d["tela"]).as_uri()
    w, h = Image.open(TELAS / d["tela"]).size
    alt = min(int(936 * h / w), 700); top = d.get("top", 360)
    corpo = (f'<div style="position:absolute;left:72px;right:72px;top:170px"><div class="rot">{d["rotulo"]}</div><h2 style="font-size:70px">{fmt(d["titulo"])}</h2></div>'
             f'<div class="tela" style="top:{top}px;height:{alt}px"><img src="{img}" style="object-fit:cover;object-position:{d.get("pos", "top center")};height:100%"></div>'
             f'<div style="position:absolute;left:72px;right:72px;top:{top + alt + 34}px;font:400 34px/1.35 ST;color:#B4B4BC">{fmt(d.get("texto", ""))}</div>')
    return moldura(n, T, False, alto, corpo)


def S_celular(d, n, T, alto):
    img = (TELAS / d["tela"]).as_uri()
    corpo = (f'<div style="position:absolute;left:72px;right:72px;top:170px"><div class="rot">{d["rotulo"]}</div><h2 style="font-size:70px">{fmt(d["titulo"])}</h2>'
             f'<p class=s style="max-width:420px;font-size:34px">{fmt(d.get("texto", ""))}</p></div>'
             f'<div class="cel" style="left:{d.get("x", 520)}px;top:{d.get("top", 400)}px;width:{d.get("w", 440)}px;height:1000px"><img src="{img}" style="height:100%;object-fit:cover;object-position:top"></div>')
    return moldura(n, T, False, alto, corpo)


def S_qa(d, n, T, alto):
    corpo = (f'<div style="position:absolute;left:72px;right:72px;top:210px;bottom:140px;display:flex;flex-direction:column;justify-content:center">'
             f'<div class="rot">PERGUNTA {d["num"]}</div><h2>{fmt(d["pergunta"])}</h2><div class="card"><div class="q">Resposta</div><p class=s style="margin-top:16px;color:{"#2a2a30" if d.get("claro") else "#E8E8EC"}">{fmt(d["resposta"])}</p></div></div>')
    return moldura(n, T, d.get("claro"), alto, corpo)


def S_cta(d, n, T, alto):
    corpo = (f'<div style="position:absolute;left:72px;right:72px;top:210px;bottom:140px;display:flex;flex-direction:column;justify-content:center">'
             f'<img class="logo-g" src="{LOGO}" style="margin-bottom:44px"><h2>{fmt(d["titulo"])}</h2><p class=s>{fmt(d["texto"])}</p>'
             f'<div><span class="btn">{d["botao"]}</span></div></div>')
    return moldura(n, T, False, alto, corpo)


TIPOS = dict(capa=S_capa, texto=S_texto, tela=S_tela, celular=S_celular, qa=S_qa, cta=S_cta)

C = {
 "C11": dict(nome="por-que-comecamos-pelas-oficinas", quando="2026-10-24 09:00", titulo="Por que começamos pelas oficinas",
  legenda="Oficina é um negócio de muita coisa acontecendo ao mesmo tempo. Foi por aí que a gente decidiu começar o AutoFlow.\n\nConhece uma oficina que ainda vive de caderno? Manda pra ela.\n\nTeste gratuito para oficinas selecionadas. Solicite acesso pelo direct.",
  hashtags="#autoflow #oficinamecanica #gestaoautomotiva #seraphimbr",
  slides=[
   dict(tipo="capa", foto="cena-04.png", rotulo="AUTOFLOW", titulo="Por que começamos|pelas *oficinas*"),
   dict(tipo="texto", rotulo="O DIA A DIA", titulo="Muita coisa *ao mesmo tempo*", texto="Carro no elevador, cliente ligando, peça pendente, **ordem de serviço** num papel."),
   dict(tipo="texto", rotulo="O PROBLEMA", claro=True, titulo="A informação fica *espalhada*", texto="No caderno, na cabeça de quem atendeu, no celular de alguém."),
   dict(tipo="texto", rotulo="A IDEIA", titulo="Um sistema feito *para esse dia a dia*", texto="O AutoFlow é um sistema de gestão **feito para oficinas mecânicas**, acessado pelo navegador."),
   dict(tipo="texto", rotulo="POR ONDE COMEÇAR", claro=True, titulo="Começar por *um segmento* para fazer bem feito", texto="Por isso o foco, agora, é a **oficina mecânica**."),
   dict(tipo="cta", titulo="Sua oficina merece uma *gestão mais simples*", texto="Teste gratuito para oficinas selecionadas.|Solicite acesso pelo direct.", botao="Solicite acesso gratuito")]),
 "C12": dict(nome="autoflow-em-6-slides", quando="2026-10-24 17:30", titulo="AutoFlow em 6 slides",
  legenda="O AutoFlow em 6 slides: o painel, o quadro de ordens de serviço e o histórico por placa — telas do sistema, com dados fictícios da “Oficina Modelo”.\n\nSua oficina merece uma gestão mais simples.\n\nTeste gratuito para oficinas selecionadas. Solicite acesso pelo direct.",
  hashtags="#autoflow #oficinamecanica #gestaoautomotiva #seraphimbr",
  slides=[
   dict(tipo="capa", foto="cena-10.png", pos="center 25%", rotulo="CONHEÇA O AUTOFLOW", titulo="AutoFlow|em *6 slides*"),
   dict(tipo="tela", rotulo="1 · O PAINEL", titulo="A oficina *num olhar*", tela="painel_conteudo.png", texto="Tela do sistema, dados fictícios."),
   dict(tipo="tela", rotulo="2 · ORDENS DE SERVIÇO", titulo="Do pendente ao *entregue*", tela="ordens_conteudo.png", texto="Um quadro com cada ordem de serviço na sua etapa."),
   dict(tipo="tela", rotulo="3 · HISTÓRICO POR PLACA", titulo="*Digitou a placa*, achou o carro", tela="historico_conteudo.png", texto="Tudo o que a oficina já fez num veículo, da primeira visita até hoje."),
   dict(tipo="tela", rotulo="4 · NOVA ORDEM", titulo="Nova OS *num só lugar*", tela="nova_os_painel.png", pos="top center", texto="Cliente, veículo, serviço e valor num só lugar."),
   dict(tipo="cta", titulo="Sua oficina merece uma *gestão mais simples*", texto="Teste gratuito para oficinas selecionadas.|Solicite acesso pelo direct.", botao="Solicite acesso gratuito")]),
 "C13": dict(nome="perguntas-sobre-o-autoflow", quando="2026-10-25 09:00", titulo="Perguntas sobre o AutoFlow",
  legenda="As perguntas que mais fazem quando a gente fala do AutoFlow. Faltou alguma? Pergunta nos comentários ou no direct.\n\nTeste gratuito para oficinas selecionadas. Solicite acesso pelo direct.",
  hashtags="#autoflow #oficinamecanica #gestaoautomotiva #seraphimbr",
  slides=[
   dict(tipo="capa", foto="cena-11.png", pos="center 30%", rotulo="FAQ", titulo="Perguntas sobre|o *AutoFlow*"),
   dict(tipo="qa", num="01", pergunta="O que é o *AutoFlow?*", resposta="Um sistema de **gestão para oficinas mecânicas**, feito pela Seraphim. Você acessa pelo navegador."),
   dict(tipo="qa", num="02", claro=True, pergunta="Para quem é?", resposta="Para **oficinas mecânicas** que querem sair do caderno e da planilha e organizar a gestão num lugar só."),
   dict(tipo="qa", num="03", pergunta="Quanto *custa?*", resposta="Estamos em **acesso antecipado**: o teste é **gratuito para oficinas selecionadas**. Os detalhes a gente combina pelo direct."),
   dict(tipo="qa", num="04", claro=True, pergunta="Como *peço acesso?*", resposta="Manda uma mensagem no **direct da @seraphimbr_**. A gente conversa sobre a sua oficina."),
   dict(tipo="cta", titulo="Ficou com *outra dúvida?*", texto="Pergunta nos comentários ou no direct.", botao="Solicite acesso gratuito")]),
}


async def render(peca, out: Path):
    from playwright.async_api import async_playwright
    d = C[peca]; T = len(d["slides"])
    async with async_playwright() as p:
        nav = await p.chromium.launch()
        for rede, alto in (("instagram", 1350), ("tiktok", 1920)):
            (out / rede).mkdir(parents=True, exist_ok=True)
            for k, s in enumerate(d["slides"], 1):
                pg = await nav.new_page(viewport={"width": 1080, "height": alto})
                tmp = out / "_t.html"; tmp.write_text(TIPOS[s["tipo"]](s, k, T, alto), encoding="utf-8")
                await pg.goto(tmp.as_uri()); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(300)
                Image.open(io.BytesIO(await pg.screenshot())).convert("RGB").save(out / rede / f"slide-{k:02d}.jpg", quality=93)
                await pg.close(); tmp.unlink()
        await nav.close()


def main():
    modo = sys.argv[1] if len(sys.argv) > 1 else "previa"
    pecas = sys.argv[2:] or list(C)
    for peca in pecas:
        d = C[peca]
        if modo == "previa":
            asyncio.run(render(peca, RAIZ / "testes" / "autoflow_carrosseis" / peca)); print("previa", peca); continue
        dest = RAIZ / "fila" / f"{d['quando'].replace(' ', '_').replace(':', '')}_{d['nome']}"
        tmp = RAIZ / "testes" / "autoflow_carrosseis" / peca
        shutil.rmtree(tmp, ignore_errors=True); asyncio.run(render(peca, tmp))
        shutil.rmtree(dest, ignore_errors=True); dest.mkdir(parents=True)
        for f in (tmp / "instagram").glob("*.jpg"): shutil.copy(f, dest / f.name)
        shutil.copytree(tmp / "tiktok", dest / "tiktok")
        (dest / "item.json").write_text(json.dumps({"tipo": "carrossel", "quando": d["quando"].replace(" ", "T") + ":00-03:00",
                                                    "legenda": d["legenda"] + "\n\n" + d["hashtags"]}, ensure_ascii=False, indent=2), encoding="utf-8")
        print("fila", dest.name)


if __name__ == "__main__":
    main()
