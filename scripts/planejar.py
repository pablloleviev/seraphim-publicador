"""
Planejador automático de conteúdo da Seraphim.

Roda todo dia no GitHub Actions. Para os próximos DIAS_A_FRENTE dias, vê quais horários
ainda não têm post e pede ao Gemini (texto, grátis) os roteiros que faltam:
  - vídeos  -> pedidos/<nome>.json   (o workflow "Gerar vídeos" transforma em vídeo)
  - carrosséis -> renderizados direto em fila/<data>_<nome>/

Volume sobe sozinho (planejamento.json):
  fase 1: 3 vídeos + 1 carrossel por dia
  fase 2: 5 vídeos + 2 carrosséis por dia
  fase 3: 10 vídeos + 5 carrosséis por dia

Variedade: nunca repete tema (historico.json), reveza formatos e o visual,
e cada dia passa por uma segunda rodada de revisão crítica antes de virar vídeo.
"""
import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from marca import ARROBA, USUARIO, INSTAGRAM_URL
import asyncio, json, os, re, sys, time, unicodedata, urllib.error, urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
BRT = timezone(timedelta(hours=-3))
CFG = json.loads((RAIZ / "planejamento.json").read_text(encoding="utf-8"))
HIST = RAIZ / "historico.json"
HT = "#inteligenciaartificial #automacao #tecnologia #startup #seraphimbr"
TEMAS = ["noir", "editorial", "terminal", "meianoite", "brutal", "vinho", "eletrico", "grafite", "ultravioleta"]


def proximo_tema(hist):
    """Tema usado há mais tempo: posts vizinhos no feed nunca ficam com a mesma cara."""
    ult = {}
    for i, h in enumerate(hist):
        if h.get("tema"):
            ult[h["tema"]] = i
    return min(TEMAS, key=lambda t: (ult.get(t, -1), TEMAS.index(t)))


# FORMATOS DE EDIÇÃO (motor/src/Cortes.tsx): cada vídeo tem uma cara diferente. Rodízio: o usado há mais tempo,
# e vídeos do mesmo dia nunca repetem formato.
# Pesos: noir (o visual antigo) é RARO por pedido do Pabllo (15/10/2026); "cartaz" foi retirado (não gostou).
FORMATOS = {"celular": 1.0, "terminal": 1.0, "documentario": 1.0, "eletrico": 1.0, "noticia": 1.0, "navegador": 1.0,
            "story": 1.0, "hud": 1.0, "vhs": 1.0, "noir": 0.25}
REPETE_APOS = 5     # um formato só pode voltar depois de 5 vídeos com outros formatos


def proximo_formato(hist, evitar=(), semente=""):
    """Sorteio ponderado e reproduzível: varia bastante, repetir é possível mas raro, noir é raríssimo."""
    import random
    recentes = [h.get("formato_edicao") for h in hist if h.get("formato_edicao")][-REPETE_APOS:]
    livres = [f for f in FORMATOS if f not in evitar and f not in recentes] or [f for f in FORMATOS if f not in evitar] or list(FORMATOS)
    rnd = random.Random(f"{semente}|{len(hist)}")
    return rnd.choices(livres, weights=[FORMATOS[f] for f in livres])[0]


POSES = ["pensando", "confiante", "surpreso", "preocupado", "feliz", "comemorando"]
MODELOS = {"impacto", "numero", "lista", "cta"}


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40] or "post"


def fase(d: date):
    atual = None
    for f in CFG["fases"]:
        if d >= date.fromisoformat(f["a_partir_de"]):
            atual = f
    return atual


_MODELOS = None


def modelos_texto():
    """Descobre quais modelos de texto do Gemini a chave tem hoje (os nomes mudam com o tempo)."""
    global _MODELOS
    if _MODELOS is None:
        req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200",
                                     headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]})
        ms = json.loads(urllib.request.urlopen(req, timeout=60).read()).get("models", [])
        nomes = [m["name"].split("/")[-1] for m in ms if "generateContent" in m.get("supportedGenerationMethods", [])]
        nomes = [n for n in nomes if "flash" in n and not re.search(r"tts|image|live|audio|embed|thinking|lite", n)]
        def nota(n):
            v = re.search(r"(\d+(?:\.\d+)?)", n)
            return (float(v.group(1)) if v else 0, "preview" not in n and "exp" not in n, "latest" in n)
        _MODELOS = sorted(nomes, key=nota, reverse=True) + ["gemini-flash-latest", "gemini-2.5-flash"]
        print("Modelos de texto:", _MODELOS[:5])
    return _MODELOS


