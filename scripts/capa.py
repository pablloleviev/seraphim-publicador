"""
Capas dos posts (Reels/TikTok 1080x1920 e 1ª página de carrossel 1080x1350).

REGRA (Pabllo, 15/10/2026): mesma PALETA para o feed combinar (preto #0A0A0C, dourado #F5A623, branco, papel #F4F1EA),
mas cada capa com uma IDEIA VISUAL diferente. Nunca o mesmo molde em sequência: há vários modelos e o sorteio
evita os usados recentemente (historico.json -> "capa_modelo").

Uso:
    python scripts/capa.py "Título" saida.jpg [modelo]
No código:
    capa.escolher(titulo, rotulo, recentes) -> nome do modelo
    asyncio.run(capa.gerar_varias([{"titulo","rotulo","modelo","saida","modo": "reels"|"carrossel"}]))
"""
import asyncio, hashlib, io, re, sys
from pathlib import Path
from playwright.async_api import async_playwright

RAIZ = Path(__file__).resolve().parent.parent
FONTES = (RAIZ / "carrossel" / "fontes").as_uri()
SERA = (RAIZ / "carrossel" / "sera").as_uri()
ICONE = (RAIZ / "carrossel" / "marca" / "icone.png").as_uri()
POSES = ["confiante", "surpreso", "pensando", "preocupado", "feliz", "comemorando"]
OURO, PRETO, BRANCO, PAPEL, CINZA, VERM = "#F5A623", "#0A0A0C", "#F5F5F7", "#F4F1EA", "#A1A1AA", "#E5484D"

BASE = f"""
@font-face{{font-family:Anton;src:url({FONTES}/anton.ttf)}}
@font-face{{font-family:Bebas;src:url({FONTES}/bebas.ttf)}}
@font-face{{font-family:DMSerif;src:url({FONTES}/dmserif.ttf)}}
@font-face{{font-family:Play;src:url({FONTES}/playfair.ttf)}}
@font-face{{font-family:Jet;src:url({FONTES}/jetbrains.ttf)}}
@font-face{{font-family:Mont;src:url({FONTES}/montserrat.ttf)}}
@font-face{{font-family:Archivo;src:url({FONTES}/archivo.ttf)}}
@font-face{{font-family:Space;src:url({FONTES}/spacegrotesk.ttf)}}
@font-face{{font-family:Inter;font-weight:500;src:url({FONTES}/inter500.ttf)}}
@font-face{{font-family:Inter;font-weight:800;src:url({FONTES}/inter800.ttf)}}
*{{margin:0;box-sizing:border-box}}
body{{width:1080px;background:{PRETO};position:relative;overflow:hidden;color:{BRANCO};font-family:Inter}}
.safe{{position:absolute;left:0;width:1080px;height:1440px;overflow:hidden}}
.g{{color:{OURO}}}
.arroba{{position:absolute;font:500 26px Inter;letter-spacing:1px}}
"""


# ---------------- texto ----------------
def limpar(t):
    return re.sub(r"\s+", " ", re.sub(r"[*|]", " ", t or "")).strip()


def destacar(t, cls="g"):
    """*palavra* vira destaque; sem asteriscos, destaca a última palavra forte."""
    t = re.sub(r"\s+", " ", (t or "").strip()).replace("|", " ")
    if "*" in t:
        return re.sub(r"\*(.+?)\*", rf'<span class="{cls}">\1</span>', t)
    p = t.split(" ")
    k = 2 if (len(p) > 3 and len(p[-2]) > 2) else 1
    return " ".join(p[:-k]) + (" " if len(p) > k else "") + f'<span class="{cls}">' + " ".join(p[-k:]) + "</span>"


def numero_de(t):
    m = re.search(r"\b(\d{1,3})\b", limpar(t))
    return m.group(1) if m else None


def tam(n, grande, medio, peq, mini):
    return grande if n <= 16 else medio if n <= 28 else peq if n <= 42 else mini


def semente(t):
    return int(hashlib.md5((t or "").encode()).hexdigest(), 16)


