# Interfaces da Pipa (P7)

Status: rascunho de planejamento, 2026-09-26. Nada aqui é código de
produto.

Este conjunto desenha as telas da extensão VS Code e do app Android da
**Pipa**, e o que elas exigem do protocolo TRCP/1. Base:

- `docs/visao.md`;
- `docs/auditoria-arquitetura-2026-09-26.md`;
- `docs/proposta-conexao-por-codigo-2026-09-26.md`;
- `docs/marca/pipa-conceitos-de-logo.html` (conceito A).

## Índice

| Arquivo | O que tem |
|---|---|
| `fluxos.md` | Fluxos numerados F1–F7 (instalar → parear → acompanhar → digitar → aprovar → revogar/cortar → remover) e 20 caminhos de falha, com diagramas mermaid |
| `vscode.md` | Cada superfície da extensão, com a API estável conferida no `vscode.d.ts` (com linha), conteúdo, estados e textos |
| `android.md` | Cada tela do app: propósito, campos do protocolo, ações e permissões, estados, textos, acessibilidade |
| `identidade-visual.md` | Marca em cada tamanho, tokens claro/escuro com contraste medido, tipografia, espaço, ícones, mapeamento Material 3 |
| `textos.md` | Catálogo completo de strings (478 chaves, PT-BR e EN), gerado do JSON |
| `exigencias-para-o-protocolo.md` | O que falta no TRCP/1 para as telas funcionarem (E1–E27, P1–P5, IPC I1–I12) |
| `prototipo/index.html` | Protótipo navegável e descartável: celular + VS Code lado a lado, PT/EN, sistema/claro/escuro |
| `prototipo/textos.catalogo.json` | Fonte única dos textos; o protótipo e o `textos.md` saem dela |

## Glossário

- **Terminal:** o que a pessoa vê e chama assim, tanto no VS Code quanto no
  celular. Nas telas, sempre "terminal".
- **Sessão:** o nome técnico do mesmo terminal no protocolo (`Session`). Só
  aparece nos documentos técnicos.
- **Só leitura / escrita liberada:** os dois modos de um terminal no
  celular. "Liberar escrita" é o termo da tela; nos documentos, "arm".
- **Pedido (de atenção):** `Attention`. Na tela: "Claude pede permissão",
  "pedido esperando sua resposta".
- **Servidor (ponte):** o servidor de retransmissão (`trc-bridge`). Só vê
  bytes cifrados. Nas telas, sempre "servidor"; "ponte" e `trc-bridge` ficam
  nos documentos técnicos (AJ-34). Não há servidor público: cada pessoa usa
  o seu; o de Sr. Garioli é privado.
- **Código:** os 12 dígitos do pareamento.
- **Código de confirmação:** os 6 dígitos (SAS) mostrados nos dois lados.

## Decisões de desenho

Cada decisão cita a razão. As que mudam o produto estão em **Perguntas**.

1. **Só leitura por padrão, escrita por terminal, com prazo e biometria ou PIN**
   (Nielsen H5, prevenção de erro):
   - o controle é por terminal, e o prazo é 1 / 5 / 15 min;
   - a faixa de modo fica sempre visível no topo do terminal;
   - no PC, a aba muda de nome e a barra de status muda de cor.
2. **Cor com um significado só:**
   - âmbar da marca = atenção (pedido pendente);
   - magenta = escrita liberada;
   - vermelho = destrutivo ou erro.

   O botão primário é tinta/papel, não âmbar: se o âmbar estivesse em todo
   botão, o pedido pendente não saltaria aos olhos.
3. **A proteção fica onde o erro custa caro:**
   - biometria ou PIN em liberar escrita, permitir destrutivo e encerrar
     terminal;
   - modal no PC só para aceitar um aparelho e para revogar;
   - o resto é rápido e reversível;
   - o kill switch não tem confirmação e oferece **Reativar** (desfazer é
     melhor que confirmar).
