# ADR-0010 — Reusar o desenho, não o código, de magic-wormhole.rs e RustDesk; `spake2`/`snow` não auditados como risco aberto

## Status

Aceita · 2026-09-26 · decidido por Sr. Garioli.

Registro da decisão: proposta de conexão por código §6, aprovada como
direção (cabeçalho da proposta). A escolha final das bibliotecas
criptográficas é da revisão de segurança P5 (Fable max) (proposta §8,
"Revisão"; mapa P5).

## Contexto

- O desenho do pareamento segue o magic-wormhole (SPAKE2 sobre código
  curto) e a topologia segue AnyDesk/RustDesk (servidor de encontro +
  relay) (proposta §3, §5).
- **[FATO]** As implementações de referência têm licença copyleft:
  magic-wormhole.rs é EUPL e RustDesk é AGPL-3.0 (proposta §6).
- **[FATO]** `spake2` e `snow` (Noise) declaram no README que não passaram
  por auditoria independente (proposta §6).
- **[FATO]** O Noise não aceita senha curta como PSK: a especificação exige
  256 bits (§15.1) (proposta §6).
- A licença do repositório público ainda está aberta (auditoria §12,
  pergunta 6).

## Decisão

- **Reaproveitar o desenho, não o código** de magic-wormhole.rs e RustDesk,
  a menos que o produto seja open source com licença compatível (proposta
  §6).
- **TLS 1.3 para todas as sessões** (biblioteca amplamente usada e
  revisada) e **SPAKE2 só no pareamento**, com vetores de teste e revisão
  de segurança dedicada (proposta §6).
- Noise `IK` nas sessões fica registrado e **não** é adotado (proposta §6).
- O uso da crate `spake2` não auditada fica registrado como **risco
  aberto**; P5 decide se ela serve, com quais mitigações, ou qual
  alternativa (proposta §6, §8).

## Alternativas consideradas

| Alternativa | Por que caiu |
|---|---|
| Copiar código de magic-wormhole.rs ou RustDesk | EUPL e AGPL-3.0 obrigariam compatibilidade de licença, e a licença do projeto não está escolhida (proposta §6; auditoria §12 pergunta 6). |
| Noise (`snow`) nas sessões | Não auditado e sem PSK curto (proposta §6). |

## Consequências

**Positivas**

- A licença do projeto fica livre para ser escolhida depois (auditoria §9
  item 9, §12 pergunta 6).
- A parte mais exposta (todas as sessões) usa TLS 1.3, amplamente revisado
  (proposta §6).

**Negativas**

- Implementação própria do fluxo de pareamento e do protocolo da ponte,
  sem atalho de código (proposta §6). **[INFERÊNCIA]** mais trabalho e
  mais superfície para revisar.
- A crate `spake2` continua sem auditoria independente; o risco fica aberto
  até P5 (proposta §6).
- **[INFERÊNCIA]** Se a licença escolhida for compatível com EUPL ou AGPL,
  a decisão de não reusar código pode ser revista (proposta §6, "a menos
  que").

## Referências

- `docs/proposta-conexao-por-codigo-2026-09-26.md` §3, §5, §6, §8.
- `docs/auditoria-arquitetura-2026-09-26.md` §9 item 9, §12 pergunta 6.
- `docs/plans/00-mapa-do-planejamento.md` P5.
