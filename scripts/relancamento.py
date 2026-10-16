"""
Relançamento (semana 19–25/10/2026): carrosséis com direção de arte PRÓPRIA por peça.
Cada carrossel = lista de slides em HTML (quadro 1080x1350). Saídas:
  instagram/slide-NN.jpg (1080x1350)  e  tiktok/slide-NN.jpg (1080x1920, mesmo quadro na faixa segura)
Uso: python scripts/relancamento.py C1 [C2 ...]   -> relancamento/<peça>/
"""
import asyncio, io, sys
from pathlib import Path
from playwright.async_api import async_playwright
sys.path.insert(0, str(Path(__file__).parent))
import capa, ingredientes
from capa import OURO, PRETO, BRANCO, PAPEL, CINZA, BASE
from marca import ARROBA

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "relancamento"
LOGO = (RAIZ / "carrossel" / "marca" / "logo-original.png").as_uri()
OURO_ESC = "#B86E00"


def assinatura(n, total, escuro=True):
    cor = CINZA if escuro else "#5a544b"
    return (f'<div style="position:absolute;left:80px;bottom:72px;width:60px;height:4px;background:{OURO}"></div>'
            f'<div style="position:absolute;left:160px;bottom:60px;font:500 26px SpaceB;color:{cor}">{ARROBA}</div>'
            f'<div style="position:absolute;right:80px;bottom:60px;font:500 24px Jet;color:{cor}">{n:02d} / {total:02d}</div>')


def d(t, cls="g"):
    return capa.destacar(t, cls) if "*" in t else t


# ---------------- C1 · O que é a Seraphim — revista editorial ----------------
def c1():
    T = 7
    fio = f'<div style="position:absolute;left:80px;right:80px;top:150px;height:2px;background:{{c}}"></div>'
    def cab(n, sec, escuro=True):
        c = "#2a2a30" if escuro else PRETO
        cor = CINZA if escuro else "#5a544b"
        return (f'<div style="position:absolute;left:80px;top:96px;font:800 22px SpaceB;letter-spacing:6px;color:{OURO if escuro else OURO_ESC}">{sec}</div>'
                f'<div style="position:absolute;right:80px;top:96px;font:500 22px Jet;color:{cor}">p. {n:02d}</div>' + fio.format(c=c))
    s = []
    s.append(("papel", f"""{cab(1, 'EDIÇÃO DE ESTREIA', False)}
<div style="position:absolute;left:80px;right:80px;top:250px;font:170px/0.92 Instrument;color:{PRETO}">O que é a<br><span style="color:{OURO_ESC};font-style:italic">Seraphim</span></div>
<div style="position:absolute;left:80px;width:560px;top:700px;font:500 34px/1.45 Manrope;color:#3a3630">Uma empresa de tecnologia, em sete páginas. Arraste para ler.</div>
<div style="position:absolute;right:80px;top:700px;font:italic 150px/1 Instrument;color:{OURO_ESC}">→</div>{assinatura(1, T, False)}"""))
    s.append(("preto", f"""{cab(2, 'EM UMA FRASE')}
<div style="position:absolute;left:80px;right:80px;top:330px;font:96px/1.06 Fraunces;color:{BRANCO}">Uma empresa de tecnologia que desenvolve sistemas, automatiza processos e <span class="g">conecta ferramentas.</span></div>{assinatura(2, T)}"""))
    s.append(("preto", f"""{cab(3, 'PARA QUEM')}
<div style="position:absolute;left:80px;top:260px">{ingredientes.icone('store', OURO, 150, 1.4)}</div>
<div style="position:absolute;left:80px;right:80px;top:470px;font:76px/1.1 Fraunces;color:{BRANCO}">Pequenas e médias empresas que cresceram <span class="g">mais rápido</span> que as próprias ferramentas.</div>{assinatura(3, T)}"""))
    col = lambda i, t, x: (f'<div style="flex:1;min-width:0;padding:0 28px;border-left:2px solid {OURO if i else "transparent"}">'
                           f'<div style="font:500 26px Jet;color:{OURO}">0{i + 1}</div>'
                           f'<div style="font:46px/1.05 Fraunces;color:{BRANCO};margin:22px 0 26px;hyphens:auto" lang="pt">{t}</div>'
                           f'<div style="font:500 28px/1.45 Manrope;color:{CINZA}">{x}</div></div>')
    s.append(("preto", f"""{cab(4, 'O QUE FAZEMOS')}
<div style="position:absolute;left:46px;right:46px;top:320px;display:flex">
{col(0, 'Sistemas sob medida', 'feitos para o jeito que a sua empresa trabalha')}{col(1, 'Automação', 'tarefas repetidas acontecendo sozinhas')}{col(2, 'Integração', 'suas ferramentas conversando entre si')}</div>{assinatura(4, T)}"""))
    passo = lambda n, t: (f'<div style="display:flex;gap:40px;align-items:baseline;padding:34px 0;border-bottom:1px solid #2a2a30">'
                          f'<div style="font:110px/1 Anton;color:{OURO};width:110px">{n}</div><div style="font:64px/1.1 Fraunces;color:{BRANCO}">{t}</div></div>')
    s.append(("preto", f"""{cab(5, 'COMO FAZEMOS')}
<div style="position:absolute;left:80px;right:80px;top:250px">{passo(1, 'Ouvimos antes.')}{passo(2, 'Construímos pequeno.')}{passo(3, 'Melhoramos com o uso.')}</div>{assinatura(5, T)}"""))
    s.append(("preto", f"""{cab(6, 'PRODUTO PRÓPRIO')}
<div style="position:absolute;left:80px;right:80px;top:300px;font:500 30px Jet;color:{OURO}">// em breve, por aqui</div>
<div style="position:absolute;left:80px;right:80px;top:370px;font:80px/1.05 Fraunces;color:{BRANCO}">Nosso primeiro produto já existe. É um sistema de gestão para <span class="g">oficinas mecânicas.</span></div>
<div style="position:absolute;left:80px;right:80px;top:960px;font:500 32px/1.5 Manrope;color:{CINZA}">No sábado, a gente apresenta.</div>{assinatura(6, T)}"""))
    s.append(("papel", f"""{cab(7, 'ATÉ A PRÓXIMA PÁGINA', False)}
<img src="{LOGO}" style="position:absolute;left:80px;top:250px;width:200px;border-radius:20px">
<div style="position:absolute;left:80px;right:80px;top:520px;font:120px/0.95 Instrument;color:{PRETO}">Nesta semana, a gente mostra <span style="color:{OURO_ESC};font-style:italic">tudo.</span></div>
<div style="position:absolute;left:80px;top:900px;font:800 30px SpaceB;letter-spacing:4px;color:{PRETO}">SIGA {ARROBA.upper()}</div>{assinatura(7, T, False)}"""))
    return s