# ---------------- modelos (cada um é uma ideia visual diferente) ----------------
def m_tipografia(t, rot, s):
    """palavras gigantes empilhadas ocupando a tela, linhas alternando cheio/contorno/dourado"""
    ws = limpar(t).upper().split(" ")
    linhas, atual = [], ""
    for w in ws:
        if len(atual) + len(w) + 1 > 9 and atual:
            linhas.append(atual); atual = w
        else:
            atual = (atual + " " + w).strip()
    linhas.append(atual)
    linhas = linhas[:6]
    out = ""
    for i, l in enumerate(linhas):
        fs = min(300, int(960 / max(3, len(l)) / 0.46))
        estilo = [f"color:{BRANCO}", f"color:transparent;-webkit-text-stroke:3px {OURO}", f"color:{OURO}"][(i + s) % 3]
        out += f'<div style="font:{fs}px/0.92 Anton;{estilo};white-space:nowrap">{l}</div>'
    return f"""<div style="position:absolute;left:60px;right:40px;top:50%;transform:translateY(-50%)">{out}</div>
<div class="arroba" style="left:60px;bottom:70px;color:{CINZA}">@seraphimbr_ {('· ' + rot.upper()) if rot else ''}</div>"""


def m_numero(t, rot, s):
    """número gigante vazado como protagonista"""
    n = numero_de(t) or "1"
    titulo = destacar(re.sub(r"\b" + n + r"\b", "", limpar(t), count=1).strip())
    return f"""<div style="position:absolute;left:40px;top:40px;font:900px/0.85 Anton;color:transparent;-webkit-text-stroke:6px {OURO};letter-spacing:-20px">{n}</div>
<div style="position:absolute;right:60px;top:120px;width:300px;height:300px;border-radius:50%;background:radial-gradient(circle,rgba(245,166,35,.35),transparent 70%)"></div>
<div style="position:absolute;left:70px;right:70px;bottom:150px;font:{tam(len(limpar(t)),130,110,92,78)}px/1.02 Anton;text-transform:uppercase">{titulo}</div>
<div style="position:absolute;left:70px;bottom:90px;width:160px;height:8px;background:{OURO}"></div>
<div class="arroba" style="right:70px;bottom:80px;color:{CINZA}">@seraphimbr_</div>"""


def m_jornal(t, rot, s):
    """capa de jornal em papel, manchete serifada"""
    barras = "".join(f'<div style="height:14px;background:#cfc8bb;margin:14px 0;width:{90 - (k * 13) % 35}%"></div>' for k in range(9))
    return f"""<div style="position:absolute;inset:0;background:{PAPEL};color:#141210">
<div style="margin:70px 70px 0;border-bottom:6px double #141210;padding-bottom:18px;display:flex;justify-content:space-between;align-items:flex-end">
<div style="font:96px/1 Play;letter-spacing:-1px">O Seraphim</div><div style="font:800 24px Inter;letter-spacing:3px;color:#6a6258">EDIÇÃO EXTRA</div></div>
<div style="margin:12px 70px 0;font:800 22px Inter;letter-spacing:4px;color:#6a6258;border-bottom:2px solid #141210;padding-bottom:12px">{(rot or 'TECNOLOGIA E NEGÓCIOS').upper()} · IA · AUTOMAÇÃO</div>
<div style="margin:46px 70px 0;font:{tam(len(limpar(t)),150,124,104,88)}px/1.02 DMSerif;letter-spacing:-1px">{destacar(t, 'gv')}</div>
<div style="display:flex;gap:40px;margin:50px 70px 0"><div style="flex:1">{barras}</div>
<div style="width:330px;height:330px;background:{PRETO};display:flex;align-items:center;justify-content:center;filter:grayscale(1) contrast(1.2)"><img src="{SERA}/{POSES[s % 6]}.png" style="height:300px"></div></div>
<div class="arroba" style="left:70px;bottom:70px;color:#6a6258">@seraphimbr_</div></div>
<style>.gv{{color:#B86E00;font-style:italic}}</style>"""


