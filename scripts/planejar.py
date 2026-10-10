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
    "nome": "mito-tecnologia-cara", "formato": "mito vs verdade",
    "titulo": "Tecnologia é cara?",
    "cenas": [
        {"modelo": "impacto", "linhas": ["TECNOLOGIA", "É *CARA*?"], "narracao": "Tecnologia é cara? Será mesmo?", "sera": "pensando"},
        {"modelo": "numero", "numero": "01", "linhas": ["CARO É", "*O RETRABALHO*"], "apoio": "todo dia, toda semana", "narracao": "Caro é o retrabalho, todo dia, toda semana."},
        {"modelo": "numero", "numero": "02", "linhas": ["CARO É", "*O CLIENTE PERDIDO*"], "apoio": "por demora ou esquecimento", "narracao": "Caro é o cliente perdido por demora ou esquecimento."},
        {"modelo": "lista", "linhas": ["UM SISTEMA"], "itens": ["Valida os dados", "Uma versão só", "Relatório automático"], "raios": True, "narracao": "Um sistema valida os dados, mantém uma versão só e gera o relatório sozinho."},
        {"modelo": "impacto", "linhas": ["TECNOLOGIA É", "*INVESTIMENTO*"], "narracao": "Tecnologia bem feita é investimento, não gasto.", "fundo": "branco"},
        {"modelo": "cta", "linhas": ["TECNOLOGIA QUE", "*TRABALHA* POR VOCÊ"], "apoio": "link na bio", "sera": "confiante", "narracao": "Seraphim: sistemas, automações e inteligência artificial para o seu negócio. Link na bio."}],
    "legenda": "Tecnologia é cara? Caro é ficar sem 💸\n\nConcorda? 👇"}

EXEMPLO_CARROSSEL = {
    "nome": "5-usos-ia", "formato": "lista prática", "titulo": "5 usos de IA que economizam horas",
    "slides": [
        {"tipo": "capa", "tag": "Inteligência artificial", "titulo": "5 usos de IA que|*economizam horas*", "texto": "Na sua empresa, a partir de hoje.", "sera": "surpreso"},
        {"tipo": "numero", "numero": "01", "titulo": "Responder|*mensagens*", "texto": "Rascunhos de resposta para clientes em **segundos**."},
        {"tipo": "texto", "titulo": "O segredo:|*contexto*", "texto": "Quanto mais detalhe você der, **melhor a resposta**.", "card": "Ex.: \"Responda como dono de loja, tom educado, 3 linhas.\""},
        {"tipo": "capa", "titulo": "Salva e|*testa hoje*", "texto": "Segue a **@seraphimtech_** para mais.", "sera": "confiante"}],
    "legenda": "5 usos de IA que economizam horas ⏱️\n\nSalva pra testar 📌"}


