# Privacidade — política de dados da Pipa (P6)

Status: rascunho de planejamento, 2026-09-26. Entrega P6 do
`docs/plans/00-mapa-do-planejamento.md`. Documento de engenharia: diz o que
cada parte do sistema guarda, mostra, transmite e apaga, e por quanto
tempo. Não é o texto jurídico da loja; os rascunhos públicos estão nos
anexos A e B, rotulados **RASCUNHO**.

Atualizado em 2026-09-26: `ponte.gariolilabs.com` é **privada** (só Sr.
Garioli e quem ele autorizar); não há ponte pública, e os demais usuários
rodam a própria ponte (ADR-0004, ADR-0006). §0.2, §2, §7, §11.1, §12.2,
§14 (DP1), §15 (PA11) e os anexos A e B foram ajustados.

Não muda telas aprovadas (`docs/interfaces/`) nem ADRs. Onde um documento
aprovado conflita com outro, o conflito vai para §15 ("Pontos em aberto");
onde é preciso escolher, vai para §14 ("Decisões pendentes").

## 0. Sobre este documento

### 0.1 Rótulos

- **[FATO]**: conferido em 2026-09-26 em fonte oficial, com o link ao lado
  e em §16.
- **[INFERÊNCIA]**: conclusão a partir de fatos; precisa de confirmação
  (jurídica, quando for sobre lei; em M0–M8, quando for técnica).
- **[DECIDIDO]**: já decidido num ADR, na spec aprovada ou numa tela
  aprovada; a fonte vem ao lado.
- **[PROPOSTA P6]**: escolha desta entrega, pelo lado mais privado, sujeita
  à revisão deste documento. Números marcados também com [P8] seguem a
  medição de P8.
- **Não é parecer jurídico.** Os trechos de lei estão transcritos da fonte
  oficial; a aplicação deles ao produto é **[INFERÊNCIA]** e pede um
  advogado antes da publicação na loja e antes de M6 (ponte no ar).

### 0.2 Resumo

1. O conteúdo dos terminais (saída, tela, histórico, texto digitado) fica
   **no PC**. Ao celular vai só o que a pessoa abre, cifrado ponta a ponta,
   e **nada disso é gravado no celular** (ADR-0012).
2. A ponte vê só **metadados**: IPs, horários, volume, o ID de
   roteamento do PC e o número de encontro de 4 dígitos. Nunca vê
   conteúdo nem chaves (ADR-0004). `ponte.gariolilabs.com`, operada pela
   Garioli Labs, é **privada**: serve só Sr. Garioli e quem ele
   autorizar; os demais usuários rodam a própria ponte (§7.1).
3. O Google (FCM) vê só um aviso opaco `{agent_id, attention_id}` e o
   identificador de instalação do app (ADR-0014).
4. Não há conta, telemetria, analytics nem envio automático de relatório
   de erro no MVP.
5. Outros programas do PC (primeiro: claude-hadouken) poderão mandar
   avisos curtos ao celular pela entrada local de avisos (EX1): mesmo
   túnel, mesmo push opaco, conteúdo mínimo (§6.3).
6. Há um ponto jurídico que pode mudar o desenho da ponte: a guarda de
   registros de acesso do Marco Civil (§7.4, decisão pendente DP1).

## 1. Princípios

| # | Princípio | Base |
|---|---|---|
| PR-1 | O PC é o dono dos dados. O que é conteúdo nasce e fica no PC. | ADR-0001, ADR-0012; auditoria §7.3 |
| PR-2 | Ao celular vai só o que uma tela aprovada mostra, e só quando a pessoa abre. | spec §16 PV6; ADR-0007 |
| PR-3 | Nada de conteúdo é persistido fora do PC. No celular, só memória. | ADR-0012; spec PV2 |
| PR-4 | Quem opera infraestrutura (ponte, FCM) vê só metadados e IDs opacos. | ADR-0004, ADR-0014 |
| PR-5 | Toda retenção tem prazo escrito neste documento; o que não tem prazo aqui não é guardado. | [PROPOSTA P6] |
| PR-6 | Relaxar privacidade depois é fácil; endurecer quebra expectativas. Na dúvida, guardar menos. | auditoria §9 item 7; ADR-0012 |
| PR-7 | Mensagens de depuração e logs nunca levam conteúdo de tela, texto digitado nem nomes de sessão. | spec PV10 |

## 2. Onde os dados vivem

```text
 PC do usuário (perímetro: conta do Windows)       Celular Android
┌───────────────────────────────────────┐        ┌───────────────────────┐
│ VS Code + extensão ── pipe local ──┐  │        │ App Pipa              │
│ Claude Code ── HTTP hook loopback ─┤  │        │ • memória: telas,     │
│ outros programas ── avisos (EX1) ──┤  │        │   lista, pedidos,     │
│                                    ▼  │        │   avisos              │
│ trcd (agente): PTYs, emulador VT,     │        │ • DataStore cifrado:  │
│ Event Log, audit, aparelhos,          │        │   PCs pareados        │
│ chave no DPAPI                        │        │ • Keystore: chave     │
└──────────────┬────────────────────────┘        └───────────┬───────────┘
               │ saída WSS                          saída WSS │
               ▼                                              ▼
        ┌──────────────────────────────────────────────────────────┐
        │ Ponte (própria, ou ponte.gariolilabs.com, privada):      │
        │ vê IPs, horários, volume, ID de roteamento,              │
        │ 4 dígitos de encontro                                    │
        └──────────────────────────────────────────────────────────┘
               └──── túnel TLS 1.3 mútuo ponta a ponta (a ponte só
                     repassa registros cifrados) ────┘

 Google FCM (a partir de M8): {agent_id, attention_id} + ID de instalação
```

## 3. Inventário de dados

Colunas: **Dado** · **Onde nasce** · **Onde fica** · **Quem vê** ·
**Retenção** · **Como apagar** · **Base**. "Dono do PC" é quem usa a conta
do Windows onde o agente roda.

### 3.1 No PC (agente `trcd` e extensão)

