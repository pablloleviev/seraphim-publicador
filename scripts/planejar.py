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
import asyncio, json, os, re, sys, unicodedata, urllib.error, urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
BRT = timezone(timedelta(hours=-3))
CFG = json.loads((RAIZ / "planejamento.json").read_text(encoding="utf-8"))
HIST = RAIZ / "historico.json"
HT = "#inteligenciaartificial #automacao #tecnologia #startup #seraphimtech"
TEMAS = ["noir", "editorial", "terminal", "meianoite", "brutal", "vinho", "eletrico", "grafite", "ultravioleta"]


def proximo_tema(hist):
    """Tema usado há mais tempo: posts vizinhos no feed nunca ficam com a mesma cara."""
    ult = {}
    for i, h in enumerate(hist):
        if h.get("tema"):
            ult[h["tema"]] = i
    return min(TEMAS, key=lambda t: (ult.get(t, -1), TEMAS.index(t)))


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
    "nome": "concorrente-ja-usa-ia", "formato": "erro que você comete", "funil": "topo", "titulo": "Seu concorrente já usa IA",
    "cenas": [
        {"tipo": "palavra", "texto": "SEU|CONCORRENTE|JÁ USA|IA", "destaque": "IA", "narracao": "Seu concorrente já usa inteligência artificial."},
        {"tipo": "frase", "texto": "e você ainda faz tudo na mão", "destaque": "mão", "narracao": "E você ainda faz tudo na mão."},
        {"tipo": "contador", "rotulo": "Horas perdidas por mês", "de": 0, "para": 87, "sufixo": "h",
         "narracao": "Só respondendo mensagem, montando orçamento e conferindo planilha, vão quase noventa horas por mês."},
        {"tipo": "foto", "busca": "tired businessman office night", "texto": "90 horas", "sub": "por mês", "tom": "vermelho", "narracao": "Noventa horas. Todo mês."},
        {"tipo": "pergunta", "texto": "tá, mas automatizar não é *caro*?", "pose": "pensando", "narracao": "Tá, mas automatizar não é caro?"},
        {"tipo": "digitando", "topo": "PONTO 1:", "texto": "WHATSAPP", "narracao": "Ponto um: o WhatsApp responde sozinho as perguntas de sempre."},
        {"tipo": "diagrama", "passos": [{"icone": "chat", "rotulo": "cliente"}, {"icone": "robo", "rotulo": "automação"}, {"icone": "dinheiro", "rotulo": "venda"}],
         "narracao": "O cliente pergunta, a automação responde, e a venda acontece, até de madrugada."},
        {"tipo": "cards", "itens": [{"rotulo": "antes:", "busca": "messy desk papers"}, {"rotulo": "depois:", "busca": "clean modern office laptop"}],
         "narracao": "Antes, papel e correria. Depois, tudo organizado num sistema."},
        {"tipo": "niveis", "texto": "Onde você está?", "itens": ["Faz na mão", "Usa planilha", "Automatizou"], "narracao": "E aí, em qual nível a sua empresa está hoje?"},
        {"tipo": "cta", "texto": "SEGUE PRA NÃO *FICAR PRA TRÁS*", "pose": "confiante",
         "narracao": "Seu concorrente já começou. Segue a Seraphim pra não ficar pra trás."}],
    "legenda": "Seu concorrente já automatizou. E você? 👀"}

