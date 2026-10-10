"""
Gera a página do material gratuito entregue por palavra-chave (GitHub Pages, grátis).

    material.gerar({"slug": "checklist-orcamento", "titulo": "...", "subtitulo": "...",
                    "itens": [{"titulo": "...", "texto": "..."}], "dica": "...", "autoflow": False})
    -> "https://pablloleviev.github.io/seraphim-publicador/m/checklist-orcamento/"

A página fica em docs/m/<slug>/index.html (o GitHub Pages publica a pasta docs/).
"""
import html, json, re, shutil, unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
BASE = "https://pablloleviev.github.io/seraphim-publicador"
INSTAGRAM = "https://instagram.com/seraphimtech_"


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:50] or "material"


def _fmt(t):
    t = html.escape(t or "")
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t).replace("\n", "<br>")


def gerar(m: dict) -> str:
    s = slug(m.get("slug") or m["titulo"])
    pasta = DOCS / "m" / s
    pasta.mkdir(parents=True, exist_ok=True)
    (DOCS / "assets").mkdir(parents=True, exist_ok=True)
    icone = DOCS / "assets" / "icone.png"
    if not icone.exists():
        shutil.copy(RAIZ / "motor" / "public" / "marca" / "icone.png", icone)
    itens = "".join(
        f'<li><label><input type="checkbox"><span class="n">{i:02d}</span>'
        f'<span class="t"><b>{_fmt(it.get("titulo"))}</b><em>{_fmt(it.get("texto"))}</em></span></label></li>'
        for i, it in enumerate(m.get("itens", []), 1))
    dica = f'<div class="dica"><span>Dica de ouro</span>{_fmt(m["dica"])}</div>' if m.get("dica") else ""
    autoflow = ('<a class="btn sec" href="https://autoflow-gestao.vercel.app">Tem oficina? Conheça o AutoFlow →</a>'
                if m.get("autoflow") else "")
    pagina = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(m['titulo'])} · Seraphim</title>
<meta name="description" content="{html.escape(m.get('subtitulo', ''))}">
<meta property="og:title" content="{html.escape(m['titulo'])}"><meta property="og:image" content="{BASE}/assets/icone.png">
<link rel="icon" href="../../assets/icone.png">
<style>
:root{{--bg:#0A0A0C;--card:#141418;--txt:#F5F5F7;--sub:#A1A1AA;--ouro:#F5A623;--linha:#26262c}}
*{{box-sizing:border-box;margin:0}}body{{background:var(--bg);color:var(--txt);font:17px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
background-image:radial-gradient(circle at 85% -10%,rgba(245,166,35,.18),transparent 45%)}}
main{{max-width:680px;margin:0 auto;padding:28px 18px 60px}}
.top{{display:flex;align-items:center;gap:12px;color:var(--sub);font-size:14px}}.top img{{width:38px;height:38px;border-radius:50%;box-shadow:0 0 0 2px var(--ouro)}}
.tag{{display:inline-block;margin:34px 0 10px;color:var(--ouro);font-weight:800;letter-spacing:.18em;font-size:12px;text-transform:uppercase}}
h1{{font-size:clamp(30px,7vw,44px);line-height:1.08;letter-spacing:-.02em}}h1 b{{color:var(--ouro)}}
.sub{{color:var(--sub);margin-top:12px;font-size:18px}}
ul{{list-style:none;padding:0;margin:30px 0}}li{{background:var(--card);border:1px solid var(--linha);border-radius:16px;margin-bottom:12px}}
label{{display:flex;gap:14px;padding:16px 18px;cursor:pointer;align-items:flex-start}}
input{{appearance:none;flex:0 0 24px;height:24px;border:2px solid #4a4a52;border-radius:7px;margin-top:3px}}
input:checked{{background:var(--ouro);border-color:var(--ouro)}}input:checked+.n+.t b{{text-decoration:line-through;opacity:.6}}
.n{{color:var(--ouro);font-weight:800;font-variant-numeric:tabular-nums;margin-top:1px}}
.t{{display:flex;flex-direction:column;gap:4px}}.t em{{font-style:normal;color:var(--sub);font-size:15.5px}}.t em b{{color:var(--txt)}}
.dica{{border-left:3px solid var(--ouro);background:rgba(245,166,35,.07);padding:16px 18px;border-radius:0 14px 14px 0;color:#e8e3da}}
.dica span{{display:block;color:var(--ouro);font-weight:800;font-size:12px;letter-spacing:.14em;text-transform:uppercase;margin-bottom:6px}}
.fim{{margin-top:38px;text-align:center}}.fim p{{color:var(--sub);margin-bottom:16px}}
.btn{{display:block;text-align:center;text-decoration:none;font-weight:800;padding:16px;border-radius:14px;background:var(--ouro);color:#0A0A0C;margin-top:10px}}
.btn.sec{{background:transparent;color:var(--txt);border:1px solid var(--linha)}}
.print{{background:none;border:0;color:var(--sub);text-decoration:underline;margin-top:18px;font:inherit;cursor:pointer}}
@media print{{body{{background:#fff;color:#000}}li{{background:#fff;border-color:#ccc}}.t em{{color:#333}}.fim,.print{{display:none}}}}
</style></head><body><main>
<div class="top"><img src="../../assets/icone.png" alt=""><span>@seraphimtech_ · material gratuito</span></div>
<div class="tag">{html.escape(m.get('tipo', 'Checklist'))}</div>
<h1>{_fmt(m['titulo']).replace('&lt;b&gt;', '<b>')}</h1>
<p class="sub">{_fmt(m.get('subtitulo', ''))}</p>
<ul>{itens}</ul>
{dica}
<div class="fim"><p>Curtiu? Todo dia tem mais conteúdo assim.</p>
<a class="btn" href="{INSTAGRAM}">Seguir a @seraphimtech_ no Instagram</a>{autoflow}
<button class="print" onclick="window.print()">Salvar em PDF / imprimir</button></div>
</main></body></html>"""
    (pasta / "index.html").write_text(pagina, encoding="utf-8")
    _indice()
    return f"{BASE}/m/{s}/"


def _indice():
    DOCS.mkdir(exist_ok=True)
    (DOCS / ".nojekyll").write_text("")
    idx = DOCS / "index.html"
    if not idx.exists():
        idx.write_text('<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=https://instagram.com/seraphimtech_">'
                       '<title>Seraphim</title><a href="https://instagram.com/seraphimtech_">@seraphimtech_</a>', encoding="utf-8")


if __name__ == "__main__":
    import sys
    print(gerar(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))))