def gemini(prompt, temperatura=1.0):
    corpo = json.dumps({"contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"responseMimeType": "application/json", "temperature": temperatura}}).encode()
    erro = None
    for modelo in modelos_texto():
        req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
                                     data=corpo, headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"],
                                                          "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                print(f"(roteiro escrito com {modelo})")
                return json.loads(json.loads(r.read())["candidates"][0]["content"]["parts"][0]["text"])
        except urllib.error.HTTPError as e:
            erro = f"{modelo}: {e.code} {e.read().decode()[:200]}"
        except Exception as e:
            erro = f"{modelo}: {e}"
        print("[aviso]", erro)
    raise RuntimeError(f"Gemini falhou: {erro}")


EXEMPLO_VIDEO = {
 "nome": "planilha-nao-e-sistema",
 "formato": "erro que você comete",
 "funil": "topo",
 "titulo": "Planilha não é sistema",
 "personalidade": "impacto",
 "estilo_legenda": "palavra",
 "cenas": [
  {
   "tipo": "objeto",
   "icone": "file-text",
   "titulo": "Sua planilha *funciona.*",
   "transicao": "zoom",
   "narracao": "Sua planilha funciona."
  },
  {
   "tipo": "frase",
   "titulo": "Até o dia em que *não funciona.*",
   "transicao": "flash",
   "camera": "tremor",
   "narracao": "Até o dia em que não funciona."
  },
  {
   "tipo": "lista",
   "titulo": "O dia em que *quebra:*",
   "itens": [
    "Duas pessoas editando",
    "A fórmula some",
    "Qual é a versão certa?"
   ],
   "narracao": "Duas pessoas editam ao mesmo tempo. Uma fórmula some. Ninguém sabe qual é a versão certa."
  },
  {
   "tipo": "contraste",
   "antes": "Planilha como coração da empresa",
   "depois": "Planilha para *começar*",
   "narracao": "Planilha é ótima pra começar, mas não foi feita pra ser o coração de uma empresa."
  },
  {
   "tipo": "moedas",
   "titulo": "Um sistema *guarda, controla e avisa*",
   "icones": [
    "database",
    "lock",
    "bell",
    "shield-check"
   ],
   "narracao": "Um sistema guarda o histórico, controla quem mexe em quê e avisa quando algo sai do lugar."
  },
  {
   "tipo": "frase",
   "titulo": "É sobre saber a hora de *crescer.*",
   "narracao": "Não é sobre abandonar a planilha. É sobre saber a hora de crescer."
  },
  {
   "tipo": "fecho",
   "titulo": "Manda pra quem *vive na planilha*",
   "cartoes": [
    "Salva o vídeo",
    "Envia pra um amigo"
   ],
   "narracao": "Salva esse vídeo e manda pra quem vive dentro da planilha."
  }
 ],
 "legenda": "Planilha é ótima pra começar. O problema é quando ela vira o lugar onde a empresa inteira mora. 📊",
 "legenda_tiktok": "Sua planilha funciona. Até o dia em que não funciona.",
 "hashtags": [
  "#planilha",
  "#gestao",
  "#sistemas",
  "#pequenasempresas",
  "#seraphimbr"
 ],
 "capa": "Planilha *não é* sistema"
}
CATALOGO_CENAS = """MOTOR "ESTILO" (direção criativa aprovada: preto + dourado, vidro 3D, objetos 3D dourados, fumaça, desfoque, cinema).
Cada vídeo tem PERSONALIDADE própria e composição própria — identidade fixa, execução sempre diferente.
Campos do vídeo: "personalidade": impacto | dinamico | elegante | minimal | emocional (escolha pelo assunto e emoção);
"estilo_legenda": karaoke | palavra | sutil | nenhuma; "tarja": true/false (tarjas de cinema, combina com elegante/emocional);
"paleta": """ + " | ".join(json.loads((RAIZ / "estilos" / "paletas.json").read_text(encoding="utf-8"))) + """ (cor escolhida pela mensagem; varie no dia e na semana — o dourado não precisa estar em tudo).
Tipos de cena (5 a 9 cenas; NUNCA o mesmo tipo duas vezes seguidas; cada cena 1 ideia, 1 a 4 s de fala; "titulo" usa *destaque* dourado):
- capa: pessoa (Pabllo) com blocos de vidro 3D flutuando. "linha" (frase curta em caixa alta), "titulo" (manchete; <br> quebra linha), "icones": 3 nomes de ícone.
- pessoa: texto gigante vazado ATRÁS da pessoa. "linha" (1 palavra), "titulo".
- objeto: um ícone 3D enorme girando com anel de luz. "icone", "titulo" (curto, caixa alta).
- moedas: moedas 3D douradas caindo com ícones. "titulo", "icones": 3 a 5.
- cartao: cartão de vidro 3D com rótulo + número/palavra grande + curva desenhando. "titulo", "rotulo", "numero" (curto, ex.: "24 H", "1 CLIQUE"; NUNCA estatística inventada). Opcional "fundo":"claro".
- numero: número gigante contando na tela cheia. "numero", "rotulo", "titulo".
- lista: cartões de vidro entrando em profundidade. "titulo", "itens": 2 a 4 textos curtos.
- contraste: tela dividida antes x depois com linha dourada. "antes", "depois" (com *destaque*).
- citacao: frase elegante em destaque, revelação lenta. "titulo".
- frase: frase com palavras surgindo do desfoque. "titulo". Opcional "fundo":"claro".
- fecho: SEMPRE a última. "titulo", "cartoes": 2 textos curtos (ações).
Opcional em qualquer cena: "transicao" (chicote|zoom|corte|flash|mascara|dissolve|luz|desfoque|deslize) e "camera" (empurra|afasta|deriva|inclina|tremor|parada) para momentos especiais; sem isso, a personalidade decide.
Ícones disponíveis (Lucide): """ + ", ".join(sorted(p.stem for p in (RAIZ / "carrossel" / "icones").glob("*.svg"))) + """
Poses do mascote: pensando, confiante, surpreso, preocupado, feliz, comemorando."""

REGRAS_FUNIL = """FUNIL (decida para cada post e escreva em "funil"):
- "topo" (~70%): IA, tecnologia, produtividade, curiosidades para qualquer pessoa. Objetivo: GANHAR SEGUIDOR. A chamada final pede para seguir a Seraphim.
- "meio" (~20%): dores de gestão (orçamento, estoque, cliente que some, planilha, atendimento). Objetivo: confiança. Chamada: palavra-chave
  para receber um material grátis no direct (ex.: cta "COMENTA *CHECKLIST*"; narração "Comenta CHECKLIST aqui que eu te mando no direct"). A pessoa comenta NO POST (nunca "comenta no direct"); o material é que chega no direct. + seguir. Preencha "palavra_chave" (1 palavra, MAIÚSCULA, sem acento)
  e "material": {"tipo": "Checklist"|"Passo a passo"|"Modelo", "titulo": "...", "subtitulo": "...", "itens": [5 a 8 {"titulo","texto"}], "dica": "..."}.
  O material deve ser REALMENTE útil e coerente com o vídeo, em português simples. Nada de prometer o que o material não entrega.
- "fundo" (~10%, SÓ quando o assunto for oficina mecânica): chamada para conhecer o AutoFlow (sistema de gestão de oficinas da Seraphim), "link na bio", e seguir.
  Sobre o AutoFlow, diga SOMENTE o que está na ficha abaixo (nunca invente funcionalidade, preço, teste grátis ou resultado).
CHAMADA FINAL (cena cta + última frase da narração): NÃO use frase pronta. Escreva a melhor chamada para AQUELE vídeo, ligada ao gancho e ao
assunto, natural, curta (até ~18 palavras), sem soar genérica. Ela tem que fazer sentido sozinha e com o resto do roteiro.
A legenda do post segue a mesma chamada (topo: seguir; meio: comentar a palavra-chave; fundo: link na bio)."""
FICHA_AUTOFLOW = (RAIZ / "estilos" / "autoflow.md").read_text(encoding="utf-8")
TEXTO_IG = (RAIZ / "estilos" / "texto-instagram.md").read_text(encoding="utf-8")

EXEMPLO_CARROSSEL = {
 "nome": "glossario-api-webhook",
 "titulo": "O glossário que ninguém te explicou",
 "slides": [
  {
   "tipo": "capa_objeto",
   "icone": "notebook-pen",
   "material": "vidro",
   "linha": "5 PALAVRAS, SEM JARGÃO",
   "titulo": "O glossário que<br>ninguém te *explicou*"
  },
  {
   "tipo": "verbete",
   "rotulo": "VERBETE",
   "icone": "key",
   "titulo": "*API*",
   "texto": "A **porta** pela qual um sistema conversa com outro.",
   "exemplo": "O site consultando o **estoque**."
  },
  {
   "tipo": "verbete",
   "rotulo": "VERBETE",
   "fundo": "claro",
   "icone": "bell",
   "titulo": "*Webhook*",
   "texto": "Um **aviso automático** quando algo acontece.",
   "exemplo": "Pagamento aprovado **avisa o sistema na hora**."
  },
  {
   "tipo": "contraste",
   "rotulo_a": "SEM INTEGRAÇÃO",
   "antes": "Digitar o pedido 3 vezes",
   "rotulo_b": "COM INTEGRAÇÃO",
   "depois": "O dado entra *uma vez*",
   "texto": "E aparece **onde precisa**."
  },
  {
   "tipo": "cta",
   "pessoa": "sera_pensando",
   "titulo": "Faltou alguma *palavra?*",
   "texto": "Pede nos comentários.",
   "botao": "COMENTA AQUI"
  }
 ],
 "legenda": "Salva pra consultar quando alguém falar difícil na reunião. 😅 Qual palavra faltou?",
 "hashtags": [
  "#tecnologia",
  "#glossario",
  "#automacao",
  "#seraphimbr"
 ]
}
PADRAO_FUNIL = ["topo", "topo", "meio", "topo", "topo", "topo", "meio", "topo", "fundo", "topo"]  # 70% / 20% / 10%


def pesquisar_ideias(dia):
    """Pesquisa na internet (Gemini + Google Search) curiosidades e novidades de tecnologia/IA para inspirar os roteiros."""
    prompt = (f"Hoje é {dia:%d/%m/%Y}. Pesquise na internet e liste 12 ideias de vídeos curtos de CURIOSIDADE e NOVIDADE sobre "
              "tecnologia, inteligência artificial, automação, golpes digitais, apps úteis e negócios digitais que despertariam a curiosidade "
              "de brasileiros donos de pequenos negócios e profissionais. Prefira fatos reais e recentes (últimas semanas), coisas surpreendentes, "
              "'você sabia', bastidores de big techs, ferramentas novas grátis. Para cada ideia: título chamativo + o fato em 1 frase + fonte (site). "
              "Responda em português, em lista simples.")
    corpo = json.dumps({"contents": [{"parts": [{"text": prompt}]}], "tools": [{"google_search": {}}]}).encode()
    for modelo in modelos_texto()[:3]:
        req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
                                     data=corpo, headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                partes = json.loads(r.read())["candidates"][0]["content"]["parts"]
                txt = "\n".join(x.get("text", "") for x in partes)
                print("Pesquisa de ideias ok:", txt[:300].replace("\n", " "))
                return txt[:6000]
        except Exception as e:
            print(f"[aviso] pesquisa com {modelo} falhou: {e}")
    return ""


def tags(v, n=12):
    hs = [h if str(h).startswith("#") else "#" + str(h) for h in (v.get("hashtags") or [])]
    hs = [re.sub(r"[^#\w]", "", h.lower()) for h in hs if "publicador" not in h.lower()]
    if not hs:
        return HT
    if "#seraphimbr" not in hs:
        hs.append("#seraphimbr")
    out = []
    for h in hs:
        if h not in out and len(h) > 2:
            out.append(h)
    return " ".join(out[:n - 1] + (["#seraphimbr"] if "#seraphimbr" not in out[:n - 1] else []))


def funis_do_dia(hist, n):
    k = sum(1 for h in hist if h.get("tipo") == "video" and h.get("funil"))
    return [PADRAO_FUNIL[(k + i) % len(PADRAO_FUNIL)] for i in range(n)]


def pedir_dia(dia, n_v, n_c, hist):
    funis = funis_do_dia(hist, n_v)
    ideias = pesquisar_ideias(dia)
    usados = [h["titulo"] for h in hist][-300:]
    formatos_recentes = [h.get("formato", "") for h in hist][-12:]
    vids = [h for h in hist if h.get("tipo") == "video" and h.get("cenas")][-15:]
    estruturas = [" > ".join(str(x) for x in h["cenas"] if x) for h in vids]
    ganchos = [next((x for x in h["cenas"] if x), "") for h in vids][-5:]
    pers_recentes = [h.get("personalidade", "") for h in vids][-3:]
    cores_recentes = [h.get("paleta", "") for h in hist if h.get("paleta")][-10:]
    cars = [" > ".join(h.get("slides", [])) for h in hist if h.get("tipo") == "carrossel" and h.get("slides")][-8:]
    buscas_usadas = sorted({b for h in hist for b in h.get("buscas", [])})[-150:]
    regras = f"""Você é o roteirista-chefe da Seraphim ({ARROBA}), startup brasileira de tecnologia:
sistemas sob medida, automações e inteligência artificial para pequenas e médias empresas.
Referências de linha editorial: perfis como os de startups de IA/automação, criadores de "IA para negócios",
SaaS de gestão. Público: donos de pequenos negócios e profissionais que querem usar tecnologia.

Crie o conteúdo do dia {dia:%d/%m/%Y} ({['segunda','terça','quarta','quinta','sexta','sábado','domingo'][dia.weekday()]}):
{n_v} roteiros de VÍDEO (Reels/TikTok vertical) e {n_c} CARROSSÉIS.
NÃO faça só vídeo com cara de comercial: pelo menos 1 vídeo por dia deve ser de CURIOSIDADE/NOVIDADE real (fato surpreendente,
"você sabia", notícia de IA explicada), escolhida a partir desta pesquisa feita hoje na internet (use só fatos que estão nela; não invente):
{ideias}
O GANCHO (primeiros 3 segundos) é a parte mais importante: comece com o fato mais surpreendente, uma pergunta que incomoda ou um contraste forte.
Cada cena pode ter "clima" (trilha sonora): epico | tensao | sombrio | emocao | energia | inspira — escolha para criar uma montanha-russa
emocional: gancho épico/energia, problema em tensão, virada em emoção, solução em energia/inspiração, final épico.
NÍVEL DE FUNIL OBRIGATÓRIO DE CADA VÍDEO, NESTA ORDEM: {funis} (o assunto de cada vídeo deve combinar com o nível: fundo = oficina mecânica + AutoFlow; meio = dor de gestão + palavra-chave; topo = IA/tecnologia para atrair seguidores).

REGRAS DE QUALIDADE (obrigatórias):
- Cada post é sobre um tema DIFERENTE. NUNCA repita nem parafraseie estes temas já usados: {json.dumps(usados, ensure_ascii=False)}
- Formatos disponíveis (reveze; não repita formato no mesmo dia se possível; evite os recentes {formatos_recentes}):
  tutorial passo a passo, mito vs verdade, erro que você comete, antes e depois, lista prática, notícia/tendência de IA explicada,
  bastidores de startup, comparação (X vs Y), pergunta polêmica, curiosidade/você sabia, notícia de IA explicada, história curta de cliente (genérica, sem nomes reais), checklist, "você sabia".
- Gancho forte na 1ª cena (pergunta, número ou contraste) — a pessoa decide em 1 segundo se fica.
- DIVERSIDADE (regra do Pabllo): cada vídeo tem que ser DIFERENTE e MELHOR que o anterior, nunca o mesmo "padrãozinho".
  Estas foram as sequências de cenas dos últimos vídeos — NÃO repita nenhuma e nem siga a mesma ordem: {json.dumps(estruturas, ensure_ascii=False)}
  O tipo da 1ª cena (gancho) não pode ser nenhum destes, usados nos últimos vídeos: {json.dumps(ganchos, ensure_ascii=False)}
  Personalidades dos últimos vídeos (use OUTRA no primeiro vídeo do dia e não repita personalidade no mesmo dia): {json.dumps(pers_recentes, ensure_ascii=False)}
  Sequências de slides dos últimos carrosséis (NÃO repita): {json.dumps(cars, ensure_ascii=False)}
  Paletas dos últimos posts (equilibre a grade; não repita a mesma cor em posts seguidos): {json.dumps(cores_recentes, ensure_ascii=False)}
  Varie a quantidade de cenas (6 a 10), o ritmo (cenas curtas e rápidas x uma cena que respira), a ordem e a combinação de tipos.
  Nos vídeos do mesmo dia, nenhum pode ter a mesma 1ª cena nem a mesma estrutura de outro.
  Termos de busca de foto já usados (invente outros, com cenas e ângulos diferentes): {json.dumps(buscas_usadas, ensure_ascii=False)}
- Uma ideia por cena. Exemplos concretos do dia a dia de pequenos negócios (loja, clínica, salão, oficina, restaurante, escritório, e-commerce).
- Vídeo: narração total entre 70 e 110 palavras, frases curtas e naturais para ser falada em voz alta.
- PROIBIDO inventar estatística: nada de "80% das pessoas", "5 vezes mais", "30% da margem". Fale de forma qualitativa ("a maioria", "bem mais barato")
  ou em hipótese clara ("imagina perder 10 clientes por mês"). No "contador", o número é um EXEMPLO e o rótulo começa com "Ex.:".
- Nada de nomes de empresas/pessoas reais como clientes.
{CATALOGO_CENAS}
{REGRAS_FUNIL}
FICHA DO AUTOFLOW:
{FICHA_AUTOFLOW}
- Carrossel (padrão aprovado, estilo Blue Ocean em preto + dourado): 5 a 8 slides, estrutura PRÓPRIA por carrossel (não repetir a sequência de tipos de outro carrossel recente). Capa promete exatamente o que o miolo entrega. Títulos com *destaque* dourado; no corpo, **negrito** nos trechos-chave. Tipos de slide:
  capa {{"linha","titulo"(<br> quebra),"pessoa":"pabllo","blocos_icones":[3 ícones]}} | capa_objeto {{"linha","titulo","icone","material":"moeda"|"vidro"}} | capa_numero {{"numero","titulo"}} |
  abertura {{"titulo","textos":[2-3 parágrafos curtos],"icones":[4]}} | topico {{"titulo","rotulo","numero"(curto),"textos":[1-3],"fundo":"claro"|"escuro"}} |
  verbete {{"rotulo","icone","titulo","texto","exemplo"}} | lista {{"rotulo","titulo","itens":[[titulo,explicação]x2-4],"marcador"(opcional "✕" ou "→")}} |
  contraste {{"rotulo_a","antes","rotulo_b","depois","texto"}} | citacao {{"titulo","texto"}} | fecho {{"titulo","textos":[1],"cartoes":[2]}} |
  cta {{"titulo","texto","botao","pessoa":"pabllo"|"sera_confiante"|"sera_pensando"}} (SEMPRE o último).
  capa_tipografica {{"linha","titulo","texto"}} (capa clara, editorial, só tipografia).
  Cada carrossel tem "paleta" (mesmas opções dos vídeos), escolhida pela mensagem e diferente dos posts vizinhos.
  Primeiro slide: capa, capa_objeto, capa_numero ou capa_tipografica (reveze; nunca a mesma capa em posts seguidos). Alterne fundos escuro/claro no miolo. Pessoa ou Sera em parte dos carrosséis, não em todos. Nunca invente número/estatística.
- Legenda (Instagram): ÚNICA para cada post, ligada ao gancho e ao assunto; 2 a 4 linhas curtas com emoji, uma pergunta que puxa comentário e a chamada do funil; SEM hashtags dentro dela.
- "legenda_tiktok": legenda própria para o TikTok (mais curta e direta, 1 a 2 linhas, tom de conversa), diferente da do Instagram.
- "hashtags": 4 a 6 hashtags de AQUELE post (2-3 de nicho, 1-2 médias, no máximo 1 ampla), sempre incluindo #seraphimbr; nunca #seraphimpublicador; nunca o mesmo conjunto de outro post.
- "capa": título CURTO da capa (até 6 palavras, com *destaque* na palavra-chave), diferente do gancho falado; pode ser pergunta ou número.
- "capa_cena": em INGLÊS, uma cena concreta e fotografável para a imagem da capa (lugar + objeto + luz), SEM texto/letras; cada post com cena diferente das outras do dia (ex.: "mechanic's hands holding a phone with a glowing notification, dark garage, warm rim light").
- "nome": slug curto em minúsculas com hífens, único.

MANUAL DE TEXTO (ganchos, legendas, narração e slides; siga à risca):
{TEXTO_IG}

DIREÇÃO CRIATIVA APROVADA (identidade fixa, execução sempre nova; siga à risca):
{(RAIZ / "estilos" / "direcao-criativa.md").read_text(encoding="utf-8")}

Responda SÓ um JSON: {{"videos": [...{n_v} itens], "carrosseis": [...{n_c} itens]}}
Exemplo de vídeo: {json.dumps(EXEMPLO_VIDEO, ensure_ascii=False)}
Exemplo de carrossel: {json.dumps(EXEMPLO_CARROSSEL, ensure_ascii=False)}"""
    rascunho = gemini(regras, 1.0)
    revisao = f"""Você é o diretor criativo exigente da Seraphim. Abaixo está o rascunho do conteúdo do dia.
Revise CADA post com olhar crítico e devolva a versão MELHORADA no mesmo formato JSON:
- corrija ortografia, palavras repetidas e frases estranhas (leia em voz alta mentalmente);
- remova todo tique de IA do MANUAL DE TEXTO abaixo (revelações forçadas, "não é X, é Y", frases-metralhadora, vocabulário de IA, isca de engajamento, excesso de emoji);
- troque ganchos fracos por ganchos que prendem; corte palavras inúteis; deixe a narração natural, falada;
- garanta que nenhum post se pareça com outro do dia nem com estes temas já usados: {json.dumps(usados[-80:], ensure_ascii=False)};
- DIVERSIDADE: compare a sequência de tipos de cena de cada vídeo com a dos outros do dia e com as dos últimos vídeos (estão nas regras);
  se estiver parecida (mesmo gancho, mesma ordem, mesmo "padrãozinho"), REMONTE a estrutura com outra combinação de cenas;
  troque buscas de foto genéricas por cenas específicas e diferentes das já usadas;
- confira todas as regras: tipos de cena válidos (catálogo do motor ESTILO) e sem repetir em sequência, 5-9 cenas, personalidade coerente com o assunto, 70-110 palavras de narração, pontuação colada;
- A CHAMADA FINAL é a parte mais importante: confira se ela combina com o gancho e o assunto, se o funil está certo (oficina -> pode ser fundo; gestão -> meio; resto -> topo), se não tem frase sem sentido, e reescreva se estiver genérica;
- remova QUALQUER estatística inventada e qualquer afirmação sobre o AutoFlow que não esteja na ficha;
- nos posts de meio, confira se o material é útil, coerente com o vídeo e se a palavra-chave aparece na cta e na legenda;
- mantenha exatamente {n_v} vídeos e {n_c} carrosséis.
Regras completas originais, para referência:
{regras}

RASCUNHO:
{json.dumps(rascunho, ensure_ascii=False)}"""
    for tentativa in range(1, 4):
        try:
            return gemini(revisao, 0.6)
        except Exception as e:
            print(f"[aviso] revisão falhou na tentativa {tentativa}/3 ({str(e)[:160]})")
            time.sleep(20 * tentativa)
    print("[ALERTA] revisão do roteiro NÃO rodou; usando rascunho sem revisão")
    return rascunho


def limpar_linhas(ls):
    return [re.sub(r"\s+([?!.,:;])", r"\1", str(l)).upper().replace("*", "*") for l in ls][:3]


TIPOS = {"capa", "pessoa", "objeto", "moedas", "cartao", "numero", "lista", "contraste", "citacao", "frase", "fecho"}
PERSONALIDADES = {"impacto", "dinamico", "elegante", "minimal", "emocional"}
ICONES = {p.stem for p in (RAIZ / "carrossel" / "icones").glob("*.svg")}


def validar_video(v):
    cenas = []
    for c in v.get("cenas", []):
        if c.get("tipo") not in TIPOS or not str(c.get("narracao", "")).strip():
            continue
        for k in ("titulo", "linha", "antes", "depois"):
            if isinstance(c.get(k), str):
                c[k] = re.sub(r"\s+([?!.,:;])", r"\1", c[k]).strip()
        for k in ("icones",):
            if c.get(k):
                c[k] = [i if i in ICONES else "sparkles" for i in c[k]]
        if c.get("icone") and c["icone"] not in ICONES:
            c["icone"] = "sparkles"
        if c["tipo"] in ("lista",) and not c.get("itens"):
            c["tipo"] = "frase"
        if c["tipo"] == "contraste" and not (c.get("antes") and c.get("depois")):
            c["tipo"] = "frase"; c.setdefault("titulo", c.get("depois", ""))
        if c["tipo"] == "moedas" and not c.get("icones"):
            c["icones"] = ["zap", "clock", "check-circle-2"]
        if cenas and cenas[-1]["tipo"] == c["tipo"] and c["tipo"] != "fecho":
            c["tipo"] = "citacao" if c["tipo"] != "citacao" else "frase"
        cenas.append(c)
    if not cenas or cenas[-1]["tipo"] != "fecho":
        raise ValueError("sem chamada final")
    if len(cenas) < 5:
        raise ValueError("roteiro curto demais")
    v["cenas"] = cenas
    if v.get("personalidade") not in PERSONALIDADES:
        v["personalidade"] = "dinamico"
    if v.get("paleta") not in json.loads((RAIZ / "estilos" / "paletas.json").read_text(encoding="utf-8")):
        v["paleta"] = "ouro"
    if v.get("estilo_legenda") not in ("karaoke", "palavra", "sutil", "nenhuma"):
        v["estilo_legenda"] = "karaoke"
    if v.get("funil") not in ("topo", "meio", "fundo"):
        v["funil"] = "topo"
    if v["funil"] == "meio" and not (v.get("palavra_chave") and (v.get("material") or {}).get("itens")):
        raise ValueError("post de meio sem palavra-chave/material")
    return v


def amostras(n):
    """Gera n roteiros de teste (amostras/), sem mexer na fila nem no histórico."""
    hist = json.loads(HIST.read_text(encoding="utf-8")) if HIST.exists() else []
    plano = pedir_dia(datetime.now(BRT).date(), n, 0, hist)
    (RAIZ / "pedidos").mkdir(exist_ok=True)
    for v in plano.get("videos", []):
        try:
            v = validar_video(v)
        except Exception as e:
            print(f"[aviso] amostra descartada: {e}"); continue
        nome = "amostra-" + slug(v.get("nome") or "video")
        spec = {"nome": nome, "arroba": ARROBA, "cenas": v["cenas"], "motor": "cortes", "amostra": True, "voz": "gemini",
                "funil": v["funil"], "legenda": v.get("legenda", "")}
        if v["funil"] == "meio":
            import material
            m = dict(v["material"]); m.setdefault("slug", nome)
            spec.update(palavra_chave=v["palavra_chave"], material_url=material.gerar(m), material_titulo=m.get("titulo", ""))
        (RAIZ / "pedidos" / f"{nome}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
        print("amostra:", nome, v["funil"], "| CTA:", v["cenas"][-1].get("texto"), "|", v["cenas"][-1].get("narracao"))


def main():
    if os.environ.get("AMOSTRAS"):
        return amostras(int(os.environ["AMOSTRAS"]))
    hist = json.loads(HIST.read_text(encoding="utf-8")) if HIST.exists() else []
    # temas que já estão na fila também contam como usados
    nomes_fila = {d.name.split("_", 2)[2] for d in (RAIZ / "fila").iterdir() if d.is_dir() and d.name.count("_") >= 2}
    for n in nomes_fila:
        if not any(h["nome"] == n for h in hist):
            hist.append({"nome": n, "titulo": n.replace("-", " "), "formato": ""})
    nomes = {h["nome"] for h in hist}
    hoje = datetime.now(BRT).date()
    (RAIZ / "pedidos").mkdir(exist_ok=True)
    criados = 0
    for k in range(1, int(os.environ.get("DIAS") or CFG["dias_a_frente"]) + 1):
        dia = hoje + timedelta(days=k)
        f = fase(dia)
        if not f:
            continue
        ocupados = {d.name.split("_")[1] for d in (RAIZ / "fila").glob(f"{dia}_*")}
        ocupados |= {json.loads(p.read_text())["quando"][11:16].replace(":", "")
                     for p in (RAIZ / "pedidos").glob("*.json") if json.loads(p.read_text()).get("quando", "").startswith(str(dia))}
        hv = [h for h in f["videos"] if h.replace(":", "") not in ocupados]
        hc = [h for h in f["carrosseis"] if h.replace(":", "") not in ocupados]
        if not hv and not hc:
            continue
        print(f"== {dia}: faltam {len(hv)} vídeos e {len(hc)} carrosséis")
        plano = pedir_dia(dia, len(hv), len(hc), hist)
        formatos_do_dia = []
        for hora, v in zip(hv, plano.get("videos", [])):
            try:
                v = validar_video(v)
            except Exception as e:
                print(f"[aviso] vídeo descartado: {e}"); continue
            nome = slug(v.get("nome") or v.get("titulo", "video"))
            while nome in nomes:
                nome += "-2"
            nomes.add(nome)
            tema = "noir"  # temas pausados: Pabllo reprovou (2026-10-10)
            fmt = proximo_formato(hist, evitar=formatos_do_dia, semente=f"{dia}{hora}")
            formatos_do_dia.append(fmt)
            spec = {"nome": nome, "arroba": ARROBA, "quando": f"{dia} {hora}", "cenas": v["cenas"], "motor": "estilo",
                    "personalidade": v["personalidade"], "estilo_legenda": v["estilo_legenda"], "tarja": bool(v.get("tarja")), "paleta": v.get("paleta", "ouro"),
                    "formato": fmt, "titulo": v.get("titulo", nome), "numero": criados + 1,
                    "funil": v["funil"], "genero_voz": "masculina" if criados % 3 else "feminina",
                    "legenda": (v.get("legenda", "").strip() + "\n\n" + tags(v)),
                    "legenda_tiktok": (str(v.get("legenda_tiktok") or v.get("legenda", "")).strip() + "\n\n" + tags(v, 6))}
            if v["funil"] == "meio":
                import material
                m = dict(v["material"]); m.setdefault("slug", nome)
                spec["palavra_chave"] = re.sub(r"[^A-Z0-9]", "", v["palavra_chave"].upper())
                spec["material_url"] = material.gerar(m)
                spec["material_titulo"] = m.get("titulo", "").replace("*", "")
            (RAIZ / "pedidos" / f"{nome}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
            buscas = [c.get("busca") for c in v["cenas"] if c.get("busca")] + [b for c in v["cenas"] for b in (c.get("buscas") or [])] \
                     + [it.get("busca") for c in v["cenas"] for it in (c.get("itens") or []) if isinstance(it, dict) and it.get("busca")]
            hist.append({"nome": nome, "funil": v["funil"], "titulo": v.get("titulo", nome), "formato": v.get("formato", ""), "dia": str(dia), "tipo": "video", "tema": tema, "formato_edicao": fmt, "capa": v.get("capa", ""), "capa_cena": v.get("capa_cena", ""),
                         "cenas": [c.get("tipo") for c in v["cenas"]], "buscas": buscas, "personalidade": v["personalidade"], "paleta": v.get("paleta", "ouro")})
            criados += 1
        for hora, c in zip(hc, plano.get("carrosseis", [])):
            import estilo_ref
            slides = [s for s in c.get("slides", []) if s.get("tipo") in estilo_ref.TIPOS and (s.get("titulo") or s.get("numero") or s.get("depois"))]
            if len(slides) < 4:
                print("[aviso] carrossel descartado: poucos slides"); continue
            fotos = {"pabllo": RAIZ / "assets/pessoas/pabllo_recorte.png", "sera_confiante": RAIZ / "carrossel/sera/confiante.png",
                     "sera_pensando": RAIZ / "carrossel/sera/pensando.png"}
            for s in slides:
                for k in ("titulo", "linha"):
                    if isinstance(s.get(k), str):
                        s[k] = re.sub(r"\s+([?!.,:;])", r"\1", s[k])
                if s.get("pessoa") in fotos:
                    s["foto"] = fotos[s["pessoa"]].as_uri()
                if s["tipo"] == "capa":
                    s.setdefault("foto", fotos["pabllo"].as_uri())
                    ics = [i if i in ICONES else "sparkles" for i in (s.get("blocos_icones") or ["layers", "zap", "link"])][:3]
                    s["blocos"] = list(zip(ics + ["zap"] * (3 - len(ics)), [40, 800, 820], [300, 220, 640], [-14, 12, -8], [230, 210, 170]))
                for k in ("icone",):
                    if s.get(k) and s[k] not in ICONES:
                        s[k] = "sparkles"
                if s.get("icones"):
                    s["icones"] = [i if i in ICONES else "sparkles" for i in s["icones"]][:4]
                if s["tipo"] == "abertura":
                    s.setdefault("textos", []); s.setdefault("icones", ["zap", "clock", "users", "check-circle-2"])
                if s["tipo"] == "topico":
                    s.setdefault("textos", []); s.setdefault("rotulo", ""); s.setdefault("numero", "")
                if s["tipo"] == "fecho":
                    s.setdefault("textos", []); s.setdefault("cartoes", ["Salva", "Compartilha"])
            if slides[-1]["tipo"] != "cta":
                slides.append({"tipo": "cta", "titulo": "Gostou? *Salva* e segue", "texto": "Mais tecnologia com método."})
            nome = slug(c.get("nome") or c.get("titulo", "carrossel"))
            while nome in nomes:
                nome += "-2"
            nomes.add(nome)
            destino = RAIZ / "fila" / f"{dia}_{hora.replace(':', '')}_{nome}"
            tema = "estilo"
            tmpd = RAIZ / "testes" / "_car" / nome
            asyncio.run(estilo_ref.render(slides, tmpd, c.get("paleta") if c.get("paleta") in estilo_ref.PALETAS else "ouro"))
            destino.mkdir(parents=True, exist_ok=True)
            import shutil as _sh
            for f in (tmpd / "instagram").glob("*.jpg"):
                _sh.copy(f, destino / f.name)
            _sh.copytree(tmpd / "tiktok", destino / "tiktok", dirs_exist_ok=True)
            _sh.rmtree(tmpd, ignore_errors=True)
            (destino / "item.json").write_text(json.dumps({
                "tipo": "carrossel", "legenda": c.get("legenda", "").strip() + "\n\n" + tags(c),
                "legenda_tiktok": (str(c.get("legenda_tiktok") or c.get("legenda", "")).strip() + "\n\n" + tags(c, 6)),
                "quando": f"{dia}T{hora}:00-03:00"}, ensure_ascii=False, indent=2), encoding="utf-8")
            modelo_capa = slides[0]["tipo"]
            hist.append({"nome": nome, "titulo": c.get("titulo", nome), "formato": c.get("formato", ""), "dia": str(dia), "tipo": "carrossel", "tema": tema,
                         "capa_modelo": modelo_capa, "capa_cena": c.get("capa_cena", ""), "slides": [x["tipo"] for x in slides], "paleta": c.get("paleta", "ouro")})
            criados += 1
        HIST.write_text(json.dumps(hist, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{criados} post(s) planejado(s)")
    Path(os.environ.get("GITHUB_OUTPUT", "/dev/null")).open("a").write(f"criados={criados}\n")


if __name__ == "__main__":
    main()
