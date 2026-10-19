"""Stories: aprovação INDIVIDUAL pelo Telegram (regra do Pabllo, 19/10/2026).

- Nenhum Story vai ao ar sem ✅ explícito naquela peça. Silêncio = não publica. Aprovar um não aprova outro.
- Story simples (sem adesivo): depois do ✅, a automação publica pela API no horário.
  Se o horário já passou quando o ✅ chega (ou na hora de publicar), pede NOVA confirmação ("publicar agora?").
- Story interativo (enquete, quiz, perguntas): NUNCA publica sozinho. Manda arte final + guia + texto exato do adesivo
  + instruções; o Pabllo publica no app. ✅ aqui significa só "aprovado, vou postar".
- ❌ = reprovado: fica parado aguardando ajuste (o plano pode ser refeito e reenviado).
Estado em estado.json -> "stories": {chave: {status, msg_id, ...}}
"""
import hashlib, json
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BRT = timezone(timedelta(hours=-3))
PLANO = RAIZ / "stories" / "plano.json"
ANTECEDENCIA = timedelta(hours=14)     # prévia chega até 14 h antes
TOLERANCIA = timedelta(minutes=30)     # passou disso do horário: pede nova confirmação


def _cod(chave):
    return "s" + hashlib.md5(chave.encode()).hexdigest()[:9]


def _lista():
    if not PLANO.exists():
        return []
    out = []
    for s in json.loads(PLANO.read_text(encoding="utf-8")).get("stories", []):
        chave = f'{s["dia"]}_{s["id"]}'
        quando = datetime.strptime(f'{s["dia"]} {s["hora"]}', "%Y-%m-%d %H:%M").replace(tzinfo=BRT)
        ades = str((s.get("interativo") or {}).get("adesivo", "nenhum"))
        auto = ades.startswith("nenhum") or ades.startswith("post do feed")
        img = RAIZ / "stories" / s["dia"] / f'{s["id"]}.jpg'
        out.append({"chave": chave, "quando": quando, "auto": auto, "img": img, "guia": img.with_name(f'{s["id"]}_guia.jpg'), "s": s})
    return out


def _n(chave):
    return chave.replace("_", " · ")


def _hora(q):
    return q.astimezone(BRT).strftime("%d/%m às %H:%M")


def _texto(st, nota=""):
    s = st["s"]; inter = s.get("interativo") or {}
    t = (f"📱 *STORY* — {_n(st['chave'])}\n🕗 Horário: *{_hora(st['quando'])}*\n🎯 Objetivo: {s.get('objetivo','')}\n")
    if st["auto"]:
        t += "\n⚙️ Story simples: se você aprovar, sai *sozinho* no horário.\n"
        if inter.get("como"):
            t += f"(Opcional, no app depois: {inter['como']})\n"
    else:
        t += (f"\n✋ *Interativo — você publica pelo app.*\nAdesivo: *{inter.get('adesivo')}*\n")
        if inter.get("pergunta"):
            t += f"Texto do adesivo: `{inter['pergunta']}`\n"
        if inter.get("texto"):
            t += f"Texto do adesivo: `{inter['texto']}`\n"
        for o in inter.get("opcoes", []):
            t += f"• `{o}`\n"
        t += ("\nComo publicar: 1) salve a arte (sem guia); 2) Instagram → Story → escolha a arte; "
              "3) toque no ícone de adesivos → adesivo acima; 4) cole os textos; 5) posicione no espaço tracejado (veja a 2ª imagem); 6) compartilhe.\n")
    if nota:
        t += f"\n⚠️ {nota}\n"
    return t


def _botoes(st, agora_mesmo=False):
    c = _cod(st["chave"])
    if agora_mesmo:
        return {"inline_keyboard": [[{"text": "✅ Publicar agora", "callback_data": f"snow|{c}"},
                                     {"text": "❌ Reprovar publicação", "callback_data": f"sno|{c}"}]]}
    ok = "✅ Aprovar publicação" if st["auto"] else "✅ Aprovado (eu publico)"
    return {"inline_keyboard": [[{"text": ok, "callback_data": f"sok|{c}"},
                                 {"text": "❌ Reprovar publicação", "callback_data": f"sno|{c}"}]]}


def _enviar(st, estado, tg, url_publica, nota="", agora_mesmo=False):
    tg("sendPhoto", chat_id=estado["_chat"], photo=url_publica(st["img"]))
    if not st["auto"] and st["guia"].exists():
        tg("sendPhoto", chat_id=estado["_chat"], photo=url_publica(st["guia"]), caption="Guia: onde colocar o adesivo (não publique esta)")
    m = tg("sendMessage", chat_id=estado["_chat"], text=_texto(st, nota), parse_mode="Markdown",
           reply_markup=_botoes(st, agora_mesmo))
    return m["result"]["message_id"]


def _publicar(st, ig, esperar_container, url_publica, ig_user):
    c = ig(f"{ig_user}/media", media_type="STORIES", image_url=url_publica(st["img"]))
    esperar_container(c["id"])
    return ig(f"{ig_user}/media_publish", creation_id=c["id"])["id"]