| Dado | Onde nasce | Onde fica | Quem vê | Retenção | Como apagar | Base |
|---|---|---|---|---|---|---|
| Saída bruta do PTY (bytes VT) | programas no terminal | só em trânsito na memória do agente | dono do PC (pelo VS Code, canal `pty.*`) | nunca persistida | — | ADR-0012; spec PV1, §9.10 |
| Tela e histórico (emulador VT) | emulador do agente | memória do agente | dono do PC; celular pareado, sob demanda, como texto já interpretado | vida da sessão + 60 min depois do fim [P8]; histórico até 2 000 linhas [P8] | fim do prazo (`session.removed`); parar o agente | ADR-0007; spec R9.26, §14 |
| Texto digitado (celular ou PC) | teclado | vai ao PTY; não é guardado | o programa do terminal | nunca persistido; o audit guarda só a contagem | — | ADR-0012; spec R6.25 (ver DP3) |
| Event Log (sessões, pedidos, escritas, política) | agente | memória, ou disco do agente (R8.2 permite) | dono do PC inteiro; celular projetado (PV5, PV6) | 24 h ou 10 000 eventos, o que for menor [P8] | automático; época nova a cada início | ADR-0007; spec R8.18 |
| Resultados guardados para `cmd.status` | agente | memória | o aparelho que enviou | 256 por aparelho, por época [P8] | reinício do agente | spec R10.2 |
| Contexto da sessão (comando em execução, último comando, estado do Claude Code) | integração de shell, hook, heurística | memória do agente [PROPOSTA P6] | dono do PC; celular, redigido (§5) | vida da sessão + 60 min | fim do prazo | spec §11.7, D-14 (ver DP5) |
| Pedidos de atenção (`Attention`) | hook do Claude Code ou heurística | memória do agente [PROPOSTA P6] | dono do PC; celular, redigido | até resolvido e enquanto a sessão estiver retida | fim do prazo | ADR-0008; spec §11.7 (ver DP5) |
| Avisos de outros programas (EX1) | programa local autorizado (claude-hadouken) | memória do agente [PROPOSTA P6] | celulares pareados; dono do PC | até 24 h, até ser dispensado, ou reinício do agente (§6.3) | dispensar; fim do prazo | `docs/exigencias-externas.md` EX1 |
| Registro mínimo de sessões abertas `{id, name, created_at}` | agente | disco do agente | agente (só para mostrar `lost` depois de um reinício) | enquanto a sessão existe; depois de um reinício, até a sessão `lost` sair do snapshot (60 min) [PROPOSTA P6] | automático | spec R8.5, D-18 |
| Aparelhos pareados `{device_id, device_name, chave pública, permissões, paired_at, last_seen_at, estado}` | pareamento | disco do agente | dono do PC; cada celular vê nome e "visto há" dos outros, sem id nem chave | até revogar ou esquecer | Revogar no PC; Remover no celular | spec §6.3, PV5; auditoria §7.2 |
| Registro de revogado/esquecido `{fingerprint, state, at}` | revogação ou esquecimento | disco do agente | agente (para fechar com 4403 e mostrar "removido às…") | **90 dias** [PROPOSTA P6], alinhado ao audit | automático | spec R6.3 |
| Token de push de cada aparelho | celular (`push.register`, M8) | disco do agente (e do remetente, P4/P5) | agente; remetente do push | até revogar, esquecer ou chegar token novo | Revogar; Remover | spec R10.45 |
| Audit (conexões, escrita liberada, envios com contagem de caracteres, respostas, encerrar, pareamento, revogação, corte, política) | agente | disco do agente | dono do PC (`activity.recent`); cada celular, só as próprias entradas e só metadados (`audit.list`) | **90 dias** (texto aprovado `devices.audit_note`) | expurgo diário automático; apagar dados do PC (DP6) | spec R6.25–R6.27, PV4 |
| Política `{write_enabled, arm_max_min, audit_input}` e estado de corte | configurações e kill switch | disco do agente + `settings.json` do VS Code (`pipa.*`, escopo `machine`) | dono do PC; celular recebe a política sem `audit_input` | até mudar | mudar a configuração; apagar dados do PC | spec R6.17, R6.20, R6.21; `interfaces/vscode.md` §10 |
| Chave privada do agente | instalação | cofre do SO (DPAPI via `keyring`) | só o agente a usa | permanente | apagar dados do PC (DP6) | ADR-0004; auditoria §7.2 |
| `agent_id` e `agent_name` (padrão: hostname) | instalação | disco do agente | celulares pareados; a ponte vê só o ID de roteamento (§7) | permanente; nome editável | apagar dados do PC; renomear | spec R5.6, E1 |
| Token do hook por sessão | agente, ao abrir a sessão | memória do agente e ambiente do PTY | processos daquele terminal | vida da sessão | fim da sessão | ADR-0008; auditoria §6 T17 |
| Código de 12 dígitos, QR e código de confirmação (SAS) | pareamento | memória do agente e da extensão | tela do PC e o celular que pareia | 5 min, uso único; nunca no log | automático | ADR-0004; spec R8.30, D-11 |
| Pergunta "perfil padrão" já feita | extensão | estado da extensão no VS Code | extensão | permanente | desinstalar a extensão | ADR-0002 |
| Log de diagnóstico do agente | agente | arquivo local na pasta do agente | dono do PC | 7 dias ou 10 MB, o que vier antes [PROPOSTA P6] | automático; apagar o arquivo | spec PV10 |

### 3.2 No celular

| Dado | Onde nasce | Onde fica | Quem vê | Retenção | Como apagar | Base |
|---|---|---|---|---|---|---|
| PCs pareados `{agent_id, agent_name, bridge, fingerprint}` | pareamento; `agent_name` atualizado a cada `hello` | DataStore cifrado | só o app | até "Remover {pc} deste celular" ou desinstalar | Remover o PC; desinstalar | ADR-0012; spec R5.6, PV2 |
| Chave do aparelho (e a de escrita, se P5 separar) | pareamento | Android Keystore, não exportável | ninguém lê; o app só usa | idem | Remover o PC (o app apaga a chave, fluxo F6); desinstalar | ADR-0003; `interfaces/fluxos.md` F6 |
| Linhas da tela, histórico carregado, lista de terminais, contextos, pedidos, avisos | túnel, sob demanda | memória (`ViewModel`) | a pessoa com o celular na mão; `FLAG_SECURE` bloqueia print e prévia em "Recentes" | até o app ficar mais de 5 min fora do primeiro plano ou o processo morrer; sem rede, a tela antiga é descartada | automático | ADR-0012; `interfaces/android.md` §0; fluxo X7 (ver PA1) |
| Posição no log (`epoch`, último `seq`) e `cmd.id` pendente | protocolo | memória | app | enquanto o processo vive | automático | spec R8.11, E15 |
| Texto no campo de comando | teclado | memória | a pessoa | enquanto a tela vive ("Seu texto continua aqui") | automático | fluxo X9, X11 |
| Nome deste celular (`device_name`, padrão `Build.MODEL`) | tela de pareamento | enviado ao PC dentro do canal SPAKE2; o app mostra o que o PC devolve em `devices.list` | dono do PC; outros celulares do mesmo PC | o do registro de aparelhos no PC | Remover o PC | `interfaces/android.md` §2; exigências P2 |
| Token FCM / ID de instalação do Firebase | Firebase SDK (M8) | armazenamento do SDK no app; servidores do Google; agente | Google; agente; remetente do push | até o app apagar o token (§8.3) ou desinstalar | Remover o último PC; desinstalar | ADR-0014 |
| Preferências (bloquear capturas, biometria ao abrir, idioma, tema, ponte; origens de aviso silenciadas, se P7 puser no celular) | a pessoa | armazenamento do app | só o app | até mudar ou desinstalar | desinstalar | `interfaces/android.md` §12, §13; EX1 |
| Notificação exibida ("Algo pede sua atenção em LUCAS-PC") | app, a partir do push | sistema Android; tela de bloqueio (`VISIBILITY_PUBLIC`) | quem vê o celular, mesmo bloqueado | até resolver ou descartar | cancelada ao resolver | `interfaces/android.md` §11 (ver PA6) |
| Texto copiado da tela | a pessoa ("selecionável para copiar") | área de transferência do Android | apps com acesso à área de transferência | regra do sistema | a pessoa sobrescreve | `interfaces/android.md` §7 (ver RQ-8) |

### 3.3 Na ponte

Detalhes, logs e o ponto do Marco Civil em §7.

| Dado | Onde nasce | Onde fica | Quem vê | Retenção | Como apagar | Base |
|---|---|---|---|---|---|---|
| IP e porta de origem do agente e do celular | conexão de saída | memória da ponte | operador da ponte; provedor de hospedagem | duração da conexão [PROPOSTA P6] | fechar a conexão | ADR-0004; proposta §7 |
| Contadores de tentativa por IP (anti-abuso) | tentativas de encontro | memória | operador | janela de no máximo 1 h [PROPOSTA P6] | automático | proposta §7 ("limita tentativas por IP") |
| ID de roteamento do PC | registro do agente na ponte | memória | operador | enquanto o agente está conectado | automático | ADR-0004 |
| Presença (`online`, `since`) | conexão e queda do agente | memória | operador; celulares que consultam (E2) | até 7 dias depois da queda, ou reinício da ponte [PROPOSTA P6]; depois o celular usa o último contato que ele mesmo teve (substituto de E2) | automático | spec §17; exigências E2 |
| Número de encontro (4 dígitos) | código de pareamento | memória | operador | até o uso ou 5 min | automático | ADR-0004 |
| Horários, duração e volume (bytes, tamanho dos registros) | tráfego | memória, só por conexão | operador; provedor | duração da conexão; métricas só agregadas, sem IP nem ID [PROPOSTA P6] | automático | ADR-0004; proposta §7 |
| Registros TLS do túnel (conteúdo cifrado, inclusive avisos EX1) | agente e celular | só em trânsito | ninguém consegue ler | não guardados | — | ADR-0004; spec §6.1 |
| Registros de acesso (IP + data e hora) por 6 meses | — | **não existe hoje** | — | ver DP1 | — | Marco Civil art. 15 (§7.4) |

### 3.4 No Google

| Dado | Onde nasce | Onde fica | Quem vê | Retenção | Como apagar | Base |
|---|---|---|---|---|---|---|
| Payload do push `{agent_id, attention_id}` (só dados), também para avisos EX1 | remetente (agente ou ponte, P4/P5) | servidores do FCM, em trânsito | Google | regra do FCM | — | ADR-0014; spec R10.46 |
| ID de instalação do Firebase / token | Firebase SDK | servidores do Google | Google | até a chamada de exclusão; depois até 180 dias para sair dos backups **[FATO]** | o app apaga (§8.3) | Firebase, "Privacy and Security" |
| Metadados de entrega (hora, aparelho, prioridade) | FCM | Google | Google; exportação para BigQuery só se ligada | regra do Google | não ligar a exportação [PROPOSTA P6] | Firebase, "Understanding message delivery" |
| Dados da instalação pela Play Store e Android vitals | Google Play | Google | Google; Garioli Labs vê agregados no Play Console | regra do Google | — | Play Console Help (§9) |

