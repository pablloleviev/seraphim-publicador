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
    item = {"status": "aguardando", "enviado_em": datetime.now(timezone.utc).isoformat()}
    redes = "Instagram"
    if meta["tipo"] == "reels":
        try:
            import tiktok
            if tiktok.conectado():
                info = tiktok.criador()
                item["tiktok"] = {"opcoes": info.get("privacy_level_options") or list(tiktok.NOMES_PRIV),
                                  "info": {k: info.get(k) for k in ("creator_nickname", "creator_username")}}
                redes = "Instagram + TikTok"
        except Exception as e:
            print(f"[aviso] TikTok indisponível: {e}")
    texto = (f"📌 *{nome}*\nTipo: {meta['tipo']}  •  Vai para: *{redes}*\n\n{meta.get('legenda','')[:800]}\n\n"
             + (f"⚠️ Não feito automaticamente: {meta['nota']}\n\n" if meta.get("nota") else ""))
    if item.get("tiktok"):
        i = item["tiktok"]["info"]
        texto += (f"🎵 TikTok: *{i.get('creator_nickname')}* (@{i.get('creator_username')})\n"
                  f"Escolha quem pode ver no TikTok e toque em ✅ Publicar.\n"
                  f"_Ao publicar, você concorda com a Confirmação de Uso de Música do TikTok._")
    else:
        texto += "Publicar?"
    msg = tg("sendMessage", chat_id=CHAT, text=texto, parse_mode="Markdown", disable_web_page_preview="true",
             reply_markup=teclado(nome, item))
    item["msg_id"] = msg["result"]["message_id"]
    estado["itens"][nome] = item


def teclado(nome, item):
    linhas = []
    tt = item.get("tiktok")
    if tt:
        priv = [{"text": ("✔️ " if tt.get("priv") == o else "") + tiktok_nome(o), "callback_data": f"ttp:{o}|{nome}"}
                for o in tt["opcoes"]]
        linhas += [priv[i:i + 3] for i in range(0, len(priv), 3)]
        chave = lambda k, rot: {"text": ("☑️ " if tt.get(k, True) else "⬜ ") + rot, "callback_data": f"ttt:{k}|{nome}"}
        linhas.append([chave("com", "Comentários"), chave("due", "Dueto"), chave("cos", "Costura")])
    linhas.append([{"text": "✅ Publicar", "callback_data": f"ok|{nome}"},
                   {"text": "❌ Pular", "callback_data": f"no|{nome}"}])
    return {"inline_keyboard": linhas}


# ---------- TikTok (tela exigida pelas regras do TikTok) ----------
def _teclado_tiktok(nome, tt, opcoes):
    linha_priv = [{"text": ("✔️ " if tt.get("priv") == o else "") + tiktok_nome(o), "callback_data": f"ttp:{o}|{nome}"}
                  for o in opcoes]
    chave = lambda k, rot: {"text": ("☑️ " if tt.get(k, True) else "⬜ ") + rot, "callback_data": f"ttt:{k}|{nome}"}
    botoes = [linha_priv[i:i + 2] for i in range(0, len(linha_priv), 2)]
    botoes.append([chave("com", "Comentários"), chave("due", "Dueto"), chave("cos", "Costura")])
    botoes.append([{"text": "🎵 Postar no TikTok", "callback_data": f"ttgo|{nome}"},
                   {"text": "Não postar", "callback_data": f"ttno|{nome}"}])
    return {"inline_keyboard": botoes}


def tiktok_nome(o):
    import tiktok
    return tiktok.NOMES_PRIV.get(o, o)


def _texto_tiktok(nome, meta, info, tt):
    return (f"🎵 *TikTok — {nome}*\n"
            f"Conta: *{info.get('creator_nickname', '?')}* (@{info.get('creator_username', '?')})\n\n"
            f"Legenda: {meta.get('legenda', '')[:300] or '(sem legenda)'}\n\n"
            f"1️⃣ Escolha quem pode ver (obrigatório)\n2️⃣ Ajuste comentários / dueto / costura\n\n"
            f"_Ao postar, você concorda com a Confirmação de Uso de Música do TikTok "
            f"(https://www.tiktok.com/legal/page/global/music-usage-confirmation/en)._")


def tela_tiktok(nome, meta, item):
    import tiktok
    info = tiktok.criador()
    opcoes = info.get("privacy_level_options") or list(tiktok.NOMES_PRIV)
    item["tiktok"] = {"opcoes": opcoes, "info": {k: info.get(k) for k in ("creator_nickname", "creator_username")}}
    msg = tg("sendMessage", chat_id=CHAT, text=_texto_tiktok(nome, meta, info, item["tiktok"]), parse_mode="Markdown",
             disable_web_page_preview="true", reply_markup=_teclado_tiktok(nome, item["tiktok"], opcoes))
    item["tiktok"]["msg_id"] = msg["result"]["message_id"]


