"""
Roda no GitHub Actions: transforma cada roteiro em pedidos/*.json num vídeo pronto
e coloca na fila de aprovação (fila/<data>_<nome>/video.mp4 + item.json).

Campos extras do roteiro (além dos de fazer_video.py):
  "quando": "2026-10-12 18:00"   (horário de Brasília; se faltar, vai para aprovação na hora)
  "voz": "elevenlabs" | "gemini" | "edge" | "edge-antonio"  (padrão: a melhor com chave disponível)
  "genero_voz": "masculina" | "feminina"  (voz do Gemini; padrão masculina)
  "genero_voz": "masculina" | "feminina"   (padrão: masculina)
  "amostra": true                 (não vai para a fila; fica em amostras/ para comparar)
"""
import json, os, subprocess, sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BRT = timezone(timedelta(hours=-3))

for pedido in sorted((RAIZ / "pedidos").glob("*.json")):
    spec = json.loads(pedido.read_text(encoding="utf-8"))
    nome = spec.get("nome", pedido.stem)
    quando = datetime.strptime(spec["quando"], "%Y-%m-%d %H:%M") if spec.get("quando") else datetime.now(BRT).replace(tzinfo=None)
    amostra = spec.get("amostra", False)
    destino = (RAIZ / "amostras" / nome) if amostra else RAIZ / "fila" / f"{quando:%Y-%m-%d_%H%M}_{nome}"
    voz = spec.get("voz") or ("gemini" if os.environ.get("GEMINI_API_KEY") else "elevenlabs" if os.environ.get("ELEVENLABS_API_KEY") else "edge")
    print(f"=== {nome} (voz {voz}) ===", flush=True)
    r = subprocess.run([sys.executable, str(RAIZ / "scripts" / "fazer_video.py"), str(pedido),
                        "--voz", voz, "--saida", str(destino / "video.mp4")], capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-3000:], flush=True)
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "log.txt").write_text(r.stdout[-3000:] + "\n" + r.stderr[-3000:], encoding="utf-8")
    if r.returncode != 0:
        print(f"[erro] {nome} falhou; o pedido fica para a próxima tentativa"); continue
    if amostra:
        pedido.unlink(); print(f"Amostra pronta: amostras/{nome}/video.mp4"); continue
    (destino / "item.json").write_text(json.dumps({
        "tipo": "reels", "legenda": spec.get("legenda", ""),
        "quando": quando.strftime("%Y-%m-%dT%H:%M:00-03:00")}, ensure_ascii=False, indent=2), encoding="utf-8")
    txt = destino / "video.txt"
    if txt.exists(): txt.unlink()
    pedido.unlink()
    print(f"Na fila: {destino.name}")
