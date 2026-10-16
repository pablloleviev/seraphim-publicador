"""Gera amostras de capas com imagem real/IA em testes/ingredientes (para conferir a qualidade)."""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import capa, ingredientes
O = Path(__file__).resolve().parent.parent / "testes" / "ingredientes"; O.mkdir(parents=True, exist_ok=True)
casos = [
    ("Sua oficina perde *cliente* no WhatsApp", "gestão", "foto", "mechanic in dark garage looking at a glowing smartphone, car on lift behind, warm rim light", "mechanic smartphone garage"),
    ("O *orçamento* que ninguém responde", "vendas", "recorte", "crumpled paper invoice on a workbench next to car keys, single warm lamp", "invoice desk"),
    ("3 automações que pagam a *mensalidade*", "automação", "vidro", "futuristic golden circuit gears inside a dark car engine, macro shot", "car engine dark"),
    ("Esse carro ficou *parado 9 dias*", "caso real", "polaroid", "a dusty car waiting alone in a dim workshop bay, calendar on the wall", "old car garage"),
]
its = []
for i, (t, r, m, cena, busca) in enumerate(casos):
    img = ingredientes.imagem_ia(cena, O / f"img{i}.jpg", "4:5") if i % 2 == 0 else ingredientes.foto(busca, O / f"img{i}.jpg")
    its.append({"titulo": t, "rotulo": r, "modelo": m, "imagem": str(img or ""), "modo": "carrossel", "saida": O / f"capa{i}_{m}.jpg"})
asyncio.run(capa.gerar_varias(its))
print("ok", [str(i["imagem"]) for i in its])
