# ADR-0007 — Dois canais de sincronização: Event Log global e Screen Sync; nunca VT cru para o celular

## Status

Aceita · 2026-09-26 · decidido por Sr. Garioli.

Registro da decisão: decisão irreversível da auditoria (§9 item 3),
mantida explicitamente na proposta aprovada (§8, "Mantido: … Event Log +
Screen Sync"); telas aprovadas dependem dela (`interfaces/android.md` §0,
"Conexão"; `interfaces/fluxos.md` F4 passo 3).

## Contexto

- A proposta inicial previa `terminal.output` incremental com replay de
  bytes e sequência por sessão (auditoria, "Conclusão", tabela).
- Replay de bytes só reconstrói uma TUI se o cliente tiver um emulador VT
  completo **e** todo o histórico desde um estado conhecido; para tela
  alternativa e redesenho isso degenera em "baixar tudo de novo"
  (auditoria §3 A4).
- Sequência por sessão sem época: se o agente reinicia, `seq` volta a 1 e o
  cliente recebe silêncio ou dados errados (auditoria §3 A5).
- **[FATO]** O mosh sincroniza estado de tela em vez de fluxo de bytes
  (USENIX ATC'12, SSP) (auditoria §5.4) — a auditoria marca a citação como
  **[verificar]**, feita de memória (Anexo A, "Mosh").
- VT cru no celular expõe o cliente a escapes maliciosos (OSC 52, OSC 8,
  título) (auditoria §6 T9).

## Decisão

**(a) Event Log** — estado de baixa frequência, confiável e ordenado
(auditoria §5.4 a):

- **Um único log por agente**, identificado por `(epoch, seq)`, `seq`
  monotônico e sem lacunas; `epoch` novo a cada start do agente.
- `resume{epoch, after_seq}`: mesma época e `after_seq` retido → eventos
  seguintes; senão → `snapshot{…, seq_at}` gerado atomicamente sob o mesmo
  lock do log, e depois `seq > seq_at`.
- O cliente descarta `seq <= último aplicado` e pede resume ao ver lacuna.

**(b) Screen Sync** — conteúdo do terminal, a última versão vale
(auditoria §5.4 b):

- O agente mantém o emulador VT da sessão e envia frames `screen` com
  `ver` e `base` (diff sobre a última versão **confirmada** por `ack`, ou
  completo com `base` nulo).
- Coalescência de no máximo ~20 frames/s por sessão assinada; sessões sem
  assinatura não geram frames.
- Histórico só sob demanda e paginado (`screen.history`, `count ≤ 200`).

**(c) Nunca bytes VT crus para o celular:** o celular recebe texto e
estilos já interpretados pelo emulador do agente; OSC 52/8 descartados
(auditoria §5.1, §6 T9).

## Alternativas consideradas

| Alternativa | Por que caiu |
|---|---|
| Fluxo de bytes incremental + replay (proposta original) | Caro e frágil para TUIs; exige emulador no cliente (auditoria §3 A4). |
| Sequência por sessão | Sem época, quebra no restart; lista de sessões inconsistente (auditoria §3 A5, §5.4 a). |
| Um log por sessão | Um log global é mais simples de retomar e deixa a lista consistente; taxa baixa (dezenas por minuto) (auditoria §5.4 a). |
| Emulador de terminal no app (xterm.js ou Termux) | Com Screen Sync o app renderiza linhas com spans e não precisa de emulador (auditoria §10). |

## Consequências

**Positivas**

- Backpressure natural: cliente lento pula versões intermediárias; um
  `cat` de 200 MB custa ao celular poucos frames (auditoria §5.4 b).
- Elimina UTF-8 cortado, injeção de escape no cliente e replay caro
  (auditoria §5.1).
- Restart do agente é explícito (época nova força snapshot) (auditoria §3
  A5).
- O app não precisa de emulador de terminal (auditoria §10).

**Negativas**

- O agente carrega um emulador VT por sessão, com custo de memória
  (auditoria §4.1; meta de ≤ 5 MB por sessão em §13, ainda não medida).
- O Event Log tem retenção limitada (24 h ou 10 000 eventos); além disso,
  só snapshot (auditoria §7.2).
- A escolha do emulador VT e o tamanho do scrollback dependem do spike M0
  (auditoria §8). **[INFERÊNCIA]** a auditoria cita dois limites de
  scrollback diferentes (5 000 linhas em §7.1, ~2 000 em §13); P3/P8
  fixam o número.
- Formato exato de envelope, frames e limites é trabalho da especificação
  TRCP/1 (P3), não deste ADR.

## Referências

- `docs/auditoria-arquitetura-2026-09-26.md` §3 (A4, A5), §4.1, §5.1,
  §5.4, §6 T9, §7.1, §7.2, §8, §9 item 3, §10, §13, "Conclusão", Anexo A.
- `docs/proposta-conexao-por-codigo-2026-09-26.md` §4, §8.
- `docs/interfaces/android.md` §0.
- `docs/interfaces/fluxos.md` F4.