### 3.5 Nas entradas locais do agente

Detalhes em §6.

| Dado | Onde nasce | Onde fica | Quem vê | Retenção | Como apagar | Base |
|---|---|---|---|---|---|---|
| JSON do evento do hook (`Notification`, `PermissionRequest`, `Stop`) | Claude Code | POST para `127.0.0.1` do agente | agente | memória, só até virar `Attention`/`Context`; o resto é descartado na chegada [PROPOSTA P6] | automático | ADR-0008 |
| `transcript_path` | Claude Code | caminho recebido | agente | descartado; o agente **nunca lê** o transcript no MVP | — | auditoria §7.3; ADR-0008 |
| Aviso de outro programa `{origin, title, text, severity}` | programa local (claude-hadouken) | entrada local de avisos → memória do agente | celulares pareados (pelo túnel); dono do PC | até 24 h, dispensa ou reinício do agente [PROPOSTA P6] | dispensar; automático | EX1; §6.3 |
| Identidade de quem chama a entrada de avisos | programa local | memória do agente (e registro de origens autorizadas, P5) | agente | enquanto autorizado | revogar a origem (P5/P7) | EX1 (autenticação: P5) |

## 4. O que atravessa a rede

| Canal | Quem fala | O que passa | O que não passa | Cifra |
|---|---|---|---|---|
| Pipe local (perfil local) | extensão ↔ agente | tudo, inclusive saída bruta (`pty.*`) e `device_id` | nada sai do PC | local, na conta do usuário |
| HTTP hook loopback | Claude Code → agente | JSON do evento (§6) | nada sai do PC | loopback + token por sessão |
| Entrada local de avisos (EX1) | programa local → agente | `{origin, title, text, severity}` | nada sai do PC por este canal; o agente projeta e envia pelo túnel | transporte local e autenticação: P3/P5 |
| Agente ↔ ponte (WSS) | agente | registro na ponte, ID de roteamento, registros TLS do túnel | conteúdo TRCP | TLS até a ponte + túnel por dentro |
| Celular ↔ ponte (WSS) | celular | pedido de conexão ao ID, número de encontro no pareamento, consulta de presença, registros TLS | conteúdo TRCP, `device_name`, segredo de 8 dígitos | idem |
| Túnel ponta a ponta | celular ↔ agente | TRCP projetado: lista, contexto redigido, pedidos redigidos, avisos, tela sob demanda, comandos | bytes VT crus, OSC, títulos, links, área de transferência, ids e chaves de outros aparelhos, `audit_input`, texto digitado de volta | TLS 1.3 mútuo com chaves fixadas (P5) |
| FCM | remetente → Google → celular | `{agent_id, attention_id}` | nome de sessão, comando, saída, nome do PC, título ou texto de aviso | HTTPS do Google |

## 5. Redação (PV9)

A spec deixa para P6 a redação de `subject.value`, `detail` e dos textos
de contexto antes de saírem do PC (spec §11.7, PV9). **[PROPOSTA P6]**:

- **RD-1 Onde:** no agente, na projeção para o perfil remoto (spec R8.6),
  antes do corte de tamanho. O perfil local recebe o texto original: a
  pessoa está no PC.
- **RD-2 Campos:** `Attention.subject.value`, `Attention.detail`,
  `Context.running_command.text`, `Context.last_command.text`,
  `Context.tool.detail` e, para avisos EX1, `title` e `text` (§6.3).
- **RD-3 O que é trocado por `•••`:**
  - blocos de chave privada (`-----BEGIN … PRIVATE KEY-----` até o fim);
  - credencial em URL (`esquema://usuário:senha@`): só a senha;
  - atribuições e flags com nome sensível, em qualquer caixa:
    `PASSWORD`, `PASSWD`, `PWD` quando atribuído, `SECRET`, `TOKEN`,
    `API_KEY`, `APIKEY`, `ACCESS_KEY`, `PRIVATE_KEY`, `CREDENTIAL`,
    `AUTH`; formas `NOME=valor`, `--nome=valor`, `--nome valor`,
    `-H "Authorization: …"`: só o valor;
  - `Bearer <token>` e `Basic <base64>`: só o token;
  - formatos conhecidos de token: prefixos `ghp_`, `gho_`, `ghs_`,
    `github_pat_`, `xox[abpr]-`, `AKIA`, `AIza`, `sk-`, `sk-ant-`,
    `glpat-`, `npm_`; e JWT (`eyJ….eyJ….…`);
  - sequência contínua de 32 caracteres ou mais em base64, base64url ou
    hexadecimal fora de caminho de arquivo (heurística).
- **RD-4 Marcação:** qualquer troca liga `subject.redacted: true`. O
  campo `detail` já sai redigido e sem marca própria (spec §11.7).
- **RD-5 Não é garantia.** A redação é *best-effort* (auditoria §6 T14) e
  existe para o que sai **sem a pessoa pedir** (lista, pedido, aviso,
  push). A **tela do terminal não é redigida**: é o conteúdo que a pessoa
  abriu, no aparelho dela, cifrado ponta a ponta (ADR-0007); por isso o
  `FLAG_SECURE` vem ligado.
- **RD-6 Nada de LLM** na redação nem em resumos no MVP (D-14). Um resumo
  futuro segue a auditoria §7.3: LLM local por padrão; externo só com
  opt-in explícito por sessão e depois da redação, com ADR próprio.
- **RD-7 Teste:** a lista de RD-3 vira fixtures de conformidade em P9
  (cada padrão com um caso positivo e um negativo).

Consequência de segurança: um comando redigido não aparece inteiro para
quem aprova; ver PA7.

## 6. Entradas locais do agente

### 6.1 O que o hook do Claude Code entrega (ADR-0008)

**[FATO]** (https://code.claude.com/docs/en/hooks, conferido em
2026-09-26): o HTTP hook faz POST do JSON do evento. Todo evento leva
`session_id`, `transcript_path`, `cwd`, `permission_mode`,
`hook_event_name` e, conforme a versão, `prompt_id`, `scratchpad_dir` e
`effort`. Por evento:

- `Notification`: `message`, `title`, `notification_type`
  (`permission_prompt`, `idle_prompt`, `elicitation_dialog`,
  `agent_needs_input`, entre outros);
- `PermissionRequest`: `tool_name`, `tool_input` (argumentos da
  ferramenta), `permission_suggestions`, `tool_use_id`;
- `Stop`: `last_assistant_message` (o texto final do assistente no turno).

**[INFERÊNCIA]** `tool_input` pode conter o conteúdo inteiro de um
arquivo (ferramentas de escrita) e comandos com segredos. É o campo mais
sensível que chega ao agente.

### 6.2 O que o agente faz com o hook — [PROPOSTA P6]

| Campo | Uso | Sai para o celular? |
|---|---|---|
| `notification_type` | vira `Attention.kind` (M5 confirma a tabela) | sim, como `kind` |
| `tool_name` | `Context.tool.last_tool` | sim |
| `tool_input` de comando (shell) | `subject{type:"command"}` | sim, redigido (§5), até 1 KB; cortado ⇒ `destructive` (R11.1) |
| `tool_input` de arquivo | só o caminho: `subject{type:"file"}`, com a pasta do usuário como `~` | só o caminho; **conteúdo nunca** |
| `tool_input` de outras ferramentas | resumo de até 256 caracteres em `detail` | redigido |
| `message`, `title` | `detail` do pedido | redigido, até 1 KB |
| `cwd` | `Attention.cwd` | sim, com `~` (PV8) |
| `last_assistant_message` | só para derivar o estado (`idle`, `finished`) | **não** (sem resumos em v1, D-14) |
| `transcript_path` | nenhum | não; nunca lido |
| `session_id`, `prompt_id`, `tool_use_id` | correlação interna, se M5 precisar | não |
| `permission_mode`, `effort`, `scratchpad_dir`, `permission_suggestions` | nenhum | não |

- **HK-1** Nada do JSON do hook é gravado em disco, nem no log de
  diagnóstico. O audit registra só a decisão (`attn_allow`/`attn_deny`),
  a hora, o aparelho e o nome da sessão (spec R6.25).
- **HK-2** O corpo do POST é descartado assim que o `Attention` e o
  `Context` são montados.
