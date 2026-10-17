"""
Publica no TikTok pelo Buffer (plano grátis), com legenda e hashtags, sem passo manual.

O Buffer é parceiro aprovado do TikTok: o post sai público e com a legenda, coisa que o nosso app
de teste do TikTok não consegue enquanto não passa na auditoria.

Precisa do segredo BUFFER_TOKEN (chave criada em publish.buffer.com/settings/api) e do TikTok
conectado dentro do Buffer. O vídeo é lido direto do repositório público (link raw do GitHub).

    python scripts/buffer.py canais                      -> lista os canais conectados
    python scripts/buffer.py teste fila/<pasta> "legenda" -> publica um vídeo no TikTok
"""
import json, os, sys, urllib.request
from pathlib import Path

API = "https://api.buffer.com"
TOKEN = os.environ.get("BUFFER_TOKEN", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "pablloleviev/seraphim-publicador")
RAIZ = Path(__file__).resolve().parent.parent


def ativo() -> bool:
    return bool(TOKEN)


def gql(query: str, variaveis=None):
    corpo = json.dumps({"query": query, "variables": variaveis or {}}).encode()
    req = urllib.request.Request(API, data=corpo, headers={"Authorization": f"Bearer {TOKEN}",
                                                           "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Buffer {e.code}: {e.read().decode()[:400]}")
    if d.get("errors"):
        raise RuntimeError("Buffer: " + "; ".join(e.get("message", "") for e in d["errors"])[:400])
    return d["data"]


def canais():
    orgs = gql("query { account { organizations { id name } } }")["account"]["organizations"]
    todos = []
    for o in orgs:
        cs = gql("query($o: OrganizationId!) { channels(input: {organizationId: $o}) { id name service } }",
                 {"o": o["id"]})["channels"]
        todos += [{**c, "org": o["id"]} for c in cs]
    return todos


def canal_tiktok():
    fixo = os.environ.get("BUFFER_CANAL_TIKTOK")
    if fixo:
        return fixo
    for c in canais():
        if "tiktok" in (c.get("service") or "").lower():
            return c["id"]
    raise RuntimeError("nenhum TikTok conectado no Buffer")


def url_publica(arquivo: Path) -> str:
    rel = arquivo.resolve().relative_to(RAIZ).as_posix()
    return f"https://raw.githubusercontent.com/{REPO}/main/{rel}"


def _s(t: str) -> str:
    return json.dumps(t, ensure_ascii=False)   # string GraphQL (mesma sintaxe de string JSON)


def publicar_tiktok(video: Path, legenda: str, capa: Path = None, rascunho=False) -> str:
    canal = canal_tiktok()
    url = url_publica(video)
    titulo = legenda.split("\n")[0][:90]
    base = (f'text: {_s(legenda[:2200])}, channelId: {_s(canal)}, schedulingType: automatic, mode: shareNow, '
            f'assets: [{{ video: {{ url: {_s(url)}, metadata: {{ thumbnailOffset: 0 }} }} }}]' + (', saveToDraft: true' if rascunho else ''))   # capa = 1º quadro (video_tiktok.mp4); a rede não aceita imagem de capa avulsa
    sel = "{ ... on PostActionSuccess { post { id } } ... on MutationError { message } }"
    tentativas = [f"{base}, metadata: {{ tiktok: {{ title: {_s(titulo)} }} }}", base]
    erro = None
    for entrada in tentativas:
        try:
            r = gql(f"mutation {{ createPost(input: {{ {entrada} }}) {sel} }}")["createPost"]
        except RuntimeError as e:
            erro = e; continue
        if r.get("post"):
            return r["post"]["id"]
        erro = RuntimeError("Buffer recusou: " + str(r.get("message")))
    raise erro


def publicar_tiktok_fotos(fotos, legenda: str, rascunho=False) -> str:
    """carrossel no TikTok (post de fotos, formato nativo). fotos = lista de Path, a 1ª é a capa."""
    canal = canal_tiktok()
    titulo = legenda.split("\n")[0][:90]
    imgs = ", ".join(f"{{ image: {{ url: {_s(url_publica(f))} }} }}" for f in fotos[:35])
    imgs2 = ", ".join(f"{{ url: {_s(url_publica(f))} }}" for f in fotos[:35])
    base = f'text: {_s(legenda[:2200])}, channelId: {_s(canal)}, schedulingType: automatic, mode: shareNow'
    if rascunho:
        base += ", saveToDraft: true"
    sel = "{ ... on PostActionSuccess { post { id } } ... on MutationError { message } }"
    tentativas = [f"{base}, assets: [{imgs}], metadata: {{ tiktok: {{ title: {_s(titulo)} }} }}", f"{base}, assets: [{imgs}]",
                  f"{base}, assets: {{ images: [{imgs2}] }}"]
    erro = None
    for entrada in tentativas:
        try:
            r = gql(f"mutation {{ createPost(input: {{ {entrada} }}) {sel} }}")["createPost"]
        except RuntimeError as e:
            erro = e; continue
        if r.get("post"):
            return r["post"]["id"]
        erro = RuntimeError("Buffer recusou: " + str(r.get("message")))
    raise erro


def esquema():
    for t in ("VideoAssetInput", "VideoMetadataInput", "CreatePostInput", "AssetsInput", "AssetInput", "ImageAssetInput", "PostMetadataInput", "TikTokPostMetadataInput", "ShareMode"):
        try:
            r = gql('query($n: String!) { __type(name: $n) { name kind inputFields { name type { name kind ofType { name kind ofType { name } } } } enumValues { name } } }', {"n": t})
            print(json.dumps(r, ensure_ascii=False))
        except RuntimeError as e:
            print(t, "->", e)


if __name__ == "__main__":
    if sys.argv[1] == "esquema":
        esquema(); sys.exit(0)
    if sys.argv[1] == "rascunho_video":   # teste sem publicar: RASCUNHO de vídeo no Buffer
        pasta = RAIZ / sys.argv[2]
        v = pasta / "video_tiktok.mp4" if (pasta / "video_tiktok.mp4").exists() else pasta / "video.mp4"
        print("rascunho de vídeo:", publicar_tiktok(v, "teste (rascunho, não publicar)", rascunho=True)); sys.exit(0)
    if sys.argv[1] == "rascunho_fotos":   # teste sem publicar: cria RASCUNHO no Buffer
        fotos = sorted((RAIZ / sys.argv[2]).glob("slide-*.jpg"))
        print("rascunho de fotos:", publicar_tiktok_fotos(fotos, "teste (rascunho, não publicar)", rascunho=True)); sys.exit(0)
    if sys.argv[1] == "canais":
        print(json.dumps(canais(), indent=1, ensure_ascii=False))
    elif sys.argv[1] == "posts":
        org = gql("query { account { organizations { id } } }")["account"]["organizations"][0]["id"]
        for q in ['query($o: OrganizationId!) { posts(input: {organizationId: $o}, first: 10) { edges { node { id status text dueAt sentAt error { message } } } } }',
                  'query($o: OrganizationId!) { posts(input: {organizationId: $o}) { edges { node { id status text dueAt error { message } } } } }',
                  'query($o: OrganizationId!) { posts(input: {organizationId: $o}) { edges { node { id status text } } } }']:
            try:
                print(json.dumps(gql(q, {"o": org}), indent=1, ensure_ascii=False)); break
            except RuntimeError as e:
                print("tentativa falhou:", e)
    elif sys.argv[1] == "teste":
        pasta = RAIZ / sys.argv[2]
        meta = json.loads((pasta / "item.json").read_text(encoding="utf-8"))
        leg = sys.argv[3] if len(sys.argv) > 3 else (meta.get("legenda_tiktok") or meta.get("legenda", ""))
        print("post:", publicar_tiktok(pasta / "video.mp4", leg))
