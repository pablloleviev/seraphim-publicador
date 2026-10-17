"""Carrosséis da semana 19–25/10 no estilo aprovado (estilo_ref), cada um com estrutura própria.
Uso: python scripts/carrosseis_semana.py [parte-do-nome ...]  -> grava em fila/<pasta>/ (slides antigos vão para arquivo/)"""
import asyncio, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import estilo_ref as E

R = E.RAIZ
EU = (R / "assets/pessoas/pabllo_recorte.png").as_uri()
SERA = (R / "motor/public/sera/confiante.png").as_uri()
SERA_P = (R / "motor/public/sera/pensando.png").as_uri()

C = {
"2026-10-19_0900_o-que-e-a-seraphim": [
 {"tipo": "capa", "foto": EU, "linha": "EDIÇÃO DE ESTREIA", "titulo": "O que é a<br>*Seraphim*", "blocos": [("layers", 40, 300, -14, 230), ("zap", 800, 220, 12, 210), ("link", 820, 640, -8, 170)]},
 {"tipo": "citacao", "titulo": "Uma empresa de tecnologia que desenvolve sistemas, automatiza processos e *conecta ferramentas.*", "texto": "Em uma frase."},
 {"tipo": "abertura", "titulo": "Para *pequenas e médias* empresas", "textos": ["Empresas que **cresceram mais rápido** que as próprias ferramentas.", "Que vivem entre **WhatsApp, planilha e papel** — e sentem o peso disso."], "icones": ["store", "users", "trending-up", "message-circle"]},
 {"tipo": "lista", "rotulo": "O QUE FAZEMOS", "titulo": "Três *frentes*", "itens": [("Sistemas sob medida", "feitos para o jeito que a sua empresa trabalha"), ("Automação", "tarefas repetidas acontecendo sozinhas"), ("Integração", "suas ferramentas conversando entre si")]},
 {"tipo": "lista", "rotulo": "COMO FAZEMOS", "fundo": "claro", "titulo": "Com *método*", "marcador": "→", "itens": ["Ouvimos antes", "Construímos pequeno", "Melhoramos com o uso"]},
 {"tipo": "cta", "foto": EU, "titulo": "Nesta semana, a gente mostra *tudo.*", "texto": "Acompanha a semana de estreia."},
],
"2026-10-19_1730_nosso-manifesto": [
 {"tipo": "capa_numero", "numero": "5", "titulo": "Frases que guiam<br>*tudo o que fazemos*"},
 {"tipo": "citacao", "titulo": "Tecnologia boa é a que *some.*", "texto": "O time para de pensar na ferramenta e volta a pensar no cliente."},
 {"tipo": "contraste", "antes": "Comprar o software primeiro", "depois": "Processo vem antes do *software.*", "texto": "Sem processo claro, nenhum sistema salva."},
 {"tipo": "citacao", "fundo": "claro", "titulo": "Automatizar bagunça só deixa a bagunça mais *rápida.*"},
 {"tipo": "capa_objeto", "icone": "store", "linha": "MANIFESTO 04", "titulo": "Pequena empresa merece<br>sistema de *empresa grande*"},
 {"tipo": "citacao", "titulo": "Promessa sem método é só *propaganda.*", "texto": "Seraphim. Tecnologia com método."},
 {"tipo": "cta", "foto": SERA, "titulo": "Qual frase é a *sua?*", "texto": "Comenta o número dela.", "botao": "COMENTA AQUI"},
],
"2026-10-20_0900_5-sinais-passou-das-ferramentas": [
 {"tipo": "capa", "foto": EU, "linha": "5 SINAIS DE QUE SUA EMPRESA", "titulo": "*Passou* das<br>ferramentas", "blocos": [("file-text", 40, 320, -12, 220), ("message-circle", 810, 240, 10, 200), ("alert-triangle", 830, 650, -6, 170)]},
 {"tipo": "topico", "fundo": "escuro", "titulo": "A informação mora em *vários lugares*", "rotulo": "SINAL", "numero": "01", "textos": ["“Tá na planilha ou no WhatsApp?”", "Quando ninguém sabe **onde está a verdade**, todo mundo perde tempo procurando."]},
 {"tipo": "topico", "fundo": "claro", "titulo": "Só *uma pessoa* sabe como funciona", "rotulo": "SINAL", "numero": "02", "textos": ["“Pergunta pra ela.”", "Se ela sai de férias, **a operação trava**."]},
 {"tipo": "topico", "fundo": "escuro", "titulo": "O mesmo dado é *digitado duas vezes*", "rotulo": "SINAL", "numero": "03", "textos": ["Pedido no WhatsApp, depois na planilha, depois no financeiro.", "**Cada digitação é uma chance de erro.**"]},
 {"tipo": "topico", "fundo": "claro", "titulo": "Relatório leva *dias*", "rotulo": "SINAL", "numero": "04", "textos": ["“Segunda eu te passo.”", "Decisão de hoje tomada com **número da semana passada**."]},
 {"tipo": "topico", "fundo": "escuro", "titulo": "O erro só aparece quando o *cliente reclama*", "rotulo": "SINAL", "numero": "05", "textos": ["E aí **já custou caro**."]},
 {"tipo": "fecho", "titulo": "Marcou 3 ou mais? *Hora de um sistema.*", "textos": ["Quantos você marcou? **Conta nos comentários.**"], "cartoes": ["Salva pra revisar depois", "Manda pra quem cuida da **operação**"]},
],
"2026-10-20_1730_por-que-a-seraphim-existe": [
 {"tipo": "capa", "foto": EU, "linha": "CARTA ABERTA", "titulo": "Por que a<br>*Seraphim* existe", "blocos": [("heart", 50, 330, -10, 200), ("users", 820, 260, 10, 210), ("sparkles", 830, 660, -6, 160)]},
 {"tipo": "citacao", "titulo": "A gente cansou de ver *gente boa presa* em trabalho repetitivo."},
 {"tipo": "contraste", "rotulo_a": "O SONHO", "antes": "Abrir um negócio pra atender bem", "rotulo_b": "A REALIDADE", "depois": "Passar o dia *conferindo planilha*"},
 {"tipo": "abertura", "fundo": "claro", "titulo": "A tecnologia que resolve isso *já existe*", "textos": ["Só que quase sempre é feita para **empresa grande**.", "Cara, complexa e do tamanho errado."], "icones": ["briefcase", "lock", "dollar-sign", "layers"]},
 {"tipo": "citacao", "titulo": "A Seraphim existe pra levar essa tecnologia pro *tamanho certo* da sua empresa."},
 {"tipo": "cta", "foto": EU, "titulo": "Sem complicar. Sem milagre. *Com método.*", "texto": "— Equipe Seraphim"},
],
"2026-10-21_0900_as-tres-frentes-da-seraphim": [
 {"tipo": "capa_numero", "numero": "3", "titulo": "Frentes da *Seraphim*"},
 {"tipo": "verbete", "rotulo": "FRENTE 01", "icone": "layers", "titulo": "Sistemas *sob medida*", "texto": "Ferramentas feitas para o **jeito que a sua empresa trabalha**.", "exemplo": "Pedidos, agenda e clientes **num lugar só**."},
 {"tipo": "verbete", "rotulo": "FRENTE 02", "fundo": "claro", "icone": "zap", "titulo": "*Automação*", "texto": "Tarefas repetidas **acontecendo sozinhas**.", "exemplo": "Lembretes, confirmações e relatórios **automáticos**."},
 {"tipo": "verbete", "rotulo": "FRENTE 03", "icone": "link", "titulo": "*Integração*", "texto": "As ferramentas que você já usa **conversando entre si**.", "exemplo": "O pedido vai do atendimento ao financeiro **sozinho**."},
 {"tipo": "cta", "foto": SERA_P, "titulo": "Qual sua empresa *precisa primeiro?*", "texto": "Responde no direct.", "botao": "MANDA NO DIRECT"},
],
"2026-10-21_1730_voce-precisa-de-sistema-proprio": [
 {"tipo": "capa_objeto", "icone": "help-circle", "material": "vidro", "linha": "RESPONDA 4 PERGUNTAS", "titulo": "Você precisa de um<br>*sistema próprio?*"},
 {"tipo": "contraste", "rotulo_a": "PERGUNTA 1", "antes": "Seu processo é comum no setor?", "rotulo_b": "SE SIM", "depois": "Use um *software pronto.*", "texto": "É **mais rápido e mais barato**. Se não, segue."},
 {"tipo": "abertura", "fundo": "claro", "titulo": "Usa 3+ ferramentas que *não conversam?*", "textos": ["WhatsApp, planilha, sistema fiscal, agenda…", "Se sim, **integração resolve muito**."], "icones": ["message-circle", "file-text", "receipt", "calendar"]},
 {"tipo": "topico", "fundo": "escuro", "titulo": "O pronto te obriga a *mudar o que funciona?*", "rotulo": "PERGUNTA", "numero": "03", "textos": ["Se sim, **sob medida faz sentido**."]},
 {"tipo": "topico", "fundo": "claro", "titulo": "Seu jeito de trabalhar é o seu *diferencial?*", "rotulo": "PERGUNTA", "numero": "04", "textos": ["Proteja ele com **um sistema próprio**."]},
 {"tipo": "citacao", "titulo": "A resposta honesta pode ser *“ainda não”.*", "texto": "E tudo bem."},
 {"tipo": "cta", "foto": EU, "titulo": "Na dúvida, a gente *ajuda a decidir.*", "texto": "Sem compromisso."},
],
"2026-10-22_0900_integracao-explicada-cozinha": [
 {"tipo": "capa_objeto", "icone": "flame", "linha": "EXPLICADO", "titulo": "Integração explicada<br>com uma *cozinha*"},
 {"tipo": "abertura", "titulo": "O garçom anota. O cozinheiro *vai até a mesa ler.*", "textos": ["E o caixa **pergunta de novo** o que a mesa comeu."], "icones": ["notebook-pen", "flame", "wallet", "repeat"]},
 {"tipo": "contraste", "rotulo_a": "SEM INTEGRAÇÃO", "antes": "Todo mundo trabalha dobrado", "rotulo_b": "E O RESULTADO", "depois": "O erro aparece *no prato.*"},
 {"tipo": "citacao", "titulo": "Integração é a comanda que vai *sozinha* pra cozinha e pro caixa."},
 {"tipo": "lista", "fundo": "claro", "rotulo": "NA SUA EMPRESA", "titulo": "A comanda *é:*", "itens": ["O pedido", "O cadastro", "A nota"]},
 {"tipo": "cta", "foto": SERA, "titulo": "Onde a sua comanda *se perde hoje?*", "texto": "Conta pra gente nos comentários.", "botao": "COMENTA AQUI"},
],
"2026-10-22_1730_glossario-api-webhook": [
 {"tipo": "capa_objeto", "icone": "notebook-pen", "material": "vidro", "linha": "5 PALAVRAS, SEM JARGÃO", "titulo": "O glossário que<br>ninguém te *explicou*"},
 {"tipo": "verbete", "rotulo": "VERBETE · SUBST. FEMININO", "icone": "key", "titulo": "*API*", "texto": "A **porta** pela qual um sistema conversa com outro.", "exemplo": "O site consultando o **estoque**."},
 {"tipo": "verbete", "rotulo": "VERBETE · SUBST. MASCULINO", "fundo": "claro", "icone": "bell", "titulo": "*Webhook*", "texto": "Um **aviso automático** quando algo acontece.", "exemplo": "Pagamento aprovado **avisa o sistema na hora**."},
 {"tipo": "verbete", "rotulo": "VERBETE · SUBST. FEMININO", "icone": "link", "titulo": "*Integração*", "texto": "Sistemas **trocando dados sozinhos**.", "exemplo": "O pedido vai do atendimento ao **financeiro**."},
 {"tipo": "verbete", "rotulo": "VERBETE · SUBST. FEMININO", "fundo": "claro", "icone": "zap", "titulo": "*Automação*", "texto": "Uma tarefa que acontece **sem ação humana**.", "exemplo": "O **lembrete de vencimento**."},
 {"tipo": "verbete", "rotulo": "VERBETE · SUBST. MASCULINO", "icone": "database", "titulo": "*Banco de dados*", "texto": "Onde a informação fica **guardada e organizada**.", "exemplo": "O **cadastro de clientes**."},
 {"tipo": "cta", "foto": SERA_P, "titulo": "Faltou alguma *palavra?*", "texto": "Pede nos comentários.", "botao": "COMENTA AQUI"},
],
"2026-10-23_0900_nosso-processo-5-etapas": [
 {"tipo": "capa", "foto": EU, "linha": "NOSSO MÉTODO", "titulo": "O processo em<br>*5 etapas*", "blocos": [("route", 40, 320, -12, 220), ("pen-tool", 810, 240, 10, 200), ("check-circle-2", 830, 650, -6, 170)]},
 {"tipo": "lista", "rotulo": "ETAPAS 1 A 3", "titulo": "Do problema ao *plano*", "itens": [("Escutar", "Conversamos com quem faz o trabalho."), ("Mapear", "Desenhamos o processo real e marcamos onde dói."), ("Priorizar", "Escolhemos o que resolve mais com menos.")]},
 {"tipo": "lista", "rotulo": "ETAPAS 4 E 5", "fundo": "claro", "titulo": "Do plano ao *uso*", "itens": [("Construir pequeno", "Entregamos uma parte que já funciona."), ("Melhorar com uso", "Ajustamos com quem usa todo dia.")]},
 {"tipo": "topico", "fundo": "escuro", "titulo": "Sem caixa-preta: você *acompanha tudo*", "rotulo": "ATUALIZAÇÕES", "numero": "SEMANAL", "textos": ["Você vê **o que está sendo construído**, enquanto é construído."]},
 {"tipo": "citacao", "titulo": "Projeto bom não termina na entrega. *Começa nela.*"},
 {"tipo": "cta", "foto": EU, "titulo": "Salva pra *lembrar.*", "texto": "E segue pra ver o método na prática."},
],
"2026-10-23_1730_o-que-nao-fazemos": [
 {"tipo": "capa_objeto", "icone": "x-circle", "linha": "HONESTIDADE", "titulo": "O que a Seraphim<br>*não faz*"},
 {"tipo": "lista", "rotulo": "NÃO FAZEMOS", "titulo": "Promessas *fáceis*", "marcador": "✕", "itens": [("Prometer resultado", "antes de entender o problema."), ("Vender sistema", "quando uma planilha bem feita resolve."), ("Usar IA", "só porque está na moda.")]},
 {"tipo": "lista", "rotulo": "NÃO FAZEMOS", "fundo": "claro", "titulo": "Projeto no *escuro*", "marcador": "✕", "itens": [("Entregar e sumir", "o suporte faz parte do projeto."), ("Esconder o que está sendo construído", "você acompanha cada etapa.")]},
 {"tipo": "citacao", "titulo": "O que a gente faz: tecnologia com *método.*"},
 {"tipo": "cta", "foto": SERA, "titulo": "Concorda com a *lista?*", "texto": "Qual você acrescentaria?", "botao": "COMENTA AQUI"},
],
"2026-10-25_1730_o-que-podemos-construir": [
 {"tipo": "capa", "foto": EU, "linha": "IDEIAS REAIS", "titulo": "O que podemos<br>*construir pra você*", "blocos": [("pie-chart", 40, 320, -12, 220), ("bell", 810, 240, 10, 200), ("users", 830, 650, -6, 170)]},
 {"tipo": "topico", "fundo": "escuro", "titulo": "Painel do *dia*", "rotulo": "IDEIA 01", "numero": "AO VIVO", "textos": ["Os números do dia **sem montar planilha**.", "Vendas, pedidos e pendências numa tela."]},
 {"tipo": "topico", "fundo": "claro", "titulo": "Cadastro *único*", "rotulo": "IDEIA 02", "numero": "1 LUGAR", "textos": ["Um cadastro de clientes que **o time inteiro usa igual**."]},
 {"tipo": "topico", "fundo": "escuro", "titulo": "Avisos *automáticos*", "rotulo": "IDEIA 03", "numero": "SOZINHO", "textos": ["Lembretes e confirmações que **saem sozinhos** por WhatsApp ou e-mail."]},
 {"tipo": "topico", "fundo": "claro", "titulo": "Ferramentas *conversando*", "rotulo": "IDEIA 04", "numero": "INTEGRADO", "textos": ["Suas ferramentas atuais **trocando dados entre si**."]},
 {"tipo": "topico", "fundo": "escuro", "titulo": "Sistema *inteiro*", "rotulo": "IDEIA 05", "numero": "SOB MEDIDA", "textos": ["Do **tamanho da sua operação**."]},
 {"tipo": "cta", "foto": EU, "titulo": "Tem um trabalho que *ninguém deveria fazer?*", "texto": "Manda pra gente.", "botao": "MANDA NO DIRECT"},
],
}


def main(filtros):
    for pasta, slides in C.items():
        if filtros and not any(f in pasta for f in filtros):
            continue
        dest = R / "fila" / pasta
        tmp = R / "testes" / "semana_carrosseis" / pasta
        shutil.rmtree(tmp, ignore_errors=True)
        asyncio.run(E.render(slides, tmp))
        arq = R / "arquivo" / "semana_antiga" / pasta
        if dest.exists():
            for f in list(dest.glob("slide-*.jpg")) + ([dest / "tiktok"] if (dest / "tiktok").exists() else []):
                arq.mkdir(parents=True, exist_ok=True)
                shutil.move(str(f), str(arq / f.name))
        dest.mkdir(parents=True, exist_ok=True)
        for f in (tmp / "instagram").glob("*.jpg"):
            shutil.copy(f, dest / f.name)
        shutil.copytree(tmp / "tiktok", dest / "tiktok")
        print(pasta, len(slides), "slides")


if __name__ == "__main__":
    main(sys.argv[1:])
