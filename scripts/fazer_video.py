"""
Faz um vídeo vertical da Seraphim do começo ao fim:
roteiro (JSON) -> narração com tempo de cada palavra -> edição no motor Remotion -> MP4.

Uso:
    python scripts/fazer_video.py entrada/meu-video.json
    python scripts/fazer_video.py entrada/meu-video.json --voz edge     (voz grátis Microsoft)
    python scripts/fazer_video.py entrada/meu-video.json --voz nenhuma  (sem narração, para testes)

Voz padrão: ElevenLabs (precisa de ELEVENLABS_API_KEY no arquivo .env na raiz do projeto).
Se a ElevenLabs falhar, cai automaticamente para a voz grátis (edge) e avisa.

Formato do roteiro: veja exemplos/video-exemplo.json
Cada cena:
  "modelo":  "impacto" | "numero" | "imagem" | "lista" | "cta"
  "linhas":  ["SUA", "*OFICINA*"]        (*palavra* = dourado)
  "numero":  "01"                        (modelo numero)
  "apoio":   "texto pequeno"             (no cta vira o botão)
  "itens":   ["item 1", "item 2"]        (modelo lista)
  "imagem":  "banco/oficina-elevador.png" (modelo imagem; caminho dentro de assets/)
  "sera":    "surpreso"                  (pose do mascote, opcional)
  "fundo":   "escuro" | "branco"
  "raios":   true | false
  "narracao":"o que a voz fala nessa cena"
"""
import argparse, base64, json, os, re, shutil, subprocess, sys, asyncio
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
MOTOR = RAIZ / "motor"
JOB = MOTOR / "public" / "job"


def carregar_env():
    env = RAIZ / ".env"
    if env.exists():
        for linha in env.read_text(encoding="utf-8").splitlines():
            if "=" in linha and not linha.strip().startswith("#"):
                k, v = linha.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"'))


def duracao_audio(caminho):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(caminho)],
                         capture_output=True, text=True).stdout.strip()
    return float(out or 0)


