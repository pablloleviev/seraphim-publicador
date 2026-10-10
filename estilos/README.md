# Manual de edição da Seraphim

Cada formato tem o SEU manual. Eles não se misturam.

| Arquivo | Para quê | Status |
|---|---|---|
| `cortes.md` | Vídeos curtos verticais (Reels, TikTok, Shorts) | ✅ em uso pelo sistema automático |
| `carrosseis.md` | Carrosséis do Instagram | ✅ em uso pelo sistema automático |
| `youtube-longo.md` | Vídeos longos horizontais do YouTube | ⏸️ rascunho (YouTube em standby) |

## Como o manual vira vídeo
O planejador automático (`scripts/planejar.py`) lê `cortes.md` e `carrosseis.md` TODO DIA antes de escrever os roteiros.
Mudou uma regra aqui → o conteúdo do dia seguinte já segue a regra nova.
As regras visuais que dependem de código (animações, fontes, efeitos) são aplicadas no motor (`motor/`) e no `scripts/carrossel.py`.

## Como alimentar com novas referências
1. Pabllo manda a referência (link de canal/vídeo/perfil, print, vídeo) no chat ou na pasta do Drive com o nome começando por `ref-corte`, `ref-youtube` ou `ref-carrossel`.
2. A referência é registrada em `referencias/<formato>/referencias.md` com: link, o que copiar (técnica), o que NÃO copiar.
3. Só o que o Pabllo aprovar vira regra no manual (seção "Regras aprovadas" + "Evolução").
4. Enquanto não houver novas referências aprovadas, o padrão atual continua igual.

## Regra de ouro
Referência ensina TÉCNICA (ritmo, estrutura, tipo de corte), nunca se copia personagem, arte, marca ou texto de outro criador.
