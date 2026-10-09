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
import json, os, random, re, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
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
            pedido["legenda"] = get(url_baixar(txt['id'])).decode("utf-8", "ignore")
        (RAIZ / "gravacoes" / f"{nome}.json").write_text(json.dumps(pedido, ensure_ascii=False, indent=2), encoding="utf-8")
        estado["vistos"].append(f["id"]); novos += 1
    ESTADO.write_text(json.dumps(estado, indent=2))
    print(f"{novos} vídeo(s) novo(s)")
    Path(os.environ.get("GITHUB_OUTPUT", "/dev/null")).open("a").write(f"novos={novos}\n")


if __name__ == "__main__":
    main()
