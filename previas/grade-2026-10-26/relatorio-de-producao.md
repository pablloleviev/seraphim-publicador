# Relatório de produção · Grade Seraphim + AutoFlow, 26/10 a 01/11/2026

**Status:** só prévias, aguardando aprovação humana. Nada foi publicado, agendado ou enfileirado. `fila/`, `pedidos/`, automações, site e materiais já aprovados não foram alterados.

## 1. Arquivos verificados (abertos e validados antes de qualquer peça)
| Arquivo | Resultado |
|---|---|
| `assets/pessoas/socio.jpg` | encontrado, 1254×1254 RGB, retrato frontal, fundo azul-marinho escuro, suéter marfim |
| `assets/pessoas/pabllo.png` | encontrado, 1024×1024 RGB, fundo preto, suéter preto |
| `assets/pessoas/pabllo_recorte.png` | encontrado, 1024×1024 RGBA (recorte antigo; ver seção 3) |
| `assets/autoflow/logo-oficial.jpg` | encontrado, 1200×540 |
| `assets/autoflow/logo-icone.png` | encontrado, 245×310 RGBA |
| `assets/autoflow/telas/` | 20 arquivos |
| `estilos/direcao-criativa.md`, `autoflow.md`, `texto-instagram.md` | lidos e aplicados |
| `previas/semana/` | 12 roteiros de referência |

Nenhum retrato estava ausente, então nenhuma peça foi bloqueada e nenhuma pessoa foi gerada por IA.

## 2. Comparação com a semana anterior
Comparado com `testes/previa_feed_semana.jpg` (19–25/10): a semana anterior era preto + dourado (e prata, rubi, esmeralda, violeta, cobre, gelo), com o Pabllo recortado entre blocos 3D flutuantes, esferas e ícones 3D, e capas de número grande. Nesta semana não há bloco 3D flutuante nem ícone 3D. A base é preto-tinta, azul elétrico, marfim e lavanda. Há diagrama de cartões e fios, papel de checklist, arco arquitetônico e tipografia sobre cor. Duas capas de Reel (Qui e Sáb) são tipográficas sobre preto, como algumas da semana passada, mas com outra paleta e outro movimento.

## 3. Tratamento dos retratos
- **Sócio** (`socio_recorte.png`): máscara por segmentação de pessoa (u2net_human_seg) + closed-form matting em resolução total + decontaminação de cor da borda. Ombros e mangas ficaram limpos. O cabelo cacheado tem uma borda levemente serrilhada se ampliado, então ele só aparece sobre fundo escuro, onde isso não é visível. Foto frontal: **não** foi possível fazer o "três quartos" pedido sem alterar a foto, então mantive frontal e à esquerda.
- **Pabllo** (`pabllo_recorte_final.png`): o recorte existente deixava contorno escuro sobre fundo claro. Refeito: matting fino na cabeça e máscara suave nos ombros (suéter preto sobre fundo preto não tem borda para o matting). Só aparece sobre fundo escuro ou lavanda difusa.
- Luz e sombra: sombra projetada de contato (sócio sobre a linha azul), sombra lavanda suave (Pabllo), vidro com desfoque de fundo sem glow. Sem borda branca, sem deformação, sem filtro pesado na pele.
- Nome e cargo: **não** foram usados, porque não estão confirmados nos materiais.
- Dupla de domingo: usei Pabllo + sócio porque as camadas funcionam (arco ao fundo, Pabllo à frente sobre faixa marfim). A pose é parecida nos dois (braços cruzados). Se achar forçado, a alternativa é Pabllo solo.