4. **Confirmações nomeiam o objeto:**
   - "Revogar “Galaxy Tab S9”?";
   - "Remover LUCAS-PC";
   - "Encerrar Backend?".

   Nunca "Tem certeza?".
5. **Pedido velho não aceita resposta.** O agente responde `already_resolved`,
   e a tela troca os botões por um cartão que diz quem respondeu e quando.
6. **O texto digitado nunca se perde.** Tela mudou, escrita expirou ou
   conexão caiu: o campo mantém o texto. O envio nunca é repetido sozinho;
   quando há dúvida, o app pergunta ao PC (`cmd.status`).
7. **Pareamento com verificação humana dos dois lados.** O mesmo código de
   confirmação aparece no celular e no modal do PC. Um código errado é
   invalidado na hora (tentativa única).
8. **Nada da tela no celular:**
   - memória apenas, com `FLAG_SECURE` ligado;
   - push opaco ("Algo pede sua atenção em LUCAS-PC");
   - o celular guarda só a lista de PCs pareados e a chave.
9. **VS Code sem invenção:**
   - só API estável, nada desenhado dentro do terminal;
   - o estado remoto aparece no nome e no ícone da aba, na barra de status e
     num painel próprio;
   - a única webview é o painel de pareamento (QR), feito com `--vscode-*`.
10. **Marca, conceito A:**
    - glifo de 16 px = losango cheio;
    - glifo de 24 px = losango vazado + `>`;
    - ícone do app = quadrado tinta com a pipa âmbar.

    O âmbar não serve para texto sobre papel (1,77:1); no claro, o texto
    "âmbar" é `#8A5300`.
11. **Acessibilidade medida, não prometida:**
    - contraste WCAG 2.2 AA: 0 reprovações em 96 pares de tokens e em 4.474
      textos renderizados, nos dois temas;
    - alvos de 48 dp;
    - TalkBack com um nó por item;
    - contagens regressivas estensíveis e não anunciadas a cada segundo.

## Como revisar

1. **Protótipo:** abra `prototipo/index.html` no Chrome. O arquivo é um
   fragmento pensado para ser publicado como página; aberto direto do disco,
   funciona igual.
   - Toque nos elementos do celular e do VS Code: as duas colunas conversam.
     - Permitir no modal conclui o pareamento no celular.
     - Liberar escrita renomeia a aba no VS Code.
     - Cortar acesso derruba o celular.
     - Revogar mostra a tela de revogado.
   - O seletor **Ir para** abre qualquer um dos 70 estados.
   - Cada estado também abre por link: `index.html#attn_destructive`,
     `#vs_modal`, `#cut`…
   - Os botões no topo trocam idioma (PT/EN) e tema (sistema/claro/escuro).
2. **Fluxos:** `fluxos.md` na ordem F1 → F7.
3. **Detalhe:** `android.md` e `vscode.md` por tela.
4. **Protocolo:** `exigencias-para-o-protocolo.md`, para quem vai escrever o
   P3/P4.
5. **Textos:** editar `prototipo/textos.catalogo.json` e gerar de novo
   `textos.md` e o protótipo (scripts `build.py` / `gen_textos.py` usados no
   planejamento).

## Perguntas para Sr. Garioli

Cada pergunta traz o padrão usado nos documentos e no protótipo. Nada disso
foi decidido em silêncio: basta confirmar ou trocar.