# ---------------- C2 · Nosso manifesto — uma frase gigante por slide ----------------
def c2():
    frases = ["Nosso *manifesto*", "Tecnologia boa é a que *some.*", "Processo vem antes do *software.*",
              "Automatizar bagunça só deixa a bagunça mais *rápida.*", "Pequena empresa merece sistema de *empresa grande.*",
              "Promessa sem método é só *propaganda.*", "Seraphim. Tecnologia com *método.*"]
    T = len(frases)
    s = []
    for i, f in enumerate(frases):
        n = i + 1
        if i == 0:
            corpo = (f'<div style="position:absolute;left:70px;right:70px;top:230px;font:300px/0.86 Anton;text-transform:uppercase;color:{BRANCO}">Nosso<br>'
                     f'<span style="color:transparent;-webkit-text-stroke:4px {OURO}">mani-<br>festo</span></div>')
        elif i % 2:
            corpo = (f'<div style="position:absolute;left:80px;top:150px;font:500 26px Jet;color:{OURO}">{n - 1:02d}</div>'
                     f'<div style="position:absolute;left:80px;right:80px;top:230px;font:{[0,150,140,108,112,128,0][i]}px/0.98 Fraunces;color:{BRANCO}">{d(f)}</div>')
        else:
            corpo = (f'<div style="position:absolute;left:80px;top:150px;font:500 26px Jet;color:{OURO}">{n - 1:02d}</div>'
                     f'<div style="position:absolute;left:70px;right:70px;top:230px;font:{[0,0,170,0,150,0,190][i]}px/0.9 Anton;text-transform:uppercase;color:{BRANCO}">{d(f)}</div>')
        s.append(("preto", corpo + assinatura(n, T)))
    return s


PECAS = {"C1": c1, "C2": c2}


def html(fundo, corpo, alto):
    bg = "papel" if fundo == "papel" else ""
    topo = 0 if alto == 1350 else 200
    return (f'<html><head><meta charset="utf-8"><style>{BASE.replace("{{", "{").replace("}}", "}")} body{{height:{alto}px}}'
            f' :root{{--fd:Anton;--fw:Unbounded;--fs:Fraunces;--fs2:Instrument;--fb:Manrope;--grao:.3}}</style></head>'
            f'<body class="{bg}" style="{"" if bg else "background:" + PRETO}"><div style="position:absolute;left:0;top:{topo}px;width:1080px;height:1350px">'
            f'{corpo}</div><div class="grao"></div></body></html>')


async def render(peca):
    from PIL import Image
    slides = PECAS[peca]()
    out = SAIDA / peca
    async with async_playwright() as p:
        nav = await p.chromium.launch()
        for rede, alto in (("instagram", 1350), ("tiktok", 1920)):
            (out / rede).mkdir(parents=True, exist_ok=True)
            for k, (fundo, corpo) in enumerate(slides):
                pg = await nav.new_page(viewport={"width": 1080, "height": alto})
                tmp = out / "_tmp.html"
                tmp.write_text(html(fundo, corpo, alto), encoding="utf-8")
                await pg.goto(tmp.as_uri()); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(300)
                Image.open(io.BytesIO(await pg.screenshot())).convert("RGB").save(out / rede / f"slide-{k + 1:02d}.jpg", quality=93)
                await pg.close(); tmp.unlink()
        await nav.close()
    print(peca, len(slides), "slides ->", out)


if __name__ == "__main__":
    for a in sys.argv[1:]:
        asyncio.run(render(a))