def ciclo(estado, chat, tg, url_publica, ig, esperar_container, ig_user):
    est = estado.setdefault("stories", {})
    estado["_chat"] = chat
    agora = datetime.now(timezone.utc)
    try:
        for st in _lista():
            reg = est.get(st["chave"])
            if not st["img"].exists():
                continue
            if reg is None:
                if agora < st["quando"] - ANTECEDENCIA:
                    continue
                if agora > st["quando"] + timedelta(hours=3):
                    est[st["chave"]] = {"status": "expirado"}   # não publica retroativo
                    continue
                nota = "O horário já passou — se aprovar, peço confirmação para publicar agora." if agora > st["quando"] + TOLERANCIA and st["auto"] else ""
                est[st["chave"]] = {"status": "aguardando", "msg_id": _enviar(st, estado, tg, url_publica, nota)}
                continue
            if reg["status"] == "aprovado" and st["auto"] and agora >= st["quando"]:
                if agora - st["quando"] > TOLERANCIA:
                    reg["status"] = "reconfirmar"
                    reg["msg_id"] = _enviar(st, estado, tg, url_publica, f"O horário ({_hora(st['quando'])}) passou. Publicar agora?", agora_mesmo=True)
                else:
                    try:
                        reg["ig_id"] = _publicar(st, ig, esperar_container, url_publica, ig_user)
                        reg["status"] = "publicado"; reg["publicado_em"] = agora.isoformat()
                        tg("sendMessage", chat_id=chat, text=f"✅ Story publicado: {_n(st['chave'])}")
                    except Exception as e:
                        reg["status"] = "falhou"; reg["erro"] = str(e)[:200]
                        tg("sendMessage", chat_id=chat, text=f"⚠️ Story {_n(st['chave'])} falhou: {str(e)[:150]}. Não vou tentar de novo sem você.")
            if reg["status"] == "aprovado" and not st["auto"] and agora >= st["quando"] - timedelta(minutes=5) and not reg.get("lembrado"):
                reg["lembrado"] = True
                tg("sendMessage", chat_id=chat, text=f"⏰ Hora do Story interativo {_n(st['chave'])} — publique pelo app (arte e textos na mensagem de aprovação).")
    finally:
        estado.pop("_chat", None)


def tratar(acao, codigo, estado, cq, tg, responder, url_publica, ig, esperar_container, ig_user, chat):
    est = estado.setdefault("stories", {})
    st = next((x for x in _lista() if _cod(x["chave"]) == codigo), None)
    if not st or st["chave"] not in est:
        return responder(cq["id"], "Story não encontrado.")
    reg = est[st["chave"]]
    if reg.get("msg_id") and cq["message"]["message_id"] != reg["msg_id"]:
        return responder(cq["id"], "Mensagem antiga — use a mais recente deste Story.")
    agora = datetime.now(timezone.utc)
    limpar = lambda: tg("editMessageReplyMarkup", chat_id=chat, message_id=cq["message"]["message_id"], reply_markup={"inline_keyboard": []})
    if acao == "sno" and reg["status"] in ("aguardando", "aprovado", "reconfirmar"):
        reg["status"] = "reprovado"; limpar()
        responder(cq["id"], "Reprovado"); tg("sendMessage", chat_id=chat, text=f"❌ Story {_n(st['chave'])} reprovado — fica parado aguardando ajuste.")
    elif acao == "sok" and reg["status"] == "aguardando":
        if st["auto"] and agora - st["quando"] > TOLERANCIA:
            reg["status"] = "reconfirmar"; limpar()
            reg["msg_id"] = None
            estado["_chat"] = chat
            try:
                reg["msg_id"] = _enviar(st, estado, tg, url_publica, f"O horário ({_hora(st['quando'])}) já passou. Publicar agora?", agora_mesmo=True)
            finally:
                estado.pop("_chat", None)
            responder(cq["id"], "Horário passou: confirme de novo")
        else:
            reg["status"] = "aprovado"; limpar()
            responder(cq["id"], "Aprovado")
            msg = (f"🕗 Story {_n(st['chave'])} aprovado — sai sozinho em {_hora(st['quando'])}." if st["auto"]
                   else f"👍 Story {_n(st['chave'])} aprovado. Eu te lembro no horário ({_hora(st['quando'])}) para publicar pelo app.")
            tg("sendMessage", chat_id=chat, text=msg)
    elif acao == "snow" and reg["status"] == "reconfirmar" and st["auto"]:
        limpar(); responder(cq["id"], "Publicando...")
        try:
            reg["ig_id"] = _publicar(st, ig, esperar_container, url_publica, ig_user)
            reg["status"] = "publicado"; reg["publicado_em"] = agora.isoformat()
            tg("sendMessage", chat_id=chat, text=f"✅ Story publicado: {_n(st['chave'])}")
        except Exception as e:
            reg["status"] = "falhou"; reg["erro"] = str(e)[:200]
            tg("sendMessage", chat_id=chat, text=f"⚠️ Story {_n(st['chave'])} falhou: {str(e)[:150]}")
    else:
        responder(cq["id"], "Esse Story já foi resolvido.")