# ---------- vozes ----------
def voz_elevenlabs(texto, destino):
    import urllib.request
    chave = os.environ.get("ELEVENLABS_API_KEY")
    if not chave:
        raise RuntimeError("ELEVENLABS_API_KEY não encontrada no .env")
    voz = os.environ.get("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")
    corpo = json.dumps({
        "text": texto,
        "model_id": os.environ.get("ELEVENLABS_MODEL", "eleven_multilingual_v2"),
        "voice_settings": {"stability": 0.38, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True},
    }).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voz}/with-timestamps?output_format=mp3_44100_128",
        data=corpo, headers={"xi-api-key": chave, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        dados = json.loads(r.read())
    Path(destino).write_bytes(base64.b64decode(dados["audio_base64"]))
    al = dados.get("normalized_alignment") or dados["alignment"]
    chars, ini, fim = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    palavras, atual, s = [], "", None
    for ch, a, b in zip(chars, ini, fim):
        if ch.isspace():
            if atual:
                palavras.append({"w": atual, "s": s, "e": e_ant}); atual = ""
            continue
        if not atual:
            s = a
        atual += ch; e_ant = b
    if atual:
        palavras.append({"w": atual, "s": s, "e": e_ant})
    return palavras


def voz_edge(texto, destino):
    import edge_tts

    async def run():
        com = edge_tts.Communicate(texto, "pt-BR-AntonioNeural", rate="+6%", boundary="WordBoundary")
        palavras = []
        with open(destino, "wb") as f:
            async for ch in com.stream():
                if ch["type"] == "audio":
                    f.write(ch["data"])
                elif ch["type"] == "WordBoundary":
                    s = ch["offset"] / 1e7
                    palavras.append({"w": ch["text"], "s": s, "e": s + ch["duration"] / 1e7})
        return palavras
    return asyncio.run(run())


def voz_estimada(texto):
    palavras, t = [], 0.3
    for w in texto.split():
        d = 0.18 + 0.045 * len(w)
        palavras.append({"w": w, "s": t, "e": t + d}); t += d + (0.25 if re.search(r"[.!?]$", w) else 0.06)
    return palavras


# ---------- principal ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roteiro")
    ap.add_argument("--voz", default="elevenlabs", choices=["elevenlabs", "edge", "nenhuma"])
    ap.add_argument("--saida", default=None, help="caminho do mp4 final")
    args = ap.parse_args()
    carregar_env()

    spec = json.loads(Path(args.roteiro).read_text(encoding="utf-8"))
    nome = spec.get("nome", Path(args.roteiro).stem)
    cenas = spec["cenas"]
    shutil.rmtree(JOB, ignore_errors=True); JOB.mkdir(parents=True)

    # narração inteira de uma vez (fica mais fluida) + índice de onde começa cada cena
    textos = [c.get("narracao", "").strip() for c in cenas]
    texto = " ".join(t for t in textos if t)
    limites, n = [], 0
    for t in textos:
        limites.append(n); n += len(t.split())

    audio, palavras = None, []
    mp3 = JOB / "voz.mp3"
    if args.voz != "nenhuma" and texto:
        ordem = ["elevenlabs", "edge"] if args.voz == "elevenlabs" else ["edge"]
        for motor_voz in ordem:
            try:
                palavras = voz_elevenlabs(texto, mp3) if motor_voz == "elevenlabs" else voz_edge(texto, mp3)
                audio = "job/voz.mp3"; print(f"Voz: {motor_voz} ({len(palavras)} palavras)"); break
            except Exception as e:
                print(f"[aviso] voz {motor_voz} falhou: {e}")
    if not palavras:
        palavras = voz_estimada(texto); print("Voz: nenhuma (tempos estimados)")

    # tempos das cenas a partir das palavras
    fim_audio = duracao_audio(mp3) if audio else (palavras[-1]["e"] if palavras else 3)
    for i, c in enumerate(cenas):
        idx = limites[i]
        c["inicio"] = 0 if i == 0 else max(0, palavras[min(idx, len(palavras) - 1)]["s"] - 0.12)
    for i, c in enumerate(cenas):
        c["fim"] = cenas[i + 1]["inicio"] if i + 1 < len(cenas) else fim_audio + 0.9
        c.setdefault("modelo", "impacto")
        if c.get("imagem"):
            origem = RAIZ / "assets" / c["imagem"]
            destino = JOB / "img" / Path(c["imagem"]).name
            destino.parent.mkdir(exist_ok=True); shutil.copy(origem, destino)
            c["imagem"] = f"job/img/{destino.name}"
        c.pop("narracao", None)

    # garante que o motor tem as poses e marca atualizadas
    for pasta in ["sera", "marca", "fontes"]:
        if (RAIZ / "assets" / pasta).exists():
          shutil.copytree(RAIZ / "assets" / pasta, MOTOR / "public" / pasta, dirs_exist_ok=True)

    props = {"fps": 30, "duracao": cenas[-1]["fim"], "arroba": spec.get("arroba", "@seraphimtech_"),
             "audio": audio, "batida": "sfx/batida.mp3", "sfx": True, "palavras": palavras, "cenas": cenas}
    (JOB / "props.json").write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")

    saida = Path(args.saida).resolve() if args.saida else RAIZ / "entrega" / "videos" / f"{nome}.mp4"
    saida.parent.mkdir(parents=True, exist_ok=True)
    cmd = f'npx remotion render src/index.ts Seraphim "{saida}" --props=public/job/props.json --log=error'
    if os.environ.get("CHROME_PATH"):
        cmd += f' --browser-executable="{os.environ["CHROME_PATH"]}"'
    print("Editando no motor Remotion... (alguns minutos)")
    subprocess.run(cmd, cwd=MOTOR, shell=True, check=True)
    if spec.get("legenda"):
        saida.with_suffix(".txt").write_text(spec["legenda"], encoding="utf-8")
    print(f"Pronto: {saida} ({props['duracao']:.1f}s)")


if __name__ == "__main__":
    main()
