# PROMPT — PRODUÇÃO DOS VÍDEOS AUTOFLOW V2 E V3 (SERAPHIM)

Você vai assumir a produção de dois vídeos de lançamento do **AutoFlow**, o sistema de gestão para oficinas mecânicas criado pela **Seraphim** (empresa de tecnologia de Brasília). Leia tudo antes de começar. Trabalhe em português do Brasil.

---

## 1. CONTEXTO EM UMA FRASE
A Seraphim já tem uma identidade audiovisual aprovada. O V1 do AutoFlow ("Apresentamos o AutoFlow") também está aprovado. O V2 foi **reprovado** e precisa de um conceito novo. O V3 foi o preferido, mas precisa **subir muito de nível**. Os dois precisam ser **vídeos de verdade, com movimento filmado** (gerado no Higgsfield), e não montagens de fotos com zoom.

---

## 2. MATERIAIS (repositório GitHub `pablloleviev/seraphim-publicador`)
- `estilos/direcao-criativa.md` — diretriz criativa permanente da Seraphim (essência x liberdade de execução, grade como composição, revisão obrigatória).
- `estilos/autoflow.md` — ficha do produto, regras comerciais e de tipografia.
- `motor/src/Estilo.tsx` — **motor de edição aprovado da Seraphim** (Remotion). É a referência concreta do estilo: personalidades de ritmo, câmeras, transições, legendas, paletas.
- `motor/src/AutoFlowV1.tsx` — V1 aprovado (referência de qualidade e de revelação do produto).
- `motor/src/AutoFlowV2.tsx`, `AutoFlowV3.tsx`, `AutoFlowKit.tsx` — versões anteriores (reprovada / a melhorar).
- `previas/autoflow/` — MP4 finais anteriores (V1 aprovado; V2 e V3 para comparação — **não apagar**).
- `assets/autoflow/telas/` — **capturas reais** do sistema (desktop e celular) e recortes limpos:
  `painel_conteudo.png`, `ordens_conteudo.png`, `historico_conteudo.png`, `nova_os_painel.png`, `celular_painel.png`, `mobile-1.png` (Ordens no celular).
- `assets/autoflow/logo-icone.png` (fundo escuro) e `logo-icone-claro.png` (fundo claro) — logo oficial.
- `assets/autoflow/cenas/` — imagens-chave já geradas no Higgsfield (Soul Cinema, 9:16): podem servir de **primeiro quadro** para gerar vídeo (image-to-video).
- `voz_saida/autoflow-v2*/` — narração anterior (voz Gemini "Puck", aprovada como voz da marca).
- `musica/` — trilhas livres (licença Pixabay) organizadas por clima, com `indice.json` (duração, LUFS, ponto de pico).
- `motor/public/sfx/` — efeitos (whoosh, impacto, clique, tic, pop, batida).
- `scripts/trilha_autoflow.py` — montagem de trilha com ducking sob a voz.
- `.github/workflows/voz-linhas.yml` + `voz_pedidos/` — gera narração por linha no GitHub Actions (commit de um JSON em `voz_pedidos/`).

---

## 3. A IDENTIDADE AUDIOVISUAL DA SERAPHIM (NÃO PODE SE PERDER)
O que caracteriza o estilo aprovado (ver `Estilo.tsx` e `direcao-criativa.md`):
- **Ritmo com intenção:** alternância entre trechos rápidos e respiros contemplativos; acelerações e desacelerações marcadas, nunca ritmo uniforme.
- **Câmera viva:** empurrar, afastar, deriva lateral, inclinação, leve tremor, parada seca.
- **Transições criativas e motivadas:** chicote (whip pan), zoom, corte seco, flash, máscara, vazamento de luz, desfoque, deslize — cada corte acompanha um movimento ou uma batida.
- **Sound design colado na imagem:** whoosh, impacto, clique e tique sincronizados aos cortes; trilha que conduz a emoção, com silêncio usado como recurso.
- **Tipografia em movimento:** frases curtas, palavra a palavra, com destaque de cor em uma palavra-chave; legendas estilo karaokê quando há narração.
- **Acabamento de cinema:** luz lateral, profundidade de campo, partículas/poeira no feixe de luz, grão de filme, vinheta, objetos e ícones 3D quando ajudam.
- **Cor:** a paleta do AutoFlow é **laranja #FF6A13 sobre fundo escuro #0E0E10**; o dourado da Seraphim aparece como assinatura discreta. Colorização quente e profissional.
- **Coerência, não repetição:** cada vídeo tem estrutura própria, mas é reconhecível como Seraphim.

