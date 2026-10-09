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


def voz_edge(texto, destino, voz=None):
    import edge_tts
    voz = voz or os.environ.get("EDGE_VOICE", "pt-BR-ThalitaMultilingualNeural")

    async def run():
        com = edge_tts.Communicate(texto, voz, rate="+8%", boundary="WordBoundary")
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


# ---------- Gemini (Google) ----------
GEMINI_MODELOS = ["gemini-2.5-flash-preview-tts", "gemini-2.5-flash-tts", "gemini-2.5-pro-preview-tts"]


def voz_gemini(texto, destino):
    import urllib.request, urllib.error
    chave = os.environ.get("GEMINI_API_KEY")
    if not chave:
        raise RuntimeError("GEMINI_API_KEY não encontrada")
    estilo = os.environ.get("GEMINI_ESTILO",
        "Fale em português do Brasil, como um criador de conteúdo animado e confiante, ritmo rápido de Reels, "
        "natural e envolvente, enfatizando as palavras-chave")
    corpo = json.dumps({
        "contents": [{"parts": [{"text": f"{estilo}:\n\n{texto}"}]}],
        "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {
            "prebuiltVoiceConfig": {"voiceName": os.environ.get("GEMINI_VOZ", "Puck")}}}},
    }).encode()
    erro = None
    for modelo in GEMINI_MODELOS:
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent",
            data=corpo, headers={"x-goog-api-key": chave, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                dados = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            erro = f"{modelo}: {e.code} {e.read().decode()[:300]}"
    else:
        raise RuntimeError(erro)
    pcm = base64.b64decode(dados["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
    raw = Path(destino).with_suffix(".pcm"); raw.write_bytes(pcm)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", str(raw),
                    "-b:a", "160k", str(destino)], check=True)
    raw.unlink()
    return alinhar(texto, destino)


def alinhar(texto, audio):
    """Descobre quando cada palavra do roteiro é falada (ouvindo o áudio com Whisper)."""
    import difflib, unicodedata
    from faster_whisper import WhisperModel
    modelo = WhisperModel(os.environ.get("WHISPER_MODELO", "small"), device="cpu", compute_type="int8")
    segs, _ = modelo.transcribe(str(audio), language="pt", word_timestamps=True, vad_filter=False)
    ouvidas = [w for s in segs for w in s.words]
    norm = lambda w: re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", w.lower()).encode("ascii", "ignore").decode())
    roteiro = texto.split()
    a, b = [norm(w) for w in roteiro], [norm(w.word) for w in ouvidas]
    tempos = [None] * len(roteiro)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            w = ouvidas[blk.b + k]; tempos[blk.a + k] = (w.start, w.end)
    # preenche as que não casaram, interpolando entre vizinhas
    fim_total = ouvidas[-1].end if ouvidas else duracao_audio(audio)
    i = 0
    while i < len(tempos):
        if tempos[i] is None:
            j = i
            while j < len(tempos) and tempos[j] is None: j += 1
            ini = tempos[i - 1][1] if i > 0 else 0.0
            fim = tempos[j][0] if j < len(tempos) else fim_total
            passo = max(fim - ini, 0.05) / (j - i)
            for k in range(i, j): tempos[k] = (ini + passo * (k - i), ini + passo * (k - i + 1))
            i = j
        else:
            i += 1
    return [{"w": w, "s": t[0], "e": t[1]} for w, t in zip(roteiro, tempos)]


def tratar_audio(mp3):
    """Acabamento de estúdio: tira grave sujo, dá presença, comprime e nivela volume."""
    tmp = mp3.with_name("voz_tratada.mp3")
    filtro = ("highpass=f=80,equalizer=f=200:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1.2:g=3,"
              "equalizer=f=9000:t=h:w=1:g=2,acompressor=threshold=-18dB:ratio=3:attack=5:release=80:makeup=3,"
              "loudnorm=I=-14:TP=-1.5:LRA=7")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(mp3), "-af", filtro, "-ar", "44100", "-b:a", "192k", str(tmp)])
    if r.returncode == 0:
        tmp.replace(mp3)


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
    ap.add_argument("--voz", default="elevenlabs", choices=["elevenlabs", "gemini", "edge", "edge-antonio", "nenhuma"])
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
        ordem = {"elevenlabs": ["elevenlabs", "gemini", "edge"], "gemini": ["gemini", "edge"]}.get(args.voz, [args.voz])
        funcs = {"elevenlabs": voz_elevenlabs, "gemini": voz_gemini, "edge": voz_edge,
                 "edge-antonio": lambda t, d: voz_edge(t, d, "pt-BR-AntonioNeural")}
        for motor_voz in ordem:
            try:
                palavras = funcs[motor_voz](texto, mp3)
                if not palavras:
                    palavras = alinhar(texto, mp3)
                tratar_audio(mp3)
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
