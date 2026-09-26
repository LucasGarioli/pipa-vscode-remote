# Visão do produto (P1)

Status: rascunho de planejamento, 2026-09-26.

## Nome e marca

**Pipa**, aprovado por Sr. Garioli em 2026-09-26. A pipa voa longe, mas
continua presa à mão por uma linha: os terminais longe, controlados por um
túnel seguro. O protocolo continua se chamando TRCP.

Marca:

- **Logo:** conceito A, "Pipa". É uma pipa em losango, âmbar, com o
  prompt `>_` dentro e rabiola embaixo. Sr. Garioli escolheu o C primeiro e
  trocou para o A no mesmo dia. Referência:
  `docs/marca/pipa-conceitos-de-logo.html`.
  - **Tamanhos pequenos:**
    - 24 px: losango vazado + `>`, em uma cor;
    - 16 px: só o losango cheio;
    - ícone do app: quadrado tinta com a pipa âmbar.
- **Cores:**
  - âmbar de fósforo `#F2A93B`;
  - âmbar para texto em fundo claro `#8A5300`;
  - tinta `#11141A`;
  - papel `#F4F1EA`.
- **Tipografia:** JetBrains Mono (marca e terminal) + IBM Plex Sans (UI).

Checagem de conflito de nome, feita em 2026-09-26 (GitHub, Marketplace do
VS Code e web): nada encontrado como ferramenta de terminal.

Descartados por colidirem com produtos quase idênticos: Farshell, Teletty,
Termote, Remotty, Farol, Vigia.

Concorrentes diretos a considerar no posicionamento: AirCodum, VSCodeMobile,
Termote, Farshell e o Remote Control oficial do Claude Code.

## Promessa

Controlar a distância, pelo celular, os terminais abertos no VS Code — com
segurança, praticidade e leveza:

- instalar o plugin;
- ler um código;
- abrir o app;
- pronto.

## Público

- Primeiro: o próprio Sr. Garioli.
- Depois: desenvolvedores que deixam tarefas longas rodando no terminal
  (builds, testes, servidores, agentes de IA como o Claude Code) e querem
  acompanhar e responder de longe.

## O que faz

- Mostra no celular todos os terminais abertos no VS Code, com estado e
  contexto mínimo.
- Mostra a tela de um terminal sob demanda, com histórico paginado.
- Envia comandos e teclas especiais, depois de liberar a escrita com
  biometria.
- Responde aprovações estruturadas, como as permissões do Claude Code.
- Avisa quando algo pede atenção.
- Conecta por código de 12 dígitos, via ponte própria, com túnel cifrado
  ponta a ponta.

## O que não faz (no MVP)

- Não acessa arquivos, Git nem processos fora dos terminais.
- Não controla terminais abertos fora do perfil "Terminal remoto".
- Não guarda no celular o conteúdo das telas.
- Não depende de Tailscale, Microsoft Dev Tunnels ou contas de terceiros.
- Não roda no iOS.

## Decisões de interface (2026-09-26)

- **Idiomas:** PT-BR e EN desde o início. O texto de referência é PT-BR, e
  toda string vem de um catálogo traduzível.
- **Identidade visual:** própria, **estilo terminal**: base sóbria, tipografia
  monoespaçada nos dados de terminal, próxima do VS Code sem copiá-lo.
- **Tema:** claro e escuro, seguindo o sistema. No VS Code, a UI nativa herda
  o tema do editor.
- **Plataformas:** extensão VS Code (Windows primeiro) + app Android.
