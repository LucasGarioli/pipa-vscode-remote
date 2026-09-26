# Exigências das interfaces para o protocolo (P7 → TRCP/1)

Status: rascunho de planejamento, 2026-09-26. Base:
`docs/auditoria-arquitetura-2026-09-26.md` §5 e §7.1, e
`docs/proposta-conexao-por-codigo-2026-09-26.md`.

Cada item lista:

- o que uma tela precisa mostrar ou fazer;
- o que falta no TRCP/1 como está descrito hoje;
- uma proposta de campo, evento ou comando.

As propostas são sugestões para quem escrever a especificação do protocolo
(P3/P4). O nome final é decisão de lá.

Legenda de prioridade:

- **M** = bloqueia o MVP (a tela não existe sem isso);
- **D** = desejável (a tela funciona com um substituto pior, descrito na
  linha).

## 1. Cliente Android ↔ agente (via ponte)

| # | Tela / texto | Falta hoje | Proposta | Prio |
|---|---|---|---|---|
| E1 | Lista de computadores, títulos, notificação: "LUCAS-PC" | `Agent` não tem nome | `hello` do servidor ganha `agent_name` (hostname do Windows, editável no VS Code). O celular guarda `{agent_id, agent_name, bridge, fingerprint}` como **dado de pareamento** (não é conteúdo de tela). | M |
| E2 | "offline desde 14:02" | Nada informa quando o agente sumiu | A ponte responde a uma consulta de presença autenticada pelo celular: `presence{agent_id} → {online, since}`. Substituto: o celular mostra a hora do último contato que ele mesmo teve. | D |
| E3 | "1 pedido esperando" na lista de computadores, antes de abrir o PC | Só vem no `snapshot` depois do `resume` completo | Contagem no `auth.ok`: `summary{sessions, open_attentions}`. Evita assinar o log inteiro só para montar a lista. | D |
| E4 | Folha "Liberar escrita": opções 1/5/15 min, "no máximo {n} min", "escrita desativada no PC" | A política do PC não é exposta | `auth.ok.policy{write_enabled, arm_max_min, arm_choices_min[]}`, e um evento `policy.changed` no log. | M |
| E5 | Liberar escrita: contagem regressiva, "retirada no PC" | Não há comando de *arm*. `Grant.armed_until` existe, mas não o fluxo | Comando `grant.arm{s, minutes, step_up}` → `result.data{armed_until, remaining_ms}`, e `grant.disarm{s}`. Eventos `grant.armed` e `grant.disarmed{by: device\|pc\|expiry\|cut}`. A contagem usa `remaining_ms` (o relógio do celular não é confiável), e o celular recalcula a partir do recebimento. | M |
| E6 | Biometria para liberar escrita, permitir destrutivo e encerrar | "step-up" citado, sem formato | `step_up = {nonce, sig}`, com `sig = ECDSA(chave com setUserAuthenticationRequired, "trcp-stepup-v1" ‖ nonce ‖ cmd_hash)`. O `nonce` vem de `cmd step_up.challenge{purpose}`, uso único e 60 s de validade. | M |
| E7 | Pedido de permissão: botões Permitir / Recusar grandes | `options[]` sem tipo | `options[]: {id, label, role: allow\|deny\|other}`. A tela mostra `allow`/`deny` como botões e o resto como lista. Sem `role`, o celular não sabe qual é o "sim". | M |
| E8 | "Já respondido no PC às 14:33" / "por Galaxy Tab às…" / "O Claude parou de esperar" / "terminou antes da resposta" | `resolved_by` sem valores definidos | `resolved_by: {kind: pc\|device\|timeout\|session_ended, device_name?}` e `resolved_at`. | M |
| E9 | "Permitir exige biometria" antes do toque | `destructive` existe; falta dizer se step-up será exigido | `attention.requires_step_up: bool`, calculado pelo agente: `destructive` **ou** sessão sem escrita liberada. A tela explica antes, em vez de surpreender (Nielsen H1). | M |
| E10 | Pedido: pasta e comando em destaque | `detail` é texto livre | `attention.subject{type: command\|file\|text, value}` separado de `detail`. O comando vai para a caixa mono; o `detail` fica como texto de apoio. | M |
| E11 | Lista de terminais: "aguardando permissão" vs "aguardando você" | `waiting` sem distinção de tipo | O estado vem de `SessionStatus=waiting` + `open_attentions` da sessão. Basta o evento `attention.opened` carregar `session_id` (já carrega). Confirmar isso na spec. | — |
| E12 | Terminal: "120×32 (VS Code)" | `screen` tem `cols, rows` | ok, sem exigência | — |
| E13 | Histórico: "Início do histórico guardado no PC" | `screen.history` não diz se acabou | `result.data{lines[], first_line, reached_start: bool}` | M |
| E14 | Envio: mensagens distintas para tela mudou / escrita expirou / grande demais / limite | Só `stale` e `already_resolved` definidos | Enumerar `code`: `stale`, `not_armed`, `too_large`, `rate_limited`, `session_ended`, `already_resolved`, `step_up_required`, `step_up_invalid`, `policy_off`. Cada código tem texto próprio em `textos.md`. | M |
| E15 | "A conexão caiu durante o envio. Conferindo…" | `cmd.status` existe | ok, e o cliente precisa guardar o `cmd.id` pendente **em memória** até a reconexão | — |
| E16 | Aparelhos e segurança: "Aparelhos com acesso a LUCAS-PC" (este + outros, visto há…) | Não há comando de leitura de aparelhos | `devices.list → [{name, last_seen_at, connected, is_self}]`, sem chaves nem ids de outros. Só leitura: revogar outro só no PC (pergunta Q6). | D |
| E17 | Atividade recente deste celular | Não há leitura de audit | `audit.list{limit ≤ 20}`, **filtrado pelo agente para o `device_id` autenticado**, só com metadados (ação, sessão, hora, contagem de caracteres). | D |
| E18 | "Remover LUCAS-PC deste celular" | Sem auto-revogação | `device.forget{step_up?}`: o agente marca `revoked_at`, registra no audit e fecha a conexão com 4403. O celular apaga a chave do Keystore. | M |
| E19 | Tela "Este celular foi removido" | 4403 fecha sem dados | `close reason = {"code":"revoked","at":…}` (JSON curto no reason do WS, ≤ 123 bytes) | M |
| E20 | Tela "Acesso remoto cortado em LUCAS-PC" (kill switch) | Não existe | Novo código de fechamento **4410 `cut`**, e a ponte responde "agente recusando" enquanto o corte durar. Diferente de 4403: o aparelho **não** foi revogado e volta sozinho quando o PC reativar. | M |
| E21 | "Atualize a Pipa: o PC usa uma versão mais nova" | `hello{protocols:[1]}` sem falha amigável | Se não houver versão comum: close **4426** com `{"min_client":"x.y"}`. | M |
| E22 | Encerrar terminal com biometria | `session.terminate` com step-up | ok, usar E6 | — |
| E23 | Configurações: "ponte alcançável · 182 ms" | — | Medido pelo cliente (RTT do ping WS). Sem exigência. | — |
| E24 | Notificação opaca: "Algo pede sua atenção em LUCAS-PC" | Push citado na visão | Push FCM **só** com `{agent_id, attention_id}`, prioridade alta, sem `notification` (data-only). O app monta o texto com o `agent_name` local (E1). Se o app não conhece o `agent_id`, usa `notif.attn_unknown`. | M |
| E25 | "Escrita liberada" visível em **outro** celular do mesmo PC | Evento de grant é por aparelho | `grant.armed` vai para todos os aparelhos conectados, com `device_name`, para eles saberem que outro está no controle. | D |
| E26 | Estado "iniciando / perdido" | `starting`, `lost` existem | ok | — |