- **HK-3** O token do hook fica no ambiente do PTY: **[INFERÊNCIA]**
  qualquer processo daquele terminal consegue lê-lo. Isso é aceito
  porque quem roda no terminal já tem o poder do usuário (PC comprometido
  está fora de escopo, auditoria §6); a proteção é contra outros
  processos e sessões (T17). Confirmação: P5.

### 6.3 Avisos de outros programas (EX1)

Origem: `docs/exigencias-externas.md` EX1 (ordem de Sr. Garioli de
2026-09-26). O agente expõe uma entrada local para programas do PC
mandarem um aviso curto ao celular; o primeiro cliente é o
claude-hadouken (alertas de consumo e de tarefa terminada). Transporte,
autenticação, esquema final e limite de taxa são de P3/P5/P8; tela e
silenciar uma origem, de P7. Aqui ficam o conteúdo permitido e a
retenção. **[PROPOSTA P6]**:

**Conteúdo permitido**

| Campo | Regra |
|---|---|
| `origin` | nome curto da origem autorizada (ex.: `claude-hadouken`), até 32 caracteres; o agente preenche a partir da autenticação (P5), não do texto de quem chama |
| `title` | até 64 caracteres, uma linha |
| `text` | até 256 caracteres, uma linha (sem LF, como D-22) |
| `severity` | `info`, `warning` ou `critical` |

- **AV-1 Nada de código, caminhos pessoais nem segredos.** A origem é
  responsável por não mandar; o agente reforça:
  - sem caracteres de controle (C0, DEL, C1), como R9.11;
  - redação de §5 em `title` e `text`;
  - pasta do usuário trocada por `~` (como PV8), e qualquer outro caminho
    absoluto trocado pelo nome do arquivo;
  - acima do limite, corta e marca `truncated`.
- **AV-2 Sem anexos, links nem ações.** Um aviso só informa. Link
  clicável ou botão que age no PC exigiria desenho e revisão de
  segurança (T9).

**Retenção com o celular offline**

- **AV-3** O aviso vive **só na memória do agente**, como um pedido de
  atenção sem sessão (inferência de EX1, a confirmar em P3). Nunca vai
  para o disco, mesmo que o Event Log seja persistido (R8.2).
- **AV-4** Validade: **24 h** (igual à retenção do log), ou menos se a
  origem pedir. Depois disso some, entregue ou não. Reinício do agente
  descarta os pendentes.
- **AV-5** Dispensado no celular ou no PC, some para todos os aparelhos.
- **AV-6** No máximo **20 avisos pendentes por origem** [P8]; acima
  disso, os mais antigos saem.
- **AV-7** O audit não registra o texto do aviso; no máximo a origem, a
  severidade e a hora, se P5 quiser rastrear abuso da entrada.

**O que chega pelo push**

- **AV-8** O mesmo payload opaco `{agent_id, attention_id}` (ADR-0014,
  PV3). Título e texto do aviso **nunca** vão ao FCM; o app busca o aviso
  pelo túnel ao acordar (spec R10.47).
- **AV-9** A notificação do Android usa os textos opacos aprovados
  (`notif.attn`). Mostrar o título do aviso na notificação seria uma
  mudança de tela e de visibilidade na tela de bloqueio: PA13.

## 7. A ponte e a Garioli Labs como operadora de metadados

### 7.1 O que a ponte vê e o que nunca vê

**[DECIDIDO]** A ponte é burra por construção: associa um ID a uma
conexão e copia bytes; sem disco, sem banco, sem chaves de sessão
(ADR-0004; proposta §4).

**[DECIDIDO]** Não há ponte pública padrão (Sr. Garioli, 2026-09-26;
ADR-0004): `ponte.gariolilabs.com` é **privada** e serve só Sr. Garioli
e quem ele autorizar, com chave de inscrição emitida por ele (formato,
emissão e revogação em P4). Os demais usuários rodam a própria ponte, com
o mesmo binário, num servidor, VPS ou Raspberry (ADR-0006). Assim, a
Garioli Labs só opera metadados de usuários autorizados. O que esta seção
diz do "operador" vale para a Garioli Labs nesses casos e, nas pontes
próprias, para quem as opera (BR-6).

| Vê | Nunca vê |
|---|---|
| IPs do PC e do celular | conteúdo TRCP (telas, comandos, nomes de sessão, avisos) |
| horários de conexão e desconexão, duração | chaves privadas ou de sessão |
| volume e tamanho dos registros cifrados | o segredo de 8 dígitos e o código de confirmação |
| o ID de roteamento do PC | `agent_name`, `device_name` (vão dentro do túnel ou do canal SPAKE2) |
| o número de encontro de 4 dígitos, durante o pareamento | quem é a pessoa: não há conta nem login |
| **[INFERÊNCIA]** que um mesmo IP de celular se liga a um mesmo PC (padrão de uso) | |

**[INFERÊNCIA]** Os IPs, combinados com horários e com o ID do PC, podem
identificar uma pessoa; por isso são tratados aqui como dado pessoal
(LGPD art. 5º I, §12).

### 7.2 Retenção mínima proposta — [PROPOSTA P6]

- **BR-1** Tudo o que está em §3.3 vive **só em memória**, com o prazo
  da tabela. Reiniciar a ponte apaga tudo.
- **BR-2** Nenhum log com IP, ID de roteamento, número de encontro ou
  presença, nem em arquivo nem em `stdout`/`stderr`.
- **BR-3** Métricas operacionais só agregadas e sem identificador:
  conexões ativas, encontros por minuto, erros por tipo, bytes totais.
  Retenção das métricas: 30 dias.
- **BR-4** Log de erro sem IP e sem ID: tipo do erro, hora, versão.
  Retenção: 30 dias.
- **BR-5** **[INFERÊNCIA]** Plataformas de hospedagem gravam sozinhas logs
  de requisição com o IP de origem (proxy reverso, balanceador, logs de
  plataforma). Em M6, o plano da ponte lista cada log da plataforma
  escolhida e o desliga, ou reduz ao prazo mínimo que a plataforma
  permitir, registrando o que não der para desligar. Verificar na
  documentação do provedor escolhido.
- **BR-6** Uma ponte própria segue a política de quem a opera; o binário
  vem com BR-1 a BR-4 como padrão.

### 7.3 Provedor de hospedagem

