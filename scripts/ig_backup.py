"""
Backup do Instagram ANTES do relançamento: todas as publicações com mídia, legenda, data, link e métricas.
Não apaga nem arquiva nada (arquivar é feito no app do Instagram; a API não permite).
Saída: backup/instagram/<data>_<id>/ (arquivos de mídia + dados.json) e backup/instagram/indice.csv
"""
import csv, json, os, sys, urllib.request
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
import comentarios as c

RAIZ = Path(__file__).resolve().parent.parent
OUT = RAIZ / "backup" / "instagram"
OUT.mkdir(parents=True, exist_ok=True)
CAMPOS = "id,caption,media_type,media_product_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count,children{id,media_type,media_url,thumbnail_url}"


def metricas(m):
    tipos = ["reach", "saved", "shares", "total_interactions", "views"]
    out = {}
    for t in tipos:   # pede uma a uma: métrica não suportada num tipo de mídia não derruba as outras
        try:
            r = c._req("GET", f"{m['id']}/insights?metric={t}")
            out[t] = r["data"][0]["values"][0]["value"] if r.get("data") else None
        except Exception as e:
            out[t] = None
    return out


def baixar(url, destino):
    try:
        destino.write_bytes(urllib.request.urlopen(url, timeout=120).read())
        return destino.name
    except Exception as e:
        print(f"[aviso] não baixou {destino.name}: {e}")
        return None


def main():
    me = c._req("GET", "me?fields=user_id,username,media_count")
    print(f"conta: @{me.get('username')} — {me.get('media_count')} publicações")
    pag = c._req("GET", f"me/media?fields={CAMPOS}&limit=50")
    itens = []
    while True:
        itens += pag.get("data", [])
        prox = pag.get("paging", {}).get("next")
        if not prox:
            break
        pag = json.loads(urllib.request.urlopen(prox, timeout=60).read())
    linhas = []
    for m in itens:
        pasta = OUT / f"{m['timestamp'][:10]}_{m['id']}"
        pasta.mkdir(exist_ok=True)
        arquivos = []
        filhos = (m.get("children") or {}).get("data") or [m]
        for k, f in enumerate(filhos):
            ext = "mp4" if f.get("media_type") == "VIDEO" else "jpg"
            if f.get("media_url"):
                arquivos.append(baixar(f["media_url"], pasta / f"{k + 1:02d}.{ext}"))
            if f.get("thumbnail_url"):
                arquivos.append(baixar(f["thumbnail_url"], pasta / f"{k + 1:02d}_capa.jpg"))
        m["metricas"] = metricas(m)
        m["arquivos"] = [a for a in arquivos if a]
        (pasta / "dados.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
        linhas.append({"data": m["timestamp"], "tipo": m.get("media_product_type") or m.get("media_type"), "link": m.get("permalink"),
                       "curtidas": m.get("like_count"), "comentarios": m.get("comments_count"), **m["metricas"],
                       "legenda": (m.get("caption") or "").replace("\n", " ")[:300]})
    with open(OUT / "indice.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()) if linhas else ["data"])
        w.writeheader(); w.writerows(linhas)
    (OUT / "conta.json").write_text(json.dumps(me, ensure_ascii=False, indent=1))
    print(f"backup: {len(itens)} publicações em {OUT}")


if __name__ == "__main__":
    main()
