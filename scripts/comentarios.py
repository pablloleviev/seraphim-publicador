"""
Resposta automática por palavra-chave nos comentários do Instagram.

Quem comenta a palavra-chave de um post recebe:
  1. uma mensagem no direct (Private Reply oficial do Instagram, até 7 dias após o comentário) com o link do material;
  2. uma resposta pública no comentário ("Te mandei no direct! 📩").
Cada pessoa recebe uma vez por post.

A palavra-chave e o material ficam no item.json do post na fila:
    "palavra_chave": "CHECKLIST",
    "material_url": "https://pablloleviev.github.io/seraphim-publicador/m/checklist-orcamento/",
    "material_titulo": "Checklist do orçamento que não se perde"

Precisa do IG_TOKEN com as permissões instagram_business_manage_comments e instagram_business_manage_messages.
Chamado pelo loop do publicar.py (verificar(estado)) a cada ~1 minuto.
"""
import json, os, random, re, time, unicodedata, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FILA = RAIZ / "fila"
GRAPH = "https://graph.instagram.com/v21.0"
TOKEN = os.environ.get("IG_TOKEN", "")
JANELA_DIAS = 7

_pausa_ate = 0.0   # depois de erro de permissão, espera antes de tentar de novo
_avisado = False


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9 ]+", " ", s)


def tem_palavra(texto: str, palavra: str) -> bool:
    return re.search(rf"\b{re.escape(_norm(palavra).strip())}\b", _norm(texto)) is not None


def _req(metodo, caminho, dados=None, json_body=None):
    url = f"{GRAPH}/{caminho}"
    if metodo == "GET":
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode({"access_token": TOKEN})
        req = urllib.request.Request(url)
    elif json_body is not None:
        req = urllib.request.Request(url, data=json.dumps(json_body).encode(), method="POST",
                                     headers={"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"})
    else:
        corpo = urllib.parse.urlencode({**(dados or {}), "access_token": TOKEN}).encode()
        req = urllib.request.Request(url, data=corpo, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.read().decode()[:300]}")


def posts_ativos(estado: dict):
    """Posts publicados nos últimos 7 dias que têm palavra-chave."""
    limite = datetime.now(timezone.utc) - timedelta(days=JANELA_DIAS)
    for nome, item in estado.get("itens", {}).items():
        if item.get("status") != "publicado" or not item.get("ig_id"):
            continue
        try:
            quando = datetime.fromisoformat(item.get("publicado_em", ""))
        except ValueError:
            continue
        if quando < limite:
            continue
        meta_arq = FILA / nome / "item.json"
        if not meta_arq.exists():
            continue
        meta = json.loads(meta_arq.read_text(encoding="utf-8"))
        if meta.get("palavra_chave") and meta.get("material_url"):
            yield nome, item, meta


DM = [
    "Oi, {u}! 👋 Aqui está o que você pediu: {titulo}\n\n👉 {url}\n\nSe curtir, segue a @seraphimtech_ que todo dia tem mais. 🚀",
    "Fala, {u}! Prometido é devido: {titulo} 📩\n\n👉 {url}\n\nE segue a @seraphimtech_ pra não perder os próximos. ✨",
]
PUBLICA = ["Te mandei no direct! 📩", "Enviado no seu direct! 🚀", "Chegou no direct, confere lá! 📩", "Mandei pra você no direct! ✨"]


def verificar(estado: dict, log=print):
    global _pausa_ate, _avisado
    if not TOKEN or time.time() < _pausa_ate:
        return
    feitos = estado.setdefault("respondidos", {})
    for nome, item, meta in posts_ativos(estado):
        try:
            r = _req("GET", f"{item['ig_id']}/comments?fields=id,text,username,timestamp&limit=50")
        except RuntimeError as e:
            if not _avisado:
                log(f"[comentários] sem acesso aos comentários ({e}). Precisa da chave com permissão de comentários e mensagens.")
                _avisado = True
            _pausa_ate = time.time() + 1800
            return
        for c in r.get("data", []):
            chave = f"{item['ig_id']}:{c.get('username') or c['id']}"
            if chave in feitos or c["id"] in feitos.values() or c.get("username") == "seraphimtech_":
                continue
            if not tem_palavra(c.get("text", ""), meta["palavra_chave"]):
                continue
            try:
                quando = datetime.fromisoformat(c["timestamp"].replace("+0000", "+00:00"))
                if quando < datetime.now(timezone.utc) - timedelta(days=JANELA_DIAS):
                    feitos[chave] = c["id"]; continue
            except Exception:
                pass
            u = c.get("username") or "tudo bem"
            texto = random.choice(DM).format(u=u, titulo=meta.get("material_titulo", "o material"), url=meta["material_url"])
            try:
                _req("POST", "me/messages", json_body={"recipient": {"comment_id": c["id"]}, "message": {"text": texto}})
                try:
                    _req("POST", f"{c['id']}/replies", {"message": random.choice(PUBLICA)})
                except RuntimeError as e:
                    log(f"[comentários] direct enviado, mas a resposta pública falhou: {e}")
                feitos[chave] = c["id"]
                log(f"[comentários] {nome}: material enviado para @{u}")
            except RuntimeError as e:
                log(f"[comentários] falhou ao mandar direct para @{u}: {e}")
                if " 10 " in f" {e} " or "permission" in str(e).lower() or "(#200)" in str(e):
                    _pausa_ate = time.time() + 1800
                    return
