"""
Monta a SEMANA DO RELANÇAMENTO (19–25/10/2026) na fila de aprovação, a partir do plano aprovado pelo Pabllo.
- Vídeos: pedidos/ (o workflow "Gerar vídeos" renderiza e põe na fila); cada um com formato de edição PRÓPRIO.
- Carrosséis: renderiza aqui (precisa das chaves de foto) direto em fila/, com capa do sistema de capas.
- V1, C1 e C2 já foram produzidos à mão (relancamento/); só são copiados para a fila.
- Peças do AutoFlow (C11, V11, C12, V12, C13, V13) ficam de fora até o material oficial chegar.
Uso (no GitHub Actions): python scripts/semana_relancamento.py [videos|carrosseis|tudo]
"""
import asyncio, json, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from marca import ARROBA

RAIZ = Path(__file__).resolve().parent.parent
FILA = RAIZ / "fila"
REL = RAIZ / "relancamento"
FIM = "\n\n"


def tags(*hs):
    return " ".join(list(hs) + ["#seraphimbr"])


# ======================= VÍDEOS (motor de cortes, um formato de edição por vídeo) =======================
VIDEOS = [
 dict(peca="V2", nome="tres-coisas-em-que-acreditamos", quando="2026-10-19 19:30", formato="hud", capa="3 coisas em que *acreditamos*", modelo_capa="blueprint",
      rotulo="PRINCÍPIOS", voz="masculina",
      cenas=[
       {"tipo": "palavra", "texto": "ANTES|DO|*CÓDIGO*", "destaque": "CÓDIGO", "narracao": "Antes de escrever uma linha de código, a gente acredita em três coisas."},
       {"tipo": "digitando", "topo": "CRENÇA 1:", "texto": "TECNOLOGIA SOME", "etiqueta": "CRENÇA 1", "narracao": "Primeira: tecnologia boa é a que some."},
       {"tipo": "foto", "busca": "team working together office laughing", "texto": "o time volta pro *cliente*", "tom": "dourado", "narracao": "O time para de pensar na ferramenta e volta a pensar no cliente."},
       {"tipo": "interruptor", "rotulo": "Automatizar a bagunça", "texto": "ligar agora?", "sub": "primeiro, organizar", "valor": 0.5, "etiqueta": "CRENÇA 2",
        "narracao": "Segunda: o processo vem antes do software. Automatizar uma bagunça só deixa a bagunça mais rápida."},
       {"tipo": "cards", "itens": [{"rotulo": "pequena:", "busca": "small shop owner counter"}, {"rotulo": "sistema de grande:", "busca": "modern office dashboard screen"}],
        "narracao": "Terceira: pequena empresa merece sistema de empresa grande, no tamanho dela."},
       {"tipo": "sera", "pose": "confiante", "texto": "é isso que guia cada projeto", "narracao": "É isso que guia cada projeto da Seraphim."},
       {"tipo": "cta", "texto": "QUAL DELAS É *A SUA?*", "pose": "pensando", "narracao": "Qual dessas três faz mais sentido pra sua empresa hoje? Comenta aqui."}],
      legenda="Antes do código, vem a forma de pensar. Qual dessas três faz mais sentido pra sua empresa hoje?",
      legenda_tiktok="As 3 coisas em que a gente acredita antes de programar qualquer coisa.", hashtags=["#tecnologia", "#pequenasempresas", "#gestao", "#automacao"]),
 dict(peca="V3", nome="custo-invisivel-trabalho-repetido", quando="2026-10-20 12:30", formato="documentario", capa="O custo *invisível*", modelo_capa="foto",
      capa_cena="office worker alone late at night tired in front of spreadsheet, warm desk lamp", rotulo="GESTÃO", voz="feminina",
      cenas=[
       {"tipo": "pergunta", "texto": "Quanto custa uma tarefa de *cinco minutos?*", "pose": "pensando", "narracao": "Quanto custa uma tarefa de cinco minutos?"},
       {"tipo": "foto", "busca": "person typing data into computer office", "texto": "parece *nada*", "tom": "cinza", "narracao": "Parece nada."},
       {"tipo": "calendario", "apoio": "1 DIA", "texto": "30 DIAS", "rotulo": "todo dia, a mesma pessoa", "narracao": "Mas ela se repete todo dia, às vezes várias vezes, e quase sempre cai na mesma pessoa."},
       {"tipo": "contador", "rotulo": "Minutos no mês (exemplo)", "de": 5, "para": 150, "sufixo": " min", "narracao": "Somando o mês, vira horas de trabalho que não aparecem em lugar nenhum."},
       {"tipo": "serifa", "itens": ["não vira venda", "não vira atendimento", "não vira descanso"], "narracao": "Não vira venda, não vira atendimento, não vira descanso."},
       {"tipo": "frase", "texto": "esse é o custo invisível", "destaque": "invisível", "narracao": "Esse é o custo invisível."},
       {"tipo": "foto", "busca": "business owner smiling talking with customer", "texto": "devolver o tempo pra *quem atende*", "tom": "dourado", "etiqueta": "O QUE FAZEMOS",
        "narracao": "A gente enxerga essas tarefas e tira das mãos de quem deveria estar fazendo outra coisa."},
       {"tipo": "cta", "texto": "QUAL TAREFA SE *REPETE AÍ?*", "pose": "confiante", "narracao": "Qual tarefa se repete todo santo dia na sua empresa? Conta nos comentários."}],
      legenda="Cinco minutos por dia parecem pouco. Faz a conta do mês. Qual tarefa aí na sua empresa se repete todo santo dia?",
      legenda_tiktok="O custo que ninguém vê na sua empresa.", hashtags=["#produtividade", "#gestaoempresarial", "#pequenasempresas", "#automacao"]),
 dict(peca="V4", nome="planilha-nao-e-sistema", quando="2026-10-20 19:30", formato="navegador", capa="Planilha não é *sistema*", modelo_capa="dividido",
      rotulo="ANTES E DEPOIS", voz="masculina",
      cenas=[
       {"tipo": "palavra", "texto": "SUA|PLANILHA|*FUNCIONA*", "destaque": "FUNCIONA", "narracao": "Sua planilha funciona."},
       {"tipo": "frase", "texto": "até o dia em que não funciona", "destaque": "não", "narracao": "Até o dia em que não funciona."},
       {"tipo": "checklist", "rotulo": "Já aconteceu aí?", "itens": ["duas pessoas editando", "fórmula sumiu", "qual versão vale?"],
        "narracao": "Duas pessoas editam ao mesmo tempo. Uma fórmula some. Ninguém sabe qual é a versão certa."},
       {"tipo": "foto", "busca": "stressed employee looking at laptop spreadsheet", "texto": "não foi feita pra ser o *coração*", "tom": "vermelho",
        "narracao": "Planilha é ótima pra começar, mas não foi feita pra ser o coração de uma empresa."},
       {"tipo": "diagrama", "passos": [{"icone": "relogio", "rotulo": "histórico"}, {"icone": "cadeado", "rotulo": "quem mexe"}, {"icone": "alerta", "rotulo": "avisos"}],
        "narracao": "Um sistema guarda o histórico, controla quem mexe em quê e avisa quando algo sai do lugar."},
       {"tipo": "serifa", "texto": "Não é abandonar a planilha. É saber a hora de crescer.", "narracao": "Não é sobre abandonar a planilha. É sobre saber a hora de crescer."},
       {"tipo": "cta", "texto": "SALVA PRA *LEMBRAR*", "pose": "feliz", "narracao": "Salva esse vídeo e manda pra quem vive dentro da planilha."}],
      legenda="Planilha é ótima pra começar. O problema é quando ela vira o lugar onde a empresa inteira mora. Já passou por algum desses?",
      legenda_tiktok="Sua planilha funciona. Até o dia em que não funciona.", hashtags=["#planilha", "#excel", "#gestao", "#sistemas"]),
 dict(peca="V5", nome="sistema-sob-medida-na-pratica", quando="2026-10-21 12:30", formato="celular", capa="Sob medida, *na prática*", modelo_capa="terminal",
      rotulo="O QUE FAZEMOS", voz="feminina",
      cenas=[
       {"tipo": "serifa", "texto": "Sistema sob medida não é luxo. É o contrário de improviso.", "narracao": "Sistema sob medida não é luxo. É o contrário de improviso."},
       {"tipo": "foto", "busca": "consultant listening to small business owner notebook", "texto": "primeiro, *estudar*", "tom": "dourado", "etiqueta": "PASSO 1",
        "narracao": "Funciona assim: a gente estuda como a sua empresa trabalha hoje,"},
       {"tipo": "diagrama", "passos": [{"icone": "chat", "rotulo": "WhatsApp"}, {"icone": "tela", "rotulo": "sistema"}, {"icone": "check", "rotulo": "nota"}],
        "narracao": "desenha o caminho ideal e constrói só o que você precisa. Se o seu atendimento começa no WhatsApp e termina numa nota, o sistema segue esse caminho."},
       {"tipo": "frase", "texto": "nem uma tela a mais", "destaque": "a mais", "narracao": "Nem uma tela a mais."},
       {"tipo": "foto", "busca": "employees using tablet in small business smiling", "texto": "o time entende no *primeiro dia*", "tom": "normal",
        "narracao": "O resultado é uma ferramenta que o time entende no primeiro dia."},
       {"tipo": "cta", "texto": "QUAL ETAPA *PRECISA?*", "pose": "pensando", "narracao": "Qual etapa do seu dia mais precisa de um sistema? Comenta aqui."}],
      legenda="Sob medida é construir só o que a sua operação usa. Conta pra gente: qual etapa do seu dia mais precisa de um sistema?",
      legenda_tiktok="O que é sistema sob medida, sem enrolação.", hashtags=["#desenvolvimento", "#sistemas", "#software", "#pequenasempresas"]),
 dict(peca="V6", nome="pronto-ou-sob-medida", quando="2026-10-21 19:30", formato="story", capa="Pronto ou *sob medida?*", modelo_capa="interrogacao",
      rotulo="", voz="masculina",
      cenas=[
       {"tipo": "sera", "pose": "surpreso", "texto": "nem toda empresa precisa", "narracao": "Nem toda empresa precisa de um sistema sob medida. E a gente fala isso de propósito."},
       {"tipo": "niveis", "texto": "Use o PRONTO quando", "itens": ["processo é comum", "precisa ser rápido", "orçamento curto"],
        "narracao": "Se o seu processo é comum e um software pronto resolve, use o pronto: é mais rápido e mais barato."},
       {"tipo": "checklist", "rotulo": "Sob medida faz sentido se", "itens": ["seu jeito é diferencial", "3 ferramentas não conversam", "o pronto te trava"],
        "narracao": "Sob medida faz sentido quando o seu jeito de trabalhar é o seu diferencial, quando você já usa três ferramentas que não conversam, ou quando o pronto te obriga a mudar o que funciona."},
       {"tipo": "foto", "busca": "two people discussing decision at table", "texto": "qual serve pra *você?*", "tom": "dourado",
        "narracao": "A pergunta certa não é qual é melhor. É qual serve pra você."},
       {"tipo": "cta", "texto": "DE QUAL LADO *VOCÊ ESTÁ?*", "pose": "confiante", "narracao": "Em qual dos dois lados a sua empresa está hoje? Responde aqui."}],
      legenda="Às vezes a melhor recomendação é não construir nada. Em qual dos dois lados a sua empresa está hoje?",
      legenda_tiktok="Pronto ou sob medida? A resposta honesta.", hashtags=["#software", "#tecnologia", "#empreendedorismo", "#gestao"]),
 dict(peca="V7", nome="uma-tarefa-tres-sistemas", quando="2026-10-22 12:30", formato="terminal", capa="Zero *copia e cola*", modelo_capa="notificacoes",
      rotulo="INTEGRAÇÃO", voz="feminina",
      cenas=[
       {"tipo": "pergunta", "texto": "Quantas vezes alguém digita a *mesma informação?*", "pose": "preocupado", "narracao": "Um pedido chega. Quantas vezes alguém digita a mesma informação?"},
       {"tipo": "digitando", "topo": "DIGITADO:", "texto": "3 VEZES", "narracao": "Uma no atendimento, outra no financeiro, outra na planilha de entrega."},
       {"tipo": "frase", "texto": "três chances de errar", "destaque": "errar", "narracao": "Três chances de errar."},
       {"tipo": "diagrama", "passos": [{"icone": "chat", "rotulo": "atendimento"}, {"icone": "dinheiro", "rotulo": "financeiro"}, {"icone": "carrinho", "rotulo": "entrega"}],
        "etiqueta": "INTEGRAÇÃO", "narracao": "Integração é fazer esses sistemas conversarem: o dado entra uma vez e aparece onde precisa."},
       {"tipo": "foto", "busca": "customer service employee smiling headset", "texto": "quem atendia volta a *atender*", "tom": "normal",
        "narracao": "Quem atendia volta a atender. Quem conferia volta a decidir."},
       {"tipo": "interruptor", "rotulo": "Erro de digitação", "texto": "sempre ligado", "sub": "deixou de existir", "valor": 0.4,
        "narracao": "E o erro de digitação simplesmente deixa de existir."},
       {"tipo": "cta", "texto": "SALVA E *MANDA PRO TIME*", "pose": "comemorando", "narracao": "Salva e manda pra quem digita a mesma coisa três vezes."}],
      legenda="O dado entra uma vez e aparece onde precisa. Quantas vezes a mesma informação é digitada aí?",
      legenda_tiktok="Uma tarefa, três sistemas, zero copia e cola.", hashtags=["#integracao", "#automacao", "#produtividade", "#tecnologia"]),
 dict(peca="V8", nome="segunda-no-automatico", quando="2026-10-22 19:30", formato="eletrico", capa="Segunda no *automático*", modelo_capa="tipografia",
      rotulo="", voz="masculina",
      cenas=[
       {"tipo": "palavra", "texto": "SEGUNDA|8 DA|*MANHÃ*", "destaque": "MANHÃ", "narracao": "Segunda-feira, oito da manhã. Olha quanta coisa poderia acontecer sozinha."},
       {"tipo": "foto", "busca": "laptop email inbox morning coffee", "texto": "08:00 · relatório *pronto*", "tom": "dourado", "narracao": "Oito horas: o relatório da semana já está na sua caixa."},
       {"tipo": "digitando", "topo": "10:00", "texto": "PEDIDO CONFIRMADO", "narracao": "Dez: o cliente recebe a confirmação do pedido sem ninguém digitar."},
       {"tipo": "painel", "rotulo": "Pagamentos em dia", "valor": 80, "texto": "12:00 · lembrete educado", "narracao": "Meio-dia: quem está com pagamento atrasado ganha um lembrete educado."},
       {"tipo": "calendario", "apoio": "HOJE", "texto": "AMANHÃ", "rotulo": "16:00 · agenda organizada", "narracao": "Quatro da tarde: a agenda de amanhã se organiza."},
       {"tipo": "serifa", "texto": "Nada disso exige tecnologia nova.", "narracao": "Nada disso exige tecnologia nova. Exige olhar pro seu dia e decidir o que não precisa mais de uma pessoa."},
       {"tipo": "cta", "texto": "QUAL VOCÊ *TIRARIA PRIMEIRO?*", "pose": "feliz", "narracao": "Qual delas você tiraria das mãos do seu time primeiro? Comenta."}],
      legenda="Nenhuma dessas exige tecnologia nova. Qual delas você tiraria das mãos do seu time primeiro?",
      legenda_tiktok="O que dá pra automatizar numa segunda-feira.", hashtags=["#automacao", "#produtividade", "#rotina", "#pequenasempresas"]),
 dict(peca="V9", nome="como-comecamos-um-projeto", quando="2026-10-23 12:30", formato="vhs", capa="Primeiro, a *caneta*", modelo_capa="postit",
      rotulo="MÉTODO", voz="feminina",
      cenas=[
       {"tipo": "frase", "texto": "o primeiro dia não tem código", "destaque": "código", "narracao": "O primeiro dia de um projeto nosso não tem código. Tem caneta."},
       {"tipo": "foto", "busca": "people meeting whiteboard sticky notes", "texto": "com quem *faz o trabalho*", "tom": "dourado", "etiqueta": "PASSO 1",
        "narracao": "A gente senta com quem faz o trabalho, não só com quem manda nele."},
       {"tipo": "parede", "buscas": ["whiteboard process diagram", "handwritten notes workflow", "team planning post it"], "texto": "o processo real",
        "narracao": "Desenha o processo como ele é de verdade, com os jeitinhos e as gambiarras."},
       {"tipo": "checklist", "rotulo": "Onde dói", "itens": ["o que atrasa", "o que erra", "o que se repete"], "narracao": "Depois marca onde dói: o que atrasa, o que erra, o que se repete."},
       {"tipo": "niveis", "texto": "Só aí", "itens": ["pequeno", "testado", "usado"], "narracao": "Só aí escolhe o que construir primeiro. Pequeno, testado, usado."},
       {"tipo": "cta", "texto": "PROJETO BOM *COMEÇA OUVINDO*", "pose": "confiante", "narracao": "Projeto bom começa ouvindo. Segue a Seraphim pra ver como a gente trabalha."}],
      legenda="Antes da tecnologia, a conversa. Quem na sua empresa conhece o processo de verdade?",
      legenda_tiktok="Como a gente começa um projeto: com caneta.", hashtags=["#metodo", "#desenvolvimento", "#processos", "#gestao"]),
 dict(peca="V10", nome="perguntas-antes-do-codigo", quando="2026-10-23 19:30", formato="noir", capa="5 perguntas antes do *código*", modelo_capa="ensaio",
      rotulo="ENSAIO", voz="masculina",
      cenas=[
       {"tipo": "palavra", "texto": "5|PERGUNTAS|*ANTES*", "destaque": "ANTES", "narracao": "Cinco perguntas que a gente faz antes de construir qualquer coisa."},
       {"tipo": "serifa", "texto": "Quem vai usar isso todo dia?", "narracao": "Quem vai usar isso todo dia?"},
       {"tipo": "foto", "busca": "worried employee phone call problem", "texto": "o que acontece quando *dá errado?*", "tom": "cinza", "narracao": "O que acontece hoje quando dá errado?"},
       {"tipo": "frase", "texto": "qual tarefa ninguém sentiria falta?", "destaque": "ninguém", "narracao": "Qual tarefa, se sumisse amanhã, ninguém sentiria falta?"},
       {"tipo": "digitando", "topo": "PERGUNTA 4:", "texto": "ONDE NASCE?", "narracao": "Onde a informação nasce?"},
       {"tipo": "pergunta", "texto": "Como saber que *deu certo?*", "pose": "pensando", "narracao": "E como a gente vai saber que deu certo?"},
       {"tipo": "cta", "texto": "SALVA *ESSAS 5*", "pose": "confiante", "narracao": "Se uma delas fica sem resposta, ainda não é hora de programar. Salva essas cinco."}],
      legenda="Se uma delas fica sem resposta, ainda não é hora de programar. Qual você acha mais difícil de responder?",
      legenda_tiktok="5 perguntas antes da primeira linha de código.", hashtags=["#programacao", "#desenvolvimento", "#tecnologia", "#metodo"]),
 dict(peca="V14", nome="sete-dias-uma-ideia", quando="2026-10-25 19:30", formato="noticia", capa="Tecnologia com *método*", modelo_capa="manifesto",
      rotulo="SEMANA 1", voz="feminina",
      cenas=[
       {"tipo": "sera", "pose": "comemorando", "texto": "sete dias depois", "narracao": "Em sete dias, a gente te contou quem é. Agora é a sua vez."},
       {"tipo": "serifa", "texto": "Tirar das pessoas o trabalho que não deveria ser delas.", "narracao": "A Seraphim existe pra tirar das pessoas o trabalho que não deveria ser delas."},
       {"tipo": "diagrama", "passos": [{"icone": "tela", "rotulo": "sistemas"}, {"icone": "engrenagem", "rotulo": "automação"}, {"icone": "raio", "rotulo": "integração"}],
        "narracao": "Com sistemas sob medida, automação e integração."},
       {"tipo": "frase", "texto": "com método, sem promessa vazia", "destaque": "método", "narracao": "Com método, sem promessa vazia. E com um primeiro produto, o AutoFlow."},
       {"tipo": "foto", "busca": "small business team smiling office", "texto": "um trabalho que *ninguém deveria fazer?*", "tom": "dourado",
        "narracao": "Se a sua empresa tem um trabalho que ninguém deveria estar fazendo, manda uma mensagem."},
       {"tipo": "cta", "texto": "A CONVERSA *COMEÇA COM CANETA*", "pose": "feliz", "narracao": "A conversa começa com caneta. Manda um direct pra gente."}],
      legenda="Uma semana, uma ideia. Se a sua empresa tem um trabalho que ninguém deveria estar fazendo, manda um direct. A gente responde.",
      legenda_tiktok="Sete dias, uma ideia: tecnologia com método.", hashtags=["#seraphim", "#tecnologia", "#automacao", "#empresas"]),
]


