"""
Publicação no TikTok (Content Posting API, envio do arquivo).

Segredos: TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET
O token da conta fica em tiktok_token.enc, CRIPTOGRAFADO com uma chave derivada do
TIKTOK_CLIENT_SECRET (só o GitHub Actions consegue abrir). Ele se renova sozinho.

    python scripts/tiktok.py autorizar <code>     # 1ª vez (código vindo do login)
    python scripts/tiktok.py teste <video.mp4>    # posta um vídeo de teste
"""
import base64, hashlib, json, math, os, sys, time, urllib.parse, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARQ = RAIZ / "tiktok_token.enc"
KEY = os.environ.get("TIKTOK_CLIENT_KEY", "")
SECRET = os.environ.get("TIKTOK_CLIENT_SECRET", "")
REDIRECT = "https://github.com/pablloleviev/seraphim-publicador"
API = "https://open.tiktokapis.com"
# enquanto o app não passa na auditoria do TikTok, só é permitido postar como privado
PRIVACIDADE = os.environ.get("TIKTOK_PRIVACIDADE", "SELF_ONLY")


def _fernet():
    from cryptography.fernet import Fernet
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(("seraphim:" + SECRET).encode()).digest()))


def salvar(tok):
    tok["obtido_em"] = int(time.time())
    ARQ.write_bytes(_fernet().encrypt(json.dumps(tok).encode()))


def carregar():
    return json.loads(_fernet().decrypt(ARQ.read_bytes()))


def _post_form(url, dados):
    req = urllib.request.Request(url, data=urllib.parse.urlencode(dados).encode(),
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=60).read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.read().decode()[:300]}")


def autorizar(code):
    tok = _post_form(f"{API}/v2/oauth/token/", {"client_key": KEY, "client_secret": SECRET, "code": code,
                                                 "grant_type": "authorization_code", "redirect_uri": REDIRECT})
    if "access_token" not in tok:
        raise RuntimeError(f"TikTok recusou: {tok}")
    salvar(tok)
    print("TikTok conectado. Conta:", tok.get("open_id", "")[:6] + "…", "escopos:", tok.get("scope"))


def token():
    tok = carregar()
    if time.time() > tok["obtido_em"] + tok.get("expires_in", 86400) - 600:
        novo = _post_form(f"{API}/v2/oauth/token/", {"client_key": KEY, "client_secret": SECRET,
                                                      "grant_type": "refresh_token", "refresh_token": tok["refresh_token"]})
        if "access_token" not in novo:
            raise RuntimeError(f"não consegui renovar o token do TikTok: {novo}")
        salvar(novo); tok = novo
    return tok["access_token"]


def _json(url, corpo, at):
    req = urllib.request.Request(url, data=json.dumps(corpo).encode(),
                                 headers={"Authorization": f"Bearer {at}", "Content-Type": "application/json; charset=UTF-8"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=60).read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.read().decode()[:400]}")


def publicar(video: Path, legenda: str) -> str:
    at = token()
    tam = video.stat().st_size
    pedaco = tam if tam <= 64 * 1024 * 1024 else 10 * 1024 * 1024
    n = 1 if pedaco == tam else tam // pedaco
    init = _json(f"{API}/v2/post/publish/video/init/", {
        "post_info": {"title": legenda[:2200], "privacy_level": PRIVACIDADE,
                      "disable_duet": False, "disable_comment": False, "disable_stitch": False},
        "source_info": {"source": "FILE_UPLOAD", "video_size": tam, "chunk_size": pedaco, "total_chunk_count": n},
    }, at)
    if init.get("error", {}).get("code") not in (None, "ok"):
        raise RuntimeError(f"TikTok: {init['error']}")
    pub_id, url = init["data"]["publish_id"], init["data"]["upload_url"]
    with open(video, "rb") as f:
        for i in range(n):
            ini = i * pedaco
            fim = tam - 1 if i == n - 1 else ini + pedaco - 1
            f.seek(ini); dados = f.read(fim - ini + 1)
            req = urllib.request.Request(url, data=dados, method="PUT", headers={
                "Content-Type": "video/mp4", "Content-Length": str(len(dados)),
                "Content-Range": f"bytes {ini}-{fim}/{tam}"})
            urllib.request.urlopen(req, timeout=300).read()
    for _ in range(60):
        st = _json(f"{API}/v2/post/publish/status/fetch/", {"publish_id": pub_id}, at)
        s = st.get("data", {}).get("status")
        if s == "PUBLISH_COMPLETE":
            return pub_id
        if s == "FAILED":
            raise RuntimeError(f"TikTok recusou o vídeo: {st['data'].get('fail_reason')}")
        time.sleep(5)
    return pub_id  # ainda processando; o TikTok termina sozinho


def conectado():
    return bool(KEY and SECRET and ARQ.exists())


if __name__ == "__main__":
    if sys.argv[1] == "autorizar":
        autorizar(sys.argv[2])
    elif sys.argv[1] == "teste":
        print("publish_id:", publicar(Path(sys.argv[2]), "Teste Seraphim"))
