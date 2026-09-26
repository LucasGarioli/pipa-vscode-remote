# ADR-0011 — Comandos de escrita at-most-once, sem retry automático, com precondição de estado

## Status

Aceita · 2026-09-26 · decidido por Sr. Garioli.

Registro da decisão: decisão irreversível da auditoria (§9 item 4),
coberta pela aprovação da proposta ("o restante desta auditoria continua
valendo", cabeçalho da proposta), e decisão de desenho 6 das interfaces
aprovadas ("O envio nunca é repetido sozinho; quando há dúvida, o app
pergunta ao PC (`cmd.status`)", `interfaces/README.md`).

## Contexto

- Input remoto não é idempotente: reenviar `terminal.input` após timeout
  pode executar `y` ou `rm` duas vezes (auditoria §3 A2).
- Corrida entre prompt e input: entre ver "Aprovar? (y/n)" e enviar `y`, a
  tela muda e o `y` cai em outro lugar (auditoria §3 A3).
- A conexão do celular cai com frequência (rede móvel, app em segundo
  plano) (auditoria §3 A8).

## Decisão

- Todo `cmd` leva um `id` gerado pelo cliente, que é a chave de
  idempotência; o agente guarda `(device_id, cmd.id) → result` por 10 min
  e devolve o resultado guardado a um duplicado **sem reaplicar**
  (auditoria §5.2, §5.5).
- O cliente **nunca** reenvia `input.send` ou `attention.respond`
  sozinho; em caso de dúvida, consulta `cmd.status` depois de reconectar
  (auditoria §5.5; `interfaces/README.md` decisão 6).
- **Precondição:** `input.send` leva `expect.screen_ver` (ou o pedido leva
  `attention_id`); tela obsoleta responde `stale`, pedido já resolvido
  responde `already_resolved` (auditoria §3 A3, §5.5;
  `interfaces/README.md` decisão 5).
- O texto digitado nunca se perde: tela mudou, escrita expirou ou conexão
  caiu, o campo mantém o texto (`interfaces/README.md` decisão 6).

## Alternativas consideradas

| Alternativa | Por que caiu |
|---|---|
| Retry automático com ack (proposta original: "Retry/ack indefinidos") | Pode executar o mesmo input duas vezes (auditoria §3 A2; "Conclusão", tabela). |
| Enviar sem precondição | O input pode cair num prompt diferente do que a pessoa viu (auditoria §3 A3). |

## Consequências

**Positivas**

- Nenhum comando é executado duas vezes por falha de rede (auditoria §3
  A2).
- Um pedido velho não aceita resposta; a tela mostra quem respondeu e
  quando (`interfaces/README.md` decisão 5).

**Negativas**

- A pessoa às vezes precisa reenviar à mão depois de ver o estado
  (`interfaces/README.md` decisão 6).
- O cliente guarda o `cmd.id` pendente em memória até reconectar
  (`interfaces/exigencias-para-o-protocolo.md` E15).
- A lista de códigos de erro (`not_armed`, `too_large`, `rate_limited`,
  `step_up_required`…) é **proposta** das interfaces para P3
  (`interfaces/exigencias-para-o-protocolo.md` E14).

## Referências

- `docs/auditoria-arquitetura-2026-09-26.md` §3 (A2, A3, A8), §5.2, §5.5,
  §9 item 4, "Conclusão".
- `docs/interfaces/README.md` decisões 5 e 6, "Aprovação".
- `docs/interfaces/exigencias-para-o-protocolo.md` E14, E15.
