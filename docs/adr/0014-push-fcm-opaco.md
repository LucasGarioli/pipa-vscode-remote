# ADR-0014 — Push pelo FCM, com payload opaco; UnifiedPush fora do MVP

## Status

Aceita · 2026-09-26 · decidido por Sr. Garioli.

Registro da decisão: resposta de Sr. Garioli em 2026-09-26 à pergunta 4
da auditoria (§12), depois da primeira versão destes ADRs (`README.md`
desta pasta, "Decididos depois da primeira versão", item 2). Completa o
ADR-0012 (minimização de dados), que já exigia push opaco.

## Contexto

- O celular não mantém conexão em segundo plano: **[FATO]** o Doze
  suspende o acesso à rede, e a documentação do Android recomenda FCM em
  vez de conexão persistente (auditoria §3 A8; ADR-0012).
- A auditoria deixou aberta a escolha: FCM (Google vê metadados; exige
  credencial de conta de serviço) ou UnifiedPush/ntfy (sem Google; o
  usuário instala um distribuidor) (auditoria §12, pergunta 4).
- **[FATO]** O payload do FCM passa pelos servidores do Google, com
  limite de 4 KB (auditoria §7.3; Anexo A).
- As interfaces aprovadas já desenharam a notificação opaca "Algo pede sua
  atenção em LUCAS-PC" e a proposta E24 já assumia FCM data-only
  (`interfaces/android.md` §0, §11;
  `interfaces/exigencias-para-o-protocolo.md` E24).

## Decisão

- **Provedor de push do MVP: FCM.**
- **Payload opaco:** só `{agent_id, attention_id}`, sem comando, nome de
  sessão, saída ou qualquer conteúdo (auditoria §7.3;
  `interfaces/exigencias-para-o-protocolo.md` E24, §4).
- O app monta o texto da notificação com o nome do PC que ele já guarda
  e **busca o conteúdo pelo túnel** cifrado ao abrir (auditoria §7.3;
  `interfaces/fluxos.md` F4; ADR-0004).
- **UnifiedPush fica fora do MVP.**

A prioridade da mensagem e o uso de mensagem só de dados (sem bloco
`notification`) estão na proposta E24 e ficam para P3 confirmar.

## Alternativas consideradas

| Alternativa | Por que caiu |
|---|---|
| UnifiedPush/ntfy | Exige que o usuário instale um distribuidor (auditoria §12, pergunta 4). Fora do MVP por decisão de Sr. Garioli; **[INFERÊNCIA]** o motivo provável é o atrito de instalação, contra a promessa "instalar, ler um código, abrir o app" (`visao.md`). |
| Sem push (só ver ao abrir o app) | A visão promete avisar quando algo pede atenção (`visao.md`, "O que faz"). |
| WebSocket persistente em segundo plano | Doze e teto do foreground service (auditoria §3 A8; ADR-0012). |

## Consequências

**Positivas**

- Notificações confiáveis em segundo plano sem conexão aberta (auditoria
  §3 A8).
- Nenhum conteúdo de terminal passa pelo Google (auditoria §7.3).
- Nenhum app extra para o usuário instalar.

**Negativas**

- O Google vê metadados: que um aparelho recebeu uma notificação, e
  quando (auditoria §12, pergunta 4).
- **[INFERÊNCIA]** Aparelhos sem Google Play Services não recebem push no
  MVP.
- Enviar pelo FCM exige uma credencial de conta de serviço (auditoria §12,
  pergunta 4). **[INFERÊNCIA]** onde ela fica (no agente de cada PC, na
  ponte ou num serviço à parte) não está decidido; guardar uma credencial
  do projeto em todo PC de usuário seria um segredo distribuído. Fica para
  P4/P5.
- Push é da fase M8 (auditoria §8); até lá o app só vê pedidos com a tela
  aberta.

## Referências

- `docs/auditoria-arquitetura-2026-09-26.md` §3 A8, §7.3, §8, §12
  pergunta 4, Anexo A.
- `docs/interfaces/android.md` §0, §11.
- `docs/interfaces/fluxos.md` F4.
- `docs/interfaces/exigencias-para-o-protocolo.md` E24, §4.
- `docs/visao.md` "Promessa", "O que faz".
- `docs/adr/0012-minimizacao-de-dados-no-celular.md`.
