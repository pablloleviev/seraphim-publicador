"""
Gera a capa.jpg (1080x1920) de cada vídeo da fila que ainda não tem, usando título/formato do historico.json.
Uso: python scripts/capas_fila.py          (só os que faltam)
     python scripts/capas_fila.py --todas   (refaz todas)
"""
import asyncio, json, re, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import capa, ingredientes


def _rotulo(h: dict) -> str:
    f = (h.get("formato") or "").strip()
    return f if 0 < len(f) <= 24 else ""


def faltantes(todas=False):
    hist = {h.get("nome"): h for h in json.loads((RAIZ / "historico.json").read_text(encoding="utf-8"))}
    itens = []
    for pasta in sorted((RAIZ / "fila").glob("*")):
        meta = pasta / "item.json"
        nome = re.sub(r"^\d{4}-\d{2}-\d{2}_\d{4}_", "", pasta.name)
        if not pasta.is_dir():
            continue
        tipo = json.loads(meta.read_text(encoding="utf-8")).get("tipo") if meta.exists() else ("reels" if (pasta / "video.mp4").exists() or nome in hist else None)
        if tipo != "reels" and not (nome in hist and hist[nome].get("tipo") == "video"):
            continue
        if pasta.name[:10] < __import__("datetime").date.today().isoformat():
            continue
        if (pasta / "capa.jpg").exists() and not todas:
            continue
        h = hist.get(nome, {})
        itens.append({"titulo": h.get("capa") or h.get("titulo") or nome.replace("-", " ").capitalize(), "rotulo": _rotulo(h), "saida": pasta / "capa.jpg",
                      "cena": h.get("capa_cena", ""), "busca": next(iter(h.get("buscas") or []), "")})
    return itens


def main(todas=False):
    itens = faltantes(todas)
    hp = RAIZ / "historico.json"
    hist = json.loads(hp.read_text(encoding="utf-8"))
    recentes = [h["capa_modelo"] for h in hist if h.get("capa_modelo")]
    por_nome = {h.get("nome"): h for h in hist}
    for it in sorted(itens, key=lambda x: x["saida"].parent.name):
        # ~60% das capas ganham imagem (IA pela cena; senão foto real pela busca); o resto fica só em design/tipografia
        img = None
        if capa.semente(it["titulo"]) % 5 < 3 and (it.get("cena") or it.get("busca")):
            img = ingredientes.ilustracao(it.get("cena") or it["busca"], it.get("busca") or it.get("cena"),
                                          it["saida"].parent / "capa_img.jpg", "4:5")
        it["imagem"] = str(img or "")
        it["modelo"] = capa.escolher(it["titulo"], it["rotulo"], recentes, tem_imagem=bool(img))
        recentes.append(it["modelo"])
        nome = re.sub(r"^\d{4}-\d{2}-\d{2}_\d{4}_", "", it["saida"].parent.name)
        if nome in por_nome:
            por_nome[nome]["capa_modelo"] = it["modelo"]
        print(it["saida"].parent.name, "->", it["modelo"])
    hp.write_text(json.dumps(hist, ensure_ascii=False, indent=1), encoding="utf-8")
    if itens:
        asyncio.run(capa.gerar_varias(itens))
        for it in itens:
            Path(it["saida"].parent / "capa_img.jpg").unlink(missing_ok=True)
    print(f"capas geradas: {len(itens)}")
    return len(itens)


if __name__ == "__main__":
    main("--todas" in sys.argv)