A referência da Apple serve para **elevar** isso (minimalismo, close-ups de produto, reflexos, revelações limpas), **não para substituir** a assinatura da Seraphim.

---

## 4. REGRAS INEGOCIÁVEIS
1. **Interface real:** nenhuma IA pode inventar ou redesenhar telas do AutoFlow. A interface entra **só** pela composição das capturas reais em notebook/monitor/celular, com perspectiva, reflexo e luz coerentes. Em cenas geradas, telas ficam desfocadas, de lado ou fora de quadro; a demonstração nítida é feita numa tomada separada e controlada.
2. **Proibido mostrar:** banner "Teste grátis até 31/12", "Plano Pro · em teste", tela "Meu plano", comparação Básico/Pro/Premium, preços, dados reais de clientes, funcionalidades não confirmadas.
3. **Comercial (modelo inicial):** plano único, preço não definido, teste gratuito por **acesso qualificado**. CTAs permitidos: "Conheça o AutoFlow", "Sua oficina merece uma gestão mais simples", "Solicite acesso gratuito", "Teste gratuito para oficinas selecionadas. Solicite acesso pelo direct." Nada de "crie sua conta agora", prazos, vagas, depoimentos, clientes ou resultados inventados.
4. **Tipografia:** **Stack Sans** (Headline para títulos, Text para apoio) — arquivos em `motor/public/fontes/stack-sans-*.woff2`.
5. **Não ridicularizar** quem usa papel.
6. **Formato:** 9:16, 1080×1920, H.264 + AAC, áreas seguras (texto fora dos 250 px do topo e 340 px da base), sem marca d'água, sem quadro preto/silêncio acidental.
7. **Não alterar** a grade de publicações, o site em produção, as automações do repositório nem materiais aprovados. **Não publicar nada.** Cada vídeo será aprovado individualmente pelo dono no Telegram, depois.
8. A foto do sócio (`assets/pessoas/socio.jpg`) **não pode ser usada**.

---

## 5. HIGGSFIELD — VÍDEO DE VERDADE, COM REGRA FINANCEIRA ABSOLUTA
- Use os créditos **já existentes** na conta do Higgsfield para gerar **cenas de vídeo** (image-to-video ou text-to-video), priorizando: mecânicos trabalhando, dono caminhando pela oficina, atendimento na recepção, pessoas usando notebook/computador/celular (tela fora de quadro), mãos e ferramentas em movimento, câmera se deslocando pelo ambiente.
- **Proibido:** comprar créditos, assinar ou fazer upgrade de plano, cadastrar cartão, ativar recarga automática, gerar qualquer cobrança.
- **Atenção — impedimento já identificado:** na última verificação (20/10/2026) a conta estava no **plano Free**, com cerca de **47 créditos** e **sem forma de pagamento cadastrada**. Nesse plano, **a geração de vídeo estava bloqueada** (Kling 3.0 Turbo, Kling 2.5 Turbo e Higgsfield Turbo abriam a tela de assinatura ao clicar em gerar). Só a geração de imagem (Soul Cinema, 0,125 crédito) funcionava. Também foram bloqueados: Nano Banana, referência de personagem com texto e mais de 1 geração simultânea.
- **Portanto:** antes de produzir, verifique na conta se a geração de vídeo está liberada. **Se continuar bloqueada, pare e informe o dono** com clareza: o que foi testado, qual tela apareceu e qual seria a solução (decisão dele). **Não substitua silenciosamente vídeo por fotos animadas.**
- Se o vídeo estiver liberado: escolha o modelo pela melhor relação qualidade/crédito (verifique o custo exibido no botão antes de cada geração), gere a partir das imagens-chave existentes ou de novas, revise cada clipe antes de usar, reserve ~20% do saldo para refazer defeitos e informe o saldo inicial e final.
- **Continuidade de personagem:** o mesmo dono/gestor deve ser a mesma pessoa em todo o vídeo. Se a ferramenta não garantir isso, filme-o de costas, mãos, silhueta ou em planos onde o rosto não decide.

