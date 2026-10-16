"""
Camada de INGREDIENTES para capas, carrosséis e vídeos (custo zero de tokens do Claude).

    foto(busca, destino, orient="vertical")        -> Pexels, depois Pixabay (chaves já nos secrets)
    imagem_ia(descricao, destino, proporcao="9:16") -> Gemini (chave existente), depois Pollinations (grátis, sem chave)
    icone(nome)                                     -> SVG do Lucide guardado no repositório (carrossel/icones)
    PARES_FONTES                                    -> pares de fontes (título + texto) para variar por modelo

Toda imagem usada fica registrada em imagens_usadas/ingredientes.json para não repetir.
Teste: python scripts/ingredientes.py teste  (gera em testes/ingredientes/)
"""
import base64, hashlib, json, os, random, sys, urllib.parse, urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
USADAS = RAIZ / "imagens_usadas" / "ingredientes.json"
ICONES = RAIZ / "carrossel" / "icones"
UA = {"User-Agent": "Mozilla/5.0 (seraphim)"}

# estilo da marca aplicado a toda imagem gerada por IA (a paleta se mantém, a ideia muda)
ESTILO_IA = ("cinematic editorial photo, dark moody background almost black, warm golden accent light (#F5A623), "
             "soft film grain, shallow depth of field, high detail, vertical composition, "
             "absolutely no text, no letters, no words, no logos, no watermark")

# pares título/texto (arquivos em carrossel/fontes). Cada modelo de capa/cena sorteia um par diferente.
PARES_FONTES = [
    ("Anton", "Inter"), ("Bebas", "Space"), ("DMSerif", "Inter"), ("Play", "Mont"), ("Archivo", "Inter"),
    ("Syne", "Manrope"), ("Fraunces", "Manrope"), ("Unbounded", "Inter"), ("Oswald", "Space"),
    ("InstrumentSerif", "Manrope"), ("BigShoulders", "Inter"), ("Sora", "Inter"), ("Righteous", "Mont"),
]


def _usadas():
    try:
        return set(json.loads(USADAS.read_text()))
    except Exception:
        return set()


def _marcar(chave):
    s = _usadas(); s.add(str(chave))
    USADAS.parent.mkdir(exist_ok=True)
    USADAS.write_text(json.dumps(sorted(s)[-5000:]))


def _get(url, headers=None, timeout=60):
    return urllib.request.urlopen(urllib.request.Request(url, headers={**UA, **(headers or {})}), timeout=timeout).read()


# ---------------- fotos reais ----------------
def _pexels(busca, orient):
    chave = os.environ.get("PEXELS_API_KEY")
    if not chave:
        return []
    o = {"vertical": "portrait", "horizontal": "landscape"}.get(orient, "square")
    d = json.loads(_get(f"https://api.pexels.com/v1/search?query={urllib.parse.quote(busca[:90])}&orientation={o}&per_page=30",
                        {"Authorization": chave}))
    return [(f"pexels:{p['id']}", p["src"].get("portrait") if o == "portrait" else p["src"]["large2x"]) for p in d.get("photos", [])]


def _pixabay(busca, orient):
    chave = os.environ.get("PIXABAY_API_KEY")
    if not chave:
        return []
    d = json.loads(_get(f"https://pixabay.com/api/?key={chave}&q={urllib.parse.quote(busca[:90])}&image_type=photo"
                        f"&orientation={orient if orient != 'quadrada' else 'all'}&safesearch=true&per_page=30&order=popular"))
    return [(f"pixabay:{h['id']}", h.get("largeImageURL") or h["webformatURL"]) for h in d.get("hits", [])]


def foto(busca, destino, orient="vertical"):
    """foto real que ainda não usamos; None se nada servir"""
    destino = Path(destino); usadas = _usadas()
    for fonte in (_pexels, _pixabay):
        try:
            opcoes = [o for o in fonte(busca, orient) if o[0] not in usadas]
        except Exception as e:
            print(f"[aviso] {fonte.__name__} '{busca}': {e}"); continue
        random.Random(busca).shuffle(opcoes)
        for chave, url in opcoes[:5]:
            try:
                dados = _get(url, timeout=90)
            except Exception:
                continue
            if len(dados) > 30000:
                destino.write_bytes(dados); _marcar(chave)
                print(f"[foto] {chave} <- '{busca}'"); return destino
    return None


