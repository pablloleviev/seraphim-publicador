"""Posts estáticos da grade: QUA 28/10 (sócio solo) e DOM 01/11 (dupla ou Pabllo solo)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from grade_1026_base import *

def qua():
    corpo = f"""
<div class='papel'></div>
<div class='abs' style='left:0;top:0;width:1080px;height:1350px;background:{MARFIM}'></div>
<div class='papel'></div>
<!-- bloco preto-tinta com corte assimétrico -->
<div class='abs' style='left:56px;top:56px;width:968px;height:862px;background:{INK};overflow:hidden;clip-path:polygon(0 0,100% 0,100% 82%,86% 100%,0 100%)'>
  <div class='abs' style='inset:0;background:radial-gradient(60% 70% at 36% 30%,#161c2b 0%,{INK} 72%)'></div>
  <svg class='abs' style='left:0;top:0' width='968' height='862'><path d='M-10 600 H470 L700 330 H1000' fill='none' stroke='{AZUL}' stroke-width='16' stroke-linecap='square'/></svg>
  <img src='{SOCIO}' class='abs' style='left:-10px;top:78px;width:900px;filter:drop-shadow(-16px 14px 26px rgba(0,0,0,.6)) saturate(.97) contrast(1.03)'>
  <!-- vidro: refração leve sobre a linha azul, em área vazia -->
  <div class='abs' style='left:640px;top:120px;width:300px;height:170px;border-radius:26px;background:linear-gradient(135deg,rgba(255,255,255,.16),rgba(255,255,255,.03));
       backdrop-filter:blur(10px) saturate(1.5);border:1.5px solid rgba(255,255,255,.26);box-shadow:0 24px 50px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.4)'>
    <div class='abs sh' style='left:26px;top:26px;font-size:20px;letter-spacing:4px;color:{MARFIM}'>SERAPHIM</div>
    <div class='abs st' style='left:26px;top:70px;right:20px;font-size:29px;line-height:1.25;color:{MARFIM}'>Tecnologia com método.</div>
  </div>
</div>
<div class='abs sh' style='left:72px;top:946px;width:940px;font-size:92px;line-height:1.0;letter-spacing:-2.4px;color:{INK}'>Tecnologia que começa <span class='az'>ouvindo a operação.</span></div>
<div class='abs' style='left:72px;top:1246px;width:120px;height:8px;background:{AZUL}'></div>
<div class='arr' style='left:72px;top:1274px;color:{INK};font-size:26px'>{ARROBA}</div>
<div class='arr' style='right:72px;top:1274px;color:{INK};font-size:26px;letter-spacing:3px'>SALVE ›</div>
"""
    return pagina(corpo, 1350, fundo=MARFIM, cor=INK)

def dom():
    corpo = f"""
<div class='abs' style='inset:0;background:radial-gradient(90% 60% at 20% 100%,#1a1f33 0%,{INK} 70%)'></div>
<div class='abs sh' style='left:72px;top:78px;width:936px;font-size:100px;line-height:1.0;letter-spacing:-2.6px;color:{MARFIM};z-index:30'>Construir tecnologia é <span style='color:{LAV}'>construir clareza.</span></div>
<svg class='abs' style='left:0;top:0;z-index:5' width='1080' height='1350'><path d='M72 372 H640 L720 452 H1008' fill='none' stroke='{AZUL}' stroke-width='10' stroke-linecap='square'/></svg>
<!-- camada de fundo: máscara arquitetônica (arco) com o sócio -->
<div class='abs' style='left:520px;top:430px;width:488px;height:740px;border-radius:244px 244px 0 0;overflow:hidden;background:linear-gradient(180deg,#232a44,#11141f);box-shadow:inset 0 0 80px rgba(0,0,0,.6),0 30px 70px rgba(0,0,0,.5);z-index:10'>
  <div class='abs' style='left:0;right:0;bottom:0;height:60%;background:radial-gradient(70% 90% at 50% 100%,rgba(184,166,255,.28),transparent 70%)'></div>
  <img src='{SOCIO}' class='abs' style='left:-86px;top:48px;width:660px;filter:drop-shadow(0 18px 24px rgba(0,0,0,.55))'>
</div>
<div class='abs' style='left:300px;top:640px;width:420px;height:420px;border-radius:50%;background:{LAV};filter:blur(120px);opacity:.30;z-index:8'></div>
<div class='abs' style='left:0;top:1170px;width:1080px;height:180px;background:{MARFIM};z-index:12'><div class='papel'></div></div>
<img src='{PABLLO}' class='abs' style='left:-70px;top:560px;width:790px;z-index:20;filter:drop-shadow(26px 14px 24px rgba(184,166,255,.5))'>
<div class='abs' style='left:740px;top:1196px;width:290px;z-index:25;color:{INK}'>
  <div class='sh' style='font-size:24px;letter-spacing:5px;color:{AZUL}'>SERAPHIM</div>
  <div class='st' style='font-size:27px;line-height:1.3;margin-top:8px;color:{INK}'>Entender a rotina primeiro.</div>
</div>
<div class='arr' style='left:740px;top:1322px;z-index:25;color:{INK};font-size:20px'>{ARROBA}</div>
"""
    return pagina(corpo, 1350)

if __name__ == "__main__":
    S = SAIDA
    rodar([(S / "2026-10-28_qua_post/capa.jpg", qua(), 1350), (S / "2026-11-01_dom_post/capa.jpg", dom(), 1350)])