## 2. Pareamento (código de 12 dígitos)

| # | Tela | Falta | Proposta | Prio |
|---|---|---|---|---|
| P1 | Celular: "Confira no PC" + código de confirmação `482 913` | A proposta cita SAS de 6 dígitos | Derivar o SAS dos dois lados a partir da transcrição SPAKE2 (`HKDF(K, "trcp-sas-v1") mod 10^6`), exibido `NNN NNN`. | M |
| P2 | PC: modal "Permitir 'Pixel 8'?" | Nome do aparelho no pareamento | O celular envia `device_name` (editável na tela, padrão = modelo) **dentro** do canal SPAKE2 já cifrado. | M |
| P3 | Erros distintos: expirado, errado, recusado, sem confirmação a tempo, ponte fora | Estados do rendezvous | A ponte/agente respondem `pair.error{code: expired\|wrong_code\|rejected\|confirm_timeout\|busy}`. `wrong_code` **invalida** o código (uso único, anti-força-bruta). Confirmação no PC expira em 60 s. | M |
| P4 | Webview: "Pixel 8 leu o código" | O agente sabe; falta chegar à extensão | Ver IPC I3 | M |
| P5 | QR | Conteúdo | `pipa://pair?c=482191372055&b=ponte.gariolilabs.com&v=1` (o celular valida `b` contra a lista de pontes conhecidas; se for outra, pergunta). | M |

## 3. IPC extensão VS Code ↔ agente `trcd` (local)

A extensão é uma view fina. Tudo que ela mostra vem do agente por IPC local
(named pipe no Windows, com ACL do usuário).

| # | Superfície | Necessidade |
|---|---|---|
| I1 | Barra de status | `state{agent: running\|stopped, remote: on\|cut, connected_devices[], armed[]: {device_name, session_id, until}}`, com push a cada mudança |
| I2 | Painel "Conectar celular" | `pair.start → {code, expires_at, bridge}`, `pair.cancel`, `pair.renew` |
| I3 | Painel + modal | Eventos `pair.claimed{device_name, sas}` (abre o modal), `pair.done`, `pair.failed{code}` |
| I4 | Modal "Permitir?" | `pair.confirm{accept: bool}`, que precisa chegar em ≤ 60 s |
| I5 | Aba do terminal | `grant.armed/disarmed{session_id, device_name, until}`, para trocar o nome (`onDidChangeName`) e a barra de status |
| I6 | Árvore Pipa | `devices.list` (todos, com `last_seen_at` e `connected`), `device.revoke{device_id}`, `activity.recent{limit}` |
| I7 | Kill switch | `remote.cut` / `remote.restore`. O corte fecha todas as conexões com 4410 e **persiste** no disco (pergunta Q5). |
| I8 | Retirar escrita | `grant.disarm{session_id \| "*"}` |
| I9 | Política | `policy.get/set{write_enabled, arm_max_min, audit_input}`, ligado às configurações `pipa.*` |
| I10 | Terminal remoto | Já coberto pela arquitetura: a extensão é a view do PTY do agente (`Pseudoterminal`) |

## 4. Não exigir (decisões de privacidade que o protocolo deve manter)

- Nenhum campo de tela ou de contexto vai no push.
- `audit.list` nunca devolve o texto digitado, nem quando `audit_input` está
  ligado no PC. Esse texto fica só no PC.
- O celular não recebe `pubkey` nem `device_id` de outros aparelhos.
