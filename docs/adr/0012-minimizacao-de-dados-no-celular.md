# ADR-0012 — Minimização de dados: nada da tela persiste no celular; push opaco; conexão só em primeiro plano

## Status

Aceita · 2026-09-26 · decidido por Sr. Garioli.

Registro da decisão: decisão irreversível da auditoria (§9 item 7, padrões
da §7.3), mantida na proposta aprovada (§8, "Mantido: … minimização de
dados"); `visao.md`, "O que não faz": "Não guarda no celular o conteúdo das
telas"; perguntas Q2 e Q3 das interfaces, aceitas na "Aprovação
(2026-09-26)".

## Contexto

- O terminal mostra código e segredos (auditoria §6 T14).
- Relaxar privacidade depois é fácil; endurecer depois quebra expectativas
  e dados já persistidos (auditoria §9 item 7).
- **[FATO]** O Doze suspende o acesso à rede, e o foreground service
  `dataSync` tem teto de 6 h/24 h no Android 15 (auditoria §3 A8).
- **[FATO]** O payload do FCM passa pelos servidores do Google (auditoria
  §7.3).

## Decisão

- **Fica no PC, sempre:** saída bruta do PTY, scrollback completo,
  variáveis de ambiente, arquivos, transcript do Claude Code, chaves
  privadas (auditoria §7.3).
- **Nunca persistido em lugar nenhum:** saída bruta, input digitado,
  conteúdo de tela no celular (auditoria §7.2, §7.3).
- **No celular:** linhas, contexto e pedidos só em memória, descartados
  quando o app sai do primeiro plano por mais de 5 min ou o processo
  morre; o celular guarda só a lista de PCs pareados
  (`{agent_id, agent_name, bridge, fingerprint}`, DataStore cifrado) e a
  chave no Keystore (`interfaces/android.md` §0; `interfaces/README.md`
  decisão 8).
- **Não guarda a lista de terminais** (Q2): nome de terminal e comando já
  são conteúdo sensível.
- **`FLAG_SECURE` ligado por padrão**, desligável (Q3).
- **Push opaco:** só `{agent_id, attention_id}`; o texto ("Algo pede sua
  atenção em LUCAS-PC") é montado no app, e o conteúdo é buscado pelo túnel
  ao abrir (auditoria §7.3; `interfaces/android.md` §0). Provedor: FCM
  (ADR-0014).
- **WebSocket só com o app em primeiro plano;** em segundo plano, só push
  (auditoria §3 A8; `interfaces/android.md` §0, "Conexão").

## Alternativas consideradas

| Alternativa | Por que caiu |
|---|---|
| Guardar a lista de terminais para abrir mais rápido | Nome e comando são conteúdo sensível (Q2). |
| Capturas de tela liberadas por padrão | O terminal pode mostrar segredos (Q3). |
| WebSocket persistente em segundo plano (foreground service) | Doze e teto de 6 h/24 h do `dataSync` (auditoria §3 A8). |
| `lastOutput` de 32 KB no contexto (proposta original) | Substituído por `last_result` ≤ 1 KB redigido e tela sob demanda (auditoria §7.1). |

## Consequências

**Positivas**

- Celular perdido ou roubado não carrega conteúdo de terminal (auditoria
  §6 T14).
- Google vê só IDs opacos no push (auditoria §7.3).
- Em segundo plano, nenhuma conexão fica aberta (meta da auditoria §13).
  **[INFERÊNCIA]** o custo de bateria fica perto de zero; a medição é
  trabalho de P8.

**Negativas**

- Sem prints para suporte enquanto `FLAG_SECURE` estiver ligado (Q3).
- Abrir o app sempre refaz `resume` e mostra "Reconectando…"
  (`interfaces/android.md` §0).
- O provedor de push é o FCM, com UnifiedPush fora do MVP (decidido por
  Sr. Garioli em 2026-09-26; ADR-0014). O Google vê metadados de entrega.

## Referências

- `docs/auditoria-arquitetura-2026-09-26.md` §3 A8, §6 T14, §7.1–§7.3, §9
  item 7, §12 pergunta 4, §13.
- `docs/proposta-conexao-por-codigo-2026-09-26.md` §8.
- `docs/visao.md` "O que não faz (no MVP)".
- `docs/interfaces/README.md` decisão 8, Q2, Q3, "Aprovação".
- `docs/interfaces/android.md` §0.
- `docs/interfaces/exigencias-para-o-protocolo.md` E24, §4.
