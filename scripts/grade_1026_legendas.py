"""Legendas (.md, uma por peça) da grade 26/10–01/11. Textos da legenda e do CTA vêm da grade aprovada pelo Pabllo; hashtags: 4–6 por peça, com #seraphimbr."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from grade_1026_base import SAIDA

PECAS = [
 ("2026-10-26_seg_reel", "SEG 26/10 · Reel", "A oficina fecha. A operação continua na cabeça.", "Identificação e compartilhamentos",
  "Quando o portão baixa, muita oficina ainda continua funcionando na cabeça de quem cuida dela. O ponto não é trabalhar menos por trabalhar menos. É não carregar sozinho o que a operação poderia deixar visível. Conheça o AutoFlow pelo link da bio.",
  "Conheça o AutoFlow pelo link da bio.", "#gestaodeoficina #oficinamecanica #gestaoautomotiva #autoflow #seraphimbr"),
 ("2026-10-27_ter_carrossel", "TER 27/10 · Carrossel (6 slides)", "O que uma IA pode fazer pela sua operação — e o que continua sendo decisão sua", "Comentários qualificados e salvamentos",
  "A conversa sobre IA ficou barulhenta porque ela mistura duas coisas: reduzir trabalho repetitivo e transferir responsabilidade. Uma ferramenta pode ajudar com a primeira. A segunda continua sendo humana. Em que parte da sua operação você sente mais ruído hoje?",
  "Em que parte da sua operação você sente mais ruído hoje?", "#inteligenciaartificial #gestaoempresarial #operacao #tecnologia #seraphimbr"),
 ("2026-10-28_qua_post", "QUA 28/10 · Post estático (retrato do sócio)", "Tecnologia que começa ouvindo a operação", "Humanização e confiança",
  "Antes de qualquer sistema, existe uma rotina real: gente atendendo, decidindo, corrigindo e tentando manter o dia em ordem. É daí que a Seraphim parte quando pensa tecnologia. A ferramenta precisa caber na operação — não obrigar a operação a caber na ferramenta.",
  "Salve para lembrar disso no próximo projeto.", "#tecnologia #sistemassobmedida #desenvolvimento #seraphimbr"),
 ("2026-10-29_qui_reel", "QUI 29/10 · Reel", "Seu negócio não precisa de mais uma aba aberta", "Compartilhamentos e alcance",
  "A ferramenta extra quase sempre parece uma solução no dia em que chega. Depois vira mais uma coisa para lembrar, abrir e conferir. Gestão começa a ganhar espaço quando você percebe o que não deveria estar espalhado. Envie para alguém que vive alternando entre tudo.",
  "Envie para alguém que vive alternando entre tudo.", "#produtividade #gestaoempresarial #organizacao #autoflow #seraphimbr"),
 ("2026-10-30_sex_carrossel", "SEX 30/10 · Carrossel (7 slides)", "Checklist de fim de mês para quem não quer começar novembro apagando incêndio", "Salvamentos",
  "Fim de mês não precisa ser só correria de fechamento. Dez minutos de pergunta certa podem mostrar onde a operação vai perder tempo de novo em novembro. Salve este checklist e use antes da próxima semana começar.",
  "Salve este checklist.", "#gestaoempresarial #checklist #fimdemes #organizacao #seraphimbr"),
 ("2026-10-31_sab_reel", "SÁB 31/10 · Reel", "O verdadeiro terror da operação? Descobrir tarde demais.", "Participar do contexto de Halloween com leveza",
  "O problema raramente é uma surpresa. É perceber a surpresa quando já virou urgência. Uma rotina mais visível muda a conversa antes que ela vire correção. Qual surpresa operacional você mais gostaria de evitar?",
  "Qual surpresa operacional você mais gostaria de evitar?", "#gestaoautomotiva #operacao #halloween #autoflow #seraphimbr"),
 ("2026-11-01_dom_post", "DOM 01/11 · Post estático (Pabllo + sócio)", "Construir tecnologia é construir clareza", "Marca, percepção e encerramento de semana",
  "Uma semana de conteúdo acaba. A vontade de deixar a operação mais clara, não. É isso que move a Seraphim: entender a rotina primeiro e construir a tecnologia a partir dela. Acompanhe a Seraphim para ver o que estamos construindo.",
  "Acompanhe a Seraphim para ver o que estamos construindo.", "#tecnologia #clareza #sistemassobmedida #seraphimbr"),
]
for pasta, rot, titulo, obj, legenda, cta, tags in PECAS:
    d = SAIDA / pasta
    d.mkdir(parents=True, exist_ok=True)
    n = len(tags.split())
    (d / "legenda.md").write_text(
        f"# {rot}\n\n**Peça:** {titulo}\n**Objetivo:** {obj}\n**Status:** prévia · aguardando aprovação humana · NÃO publicar · NÃO enfileirar\n\n"
        f"## Legenda\n\n{legenda}\n\n{tags}\n\n## CTA único\n\n{cta}\n\n## Checagem\n- Hashtags: {n} (limite 4–6, inclui #seraphimbr)\n- Sem preço, plano, prazo de teste, cliente, depoimento ou métrica.\n", encoding="utf-8")
    (d / "legenda.txt").write_text(f"{legenda}\n\n{tags}\n", encoding="utf-8")
    print("ok", pasta, n, "hashtags")
