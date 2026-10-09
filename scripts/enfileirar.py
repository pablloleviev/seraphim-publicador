"""
Coloca um carrossel ou vídeo pronto na fila de publicação.
Roda no seu PC (dentro da pasta seraphim-publicador).

Uso:
    python scripts/enfileirar.py <pasta-ou-mp4> "2026-10-12 18:00" [arquivo-legenda.txt]

Exemplos:
    python scripts/enfileirar.py ..\Seraphim-Conteudo\entrega\carrosseis\5-erros "2026-10-12 18:00"
    python scripts/enfileirar.py ..\Seraphim-Conteudo\entrega\videos\fiado.mp4 "2026-10-13 12:00"

Depois: git add . && git commit -m "fila" && git push
"""
import json, shutil, sys
from datetime import datetime
from pathlib import Path
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    origem = Path(sys.argv[1]).resolve()
    quando = datetime.strptime(sys.argv[2], "%Y-%m-%d %H:%M")
    nome = origem.stem if origem.is_file() else origem.name
    destino = RAIZ / "fila" / f"{quando:%Y-%m-%d_%H%M}_{nome}"
    destino.mkdir(parents=True, exist_ok=True)

    if origem.is_file() and origem.suffix.lower() == ".mp4":
        tipo = "reels"
        shutil.copy(origem, destino / "video.mp4")
        leg = origem.with_suffix(".txt")
    else:
        tipo = "carrossel"
        slides = sorted(origem.glob("slide-*.png")) + sorted(origem.glob("slide-*.jpg"))
        for s in slides:
            Image.open(s).convert("RGB").save(destino / f"{s.stem}.jpg", quality=92)
        leg = origem / "legenda.txt"
    if len(sys.argv) > 3:
        leg = Path(sys.argv[3])
    legenda = leg.read_text(encoding="utf-8") if leg.exists() else ""

    (destino / "item.json").write_text(json.dumps({
        "tipo": tipo, "legenda": legenda, "quando": quando.strftime("%Y-%m-%dT%H:%M:00-03:00"),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Na fila: {destino.name} ({tipo}) para {quando:%d/%m %H:%M}")


if __name__ == "__main__":
    main()
