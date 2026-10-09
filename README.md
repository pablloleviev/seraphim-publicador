# Seraphim — Publicador automático

Publica no Instagram (@seraphimtech_) **24 horas, de graça**, usando o GitHub Actions.
Nada é publicado sem a sua aprovação no Telegram.

## Como funciona
1. Uma vez por semana você gera os posts no VS Code (projeto Seraphim-Conteudo) e coloca na **fila**.
2. A cada 15 minutos o GitHub verifica a fila. Quando chega o horário de um post, ele manda para o seu **Telegram** com os botões **✅ Publicar** e **❌ Pular**.
3. Tocou em ✅ → em até 15 minutos o post está no Instagram e o bot te avisa.

## Colocar posts na fila (no seu PC)
```
python scripts/enfileirar.py ..\Seraphim-Conteudo\entrega\carrosseis\NOME "2026-10-12 18:00"
python scripts/enfileirar.py ..\Seraphim-Conteudo\entrega\videos\NOME.mp4 "2026-10-13 12:00"
git add . && git commit -m "fila da semana" && git push
```
Ou, no Claude Code: *"coloca os conteúdos aprovados na fila do publicador para a semana"*.

## Segredos (configurar uma vez)
GitHub → este repositório → **Settings → Secrets and variables → Actions → New repository secret**:

| Nome | O que é |
|---|---|
| `TELEGRAM_TOKEN` | Token do bot criado no @BotFather |
| `TELEGRAM_CHAT_ID` | Seu ID no Telegram (o publicador mostra no log na primeira execução) |
| `IG_USER_ID` | ID da conta do Instagram na API da Meta |
| `IG_TOKEN` | Token de acesso da Página "Seraphim Tech" (sem validade, gerado a partir do token longo) |

## Arquivos
- `fila/` — posts aguardando (cada pasta = 1 post com `item.json` + imagens/vídeo)
- `estado.json` — o que já foi enviado/publicado (atualizado sozinho)
- `scripts/publicar.py` — o robô (roda no GitHub)
- `scripts/enfileirar.py` — coloca posts na fila (roda no seu PC)
- `.github/workflows/publicar.yml` — o agendamento a cada 15 minutos