---

## 6. V2 — "DO CADERNO AO SISTEMA" (REFAZER O CONCEITO)
O V2 anterior foi reprovado por ser genérico (papel x tecnologia) e por parecer slide. Crie uma **história** que gere identificação em quem administra oficina.

Direção sugerida (pode melhorar, mantendo a verdade):
- **Gancho (0–3 s):** um momento real e tenso do dia: o telefone toca, um cliente pergunta "o que foi feito no meu carro da última vez?". Close nas mãos folheando o caderno, páginas passando rápido, som de papel sincronizado ao ritmo.
- **Identificação (3–14 s):** a rotina vista com respeito: o caderno cheio de anos de trabalho, o mural de ordens, o pátio em movimento, o dono olhando o relógio enquanto procura. Cortes acompanhando o movimento das mãos e das páginas.
- **Virada (≈14–17 s):** a escrita à mão da placa **vira** — por transição motivada (match cut, máscara, luz) — o campo de placa da tela real **Histórico por placa**. Silêncio curto antes, batida na entrada.
- **Revelação do produto (17–32 s):** notebook ou monitor com as telas reais (Histórico por placa → quadro de Ordens), close-ups de produto, reflexos, luz laranja controlada. Narração natural.
- **Fecho:** o caderno é fechado com carinho ao lado do notebook aberto; logo oficial e **"Sua oficina merece uma gestão mais simples."**
- **Narração:** voz sintética profissional em PT-BR (a voz "Puck" do Gemini já foi aprovada), calma e segura, frases curtas. Sem prometer resultados ("em segundos", "economize X") — só mostrar.

## 7. V3 — "UM DIA NA OFICINA" (EVOLUIR O QUE FUNCIONOU)
O que funcionou e deve ficar: o **relógio narrativo** (07:42 → 09:15 → 13:40 → 18:20) em Stack Sans grande, a luz mudando ao longo do dia (manhã fria → meio-dia → pôr do sol), o AutoFlow aparecendo como "olhares" do gestor (Painel no notebook, Nova OS, Ordens no celular) e o encerramento com **"Teste gratuito para oficinas selecionadas. Solicite acesso pelo direct."**

Elevar: cenas de vídeo reais no lugar das fotos; personagens naturais e consistentes; transições motivadas (o portão subindo vira a tela acendendo, o giro do elevador vira o giro do celular etc.); ritmo que acelera no meio da manhã e desacelera no fim do dia; sound design com ambiente de oficina (compressor, ferramentas, porta de enrolar), tiques no relógio e trilha que cresce até o encerramento.

---

## 8. FLUXO DE TRABALHO
1. Leia os materiais do item 2 e escreva, em poucas linhas, o que define o estilo aprovado e por que o V2/V3 anteriores se afastaram dele.
2. Verifique o Higgsfield (item 5). Se o vídeo estiver bloqueado, **pare e reporte**.
3. Gere as cenas, revise cada clipe (artefatos, mãos, rostos, continuidade).
4. Edite com a linguagem da Seraphim (Remotion já está montado no repositório, ou outra ferramenta de qualidade equivalente), compondo as telas reais.
5. Revise o arquivo final inteiro: imagem, áudio (sem distorção, pico ≤ -1 dBTP, ~-14 LUFS), ritmo, continuidade, ortografia, telas, áreas seguras.
6. Entregue: `AutoFlow_V2_Do_Caderno_Ao_Sistema_FINAL_v2.mp4` e `AutoFlow_V3_Um_Dia_Na_Oficina_FINAL_v2.mp4`, mantendo as versões anteriores para comparação, com um resumo curto: o que mudou, cenas geradas, créditos gastos e saldo restante.

**Prioridade:** preservar a identidade da Seraphim, dar protagonismo ao produto real, movimento filmado de verdade, zero cobrança extra, nada publicado sem aprovação.
