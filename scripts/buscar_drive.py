"""
Olha a pasta "Seraphim Gravações" do Google Drive e transforma cada vídeo novo
em um pedido para o processo cinematográfico (gravacoes/<nome>.json + .mp4).

Nome do arquivo = instruções (tudo opcional):
    garagem-escura - sinais.mp4          -> cenário "garagem-escura", nome "sinais"
    oficina-elevador - preco - 18h.mp4   -> agenda para as 18h do dia
    sinais.mp4                           -> cenário escolhido automaticamente
Um .txt com o mesmo nome (sinais.txt) vira a legenda do post.

Segredo: DRIVE_FOLDER_ID (pasta compartilhada como "qualquer pessoa com o link: leitor"). Sem chave de API.
"""
import json, os, random, re, sys, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
ESTADO = RAIZ / "estado_drive.json"
PASTA = os.environ.get("DRIVE_FOLDER_ID", "")
CHAVE = os.environ.get("GOOGLE_API_KEY", "")
BRT = timezone(timedelta(hours=-3))
API = "https://www.googleapis.com/drive/v3/files"


def get(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.read()


def listar():
    """Lê a página pública da pasta (sem chave de API)."""
    import html
    pag = get(f"https://drive.google.com/embeddedfolderview?id={PASTA}#list").decode("utf-8", "ignore")
    itens = re.findall(r'<div class="flip-entry" id="entry-([\w-]+)".*?<div class="flip-entry-title">(.*?)</div>', pag, re.S)
    out = []
    for i, (fid, nome) in enumerate(itens):
        nome = html.unescape(nome).strip()
        ext = Path(nome).suffix.lower()
        mime = "video/" if ext in (".mp4", ".mov", ".m4v", ".webm") else "text/" if ext == ".txt" else "outro"
        out.append({"id": fid, "name": nome, "mimeType": mime, "createdTime": f"{i:05d}"})
    return out


def url_baixar(fid):
    return f"https://drive.usercontent.google.com/download?id={fid}&export=download&confirm=t"


def baixar(fid, destino):
    req = urllib.request.Request(url_baixar(fid), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=600) as r, open(destino, "wb") as f:
        while bloco := r.read(1 << 20):
            f.write(bloco)


def interpretar(prompt, cenarios):
    """Transforma o pedido em texto livre do Pabllo em instruções (Gemini, grátis)."""
    chave = os.environ.get("GEMINI_API_KEY")
    if not chave:
        raise RuntimeError("sem GEMINI_API_KEY")
    instr = f"""Você é o editor de vídeos da Seraphim (software AutoFlow para oficinas mecânicas).
O dono gravou um vídeo e escreveu este pedido:
---
{prompt}
---
Responda SÓ um JSON com as chaves (todas opcionais, omita o que ele não pediu):
"cenario": um destes já prontos: {cenarios} — use SÓ se o lugar pedido for praticamente igual
"cenario_novo": se ele pediu outro lugar, descreva o cenário em inglês, detalhado (lugar, luz, clima, época), SEM pessoas
"titulo": lista de 1 a 3 linhas curtas EM MAIÚSCULAS para o topo; marque a palavra de destaque com *asteriscos*
"insercoes": lista de telas gráficas por cima, cada uma {{"inicio": seg, "fim": seg, "modelo": "numero"|"impacto"|"lista"|"cta", "numero": "01", "linhas": [...], "itens": [...], "apoio": "..."}}
"quando": "AAAA-MM-DD HH:MM" se ele pediu horário (hoje é {datetime.now(BRT):%Y-%m-%d})
"legenda": a legenda do post do Instagram (curta, com CTA e 3-5 hashtags), se ele pediu ou deu o texto
"pedidos_extras": texto com o que ele pediu e o sistema não faz sozinho (ex.: trocar roupa, adicionar relógio)"""
    corpo = json.dumps({"contents": [{"parts": [{"text": instr}]}],
                        "generationConfig": {"responseMimeType": "application/json"}}).encode()
    req = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
                                 data=corpo, headers={"x-goog-api-key": chave, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        txt = json.loads(r.read())["candidates"][0]["content"]["parts"][0]["text"]
    d = json.loads(txt)
    if d.get("cenario_novo"):
        import gerar_cenario
        try:
            d["cenario"] = str(gerar_cenario.gerar(d.pop("cenario_novo")).relative_to(RAIZ))
        except Exception as e:
            print(f"[aviso] cenário novo falhou: {e}"); d.pop("cenario", None)
    elif d.get("cenario") in cenarios:
        d["cenario"] = f"cenarios/{d['cenario']}.jpg"
    else:
        d.pop("cenario", None)
    print("Instruções entendidas:", json.dumps(d, ensure_ascii=False))
    return d


def slug(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-") or "video"


def main():
    if not PASTA:
        print("Falta DRIVE_FOLDER_ID")
        Path(os.environ.get("GITHUB_OUTPUT", "/dev/null")).open("a").write("novos=0\n"); return
    estado = json.loads(ESTADO.read_text()) if ESTADO.exists() else {"vistos": []}
    arquivos = listar()
    textos = {Path(f["name"]).stem: f for f in arquivos if f["name"].lower().endswith(".txt")}
    cenarios = sorted(p.stem for p in (RAIZ / "cenarios").glob("*.jpg"))
    novos = 0
    for f in sorted(arquivos, key=lambda x: x["createdTime"]):
        if f["id"] in estado["vistos"] or not f.get("mimeType", "").startswith("video/"):
            continue
        partes = [p.strip() for p in Path(f["name"]).stem.split(" - ")]
        cenario = partes[0] if partes[0] in cenarios else None
        resto = partes[1:] if cenario else partes
        hora = next((p for p in resto if re.fullmatch(r"\d{1,2}h(\d\d)?", p)), None)
        nome = slug(" ".join(p for p in resto if p != hora) or Path(f["name"]).stem)
        nome = f"{datetime.now(BRT):%m%d}-{nome}"
        mp4 = RAIZ / "gravacoes" / f"{nome}.mp4"
        mp4.parent.mkdir(exist_ok=True)
        print(f"Baixando {f['name']} -> {mp4.name}")
        baixar(f["id"], mp4)
        pedido = {"nome": nome, "video": f"gravacoes/{mp4.name}",
                  "cenario": f"cenarios/{cenario or random.choice(cenarios)}.jpg"}
        if hora:
            h, _, m = hora.partition("h")
            pedido["quando"] = datetime.now(BRT).strftime("%Y-%m-%d ") + f"{int(h):02d}:{int(m or 0):02d}"
        txt = textos.get(Path(f["name"]).stem)
        if txt:
            prompt = get(url_baixar(txt['id'])).decode("utf-8", "ignore").strip()
            try:
                pedido.update(interpretar(prompt, cenarios))
            except Exception as e:
                print(f"[aviso] não consegui interpretar o prompt ({e}); usando como legenda")
                pedido["legenda"] = prompt
        (RAIZ / "gravacoes" / f"{nome}.json").write_text(json.dumps(pedido, ensure_ascii=False, indent=2), encoding="utf-8")
        estado["vistos"].append(f["id"]); novos += 1
    ESTADO.write_text(json.dumps(estado, indent=2))
    print(f"{novos} vídeo(s) novo(s)")
    Path(os.environ.get("GITHUB_OUTPUT", "/dev/null")).open("a").write(f"novos={novos}\n")


if __name__ == "__main__":
    main()