def pedidos_videos():
    (RAIZ / "pedidos").mkdir(exist_ok=True)
    import capa
    for k, v in enumerate(VIDEOS):
        destino = FILA / f"{v['quando'].replace(' ', '_').replace(':', '')}_{v['nome']}"
        destino.mkdir(parents=True, exist_ok=True)
        spec = {"nome": v["nome"], "arroba": ARROBA, "quando": v["quando"], "cenas": v["cenas"], "motor": "cortes",
                "formato": v["formato"], "titulo": v["capa"].replace("*", ""), "numero": k + 2, "funil": "topo",
                "genero_voz": v["voz"], "voz": "gemini", "relancamento": v["peca"],
                "legenda": v["legenda"] + FIM + tags(*v["hashtags"]), "legenda_tiktok": v["legenda_tiktok"] + FIM + tags(*v["hashtags"][:3])}
        (RAIZ / "pedidos" / f"{v['nome']}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
        img = ""
        if v.get("capa_cena"):
            import ingredientes
            img = str(ingredientes.ilustracao(v["capa_cena"], v["capa_cena"], destino / "capa_img.jpg", "9:16") or "")
        modelo = v["modelo_capa"] if (img or v["modelo_capa"] not in capa.COM_IMAGEM) else "manifesto"
        asyncio.run(capa.gerar_varias([{"titulo": v["capa"], "rotulo": v["rotulo"], "modelo": modelo, "imagem": img, "saida": destino / "capa.jpg"}]))
        Path(destino / "capa_img.jpg").unlink(missing_ok=True)
        print("pedido:", v["peca"], v["nome"], v["formato"], "capa:", modelo)


def v1_na_fila():
    destino = FILA / "2026-10-19_1230_v1-prazer-seraphim"
    destino.mkdir(parents=True, exist_ok=True)
    shutil.copy(REL / "V1" / "video.mp4", destino / "video.mp4")
    shutil.copy(REL / "V1" / "capa.jpg", destino / "capa.jpg")
    hs = tags("#tecnologia", "#automacao", "#sistemas", "#empresas")
    (destino / "item.json").write_text(json.dumps({
        "tipo": "reels", "quando": "2026-10-19T12:30:00-03:00", "funil": "topo",
        "legenda": "A partir de hoje, a Seraphim começa do zero por aqui. Uma empresa de tecnologia que desenvolve sistemas, automatiza processos e conecta ferramentas. Nesta semana, a gente mostra como pensa. Segue pra acompanhar." + FIM + hs,
        "legenda_tiktok": "Prazer, Seraphim. Tecnologia com método." + FIM + tags("#tecnologia", "#automacao")}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("fila: V1")


# ======================= CARROSSÉIS =======================
CARROSSEIS = [
 dict(peca="C3", nome="5-sinais-passou-das-ferramentas", quando="2026-10-20 09:00", capa="5 sinais de que você *passou das ferramentas*", modelo_capa="lista", rotulo="CHECKLIST",
      slides=[
       {"tipo": "capa_foto", "rotulo": "GESTÃO", "titulo": "5 sinais de que sua empresa|*passou das ferramentas*", "busca": "busy small business owner many papers desk"},
       {"tipo": "numero", "numero": "01", "titulo": "A informação mora|em *vários lugares*", "texto": "“Tá na planilha ou no WhatsApp?”"},
       {"tipo": "numero", "numero": "02", "titulo": "Só *uma pessoa*|sabe como funciona", "texto": "“Pergunta pra ela.”", "fundo": "branco"},
       {"tipo": "whatsapp", "rotulo": "SINAL 03", "titulo": "O mesmo dado é|*digitado duas vezes*", "contato": "Financeiro",
        "mensagens": [{"de": "cliente", "texto": "lançou o pedido do João?", "hora": "09:12"}, {"de": "empresa", "texto": "já lancei, mas lança de novo aí na planilha", "hora": "09:14"}]},
       {"tipo": "numero", "numero": "04", "titulo": "Relatório leva|*dias*", "texto": "“Segunda eu te passo.”"},
       {"tipo": "numero", "numero": "05", "titulo": "O erro só aparece quando|o *cliente reclama*", "texto": "E aí já custou caro.", "fundo": "branco"},
       {"tipo": "capa", "titulo": "Marcou 3 ou mais?|*Hora de um sistema*", "texto": "Manda um direct pra **" + ARROBA + "**.", "sera": "pensando"},
       {"tipo": "perfil_cta", "titulo": "Salva e manda pra|quem cuida da *operação*", "texto": "Siga a " + ARROBA + " para mais."}],
      legenda="Quantos você marcou? Salva e manda pra quem cuida da operação aí.", hashtags=["#gestao", "#pequenasempresas", "#processos", "#produtividade"]),
 dict(peca="C4", nome="por-que-a-seraphim-existe", quando="2026-10-20 17:30", capa="Por que a Seraphim *existe*", modelo_capa="recorte", rotulo="CARTA",
      capa_cena="handwritten letter on a wooden desk next to a laptop, warm morning light",
      slides=[
       {"tipo": "capa_foto", "rotulo": "CARTA ABERTA", "titulo": "Por que a Seraphim|*existe*", "busca": "handwritten letter desk laptop"},
       {"tipo": "citacao", "titulo": "A gente cansou de ver|*gente boa presa*", "texto": "em trabalho repetitivo."},
       {"tipo": "capa_foto", "titulo": "Gente que abriu um negócio pra atender bem,|e passa o dia *conferindo planilha*", "busca": "tired shop owner checking papers"},
       {"tipo": "texto", "titulo": "A tecnologia que resolve|*isso existe*", "texto": "Só que quase sempre é feita para **empresa grande**.", "fundo": "branco"},
       {"tipo": "citacao", "titulo": "A Seraphim existe pra levar essa tecnologia pro|*tamanho certo*", "texto": "da sua empresa."},
       {"tipo": "capa", "titulo": "Sem complicar.|Sem prometer milagre.|*Com método.*", "texto": "— Equipe Seraphim", "sera": "confiante"},
       {"tipo": "perfil_cta", "titulo": "Esse é o|*nosso motivo*", "texto": "Siga a " + ARROBA + " para acompanhar."}],
      legenda="Toda empresa tem um motivo pra existir. Esse é o nosso.", hashtags=["#proposito", "#tecnologia", "#empreendedorismo", "#startup"]),
 dict(peca="C5", nome="as-tres-frentes-da-seraphim", quando="2026-10-21 09:00", capa="As 3 frentes da *Seraphim*", modelo_capa="vidro", rotulo="SERVIÇOS",
      capa_cena="abstract golden light trails connecting three glowing nodes in dark space",
      slides=[
       {"tipo": "capa_foto", "rotulo": "O QUE FAZEMOS", "titulo": "As 3 frentes|da *Seraphim*", "busca": "team developers working laptops modern office"},
       {"tipo": "card", "rotulo": "FRENTE 01", "titulo": "Sistemas|*sob medida*", "icone": "🧩", "subtitulo": "Ferramentas feitas para o jeito que a sua empresa trabalha.",
        "card": "Ex.: pedidos, agenda e clientes num lugar só.", "chips": ["cadastro", "painel", "relatórios"]},
       {"tipo": "card", "rotulo": "FRENTE 02", "titulo": "*Automação*", "icone": "⚙️", "subtitulo": "Tarefas repetidas acontecendo sozinhas.",
        "card": "Ex.: lembretes, confirmações e relatórios automáticos.", "chips": ["lembretes", "confirmações"], "fundo": "branco"},
       {"tipo": "card", "rotulo": "FRENTE 03", "titulo": "*Integração*", "icone": "🔗", "subtitulo": "As ferramentas que você já usa conversando entre si.",
        "card": "Ex.: o pedido vai do atendimento ao financeiro sozinho.", "chips": ["dados", "sistemas", "planilhas"]},
       {"tipo": "capa", "titulo": "Qual dessas a sua empresa|*precisa primeiro?*", "texto": "Manda no direct.", "sera": "feliz"},
       {"tipo": "perfil_cta", "titulo": "Tirar trabalho repetido|*das pessoas*", "texto": "Siga a " + ARROBA + "."}],
      legenda="Três frentes, um objetivo: tirar trabalho repetido das pessoas. Qual delas faz falta aí?", hashtags=["#sistemas", "#automacao", "#integracao", "#tecnologia"]),
 dict(peca="C6", nome="voce-precisa-de-sistema-proprio", quando="2026-10-21 17:30", capa="Você precisa de um *sistema próprio?*", modelo_capa="icone", rotulo="DECISÃO",
      slides=[
       {"tipo": "capa", "tag": "Teste rápido", "titulo": "Você precisa de um|*sistema próprio?*", "texto": "Responde as 4 perguntas.", "sera": "pensando"},
       {"tipo": "comparacao", "rotulo": "PERGUNTA 1", "titulo": "Seu processo é|*comum no setor?*", "esquerda": {"rotulo": "Sim", "itens": ["software pronto", "mais rápido", "mais barato"]},
        "direita": {"rotulo": "Não", "itens": ["continua", "próxima pergunta", "→"]}},
       {"tipo": "pilulas", "rotulo": "PERGUNTA 2", "titulo": "Usa 3+ ferramentas que|*não conversam?*", "texto": "Se sim, integração resolve muito.", "itens": ["WhatsApp", "planilha", "sistema fiscal", "agenda"]},
       {"tipo": "texto", "titulo": "O pronto te obriga a|*mudar o que funciona?*", "texto": "Se sim, **sob medida faz sentido**.", "fundo": "branco"},
       {"tipo": "texto", "titulo": "Seu jeito de trabalhar é|o seu *diferencial?*", "texto": "Proteja ele com **um sistema próprio**."},
       {"tipo": "citacao", "titulo": "A resposta honesta pode ser|*“ainda não”*", "texto": "E tudo bem."},
       {"tipo": "perfil_cta", "titulo": "Na dúvida, a gente|*ajuda a decidir*", "texto": "Sem compromisso. Siga a " + ARROBA + "."}],
      legenda="Antes de investir em sistema, responde essas 4 perguntas. Salva pra usar quando chegar a hora.", hashtags=["#software", "#gestao", "#empreendedorismo", "#decisao"]),
 dict(peca="C7", nome="integracao-explicada-cozinha", quando="2026-10-22 09:00", capa="Integração explicada com uma *cozinha*", modelo_capa="polaroid", rotulo="explicado",
      capa_cena="busy restaurant kitchen with chefs cooking, warm golden light, cinematic",
      slides=[
       {"tipo": "capa_foto", "rotulo": "EXPLICADO", "titulo": "Integração explicada|com uma *cozinha*", "busca": "restaurant kitchen chef cooking"},
       {"tipo": "capa_foto", "titulo": "O garçom anota o pedido,|e o cozinheiro precisa *ir até a mesa ler*", "busca": "waiter taking order restaurant notepad"},
       {"tipo": "capa_foto", "titulo": "E o caixa pergunta de novo|*o que a mesa comeu*", "busca": "restaurant cashier counter"},
       {"tipo": "texto", "titulo": "Funciona. Mas todo mundo|*trabalha dobrado*", "texto": "E o erro aparece **no prato**.", "fundo": "branco"},
       {"tipo": "citacao", "titulo": "Integração é a comanda que vai|*sozinha pra cozinha e pro caixa*", "texto": ""},
       {"tipo": "texto", "titulo": "Na sua empresa, a comanda é|o *pedido, o cadastro, a nota*", "texto": "A ideia é a mesma."},
       {"tipo": "perfil_cta", "titulo": "Onde a sua comanda|*se perde hoje?*", "texto": "Conta pra gente. Siga a " + ARROBA + "."}],
      legenda="O jeito mais simples de entender integração. Manda pra quem ainda acha que é coisa de TI.", hashtags=["#integracao", "#tecnologia", "#explicado", "#processos"]),
 dict(peca="C8", nome="glossario-api-webhook", quando="2026-10-22 17:30", capa="O glossário que ninguém te *explicou*", modelo_capa="jornal", rotulo="GLOSSÁRIO",
      slides=[
       {"tipo": "capa", "tag": "Glossário", "titulo": "O glossário que ninguém|te *explicou*", "texto": "5 palavras de tecnologia, sem jargão.", "sera": "surpreso"},
       {"tipo": "card", "rotulo": "VERBETE", "titulo": "*API*", "icone": "🚪", "subtitulo": "A porta pela qual um sistema conversa com outro.", "card": "Na prática: o site consultando o estoque.", "chips": ["substantivo feminino"]},
       {"tipo": "card", "rotulo": "VERBETE", "titulo": "*Webhook*", "icone": "🔔", "subtitulo": "Um aviso automático quando algo acontece.", "card": "Na prática: pagamento aprovado avisa o sistema na hora.", "chips": ["substantivo masculino"], "fundo": "branco"},
       {"tipo": "card", "rotulo": "VERBETE", "titulo": "*Integração*", "icone": "🔗", "subtitulo": "Sistemas trocando dados sozinhos.", "card": "Na prática: o pedido vai do atendimento ao financeiro.", "chips": ["substantivo feminino"]},
       {"tipo": "card", "rotulo": "VERBETE", "titulo": "*Automação*", "icone": "⚙️", "subtitulo": "Uma tarefa que acontece sem ação humana.", "card": "Na prática: o lembrete de vencimento.", "chips": ["substantivo feminino"], "fundo": "branco"},
       {"tipo": "card", "rotulo": "VERBETE", "titulo": "*Banco de dados*", "icone": "🗄️", "subtitulo": "Onde a informação fica guardada e organizada.", "card": "Na prática: o cadastro de clientes.", "chips": ["substantivo masculino"]},
       {"tipo": "perfil_cta", "titulo": "Faltou alguma|*palavra?*", "texto": "Pede nos comentários. Siga a " + ARROBA + "."}],
      legenda="Cinco palavras que você vai ouvir em qualquer conversa sobre tecnologia. Salva pra consultar.", hashtags=["#glossario", "#tecnologia", "#api", "#aprenda"]),
 dict(peca="C9", nome="nosso-processo-5-etapas", quando="2026-10-23 09:00", capa="Nosso processo em *5 etapas*", modelo_capa="alvo", rotulo="MÉTODO",
      slides=[
       {"tipo": "capa_foto", "rotulo": "MÉTODO", "titulo": "Nosso processo|em *5 etapas*", "busca": "team planning project whiteboard"},
       {"tipo": "passos", "rotulo": "ETAPAS 1 A 3", "titulo": "Do problema|ao *plano*", "itens": [{"titulo": "Escutar", "texto": "Conversamos com quem faz o trabalho."},
        {"titulo": "Mapear", "texto": "Desenhamos o processo real e marcamos onde dói."}, {"titulo": "Priorizar", "texto": "Escolhemos o que resolve mais com menos."}]},
       {"tipo": "passos", "rotulo": "ETAPAS 4 E 5", "titulo": "Do plano|ao *uso*", "itens": [{"titulo": "Construir pequeno", "texto": "Entregamos uma parte que já funciona."},
        {"titulo": "Melhorar com uso", "texto": "Ajustamos com quem usa todo dia."}], "fundo": "branco"},
       {"tipo": "capa_foto", "titulo": "Sem caixa-preta:|você *acompanha tudo*", "busca": "client and developer looking at screen together"},
       {"tipo": "citacao", "titulo": "Projeto bom não termina na entrega.|*Começa nela.*", "texto": ""},
       {"tipo": "perfil_cta", "titulo": "Salva pra|*lembrar*", "texto": "Siga a " + ARROBA + "."}],
      legenda="Sem caixa-preta: é assim que um projeto anda com a gente.", hashtags=["#metodo", "#projetos", "#desenvolvimento", "#processos"]),
 dict(peca="C10", nome="o-que-nao-fazemos", quando="2026-10-23 17:30", capa="O que a Seraphim *não faz*", modelo_capa="alerta", rotulo="HONESTIDADE",
      slides=[
       {"tipo": "capa", "tag": "Sem enrolação", "titulo": "O que a Seraphim|*não faz*", "texto": "", "sera": "confiante"},
       {"tipo": "numero", "numero": "✕", "titulo": "Prometer resultado antes|de *entender o problema*", "texto": ""},
       {"tipo": "numero", "numero": "✕", "titulo": "Vender sistema quando|uma *planilha bem feita* resolve", "texto": "", "fundo": "branco"},
       {"tipo": "numero", "numero": "✕", "titulo": "Usar IA só porque|está *na moda*", "texto": ""},
       {"tipo": "numero", "numero": "✕", "titulo": "Entregar|e *sumir*", "texto": "", "fundo": "branco"},
       {"tipo": "numero", "numero": "✕", "titulo": "Esconder o que está|sendo *construído*", "texto": ""},
       {"tipo": "perfil_cta", "titulo": "O que a gente faz:|tecnologia com *método*", "texto": "Siga a " + ARROBA + "."}],
      legenda="Às vezes o que uma empresa não faz diz mais do que o que ela faz.", hashtags=["#transparencia", "#tecnologia", "#empresas", "#confianca"]),
 dict(peca="C14", nome="o-que-podemos-construir", quando="2026-10-25 17:30", capa="O que podemos *construir pra você*", modelo_capa="dado", rotulo="IDEIAS",
      slides=[
       {"tipo": "capa_foto", "rotulo": "IDEIAS", "titulo": "O que podemos|*construir pra você*", "busca": "small business owner smiling using laptop"},
       {"tipo": "card", "rotulo": "IDEIA 1", "titulo": "Painel do *dia*", "icone": "📊", "subtitulo": "Os números do dia, sem montar planilha.", "card": "", "chips": ["vendas", "pedidos"]},
       {"tipo": "card", "rotulo": "IDEIA 2", "titulo": "Cadastro *único*", "icone": "👥", "subtitulo": "Um cadastro de clientes que o time inteiro usa igual.", "card": "", "chips": ["clientes"], "fundo": "branco"},
       {"tipo": "card", "rotulo": "IDEIA 3", "titulo": "Avisos *automáticos*", "icone": "🔔", "subtitulo": "Lembretes e confirmações que saem sozinhos.", "card": "", "chips": ["WhatsApp", "e-mail"]},
       {"tipo": "card", "rotulo": "IDEIA 4", "titulo": "Ferramentas *conversando*", "icone": "🔗", "subtitulo": "Suas ferramentas atuais trocando dados entre si.", "card": "", "chips": ["integração"], "fundo": "branco"},
       {"tipo": "card", "rotulo": "IDEIA 5", "titulo": "Sistema *inteiro*", "icone": "🧩", "subtitulo": "Do tamanho da sua operação.", "card": "", "chips": ["sob medida"]},
       {"tipo": "capa", "titulo": "Tem um trabalho que|*ninguém deveria fazer?*", "texto": "Manda no direct.", "sera": "feliz"}],
      legenda="Ideias do que dá pra construir. A sua empresa tem a própria lista — conta pra gente.", hashtags=["#sistemas", "#automacao", "#pequenasempresas", "#tecnologia"]),
]


def carrosseis():
    import capa, carrossel, ingredientes
    from PIL import Image
    hist = json.loads((RAIZ / "historico.json").read_text(encoding="utf-8"))
    for c in CARROSSEIS:
        destino = FILA / f"{c['quando'].replace(' ', '_').replace(':', '')}_{c['nome']}"
        destino.mkdir(parents=True, exist_ok=True)
        tmp = RAIZ / f"_car_{c['nome']}.json"
        tmp.write_text(json.dumps({"nome": c["nome"], "arroba": ARROBA, "slides": c["slides"], "tema": "noir"}, ensure_ascii=False), encoding="utf-8")
        asyncio.run(carrossel.main(str(tmp), str(destino)))
        tmp.unlink()
        for png in sorted(destino.glob("slide-*.png")):
            Image.open(png).convert("RGB").save(png.with_suffix(".jpg"), quality=93); png.unlink()
        img = ""
        if c.get("capa_cena"):
            img = str(ingredientes.ilustracao(c["capa_cena"], c["capa_cena"], destino / "_capa_img.jpg", "4:5") or "")
        modelo = c["modelo_capa"] if (img or c["modelo_capa"] not in capa.COM_IMAGEM) else "ensaio"
        asyncio.run(capa.gerar_varias([{"titulo": c["capa"], "rotulo": c["rotulo"], "modelo": modelo, "modo": "carrossel", "imagem": img,
                                        "saida": destino / "slide-01.jpg"}]))
        Path(destino / "_capa_img.jpg").unlink(missing_ok=True)
        (destino / "item.json").write_text(json.dumps({
            "tipo": "carrossel", "quando": c["quando"].replace(" ", "T") + ":00-03:00",
            "legenda": c["legenda"] + FIM + tags(*c["hashtags"])}, ensure_ascii=False, indent=2), encoding="utf-8")
        hist.append({"nome": c["nome"], "titulo": c["capa"].replace("*", ""), "dia": c["quando"][:10], "tipo": "carrossel", "capa_modelo": modelo, "relancamento": c["peca"]})
        print("fila:", c["peca"], c["nome"], "capa:", modelo)
    for v in VIDEOS:
        hist.append({"nome": v["nome"], "titulo": v["capa"].replace("*", ""), "dia": v["quando"][:10], "tipo": "video", "formato_edicao": v["formato"],
                     "capa_modelo": v["modelo_capa"], "relancamento": v["peca"]})
    (RAIZ / "historico.json").write_text(json.dumps(hist, ensure_ascii=False, indent=1), encoding="utf-8")


def c1_c2_na_fila():
    for peca, nome, quando, leg, hs in [
        ("C1", "o-que-e-a-seraphim", "2026-10-19 09:00", "Prazer. Em 7 páginas, quem somos e o que fazemos. Salva pra lembrar de nós quando a sua empresa precisar.",
         ("#tecnologia", "#sistemas", "#automacao", "#empresas")),
        ("C2", "nosso-manifesto", "2026-10-19 17:30", "Seis frases que guiam tudo o que a gente constrói. Qual delas você assinaria embaixo?",
         ("#manifesto", "#tecnologia", "#proposito", "#empreendedorismo"))]:
        destino = FILA / f"{quando.replace(' ', '_').replace(':', '')}_{nome}"
        destino.mkdir(parents=True, exist_ok=True)
        for f in sorted((REL / peca / "instagram").glob("slide-*.jpg")):
            shutil.copy(f, destino / f.name)
        tt = destino / "tiktok"; tt.mkdir(exist_ok=True)
        for f in sorted((REL / peca / "tiktok").glob("slide-*.jpg")):
            shutil.copy(f, tt / f.name)
        (destino / "item.json").write_text(json.dumps({"tipo": "carrossel", "quando": quando.replace(" ", "T") + ":00-03:00",
                                                       "legenda": leg + FIM + tags(*hs)}, ensure_ascii=False, indent=2), encoding="utf-8")
        print("fila:", peca)


if __name__ == "__main__":
    o = sys.argv[1] if len(sys.argv) > 1 else "tudo"
    if o in ("tudo", "manuais"):
        v1_na_fila(); c1_c2_na_fila()
    if o in ("tudo", "carrosseis"):
        carrosseis()
    if o in ("tudo", "videos"):
        pedidos_videos()