def m_chat(t, rot, s):
    """conversa de WhatsApp: o título vira a mensagem que chegou"""
    return f"""<div style="position:absolute;inset:0;background:#0b141a"></div>
<div style="position:absolute;left:0;right:0;top:60px;height:130px;background:#1f2c34;display:flex;align-items:center;gap:26px;padding:0 60px">
<div style="width:84px;height:84px;border-radius:50%;background:{OURO}"></div><div><div style="font:800 40px Inter">Cliente</div><div style="font:500 28px Inter;color:#8696a0">online</div></div></div>
<div style="position:absolute;left:60px;right:160px;top:300px;background:#202c33;border-radius:8px 40px 40px 40px;padding:40px 46px;font:800 {tam(len(limpar(t)),92,78,66,58)}px/1.15 Inter">{destacar(t)}
<div style="text-align:right;font:500 28px Inter;color:#8696a0;margin-top:14px">14:02</div></div>
<div style="position:absolute;right:60px;top:{'860' if len(limpar(t)) > 28 else '760'}px;background:#005c4b;border-radius:40px 8px 40px 40px;padding:26px 40px;font:500 44px Inter;color:#e9edef">digitando<span class="g">...</span></div>
<div style="position:absolute;left:60px;right:60px;bottom:90px;font:500 34px Inter;color:#8696a0;text-align:center">@seraphimbr_</div>"""


def m_terminal(t, rot, s):
    """janela de terminal com o título sendo digitado"""
    return f"""<div style="position:absolute;inset:0;background:radial-gradient(circle at 70% 20%,rgba(245,166,35,.18),transparent 50%),{PRETO}"></div>
<div style="position:absolute;left:60px;right:60px;top:170px;bottom:200px;border-radius:30px;background:#111114;border:2px solid #2a2a31;box-shadow:0 40px 120px rgba(0,0,0,.7);overflow:hidden">
<div style="height:80px;background:#1b1b20;display:flex;align-items:center;gap:16px;padding:0 34px">
<i style="width:24px;height:24px;border-radius:50%;background:#ff5f57"></i><i style="width:24px;height:24px;border-radius:50%;background:#febc2e"></i><i style="width:24px;height:24px;border-radius:50%;background:#28c840"></i>
<span style="margin-left:24px;font:500 26px Jet;color:{CINZA}">seraphim@ia: ~</span></div>
<div style="padding:60px 54px;font:500 34px/1.6 Jet;color:{CINZA}">$ seraphim --analisar<br><span class="g">✓</span> pronto em 0,3s<br><br>
<div style="font:800 {tam(len(limpar(t)),104,88,74,62)}px/1.15 Jet;color:{BRANCO};text-transform:uppercase">&gt; {destacar(t)}<span style="display:inline-block;width:.55em;height:1em;background:{OURO};vertical-align:middle;margin-left:10px"></span></div></div></div>
<div class="arroba" style="left:60px;bottom:110px;color:{CINZA}">@seraphimbr_</div>"""


def m_alerta(t, rot, s):
    """faixas de atenção (zebrado dourado/preto) + triângulo"""
    zeb = f"repeating-linear-gradient(-45deg,{OURO} 0 50px,{PRETO} 50px 100px)"
    return f"""<div style="position:absolute;left:0;right:0;top:0;height:120px;background:{zeb}"></div>
<div style="position:absolute;left:0;right:0;bottom:0;height:120px;background:{zeb}"></div>
<div style="position:absolute;left:50%;top:230px;transform:translateX(-50%);width:0;height:0;border-left:190px solid transparent;border-right:190px solid transparent;border-bottom:330px solid {OURO}"></div>
<div style="position:absolute;left:0;right:0;top:330px;text-align:center;font:230px/1 Anton;color:{PRETO}">!</div>
<div style="position:absolute;left:70px;right:70px;top:640px;text-align:center;font:800 30px Inter;letter-spacing:8px;color:{OURO}">{(rot or 'ATENÇÃO').upper()}</div>
<div style="position:absolute;left:60px;right:60px;top:710px;text-align:center;font:{tam(len(limpar(t)),140,116,96,82)}px/1.02 Anton;text-transform:uppercase">{destacar(t)}</div>
<div class="arroba" style="left:0;right:0;bottom:150px;text-align:center;color:{CINZA}">@seraphimbr_</div>"""