| # | Pergunta | Padrão proposto | Por quê |
|---|---|---|---|
| Q1 | Recusar um pedido pede biometria? | **Não** | Recusar é o lado seguro; exigir biometria atrasa justamente a resposta de proteção |
| Q2 | O celular guarda a lista de terminais (só nomes e estados) para abrir mais rápido? | **Não** | A visão diz "não guarda conteúdo das telas"; nome de terminal e comando já são conteúdo sensível |
| Q3 | Bloquear capturas de tela (`FLAG_SECURE`) ligado por padrão? | **Sim**, desligável | O terminal pode mostrar segredos; o custo é não poder tirar print para suporte |
| Q4 | No pareamento, o PC só **compara** o código de confirmação ou a pessoa **digita** no PC? | **Comparar** | Digitar é mais seguro contra o clique no reflexo, mas custa atrito numa ação feita uma vez; a comparação + código de uso único + modal nomeado já cobrem |
| Q5 | O corte de acesso (kill switch) persiste depois de reiniciar o PC? | **Sim** | Quem cortou numa emergência não quer ver o acesso voltar sozinho num reboot |
| Q6 | O celular pode revogar **outros** aparelhos? | **Não**, só no PC | Um celular roubado não pode expulsar o dono legítimo |
| Q7 | Durações de escrita | **1 / 5 / 15 min, padrão 5**, teto configurável no PC | 5 min cobre "responder e acompanhar"; 15 cobre uma sessão curta |
| Q8 | Vários PCs no MVP (a lista "Computadores")? | **Sim na tela, sem trabalho extra** | O desenho já suporta; se o MVP for um PC só, a lista abre direto nos terminais |
| Q9 | Notificação no PC quando um celular libera escrita | **Ligada**, desligável | O dono precisa saber que alguém está no controle, mesmo sem olhar a barra de status |
| Q10 | Pedir biometria ao **abrir** o app | **Desligado** | Ler é inofensivo, e escrever já exige biometria; ligar custa um toque a cada abertura |
| Q11 | Nome do PC: o hostname do Windows ou um nome escolhido no VS Code? | **Hostname, editável** | Funciona sem pergunta no primeiro uso |

## O que ficou fora (de propósito)

- iOS;
- widget e Wear OS;
- criar terminal pelo celular;
- redimensionar o terminal;
- teclado completo (F1–F12, Alt);
- ações na notificação;
- temas além de claro e escuro.

Motivos em `android.md` §15.


## Aprovação (2026-09-26)

- **Interfaces aprovadas** por Sr. Garioli depois de navegar no protótipo.
- **Os 11 padrões das perguntas Q1–Q11 foram aceitos como decididos:**
  - Q1: recusar sem biometria;
  - Q2: o celular não guarda a lista de terminais;
  - Q3: FLAG_SECURE ligado;
  - Q4: o PC compara o código de confirmação;
  - Q5: o corte persiste após reiniciar;
  - Q6: o celular não revoga outros aparelhos;
  - Q7: escrita por 1/5/15 min, padrão 5;
  - Q8: vários PCs no MVP;
  - Q9: notificação no PC ao liberar escrita;
  - Q10: sem biometria ao abrir o app;
  - Q11: nome do PC = hostname, editável.
- O protótipo é regenerado por `prototipo/ferramentas/build.py`, que lê
  `proto.src.html` e `textos.catalogo.json`. Os textos são regenerados por
  `gen_textos.py`.
- **Revisão 2 das interfaces aprovada e aplicada em 2026-09-26.** Sr.
  Garioli aprovou os ajustes de `ajustes-pendentes-2026-09-26.md`: as 21
  correções óbvias e as 13 decisões na opção recomendada (AJ-03, 04, 07,
  08, 10, 11, 15, 16, 18, 19, 25, 33 e 34). Os 34 entraram nas telas, no
  catálogo (478 chaves), nos fluxos, nas exigências do protocolo, na visão e
  no protótipo (70 estados). AJ-22 e AJ-32 ficam para P5 (segurança).

## Ajustes pendentes

Os ajustes de tela e texto pedidos pelas entregas de planejamento estão
numa lista única, com o arquivo e a seção onde cada um entrou:
[`ajustes-pendentes-2026-09-26.md`](ajustes-pendentes-2026-09-26.md).
Aplicados em 2026-09-26, exceto AJ-22 e AJ-32, que ficam para P5.