## 4. Peças e materiais usados
| Dia | Peça | Materiais | Tela real do AutoFlow? |
|---|---|---|---|
| Seg 26/10 | Reel 25 s | imagens de cena da oficina já existentes do AutoFlow (`motor/public/af/`), com grade azul; tela real no notebook | sim (Ordens de serviço, recorte de conteúdo) |
| Ter 27/10 | Carrossel 6 slides | gráficos de cartões e fios (nenhuma interface) | não |
| Qua 28/10 | Post | `socio.jpg` (recorte) | não |
| Qui 29/10 | Reel 19,6 s | colagem de caderno, planilha vazia, post-its, notificações abstratas, janelas abstratas; tela real no notebook | sim (mesma tela) |
| Sex 30/10 | Carrossel 7 slides | papel de checklist, sem pessoa | não |
| Sáb 31/10 | Reel 14 s | papel, mensagem, celular desfocado (gráficos abstratos) | não |
| Dom 01/11 | Post | `pabllo.png` e `socio.jpg` (recortes) | não |

Telas: usei apenas o recorte de conteúdo "Ordens de serviço", sem "Meu plano", "Teste grátis até 31/12" nem "Plano Pro · em teste". É uma captura real com dados de demonstração ("Oficina Modelo"), mostrada pequena, escurecida e sem destacar nenhuma função. Nada de interface foi redesenhado ou gerado.

## 5. Vídeo e som
- Composição nova `SinalVivo` (Remotion), 1080×1920, 30 fps, H.264 + AAC, margens seguras respeitadas (250 px topo, 340 px base).
- Sem narração: texto em tela palavra a palavra e som desenhado do zero (drone grave, cliques, pings, pancadas, whoosh, acorde final), com silêncios reais onde a grade pede pausa (Seg 6,4–7,2 s; Qui, notebook; Sáb 5,1–5,6 s).
- **Os Reels da Seraphim desta semana não usam o motor `Estilo` com narração.** A grade pede texto em tela e som seco, e o motor `Estilo` é guiado por locução. Se você preferir o `Estilo` com voz, refaço.

## 6. QA
- Ortografia e acentos conferidos nos textos e nas legendas. As quatro legendas têm um único CTA e 4 a 5 hashtags com `#seraphimbr`.
- Nenhum post usa "preto + glow apagado" como solução pronta. Cada peça tem formato, composição e tratamento diferentes.
- Nenhuma capacidade, cliente, depoimento, número ou métrica foi inventado.
- Não houve ridicularização de quem usa papel ou planilha.
- Conferência visual feita por folhas de quadros dos 3 Reels, dos 13 slides e das capas. Ainda **não foi feita revisão em celular real**.

## 7. Limitações e pontos de atenção
1. As cenas de oficina do Seg são imagens estáticas já existentes do AutoFlow (não são filmagem real) com movimento de câmera digital. Não há cena de mão fechando caderno nem de porta descendo. É o ponto mais fraco da semana. Para o nível pedido, o ideal seria filmar ou gerar essas cenas.
2. As cenas do Seg incluem pessoas genéricas (não são recortes e não são os fundadores).
3. Legenda de Seg: a frase "O ponto não é trabalhar menos por trabalhar menos. É não carregar sozinho…" segue o texto da grade, mas é o tique "não é X, é Y" que `texto-instagram.md` desaconselha. Legenda de Qua tem um travessão. Mantive os dois como estão na grade.
4. Texto do slide 6 de Ter ("Onde você colocaria mais clareza na sua rotina?") é diferente da pergunta da legenda ("Em que parte da sua operação você sente mais ruído hoje?"), como na grade. Cada peça mantém um CTA na legenda.
5. Stories: foram feitas as placas (1080×1920) e o trecho do Reel de segunda (`seg_2_trecho-do-reel.mp4`, 10 s). Os stickers interativos (enquete, caixa, quiz, lembrete) são nativos e entram na hora de agendar. `ter_2_resposta-modelo.jpg` é um **modelo**, e a resposta real só entra depois da sua aprovação, sem nome nem dados pessoais. O story de resultado do quiz de quinta depende dos votos reais, então ainda não existe.
6. Horários de postagem não foram definidos, porque a grade não os traz.

## 8. Arquivos
`feed-preview.jpg`, as 7 pastas por data (capa, slides ou `video.mp4`, `legenda.md/.txt`), `stories/`, `_trabalho/` (recortes). Scripts: `scripts/grade_1026_*.py`, composição `motor/src/SinalVivo.tsx`.
