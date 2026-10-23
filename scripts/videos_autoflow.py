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
 dict(saida="tela-painel.png", tela="painel_conteudo.png", largura=0.92, corte=(0, 0, 1, 0.97)),
 dict(saida="tela-ordens.png", tela="ordens_conteudo.png", largura=0.86, corte=(0, 0, 0.74, 1)),
 dict(saida="tela-historico.png", tela="historico_conteudo.png", largura=0.92, corte=(0, 0, 1, 0.95)),
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


CAPAS = {
 "do-caderno-ao-sistema": dict(foto="n-caderno-notebook.png", rotulo="AUTOFLOW", titulo="Do caderno|ao *sistema*", pos="center 45%"),
 "um-dia-na-oficina": dict(foto="n-silhueta-portao.png", rotulo="UM DIA NA OFICINA", titulo="Das 7h42|às *18h20*", pos="center 40%"),
}


def capas(pastas: dict):
    """Capa 9:16 de cada vídeo (a do Reels e o 1º quadro do TikTok), na identidade do AutoFlow."""
    import asyncio, io, re
    from PIL import Image
    from playwright.async_api import async_playwright
    fontes = (RAIZ / "motor/public/fontes").as_uri()
    logo = (RAIZ / "assets/autoflow/logo-icone.png").as_uri()

    async def gerar():
        async with async_playwright() as p:
            nav = await p.chromium.launch()
            for nome, destino in pastas.items():
                d = CAPAS[nome]
                img = (CENAS / d["foto"]).as_uri()
                titulo = re.sub(r"\*(.+?)\*", r'<span style="color:#FF6A13">\1</span>', d["titulo"]).replace("|", "<br>")
                html = f"""<html><head><meta charset="utf-8"><style>
                @font-face{{font-family:SH;font-weight:700;src:url({fontes}/stack-sans-headline-latin-700-normal.woff2)}}
                @font-face{{font-family:ST;font-weight:500;src:url({fontes}/stack-sans-text-latin-500-normal.woff2)}}
                *{{margin:0;box-sizing:border-box}} body{{width:1080px;height:1920px;position:relative;background:#0E0E10;overflow:hidden}}
                .f{{position:absolute;inset:0;background:url({img}) center/cover;background-position:{d['pos']}}}
                .v{{position:absolute;inset:0;background:linear-gradient(180deg,rgba(14,14,16,.6),rgba(14,14,16,.05) 32%,rgba(14,14,16,.9) 72%,#0E0E10)}}
                .m{{position:absolute;left:84px;top:96px;display:flex;align-items:center;gap:18px;font:700 34px SH;color:#F4F2EC}}
                .m img{{width:70px;height:70px;border-radius:18px}}
                .r{{font:700 30px SH;letter-spacing:5px;color:#FF6A13;margin-bottom:26px}}
                h1{{font:700 108px/1.02 SH;color:#F4F2EC;letter-spacing:-3px}}
                .c{{position:absolute;left:84px;right:84px;bottom:420px}}</style></head>
                <body><div class="f"></div><div class="v"></div>
                <div class="m"><img src="{logo}">AutoFlow</div>
                <div class="c"><div class="r">{d['rotulo']}</div><h1>{titulo}</h1></div></body></html>"""
                pg = await nav.new_page(viewport={"width": 1080, "height": 1920})
                tmp = RAIZ / "_capa_af.html"; tmp.write_text(html, encoding="utf-8")
                await pg.goto(tmp.as_uri()); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(300)
                Image.open(io.BytesIO(await pg.screenshot())).convert("RGB").save(destino / "capa.jpg", quality=93)
                await pg.close(); tmp.unlink()
                print("capa:", destino.name)
            await nav.close()
    asyncio.run(gerar())


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


def pasta_na_fila(v: dict) -> Path:
    return RAIZ / "fila" / f"{v['quando'].replace(' ', '_').replace(':', '')}_{v['nome']}"


if __name__ == "__main__":
    o = sys.argv[1] if len(sys.argv) > 1 else "tudo"
    if o == "capas":          # capa do Reels + 1º quadro do TikTok, depois que o vídeo já está na fila
        import capa_no_video
        destinos = {v["nome"]: pasta_na_fila(v) for v in VIDEOS if pasta_na_fila(v).exists()}
        capas(destinos)
        for d in destinos.values():
            (d / "video_tiktok.mp4").unlink(missing_ok=True)
            print("tiktok:", capa_no_video.fazer(d))
        sys.exit()
    if o != "pedidos":
        montar_telas()
    pedidos()
