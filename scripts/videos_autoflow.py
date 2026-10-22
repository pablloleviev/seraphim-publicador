"""Vídeos do AutoFlow no NOSSO estilo de edição (motor de cortes), com a identidade do AutoFlow.

- Formato de edição "autoflow" (laranja #FF6A13 sobre #0E0E10, Stack Sans + Anton nas palavras de impacto).
- Só material oficial: cenas de oficina (assets/autoflow/cenas) e telas reais (assets/autoflow/telas).
- Narração do Gemini: masculina no V12, feminina no V13 (se cair para a voz reserva, o revoz refaz depois).
- Nada de preço, plano, teste com data, cliente ou resultado inventado.

Uso: python scripts/videos_autoflow.py        -> monta as telas 9:16 e escreve pedidos/*.json
     (o workflow "Gerar vídeos" renderiza e põe na fila de aprovação)
"""
import json, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TELAS = RAIZ / "assets/autoflow/telas"
CENAS = RAIZ / "assets/autoflow/cenas"
SAIDA = RAIZ / "assets/autoflow/telas-9x16"
ARROBA = "@seraphimbr_"
FIM = "\n\n"

# tela real -> imagem 9:16 pronta para entrar como cena (quanto da largura a tela ocupa, e de onde recortar)
MONTAGENS = [
 dict(saida="tela-painel.png", tela="painel_conteudo.png", largura=0.82, corte=(0, 0, 0.55, 0.70)),
 dict(saida="tela-ordens.png", tela="ordens_conteudo.png", largura=0.82, corte=(0, 0, 0.62, 1)),
 dict(saida="tela-historico.png", tela="historico_conteudo.png", largura=0.82, corte=(0, 0, 0.78, 0.95)),
 dict(saida="tela-nova-os.png", tela="nova_os_painel.png", largura=0.70, corte=(0, 0, 1, 1)),
]