CATALOGO_CENAS = """Tipos de cena do motor de cortes (vertical). Reveze: NUNCA o mesmo tipo duas vezes seguidas; use 7 a 10 cenas; cada cena 1 ideia, 1 a 3 s de fala.
- palavra: palavras gigantes, uma por vez, no branco. "texto" com palavras/expressões separadas por | (máx. 4 blocos curtos), "destaque" = bloco em vermelho. Ótimo para o gancho.
- frase: frase curta minúscula no preto (até ~8 palavras). "destaque" = palavra dourada.
- contador: card de app em 3D com número contando. "rotulo", "de", "para", "sufixo" (ex.: "h", "%", " clientes"), opcional "riscar" (texto que aparece após riscar). Só números ilustrativos coerentes, nunca estatística inventada como fato.
- foto: foto real tratada com texto grande. "busca" (inglês, 2 a 5 palavras, SEM pessoas famosas/marcas), "texto", "sub", "tom": cinza|vermelho|dourado.
- pergunta: pergunta em letra de máquina no branco com o mascote; marque a palavra-chave com *asteriscos*; "pose".
- digitando: "topo" (ex.: "PONTO 1:", "ERRO 2:") e "texto" CURTO (1 a 3 palavras, máx. 18 letras) em MAIÚSCULAS sendo digitado.
- diagrama: 3 a 4 "passos" {icone, rotulo}; icones: tela pessoas dinheiro robo grafico chat engrenagem raio relogio cadeado carrinho planilha check alerta.
- cards: 2 cards de foto com rótulo ("antes:"/"depois:", "errado:"/"certo:"): "itens":[{"rotulo","busca"}].
- parede: parede 3D de imagens com o mascote no centro. "buscas": 2 a 3 termos em inglês, "texto" curto opcional.
- sera: mascote em fundo cinza de retícula, "pose", "texto" curto minúsculo opcional.
- painel: HUD de jogo (alerta + barra). "rotulo" (ex.: "Produtividade"), "valor" (0-100), "texto" curto.
- niveis: 3 níveis em cards. "texto" (título curto), "itens": 3 textos curtos.
- serifa: frase séria em serifa itálica (momento de verdade). "texto" ou "itens" (2-3 frases curtas).
- cta: SEMPRE a última cena. "texto" curto em MAIÚSCULAS com *destaque*, "pose"; nos posts de fundo, "apoio": "link na bio".
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

EXEMPLO_CARROSSEL = {
    "nome": "5-usos-ia", "formato": "lista prática", "titulo": "5 usos de IA que economizam horas",
    "slides": [
        {"tipo": "capa", "tag": "Inteligência artificial", "titulo": "5 usos de IA que|*economizam horas*", "texto": "Na sua empresa, a partir de hoje.", "sera": "surpreso"},
        {"tipo": "numero", "numero": "01", "titulo": "Responder|*mensagens*", "texto": "Rascunhos de resposta para clientes em **segundos**."},
        {"tipo": "texto", "titulo": "O segredo:|*contexto*", "texto": "Quanto mais detalhe você der, **melhor a resposta**.", "card": "Ex.: \"Responda como dono de loja, tom educado, 3 linhas.\""},
        {"tipo": "capa", "titulo": "Salva e|*testa hoje*", "texto": "Segue a **@seraphimtech_** para mais.", "sera": "confiante"}],
    "legenda": "5 usos de IA que economizam horas ⏱️\n\nSalva pra testar 📌"}


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
    if "#seraphimtech" not in hs:
        hs.append("#seraphimtech")
    out = []
    for h in hs:
        if h not in out and len(h) > 2:
            out.append(h)
    return " ".join(out[:n - 1] + (["#seraphimtech"] if "#seraphimtech" not in out[:n - 1] else []))


def funis_do_dia(hist, n):
    k = sum(1 for h in hist if h.get("tipo") == "video" and h.get("funil"))
    return [PADRAO_FUNIL[(k + i) % len(PADRAO_FUNIL)] for i in range(n)]


def pedir_dia(dia, n_v, n_c, hist):
    funis = funis_do_dia(hist, n_v)
    ideias = pesquisar_ideias(dia)
    usados = [h["titulo"] for h in hist][-300:]
    formatos_recentes = [h.get("formato", "") for h in hist][-12:]
    regras = f"""Você é o roteirista-chefe da Seraphim (@seraphimtech_), startup brasileira de tecnologia:
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
- Uma ideia por cena. Exemplos concretos do dia a dia de pequenos negócios (loja, clínica, salão, oficina, restaurante, escritório, e-commerce).
- Vídeo: narração total entre 70 e 110 palavras, frases curtas e naturais para ser falada em voz alta.
- PROIBIDO inventar estatística: nada de "80% das pessoas", "5 vezes mais", "30% da margem". Fale de forma qualitativa ("a maioria", "bem mais barato")
  ou em hipótese clara ("imagina perder 10 clientes por mês"). No "contador", o número é um EXEMPLO e o rótulo começa com "Ex.:".
