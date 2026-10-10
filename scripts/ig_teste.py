"""Testa a chave do Instagram: conta, publicação recente e leitura de comentários."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import comentarios as c
out = []
try:
    me = c._req("GET", "me?fields=user_id,username")
    out.append(f"Conta: @{me.get('username')}")
    mid = c._req("GET", "me/media?fields=id,caption,timestamp&limit=3")
    for m in mid.get("data", []):
        try:
            cm = c._req("GET", f"{m['id']}/comments?fields=id,text,username&limit=5")
            out.append(f"Post {m['id']} ({m.get('timestamp')}): {len(cm.get('data', []))} comentário(s) lidos ✓")
        except RuntimeError as e:
            out.append(f"Post {m['id']}: ERRO ao ler comentários: {e}")
except RuntimeError as e:
    out.append(f"ERRO: {e}")
print("\n".join(out))
open("ig_teste_log.txt", "w").write("\n".join(out) + "\n")
