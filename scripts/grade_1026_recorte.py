import sys, numpy as np, cv2
from PIL import Image
from rembg import remove, new_session
from pymatting import estimate_alpha_cf, estimate_foreground_ml
src, out = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
s = new_session("u2net_human_seg")
m = np.array(remove(im, session=s, only_mask=True)).astype(np.uint8)
m = cv2.resize(m, im.size, interpolation=cv2.INTER_CUBIC)
m = cv2.GaussianBlur(m, (0, 0), 5)
_, b = cv2.threshold(m, 127, 255, cv2.THRESH_BINARY)
b = cv2.GaussianBlur(b, (0, 0), 3); _, b = cv2.threshold(b, 127, 255, cv2.THRESH_BINARY)
k = lambda r: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r+1, 2*r+1))
fg = cv2.erode(b, k(6)); bgm = cv2.dilate(b, k(11))
tri = np.full(b.shape, 0.5, np.float64); tri[fg == 255] = 1.0; tri[bgm == 0] = 0.0
img = np.asarray(im, np.float64) / 255
alpha = estimate_alpha_cf(img, tri)
alpha = np.clip(alpha, 0, 1)
F = estimate_foreground_ml(img, alpha)
rgba = np.dstack([np.clip(F, 0, 1), alpha])
Image.fromarray((rgba * 255).astype(np.uint8), "RGBA").save(out)
print("ok", out)