def pedir_dia(dia, n_v, n_c, hist):
    usados = [h["titulo"] for h in hist][-300:]
    formatos_recentes = [h.get("formato", "") for h in hist][-12:]
    regras = f"""Você é o roteirista-chefe da Seraphim (@seraphimtech_), startup brasileira de tecnologia:
sistemas sob medida, automações e inteligência artificial para pequenas e médias empresas.
Referências de linha editorial: perfis como os de startups de IA/automação, criadores de "IA para negócios",
SaaS de gestão. Público: donos de pequenos negócios e profissionais que querem usar tecnologia.

Crie o conteúdo do dia {dia:%d/%m/%Y} ({['segunda','terça','quarta','quinta','sexta','sábado','domingo'][dia.weekday()]}):
{n_v} roteiros de VÍDEO (Reels/TikTok vertical) e {n_c} CARROSSÉIS.

REGRAS DE QUALIDADE (obrigatórias):
- Cada post é sobre um tema DIFERENTE. NUNCA repita nem parafraseie estes temas já usados: {json.dumps(usados, ensure_ascii=False)}
- Formatos disponíveis (reveze; não repita formato no mesmo dia se possível; evite os recentes {formatos_recentes}):
  tutorial passo a passo, mito vs verdade, erro que você comete, antes e depois, lista prática, notícia/tendência de IA explicada,
  bastidores de startup, comparação (X vs Y), pergunta polêmica, história curta de cliente (genérica, sem nomes reais), checklist, "você sabia".
- Gancho forte na 1ª cena (pergunta, número ou contraste) — a pessoa decide em 1 segundo se fica.
- Uma ideia por cena. Exemplos concretos do dia a dia de pequenos negócios (loja, clínica, salão, oficina, restaurante, escritório, e-commerce).
- Vídeo: 5 a 7 cenas, narração total entre 55 e 95 palavras, frases curtas e naturais para ser falada em voz alta.
- "linhas": 1 a 3 linhas curtas EM MAIÚSCULAS (máx. ~16 caracteres cada); marque 1 destaque por cena com *asteriscos*.
- Pontuação colada na palavra ("BASTA?", nunca "BASTA ?").
- Varie o visual: use "fundo":"branco" em no máximo 1 cena por vídeo, "raios":true em no máximo 1, e poses do mascote "sera" variadas ({POSES}) em 1 a 2 cenas.
- Modelos de cena: impacto (linhas), numero (numero "01".., linhas, apoio curto), lista (linhas + 3 itens curtos), cta (última cena, sempre).
- A cena cta VARIA de post para post (seguir, salvar, comentar uma palavra, link na bio, mandar para alguém) e cita a Seraphim.
- Nada de promessas falsas, números inventados apresentados como estatística, nem nomes de empresas/pessoas reais como clientes.
- Carrossel: 6 a 9 slides; tipos capa, numero, texto (pode ter "card"); primeiro e último são "capa"; títulos usam | para quebrar linha.
- Legenda: 1 a 3 linhas com emoji, uma pergunta ou chamada, SEM hashtags (são adicionadas depois).
- "nome": slug curto em minúsculas com hífens, único.

MANUAL DE EDIÇÃO DOS CORTES (siga à risca nos vídeos):
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
- confira todas as regras: linhas curtas em maiúsculas com 1 *destaque*, pontuação colada, 5-7 cenas, cta final variado, 55-95 palavras de narração;
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


def validar_video(v):
    cenas = []
    for c in v.get("cenas", []):
        if c.get("modelo") not in MODELOS or not c.get("narracao"):
            continue
        c["linhas"] = limpar_linhas(c.get("linhas") or ["SERAPHIM"])
        if c.get("sera") not in POSES:
            c.pop("sera", None)
        if c["modelo"] == "lista" and not c.get("itens"):
            c["modelo"] = "impacto"
        cenas.append(c)
    if not cenas or cenas[-1]["modelo"] != "cta":
        cenas.append({"modelo": "cta", "linhas": ["TECNOLOGIA QUE", "*TRABALHA* POR VOCÊ"], "apoio": "link na bio",
                      "sera": "confiante", "narracao": "Seraphim: sistemas, automações e inteligência artificial para o seu negócio. Link na bio."})
    if len(cenas) < 4:
        raise ValueError("roteiro curto demais")
    v["cenas"] = cenas
    return v


def main():
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
            spec = {"nome": nome, "arroba": "@seraphimtech_", "quando": f"{dia} {hora}", "cenas": v["cenas"],
                    "genero_voz": "masculina" if criados % 3 else "feminina",
                    "legenda": (v.get("legenda", "").strip() + "\n\n👉 Seraphim, link na bio.\n\n" + HT)}
            (RAIZ / "pedidos" / f"{nome}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
            hist.append({"nome": nome, "titulo": v.get("titulo", nome), "formato": v.get("formato", ""), "dia": str(dia), "tipo": "video"})
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
            spec = {"nome": nome, "arroba": "@seraphimtech_", "slides": slides}
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
            hist.append({"nome": nome, "titulo": c.get("titulo", nome), "formato": c.get("formato", ""), "dia": str(dia), "tipo": "carrossel"})
            criados += 1
        HIST.write_text(json.dumps(hist, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{criados} post(s) planejado(s)")
    Path(os.environ.get("GITHUB_OUTPUT", "/dev/null")).open("a").write(f"criados={criados}\n")


if __name__ == "__main__":
    main()