def m_pergunta(t, rot, s):
    """ponto de interrogação gigante saindo da tela + pergunta em serifa itálica"""
    return f"""<div style="position:absolute;right:-160px;top:-140px;font:1150px/1 Play;color:{OURO};opacity:.95">?</div>
<div style="position:absolute;left:70px;right:300px;bottom:170px;font:italic {tam(len(limpar(t)),120,100,84,72)}px/1.08 Play">{destacar(t)}</div>
<div style="position:absolute;left:70px;bottom:110px;font:800 26px Inter;letter-spacing:5px;color:{CINZA}">{(rot or 'PERGUNTA SÉRIA').upper()} · @seraphimbr_</div>"""


def m_dividido(t, rot, s):
    """tela dividida: metade de cima escura com ✕, metade de baixo dourada com ✓, título na faixa"""
    return f"""<div style="position:absolute;left:0;right:0;top:0;height:50%;background:#16161a"></div>
<div style="position:absolute;left:0;right:0;bottom:0;height:50%;background:{OURO}"></div>
<div style="position:absolute;left:70px;top:90px;font:800 34px Inter;letter-spacing:6px;color:{CINZA}">ANTES · <span style="font-weight:500;letter-spacing:1px">@seraphimbr_</span></div>
<div style="position:absolute;right:70px;top:60px;font:260px/1 Inter;font-weight:800;color:#3a3a42">✕</div>
<div style="position:absolute;left:70px;bottom:90px;font:800 34px Inter;letter-spacing:6px;color:{PRETO}">DEPOIS</div>
<div style="position:absolute;right:70px;bottom:40px;font:260px/1 Inter;font-weight:800;color:{PRETO}">✓</div>
<div style="position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);background:{PRETO};padding:50px 70px;font:{tam(len(limpar(t)),120,100,84,72)}px/1.02 Anton;text-transform:uppercase;box-shadow:0 30px 80px rgba(0,0,0,.6)">{destacar(t)}</div>
<div class="arroba" style="left:70px;top:150px;display:none;color:{CINZA}">@seraphimbr_</div>"""


def m_postit(t, rot, s):
    """bilhete colado num quadro escuro"""
    giro = [-4, 3, -2][s % 3]
    return f"""<div style="position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.08) 2px,transparent 2.5px);background-size:30px 30px"></div>
<div style="position:absolute;left:110px;right:110px;top:260px;height:820px;background:{OURO};transform:rotate({giro}deg);box-shadow:0 50px 100px rgba(0,0,0,.7);padding:110px 70px 60px;color:{PRETO}">
<div style="position:absolute;left:50%;top:-30px;transform:translateX(-50%);width:80px;height:80px;border-radius:50%;background:{VERM};box-shadow:0 10px 20px rgba(0,0,0,.4)"></div>
<div style="font:800 28px Space;letter-spacing:5px;margin-bottom:30px">{(rot or 'LEMBRETE').upper()}</div>
<div style="font:{tam(len(limpar(t)),118,98,82,70)}px/1.05 Archivo;text-transform:uppercase">{limpar(t)}</div></div>
<div class="arroba" style="left:0;right:0;bottom:120px;text-align:center;color:{CINZA}">@seraphimbr_</div>"""


