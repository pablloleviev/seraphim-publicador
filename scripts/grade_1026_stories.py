"""Stories da grade (1080x1920): placas de fundo/pergunta. Os stickers interativos (enquete, caixa, quiz, lembrete) são nativos e entram na hora de agendar."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from grade_1026_base import *

H = 1920
def q(texto, cls="az", y=470, tam=104, cor=MARFIM, w=900):
    return f"<div class='abs sh' style='left:90px;top:{y}px;width:{w}px;font-size:{tam}px;line-height:1.04;letter-spacing:-2.6px;color:{cor}'>{realce(texto, cls)}</div>"
def tag(txt, bg, fg, y=330):
    return f"<div class='abs sh' style='left:90px;top:{y}px;background:{bg};color:{fg};font-size:28px;letter-spacing:5px;padding:12px 22px;border-radius:10px'>{txt}</div>"
def guia(txt, cor):
    return f"<div class='abs st' style='left:90px;right:90px;top:1180px;font-size:34px;color:{cor};opacity:.7;letter-spacing:1px'>{txt}</div>"

def seg():
    return pagina(f"<div class='abs' style='inset:0;background:radial-gradient(80% 50% at 80% 100%,rgba(47,107,255,.35),transparent 70%)'></div>{marca(MARFIM,90,260)}"
        + tag("ENQUETE", AZUL, MARFIM, 400) + q("Depois que a oficina fecha, sua cabeça ainda está trabalhando?", "ac", 500, 96), H)
def ter():
    return pagina(f"<div class='abs' style='inset:0;background:{LAV}'></div>{marca(INK,90,260)}"
        + tag("CAIXA DE PERGUNTA", INK, LAV, 400) + q("Qual tarefa repetitiva mais rouba sua atenção?", "az", 500, 98, INK) , H, fundo=LAV, cor=INK, extra_css=f".az{{color:{INK};background:linear-gradient(transparent 70%,{MARFIM} 70% 94%,transparent 94%)}}")
def ter_resposta():
    return pagina(f"<div class='papel'></div><div class='abs' style='inset:0;background:{MARFIM}'></div><div class='papel'></div>{marca(INK,90,260)}"
        + tag("RESPOSTA DE VOCÊS", INK, MARFIM, 400)
        + f"<div class='abs' style='left:90px;right:90px;top:520px;height:760px;background:#fff;border-radius:40px;box-shadow:0 30px 0 rgba(11,13,18,.12);border:3px dashed {AZUL};display:flex;align-items:center;justify-content:center'>"
          f"<div class='sh' style='font-size:44px;color:{CINZA};letter-spacing:3px;text-align:center;line-height:1.3'>MODELO<br><span style='font-size:30px;font-weight:400;letter-spacing:1px'>a resposta escolhida entra aqui,<br>sem nome e sem dados pessoais</span></div></div>", H, fundo=MARFIM, cor=INK)
def qua():
    return pagina(f"<div class='abs' style='inset:0;background:{PAINEL}'></div>{marca(MARFIM,90,260)}"
        + tag("BASTIDOR DO RETRATO", ACIDO, INK, 400)
        + f"<div class='abs' style='left:90px;top:520px;width:430px;height:540px;overflow:hidden;border-radius:26px;box-shadow:0 20px 0 rgba(0,0,0,.4)'><img src='{(RAIZ/'assets/pessoas/socio.jpg').as_uri()}' style='width:760px;margin:-60px 0 0 -170px'></div>"
        + f"<div class='abs' style='left:560px;top:520px;width:430px;height:540px;overflow:hidden;border-radius:26px;background:{MARFIM};box-shadow:0 20px 0 rgba(0,0,0,.4)'><img src='{SOCIO}' style='width:760px;margin:-60px 0 0 -170px'></div>"
        + f"<div class='abs sh' style='left:90px;top:1090px;font-size:30px;letter-spacing:4px;color:{CINZA}'>ORIGINAL</div><div class='abs sh' style='left:560px;top:1090px;font-size:30px;letter-spacing:4px;color:{AZUL}'>RECORTE + COR</div>"
        + q("Antes de entrar no post, o retrato passa por máscara e cor.", "lv", 1180, 66, MARFIM), H)
def qui():
    return pagina(f"<div class='abs' style='inset:0;background:radial-gradient(70% 40% at 20% 100%,rgba(199,255,61,.14),transparent 70%)'></div>{marca(MARFIM,90,260)}"
        + tag("QUIZ", ACIDO, INK, 400) + q("Onde a informação mais se perde?", "ac", 500, 108), H)
def sex():
    itens = ["Pendências sem resposta", "Conhecimento em uma pessoa só", "Papel, conversa ou memória", "Rotina que recomeça do zero", "Clareza para o próximo mês"]
    lin = "".join(f"<div class='abs' style='left:90px;top:{620 + k * 118}px;display:flex;align-items:center;gap:28px'><div style='width:58px;height:58px;border:6px solid {AZUL};border-radius:14px;background:rgba(255,255,255,.6)'></div><div class='sh' style='font-size:44px;letter-spacing:-.8px'>{t}</div></div>" for k, t in enumerate(itens))
    return pagina(f"<div class='abs' style='inset:0;background:{MARFIM}'></div><div class='papel'></div>{marca(INK,90,260)}"
        + tag("FIM DE MÊS", ACIDO, INK, 400) + f"<div class='abs sh' style='left:90px;top:500px;font-size:46px;color:{INK}'>Checklist</div>{lin}", H, fundo=MARFIM, cor=INK)
def sab():
    return pagina(f"<div class='abs' style='inset:0;background:radial-gradient(70% 45% at 50% 60%,rgba(199,255,61,.16),transparent 70%)'></div>{marca(MARFIM,90,260)}"
        + tag("ENQUETE", ACIDO, INK, 400) + q("Pior susto da rotina?", "ac", 500, 124) +
        f"<div class='abs' style='left:90px;top:1000px;width:240px;height:14px;background:{AZUL}'></div>", H)
def dom():
    return pagina(f"<div class='abs' style='inset:0;background:radial-gradient(80% 45% at 20% 100%,rgba(184,166,255,.28),transparent 70%)'></div>{marca(MARFIM,90,260)}"
        + tag("CAIXA DE PERGUNTA", LAV, INK, 400) + q("Qual operação você gostaria de enxergar com mais clareza em novembro?", "lv", 500, 90), H)

if __name__ == "__main__":
    S = SAIDA / "stories"
    rodar([(S / "seg_1_enquete.jpg", seg(), H), (S / "ter_1_caixa.jpg", ter(), H), (S / "ter_2_resposta-modelo.jpg", ter_resposta(), H),
           (S / "qua_1_bastidor-retrato.jpg", qua(), H), (S / "qui_1_quiz.jpg", qui(), H), (S / "sex_1_checklist.jpg", sex(), H),
           (S / "sab_1_enquete.jpg", sab(), H), (S / "dom_1_caixa.jpg", dom(), H)])