**[INFERÊNCIA]** O provedor da máquina (VPS, Google Cloud) vê o mesmo que
a ponte vê de fora: IPs, horários e volume (proposta §4.1: "o provedor só
vê bytes cifrados, IPs e horários"). Pela LGPD, ele trata esses dados em
nome da Garioli Labs (operador, art. 5º VII). Se a ponte ficar fora do
Brasil (a opção e2-micro fica nos EUA, ADR-0006), há transferência
internacional de dados (art. 33); ver DP4.

### 7.4 Marco Civil: guarda de registros de acesso

**[FATO]** Lei nº 12.965/2014, art. 15
(https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2014/lei/l12965.htm):
"O provedor de aplicações de internet constituído na forma de pessoa
jurídica e que exerça essa atividade de forma organizada, profissionalmente
e com fins econômicos deverá manter os respectivos registros de acesso a
aplicações de internet, sob sigilo, em ambiente controlado e de segurança,
pelo prazo de 6 (seis) meses, nos termos do regulamento." O art. 5º VIII
define esses registros como "o conjunto de informações referentes à data e
hora de uso de uma determinada aplicação de internet a partir de um
determinado endereço IP". O §3º exige ordem judicial para entregá-los.

**[INFERÊNCIA]** Se a Garioli Labs for pessoa jurídica e operar a ponte
com fins econômicos (por exemplo, se a Pipa for paga ou fizer parte
de uma oferta paga), ela pode estar obrigada a guardar IP + data e hora
de uso por 6 meses. Isso **conflita** com "sem disco" do ADR-0004
(PA4) e muda a retenção de BR-1. Não cabe a este documento decidir:
DP1.

**[INFERÊNCIA]** Com a ponte privada (decisão de 2026-09-26),
`ponte.gariolilabs.com` deixa de ser oferecida ao público: atende Sr.
Garioli e quem ele autorizar. Isso provavelmente diminui o peso do art.
15 (uso pessoal e de convidados, sem oferta ao público), mas não o afasta
por si só; o parecer jurídico antes de M6 (DP1, opção c) continua. As
pontes próprias de outros usuários são de quem as opera.

## 8. Push pelo FCM (ADR-0014)

### 8.1 O que o Google vê

- **[DECIDIDO]** Payload só de dados com `{agent_id, attention_id}`;
  nada de comando, nome de sessão, saída ou nome do PC (ADR-0014; spec
  R10.46). O texto "Algo pede sua atenção em LUCAS-PC" é montado no app.
  Vale também para os avisos EX1 (AV-8).
- **[FATO]** Uma mensagem só de dados contém só os pares chave-valor
  definidos pelo remetente, é tratada pelo app, e o limite é 4096 bytes
  (https://firebase.google.com/docs/cloud-messaging/customize-messages/set-message-type).
- **[FATO]** O FCM usa o ID de instalação do Firebase para saber a que
  aparelho entregar, e o Firebase o guarda até o cliente do Firebase
  chamar a API de exclusão; depois disso, sai dos sistemas ativos e dos
  backups em até 180 dias (https://firebase.google.com/support/privacy).
- **[FATO]** O SDK do FCM coleta automaticamente a versão do app e um
  "Firebase user agent" (metadados do aparelho, versões de SDK, app
  instalador), cifrados em trânsito
  (https://firebase.google.com/docs/android/play-data-disclosure).
- **[INFERÊNCIA]** O Google sabe que um aparelho recebeu um aviso, quando,
  e que avisos com o mesmo `agent_id` vêm do mesmo PC. O `attention_id` é
  um ULID e revela o milissegundo em que o pedido foi criado (spec R7.3);
  o Google já sabe a hora do envio, então isso não acrescenta nada
  relevante.

### 8.2 Quem envia

Aberto (P4/P5/M8; spec §19.2 item 15). Efeito na privacidade:

- **Agente envia:** a Garioli Labs não vê nada do push; a credencial de
  envio fica distribuída nos PCs (risco de segurança, P5).
- **Ponte envia:** a ponte passa a saber o token de cada celular e **quando
  cada PC pede atenção**. É metadado novo para o operador. Se for o
  caminho escolhido, vale BR-1/BR-2: token e hora só em memória, sem log.

### 8.3 Requisitos — [PROPOSTA P6]

- **PS-1** Ao remover o **último** PC pareado, o app apaga o próprio
  token/ID de instalação do Firebase pela API do SDK, para disparar a
  exclusão do lado do Google. Nome exato da chamada: confirmar em M8.
- **PS-2** Sem Google Analytics, sem exportação de entrega para
  BigQuery, sem Firebase Crashlytics (§9).
- **PS-3** O push de limpeza tem o mesmo formato (spec R10.47, D-20).

## 9. Telemetria, diagnóstico e relatórios de erro

- **TL-1 Nenhuma telemetria no MVP.** Nenhum documento do planejamento
  prevê telemetria, analytics ou SDK de relatório de erro (busca em
  `docs/` em 2026-09-26). O único serviço de terceiro do MVP é o FCM
  (ADR-0005, "Consequências"). [PROPOSTA P6: manter assim.]
- **TL-2 Relatório de erro automático: nenhum**, no app, na extensão e no
  agente. O agente grava só o log local de diagnóstico (§3.1), sem
  conteúdo (PV10). Suporte: a pessoa envia o log por iniciativa própria.
- **TL-3 Android vitals.** **[FATO]** Os dados do Android vitals vêm de
  "users who have opted in to automatically share usage and diagnostics
  data", sem SDK no app
  (https://support.google.com/googleplay/android-developer/answer/9844486).
  **[INFERÊNCIA]** É coleta do Google Play, não do app; a Garioli Labs vê
  só agregados de travamentos no Play Console.
- **TL-4** Qualquer telemetria futura exige ADR novo, opt-in explícito,
  atualização deste documento, da política pública e do formulário da
  Play.
- **TL-5** Verificação de atualização do agente ou download de binários:
  não descritos no planejamento. Se existirem, entram aqui antes do código
  (PA10).

## 10. Requisitos de privacidade para a implementação

Para P9 transformar em tarefas e testes. **[PROPOSTA P6]**, salvo quando a
fonte diz outra coisa.

| # | Requisito | Onde |
|---|---|---|
| RQ-1 | Nenhum `Log.*`/`println`/`tracing` com conteúdo de tela, texto digitado, nome de sessão, comando, `subject`, `detail`, texto de aviso ou JSON de hook, em nenhum componente. Teste: fixtures com marcador em cada campo e busca do marcador nos logs. | app, agente, extensão, ponte |
| RQ-2 | O app não grava frames, histórico, eventos, contextos, pedidos, avisos nem lista de terminais em disco (spec PV2). Teste: inspeção de `files/`, `databases/`, `shared_prefs/`, `datastore/` depois de uma sessão. | app |
| RQ-3 | `android:allowBackup="false"` e `dataExtractionRules` que excluem tudo. **[FATO]** O Auto Backup vem ligado para apps com alvo 23+, até 25 MB por usuário; no Android 12+, em alguns fabricantes, `allowBackup="false"` não impede a transferência de aparelho para aparelho (https://developer.android.com/identity/data/autobackup). **[INFERÊNCIA]** Os dados pareados copiados para outro aparelho seriam inúteis (a chave do Keystore não vai junto), mas levariam o nome do PC e a ponte. | app |
| RQ-4 | `FLAG_SECURE` ligado por padrão, desligável (Q3). | app |
| RQ-5 | Descarte da tela em memória conforme `interfaces/android.md` §0 e fluxo X7 (ver PA1). | app |
| RQ-6 | Expurgos automáticos no agente: log de eventos (24 h / 10 000), audit (90 dias), revogados (90 dias), tela depois do fim (60 min), avisos EX1 (24 h), log de diagnóstico (7 dias / 10 MB). Teste com relógio simulado. | agente |
| RQ-7 | Redação §5 com fixtures (RD-7). | agente |
| RQ-8 | Ao copiar texto da tela, marcar o conteúdo como sensível: **[FATO]** `ClipDescription.EXTRA_IS_SENSITIVE` esconde a prévia do texto copiado no Android 13+ (https://developer.android.com/develop/ui/views/touch-and-input/copy-paste). Não muda a tela aprovada. | app |
| RQ-9 | Ponte: BR-1 a BR-5, com teste que procura IP e ID de roteamento em toda saída do processo. | ponte |
| RQ-10 | Hook: HK-1 e HK-2; `transcript_path` nunca aberto (teste: o arquivo não é lido). | agente |
| RQ-11 | Push: PS-1 e PS-2; payload conferido contra PV3 em fixture, inclusive para avisos EX1. | app, remetente |
| RQ-12 | Pasta de dados do agente dentro do perfil do usuário, com permissão só para ele; local exato definido em P9. | agente |
| RQ-13 | Avisos EX1: AV-1 a AV-7, com fixtures de aviso com caminho pessoal, segredo, LF e texto acima do limite. | agente |

## 11. Direitos do usuário: esquecer, revogar, cortar, desinstalar, apagar

| Ação | Onde | O que apaga ou para | O que continua | Base |
|---|---|---|---|---|
| **Remover {pc} deste celular** | celular, Aparelhos e segurança | no PC: aparelho vira `forgotten`, escritas retiradas, token de push apagado, entrada no audit; no celular: entrada do DataStore e chave | registro mínimo do esquecido (90 dias), entradas antigas do audit (até 90 dias) | spec §10.6.6, R6.2, R10.45; fluxo F6 (ver PA5) |
| **Revogar aparelho** | PC | mesmo efeito no PC; o celular cai com 4403 e mostra "removido" | registro mínimo do revogado (90 dias), audit | ADR-0013; spec R6.2, R6.3 |
| **Cortar acesso remoto** | PC | fecha todas as conexões, retira escritas, cancela pareamento | todos os dados; o corte persiste até Reativar | ADR-0013; spec R6.21 |
| **Desligar a escrita** (`pipa.write.enabled`) | PC | retira todas as escritas liberadas | leitura | spec R6.19 |
| **Silenciar uma origem de avisos** | a definir em P7 | novos avisos daquela origem deixam de chegar | a origem continua podendo chamar a entrada; P5 decide se o agente recusa | EX1 |
| **Desinstalar o app** | celular | **[INFERÊNCIA]** o Android apaga os dados do app, inclusive as chaves dele no Keystore | o aparelho continua `active` no PC até ser revogado; o token de push deixa de valer | — (ver §11.1) |
| **Desinstalar a extensão / o agente** | PC | ver DP6 | ver DP6 | — |
| **Apagar dados na ponte** | — | nada a apagar: só memória (BR-1) | se DP1 exigir registros de acesso, eles ficam pelo prazo legal | §7 |
| **Apagar no Google** | — | PS-1 dispara a exclusão do ID de instalação | até 180 dias em backups do Google **[FATO]** | §8.1 |

### 11.1 Recomendações ao usuário (vão para a política pública)

- Celular perdido: revogar o aparelho no PC; se estiver longe do PC, a
  escrita continua protegida pela biometria ou PIN (ADR-0003).
- Antes de desinstalar o app: remover os PCs pelo próprio app, para o PC
  apagar o registro e o token.
- Não há ponte pública: quem não foi autorizado por Sr. Garioli instala
  a própria ponte (`trc-bridge`) num servidor, VPS ou Raspberry e informa
  o endereço na extensão (`pipa.bridge`) na primeira vez.

## 12. LGPD

### 12.1 Fatos legais (fontes oficiais)

Lei nº 13.709/2018, texto compilado do Planalto
(https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm),
conferido em 2026-09-26:

- **[FATO]** Art. 4º I: a lei não se aplica ao tratamento "realizado por
  pessoa natural para fins exclusivamente particulares e não econômicos".
- **[FATO]** Art. 5º: dado pessoal é "informação relacionada a pessoa
  natural identificada ou identificável" (I); controlador é quem decide
  sobre o tratamento (VI); operador trata "em nome do controlador" (VII);
  encarregado é a pessoa indicada "pelo controlador e operador para atuar
  como canal de comunicação entre o controlador, os titulares dos dados e
  a Agência Nacional de Proteção de Dados (ANPD)" (VIII, redação da Lei
  nº 15.352/2026).
- **[FATO]** Art. 7º: hipóteses de tratamento, entre elas o consentimento
  (I), o cumprimento de obrigação legal (II), a execução de contrato "a
  pedido do titular" (V) e o legítimo interesse (IX).
- **[FATO]** Art. 9º: o titular tem direito a informação clara sobre
  finalidade, forma e duração, identificação e contato do controlador,
  uso compartilhado e direitos do art. 18.
- **[FATO]** Art. 16: eliminação ao fim do tratamento, com conservação
  autorizada, entre outros, para "cumprimento de obrigação legal ou
  regulatória" (I).
- **[FATO]** Art. 18: confirmação, acesso, correção, anonimização ou
  eliminação de dados desnecessários, portabilidade, eliminação dos
  tratados com consentimento, informação sobre compartilhamento, sobre a
  negativa de consentimento, e revogação do consentimento.
- **[FATO]** Art. 33: transferência internacional só nos casos listados
  (país adequado, cláusulas contratuais, consentimento específico, entre
  outros).
- **[FATO]** Art. 37 (registro das operações), art. 41 (o controlador
  indica encarregado e divulga identidade e contato "preferencialmente no
  sítio eletrônico"), art. 46 (medidas de segurança), art. 48
  (comunicação de incidente à autoridade e ao titular).
- **[FATO]** Resolução CD/ANPD nº 2/2022, agentes de tratamento de
  pequeno porte
  (https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos/regulamentacoes_anpd/resolucao-cd-anpd-no-2-de-27-de-janeiro-de-2022):
  art. 11 dispensa a indicação de encarregado, mas exige "um canal de
  comunicação com o titular"; indicar encarregado conta como boa prática
  (§2º); art. 9º permite registro simplificado das operações; art. 3º I
  exclui do regime quem faz tratamento de alto risco.
- **[FATO]** Marco Civil, art. 7º X: exclusão definitiva dos dados
  fornecidos a uma aplicação, a pedido, ao fim da relação, "ressalvadas as
  hipóteses de guarda obrigatória de registros"; art. 15 em §7.4.

### 12.2 Enquadramento do produto — [INFERÊNCIA], a validar com advogado

| Tratamento | Quem é o controlador | Base legal provável | Observação |
|---|---|---|---|
| Conteúdo dos terminais, avisos, audit, aparelhos, no PC e no celular do usuário | o próprio usuário (ou o empregador dele, em uso profissional); a Garioli Labs **não acessa** | — | software local: a Garioli Labs não trata esses dados; em uso pessoal, art. 4º I |
| Metadados na ponte privada `ponte.gariolilabs.com` (IP, horários, volume, ID de roteamento), só de Sr. Garioli e de quem ele autorizar | Garioli Labs | execução do serviço pedido pelo usuário (art. 7º V); anti-abuso por legítimo interesse (art. 7º IX) | provedor de hospedagem = operador |
| Metadados numa ponte própria de outro usuário | quem opera essa ponte | — | a Garioli Labs não recebe nada |
| Registros de acesso, se DP1 concluir que são obrigatórios | Garioli Labs | obrigação legal (art. 7º II; Marco Civil art. 15) | retenção de 6 meses; eliminação só depois (art. 16 I) |
| Push pelo FCM (ID de instalação, payload opaco) | Garioli Labs (dona do projeto Firebase) | execução do serviço (art. 7º V) | Google = operador para o FCM; transferência internacional (art. 33) |
| Contato de suporte ou privacidade (e-mail) | Garioli Labs | pedido do titular | fora do produto |

- **[INFERÊNCIA]** Com a Garioli Labs como microempresa ou startup e sem
  tratamento de alto risco, cabe o regime de pequeno porte (Res. 2/2022):
  pode não indicar encarregado, mas precisa de canal de comunicação.
  Depende da forma jurídica e da receita (DP2).
- **[INFERÊNCIA]** O inventário de §3 serve de base para o registro
  simplificado das operações (art. 37; Res. 2/2022 art. 9º).
- **[INFERÊNCIA]** Direitos do art. 18 na prática: a Garioli Labs quase
  não guarda nada (ponte em memória); a resposta padrão a pedidos de
  acesso ou eliminação é "não guardamos", mais PS-1 para o Google. Com
  DP1 obrigando registros, a eliminação espera o prazo legal.

## 13. Ganchos da spec atendidos

### 13.1 Tabela §16 (PV1–PV11)

| # | Regra da spec | Como este documento atende |
|---|---|---|
| PV1 | Nunca bytes VT crus para o celular | §3.1 (saída bruta nunca sai do PC), §4 |
| PV2 | Celular não grava frames, histórico, eventos, contextos, pedidos; só pareamento e chave | §3.2, RQ-2, RQ-5; conflito de prazo em PA1 |
| PV3 | Push só `{agent_id, attention_id}` | §8.1, AV-8, RQ-11 |
| PV4 | `audit.list` nunca devolve texto digitado | §3.1 (audit), §4; DP3 |
| PV5 | Celular não recebe `device_id` nem chave de outros | §3.1 (aparelhos), §4 |
| PV6 | Só os campos que as telas mostram | §4; §6.2; confirma D-14 (§13.2) |
| PV7 | Texto oculto vira espaço; título, links, área de transferência não saem | §4; AV-1, AV-2 para avisos |
| PV8 | Pasta do usuário como `~` em `cwd` | §6.2; AV-1 |
| PV9 | Redação de `subject`, `detail`, contexto; `redacted: true` | §5 (RD-1 a RD-7) |
| PV10 | `msg` de depuração e reasons sem conteúdo | PR-7, RQ-1, TL-2 |
| PV11 | Retenções no PC | §3.1 e RQ-6: log 24 h / 10 000; resultados em memória (256); audit 90 dias; tela depois do fim 60 min; revogados 90 dias; registro para `lost` até a sessão sair do snapshot |

Notas da spec §16:

- `FLAG_SECURE` e biometria ao abrir são do app: RQ-4; biometria ao abrir
  fica desligada por padrão (Q10).
- `audit_input` e o texto `devices.audit_note`: DP3.

### 13.2 Outros ganchos de P6

| Gancho | Resposta |
|---|---|
| §17 "campos do Context" e §19.2 item 22 | Mantém D-14 em v1: sem pasta, título, resumos, `last_result` e `files_touched` (entidades da auditoria §7.1). Voltam só com ADR e opt-in (RD-6). |
| §19.2 item 21 e R9.26 | Tela depois do fim: 60 min, só memória. Registro para `lost`: §3.1. Revogados: 90 dias. |
| §19.2 item 26 | Até 20 sessões encerradas no snapshot, cada uma só enquanto a tela final está retida (60 min). |
| §19.2 item 31 | DP3. |
| R6.3 | Registro de revogado: 90 dias. |
| §6.9 "onde fica o audit" | No disco do agente, na pasta de dados do usuário (RQ-12). |
| R7.3 | Confirmado: o ULID revela a hora de criação, que as telas já mostram; no push, ver §8.1. |
| R8.5 / D-18 | Registro mínimo `{id, name, created_at}` aceito; o nome da sessão fica só no PC. |
| D-10 | Aceito: projeção por destinatário com `log.hidden`. |
| EX1, "esquema da mensagem" e "comportamento offline" (parte de P6) | §6.3 (AV-1 a AV-9). |

## 14. Decisões pendentes (Sr. Garioli)

**DP1 — Registros de acesso na ponte da Garioli Labs (Marco Civil art.
15).**

- (a) Zero registro, como hoje (ADR-0004). Exige parecer de que o art. 15
  não se aplica (por exemplo, serviço sem fins econômicos). Risco: se a
  Pipa passar a ser paga, a obrigação pode surgir.
- (b) Guardar 6 meses só `{data e hora, IP, evento de conexão, ID de
  roteamento}`, cifrado, com acesso restrito e expurgo automático.
  Exige um ADR que emende o "sem disco" do ADR-0004.
- (c) Pedir parecer jurídico antes de M6 e, enquanto isso, P4 desenha a
  ponte com um registro de acesso **opcional e desligado por padrão**,
  que `ponte.gariolilabs.com` liga só se o parecer exigir; pontes
  próprias ficam
  sem registro.
- **Recomendação: (c).** Não muda nenhum ADR agora, não bloqueia M0–M5 e
  evita retrabalho em M6. **DECIDIDA 2026-09-26 por Sr. Garioli: opção (c).**
- **Nota de 2026-09-26:** com a ponte privada (ADR-0004), a ponte da
  Garioli Labs atende só usuários autorizados. **[INFERÊNCIA]** a
  questão provavelmente diminui; a opção (c), com parecer antes de M6,
  continua valendo.

**DP2 — Quem é o controlador e qual é o canal de privacidade.**

- (a) Garioli Labs como pessoa jurídica controladora, com Sr. Garioli
  indicado como encarregado e um e-mail de privacidade público.
- (b) Garioli Labs como agente de pequeno porte, sem encarregado, só com
  canal de comunicação (Res. 2/2022 art. 11).
- (c) Sr. Garioli como pessoa natural controladora.
- **Recomendação: (a).** Indicar encarregado conta como boa prática (Res.
  2/2022 art. 11 §2º) e custa um endereço de e-mail. Falta saber a forma
  jurídica e o CNPJ da Garioli Labs para preencher o Anexo A. **DECIDIDA 2026-09-26 por Sr. Garioli: opção (a). Forma jurídica e CNPJ PENDENTES.**

**DP3 — `pipa.audit.input` (texto digitado no audit).** Conflito: ADR-0012
diz "input digitado nunca persistido em lugar nenhum"; `devices.audit_note`
diz "O texto digitado não é registrado"; `interfaces/vscode.md` §10 e a
spec R6.25 permitem gravá-lo no PC com a opção ligada (spec §19.2 item
31).

- (a) Tirar a opção do MVP. ADR-0012 e o texto aprovado passam a valer sem
  exceção; muda `interfaces/vscode.md` §10, `vsc.set_audit_input` e a
  spec (R6.25, `policy.audit_input`).
- (b) Manter, desligada por padrão, com as entradas de texto cifradas pelo
  DPAPI, retenção de 7 dias e texto condicional em `devices.audit_note`
  (reaprovação da tela) e ADR-0012 emendado.
- (c) Manter como está: a nota fica falsa para quem ligar a opção.
- **Recomendação: (a).** Senhas digitadas pelo celular (por exemplo num
  `sudo`) iriam para um banco em disco sem cifra; o ganho de auditoria não
  compensa, e (a) mantém a promessa do ADR-0012. **DECIDIDA 2026-09-26 por Sr. Garioli: opção (a).**

**DP4 — Ponte fora do Brasil e transferência internacional.** Junto com a
decisão de hospedagem de M6 (ADR-0006).

- (a) Preferir região no Brasil quando o custo permitir.
- (b) Aceitar EUA (e2-micro) e registrar a hipótese do art. 33 com o
  provedor (cláusulas contratuais), declarando na política pública.
- **Recomendação:** decidir em M6 com o custo na mão; em qualquer caso, a
  política pública declara o país. O FCM já é transferência internacional
  inevitável (Google), a declarar do mesmo jeito. **Continua pendente: decidir em M6.**

**DP5 — Guardar contexto e pedidos em disco (auditoria §7.2).** A
auditoria propõe SQLite com sessão e contexto por 7 dias depois do fim e
pedidos por 7 dias. A spec adotou só o registro mínimo para `lost`
(D-18).

- (a) Só memória para contexto, pedidos e avisos EX1 (esta proposta,
  §3.1); o audit já guarda as decisões como metadados.
- (b) Seguir a auditoria: 7 dias em disco.
- **Recomendação: (a).** Nome de terminal e comando são conteúdo sensível e devem ficar só em memória. **DECIDIDA 2026-09-26 por Sr. Garioli: opção (a).**
  (Q2); nenhuma tela aprovada mostra contexto de sessões encerradas há
  mais de 60 min.

**DP6 — Como apagar os dados da Pipa no PC.** Hoje nenhuma tela aprovada
faz isso.

- (a) Novo comando "Pipa: Apagar dados deste PC", com modal que nomeia o
  efeito (todos os celulares precisam parear de novo); exige texto e
  aprovação em P7.
- (b) O desinstalador do agente pergunta se apaga; a documentação diz a
  pasta.
- (c) Apagar sozinho ao desinstalar a extensão. **[INFERÊNCIA]**
  arriscado: reinstalar a extensão perderia todos os pareamentos sem
  aviso.
- **Recomendação: (b) no MVP e (a) na próxima revisão de interface.** **DECIDIDA 2026-09-26 por Sr. Garioli: opção (b) no MVP.**

## 15. Pontos em aberto

| # | Ponto | Documentos | Dono |
|---|---|---|---|
| PA1 | Quando a tela some do celular: `interfaces/android.md` §0 diz "mais de 5 min fora do primeiro plano"; spec PV2 diz "ao sair do app ou perder a rede". A tela aprovada prevalece; sugiro que P3 ajuste o texto de PV2. | android.md §0; spec PV2; fluxo X7 | P3, P7 |
| PA2 | `audit_input` contra ADR-0012 e `devices.audit_note`. | ADR-0012; spec §19.2 item 31 | Resolvido por DP3 |
| PA3 | Retenção de contexto e pedidos: auditoria §7.2 contra spec D-18. | auditoria §7.2; spec R8.5 | Resolvido por DP5 |
| PA4 | "Ponte sem disco" contra a possível guarda obrigatória de registros de acesso. | ADR-0004; Marco Civil art. 15 | DP1, P4 |
| PA5 | Remover o PC com o PC offline: `device.forget` exige conexão (R10.36); o fluxo F6 não diz o que acontece se não houver. Sugestão: o celular apaga localmente mesmo assim e avisa para revogar no PC. | fluxo F6; spec R10.36 | P7, P3 |
| PA6 | A notificação usa `VISIBILITY_PUBLIC` e mostra o nome do PC na tela de bloqueio; o nome padrão é o hostname, que costuma ter o nome da pessoa ("LUCAS-PC"). Sugestão para P7 avaliar: versão pública genérica (`notif.attn_unknown`). | android.md §11; spec E1 | P7 |
| PA7 | Assunto **redigido** não força `destructive`; só o cortado força (R11.1). A pessoa pode aprovar um comando que não vê inteiro sem biometria extra. | spec R11.1; §5 | P5 |
| PA8 | Quem envia o push: a ponte enviar dá ao operador o token e a hora dos pedidos de cada PC (§8.2). | ADR-0014; spec §19.2 item 15 | P4, P5, M8 |
| PA9 | Consulta de presença (E2): a ponte fica sabendo qual celular pergunta por qual PC. P4 deve evitar identificar o celular na consulta. | exigências E2; spec §17 | P4 |
| PA10 | Atualização e distribuição do agente: nenhuma chamada de rede descrita; se houver, entra em §9 antes do código. | — | P9 |
| PA11 | Chave de inscrição da ponte privada (emitida por Sr. Garioli a quem ele autoriza): se for uma por pessoa, vira um identificador guardado pelo operador e entra em §3.3 quando P4 fechar o formato. | ADR README ponto 3 | P4 |
| PA12 | Formulário da Play: tratamento de IP e metadados de conexão enviados à ponte (Anexo B, item 6) precisa ser conferido na submissão. | Anexo B | M8 / publicação |
| PA13 | Avisos EX1 na notificação: o texto aprovado é opaco (`notif.attn`); mostrar o título do aviso (buscado pelo túnel, nunca pelo push) muda tela e visibilidade na tela de bloqueio. Também falta onde o aviso aparece no app e como silenciar uma origem. | EX1; android.md §11 | P7 |
| PA14 | Avisos EX1: autenticação de quem chama e se o agente guarda uma lista de origens autorizadas (dado novo no PC). | EX1 | P5, P3 |

## 16. Referências

Externas, conferidas em 2026-09-26:

- Lei nº 13.709/2018 (LGPD), texto compilado:
  https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm
- Lei nº 12.965/2014 (Marco Civil da Internet):
  https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2014/lei/l12965.htm
- Resolução CD/ANPD nº 2/2022 (pequeno porte):
  https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos/regulamentacoes_anpd/resolucao-cd-anpd-no-2-de-27-de-janeiro-de-2022
- Google Play, "Provide information for Google Play's Data safety
  section": https://support.google.com/googleplay/android-developer/answer/10787469
- Google Play, Android vitals:
  https://support.google.com/googleplay/android-developer/answer/9844486
- Firebase, "Privacy and Security in Firebase":
  https://firebase.google.com/support/privacy
- Firebase, dados para o formulário da Play:
  https://firebase.google.com/docs/android/play-data-disclosure
- FCM, tipos de mensagem:
  https://firebase.google.com/docs/cloud-messaging/customize-messages/set-message-type
- FCM, entrega de mensagens:
  https://firebase.google.com/docs/cloud-messaging/understand-delivery
- Android, Auto Backup:
  https://developer.android.com/identity/data/autobackup
- Android, copiar e colar (conteúdo sensível):
  https://developer.android.com/develop/ui/views/touch-and-input/copy-paste
- Claude Code, hooks: https://code.claude.com/docs/en/hooks

Internas:

- `docs/adr/0001` a `0014`, em especial 0004, 0005, 0006, 0007, 0008,
  0012, 0013, 0014
- `docs/spec/trcp-1.md` §6, §8, §9.9, §10.6.6, §10.6.11, §11.7, §14, §16,
  §17, §19
- `docs/interfaces/android.md` §0, §2, §7, §10–§13; `fluxos.md` F6, F7;
  `textos.md`; `vscode.md` §7, §8, §10; `README.md` decisão 8, Q2, Q3, Q10
- `docs/exigencias-externas.md` EX1
- `docs/auditoria-arquitetura-2026-09-26.md` §6, §7, §9, §12
- `docs/proposta-conexao-por-codigo-2026-09-26.md` §4, §4.1, §7
- `docs/visao.md`

---

## Anexo A — RASCUNHO: Política de privacidade pública

> **RASCUNHO para revisão jurídica. Não publicar.** Campos entre chaves
> dependem de DP1, DP2 e DP4.

**Política de privacidade da Pipa**

Última atualização: {data}.

A Pipa é um app Android e uma extensão do VS Code que deixam você ver e
controlar pelo celular os terminais do seu computador. Esta política diz
quais dados passam por nós e quais nunca passam.

**Quem somos.** {Garioli Labs, razão social, CNPJ, endereço}. Contato de
privacidade: {e-mail}. Encarregado: {nome}.

**O que fica só nos seus aparelhos.** O conteúdo dos seus terminais
(telas, histórico, comandos, o que você digita) fica no seu computador. O
celular mostra esse conteúdo só quando você abre um terminal e não grava
nada disso. O registro de atividade (quem conectou, quando, quantos
caracteres foram enviados) fica no seu computador por 90 dias. Avisos de
outros programas do seu computador que você ativar (por exemplo, alertas
de consumo) seguem o mesmo caminho cifrado e também não são gravados no
celular. Nós não temos acesso a nada disso.

**O que a ponte vê.** Para o celular achar o computador de qualquer rede,
a conexão passa por uma ponte. Não oferecemos ponte pública: você usa a
sua própria ponte (o mesmo programa, instalado num servidor seu, num VPS
ou num Raspberry) e informa o endereço dela na extensão. A nossa ponte
(`ponte.gariolilabs.com`) é privada e só atende pessoas que autorizamos.
Em qualquer ponte, tudo o que passa é cifrado de ponta a ponta entre o
seu celular e o seu computador: a ponte não consegue ler. Ela vê apenas
os endereços IP, os horários, a quantidade de dados, um identificador do
computador e, durante o pareamento, os 4 primeiros dígitos do código.
Na sua própria ponte, só você vê esses dados. Na nossa, se você foi
autorizado, guardamos esses dados só em memória, enquanto a conexão
existe {ou: "e, por obrigação legal, guardamos IP, data e hora de acesso
por 6 meses, sob sigilo"}.

**Notificações.** Para avisar que algo pede sua atenção, usamos o Firebase
Cloud Messaging, do Google. O aviso leva só dois identificadores
aleatórios; o texto que você vê é montado no próprio celular. O Google
recebe o identificador de instalação do app para entregar o aviso.

**O que não fazemos.** Não temos conta nem login. Não usamos analytics,
publicidade nem relatórios de erro automáticos. Não vendemos nem
compartilhamos dados.

**Onde os dados são tratados.** A nossa ponte privada fica em {país}; a
sua ponte fica onde você a instalar. O Google pode tratar os dados do
aviso fora do Brasil.

**Seus direitos.** Pela LGPD, você pode pedir confirmação, acesso,
correção e eliminação dos dados que tratamos, entre outros direitos, pelo
{e-mail}. Na prática, quase nada fica conosco. Para apagar tudo:
remova o computador no app (Aparelhos e segurança), revogue o celular no
VS Code e desinstale o app e a extensão.

**Mudanças.** Avisaremos no app e nesta página antes de qualquer mudança
que colete dados novos.

## Anexo B — RASCUNHO: respostas da "Segurança dos dados" (Google Play)

> **RASCUNHO. Conferir o formulário no momento da submissão.** Base:
> definições oficiais da Play (§16). **[FATO]** "Collect" é transmitir
> dados para fora do aparelho; dados cifrados de ponta a ponta,
> ilegíveis para o desenvolvedor, e dados processados de forma efêmera
> não precisam ser declarados; transferir a um prestador de serviço que
> trata em nome do desenvolvedor não conta como "sharing"; mesmo um app
> que não coleta nada precisa informar o link da política de privacidade.

| # | Pergunta | Resposta proposta | Por quê |
|---|---|---|---|
| 1 | O app coleta ou compartilha algum tipo de dado exigido? | **Sim**, a partir de M8 (push). Antes do push: **Não**. | **[INFERÊNCIA]** O SDK do FCM envia o ID de instalação para fora do aparelho. |
| 2 | Tipos coletados | **IDs do dispositivo ou outros** (ID de instalação do Firebase). | A definição da Play cita o "Firebase installation ID" como exemplo. |
| 3 | Finalidade | **Funcionalidade do app** (entregar avisos). | ADR-0014. |
| 4 | Coleta obrigatória ou opcional? | **[INFERÊNCIA]** Opcional se o app só registrar o token depois que a pessoa permitir notificações; obrigatória se registrar sempre. Definir em M8. | — |
| 5 | Conteúdo dos terminais, comandos, nomes, avisos | **Não declarado.** | Cifrado ponta a ponta, ilegível para a Garioli Labs. |
| 6 | IP e metadados de conexão na ponte | **Não declarado**, se a ponte só os processa em memória (BR-1). **Declarar** se DP1 levar à guarda de registros. | **[INFERÊNCIA]** Processamento efêmero; conferir na submissão (PA12). Na ponte própria do usuário, a Garioli Labs não recebe nada. |
| 7 | Compartilhamento com terceiros | **Não.** | O Google atua como prestador de serviço do FCM. |
| 8 | Dados cifrados em trânsito? | **Sim.** | Túnel TLS; FCM por HTTPS. |
| 9 | O usuário pode pedir a exclusão? | **Sim**: remover o PC no app (dispara PS-1), desinstalar, ou pedir pelo e-mail de privacidade. | §11. |
| 10 | Revisão de segurança independente | **Não** (no MVP). | — |
| 11 | Link da política de privacidade | Página pública com o Anexo A revisado. | Exigido mesmo sem coleta. |