def m_notificacoes(t, rot, s):
    """pilha de notificações de celular; a de cima traz o título"""
    def card(y, giro, op, txt=""):
        corpo = (f'<div style="font:800 46px/1.2 Inter;color:{PRETO}">{txt}</div>' if txt else
                 '<div style="height:22px;width:70%;background:#d9d4c8;border-radius:11px"></div><div style="height:22px;width:45%;background:#e6e1d6;border-radius:11px;margin-top:16px"></div>')
        return (f'<div style="position:absolute;left:70px;right:70px;top:{y}px;background:{PAPEL};border-radius:40px;padding:36px 40px;display:flex;gap:30px;align-items:center;'
                f'transform:rotate({giro}deg);opacity:{op};box-shadow:0 30px 80px rgba(0,0,0,.55)">'
                f'<div style="flex:0 0 110px;height:110px;border-radius:28px;background:{OURO};display:flex;align-items:center;justify-content:center"><img src="{ICONE}" style="width:80px;border-radius:50%"></div>'
                f'<div style="flex:1">{corpo}</div></div>')
    return f"""<div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 30%,rgba(245,166,35,.22),transparent 55%)"></div>
<div style="position:absolute;left:0;right:0;top:110px;text-align:center;font:500 150px/1 Space;letter-spacing:-4px">09:41</div>
<div style="position:absolute;left:0;right:0;top:270px;text-align:center;font:500 34px Inter;color:{CINZA}">quinta-feira, agora</div>
{card(820, 2.5, .5)}{card(700, -1.5, .8)}{card(420, 0, 1, destacar(t))}
<div class="arroba" style="left:0;right:0;bottom:100px;text-align:center;color:{CINZA}">@seraphimbr_</div>"""


def m_alvo(t, rot, s):
    """anéis concêntricos (alvo/radar) com o título no centro"""
    aneis = "".join(f'<div style="position:absolute;left:50%;top:50%;width:{d}px;height:{d}px;margin:-{d // 2}px 0 0 -{d // 2}px;border-radius:50%;border:{3 if k % 2 else 10}px solid rgba(245,166,35,{.15 + .12 * (k % 3)})"></div>'
                    for k, d in enumerate([1500, 1250, 1000, 760, 540]))
    return f"""{aneis}<div style="position:absolute;left:50%;top:50%;width:24px;height:24px;margin:-12px;border-radius:50%;background:{OURO};box-shadow:0 0 60px {OURO}"></div>
<div style="position:absolute;left:90px;right:90px;top:50%;transform:translateY(-50%);text-align:center;font:{tam(len(limpar(t)),120,98,82,70)}px/1.02 Bebas;letter-spacing:2px;text-transform:uppercase;text-shadow:0 10px 50px #000;background:rgba(10,10,12,.55);padding:40px 30px;border-radius:30px">{destacar(t)}</div>
<div class="arroba" style="left:0;right:0;bottom:90px;text-align:center;color:{CINZA}">@seraphimbr_</div>"""


def m_mascote(t, rot, s):
    """Sera em destaque + manchete no terço de baixo"""
    pill = f'<div style="background:{OURO};color:{PRETO};font:800 30px Inter;letter-spacing:3px;padding:14px 28px;border-radius:12px;text-transform:uppercase">{rot[:26]}</div>' if rot else ""
    return f"""<div style="position:absolute;inset:0;background:radial-gradient(circle at 78% 28%,rgba(245,166,35,.30),transparent 42%)"></div>
<img src="{SERA}/{POSES[s % 6]}.png" style="position:absolute;left:50%;top:110px;transform:translateX(-50%);height:740px">
<div style="position:absolute;left:70px;right:70px;bottom:150px;display:flex;flex-direction:column;align-items:flex-start;gap:28px">{pill}
<div style="font:{tam(len(limpar(t)),160,136,112,96)}px/1.0 Anton;text-transform:uppercase">{destacar(t)}</div></div>
<div class="arroba" style="left:70px;bottom:80px;color:{CINZA}">@seraphimbr_</div>"""


def m_lista(t, rot, s):
    """caderno de checklist: título como item principal marcado e linhas de lista"""
    linhas = "".join(f'<div style="display:flex;align-items:center;gap:30px;margin-top:40px;opacity:{.9 - k * .2}"><div style="width:70px;height:70px;border:5px solid {OURO};border-radius:16px"></div>'
                     f'<div style="height:24px;flex:1;max-width:{560 - k * 90}px;background:#2a2a31;border-radius:12px"></div></div>' for k in range(3))
    return f"""<div style="position:absolute;left:70px;right:70px;top:140px;font:800 30px Inter;letter-spacing:6px;color:{OURO}">{(rot or 'CHECKLIST').upper()}</div>
<div style="position:absolute;left:70px;right:70px;top:230px;display:flex;gap:34px">
<div style="flex:0 0 110px;height:110px;border-radius:24px;background:{OURO};color:{PRETO};font:800 80px/110px Inter;text-align:center">✓</div>
<div style="font:{tam(len(limpar(t)),118,98,82,70)}px/1.05 Mont;font-weight:900;text-transform:uppercase;letter-spacing:-2px">{destacar(t)}</div></div>
<div style="position:absolute;left:70px;right:70px;bottom:250px">{linhas}</div>
<div class="arroba" style="left:70px;bottom:110px;color:{CINZA}">@seraphimbr_</div>"""