# ---------------- imagem gerada por IA ----------------
def _gemini_img(descricao, proporcao):
    chave = os.environ.get("GEMINI_API_KEY")
    if not chave:
        return None
    corpo = {"contents": [{"parts": [{"text": f"{descricao}. {ESTILO_IA}"}]}],
             "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": proporcao}}}
    for modelo in ("gemini-2.5-flash-image", "gemini-2.0-flash-preview-image-generation"):
        try:
            if "2.0" in modelo:
                corpo["generationConfig"] = {"responseModalities": ["TEXT", "IMAGE"]}
            req = urllib.request.Request(
                f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={chave}",
                data=json.dumps(corpo).encode(), headers={"Content-Type": "application/json"})
            r = json.loads(urllib.request.urlopen(req, timeout=120).read())
            for p in r["candidates"][0]["content"]["parts"]:
                if "inlineData" in p:
                    return base64.b64decode(p["inlineData"]["data"]), modelo
        except Exception as e:
            msg = getattr(e, "read", lambda: b"")()[:200]
            print(f"[aviso] {modelo}: {e} {msg}")
    return None


def _pollinations(descricao, proporcao):
    w, h = {"9:16": (1080, 1920), "4:5": (1080, 1350), "1:1": (1080, 1080), "16:9": (1920, 1080)}.get(proporcao, (1080, 1350))
    seed = int(hashlib.md5(descricao.encode()).hexdigest(), 16) % 10**6
    url = (f"https://image.pollinations.ai/prompt/{urllib.parse.quote(descricao + '. ' + ESTILO_IA)}"
           f"?width={w}&height={h}&nologo=true&seed={seed}&model=flux")
    try:
        dados = _get(url, timeout=180)
        return (dados, "pollinations") if len(dados) > 20000 else None
    except Exception as e:
        print(f"[aviso] pollinations: {e}")
        return None


def imagem_ia(descricao, destino, proporcao="9:16"):
    """descricao em inglês, concreta (cena, objeto, luz). Sempre sem texto na imagem."""
    destino = Path(destino)
    for f in (_gemini_img, _pollinations):
        r = f(descricao, proporcao)
        if r:
            destino.write_bytes(r[0]); print(f"[ia] {r[1]} <- '{descricao[:60]}'"); return destino
    return None


def ilustracao(descricao, busca_foto, destino, proporcao="9:16"):
    """tenta IA; se falhar, foto real; se falhar, None (o modelo usa só tipografia)"""
    return imagem_ia(descricao, destino, proporcao) or foto(busca_foto or descricao, destino,
                                                             "vertical" if proporcao in ("9:16", "4:5") else "horizontal")


# ---------------- ícones ----------------
def icone(nome, cor="#F5A623", tam=96, traco=2):
    """SVG inline do Lucide (pasta carrossel/icones); '' se não existir"""
    f = ICONES / f"{nome}.svg"
    if not f.exists():
        return ""
    s = f.read_text()
    return (s.replace('width="24"', f'width="{tam}"').replace('height="24"', f'height="{tam}"')
             .replace('stroke="currentColor"', f'stroke="{cor}"').replace('stroke-width="2"', f'stroke-width="{traco}"'))


if __name__ == "__main__" and sys.argv[1:2] == ["teste"]:
    out = RAIZ / "testes" / "ingredientes"; out.mkdir(parents=True, exist_ok=True)
    rel = {
        "foto": str(foto("mechanic workshop car engine", out / "foto.jpg")),
        "ia": str(imagem_ia("a lone smartphone glowing on a mechanic's workbench at night, tools around", out / "ia.jpg")),
        "pollinations": bool(_pollinations("golden robot hand typing on a keyboard", "4:5")),
        "gemini": bool(_gemini_img("golden robot hand typing on a keyboard", "4:5")),
    }
    (out / "resultado.json").write_text(json.dumps(rel, indent=1)); print(rel)