- Nada de nomes de empresas/pessoas reais como clientes.
{CATALOGO_CENAS}
{REGRAS_FUNIL}
FICHA DO AUTOFLOW:
{FICHA_AUTOFLOW}
- Carrossel (estilo de carrossel viral): capa com manchete forte = número + ferramenta/assunto conhecido + promessa ou segredo (ex.: "5 comandos pra fazer o ChatGPT trabalhar na sua empresa", "3 erros que fazem seu cliente sumir"); a capa promete exatamente a quantidade de itens do miolo; miolo com 1 item por slide (título curto + explicação ou comando pronto pra copiar); último slide = chamada (seguir/salvar). Carrossel: 6 a 9 slides; tipos capa, numero, texto (pode ter "card"); primeiro e último são "capa"; títulos usam | para quebrar linha.
- Legenda (Instagram): ÚNICA para cada post, ligada ao gancho e ao assunto; 2 a 4 linhas curtas com emoji, uma pergunta que puxa comentário e a chamada do funil; SEM hashtags dentro dela.
- "legenda_tiktok": legenda própria para o TikTok (mais curta e direta, 1 a 2 linhas, tom de conversa), diferente da do Instagram.
- "hashtags": 8 a 12 hashtags relevantes para AQUELE post (misture 3 amplas, 5 do nicho/assunto e 2 de público, ex.: #inteligenciaartificial #chatgpt #pequenasempresas #empreendedorismo #automacao), sempre incluindo #seraphimtech; nunca #seraphimpublicador.
- "nome": slug curto em minúsculas com hífens, único.

MANUAL DE EDIÇÃO DOS CORTES (estilo e ritmo; para os campos de cena, siga o catálogo acima):
{(RAIZ / "estilos" / "cortes.md").read_text(encoding="utf-8")}

MANUAL DOS CARROSSÉIS (siga à risca nos carrosséis):
{(RAIZ / "estilos" / "carrosseis.md").read_text(encoding="utf-8")}

Responda SÓ um JSON: {{"videos": [...{n_v} itens], "carrosseis": [...{n_c} itens]}}
Exemplo de vídeo: {json.dumps(EXEMPLO_VIDEO, ensure_ascii=False)}
Exemplo de carrossel: {json.dumps(EXEMPLO_CARROSSEL, ensure_ascii=False)}"""
    rascunho = gemini(regras, 1.0)
    revisao = f"""Você é o diretor criativo exigente da Seraphim. Abaixo está o rascunho do conteúdo do dia.
Revise CADA post com olhar crítico e devolva a versão MELHORADA no mesmo formato JSON:
- corrija ortografia, palavras repetidas e frases estranhas (leia em voz alta mentalmente);
- troque ganchos fracos por ganchos que prendem; corte palavras inúteis; deixe a narração natural, falada;
- garanta que nenhum post se pareça com outro do dia nem com estes temas já usados: {json.dumps(usados[-80:], ensure_ascii=False)};
- confira todas as regras: tipos de cena válidos e sem repetir em sequência, 7-10 cenas, 70-110 palavras de narração, pontuação colada;
- A CHAMADA FINAL é a parte mais importante: confira se ela combina com o gancho e o assunto, se o funil está certo (oficina -> pode ser fundo; gestão -> meio; resto -> topo), se não tem frase sem sentido, e reescreva se estiver genérica;
- remova QUALQUER estatística inventada e qualquer afirmação sobre o AutoFlow que não esteja na ficha;
- nos posts de meio, confira se o material é útil, coerente com o vídeo e se a palavra-chave aparece na cta e na legenda;
- mantenha exatamente {n_v} vídeos e {n_c} carrosséis.
Regras completas originais, para referência:
{regras}

RASCUNHO:
{json.dumps(rascunho, ensure_ascii=False)}"""
    try:
        return gemini(revisao, 0.6)
    except Exception as e:
        print(f"[aviso] revisão falhou ({e}); usando rascunho")
        return rascunho


def limpar_linhas(ls):
    return [re.sub(r"\s+([?!.,:;])", r"\1", str(l)).upper().replace("*", "*") for l in ls][:3]


TIPOS = {"palavra", "frase", "contador", "foto", "pergunta", "digitando", "diagrama", "cards", "parede", "sera", "painel", "niveis", "serifa", "cta"}


def validar_video(v):
    cenas = []
    for c in v.get("cenas", []):
        if c.get("tipo") not in TIPOS or not str(c.get("narracao", "")).strip():
            continue
        for k in ("texto", "topo", "sub"):
            if isinstance(c.get(k), str):
                c[k] = re.sub(r"\s+([?!.,:;])", r"\1", c[k]).strip()
        if c.get("pose") and c["pose"] not in POSES:
            c["pose"] = "pensando"
        if c["tipo"] == "diagrama" and not c.get("passos"):
            c["tipo"] = "frase"
        if c["tipo"] in ("niveis", "cards") and not c.get("itens"):
            c["tipo"] = "frase"
        if c["tipo"] == "digitando" and len(str(c.get("texto", ""))) > 22:
            c["tipo"] = "frase"
        if cenas and cenas[-1]["tipo"] == c["tipo"] and c["tipo"] != "cta":
            c["tipo"] = "frase" if c["tipo"] != "frase" else "serifa"
        cenas.append(c)
    if not cenas or cenas[-1]["tipo"] != "cta":
        raise ValueError("sem chamada final")
    if len(cenas) < 6:
        raise ValueError("roteiro curto demais")
    v["cenas"] = cenas
    if v.get("funil") not in ("topo", "meio", "fundo"):
        v["funil"] = "topo"
    if v["funil"] == "meio" and not (v.get("palavra_chave") and (v.get("material") or {}).get("itens")):
        raise ValueError("post de meio sem palavra-chave/material")
    if v["funil"] == "fundo":
        cenas[-1].setdefault("apoio", "link na bio")
    cenas[-1]["funil"] = v["funil"]
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
        spec = {"nome": nome, "arroba": "@seraphimtech_", "cenas": v["cenas"], "motor": "cortes", "amostra": True, "voz": "gemini",
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
            spec = {"nome": nome, "arroba": "@seraphimtech_", "quando": f"{dia} {hora}", "cenas": v["cenas"], "motor": "cortes",
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
            hist.append({"nome": nome, "funil": v["funil"], "titulo": v.get("titulo", nome), "formato": v.get("formato", ""), "dia": str(dia), "tipo": "video", "tema": tema})
            criados += 1
        for hora, c in zip(hc, plano.get("carrosseis", [])):
            slides = [s for s in c.get("slides", []) if s.get("titulo")]
            if len(slides) < 4:
                print("[aviso] carrossel descartado: poucos slides"); continue
            for s in slides:
                if s.get("sera") not in POSES:
                    s.pop("sera", None)
                s["titulo"] = re.sub(r"\s+([?!.,:;])", r"\1", s["titulo"])
            nome = slug(c.get("nome") or c.get("titulo", "carrossel"))
            while nome in nomes:
                nome += "-2"
            nomes.add(nome)
            destino = RAIZ / "fila" / f"{dia}_{hora.replace(':', '')}_{nome}"
            tema = "noir"  # temas pausados: Pabllo reprovou (2026-10-10)
            spec = {"nome": nome, "arroba": "@seraphimtech_", "slides": slides, "tema": tema}
            tmp = RAIZ / "pedidos" / f"_car_{nome}.json"
            tmp.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
            import carrossel
            from PIL import Image
            asyncio.run(carrossel.main(str(tmp), str(destino)))
            tmp.unlink()
            for png in sorted(destino.glob("slide-*.png")):
                Image.open(png).convert("RGB").save(png.with_suffix(".jpg"), quality=92); png.unlink()
            (destino / "item.json").write_text(json.dumps({
                "tipo": "carrossel", "legenda": c.get("legenda", "").strip() + "\n\n👉 Seraphim, link na bio.\n\n" + HT,
                "quando": f"{dia}T{hora}:00-03:00"}, ensure_ascii=False, indent=2), encoding="utf-8")
            # versão Canva (feita pela sessão agendada; esta versão em código fica de reserva)
            (RAIZ / "canva" / "pendentes").mkdir(parents=True, exist_ok=True)
            (RAIZ / "canva" / "pendentes" / f"{destino.name}.json").write_text(json.dumps({
                "destino": str(destino.relative_to(RAIZ)), "titulo": c.get("titulo", nome), "formato": c.get("formato", ""),
                "slides": slides, "legenda": c.get("legenda", "")}, ensure_ascii=False, indent=1), encoding="utf-8")
            hist.append({"nome": nome, "titulo": c.get("titulo", nome), "formato": c.get("formato", ""), "dia": str(dia), "tipo": "carrossel", "tema": tema})
            criados += 1
        HIST.write_text(json.dumps(hist, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{criados} post(s) planejado(s)")
    Path(os.environ.get("GITHUB_OUTPUT", "/dev/null")).open("a").write(f"criados={criados}\n")


if __name__ == "__main__":
    main()
