# ADR-0008 — "Aguardando" detectado por hooks do Claude Code; heurística de tela só como fallback rotulado

## Status

Aceita · 2026-09-26 · decidido por Sr. Garioli.

Registro da decisão: recomendação da auditoria (§1, §3 C3, "Conclusão"),
coberta pela aprovação da proposta ("o restante desta auditoria continua
valendo", cabeçalho da proposta), e pelas interfaces aprovadas, que já
mostram a origem do pedido (`interfaces/android.md` §10;
`interfaces/fluxos.md` F4; `interfaces/README.md`, "Aprovação").
**[INFERÊNCIA]** Não há frase de Sr. Garioli dedicada só a este ponto; a
aceitação vem dessas duas aprovações.

## Contexto

- Detectar "Claude esperando interação" raspando a saída não é confiável.
  **[INFERÊNCIA]** a TUI redesenha a tela com diffs de escape; digitar "1"
  num menu no momento errado aprova a coisa errada (auditoria §3 C3).
- **[FATO]** O Claude Code expõe hooks: `Notification` com
  `notification_type` (`permission_prompt`, `idle_prompt`,
  `elicitation_dialog`, `agent_needs_input`…), `PermissionRequest` (que
  pode devolver `allow`/`deny`), `Stop` com `last_assistant_message`, e
  HTTP hooks que fazem POST do JSON para um endpoint, com headers
  interpolados de variáveis de ambiente (`allowedEnvVars`) (auditoria §3
  C3; https://code.claude.com/docs/en/hooks).
- Um programa malicioso pode imitar o prompt do Claude na tela (auditoria
  §6 T10).
- Campos como objetivo e tarefa atual não saem de heurística (auditoria §3
  A7).

## Decisão

- O agente tem um **adaptador Claude Code**: um HTTP hook do Claude Code
  faz POST para um endpoint do agente em `127.0.0.1`, que exige um header
  com **token por sessão**, injetado no ambiente do PTY (auditoria §4.2,
  §6 T11, T17).
- Esses eventos viram `Attention` estruturada (`kind`, `options`,
  `destructive`, `source`), e a aprovação pelo celular é uma **decisão
  estruturada** (`attention.respond`), não um toque de tecla (auditoria §3
  C3, §5.5, §7.1).
- A **heurística de tela fica só como fallback**, sempre rotulada:
  `SessionStatus=waiting` carrega `{source: adapter|heuristic,
  confidence}`, e a tela do celular mostra "Detectado pela tela. Confira o
  terminal antes de responder." (auditoria §7.1, §6 T10;
  `interfaces/android.md` §10; texto `attn.source_heuristic`).
- Todo campo de contexto marca a origem (`adapter|heuristic|llm`)
  (auditoria §3 A7, §7.1).
- Uma decisão remota de permissão entra no audit (auditoria §6 T17).

## Alternativas consideradas

| Alternativa | Por que caiu |
|---|---|
| Só heurística sobre a saída do terminal | Frágil com TUI; risco de aprovar a coisa errada; imitável por saída maliciosa (auditoria §3 C3, §6 T10). |
| Remote Control oficial do Claude Code | Tráfego pela API da Anthropic e transcript nos servidores dela; só cobre Claude (auditoria §4.1; ADR-0001). |
| Ler o transcript do Claude Code | O agente não lê `transcript_path` no MVP (auditoria §7.3). |

## Consequências

**Positivas**

- Pedidos de permissão chegam estruturados; o celular mostra Permitir /
  Recusar grandes e o comando em destaque (auditoria §3 C3;
  `interfaces/android.md` §10).
- Atenções de adaptador autenticado valem mais que heurística, e a UI
  mostra a diferença (auditoria §6 T10).
- Critério de pronto de M5: "Atenção 'permissão' chega estruturada"
  (auditoria §8).

**Negativas**

- **Não verificado:** o timeout máximo de um `PermissionRequest` esperando
  decisão humana; o spike M0 mede (auditoria §8 M0, Anexo A). Se for
  curto, a aprovação pelo celular pode chegar tarde.
- O endpoint loopback é superfície nova; mitigada por token por sessão e
  só loopback (auditoria §6 T17, T11).
- Só o Claude Code tem adaptador no MVP; outras ferramentas ficam na
  heurística rotulada (auditoria §4.2 "adaptadores"; §8 M5).
  **[INFERÊNCIA]** novos adaptadores exigem trabalho por ferramenta.
- Os campos `options[].role`, `subject`, `requires_step_up` e
  `resolved_by` são **propostas** das interfaces
  (`interfaces/exigencias-para-o-protocolo.md` E7–E10) para P3.

## Referências

- `docs/auditoria-arquitetura-2026-09-26.md` §1, §3 (A7, C3), §4.1, §4.2,
  §5.5, §6 (T10, T11, T17), §7.1, §7.3, §8, "Conclusão", Anexo A.
- `docs/interfaces/android.md` §10.
- `docs/interfaces/fluxos.md` F4.
- `docs/interfaces/textos.md` (`attn.source_heuristic`,
  `ctx.heuristic`).
- `docs/interfaces/exigencias-para-o-protocolo.md` E7–E10.
