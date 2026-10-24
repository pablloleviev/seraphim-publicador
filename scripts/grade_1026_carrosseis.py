"""Carrosséis da grade: TER 27/10 (IA na operação, 6 slides) e SEX 30/10 (checklist de fim de mês, 7 slides)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from grade_1026_base import *

def rod(n, total, cor, claro=False):
    pts = "".join(f"<i style='display:block;height:10px;border-radius:5px;width:{34 if i == n else 10}px;background:{cor};opacity:{1 if i == n else .28}'></i>" for i in range(1, total + 1))
    return (f"<div class='arr' style='left:72px;bottom:56px;color:{cor}'>{ARROBA}</div>"
            f"<div class='abs' style='left:50%;bottom:62px;transform:translateX(-50%);display:flex;gap:8px;z-index:40'>{pts}</div>"
            f"<div class='arr' style='right:72px;bottom:56px;color:{cor};letter-spacing:3px'>{'›' if n < total else ''}</div>")

def titulo(t, cor, y=190, tam=88, cls="az", w=936):
    return f"<div class='abs sh' style='left:72px;top:{y}px;width:{w}px;font-size:{tam}px;line-height:1.03;letter-spacing:-2.2px;color:{cor}'>{realce(t, cls)}</div>"

def card(x, y, w, h, fill, linha=None, r=22, rot=0, barras=3, bcor=None, op=1):
    bcor = bcor or (INK if fill in (MARFIM, LAV) else MARFIM)
    bars = "".join(f"<rect x='{w*.1}' y='{h*.2 + i*h*.22}' width='{w*(.8 if i != barras-1 else .5)}' height='{max(6, h*.08)}' rx='4' fill='{bcor}' opacity='.35'/>" for i in range(barras))
    st = f"stroke='{linha}' stroke-width='3'" if linha else ""
    return (f"<g transform='translate({x} {y}) rotate({rot} {w/2} {h/2})' opacity='{op}'><rect width='{w}' height='{h}' rx='{r}' fill='{fill}' {st}/>{bars}</g>")

def fio(d, cor, w=4, dash=None, op=1):
    da = f"stroke-dasharray='{dash}'" if dash else ""
    return f"<path d='{d}' fill='none' stroke='{cor}' stroke-width='{w}' stroke-linecap='round' {da} opacity='{op}'/>"

def svg(inner, y=0, h=1350, dy=-120):
    return f"<svg class='abs' style='left:0;top:{y}px' width='1080' height='{h}' viewBox='0 {y} 1080 {h}'><g transform='translate(0 {dy})'>{inner}</g></svg>"

def ter():
    L = []
    # 1 capa (escuro, lavanda): cartões que ajudam x nó de decisão
    d1 = svg(
        card(72, 800, 250, 120, LAV, rot=-4) + card(120, 960, 250, 120, MARFIM, rot=3) + card(60, 1110, 250, 120, LAV, rot=-2, op=.9) +
        fio("M322 860 C520 860 520 1010 640 1010", LAV, 4) + fio("M370 1020 C500 1020 560 1010 640 1010", LAV, 4) + fio("M310 1170 C500 1170 540 1010 640 1010", LAV, 4) +
        f"<circle cx='640' cy='1010' r='18' fill='{LAV}'/>" +
        fio("M658 1010 H760", CINZA, 4, "4 14") +
        f"<rect x='770' y='900' width='238' height='220' rx='30' fill='none' stroke='{MARFIM}' stroke-width='4' stroke-dasharray='14 12'/>"
        f"<text x='889' y='1018' text-anchor='middle' font-family='SH' font-weight='700' font-size='30' fill='{MARFIM}' letter-spacing='3'>DECISÃO</text>"
        f"<text x='889' y='1056' text-anchor='middle' font-family='SH' font-weight='700' font-size='30' fill='{LAV}' letter-spacing='3'>SUA</text>"
        f"<text x='190' y='780' font-family='SH' font-weight='700' font-size='22' fill='{LAV}' letter-spacing='5'>AJUDA</text>")
    L.append(pagina(f"<div class='abs' style='inset:0;background:radial-gradient(70% 45% at 15% 100%,rgba(184,166,255,.20),transparent 70%)'></div>{marca()}"
        f"<div class='abs sh' style='left:72px;top:150px;font-size:24px;letter-spacing:6px;color:{LAV}'>IA NA OPERAÇÃO</div>"
        + titulo("O que ela *ajuda* a fazer — e o que não *decide* por você.", MARFIM, 210, 84, "lv") + d1 + rod(1, 6, MARFIM)))
    # 2 ivory: caos -> organizado
    d2 = svg(card(70, 760, 220, 110, LAV, rot=-9) + card(190, 880, 220, 110, INK, rot=7, op=.9) + card(80, 1010, 220, 110, LAV, rot=4) + card(230, 1130, 200, 100, INK, rot=-6, op=.9) +
        fio("M440 990 H610", AZUL, 5) + f"<path d='M610 990 l-22 -16 v32z' fill='{AZUL}' transform='translate(30 0)'/>" +
        "".join(card(640, 770 + i * 96, 340, 76, [LAV, MARFIM][i % 2] if False else (LAV if i % 2 == 0 else "#fff"), linha=INK if i % 2 else None, r=18, barras=2) for i in range(5)) +
        f"<circle cx='1000' cy='{770 + 38}' r='11' fill='{ACIDO}' stroke='{INK}' stroke-width='3'/>")
    L.append(pagina(f"<div class='papel'></div>{marca(INK)}" + titulo("Ela pode *organizar* sinais e tarefas repetitivas.", INK, 190, 88, "az") + d2 + rod(2, 6, INK), fundo=MARFIM, cor=INK))
    # 3 lavanda: resumir
    d3 = svg("".join(card(60 + (i % 2) * 70, 790 + i * 58, 250, 62, MARFIM, r=14, barras=1, bcor=INK, op=.9, rot=(-3, 2, -1, 3, -2, 1)[i % 6]) for i in range(7)) +
        "".join(fio(f"M{320 + (i % 2) * 70} {821 + i * 58} C560 {821 + i * 58} 560 1010 690 1010", INK, 3, op=.8) for i in range(7)) +
        f"<rect x='690' y='850' width='318' height='320' rx='30' fill='{INK}'/>"
        + "".join(f"<rect x='720' y='{890 + j * 52}' width='{258 if j < 4 else 170}' height='16' rx='8' fill='{MARFIM}' opacity='.8'/>" for j in range(5)) +
        f"<rect x='720' y='1130' width='60' height='10' rx='5' fill='{ACIDO}'/>")
    L.append(pagina(marca(INK) + titulo("Ela pode *resumir* informação espalhada.", INK, 190, 88, "lv" if False else "az") + d3 + rod(3, 6, INK), fundo=LAV, cor=INK, extra_css=".az{color:%s;background:linear-gradient(transparent 68%%,%s 68%% 94%%,transparent 94%%)}" % (INK, MARFIM)))
    # 4 escuro: quem atende x ferramenta
    d4 = svg(f"<circle cx='360' cy='1010' r='150' fill='none' stroke='{LAV}' stroke-width='5'/><circle cx='360' cy='1010' r='96' fill='{LAV}'/>"
        f"<text x='360' y='1002' text-anchor='middle' font-family='SH' font-weight='700' font-size='26' fill='{INK}' letter-spacing='2'>QUEM</text><text x='360' y='1034' text-anchor='middle' font-family='SH' font-weight='700' font-size='26' fill='{INK}' letter-spacing='2'>ATENDE</text>" +
        "".join(fio(f"M{360 + 150 * __import__('math').cos(a)} {1010 + 150 * __import__('math').sin(a)} L{360 + 330 * __import__('math').cos(a)} {1010 + 250 * __import__('math').sin(a)}", LAV, 3, op=.8) +
                f"<circle cx='{360 + 330 * __import__('math').cos(a)}' cy='{1010 + 250 * __import__('math').sin(a)}' r='9' fill='{MARFIM}'/>" for a in (-1.15, -.7, -.25, .25, .7, 1.15)) +
        f"<rect x='800' y='930' width='208' height='160' rx='26' fill='none' stroke='{CINZA}' stroke-width='4' stroke-dasharray='12 12'/>"
        f"<text x='904' y='1018' text-anchor='middle' font-family='SH' font-weight='700' font-size='24' fill='{CINZA}' letter-spacing='2'>FERRAMENTA</text>"
        + fio("M690 960 L800 990", CINZA, 3, "3 10"))
    L.append(pagina(f"<div class='abs' style='inset:0;background:radial-gradient(60% 40% at 30% 80%,rgba(184,166,255,.16),transparent 70%)'></div>{marca()}"
        + titulo("Ela não conhece o seu cliente *melhor* do que quem atende.", MARFIM, 190, 84, "lv") + d4 + rod(4, 6, MARFIM)))
    # 5 ivory: três pilares humanos
    nomes = ["PRIORIDADE", "RESPONSA-\nBILIDADE", "CRITÉRIO"]
    pil = "".join(f"<rect x='{72 + i * 316}' y='800' width='296' height='{360 - i * 40}' rx='28' fill='{[INK, AZUL, LAV][i]}'/>"
                  f"<text x='{72 + i * 316 + 148}' y='{1100 - i * 40 - (30 if i == 1 else 0)}' text-anchor='middle' font-family='SH' font-weight='700' font-size='30' fill='{[MARFIM, MARFIM, INK][i]}' letter-spacing='1'>{nomes[i].split(chr(10))[0]}</text>"
                  + (f"<text x='{72 + i * 316 + 148}' y='{1100 - i * 40}' text-anchor='middle' font-family='SH' font-weight='700' font-size='30' fill='{MARFIM}'>{nomes[i].split(chr(10))[1]}</text>" if i == 1 else "") for i in range(3))
    d5 = svg(pil + f"<path d='M72 1200 H1008' stroke='{INK}' stroke-width='4'/><path d='M72 1190 V1210 M1008 1190 V1210' stroke='{INK}' stroke-width='4'/>"
        f"<rect x='410' y='1176' width='260' height='46' rx='23' fill='{ACIDO}'/><text x='540' y='1208' text-anchor='middle' font-family='SH' font-weight='700' font-size='24' fill='{INK}' letter-spacing='4'>FICA COM VOCÊ</text>"
        '')
    L.append(pagina(f"<div class='papel'></div>{marca(INK)}" + titulo("Ela não substitui *prioridade*, *responsabilidade* ou *critério*.", INK, 190, 78, "az") + d5 + rod(5, 6, INK), fundo=MARFIM, cor=INK))
    # 6 escuro/azul: amplia + pergunta
    d6 = svg(f"<rect x='455' y='830' width='170' height='170' rx='28' fill='none' stroke='{LAV}' stroke-width='3' opacity='.25'/><rect x='400' y='775' width='280' height='280' rx='40' fill='none' stroke='{LAV}' stroke-width='3' opacity='.4'/>"
        f"<rect x='335' y='710' width='410' height='410' rx='54' fill='none' stroke='{LAV}' stroke-width='3' opacity='.6'/><rect x='500' y='875' width='80' height='80' rx='16' fill='{AZUL}'/>")
    L.append(pagina(f"<div class='abs' style='inset:0;background:radial-gradient(80% 40% at 50% 70%,rgba(47,107,255,.28),transparent 70%)'></div>{marca()}"
        + titulo("Tecnologia boa *amplia* uma operação bem conduzida.", MARFIM, 190, 86, "lv") + d6
        + f"<div class='abs' style='left:72px;right:72px;top:1140px;background:{MARFIM};color:{INK};border-radius:30px;padding:34px 40px;font:700 40px/1.15 SH;letter-spacing:-.8px'>Onde você colocaria mais clareza na sua rotina?</div>"
        + rod(6, 6, MARFIM)))
    return L

def sex():
    reg = (f"<div class='abs' style='inset:0;background:repeating-linear-gradient(180deg,transparent 0 66px,rgba(47,107,255,.10) 66px 68px)'></div>"
           f"<div class='abs' style='left:118px;top:0;bottom:0;width:3px;background:rgba(47,107,255,.35)'></div>")
    def base(corpo, n, extra=""):
        return pagina(f"<div class='abs' style='inset:0;background:{MARFIM}'></div><div class='papel'></div>{reg}{marca(INK)}{corpo}{rod(n, 7, INK)}", fundo=MARFIM, cor=INK, extra_css=extra)
    def caixa(x, y, tam=120):
        return f"<div class='abs' style='left:{x}px;top:{y}px;width:{tam}px;height:{tam}px;border:7px solid {AZUL};border-radius:18px;background:rgba(255,255,255,.55)'></div>"
    def marca_acido(txt, x, y):
        return f"<div class='abs sh' style='left:{x}px;top:{y}px;background:{ACIDO};color:{INK};font-size:26px;letter-spacing:4px;padding:10px 20px;border-radius:10px'>{txt}</div>"
    L = []
    L.append(base(
        f"<div class='abs' style='left:340px;top:44px;width:400px;height:64px;background:{INK};border-radius:0 0 26px 26px'></div>"
        f"<div class='abs sh' style='left:150px;top:200px;font-size:26px;letter-spacing:6px;color:{AZUL}'>CHECKLIST · FIM DE MÊS</div>"
        f"<div class='abs sh' style='left:150px;top:260px;width:860px;font-size:112px;line-height:1.0;letter-spacing:-3px'>Antes de novembro:</div>"
        f"<div class='abs sh' style='left:150px;top:560px;width:860px;font-size:150px;line-height:.98;letter-spacing:-4px'><span style='background:linear-gradient(transparent 62%,{ACIDO} 62% 92%,transparent 92%)'>5 perguntas</span></div>"
        f"<div class='abs sh' style='left:150px;top:740px;width:860px;font-size:84px;line-height:1.05;letter-spacing:-2px'>que organizam a operação.</div>"
        f"<div class='abs st' style='left:150px;top:1090px;font-size:34px;color:#4b505c'>Arraste e responda uma por uma ›</div>", 1))
    qs = ["O que ficou pendente de resposta?", "O que só uma pessoa sabe explicar?", "Que informação ficou em papel, conversa ou memória?",
          "Qual rotina vai recomeçar do zero na segunda?", "O que você quer enxergar com clareza no próximo mês?"]
    lay = [("esq", 0), ("topo", 1), ("esq", 2), ("topo", 3), ("esq", 4)]
    for i, q in enumerate(qs):
        n = i + 2
        if lay[i][0] == "esq":
            corpo = (marca_acido(f"PERGUNTA {i+1}/5", 150, 330) + caixa(150, 440, 130) +
                     f"<div class='abs sh' style='left:150px;top:660px;width:850px;font-size:108px;line-height:1.04;letter-spacing:-2.8px'>{q}</div>")
        else:
            corpo = (f"<div class='abs sh' style='left:150px;top:300px;font-size:250px;line-height:1;letter-spacing:-8px;color:{AZUL}'>0{i+1}</div>" +
                     f"<div class='abs sh' style='left:150px;top:650px;width:850px;font-size:104px;line-height:1.05;letter-spacing:-2.6px'>{q}</div>" +
                     marca_acido(f"PERGUNTA {i+1}/5", 150, 1120) + caixa(860, 1110, 90))
        L.append(base(corpo, n))
    itens = ["Pendências sem resposta", "Conhecimento que mora em uma pessoa", "Informação em papel, conversa ou memória", "Rotina que recomeça do zero na segunda", "Clareza para o próximo mês"]
    lin = "".join(f"<div class='abs' style='left:150px;top:{300 + k * 118}px;display:flex;align-items:center;gap:30px'><div style='width:64px;height:64px;border:6px solid {AZUL};border-radius:14px;background:rgba(255,255,255,.55)'></div>"
                  f"<div class='sh' style='font-size:40px;letter-spacing:-.8px'>{t}</div></div>" for k, t in enumerate(itens))
    L.append(base(f"<div class='abs sh' style='left:150px;top:190px;font-size:26px;letter-spacing:6px;color:{AZUL}'>RESUMO</div>{lin}"
        f"<div class='abs sh' style='left:150px;top:980px;right:72px;background:{ACIDO};color:{INK};font-size:46px;line-height:1.1;letter-spacing:-1px;padding:30px 36px;border-radius:24px'>Salve para revisar antes de virar o mês.</div>", 7))
    return L

if __name__ == "__main__":
    S = SAIDA
    its = [(S / f"2026-10-27_ter_carrossel/slide-{i+1:02d}.jpg", h, 1350) for i, h in enumerate(ter())]
    its += [(S / f"2026-10-30_sex_carrossel/slide-{i+1:02d}.jpg", h, 1350) for i, h in enumerate(sex())]
    rodar(its)
