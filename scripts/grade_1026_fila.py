"""Põe na fila (fila/) as peças da grade 26/10–01/11 a partir de amanhã (TER 27/10). A SEG 26/10 fica de fora (dia perdido, por decisão do Pabllo).
Cada item ainda passa pelo ✅ individual no Telegram antes de publicar. Uso: python scripts/grade_1026_fila.py"""
import json, shutil, subprocess, sys
from pathlib import Path
from PIL import Image, ImageFilter
sys.path.insert(0, str(Path(__file__).parent))
import capa_no_video

R = Path(__file__).resolve().parent.parent
P = R / "previas/grade-2026-10-26"
PLANO = [  # (pasta da prévia, data, hora, slug)
    ("2026-10-27_ter_carrossel", "2026-10-27", "1230", "ia-na-operacao"),
    ("2026-10-28_qua_post", "2026-10-28", "1230", "tecnologia-que-comeca-ouvindo"),
    ("2026-10-29_qui_reel", "2026-10-29", "1930", "mais-uma-aba-aberta"),
    ("2026-10-30_sex_carrossel", "2026-10-30", "1230", "checklist-fim-de-mes"),
    ("2026-10-31_sab_reel", "2026-10-31", "1930", "terror-da-operacao"),
    ("2026-11-01_dom_post", "2026-11-01", "1230", "construir-e-construir-clareza"),
]

def tiktok_slide(src: Path, dst: Path):
    im = Image.open(src).convert("RGB")
    fundo = im.resize((1080, 1920)).filter(ImageFilter.GaussianBlur(40))
    fundo.paste(im, (0, (1920 - im.height) // 2))
    fundo.save(dst, quality=94)

for pasta, dia, hora, slug in PLANO:
    src = P / pasta
    dest = R / "fila" / f"{dia}_{hora}_{slug}"
    if dest.exists():
        print("já existe:", dest.name); continue
    dest.mkdir(parents=True)
    legenda = (src / "legenda.txt").read_text(encoding="utf-8").strip()
    quando = f"{dia}T{hora[:2]}:{hora[2:]}:00-03:00"
    if (src / "video.mp4").exists():
        shutil.copy(src / "video.mp4", dest / "video.mp4"); shutil.copy(src / "capa.jpg", dest / "capa.jpg")
        capa_no_video.fazer(dest)
        tags = " ".join(legenda.split("\n")[-1].split()[:3] + ["#seraphimbr"])
        item = {"tipo": "reels", "legenda": legenda, "quando": quando, "funil": "topo",
                "legenda_tiktok": legenda.split("\n\n")[0][:150] + "\n\n" + tags}
    else:
        slides = sorted(src.glob("slide-*.jpg")) or [src / "capa.jpg"]
        (dest / "tiktok").mkdir()
        for i, s in enumerate(slides, 1):
            shutil.copy(s, dest / f"slide-{i:02d}.jpg"); tiktok_slide(s, dest / "tiktok" / f"slide-{i:02d}.jpg")
        item = {"tipo": "carrossel", "legenda": legenda, "quando": quando}
    (dest / "item.json").write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")
    print("ok", dest.name)
