"""
Cria um cenário novo a partir de uma descrição em texto (qualquer lugar).
    python scripts/gerar_cenario.py "barbearia vintage à noite com neon" -> cenarios/<slug>.jpg

Tenta, em ordem (tudo grátis):
  1. Pexels (foto real)       — precisa de PEXELS_API_KEY (grátis)
  2. Gemini (imagem por IA)   — precisa de GEMINI_API_KEY (pode não ter cota grátis)
O cenário fica salvo em cenarios/ e pode ser reutilizado pelo nome.
"""
import base64, json, os, re, sys, unicodedata, urllib.parse, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ESTILO = ("vertical 9:16 photo, empty background plate for a person to stand in front, no people, "
          "cinematic lighting, shallow depth of field, moody, premium, warm golden accents, "
          "photorealistic, 35mm film look, high detail")


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:50] or "cenario"


def via_gemini(desc):
    chave = os.environ.get("GEMINI_API_KEY")
    if not chave:
        raise RuntimeError("sem chave")
    corpo = json.dumps({"contents": [{"parts": [{"text": f"Generate an image: {desc}. {ESTILO}"}]}],
                        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"],
                                             "imageConfig": {"aspectRatio": "9:16"}}}).encode()
    for modelo in ["gemini-2.5-flash-image", "gemini-2.5-flash-image-preview", "gemini-2.0-flash-preview-image-generation"]:
        try:
            req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
                                         data=corpo, headers={"x-goog-api-key": chave, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.loads(r.read())
            for p in d["candidates"][0]["content"]["parts"]:
                if "inlineData" in p:
                    return base64.b64decode(p["inlineData"]["data"])
        except Exception as e:
            erro = e
    raise RuntimeError(f"gemini falhou: {erro}")


def via_pexels(desc):
    """Foto real, vertical, de banco grátis (uso comercial liberado)."""
    chave = os.environ.get("PEXELS_API_KEY")
    if not chave:
        raise RuntimeError("sem PEXELS_API_KEY")
    q = urllib.parse.quote(desc[:100])
    req = urllib.request.Request(f"https://api.pexels.com/v1/search?query={q}&orientation=portrait&size=large&per_page=15",
                                 headers={"Authorization": chave, "User-Agent": "Mozilla/5.0"})
    fotos = json.loads(urllib.request.urlopen(req, timeout=60).read())["photos"]
    if not fotos:
        raise RuntimeError("nenhuma foto")
    url = fotos[0]["src"]["original"] + "?auto=compress&w=2160"
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read()


def via_pixabay(desc):
    """Foto real vertical do Pixabay (grátis, uso comercial liberado)."""
    chave = os.environ.get("PIXABAY_API_KEY")
    if not chave:
        raise RuntimeError("sem PIXABAY_API_KEY")
    q = urllib.parse.quote(desc[:100])
    url = (f"https://pixabay.com/api/?key={chave}&q={q}&image_type=photo&orientation=vertical"
           f"&safesearch=true&per_page=20&order=popular")
    ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36"}
    fotos = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=ua), timeout=60).read())["hits"]
    if not fotos:
        raise RuntimeError("nenhuma foto")
    img = fotos[0]["largeImageURL"]
    return urllib.request.urlopen(urllib.request.Request(img, headers=ua), timeout=120).read()


def via_pollinations(desc):
    url = ("https://image.pollinations.ai/prompt/" + urllib.parse.quote(f"{desc}, {ESTILO}")
           + "?width=1080&height=1920&nologo=true&model=flux&seed=7")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=240) as r:
        return r.read()


def gerar(desc):
    destino = RAIZ / "cenarios" / f"{slug(desc)}.jpg"
    if destino.exists():
        return destino
    for f in (via_pixabay, via_pexels, via_gemini):
        try:
            dados = f(desc)
            if len(dados) > 20000:
                destino.write_bytes(dados)
                print(f"Cenário criado ({f.__name__}): {destino.name}")
                return destino
        except Exception as e:
            print(f"[aviso] {f.__name__}: {e}")
    raise RuntimeError("não consegui gerar o cenário")


if __name__ == "__main__":
    print(gerar(" ".join(sys.argv[1:])))
