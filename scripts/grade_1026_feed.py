"""feed-preview.jpg: 7 capas na ordem semanal + auditoria de variedade."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from grade_1026_base import *

P = [("2026-10-26_seg_reel/capa.jpg", "SEG 26 · Reel", "Azul-tinta (foto tingida)", "Oficina fechada, cabeça aberta", "Pátio + título", "Nenhuma", "Lento, desacelera"),
     ("2026-10-27_ter_carrossel/slide-01.jpg", "TER 27 · Carrossel", "Preto-tinta + lavanda", "IA: ajuda x decisão", "Diagrama cartões e fios", "Nenhuma", "Editorial, 6 slides"),
     ("2026-10-28_qua_post/capa.jpg", "QUA 28 · Post", "Marfim + preto + azul", "Confiança e escuta", "Retrato do sócio", "Sócio (solo)", "Estático, calmo"),
     ("2026-10-29_qui_reel/capa.jpg", "QUI 29 · Reel", "Preto-tinta + verde ácido", "Excesso de abas", "Tipografia", "Nenhuma", "Acelerado, corte seco"),
     ("2026-10-30_sex_carrossel/slide-01.jpg", "SEX 30 · Carrossel", "Marfim + azul + ácido", "Checklist de fim de mês", "Tipografia + caixa", "Nenhuma", "Utilitário, 7 slides"),
     ("2026-10-31_sab_reel/capa.jpg", "SÁB 31 · Reel", "Preto-tinta + ácido → azul", "Descobrir tarde demais", "Tipografia", "Nenhuma", "Choque curto, 14 s"),
     ("2026-11-01_dom_post/capa.jpg", "DOM 01 · Post", "Preto-tinta + lavanda + marfim", "Clareza e marca", "Dupla Pabllo + sócio", "Pabllo e sócio", "Estático, institucional")]
cel = "".join(f"<div style='position:relative;width:356px;height:445px;overflow:hidden'><img src='{(SAIDA/f).as_uri()}' style='width:100%;height:100%;object-fit:cover'>"
              f"<div style='position:absolute;left:0;right:0;bottom:0;padding:8px 10px;background:rgba(0,0,0,.72);font:700 17px SH;color:{ACIDO};letter-spacing:1px'>{r}</div></div>" for f, r, *_ in P)
lin = "".join(f"<tr><td class=b>{r}</td><td>{c}</td><td>{a}</td><td>{pf}</td><td>{pe}</td><td>{ri}</td></tr>" for _, r, c, a, pf, pe, ri in P)
corpo = (f"<div style='padding:36px 40px;'><div class='sh' style='font-size:44px;letter-spacing:-1px'>Grade 26/10 a 01/11 · <span class='ac'>prévia do feed</span></div>"
         f"<div style='display:grid;grid-template-columns:repeat(3,356px);gap:4px;margin:26px 0 30px'>{cel}</div>"
         f"<div class='sh' style='font-size:30px;margin-bottom:12px'>Auditoria de variedade</div>"
         f"<table style='border-collapse:collapse;width:100%;font:500 19px ST'><tr style='color:{CINZA};text-align:left'><th>Peça</th><th>Cor</th><th>Assunto</th><th>Ponto focal</th><th>Pessoas</th><th>Ritmo</th></tr>{lin}</table></div>")
css = "td,th{padding:9px 10px;border-top:1px solid #2a2f3b} td.b{font:700 19px SH;color:#C7FF3D}"
rodar([(SAIDA / "feed-preview.jpg", pagina(corpo, 2330, css), 2330)])
