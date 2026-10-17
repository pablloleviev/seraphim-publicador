"""
Canva Connect API direto do GitHub (NÃO usa o Claude, não gasta tokens).
Segredos no GitHub: CANVA_CLIENT_ID, CANVA_CLIENT_SECRET, CANVA_REFRESH (renovado sozinho), GH_PAT (para salvar o refresh novo).
Uso:
  python scripts/canva_api.py conectar <code> <verifier>   -> troca o código do login pelo refresh e salva no GitHub
  python scripts/canva_api.py teste                          -> lista modelos (brand templates) e seus campos
  python scripts/canva_api.py preencher <template_id> <json_campos> <saida.png>
"""
import base64, json, os, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path

API = "https://api.canva.com/rest/v1"
CID = os.environ.get("CANVA_CLIENT_ID", "OC-AaFKcEUDqxNX")
CSEC = os.environ.get("CANVA_CLIENT_SECRET", "")
REDIRECT = "https://pablloleviev.github.io/seraphim-publicador/canva/"
_token = None


def _salvar_refresh(rt):
    """o Canva troca o refresh a cada uso: guarda o novo como segredo do GitHub (criptografado)"""
    env = dict(os.environ, GH_TOKEN=os.environ.get("GH_PAT", ""))
    r = subprocess.run(["gh", "secret", "set", "CANVA_REFRESH", "--body", rt, "--repo",
                        os.environ.get("GITHUB_REPOSITORY", "pablloleviev/seraphim-publicador")], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"não salvou o refresh no GitHub (GH_PAT sem permissão de Secrets: escrita?): {r.stderr[:300]}")
    print("refresh salvo no GitHub")


def _token_req(dados):
    basic = base64.b64encode(f"{CID}:{CSEC}".encode()).decode()
    req = urllib.request.Request(f"{API}/oauth/token", data=urllib.parse.urlencode(dados).encode(),
                                 headers={"Authorization": f"Basic {basic}", "Content-Type": "application/x-www-form-urlencoded"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=60).read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"token {e.code}: {e.read().decode()[:300]}")


def token():
    global _token
    if _token:
        return _token
    r = _token_req({"grant_type": "refresh_token", "refresh_token": os.environ["CANVA_REFRESH"]})
    _salvar_refresh(r["refresh_token"])
    _token = r["access_token"]
    return _token


def api(metodo, caminho, corpo=None):
    req = urllib.request.Request(f"{API}{caminho}", method=metodo, data=json.dumps(corpo).encode() if corpo is not None else None,
                                 headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=120).read() or b"{}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{metodo} {caminho} {e.code}: {e.read().decode()[:400]}")


def esperar(caminho, chave="job"):
    for _ in range(90):
        r = api("GET", caminho)[chave]
        if r["status"] == "success":
            return r
        if r["status"] == "failed":
            raise RuntimeError(f"falhou: {r}")
        time.sleep(2)
    raise RuntimeError("tempo esgotado")


def subir_imagem(caminho: Path, nome="img"):
    """envia uma imagem local para a biblioteca do Canva e devolve o asset_id"""
    meta = base64.b64encode(json.dumps({"name_base64": base64.b64encode(nome.encode()).decode()}).encode()).decode()
    req = urllib.request.Request(f"{API}/asset-uploads", method="POST", data=caminho.read_bytes(),
                                 headers={"Authorization": f"Bearer {token()}", "Content-Type": "application/octet-stream",
                                          "Asset-Upload-Metadata": json.dumps({"name_base64": base64.b64encode(nome.encode()).decode()})})
    job = json.loads(urllib.request.urlopen(req, timeout=120).read())["job"]
    return esperar(f"/asset-uploads/{job['id']}")["asset"]["id"]


def preencher(template_id, campos: dict, saida: Path, fmt="png"):
    """campos: {"titulo": "texto", "foto": Path(...)} -> design preenchido exportado em saida"""
    data = {}
    for k, v in campos.items():
        if isinstance(v, Path):
            data[k] = {"type": "image", "asset_id": subir_imagem(v, k)}
        else:
            data[k] = {"type": "text", "text": str(v)}
    job = api("POST", "/autofills", {"brand_template_id": template_id, "data": data})["job"]
    design_id = esperar(f"/autofills/{job['id']}")["result"]["design"]["id"]
    exp = api("POST", "/exports", {"design_id": design_id, "format": {"type": fmt}})["job"]
    urls = esperar(f"/exports/{exp['id']}")["urls"]
    saida.parent.mkdir(parents=True, exist_ok=True)
    arqs = []
    for i, u in enumerate(urls):
        d = saida if len(urls) == 1 else saida.with_name(f"{saida.stem}-{i + 1:02d}{saida.suffix}")
        d.write_bytes(urllib.request.urlopen(u, timeout=120).read()); arqs.append(d)
    return arqs


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "conectar":
        r = _token_req({"grant_type": "authorization_code", "code": a[1], "code_verifier": a[2], "redirect_uri": REDIRECT})
        _salvar_refresh(r["refresh_token"]); print("Canva conectado. Escopos:", r.get("scope"))
    elif a[0] == "teste":
        bts = api("GET", "/brand-templates?dataset=any").get("items", [])
        print(f"{len(bts)} modelos")
        for b in bts:
            ds = api("GET", f"/brand-templates/{b['id']}/dataset").get("dataset", {})
            print(b["id"], b.get("title"), list(ds))
    elif a[0] == "preencher":
        campos = {k: (Path(v[1:]) if str(v).startswith("@") else v) for k, v in json.loads(a[2]).items()}
        print(preencher(a[1], campos, Path(a[3])))