def tratar_tiktok(acao, nome, estado):
    import tiktok
    item = estado["itens"].get(nome) or {}
    tt = item.get("tiktok")
    if not tt or tt.get("feito"):
        return
    pasta = FILA / nome
    meta = json.loads((pasta / "item.json").read_text(encoding="utf-8"))
    if acao.startswith("ttp:"):
        tt["priv"] = acao[4:]
    elif acao.startswith("ttt:"):
        k = acao[4:]; tt[k] = not tt.get(k, True)
    elif acao == "ttno":
        tt["feito"] = "pulado"
        tg("editMessageReplyMarkup", chat_id=CHAT, message_id=tt["msg_id"], reply_markup={"inline_keyboard": []})
        tg("sendMessage", chat_id=CHAT, text=f"TikTok: {nome} não será postado."); return
    elif acao == "ttgo":
        if not tt.get("priv"):
            tg("sendMessage", chat_id=CHAT, text="⚠️ Escolha primeiro quem pode ver o vídeo no TikTok."); return
        tg("editMessageReplyMarkup", chat_id=CHAT, message_id=tt["msg_id"], reply_markup={"inline_keyboard": []})
        try:
            tt["id"] = tiktok.publicar(pasta / "video.mp4", meta.get("legenda", ""), tt["priv"],
                                       tt.get("com", True), tt.get("due", True), tt.get("cos", True))
            tt["feito"] = tiktok.MODO
            tg("sendMessage", chat_id=CHAT, text=(
                f"🎵 {nome} foi para os RASCUNHOS do TikTok (app ainda em auditoria). Abra o app e toque em Publicar."
                if tiktok.MODO == "rascunho" else
                f"🎵 {nome} enviado ao TikTok! Pode levar alguns minutos para aparecer no seu perfil."))
        except Exception as e:
            tg("sendMessage", chat_id=CHAT, text=f"⚠️ TikTok falhou para {nome}: {str(e)[:300]}")
        return
    info = tt.get("info", {})
    tg("editMessageReplyMarkup", chat_id=CHAT, message_id=tt["msg_id"],
       reply_markup=_teclado_tiktok(nome, tt, tt.get("opcoes", [])))


def tiktok_pendente(estado):
    return False  # tela única: não precisa mais ficar ouvindo


def processar_respostas(estado: dict, espera: int = 0):
    r = tg("getUpdates", offset=estado.get("telegram_offset", 0) + 1, timeout=espera,
           allowed_updates=["callback_query", "message"])
    for up in r.get("result", []):
        estado["telegram_offset"] = up["update_id"]
        if "message" in up and not CHAT:
            print("CHAT_ID encontrado:", up["message"]["chat"]["id"])
        cq = up.get("callback_query")
        if not cq or str(cq["message"]["chat"]["id"]) != str(CHAT):
            continue
        acao, nome = cq["data"].split("|", 1)
        if acao.startswith("tt"):
            item = estado["itens"].get(nome) or {}
            tt = item.get("tiktok")
            if tt and item.get("status") == "aguardando":
                if acao.startswith("ttp:"):
                    tt["priv"] = acao[4:]
                elif acao.startswith("ttt:"):
                    tt[acao[4:]] = not tt.get(acao[4:], True)
                responder(cq["id"], "Ok")
                try:
                    tg("editMessageReplyMarkup", chat_id=CHAT, message_id=item["msg_id"], reply_markup=teclado(nome, item))
                except Exception:
                    pass
            else:
                responder(cq["id"], "Esse post já foi resolvido.")
            continue
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
        tt = item.get("tiktok")
        if tt and not tt.get("priv"):
            responder(cq["id"], "Escolha primeiro quem pode ver no TikTok")
            tg("sendMessage", chat_id=CHAT, text="⚠️ Escolha quem pode ver no TikTok (🌍 / 👥 / 🔒) e toque em ✅ de novo.")
            continue
        responder(cq["id"], "Publicando...")
        tg("sendMessage", chat_id=CHAT, text=f"⏳ Publicando {nome}...")
        try:
            meta = json.loads((pasta / "item.json").read_text(encoding="utf-8"))
            pid = publicar_instagram(pasta, meta)
            item.update(status="publicado", ig_id=pid, publicado_em=datetime.now(timezone.utc).isoformat())
            if meta["tipo"] == "reels":
                if tt:
                    try:
                        import tiktok
                        tt["id"] = tiktok.publicar(pasta / "video.mp4", meta.get("legenda", ""), tt["priv"],
                                                   tt.get("com", True), tt.get("due", True), tt.get("cos", True))
                        tt["feito"] = tiktok.MODO
                    except Exception as e:
                        tt["erro"] = str(e)[:300]
            try:
                tg("editMessageReplyMarkup", chat_id=CHAT, message_id=item["msg_id"], reply_markup={"inline_keyboard": []})
            except Exception:
                pass
            res = f"✅ {nome}\n• Instagram: publicado"
            if tt:
                res += ("\n• TikTok: " + ("está na caixa de entrada do app — abra o TikTok e toque em Publicar (até a auditoria ser aprovada)"
                        if tt.get("feito") == "rascunho" else "publicado" if tt.get("feito") else f"falhou ({tt.get('erro')})"))
            tg("sendMessage", chat_id=CHAT, text=res)
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
    # fica ligado ~50 min ouvindo o Telegram (resposta quase instantânea aos botões)
    # e mandando os posts que vencerem; o agendamento de hora em hora emenda o próximo ciclo
    fim = time.time() + int(os.environ.get("MINUTOS_OUVINDO", "50")) * 60
    ultimo_pull = time.time()
    while True:
        processar_respostas(estado, espera=0 if time.time() >= fim else 25)
        if os.environ.get("GITHUB_ACTIONS") and time.time() - ultimo_pull > 120:
            # puxa vídeos/carrosséis novos que entraram na fila enquanto este ciclo está ligado
            salvar_estado(estado)
            import subprocess
            subprocess.run("git pull -q --rebase --autostash", shell=True, cwd=RAIZ)
            ultimo_pull = time.time()
        agora = datetime.now(timezone.utc)
        for pasta, meta in itens_da_fila():
            if pasta.name in estado["itens"]:
                continue
            if datetime.fromisoformat(meta["quando"]) <= agora:
                try:
                    enviar_para_aprovacao(pasta, meta, estado)
                except Exception as e:
                    print(f"[erro] não consegui enviar {pasta.name}: {e}")
        salvar_estado(estado)
        if time.time() >= fim:
            break


if __name__ == "__main__":
    main()
