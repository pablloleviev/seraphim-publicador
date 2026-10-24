"""Recorte do Pabllo: matting fino na cabeça (cabelo/orelhas) + máscara suave nos ombros (suéter preto sobre fundo preto não tem borda para o matting achar)."""
import numpy as np, cv2
from PIL import Image
from pathlib import Path
R = Path(__file__).resolve().parent.parent
T = R / "previas/grade-2026-10-26/_trabalho"
fino = np.asarray(Image.open(T / "pabllo_recorte_fino.png").convert("RGBA"), np.float64) / 255
orig = np.asarray(Image.open(R / "assets/pessoas/pabllo.png").convert("RGB"), np.float64) / 255
a_fino = fino[..., 3]
# máscara suave: do alpha fino, binarizado, aberto/fechado e feather
b = (cv2.GaussianBlur(a_fino, (0, 0), 6) > .5).astype(np.float64)
b = cv2.GaussianBlur(b, (0, 0), 2.2)
h = a_fino.shape[0]
y = np.arange(h)[:, None] / h * 1.0
rampa = np.clip((y * 1024 - 330) / 70, 0, 1)           # 0 na cabeça (matting) -> 1 nos ombros (suave)
alpha = a_fino * (1 - rampa) + b * rampa
rgb = fino[..., :3] * (1 - rampa[..., None]) + orig * rampa[..., None]
out = np.dstack([rgb, alpha])
Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "RGBA").save(T / "pabllo_recorte_final.png")
print("ok")
