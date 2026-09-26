# ADR-0009 — Identidade: nome Pipa, logo A, PT-BR + EN, claro + escuro

## Status

Aceita · 2026-09-26 · decidido por Sr. Garioli.

Registro da decisão: `visao.md`, "Nome e marca" e "Decisões de interface
(2026-09-26)"; interfaces aprovadas (`interfaces/README.md`,
"Aprovação").

## Contexto

O produto precisava de nome, marca, idiomas e tema antes das telas (mapa
do planejamento, "Ordem", passo 1).

## Decisão

- **Nome:** Pipa. O protocolo continua se chamando TRCP (`visao.md`).
- **Logo:** conceito A, pipa em losango âmbar com `>_` dentro e rabiola;
  Sr. Garioli escolheu o C primeiro e trocou para o A no mesmo dia
  (`visao.md`). Tamanhos pequenos: 16 px losango cheio, 24 px losango
  vazado + `>`, ícone do app quadrado tinta com a pipa âmbar
  (`visao.md`; `interfaces/README.md` decisão 10).
- **Cores e tipografia:** âmbar `#F2A93B`, âmbar para texto em claro
  `#8A5300`, tinta `#11141A`, papel `#F4F1EA`; JetBrains Mono + IBM Plex
  Sans (`visao.md`).
- **Idiomas:** PT-BR e EN desde o início; PT-BR é o texto de referência, e
  toda string vem de um catálogo traduzível (`visao.md`;
  `interfaces/prototipo/textos.catalogo.json`).
- **Tema:** claro e escuro, seguindo o sistema; no VS Code a UI nativa
  herda o tema do editor (`visao.md`; `interfaces/vscode.md`, "Regras").

## Alternativas consideradas

| Alternativa | Por que caiu |
|---|---|
| Farshell, Teletty, Termote, Remotty, Farol, Vigia | Colidem com produtos quase idênticos (`visao.md`). |
| Logo conceito C | Escolhido primeiro e trocado pelo A no mesmo dia (`visao.md`). O motivo da troca não está registrado. |
| Só PT-BR ou só um tema | Não registrado como alternativa; a decisão já veio com os dois (`visao.md`). |

## Consequências

**Positivas**

- Nome sem conflito encontrado como ferramenta de terminal (GitHub,
  Marketplace do VS Code e web, 2026-09-26) (`visao.md`).
- Contraste medido: 0 reprovações WCAG 2.2 AA nos dois temas
  (`interfaces/README.md` decisão 11).

**Negativas**

- Toda string passa por catálogo em dois idiomas (418 chaves hoje,
  `interfaces/README.md`, índice).
- O âmbar não serve para texto sobre papel (1,77:1); no claro o texto
  "âmbar" é `#8A5300` (`interfaces/README.md` decisão 10).

## Referências

- `docs/visao.md` "Nome e marca", "Decisões de interface (2026-09-26)".
- `docs/interfaces/README.md` decisões 10 e 11, "Aprovação".
- `docs/interfaces/identidade-visual.md`.
- `docs/marca/pipa-conceitos-de-logo.html`.