MODELOS = {
    "tipografia": m_tipografia, "numero": m_numero, "jornal": m_jornal, "chat": m_chat, "terminal": m_terminal,
    "alerta": m_alerta, "pergunta": m_pergunta, "dividido": m_dividido, "postit": m_postit,
    "notificacoes": m_notificacoes, "alvo": m_alvo, "mascote": m_mascote, "lista": m_lista,
}


def escolher(titulo, rotulo="", recentes=()):
    """modelo que combina com o título e que NÃO foi usado nas últimas capas"""
    t, r = limpar(titulo).lower(), (rotulo or "").lower()
    ok = dict.fromkeys(MODELOS, 1.0)
    if not numero_de(titulo):
        ok.pop("numero")
    if not t.endswith("?"):
        ok["pergunta"] = 0.3
    else:
        ok["pergunta"] = 2.0; ok["chat"] = 1.5
    if any(k in t + r for k in ("erro", "perigo", "golpe", "cuidado", "alerta", "senha", "vazamento", "perde")):
        ok["alerta"] = 2.0
    if any(k in t + r for k in ("antes", "depois", " vs", "x ", "mito")):
        ok["dividido"] = 2.0
    if any(k in t + r for k in ("notícia", "novidade", "semana", "2026", "lança")):
        ok["jornal"] = 2.0
    if numero_de(titulo):
        ok["numero"] = 2.0; ok["lista"] = 1.5
    ok["mascote"] = 0.5
    if len(t) > 24:
        ok.pop("tipografia", None)
    bloqueados = set(list(recentes)[-8:])
    cand = {k: v for k, v in ok.items() if k not in bloqueados} or ok
    import random
    rnd = random.Random(semente(titulo) + len(recentes))
    return rnd.choices(list(cand), weights=list(cand.values()))[0]


def html_capa(titulo, rotulo="", modelo="", modo="reels"):
    s = semente(titulo)
    modelo = modelo if modelo in MODELOS else escolher(titulo, rotulo)
    corpo = MODELOS[modelo](titulo, rotulo or "", s)
    altura, topo = (1920, 240) if modo == "reels" else (1350, -45)
    return f"""<html><head><meta charset="utf-8"><style>{BASE} body{{height:{altura}px}} .safe{{top:{topo}px}}</style></head>
<body><div class="safe">{corpo}</div></body></html>"""


async def gerar_varias(itens):
    """itens: [{titulo, rotulo?, modelo?, saida: Path, modo?}] -> JPG"""
    from PIL import Image
    async with async_playwright() as p:
        nav = await p.chromium.launch()
        tmp = RAIZ / "_capa_tmp.html"
        for it in itens:
            modo = it.get("modo", "reels")
            pg = await nav.new_page(viewport={"width": 1080, "height": 1920 if modo == "reels" else 1350})
            tmp.write_text(html_capa(it["titulo"], it.get("rotulo", ""), it.get("modelo", ""), modo), encoding="utf-8")
            await pg.goto(tmp.as_uri())
            await pg.wait_for_timeout(300)
            png = await pg.screenshot()
            await pg.close()
            Path(it["saida"]).parent.mkdir(parents=True, exist_ok=True)
            Image.open(io.BytesIO(png)).convert("RGB").save(it["saida"], quality=92)
        tmp.unlink(missing_ok=True)
        await nav.close()


if __name__ == "__main__":
    a = sys.argv
    asyncio.run(gerar_varias([{"titulo": a[1], "saida": Path(a[2]), "modelo": a[3] if len(a) > 3 else ""}]))
    print("capa:", a[2])
