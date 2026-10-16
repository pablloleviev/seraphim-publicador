"""@ da marca num lugar só (marca.json). Ao trocar o nome do Instagram, mude apenas marca.json."""
import json
from pathlib import Path

_M = json.loads((Path(__file__).resolve().parent.parent / "marca.json").read_text(encoding="utf-8"))
USUARIO = _M["usuario"]
ARROBA = "@" + USUARIO
INSTAGRAM_URL = "https://instagram.com/" + USUARIO
