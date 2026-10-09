"""
Cria um cenário novo a partir de uma descrição em texto (qualquer lugar).
    python scripts/gerar_cenario.py "barbearia vintage à noite com neon" -> cenarios/<slug>.jpg

Tenta, em ordem (tudo grátis):
  1. Gemini (imagem)          — precisa de GEMINI_API_KEY
  2. Pollinations (Flux)      — sem chave
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
    for f in (via_gemini, via_pollinations):
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