def montar_telas():
    from PIL import Image, ImageDraw, ImageFilter
    SAIDA.mkdir(parents=True, exist_ok=True)
    L, A = 1080, 1920
    for m in MONTAGENS:
        fundo = Image.new("RGB", (L, A), "#0E0E10")
        brilho = Image.new("RGB", (L, A), "#0E0E10")
        d = ImageDraw.Draw(brilho)
        d.ellipse((-260, A - 1180, L + 260, A + 240), fill="#3d1c08")
        d.ellipse((L - 520, -360, L + 420, 420), fill="#241208")
        fundo = Image.blend(fundo, brilho.filter(ImageFilter.GaussianBlur(170)), 0.9)

        tela = Image.open(TELAS / m["tela"]).convert("RGB")
        x0, y0, x1, y1 = m["corte"]
        tela = tela.crop((int(x0 * tela.width), int(y0 * tela.height), int(x1 * tela.width), int(y1 * tela.height)))
        larg = int(L * m["largura"])
        tela = tela.resize((larg, max(1, round(larg * tela.height / tela.width))), Image.LANCZOS)
        if tela.height > A * 0.66:
            alt = int(A * 0.66)
            tela = tela.resize((max(1, round(alt * tela.width / tela.height)), alt), Image.LANCZOS)

        cantos = Image.new("L", tela.size, 0)
        ImageDraw.Draw(cantos).rounded_rectangle((0, 0, tela.width - 1, tela.height - 1), radius=34, fill=255)
        pos = ((L - tela.width) // 2, (A - tela.height) // 2)
        sombra = Image.new("RGB", (L, A), "#0E0E10")
        ImageDraw.Draw(sombra).rounded_rectangle((pos[0] - 6, pos[1] + 18, pos[0] + tela.width + 6, pos[1] + tela.height + 40), radius=44, fill="#000000")
        fundo = Image.blend(fundo, sombra.filter(ImageFilter.GaussianBlur(60)), 0.55)

        borda = Image.new("RGB", tela.size, "#FF6A13")
        ImageDraw.Draw(borda).rounded_rectangle((2, 2, tela.width - 3, tela.height - 3), radius=32, fill=None, outline="#FF6A13", width=0)
        fundo.paste(borda, pos, cantos)
        fundo.paste(tela, pos, cantos)
        ImageDraw.Draw(fundo).rounded_rectangle((pos[0], pos[1], pos[0] + tela.width, pos[1] + tela.height), radius=34, outline="#FF6A13", width=3)
        fundo.save(SAIDA / m["saida"], quality=95)
        print("tela:", m["saida"], tela.size)


VIDEOS = [
 dict(peca="V12", nome="do-caderno-ao-sistema", quando="2026-10-24 19:30", voz="masculina", numero=12,
      titulo="Do caderno ao sistema",
      cenas=[
       {"tipo": "palavra", "texto": "CADÊ|AQUELA|*ORDEM?*", "destaque": "ORDEM",
        "narracao": "Cadê aquela ordem de serviço?"},
       {"tipo": "foto", "imagem": "autoflow/cenas/n-recepcionista-folheando.png", "tom": "normal",
        "narracao": "Tá no caderno, na memória de quem atendeu, ou num papel que sumiu."},
       {"tipo": "foto", "imagem": "autoflow/cenas/n-celular-tocando.png", "tom": "normal",
        "narracao": "Aí o cliente liga perguntando o que foi feito no carro dele da última vez."},
       {"tipo": "digitando", "topo": "AUTOFLOW", "texto": "UM LUGAR SÓ",
        "narracao": "O AutoFlow é um sistema de gestão feito para oficinas mecânicas."},
       {"tipo": "foto", "imagem": "autoflow/telas-9x16/tela-ordens.png", "tom": "normal",
        "narracao": "Cada ordem no quadro: pendente, em andamento, finalizado, entregue."},
       {"tipo": "foto", "imagem": "autoflow/telas-9x16/tela-historico.png", "tom": "normal",
        "narracao": "E o histórico de cada carro pela placa, da primeira visita até hoje."},
       {"tipo": "cta", "texto": "SUA OFICINA MERECE UMA|*GESTÃO MAIS SIMPLES*", "apoio": "Solicite acesso gratuito",
        "marca": "af/logo-icone.png", "funil": "fundo",
        "narracao": "Sua oficina merece uma gestão mais simples. Solicite acesso gratuito pelo direct."}],
      legenda="O caderno guarda muita coisa. O difícil é achar na hora certa.\n\nO AutoFlow é um sistema de gestão feito para oficinas mecânicas: as ordens de serviço num quadro e o histórico de cada carro pela placa.\n\nTeste gratuito para oficinas selecionadas. Solicite acesso pelo direct.",
      legenda_tiktok="Do caderno ao sistema: AutoFlow, gestão para oficinas mecânicas.",
      hashtags=["#autoflow", "#oficinamecanica", "#gestaoautomotiva", "#mecanica"]),
 dict(peca="V13", nome="um-dia-na-oficina", quando="2026-10-25 12:30", voz="feminina", numero=13,
      titulo="Um dia na oficina",
      cenas=[
       {"tipo": "palavra", "texto": "UM DIA|*NA OFICINA*", "destaque": "NA OFICINA",
        "narracao": "Um dia na oficina."},
       {"tipo": "foto", "imagem": "autoflow/cenas/n-cadeado.png", "tom": "normal", "texto": "07:42",
        "narracao": "Sete e quarenta e dois: o portão sobe."},
       {"tipo": "foto", "imagem": "autoflow/telas-9x16/tela-painel.png", "tom": "normal",
        "narracao": "O dia começa com o pátio na tela: o que entrou e o que está em andamento."},
       {"tipo": "foto", "imagem": "autoflow/cenas/n-carro-entrando.png", "tom": "normal", "texto": "09:15",
        "narracao": "Nove e quinze: mais um carro entra."},
       {"tipo": "foto", "imagem": "autoflow/telas-9x16/tela-nova-os.png", "tom": "normal",
        "narracao": "Nova ordem de serviço: cliente, veículo, serviço e valor."},
       {"tipo": "foto", "imagem": "autoflow/cenas/n-elevador.png", "tom": "normal", "texto": "13:40",
        "narracao": "Treze e quarenta: a oficina no ritmo dela, e tudo seguindo registrado."},
       {"tipo": "foto", "imagem": "autoflow/cenas/n-silhueta-portao.png", "tom": "normal", "texto": "18:20",
        "narracao": "Dezoito e vinte: o portão desce com o dia inteiro anotado."},
       {"tipo": "cta", "texto": "TESTE GRATUITO PARA|*OFICINAS SELECIONADAS*", "apoio": "Solicite acesso pelo direct",
        "marca": "af/logo-icone.png", "funil": "fundo",
        "narracao": "Teste gratuito para oficinas selecionadas. Solicite acesso pelo direct."}],
      legenda="Das sete e quarenta e dois às dezoito e vinte: um dia de oficina, do portão que sobe ao portão que desce.\n\nO AutoFlow é um sistema de gestão feito para oficinas mecânicas.\n\nTeste gratuito para oficinas selecionadas. Solicite acesso pelo direct.",
      legenda_tiktok="Um dia na oficina, com o AutoFlow.",
      hashtags=["#autoflow", "#oficinamecanica", "#gestaoautomotiva", "#rotina"]),
]


def pedidos():
    (RAIZ / "pedidos").mkdir(exist_ok=True)
    for v in VIDEOS:
        tags = " ".join(v["hashtags"] + ["#seraphimbr"])
        spec = {"nome": v["nome"], "arroba": ARROBA, "quando": v["quando"], "cenas": v["cenas"], "motor": "cortes",
                "formato": "autoflow", "titulo": v["titulo"], "numero": v["numero"], "funil": "topo",
                "genero_voz": v["voz"], "voz": "gemini", "relancamento": v["peca"],
                "legenda": v["legenda"] + FIM + tags,
                "legenda_tiktok": v["legenda_tiktok"] + FIM + " ".join(v["hashtags"][:3] + ["#seraphimbr"])}
        (RAIZ / "pedidos" / f"{v['nome']}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
        print("pedido:", v["peca"], v["nome"], v["voz"])


if __name__ == "__main__":
    if sys.argv[1:2] != ["pedidos"]:
        montar_telas()
    pedidos()
