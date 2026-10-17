"""Manda imagens para o Figma (URLs de upload do MCP do Figma, válidas por 10 min).
ITENS (env, JSON): [{"u": submitUrl, "f": "caminho/no/repo.jpg"} | {"u": submitUrl, "busca": "termos em inglês", "nome": "..."}]"""
import json, os, subprocess, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
import ingredientes

RAIZ = Path(__file__).resolve().parent.parent
for it in json.loads(os.environ["ITENS"]):
    if it.get("f"):
        arq = RAIZ / it["f"]
    else:
        arq = Path(tempfile.mkdtemp()) / f"{it.get('nome', 'foto')}.jpg"
        if not ingredientes.foto(it["busca"], arq, it.get("orient", "vertical")):
            print("sem foto:", it["busca"]); continue
    r = subprocess.run(["curl", "-sS", "-m", "60", "-F", f"file=@{arq}", it["u"]], capture_output=True, text=True)
    print(arq.name, "->", r.stdout[:200], r.stderr[:200])
