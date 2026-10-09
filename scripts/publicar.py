"""
Publicador da Seraphim — roda no GitHub Actions a cada 15 minutos.

1. Lê respostas do Telegram (botões ✅ Publicar / ❌ Pular).
   - ✅ -> publica no Instagram e marca como publicado.
   - ❌ -> marca como pulado.
2. Procura na pasta fila/ o próximo item cujo horário já chegou e que ainda
   não foi enviado, e manda para o Telegram com os botões de aprovação.

Cada item da fila é uma pasta: fila/<AAAA-MM-DD_HHMM>_<nome>/
    item.json     {"tipo": "carrossel" | "reels", "legenda": "...", "quando": "2026-10-10T18:00:00-03:00"}
    slide-01.jpg, slide-02.jpg ...   (carrossel, JPEG 1080x1350)
    video.mp4                         (reels)

Segredos (GitHub > Settings > Secrets and variables > Actions):
    TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, IG_USER_ID, IG_TOKEN
"""
import json, os, sys, time, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FILA = RAIZ / "fila"
ESTADO = RAIZ / "estado.json"
REPO = os.environ.get("GITHUB_REPOSITORY", "pablloleviev/seraphim-publicador")
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")
TG = os.environ.get("TELEGRAM_TOKEN", "")
CHAT = os.environ.get("TELEGRAM_CHAT_ID", "")
IG_USER = os.environ.get("IG_USER_ID", "") or "me"
IG_TOKEN = os.environ.get("IG_TOKEN", "")
GRAPH = "https://graph.instagram.com/v21.0"


# ---------- utilidades ----------
def http(url, dados=None, metodo=None):
    corpo = urllib.parse.urlencode(dados).encode() if dados is not None else None
    req = urllib.request.Request(url, data=corpo, method=metodo or ("POST" if corpo else "GET"))
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.read().decode()[:400]}")


def tg(metodo, **dados):
    for k, v in list(dados.items()):
        if isinstance(v, (dict, list)):
            dados[k] = json.dumps(v)
    return http(f"https://api.telegram.org/bot{TG}/{metodo}", dados)


def responder(cq_id, texto):
    try:
        tg("answerCallbackQuery", callback_query_id=cq_id, text=texto)
    except Exception:
        pass  # clique antigo (>15 min): o Telegram não aceita mais resposta, tudo bem


