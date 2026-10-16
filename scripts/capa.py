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
import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from marca import ARROBA, USUARIO, INSTAGRAM_URL
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
@font-face{{font-family:Oswald;src:url({FONTES}/oswald-700.woff2)}}
@font-face{{font-family:BigSh;src:url({FONTES}/big-shoulders-display-900.woff2)}}
@font-face{{font-family:Sora;src:url({FONTES}/sora-700.woff2)}}
@font-face{{font-family:Syne;src:url({FONTES}/syne-800.woff2)}}
@font-face{{font-family:Unbounded;src:url({FONTES}/unbounded-800.woff2)}}
@font-face{{font-family:Fraunces;src:url({FONTES}/fraunces-900.woff2)}}
@font-face{{font-family:Instrument;src:url({FONTES}/instrument-serif-400.woff2)}}
@font-face{{font-family:Manrope;font-weight:500;src:url({FONTES}/manrope-500.woff2)}}
@font-face{{font-family:Manrope;font-weight:800;src:url({FONTES}/manrope-800.woff2)}}
@font-face{{font-family:SpaceB;src:url({FONTES}/space-grotesk-700.woff2)}}
*{{margin:0;box-sizing:border-box}}
body{{width:1080px;background:{PRETO};position:relative;overflow:hidden;color:{BRANCO};font-family:Inter}}
.safe{{position:absolute;left:0;width:1080px;height:1440px;overflow:hidden}}
.g{{color:{OURO}}}
.arroba{{position:absolute;font:500 26px var(--fb);letter-spacing:1px}}
/* acabamento: grão de filme, papel, vidro fosco, sombras suaves, recorte rasgado */
.grao{{position:absolute;inset:0;pointer-events:none;z-index:50;mix-blend-mode:overlay;opacity:var(--grao,.35);
  background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 1.4 -.2'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}}
.vinheta{{position:absolute;inset:0;pointer-events:none;z-index:49;background:radial-gradient(ellipse at 50% 45%,transparent 55%,rgba(0,0,0,.55))}}
.papel{{background-color:{PAPEL};background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='400'><filter id='p'><feTurbulence type='fractalNoise' baseFrequency='.04' numOctaves='5'/><feColorMatrix values='0 0 0 0 .55  0 0 0 0 .5  0 0 0 0 .42  0 0 0 .18 0'/></filter><rect width='100%' height='100%' filter='url(%23p)'/></svg>")}}
.vidro{{background:rgba(255,255,255,.08);backdrop-filter:blur(28px) saturate(1.4);-webkit-backdrop-filter:blur(28px) saturate(1.4);
  border:1.5px solid rgba(255,255,255,.18);box-shadow:0 30px 80px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.25)}}
.sombra{{box-shadow:0 2px 4px rgba(0,0,0,.2),0 18px 40px rgba(0,0,0,.35),0 60px 120px rgba(0,0,0,.35)}}
.rasgado{{clip-path:polygon(0 3%,6% 0,13% 2%,21% 0,30% 3%,38% 1%,47% 3%,55% 0,63% 2%,72% 0,80% 3%,88% 1%,95% 3%,100% 1%,99% 22%,100% 45%,98% 70%,100% 97%,93% 100%,85% 97%,76% 100%,68% 98%,59% 100%,50% 97%,41% 100%,33% 98%,24% 100%,15% 97%,7% 100%,0 98%,2% 75%,0 50%,1% 25%)}}
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
        out += f'<div style="font:{fs}px/0.92 var(--fd);{estilo};white-space:nowrap">{l}</div>'
    return f"""<div style="position:absolute;left:60px;right:40px;top:50%;transform:translateY(-50%)">{out}</div>
<div class="arroba" style="left:60px;bottom:70px;color:{CINZA}">{ARROBA} {('· ' + rot.upper()) if rot else ''}</div>"""


def m_numero(t, rot, s):
    """número gigante vazado como protagonista"""
    n = numero_de(t) or "1"
    titulo = destacar(re.sub(r"\b" + n + r"\b", "", limpar(t), count=1).strip())
    return f"""<div style="position:absolute;left:40px;top:40px;font:900px/0.85 var(--fd);color:transparent;-webkit-text-stroke:6px {OURO};letter-spacing:-20px">{n}</div>
<div style="position:absolute;right:60px;top:120px;width:300px;height:300px;border-radius:50%;background:radial-gradient(circle,rgba(245,166,35,.35),transparent 70%)"></div>
<div style="position:absolute;left:70px;right:70px;bottom:150px;font:{tam(len(limpar(t)),130,110,92,78)}px/1.02 var(--fd);text-transform:uppercase">{titulo}</div>
<div style="position:absolute;left:70px;bottom:90px;width:160px;height:8px;background:{OURO}"></div>
<div class="arroba" style="right:70px;bottom:80px;color:{CINZA}">{ARROBA}</div>"""


def m_jornal(t, rot, s):
    """capa de jornal em papel, manchete serifada"""
    barras = "".join(f'<div style="height:14px;background:#cfc8bb;margin:14px 0;width:{90 - (k * 13) % 35}%"></div>' for k in range(9))
    return f"""<div style="position:absolute;inset:0;background:{PAPEL};color:#141210">
<div style="margin:70px 70px 0;border-bottom:6px double #141210;padding-bottom:18px;display:flex;justify-content:space-between;align-items:flex-end">
<div style="font:96px/1 var(--fs);letter-spacing:-1px">O Seraphim</div><div style="font:800 24px var(--fb);letter-spacing:3px;color:#6a6258">EDIÇÃO EXTRA</div></div>
<div style="margin:12px 70px 0;font:800 22px var(--fb);letter-spacing:4px;color:#6a6258;border-bottom:2px solid #141210;padding-bottom:12px">{(rot or 'TECNOLOGIA E NEGÓCIOS').upper()} · IA · AUTOMAÇÃO</div>
<div style="margin:46px 70px 0;font:{tam(len(limpar(t)),150,124,104,88)}px/1.02 var(--fs2);letter-spacing:-1px">{destacar(t, 'gv')}</div>
<div style="display:flex;gap:40px;margin:50px 70px 0"><div style="flex:1">{barras}</div>
<div style="width:330px;height:330px;background:{PRETO};display:flex;align-items:center;justify-content:center;filter:grayscale(1) contrast(1.2)"><img src="{SERA}/{POSES[s % 6]}.png" style="height:300px"></div></div>
<div class="arroba" style="left:70px;bottom:70px;color:#6a6258">{ARROBA}</div></div>
<style>.gv{{color:#B86E00;font-style:italic}}</style>"""


def m_chat(t, rot, s):
    """conversa de WhatsApp: o título vira a mensagem que chegou"""
    return f"""<div style="position:absolute;inset:0;background:#0b141a"></div>
<div style="position:absolute;left:0;right:0;top:60px;height:130px;background:#1f2c34;display:flex;align-items:center;gap:26px;padding:0 60px">
<div style="width:84px;height:84px;border-radius:50%;background:{OURO}"></div><div><div style="font:800 40px var(--fb)">Cliente</div><div style="font:500 28px var(--fb);color:#8696a0">online</div></div></div>
<div style="position:absolute;left:60px;right:160px;top:300px;background:#202c33;border-radius:8px 40px 40px 40px;padding:40px 46px;font:800 {tam(len(limpar(t)),92,78,66,58)}px/1.15 var(--fb)">{destacar(t)}
<div style="text-align:right;font:500 28px var(--fb);color:#8696a0;margin-top:14px">14:02</div></div>
<div style="position:absolute;right:60px;top:{'860' if len(limpar(t)) > 28 else '760'}px;background:#005c4b;border-radius:40px 8px 40px 40px;padding:26px 40px;font:500 44px var(--fb);color:#e9edef">digitando<span class="g">...</span></div>
<div style="position:absolute;left:60px;right:60px;bottom:90px;font:500 34px var(--fb);color:#8696a0;text-align:center">{ARROBA}</div>"""


def m_terminal(t, rot, s):
    """janela de terminal com o título sendo digitado"""
    return f"""<div style="position:absolute;inset:0;background:radial-gradient(circle at 70% 20%,rgba(245,166,35,.18),transparent 50%),{PRETO}"></div>
<div style="position:absolute;left:60px;right:60px;top:170px;bottom:200px;border-radius:30px;background:#111114;border:2px solid #2a2a31;box-shadow:0 40px 120px rgba(0,0,0,.7);overflow:hidden">
<div style="height:80px;background:#1b1b20;display:flex;align-items:center;gap:16px;padding:0 34px">
<i style="width:24px;height:24px;border-radius:50%;background:#ff5f57"></i><i style="width:24px;height:24px;border-radius:50%;background:#febc2e"></i><i style="width:24px;height:24px;border-radius:50%;background:#28c840"></i>
<span style="margin-left:24px;font:500 26px Jet;color:{CINZA}">seraphim@ia: ~</span></div>
<div style="padding:60px 54px;font:500 34px/1.6 Jet;color:{CINZA}">$ seraphim --analisar<br><span class="g">✓</span> pronto em 0,3s<br><br>
<div style="font:800 {tam(len(limpar(t)),104,88,74,62)}px/1.15 Jet;color:{BRANCO};text-transform:uppercase">&gt; {destacar(t)}<span style="display:inline-block;width:.55em;height:1em;background:{OURO};vertical-align:middle;margin-left:10px"></span></div></div></div>
<div class="arroba" style="left:60px;bottom:110px;color:{CINZA}">{ARROBA}</div>"""


def m_alerta(t, rot, s):
    """faixas de atenção (zebrado dourado/preto) + triângulo"""
    zeb = f"repeating-linear-gradient(-45deg,{OURO} 0 50px,{PRETO} 50px 100px)"
    return f"""<div style="position:absolute;left:0;right:0;top:0;height:120px;background:{zeb}"></div>
<div style="position:absolute;left:0;right:0;bottom:0;height:120px;background:{zeb}"></div>
<div style="position:absolute;left:50%;top:230px;transform:translateX(-50%);width:0;height:0;border-left:190px solid transparent;border-right:190px solid transparent;border-bottom:330px solid {OURO}"></div>
<div style="position:absolute;left:0;right:0;top:330px;text-align:center;font:230px/1 var(--fd);color:{PRETO}">!</div>
<div style="position:absolute;left:70px;right:70px;top:640px;text-align:center;font:800 30px var(--fb);letter-spacing:8px;color:{OURO}">{(rot or 'ATENÇÃO').upper()}</div>
<div style="position:absolute;left:60px;right:60px;top:710px;text-align:center;font:{tam(len(limpar(t)),140,116,96,82)}px/1.02 var(--fd);text-transform:uppercase">{destacar(t)}</div>
<div class="arroba" style="left:0;right:0;bottom:150px;text-align:center;color:{CINZA}">{ARROBA}</div>"""


def m_pergunta(t, rot, s):
    """ponto de interrogação gigante saindo da tela + pergunta em serifa itálica"""
    return f"""<div style="position:absolute;right:-160px;top:-140px;font:1150px/1 var(--fs);color:{OURO};opacity:.95">?</div>
<div style="position:absolute;left:70px;right:300px;bottom:170px;font:italic {tam(len(limpar(t)),120,100,84,72)}px/1.08 var(--fs)">{destacar(t)}</div>
<div style="position:absolute;left:70px;bottom:110px;font:800 26px var(--fb);letter-spacing:5px;color:{CINZA}">{(rot or 'PERGUNTA SÉRIA').upper()} · {ARROBA}</div>"""


def m_dividido(t, rot, s):
    """tela dividida: metade de cima escura com ✕, metade de baixo dourada com ✓, título na faixa"""
    return f"""<div style="position:absolute;left:0;right:0;top:0;height:50%;background:#16161a"></div>
<div style="position:absolute;left:0;right:0;bottom:0;height:50%;background:{OURO}"></div>
<div style="position:absolute;left:70px;top:90px;font:800 34px var(--fb);letter-spacing:6px;color:{CINZA}">ANTES · <span style="font-weight:500;letter-spacing:1px">{ARROBA}</span></div>
<div style="position:absolute;right:70px;top:60px;font:260px/1 var(--fb);font-weight:800;color:#3a3a42">✕</div>
<div style="position:absolute;left:70px;bottom:90px;font:800 34px var(--fb);letter-spacing:6px;color:{PRETO}">DEPOIS</div>
<div style="position:absolute;right:70px;bottom:40px;font:260px/1 var(--fb);font-weight:800;color:{PRETO}">✓</div>
<div style="position:absolute;left:0;right:0;top:50%;transform:translateY(-50%);background:{PRETO};padding:50px 70px;font:{tam(len(limpar(t)),120,100,84,72)}px/1.02 var(--fd);text-transform:uppercase;box-shadow:0 30px 80px rgba(0,0,0,.6)">{destacar(t)}</div>
<div class="arroba" style="left:70px;top:150px;display:none;color:{CINZA}">{ARROBA}</div>"""


def m_postit(t, rot, s):
    """bilhete colado num quadro escuro"""
    giro = [-4, 3, -2][s % 3]
    return f"""<div style="position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.08) 2px,transparent 2.5px);background-size:30px 30px"></div>
<div style="position:absolute;left:110px;right:110px;top:260px;height:820px;background:{OURO};transform:rotate({giro}deg);box-shadow:0 50px 100px rgba(0,0,0,.7);padding:110px 70px 60px;color:{PRETO}">
<div style="position:absolute;left:50%;top:-30px;transform:translateX(-50%);width:80px;height:80px;border-radius:50%;background:{VERM};box-shadow:0 10px 20px rgba(0,0,0,.4)"></div>
<div style="font:800 28px Space;letter-spacing:5px;margin-bottom:30px">{(rot or 'LEMBRETE').upper()}</div>
<div style="font:{tam(len(limpar(t)),118,98,82,70)}px/1.05 Archivo;text-transform:uppercase">{limpar(t)}</div></div>
<div class="arroba" style="left:0;right:0;bottom:120px;text-align:center;color:{CINZA}">{ARROBA}</div>"""


def m_notificacoes(t, rot, s):
    """pilha de notificações de celular; a de cima traz o título"""
    def card(y, giro, op, txt=""):
        corpo = (f'<div style="font:800 46px/1.2 var(--fb);color:{PRETO}">{txt}</div>' if txt else
                 '<div style="height:22px;width:70%;background:#d9d4c8;border-radius:11px"></div><div style="height:22px;width:45%;background:#e6e1d6;border-radius:11px;margin-top:16px"></div>')
        return (f'<div style="position:absolute;left:70px;right:70px;top:{y}px;background:{PAPEL};border-radius:40px;padding:36px 40px;display:flex;gap:30px;align-items:center;'
                f'transform:rotate({giro}deg);opacity:{op};box-shadow:0 30px 80px rgba(0,0,0,.55)">'
                f'<div style="flex:0 0 110px;height:110px;border-radius:28px;background:{OURO};display:flex;align-items:center;justify-content:center"><img src="{ICONE}" style="width:80px;border-radius:50%"></div>'
                f'<div style="flex:1">{corpo}</div></div>')
    return f"""<div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 30%,rgba(245,166,35,.22),transparent 55%)"></div>
<div style="position:absolute;left:0;right:0;top:110px;text-align:center;font:500 150px/1 Space;letter-spacing:-4px">09:41</div>
<div style="position:absolute;left:0;right:0;top:270px;text-align:center;font:500 34px var(--fb);color:{CINZA}">quinta-feira, agora</div>
{card(820, 2.5, .5)}{card(700, -1.5, .8)}{card(420, 0, 1, destacar(t))}
<div class="arroba" style="left:0;right:0;bottom:100px;text-align:center;color:{CINZA}">{ARROBA}</div>"""


def m_alvo(t, rot, s):
    """anéis concêntricos (alvo/radar) com o título no centro"""
    aneis = "".join(f'<div style="position:absolute;left:50%;top:50%;width:{d}px;height:{d}px;margin:-{d // 2}px 0 0 -{d // 2}px;border-radius:50%;border:{3 if k % 2 else 10}px solid rgba(245,166,35,{.15 + .12 * (k % 3)})"></div>'
                    for k, d in enumerate([1500, 1250, 1000, 760, 540]))
    return f"""{aneis}<div style="position:absolute;left:50%;top:50%;width:24px;height:24px;margin:-12px;border-radius:50%;background:{OURO};box-shadow:0 0 60px {OURO}"></div>
<div style="position:absolute;left:90px;right:90px;top:50%;transform:translateY(-50%);text-align:center;font:{tam(len(limpar(t)),120,98,82,70)}px/1.02 var(--fd);letter-spacing:2px;text-transform:uppercase;text-shadow:0 10px 50px #000;background:rgba(10,10,12,.55);padding:40px 30px;border-radius:30px">{destacar(t)}</div>
<div class="arroba" style="left:0;right:0;bottom:90px;text-align:center;color:{CINZA}">{ARROBA}</div>"""


def m_mascote(t, rot, s):
    """Sera em destaque + manchete no terço de baixo"""
    pill = f'<div style="background:{OURO};color:{PRETO};font:800 30px var(--fb);letter-spacing:3px;padding:14px 28px;border-radius:12px;text-transform:uppercase">{rot[:26]}</div>' if rot else ""
    return f"""<div style="position:absolute;inset:0;background:radial-gradient(circle at 78% 28%,rgba(245,166,35,.30),transparent 42%)"></div>
<img src="{SERA}/{POSES[s % 6]}.png" style="position:absolute;left:50%;top:110px;transform:translateX(-50%);height:740px">
<div style="position:absolute;left:70px;right:70px;bottom:150px;display:flex;flex-direction:column;align-items:flex-start;gap:28px">{pill}
<div style="font:{tam(len(limpar(t)),160,136,112,96)}px/1.0 var(--fd);text-transform:uppercase">{destacar(t)}</div></div>
<div class="arroba" style="left:70px;bottom:80px;color:{CINZA}">{ARROBA}</div>"""


def m_lista(t, rot, s):
    """caderno de checklist: título como item principal marcado e linhas de lista"""
    linhas = "".join(f'<div style="display:flex;align-items:center;gap:30px;margin-top:40px;opacity:{.9 - k * .2}"><div style="width:70px;height:70px;border:5px solid {OURO};border-radius:16px"></div>'
                     f'<div style="height:24px;flex:1;max-width:{560 - k * 90}px;background:#2a2a31;border-radius:12px"></div></div>' for k in range(3))
    return f"""<div style="position:absolute;left:70px;right:70px;top:140px;font:800 30px var(--fb);letter-spacing:6px;color:{OURO}">{(rot or 'CHECKLIST').upper()}</div>
<div style="position:absolute;left:70px;right:70px;top:230px;display:flex;gap:34px">
<div style="flex:0 0 110px;height:110px;border-radius:24px;background:{OURO};color:{PRETO};font:800 80px/110px var(--fb);text-align:center">✓</div>
<div style="font:{tam(len(limpar(t)),118,98,82,70)}px/1.05 var(--fw);font-weight:900;text-transform:uppercase;letter-spacing:-2px">{destacar(t)}</div></div>
<div style="position:absolute;left:70px;right:70px;bottom:250px">{linhas}</div>
<div class="arroba" style="left:70px;bottom:110px;color:{CINZA}">{ARROBA}</div>"""


# ---------------- modelos com IMAGEM (IA ou foto real; ver ingredientes.py) ----------------
def _img(im):
    return Path(im).resolve().as_uri() if im else ""


def m_foto(t, rot, s, im=""):
    """imagem sangrando a tela inteira com duotone dourado/preto e manchete embaixo"""
    lado = ["left", "right"][s % 2]
    return f"""<div style="position:absolute;inset:0;background:url({_img(im)}) center/cover;filter:grayscale(.35) contrast(1.1) brightness(.85)"></div>
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(10,10,12,.15) 0%,rgba(10,10,12,.1) 40%,rgba(10,10,12,.92) 72%,{PRETO} 100%)"></div>
<div style="position:absolute;inset:0;background:{OURO};mix-blend-mode:color;opacity:.22"></div>
<div style="position:absolute;left:70px;right:70px;bottom:150px;text-align:{lado}">
<div style="display:inline-block;font:800 26px var(--fb);letter-spacing:6px;color:{PRETO};background:{OURO};padding:12px 22px;margin-bottom:30px">{(rot or 'SERAPHIM').upper()[:24]}</div>
<div style="font:{tam(len(limpar(t)),150,124,104,88)}px/1 var(--fd);text-transform:uppercase;text-shadow:0 8px 40px rgba(0,0,0,.6)">{destacar(t)}</div></div>
<div class="arroba" style="{lado}:70px;bottom:85px;color:{CINZA}">{ARROBA}</div><div class="vinheta"></div>"""


def m_recorte(t, rot, s, im=""):
    """colagem: foto recortada em papel rasgado, fita adesiva e manchete serifada no papel"""
    giro = [-3, 2.5, -1.5][s % 3]
    return f"""<div class="papel" style="position:absolute;inset:0"></div>
<div style="position:absolute;left:90px;right:90px;top:110px;height:780px;transform:rotate({giro}deg)">
<div class="rasgado sombra" style="position:absolute;inset:0;background:url({_img(im)}) center/cover;filter:contrast(1.05) saturate(.8)"></div>
<div style="position:absolute;left:40%;top:-26px;width:220px;height:60px;background:rgba(245,166,35,.75);transform:rotate({-giro * 2}deg)"></div></div>
<div style="position:absolute;left:70px;right:70px;top:960px;color:#141210">
<div style="font:800 24px var(--fb);letter-spacing:6px;color:#8a6a2a;margin-bottom:18px">{(rot or 'RECORTE DO DIA').upper()[:28]}</div>
<div style="font:{tam(len(limpar(t)),120,100,84,72)}px/1.04 var(--fs2)">{destacar(t, 'gv')}</div></div>
<div class="arroba" style="left:70px;bottom:70px;color:#6a6258">{ARROBA}</div>
<style>.gv{{color:#B86E00;font-style:italic}}</style>"""


def m_vidro(t, rot, s, im=""):
    """imagem de fundo + cartão de vidro fosco com a manchete e um ícone"""
    import ingredientes
    ic = ingredientes.icone(["sparkles", "zap", "target", "rocket", "lightbulb", "bot", "trending-up"][s % 7], OURO, 90, 1.8)
    return f"""<div style="position:absolute;inset:0;background:url({_img(im)}) center/cover;filter:brightness(.7) saturate(1.1)"></div>
<div style="position:absolute;inset:0;background:radial-gradient(circle at 30% 20%,rgba(245,166,35,.25),transparent 50%)"></div>
<div class="vidro" style="position:absolute;left:70px;right:70px;top:50%;transform:translateY(-45%);border-radius:48px;padding:70px 60px">
<div style="display:flex;align-items:center;gap:20px;margin-bottom:34px">{ic}<span style="font:800 26px var(--fb);letter-spacing:5px;color:{OURO}">{(rot or '').upper()[:26]}</span></div>
<div style="font:{tam(len(limpar(t)),112,96,80,68)}px/1.06 var(--fw);letter-spacing:-1px">{destacar(t)}</div></div>
<div class="arroba" style="left:0;right:0;bottom:90px;text-align:center;color:{BRANCO};opacity:.8">{ARROBA}</div>"""


def m_polaroid(t, rot, s, im=""):
    """foto revelada (polaroid) inclinada sobre a mesa escura, legenda escrita embaixo"""
    giro = [4, -5, 3][s % 3]
    return f"""<div style="position:absolute;inset:0;background:radial-gradient(circle at 50% 35%,#2a2420,{PRETO} 70%)"></div>
<div class="sombra" style="position:absolute;left:150px;right:150px;top:120px;background:#f7f4ec;padding:34px 34px 150px;transform:rotate({giro}deg)">
<div style="height:640px;background:url({_img(im)}) center/cover;filter:sepia(.25) contrast(1.05)"></div>
<div style="position:absolute;left:34px;right:34px;bottom:40px;font:italic 56px/1.1 Instrument;color:#2a2620;text-align:center">{(rot or 'olha isso').lower()[:30]}</div></div>
<div style="position:absolute;left:70px;right:70px;bottom:150px;font:{tam(len(limpar(t)),118,98,82,70)}px/1.04 var(--fd);text-transform:uppercase">{destacar(t)}</div>
<div class="arroba" style="left:70px;bottom:85px;color:{CINZA}">{ARROBA}</div><div class="vinheta"></div>"""


def m_icone(t, rot, s, im=""):
    """ícone gigante em traço dourado como protagonista (sem foto)"""
    import ingredientes
    t2 = limpar(t).lower()
    mapa = [("carro", "car"), ("oficina", "wrench"), ("dinheiro", "coins"), ("venda", "shopping-cart"), ("cliente", "users"),
            ("whats", "message-circle"), ("mensag", "message-square"), ("senha", "lock"), ("segur", "shield-check"), ("tempo", "hourglass"),
            ("hora", "clock"), ("email", "mail"), ("e-mail", "mail"), ("celular", "smartphone"), ("ia", "bot"), ("robô", "bot"),
            ("planilha", "calculator"), ("agenda", "calendar-check"), ("nota", "receipt"), ("ideia", "lightbulb"), ("cresc", "trending-up")]
    nome = next((n for k, n in mapa if k in t2), ["sparkles", "target", "rocket", "zap", "brain"][s % 5])
    ic = ingredientes.icone(nome, OURO, 620, 1.1)
    return f"""<div style="position:absolute;inset:0;background:radial-gradient(circle at 70% 30%,rgba(245,166,35,.16),transparent 55%)"></div>
<div style="position:absolute;right:-60px;top:60px;opacity:.95;filter:drop-shadow(0 0 40px rgba(245,166,35,.35))">{ic}</div>
<div style="position:absolute;left:70px;right:70px;bottom:150px;font:{tam(len(limpar(t)),128,108,90,76)}px/1.02 var(--fw);letter-spacing:-2px">{destacar(t)}</div>
<div class="arroba" style="left:70px;bottom:85px;color:{CINZA}">{(rot.upper() + ' · ') if rot else ''}{ARROBA}</div>"""


# ---------------- modelos desenhados no Figma ("Seraphim — Sistema de Capas", 16/10/2026) ----------------
# assinatura fixa da marca em todos: filete dourado + @ + número da peça (o resto muda de capa para capa)
def _sig(s, escuro=True):
    cor = CINZA if escuro else "#3a3630"
    return (f'<div style="position:absolute;left:80px;bottom:108px;width:60px;height:4px;background:{OURO}"></div>'
            f'<div style="position:absolute;left:160px;bottom:96px;font:500 26px SpaceB;color:{cor}">{ARROBA}</div>'
            f'<div style="position:absolute;right:80px;bottom:96px;font:500 24px Jet;color:{cor}">{s % 97 + 1:02d}</div>')


def f_manifesto(t, rot, s):
    """declaração em serifa pesada gigante, última frase em dourado"""
    return f"""<div style="position:absolute;left:80px;top:110px;font:800 24px SpaceB;letter-spacing:7px;color:{OURO}">{(rot or 'MANIFESTO').upper()[:26]}</div>
<div style="position:absolute;left:80px;right:80px;top:200px;font:{tam(len(limpar(t)),150,130,108,92)}px/0.95 Fraunces;color:{BRANCO}">{destacar(t)}</div>{_sig(s)}"""


def f_blueprint(t, rot, s):
    """grade técnica dourada (planta de arquitetura), moldura e legenda de figura"""
    grade = (f"background-image:linear-gradient(rgba(245,166,35,.09) 1px,transparent 1px),linear-gradient(90deg,rgba(245,166,35,.09) 1px,transparent 1px),"
             f"linear-gradient(rgba(245,166,35,.25) 1px,transparent 1px),linear-gradient(90deg,rgba(245,166,35,.25) 1px,transparent 1px);"
             f"background-size:60px 60px,60px 60px,300px 300px,300px 300px")
    return f"""<div style="position:absolute;inset:0;{grade}"></div>
<div style="position:absolute;left:80px;right:80px;top:300px;border:2px solid {OURO};padding:30px 30px 60px;background:rgba(10,10,12,.6)">
<div style="font:500 26px Jet;color:{OURO};margin-bottom:24px">// {(rot or 'arquitetura').upper()[:24]}</div>
<div style="font:{tam(len(limpar(t)),96,84,72,62)}px/1.08 Unbounded;color:{BRANCO}">{destacar(t)}</div></div>
<div style="position:absolute;left:80px;top:960px;font:500 24px Jet;color:{CINZA}">Fig. {s % 9 + 1:02d} — do processo ao código</div>{_sig(s)}"""


def f_ensaio(t, rot, s):
    """página de ensaio em papel, serifa clássica e dourado escuro"""
    return f"""<div class="papel" style="position:absolute;inset:0"></div>
<div style="position:absolute;left:80px;top:110px;font:800 24px SpaceB;letter-spacing:7px;color:#B86E00">{(rot or 'ENSAIO').upper()[:22]} Nº {s % 40 + 1}</div>
<div style="position:absolute;left:80px;right:80px;top:160px;height:3px;background:{PRETO}"></div>
<div style="position:absolute;left:80px;right:80px;top:200px;font:{tam(len(limpar(t)),132,116,98,84)}px/0.98 Instrument;color:{PRETO}">{destacar(t, 'gv')}</div>{_sig(s, False)}
<style>.gv{{color:#B86E00}}</style>"""


def f_produto(t, rot, s):
    """cartão de vidro com tela de sistema (ordem de serviço) e brilho dourado ao fundo"""
    linhas = "".join(f'<div style="height:84px;border-radius:18px;background:#16161a;margin-bottom:26px;display:flex;align-items:center;justify-content:space-between;padding:0 30px">'
                     f'<div style="height:26px;width:{[380,300,440,260][k]}px;border-radius:13px;background:rgba(142,142,150,.5)"></div>'
                     f'<div style="width:100px;height:40px;border-radius:20px;background:{OURO if k < 2 else "#26262c"}"></div></div>' for k in range(4))
    return f"""<div style="position:absolute;left:300px;top:-200px;width:900px;height:900px;border-radius:50%;background:{OURO};opacity:.35;filter:blur(200px)"></div>
<div class="vidro" style="position:absolute;left:80px;right:80px;top:240px;border-radius:40px;padding:50px">
<div style="font:500 28px SpaceB;color:{OURO};margin-bottom:34px">{(rot or 'AUTOFLOW · ordem de serviço')[:34]}</div>{linhas}</div>
<div style="position:absolute;left:80px;right:80px;top:930px;font:{tam(len(limpar(t)),96,84,72,62)}px/1.04 Unbounded;color:{BRANCO}">{destacar(t)}</div>{_sig(s)}"""


def f_interrogacao(t, rot, s):
    """interrogação dourada gigante em serifa itálica + pergunta em itálico"""
    return f"""<div style="position:absolute;left:500px;top:-300px;font:italic 1150px/1 Instrument;color:{OURO}">?</div>
<div style="position:absolute;left:80px;width:600px;bottom:180px;font:italic {tam(len(limpar(t)),118,100,86,74)}px/0.98 Instrument;color:{BRANCO}">{destacar(t)}</div>{_sig(s)}"""


def f_dado(t, rot, s):
    """número/dado gigante condensado + frase de apoio (só com dado real)"""
    m = re.search(r"\d{1,3}(?:[.,]\d+)?\s?%?", limpar(t))
    n = m.group(0).replace(" ", "") if m else "1"
    resto = limpar(t).replace(m.group(0), "", 1).strip() if m else limpar(t)
    return f"""<div style="position:absolute;left:60px;top:120px;font:430px/1 Anton;color:{OURO}">{n}</div>
<div style="position:absolute;left:80px;right:80px;top:760px;height:2px;background:#26262c"></div>
<div style="position:absolute;left:80px;right:80px;top:800px;font:800 58px/1.18 var(--fb);color:{BRANCO}">{resto}</div>{_sig(s)}"""


DO_FIGMA = {"manifesto": f_manifesto, "blueprint": f_blueprint, "ensaio": f_ensaio, "produto": f_produto,
            "interrogacao": f_interrogacao, "dado": f_dado}


COM_IMAGEM = {"foto": m_foto, "recorte": m_recorte, "vidro": m_vidro, "polaroid": m_polaroid}


MODELOS = {
    "tipografia": m_tipografia, "numero": m_numero, "jornal": m_jornal, "chat": m_chat, "terminal": m_terminal,
    "alerta": m_alerta, "pergunta": m_pergunta, "dividido": m_dividido, "postit": m_postit,
    "notificacoes": m_notificacoes, "alvo": m_alvo, "mascote": m_mascote, "lista": m_lista, "icone": m_icone,
    **COM_IMAGEM, **DO_FIGMA,
}

# pares de fonte (manchete condensada, manchete larga, serifa, serifa 2, texto). Sorteados por capa.
PARES = [
    ("Anton", "Mont", "Play", "DMSerif", "Inter"),
    ("Oswald", "Sora", "Fraunces", "DMSerif", "Manrope"),
    ("BigSh", "Unbounded", "Instrument", "Fraunces", "Inter"),
    ("Bebas", "Syne", "Play", "Instrument", "SpaceB"),
    ("Anton", "Unbounded", "Fraunces", "DMSerif", "Manrope"),
    ("Oswald", "Mont", "Instrument", "Play", "Inter"),
]


def escolher(titulo, rotulo="", recentes=(), tem_imagem=False):
    """modelo que combina com o título e que NÃO foi usado nas últimas capas"""
    t, r = limpar(titulo).lower(), (rotulo or "").lower()
    ok = dict.fromkeys(MODELOS, 1.0)
    for k in COM_IMAGEM:
        if tem_imagem:
            ok[k] = 1.6   # com imagem nova, as capas com foto/IA ganham mais chance
        else:
            ok.pop(k)
    if not numero_de(titulo):
        ok.pop("numero"); ok.pop("dado", None)
    if not t.endswith("?"):
        ok["interrogacao"] = 0.2
    if not any(k in t + r for k in ("autoflow", "oficina", "sistema", "ordem", "produto")):
        ok["produto"] = 0.3
    for k in ("manifesto", "blueprint", "ensaio"):
        ok[k] = 1.4   # desenhados no Figma: padrão principal do relançamento
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


def html_capa(titulo, rotulo="", modelo="", modo="reels", imagem=""):
    s = semente(titulo)
    if modelo in COM_IMAGEM and not imagem:
        modelo = ""
    modelo = modelo if modelo in MODELOS else escolher(titulo, rotulo, tem_imagem=bool(imagem))
    corpo = MODELOS[modelo](titulo, rotulo or "", s, imagem) if modelo in COM_IMAGEM else MODELOS[modelo](titulo, rotulo or "", s)
    fd, fw, fs, fs2, fb = PARES[(s >> 5) % len(PARES)]
    grao = [0, .25, .4, .55][(s >> 9) % 4]
    altura, topo = (1920, 240) if modo == "reels" else (1350, -45)
    # reels: a imagem/fundo ocupa a tela toda, o conteúdo fica na zona segura
    return f"""<html><head><meta charset="utf-8"><style>{BASE} body{{height:{altura}px}} .safe{{top:{topo}px}}
:root{{--fd:{fd};--fw:{fw};--fs:{fs};--fs2:{fs2};--fb:{fb};--grao:{grao}}}</style></head>
<body><div class="safe">{corpo}</div><div class="grao"></div></body></html>"""


# encolhe qualquer texto grande que estoure a largura/altura do seu bloco ou da tela (fontes largas variam)
AJUSTAR = """() => { for (const el of document.querySelectorAll('.safe div')) {
  const cs = getComputedStyle(el); let fs = parseFloat(cs.fontSize);
  if (fs < 50 || !el.textContent.trim() || /^-/.test(el.style.right) || /^-/.test(el.style.left)) continue;
  const fora = () => el.scrollWidth > el.clientWidth + 2 || el.getBoundingClientRect().right > 1040;
  let n = 0; while (fora() && n++ < 40) { fs *= 0.95; el.style.fontSize = fs + 'px'; } } }"""


async def gerar_varias(itens):
    """itens: [{titulo, rotulo?, modelo?, saida: Path, modo?}] -> JPG"""
    from PIL import Image
    async with async_playwright() as p:
        nav = await p.chromium.launch()
        tmp = RAIZ / "_capa_tmp.html"
        for it in itens:
            modo = it.get("modo", "reels")
            pg = await nav.new_page(viewport={"width": 1080, "height": 1920 if modo == "reels" else 1350})
            tmp.write_text(html_capa(it["titulo"], it.get("rotulo", ""), it.get("modelo", ""), modo, it.get("imagem", "")), encoding="utf-8")
            await pg.goto(tmp.as_uri())
            await pg.evaluate("document.fonts.ready")
            await pg.evaluate(AJUSTAR)
            await pg.wait_for_timeout(400)
            png = await pg.screenshot()
            await pg.close()
            Path(it["saida"]).parent.mkdir(parents=True, exist_ok=True)
            Image.open(io.BytesIO(png)).convert("RGB").save(it["saida"], quality=92)
        tmp.unlink(missing_ok=True)
        await nav.close()


if __name__ == "__main__":
    a = sys.argv
    asyncio.run(gerar_varias([{"titulo": a[1], "saida": Path(a[2]), "modelo": a[3] if len(a) > 3 else "",
                               "imagem": a[4] if len(a) > 4 else "", "rotulo": a[5] if len(a) > 5 else ""}]))
    print("capa:", a[2])
