"""
Prévia do FEED do Instagram: mostra como a grade fica com os posts agendados (capas dos vídeos + 1º slide dos carrosséis).
Uso:
    python scripts/feed.py                 -> feed/previa-AAAA-MM-DD.png
    python scripts/feed.py --enviar        -> também manda a imagem para o Telegram (precisa TELEGRAM_TOKEN e TELEGRAM_CHAT_ID)
    python scripts/feed.py --dias 7        -> quantos dias à frente entram (padrão 7)
"""
import sys as _s, os as _o; _s.path.insert(0, _o.path.dirname(_o.path.abspath(__file__)))
from marca import ARROBA, USUARIO, INSTAGRAM_URL
import asyncio, json, os, re, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from playwright.async_api import async_playwright

RAIZ = Path(__file__).resolve().parent.parent
BRT = timezone(timedelta(hours=-3))
ICONE = (RAIZ / "carrossel" / "marca" / "icone.png").as_uri()
FONTES = (RAIZ / "carrossel" / "fontes").as_uri()


def coletar(dias):
    agora = datetime.now(BRT).replace(tzinfo=None)
    limite = agora + timedelta(days=dias)
    est = json.loads((RAIZ / "estado.json").read_text(encoding="utf-8")).get("itens", {}) if (RAIZ / "estado.json").exists() else {}
    fut, pas = [], []
    for pasta in sorted((RAIZ / "fila").glob("*")):
        m = re.match(r"(\d{4}-\d{2}-\d{2})_(\d{2})(\d{2})_", pasta.name)
        if not m or not pasta.is_dir():
            continue
        quando = datetime.strptime(f"{m.group(1)} {m.group(2)}:{m.group(3)}", "%Y-%m-%d %H:%M")
        capa = pasta / "capa.jpg" if (pasta / "capa.jpg").exists() else (pasta / "slide-01.jpg" if (pasta / "slide-01.jpg").exists() else None)
        if not capa:
            continue
        item = {"quando": quando, "img": capa.as_uri(), "carrossel": capa.name.startswith("slide"), "status": est.get(pasta.name, {}).get("status")}
        if quando > agora:
            if quando <= limite:
                fut.append(item)
        elif item["status"] == "publicado":
            pas.append(item)
    fut.sort(key=lambda x: x["quando"], reverse=True)
    pas.sort(key=lambda x: x["quando"], reverse=True)
    return fut, pas[:9]


def html(fut, pas):
    def tile(it, futuro):
        sel = f'<div class="d">{it["quando"]:%d/%m %Hh}</div>' if futuro else ""
        ic = '<div class="i">❐</div>' if it["carrossel"] else '<div class="i">▶</div>'
        return f'<div class="t"><img src="{it["img"]}">{ic}{sel}</div>'
    grade = "".join(tile(i, True) for i in fut) + "".join(tile(i, False) for i in pas)
    return f"""<html><head><meta charset="utf-8"><style>
@font-face{{font-family:Inter;font-weight:500;src:url({FONTES}/inter500.ttf)}}
@font-face{{font-family:Inter;font-weight:800;src:url({FONTES}/inter800.ttf)}}
@font-face{{font-family:Anton;src:url({FONTES}/anton.ttf)}}
*{{margin:0;box-sizing:border-box}} body{{width:1080px;background:#000;color:#fff;font-family:Inter}}
.top{{padding:50px 48px 30px;display:flex;align-items:center;gap:36px}} .av{{width:170px;height:170px;border-radius:50%;box-shadow:0 0 0 6px #F5A623;background:#0A0A0C}}
.nm{{font:800 46px Inter}} .bio{{font:500 30px/1.3 Inter;color:#cfcfd4;margin-top:8px}}
.nota{{margin:0 48px 26px;padding:16px 24px;border-radius:18px;background:#15151a;border:2px solid rgba(245,166,35,.4);font:500 28px Inter;color:#F5A623}}
.g{{display:grid;grid-template-columns:repeat(3,1fr);gap:4px}}
.t{{position:relative;aspect-ratio:3/4;overflow:hidden;background:#111}} .t img{{width:100%;height:100%;object-fit:cover;object-position:center}}
.i{{position:absolute;right:14px;top:12px;font:800 34px Inter;text-shadow:0 2px 8px #000}}
.d{{position:absolute;left:10px;bottom:10px;background:rgba(0,0,0,.72);border:2px solid #F5A623;color:#F5A623;font:800 24px Inter;padding:6px 12px;border-radius:10px}}
</style></head><body>
<div class="top"><img class="av" src="{ICONE}"><div><div class="nm">{USUARIO}</div><div class="bio">Seraphim • IA e automação<br>para pequenas empresas</div></div></div>
<div class="nota">Prévia do feed: os posts com data (dd/mm hh) ainda vão ser publicados; os sem data já estão no ar.</div>
<div class="g">{grade}</div></body></html>"""


async def gerar(dias):
    fut, pas = coletar(dias)
    saida = RAIZ / "feed"; saida.mkdir(exist_ok=True)
    arq = saida / f"previa-{datetime.now(BRT):%Y-%m-%d}.png"
    tmp = RAIZ / "_feed_tmp.html"; tmp.write_text(html(fut, pas), encoding="utf-8")
    async with async_playwright() as p:
        nav = await p.chromium.launch()
        pg = await nav.new_page(viewport={"width": 1080, "height": 1200})
        await pg.goto(tmp.as_uri()); await pg.wait_for_timeout(600)
        await pg.screenshot(path=str(arq), full_page=True)
        await nav.close()
    tmp.unlink()
    print(f"prévia: {arq} ({len(fut)} agendados + {len(pas)} publicados)")
    return arq


def enviar(arq):
    tok, chat = os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")
    if not tok or not chat:
        print("[aviso] sem TELEGRAM_TOKEN/CHAT_ID: não enviei"); return
    leg = "🗓️ Prévia do feed da semana: capas dos vídeos e carrosséis agendados (data em dourado). Se algo não combinar, me avisa antes de postar."
    r = subprocess.run(["curl", "-s", "-F", f"chat_id={chat}", "-F", f"caption={leg}", "-F", f"document=@{arq}",
                        f"https://api.telegram.org/bot{tok}/sendDocument"], capture_output=True, text=True)
    print("telegram:", r.stdout[:120])


if __name__ == "__main__":
    dias = int(sys.argv[sys.argv.index("--dias") + 1]) if "--dias" in sys.argv else 7
    arq = asyncio.run(gerar(dias))
    if "--enviar" in sys.argv:
        enviar(arq)