def tg_arquivo(metodo, campo, caminho: Path, **dados):
    """Envia arquivo direto (até 50 MB), sem depender do limite de 20 MB do envio por link."""
    import uuid
    b = uuid.uuid4().hex
    partes = []
    for k, v in dados.items():
        partes.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
    partes.append(f"--{b}\r\nContent-Disposition: form-data; name=\"{campo}\"; filename=\"{caminho.name}\"\r\n"
                  f"Content-Type: video/mp4\r\n\r\n".encode() + caminho.read_bytes() + b"\r\n")
    partes.append(f"--{b}--\r\n".encode())
    req = urllib.request.Request(f"https://api.telegram.org/bot{TG}/{metodo}", data=b"".join(partes),
                                 headers={"Content-Type": f"multipart/form-data; boundary={b}"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{e.code} {e.read().decode()[:300]}")


def url_publica(caminho: Path):
    rel = caminho.relative_to(RAIZ).as_posix()
    return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/{urllib.parse.quote(rel)}"


def carregar_estado():
    return json.loads(ESTADO.read_text(encoding="utf-8"))


def salvar_estado(e):
    ESTADO.write_text(json.dumps(e, ensure_ascii=False, indent=2), encoding="utf-8")


def itens_da_fila():
    for pasta in sorted(p for p in FILA.iterdir() if p.is_dir()):
        meta = pasta / "item.json"
        if meta.exists():
            yield pasta, json.loads(meta.read_text(encoding="utf-8"))


# ---------- Instagram ----------
def ig(endpoint, **dados):
    dados["access_token"] = IG_TOKEN
    return http(f"{GRAPH}/{endpoint}", dados)


def esperar_container(cid, limite=300):
    inicio = time.time()
    while time.time() - inicio < limite:
        st = http(f"{GRAPH}/{cid}?fields=status_code&access_token={IG_TOKEN}")
        if st.get("status_code") == "FINISHED":
            return
        if st.get("status_code") == "ERROR":
            raise RuntimeError(f"Instagram recusou a mídia: {st}")
        time.sleep(5)
    raise RuntimeError("Instagram demorou demais para processar a mídia")


def publicar_instagram(pasta: Path, meta: dict) -> str:
    legenda = meta.get("legenda", "")
    if meta["tipo"] == "reels":
        c = ig(f"{IG_USER}/media", media_type="REELS", video_url=url_publica(pasta / "video.mp4"),
               caption=legenda, share_to_feed="true")
        esperar_container(c["id"], 600)
        criacao = c["id"]
    else:
        slides = sorted(pasta.glob("slide-*.jpg"))
        if len(slides) == 1:
            c = ig(f"{IG_USER}/media", image_url=url_publica(slides[0]), caption=legenda)
            esperar_container(c["id"])
            criacao = c["id"]
        else:
            filhos = []
            for s in slides[:10]:
                f = ig(f"{IG_USER}/media", image_url=url_publica(s), is_carousel_item="true")
                filhos.append(f["id"])
            for f in filhos:
                esperar_container(f)
            c = ig(f"{IG_USER}/media", media_type="CAROUSEL", children=",".join(filhos), caption=legenda)
            esperar_container(c["id"])
            criacao = c["id"]
    pub = ig(f"{IG_USER}/media_publish", creation_id=criacao)
    return pub["id"]


# ---------- Telegram ----------
def enviar_para_aprovacao(pasta: Path, meta: dict, estado: dict):
    nome = pasta.name
    if meta["tipo"] == "reels":
        tg_arquivo("sendVideo", "video", pasta / "video.mp4", chat_id=CHAT, supports_streaming="true")
    else:
        slides = sorted(pasta.glob("slide-*.jpg"))[:10]
        midia = [{"type": "photo", "media": url_publica(s)} for s in slides]
        tg("sendMediaGroup", chat_id=CHAT, media=midia)
    texto = (f"📌 *{nome}*\nTipo: {meta['tipo']}\n\n{meta.get('legenda','')[:800]}\n\n"
             + (f"⚠️ Não feito automaticamente: {meta['nota']}\n\n" if meta.get("nota") else "")
             + "Publicar no Instagram?")
    msg = tg("sendMessage", chat_id=CHAT, text=texto, parse_mode="Markdown",
             reply_markup={"inline_keyboard": [[
                 {"text": "✅ Publicar", "callback_data": f"ok|{nome}"},
                 {"text": "❌ Pular", "callback_data": f"no|{nome}"}]]})
    estado["itens"][nome] = {"status": "aguardando", "msg_id": msg["result"]["message_id"],
                             "enviado_em": datetime.now(timezone.utc).isoformat()}


def processar_respostas(estado: dict):
    r = tg("getUpdates", offset=estado.get("telegram_offset", 0) + 1, timeout=0,
           allowed_updates=["callback_query", "message"])
    for up in r.get("result", []):
        estado["telegram_offset"] = up["update_id"]
        if "message" in up and not CHAT:
            print("CHAT_ID encontrado:", up["message"]["chat"]["id"])
        cq = up.get("callback_query")
        if not cq or str(cq["message"]["chat"]["id"]) != str(CHAT):
            continue
        acao, nome = cq["data"].split("|", 1)
        item = estado["itens"].get(nome)
        if not item or item["status"] != "aguardando":
            responder(cq["id"], "Esse post já foi resolvido.")
            continue
        pasta = FILA / nome
        if acao == "no":
            item["status"] = "pulado"
            responder(cq["id"], "Pulado.")
            tg("editMessageReplyMarkup", chat_id=CHAT, message_id=item["msg_id"], reply_markup={"inline_keyboard": []})
            tg("sendMessage", chat_id=CHAT, text=f"❌ {nome} pulado.")
            continue
        responder(cq["id"], "Publicando...")
        tg("sendMessage", chat_id=CHAT, text=f"⏳ Publicando {nome} no Instagram...")
        try:
            meta = json.loads((pasta / "item.json").read_text(encoding="utf-8"))
            pid = publicar_instagram(pasta, meta)
            item.update(status="publicado", ig_id=pid, publicado_em=datetime.now(timezone.utc).isoformat())
            if meta["tipo"] == "reels":
                try:
                    import tiktok
                    if tiktok.conectado():
                        item["tiktok_id"] = tiktok.publicar(pasta / "video.mp4", meta.get("legenda", ""))
                        tg("sendMessage", chat_id=CHAT, text=f"🎵 {nome} enviado ao TikTok"
                           + (" (privado até a auditoria do TikTok)" if tiktok.PRIVACIDADE == "SELF_ONLY" else "") + ".")
                except Exception as e:
                    tg("sendMessage", chat_id=CHAT, text=f"⚠️ TikTok falhou para {nome}: {str(e)[:300]}")
            try:
                tg("editMessageReplyMarkup", chat_id=CHAT, message_id=item["msg_id"], reply_markup={"inline_keyboard": []})
            except Exception:
                pass
            tg("sendMessage", chat_id=CHAT, text=f"✅ {nome} publicado no Instagram!")
        except Exception as e:
            item["status"] = "aguardando"
            tg("sendMessage", chat_id=CHAT, text=f"⚠️ Erro ao publicar {nome}: {str(e)[:300]}\nToque em ✅ de novo para tentar outra vez.")


def main():
    if not TG:
        sys.exit("Falta o segredo TELEGRAM_TOKEN")
    estado = carregar_estado()
    eu = tg("getMe")["result"]
    print(f"Bot conectado: @{eu.get('username')}")
    if not CHAT:
        pend = tg("getUpdates", timeout=0).get("result", [])
        print(f"Mensagens pendentes no bot: {len(pend)}")
        for up in pend:
            m = up.get("message") or up.get("my_chat_member") or {}
            ch = m.get("chat", {})
            if ch:
                print(f"CHAT_ID encontrado: {ch.get('id')} ({ch.get('first_name', '')})")
        processar_respostas(estado)
        salvar_estado(estado)
        sys.exit("Falta TELEGRAM_CHAT_ID. Mande uma mensagem para o bot e veja o CHAT_ID acima no log.")
    processar_respostas(estado)
    agora = datetime.now(timezone.utc)
    for pasta, meta in itens_da_fila():
        if pasta.name in estado["itens"]:
            continue
        quando = datetime.fromisoformat(meta["quando"])
        if quando <= agora:
            try:
                enviar_para_aprovacao(pasta, meta, estado)
            except Exception as e:
                print(f"[erro] não consegui enviar {pasta.name}: {e}")
    salvar_estado(estado)


if __name__ == "__main__":
    main()
