"""Vídeos do AutoFlow no PADRÃO OFICIAL da semana: motor "estilo" (motor/src/Estilo.tsx).

Referência: previas/semana/*.json (todos com "motor": "estilo") — os vídeos desta semana.
Identidade do produto: paleta "autoflow" (laranja #FF6A13), telas reais do sistema na cena "tela"
e o logo no fecho. Narração do Gemini com legenda palavra a palavra, como nos vídeos da semana.
Nada de preço, plano, teste com data, cliente ou resultado inventado.

Uso: python scripts/videos_autoflow.py          -> escreve previas/semana/*.json e pedidos/*.json
     (o workflow "Gerar vídeos" renderiza e põe na fila de aprovação)
"""
import json, sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ARROBA = "@seraphimbr_"
FIM = "\n\n"

VIDEOS = [
 dict(peca="V12", nome="do-caderno-ao-sistema", quando="2026-10-24 19:30", voz="masculina",
      titulo="Do caderno ao sistema", personalidade="elegante", legenda="palavra",
      cenas=[
       {"tipo": "objeto", "icone": "notebook-pen", "titulo": "Do caderno ao *sistema*",
        "narracao": "Toda oficina anota. No caderno, na planilha, num papel em cima da bancada."},
       {"tipo": "frase", "titulo": "Anotar é fácil. Difícil é *achar depois*.",
        "narracao": "Anotar é fácil. Difícil é achar depois, quando o cliente liga perguntando o que foi feito no carro dele."},
       {"tipo": "contraste", "antes": "Cada informação num lugar diferente", "depois": "Tudo num *lugar só*",
        "narracao": "O AutoFlow é um sistema de gestão feito para oficinas mecânicas."},
       {"tipo": "tela", "tela": "af/ordens_conteudo.png", "rotulo": "ORDENS DE SERVIÇO", "titulo": "Cada ordem no *quadro*",
        "narracao": "Cada ordem de serviço no quadro: pendente, em andamento, finalizado, entregue."},
       {"tipo": "tela", "tela": "af/historico_conteudo.png", "rotulo": "HISTÓRICO POR PLACA", "titulo": "E o histórico *pela placa*",
        "narracao": "E o histórico de cada carro pela placa, da primeira visita até hoje."},
       {"tipo": "fecho", "logo": "af/logo-icone.png", "titulo": "Sua oficina merece uma *gestão mais simples*",
        "cartoes": ["Teste gratuito para oficinas selecionadas", "Solicite acesso pelo direct"],
        "narracao": "Sua oficina merece uma gestão mais simples. O teste é gratuito para oficinas selecionadas: solicite acesso pelo direct."}],
      legenda_post="O caderno guarda muita coisa. O difícil é achar na hora certa.\n\nO AutoFlow é um sistema de gestão feito para oficinas mecânicas: as ordens de serviço num quadro e o histórico de cada carro pela placa.\n\nTeste gratuito para oficinas selecionadas. Solicite acesso pelo direct.",
      legenda_tiktok="Do caderno ao sistema: AutoFlow, gestão para oficinas mecânicas.",
      hashtags=["#autoflow", "#oficinamecanica", "#gestaoautomotiva", "#mecanica"]),
 dict(peca="V13", nome="um-dia-na-oficina", quando="2026-10-25 12:30", voz="feminina",
      titulo="Um dia na oficina", personalidade="dinamico", legenda="palavra",
      cenas=[
       {"tipo": "objeto", "icone": "clock", "titulo": "Um dia *na oficina*",
        "narracao": "Sete e quarenta e dois. O portão sobe e o dia começa."},
       {"tipo": "tela", "tela": "af/painel_conteudo.png", "rotulo": "PAINEL", "titulo": "O pátio *na tela*",
        "narracao": "No painel, o que entrou, o que está em andamento e o que já pode ser entregue."},
       {"tipo": "frase", "titulo": "Nove e quinze. Mais um *carro entra*.",
        "narracao": "Nove e quinze. Mais um carro entra."},
       {"tipo": "tela", "tela": "af/nova_os_painel.png", "dispositivo": "celular", "rotulo": "NOVA ORDEM", "titulo": "Uma ordem nova em *poucos campos*",
        "narracao": "Cliente, veículo, serviço e valor: a ordem nova já entra no quadro."},
       {"tipo": "tela", "tela": "af/celular_painel.png", "dispositivo": "celular", "rotulo": "NO CELULAR", "titulo": "Na mesa ou *no bolso*",
        "narracao": "E a oficina continua com você, na mesa ou no bolso."},
       {"tipo": "frase", "titulo": "Dezoito e vinte. O portão *desce*.",
        "narracao": "Dezoito e vinte. O portão desce com o dia inteiro registrado."},
       {"tipo": "fecho", "logo": "af/logo-icone.png", "titulo": "O AutoFlow acompanha o *dia da sua oficina*",
        "cartoes": ["Teste gratuito para oficinas selecionadas", "Solicite acesso pelo direct"],
        "narracao": "O AutoFlow acompanha o dia da sua oficina. Teste gratuito para oficinas selecionadas: solicite acesso pelo direct."}],
      legenda_post="Das sete e quarenta e dois às dezoito e vinte: um dia de oficina, do portão que sobe ao portão que desce.\n\nO AutoFlow é um sistema de gestão feito para oficinas mecânicas.\n\nTeste gratuito para oficinas selecionadas. Solicite acesso pelo direct.",
      legenda_tiktok="Um dia na oficina, com o AutoFlow.",
      hashtags=["#autoflow", "#oficinamecanica", "#gestaoautomotiva", "#rotina"]),
]


def escrever():
    (RAIZ / "pedidos").mkdir(exist_ok=True)
    (RAIZ / "previas/semana").mkdir(parents=True, exist_ok=True)
    for v in VIDEOS:
        pasta = f"{v['quando'].replace(' ', '_').replace(':', '')}_{v['nome']}"
        base = {"nome": v["nome"], "pasta": pasta, "motor": "estilo", "personalidade": v["personalidade"],
                "genero_voz": v["voz"], "estilo_legenda": v["legenda"], "paleta": "autoflow", "cenas": v["cenas"]}
        (RAIZ / "previas/semana" / f"{pasta}.json").write_text(json.dumps(base, ensure_ascii=False, indent=1), encoding="utf-8")
        tags = " ".join(v["hashtags"] + ["#seraphimbr"])
        pedido = dict(base, arroba=ARROBA, quando=v["quando"], titulo=v["titulo"], funil="topo", voz="gemini",
                      relancamento=v["peca"], legenda=v["legenda_post"] + FIM + tags,
                      legenda_tiktok=v["legenda_tiktok"] + FIM + " ".join(v["hashtags"][:3] + ["#seraphimbr"]))
        (RAIZ / "pedidos" / f"{v['nome']}.json").write_text(json.dumps(pedido, ensure_ascii=False, indent=1), encoding="utf-8")
        print("roteiro:", v["peca"], pasta, "| personalidade:", v["personalidade"], "| voz:", v["voz"])


if __name__ == "__main__":
    escrever()
