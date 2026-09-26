# Auditoria técnica e arquitetural — controle remoto de terminais (TRCP)

Data: 2026-09-26 · Escopo: proposta inicial (extensão VS Code + agente Rust +
app Android) · Estado do repositório: só `README.md`, nenhum código.

**Legenda obrigatória.** Cada afirmação relevante é marcada:

- **[FATO]** — verificado hoje em fonte primária (URL citada ou listada no
  Anexo A).
- **[INFERÊNCIA]** — conclusão minha a partir de fatos; precisa de spike
  quando marcada "validar".
- **[RECOMENDAÇÃO]** — decisão que eu tomaria.

---

## 1. Veredito executivo

**Nota: 5/10. Aprovaria com mudanças — mas as mudanças são estruturais, não
cosméticas.**

A ideia central (Context Snapshot + Event Stream + Resume, contexto mínimo
no celular, rede privada) é boa e diferenciada. O problema está no
**mecanismo de captura**: a proposta assume que a extensão consegue observar
e controlar os terminais comuns do VS Code. Pela API estável, ela não
consegue fazer isso de forma confiável:

1. **[FATO]** Não existe API estável para ler a saída bruta de um terminal.
   `window.onDidWriteTerminalData` segue *proposed*, e o próprio arquivo
   declara: "we don't intend on promoting it to stable due to problems
   around performance" (`vscode.proposed.terminalDataWriteEvent.d.ts`).
   APIs *proposed* não podem ser usadas em extensões publicadas.
2. **[FATO]** A única leitura estável é `TerminalShellExecution.read()`
   (1.93+). Ela funciona **por comando**, exige shell integration, só entrega
   dados escritos **depois** da primeira chamada e não dá acesso ao
   buffer/scrollback. O `cmd.exe` não tem shell integration.
3. **[FATO]** Ao fechar a janela do VS Code, os processos de terminal são
   descartados. Só o *reload* reconecta.

Consequência: com a arquitetura atual, o celular perderia a saída sempre que
a extensão recarregasse. Não enxergaria nada que já estivesse rodando antes
da inscrição (por exemplo, um Claude Code iniciado antes). Não funcionaria em
CMD. E perderia todas as sessões ao fechar o VS Code.

**A mudança principal: o agente passa a ser o dono dos PTYs** (um *session
host*, no estilo tmux/mosh). O terminal no VS Code vira uma *view* desse PTY,
via `Pseudoterminal`. Isso resolve captura, persistência, fechamento do VS
Code, múltiplas janelas e o futuro JetBrains/CLI — e ainda melhora a
segurança, porque só é remotamente acessível o que o usuário abriu como
remoto.

Outras quatro mudanças de peso:

- Sincronizar o **estado da tela** (modelo mosh), e não reenviar o fluxo de
  bytes.
- Detectar "esperando input" via **adaptadores de ferramenta**, começando
  pelos hooks do Claude Code, com heurística apenas como fallback.
- Ter **autenticação de aplicação independente do Tailscale**.
- **Reordenar o roadmap**: segurança antes de qualquer exposição à rede.

---

## 2. O que está correto (eu manteria)

| Decisão | Por quê |
|---|---|
| Processo agente separado da extensão | O extension host morre com a janela; o agente precisa sobreviver a ela. **[FATO]** `deactivate()` recebe no máximo 5 s (`extHostExtensionService.ts`). |
| Rust + Tokio para o agente | Binário único, sem runtime, bom para ConPTY/PTY multiplataforma e para processo de longa duração. |
| Protocolo próprio, independente do VS Code | É o que permite JetBrains/CLI/servidor depois. Manter. |
| Snapshot + event stream + sequência + resume | Conceito correto. A implementação precisa de ajustes (seção 5). |
| Contexto com limites explícitos | Correto e essencial para privacidade e para a bateria. |
| Rede privada, sem porta pública | Correto. Mas a rede **não é** a autenticação (seção 6). |
| Pairing + identidade por dispositivo | Correto. O formato do código precisa mudar (seção 6). |
| Arquivos e processos fora do MVP | Correto. |
| LLM opcional, com processamento local possível | Correto. Deve ser opt-in e com redação prévia. |
| SQLite | Adequado para o volume. Mas **não** para guardar saída bruta (seção 8). |
| CLI de teste antes do mobile | Correto. Vai virar o cliente de conformidade do protocolo. |

---

## 3. Problemas críticos

### CRÍTICO

**C1 — O mecanismo de captura não se sustenta na API estável.** *Eu mudaria
isso.*
**[FATO]** O cenário atual da API:

- `onDidWriteTerminalData`: *proposed*, sem plano de estabilizar.
- `onDidExecuteTerminalCommand` (com `output`): *proposed*.
- `Terminal.selection` e `Terminal.dimensions`: *proposed*.
- Não há API de buffer/scrollback.
- `read()` só funciona por execução e a partir da inscrição.

**[INFERÊNCIA]** Um app TUI de longa duração como o Claude Code aparece como
**uma** execução: se a extensão não estava inscrita quando `claude` começou
(por exemplo, depois de um reload), aquela saída está perdida até o comando
acabar.
**Solução:** o agente passa a ser o dono do PTY (seção 4).

**C2 — Fechar o VS Code mata as sessões.**
**[FATO]** "Terminal processes are disposed of when a VS Code window is
closed" (release 1.61). A opção `persistentSessionReviveProcess`
**relança** um processo novo; não preserva o antigo.
Com a proposta atual, "controlar do celular depois de fechar o notebook" é
impossível. Com o agente como dono dos PTYs, a sessão sobrevive ao VS Code.

**C3 — Detectar "Claude esperando interação" por heurística de saída não é
confiável.**
**[FATO]** O Claude Code expõe hooks:

- `Notification` com `notification_type` (`permission_prompt`,
  `idle_prompt`, `elicitation_dialog`, `agent_needs_input`…).
- `PermissionRequest`, que **pode devolver `allow`/`deny`**.
- `Stop`, com `last_assistant_message`.
- **HTTP hooks** (`"type":"http"`), que fazem POST do JSON para um endpoint
  e aceitam headers com interpolação de variáveis de ambiente
  (`allowedEnvVars`).

Fonte: https://code.claude.com/docs/en/hooks.

**[INFERÊNCIA]** A TUI redesenha a tela com diffs de escape. Raspar esses
bytes é frágil, e digitar "1" num menu no momento errado aprova a coisa
errada.
**Solução:** adaptador Claude Code via HTTP hook para o agente; a aprovação
pelo celular vira decisão estruturada, não um toque de tecla.

**C4 — Autenticação apoiada na rede.**
"Está no tailnet" não é identidade do celular. **[FATO]** Com o Tailscale
Serve, os headers de identidade só são confiáveis se o serviço escutar
apenas em localhost, e o Funnel não os envia (kb/1312). Um nó comprometido
ou uma conta Tailscale tomada dão acesso de rede ao agente.
**Solução:** autenticação mútua na camada de aplicação, com chave de
dispositivo não exportável (seção 6).

**C5 — Ordem do roadmap expõe execução remota antes da autenticação.**
Na proposta, o item 7 (input remoto) e o 8 (streaming) vêm antes do 12–14
(pairing, auth, autorização). Um agente que aceita `terminal.input` numa
porta de rede sem autenticação é RCE, mesmo "só para testar".
**Solução:** até existir auth, o agente só escuta IPC local (seção 8 do
roadmap).

### ALTO

**A1 — Sessão criada pelo celular = executável arbitrário.** Se
`session.create` aceitar `shell`/`args`/`cwd` do cliente, o celular vira um
lançador de processos. **Solução:** o celular só escolhe um `profile_id`
definido no PC.

**A2 — Input remoto não é idempotente, e a proposta não trata retry.**
Reenviar `terminal.input` após timeout pode executar `y` ou `rm` duas vezes.
**Solução:** entrega at-most-once com `command_id` e deduplicação; nenhum
retry automático de input; precondição de estado (`expect`) — seção 5.

**A3 — Corrida entre o prompt e o input.** O celular vê "Aprovar? (y/n)" e
envia `y`. Entre ver e enviar, a tela mudou, e o `y` cai em outro lugar.
**Solução:** o input carrega `expect.screen_ver` ou `attention_id`, e o
agente rejeita se estiver obsoleto (concorrência otimista).

**A4 — Replay de bytes não serve para TUI.** Reenviar os eventos 1848–1849 de
`terminal.output` só reconstrói a tela se o cliente tiver um emulador VT
completo **e** todo o histórico desde um estado conhecido. Para TUIs com
tela alternativa/redesenho, isso degenera em "baixar tudo de novo" — o
oposto do objetivo.
**Solução:** o agente mantém um emulador VT por sessão e sincroniza **o
estado da tela** (seção 5).

**A5 — Sequência por sessão sem época.** Se o agente reiniciar, o `seq`
volta a 1, e o cliente com `lastEvent: 1847` recebe silêncio ou dados
errados. **Solução:** `(epoch, seq)`; época nova força snapshot.

**A6 — stdout vs stderr é impossível.**
**[FATO]** Num PTY, stdout e stderr do processo apontam para o mesmo
dispositivo de terminal, e a separação não existe mais do lado de quem lê. Remover isso dos
requisitos. Só um adaptador que executa o comando diretamente (fora do PTY)
separaria os fluxos.

**A7 — Campos de contexto que a heurística não consegue produzir.**
`objective`, `currentTask` e `summary` não saem de exit code e cwd. Ou vêm
de um adaptador (por exemplo, o `UserPromptSubmit` do Claude Code) ou de um
LLM. Marcar a origem (`source: adapter|heuristic|llm`) e a confiança em cada
campo; não fingir.

**A8 — Android não mantém WebSocket em background.**
**[FATO]** O Doze "suspends network access". A doc recomenda FCM em vez de
conexão persistente. O foreground service `dataSync` tem teto de 6 h/24 h no
Android 15 (target 35+). **Solução:** WebSocket só com o app em primeiro
plano; o push acorda o app, que então busca os dados pelo túnel.

### MÉDIO

**M1 — Conflito de tamanho de tela.**
**[FATO]** Não há API para redimensionar um terminal comum; num
`Pseudoterminal`, `onDidOverrideDimensions` só consegue reduzir.
Dois viewers (VS Code e celular) com tamanhos diferentes criam o problema
clássico do tmux. **Solução:** o tamanho do PTY pertence à view desktop
quando anexada; o celular renderiza com reflow/scroll horizontal e só
assume o tamanho quando não há view desktop, ou por ação explícita.

**M2 — Digitação concorrente PC + celular.** Os bytes se intercalam.
**Solução:** o agente serializa o input por sessão, e o VS Code mostra
"controlado remotamente por <dispositivo>".

**M3 — Perdas do modelo "agente dono do PTY"** (trade-off a registrar):

- As contribuições de ambiente de outras extensões
  (`environmentVariableCollection`, por exemplo a ativação de venv do
  Python) não se aplicam a shells criados pelo agente.
- A shell integration nativa do VS Code (decorações, navegação de comandos)
  só funciona se o fluxo contiver OSC 633. **[INFERÊNCIA — validar em
  spike]** Como o xterm do VS Code interpreta as sequências vindas de
  qualquer PTY, incluindo `Pseudoterminal`, o agente pode injetar os
  próprios scripts de integração emitindo OSC 633 e recuperar parte disso.

**M4 — Sleep do PC.** Não há solução de rede para isso: o PC dormindo está
fora do ar. O celular precisa mostrar "offline desde…" com o último
snapshot, sem pretender estado ao vivo. "Manter acordado enquanto houver
sessão remota armada" pode ser uma opção explícita — **[proposta]**, fora
do MVP.

**M5 — Identidade persistente de sessão no VS Code.**
**[FATO]** Os objetos `Terminal` são recriados quando o extension host
reinicia; a documentação não garante nenhum ID estável.
**[INFERÊNCIA]** O PID sobrevive ao reload (processo reconectado), mas não
ao revive. **Solução:** o ID da sessão é do agente (ULID), e a view do VS
Code guarda esse ID.

### BAIXO

**B1 — O nome "TRCP"** colide com siglas existentes; irrelevante tecnicamente.
Registrar o identificador de subprotocolo WebSocket cedo (`trcp.v1`) e não
mudar mais.

**B2 — `timestamp` em segundos.** Usar milissegundos, e nunca como ordem
(a ordem é `seq`).

**B3 — `apps/agent` + `packages/protocol` misturam convenções npm e Cargo.**
Ajuste na seção 11.

---

## 4. Arquitetura recomendada

### 4.1 Alternativas comparadas

| | A. Proposta original | **B. Agente dono do PTY (recomendada)** | C. Só Claude Code (hooks/SDK/Remote Control oficial) |
|---|---|---|---|
| Captura de saída | Parcial (por comando, depois da inscrição) | Total (o agente lê o PTY) | Só eventos do Claude |
| CMD | Sem shell integration | Funciona (PTY genérico) | n/a |
| Sobrevive ao fechar o VS Code | Não | **Sim** | Sim |
| Terminais normais do VS Code | Visíveis (parcialmente) | Não, só os abertos pelo perfil remoto | Não |
| Superfície de ataque | Todo terminal do VS Code | **Só sessões opt-in** | Só Claude |
| JetBrains/CLI depois | Reescreve a captura | Só uma nova view | n/a |
| Custo | Menor no início, alto depois | Médio (ConPTY + emulador VT) | Baixo |

**[FATO]** O Claude Code já tem um "Remote Control" oficial que conecta o app
Claude Android a uma sessão local. O tráfego passa pela API da Anthropic e o
transcript fica nos servidores dela (https://code.claude.com/docs/en/remote-control).
**[INFERÊNCIA]** O diferencial deste produto precisa ser: terminais
genéricos, vários ao mesmo tempo, dados que não saem da rede do usuário e
contexto mínimo. Se o uso for só Claude Code e não houver problema em o
transcript ir para a Anthropic, a alternativa C já resolve. Isso é pergunta
aberta (seção 12).

### 4.2 Desenho

```text
┌──────────────────────────── PC (usuário comum, nunca admin) ─────────────────────┐
│                                                                                  │
│  VS Code (N janelas)                    trcd — agente Rust (1 por usuário)       │
│  ┌──────────────────────────┐           ┌──────────────────────────────────────┐ │
│  │ Extensão (view fina)     │  named    │ Session Host                          │ │
│  │ • perfil "Terminal       │  pipe /   │  • PTY (ConPTY | openpty)             │ │
│  │   remoto" (profile       │  unix     │  • emulador VT por sessão (tela +     │ │
│  │   provider)              │  socket   │    scrollback limitado)               │ │
│  │ • Pseudoterminal ⇄       │◄─────────►│  • shell integration própria (OSC 633)│ │
│  │   sessão do agente       │  (ACL do  │ Context Engine                        │ │
│  │ • indicador "remoto",    │  usuário) │  • heurística (prompt/exit/cwd/título)│ │
│  │   aprovar pairing,       │           │  • adaptadores: Claude Code (HTTP hook)│ │
│  │   revogar, kill switch   │           │ Event Log (epoch, seq) + Screen Sync  │ │
│  └──────────────────────────┘           │ AuthN/AuthZ + Audit                   │ │
│                                         │ SQLite (metadados, eventos, audit)    │ │
│  Claude Code (dentro de uma sessão) ───►│ ◄─ HTTP hook 127.0.0.1 + token/sessão │ │
│  trc (CLI) ────── mesmo IPC ───────────►│                                       │ │
│                                         │ Listener de rede: TLS 1.3 (rustls,    │ │
│                                         │ cert auto-assinado fixado no pairing) │ │
│                                         │ bind SÓ no IP do Tailscale (100.x)    │ │
│                                         └───────────────┬──────────────────────┘ │
└─────────────────────────────────────────────────────────┼────────────────────────┘
                                                          │ WSS subprotocolo trcp.v1
                                          WireGuard (Tailscale) — camada de transporte
                                                          │
                                   ┌──────────────────────▼───────────────────────┐
                                   │ Android                                       │
                                   │ • chave do dispositivo no Keystore (TEE/      │
                                   │   StrongBox), biometria por operação crítica  │
                                   │ • WS só em primeiro plano                     │
                                   │ • renderiza linhas com estilo (sem emulador)  │
                                   │ • push (fase posterior): só ID opaco          │
                                   └───────────────────────────────────────────────┘
```

### 4.3 Respostas diretas às perguntas de arquitetura

- **O Rust Agent deve existir separado?** Sim. Mais do que isso: ele vira o
  componente principal. A extensão vira uma view fina.
- **Processo, serviço ou child process?** Um **processo de usuário**
  iniciado no logon (Agendador de Tarefas / chave Run no Windows; systemd
  `--user` ou LaunchAgent no Linux/macOS), em instância única (lock via
  named pipe). A extensão o inicia se não estiver rodando, **destacado**, e
  ele não morre com o VS Code.
  *Eu não usaria Windows Service*:
  - O serviço roda na sessão 0, como SYSTEM ou uma conta de serviço.
  - Criar shells na sessão interativa do usuário exige manipular tokens.
  - Um bug viraria escalada de privilégio.
- **Sleep:** o agente não impede o sleep. No resume do sistema, reata o bind
  no IP do Tailscale (ele pode sumir e voltar) e incrementa um contador de
  "gap". O celular mostra que ficou offline.
- **Múltiplas janelas:** cada janela conecta ao mesmo agente. A sessão tem
  `workspace` como etiqueta e abre na janela que a criou. Outra janela pode
  "anexar", e aí há dois viewers, com as regras M1/M2.
- **Remote-SSH/WSL:** fora do MVP. **[INFERÊNCIA]** No modelo B, o agente
  roda onde o shell roda. Para WSL/SSH, um segundo agente no destino é o
  caminho natural (é o "múltiplos computadores"), não a extensão.
- **Crash do agente:** os PTYs são filhos dele e morrem junto. É o preço do
  modelo B. Mitigações:
  - Agente pequeno e sem pânico (`unwrap` proibido).
  - As sessões são marcadas `lost`, com o motivo persistido.
  - O desenho permite, depois, separar um *ptyhost* mínimo do front de rede
    (como o VS Code faz). Não fazer isso no MVP.

---

## 5. Protocolo recomendado — TRCP/1 revisado

### 5.1 Decisões de base

| Tema | Decisão | Motivo |
|---|---|---|
| Transporte | WebSocket sobre TLS 1.3, subprotocolo `trcp.v1` | WS basta: bidirecional, com ping/pong nativo, e OkHttp e tokio-tungstenite são maduros. QUIC/WebTransport não trazem ganho que justifique a complexidade agora. |
| Codificação | **JSON (UTF-8) em frames de texto** no MVP; `caps` prevê `"enc":"cbor"` para depois | Debugável com o CLI e fixtures legíveis. O volume é baixo porque a tela é sincronizada por diff (5.4), não por bytes brutos. MessagePack/CBOR só se medições mostrarem ganho. |
| Saída de terminal | **Nunca bytes VT brutos para o celular** | Elimina o problema de UTF-8 cortado, a injeção de escape no cliente e o replay caro. |
| IDs | ULID/UUIDv7 (ordenáveis) para sessão, comando e atenção | Ordenáveis e sem coordenação. |
| Tempo | `ts` em ms Unix, **só informativo** | A ordem é dada por `seq`. |

### 5.2 Envelope

```json
{ "v": 1, "t": "event", "k": "session.state", "id": "01J…", "ts": 1788380000123,
  "epoch": "01J…", "seq": 18847, "s": "01J…sessao", "p": { } }
```

- `t`:
  - `hello | auth | cmd | result | event | screen | ack | error`.
- `k`: tipo específico.
- `s`: sessão, quando houver.
- `p`: payload.
- `epoch`/`seq`: só em `event`.
- `id`: sempre; em `cmd` é gerado pelo cliente e serve de chave de
  idempotência.
- **Regras de evolução:** campos desconhecidos são ignorados; `event` de
  tipo desconhecido é ignorado; `cmd` desconhecido recebe
  `error{code:"unsupported"}`. Mudança incompatível = `trcp.v2`, negociada
  no subprotocolo.

### 5.3 Handshake e autenticação

1. O TLS 1.3 fecha com o certificado do agente **fixado** (fingerprint
   recebido no pairing).
2. O cliente envia `hello{protocols:[1], client, device_id, caps}`. O
   servidor responde `hello{agent_id, agent_version, epoch, caps, nonce}`.
3. O cliente envia `auth{sig}`, com `sig = ECDSA-P256(chave do dispositivo,
   "trcp-auth-v1" ‖ nonce ‖ tls_exporter ‖ device_id)`. O `tls_exporter`
   segue a RFC 9266 e amarra a prova ao canal: sem MITM e sem replay em
   outra conexão.
4. O servidor responde `auth.ok{grants}`, ou fecha com código 4401.

Nada de bearer token de longa duração em nenhum lugar.

### 5.4 Dois canais de sincronização (a mudança central)

**(a) Event Log — estado de baixa frequência, confiável e ordenado.**

- **Conteúdo:** `session.created`, `session.state`, `session.context`,
  `attention.opened`, `attention.resolved`, `session.exited`,
  `session.removed`, `device.revoked`.
- **Um único log por agente** (não um por sessão), identificado por
  `(epoch, seq)`, com `seq` monotônico e sem lacunas. É mais simples de
  retomar, e a lista de sessões fica consistente. A taxa é baixa (dezenas
  por minuto), então não vira gargalo.
- **Resume:** o cliente envia `cmd resume{epoch, after_seq}`.
  - Mesma época e `after_seq` ainda retido: o agente envia os eventos
    seguintes em ordem e depois continua ao vivo.
  - Época diferente, ou `after_seq` abaixo da retenção: o agente envia
    `event snapshot{sessions[], contexts[], open_attentions[], seq_at}` e
    depois os eventos com `seq > seq_at`.
  - O snapshot é gerado atomicamente com `seq_at` (sob o mesmo lock do log).
- **Duplicados:** o cliente descarta `seq <= último aplicado`.
- **Fora de ordem:** impossível dentro de uma conexão WS (TCP), e entre
  conexões resolvido por `seq`.
- **Lacuna detectada** (`seq > último + 1`): o cliente pede resume.

**(b) Screen Sync — conteúdo do terminal, com a última versão valendo
(modelo mosh/SSP).**

- **[FATO]** O mosh sincroniza estado de tela em vez de fluxo de bytes
  (paper USENIX ATC'12, "State Synchronization Protocol").
- **Fluxo:**
  - O agente mantém o emulador VT da sessão.
  - O cliente assina com `cmd screen.sub{s}`.
  - O agente envia `screen{s, ver, base, cols, rows, cursor, lines:[{i,
    spans:[{text, fg, bg, attr}]}]}`. `base` é a versão que o cliente
    confirmou: com `base` preenchido, o frame é um diff; com `base` nulo, é
    completo.
  - O cliente responde `ack{s, ver}`.
  - O agente só gera diff em relação ao último `ver` confirmado.
- **Coalescência:** no máximo ~20 frames/s por sessão com assinatura ativa.
  Sessões sem assinatura não geram frames.
- **Backpressure natural:** se o cliente fica lento, versões intermediárias
  simplesmente não são enviadas. Um `cat` de 200 MB no PC custa ao celular
  poucos frames.
- **Histórico:** `cmd screen.history{s, before_line, count ≤ 200}`, sob
  demanda e paginado. Não há download do histórico inteiro, que era o
  objetivo original.

### 5.5 Comandos (cliente → agente) e garantias

| `k` | Payload | Permissão | Notas |
|---|---|---|---|
| `resume` | `epoch, after_seq` | read | — |
| `screen.sub` / `screen.unsub` | `s` | read | — |
| `screen.history` | `s, before_line, count` | read | Paginado |
| `input.send` | `s, data` (texto) ou `keys:["ctrl+c","up"]`, `expect:{screen_ver?}` | write | **At-most-once** |
| `attention.respond` | `attention_id, choice` | write (+step-up se `destructive`) | Caminho preferido para aprovar |
| `session.create` | `profile_id, name?` | create | Nunca shell/args/cwd livres |
| `session.terminate` | `s, signal: "int" \| "kill"` | terminate | Step-up |
| `cmd.status` | `id` | — | Consulta o resultado de um comando incerto |
| `resize` | `s, cols, rows` | write | Só quando não há view desktop (M1) |

- **Idempotência:** o agente guarda `(device_id, cmd.id) → result` por 10
  min. Um duplicado devolve o resultado guardado **sem reaplicar**.
- **Retry:** o cliente **nunca** reenvia `input.send` ou
  `attention.respond` automaticamente. Em caso de dúvida (conexão caiu antes
  do `result`), consulta `cmd.status` após reconectar.
- **Precondição:** se `expect.screen_ver` for mais antigo que a tela atual
  e as linhas visíveis tiverem mudado, a resposta é
  `result{ok:false, code:"stale"}`. Uma `attention` já resolvida responde
  `code:"already_resolved"`.
- **Ack:** todo `cmd` recebe exatamente um `result{re:id, ok, code?, data?}`.

### 5.6 Heartbeat, backpressure e limites

- **Heartbeat:**
  - O servidor manda ping WS a cada 20 s.
  - Sem pong em 45 s, a conexão é derrubada.
  - Sem ping recebido em 45 s, o cliente considera a conexão morta e
    reconecta com backoff exponencial e jitter (1 s → 30 s).
- **Backpressure:**
  - O Event Log nunca descarta eventos.
  - Se a fila de saída de uma conexão passar de N MB, o agente fecha com
    4429, e o cliente retoma via resume.
  - O Screen Sync coalesce.
- **Limites:** frame ≤ 256 KB, `input.send.data` ≤ 4 KB, e ≤ 30 comandos
  por segundo por dispositivo.
- **Códigos de fechamento:**
  - 4400: protocolo inválido
  - 4401: não autenticado
  - 4403: revogado
  - 4409: época inválida
  - 4429: lento/limite

### 5.7 Pairing

1. No PC, o usuário executa "Parear celular" (extensão ou `trc pair`). O
   agente gera `pairing_secret` (128 bits, 5 min, uso único) e mostra um
   **QR** com `{agent_id, endpoint(100.x ou nome MagicDNS), cert_fp,
   pairing_secret}`.
2. O celular gera um par de chaves no Keystore (P-256; StrongBox se houver)
   e conecta fixando `cert_fp`. Envia `pair{device_pub, device_name,
   mac=HMAC(pairing_secret, transcript ‖ tls_exporter)}`.
3. O agente valida e mostra **no PC** "Autorizar <device_name>? Código
   482-913". Esse código é derivado do transcript e aparece também no
   celular. O usuário confirma no PC.
4. O dispositivo é gravado com grants padrão (read).

Um código digitado como `7F4K-92MX` (~40 bits, sem QR) só entra como
fallback, com limite de 5 tentativas por janela e a mesma confirmação no PC.

---

## 6. Threat model

**Premissa declarada:** o produto é, por definição, **execução remota de
comandos**. O objetivo não é torná-la impossível; é garantir que só o
dispositivo certo, na sessão certa, com intenção confirmada, consiga fazê-la,
e que tudo fique registrado. **PC comprometido está fora de escopo**: quem
controla o PC já controla os terminais.

**Ativos a proteger:**

- a capacidade de escrever no PTY;
- o conteúdo das telas (código, secrets);
- a chave privada do agente e as dos dispositivos;
- o audit log.

| # | Ameaça | Impacto | Mitigação |
|---|---|---|---|
| T1 | Celular roubado desbloqueado | Crítico | A chave do dispositivo exige autenticação do usuário para operações de escrita. Step-up com `BiometricPrompt` + `CryptoObject` e `setUserAuthenticationParameters(0, BIOMETRIC_STRONG\|DEVICE_CREDENTIAL)` **[FATO, doc Keystore]**, que "arma" a escrita por sessão durante X min. `setInvalidatedByBiometricEnrollment(true)`. Revogação pelo PC com efeito imediato (4403 às conexões abertas). |
| T2 | Token roubado | Alto | Não existe token portador. A chave privada não é exportável (TEE/StrongBox) e a prova é amarrada ao canal TLS. |
| T3 | Nó do tailnet comprometido / conta Tailscale tomada | Alto | Acesso de rede ≠ acesso: TLS fixado + prova de chave de dispositivo. Opcional: Device Approval no tailnet **[FATO: disponível em todos os planos]**. |
| T4 | MITM | Alto | WireGuard + TLS 1.3 fixado no pairing + channel binding (RFC 9266). |
| T5 | Replay | Médio | Nonce por conexão + exporter. `cmd.id` é deduplicado, não reexecutado. |
| T6 | Brute force no pairing | Alto | Segredo de 128 bits via QR, com validade de 5 min e uso único. Pairing só existe enquanto o usuário o iniciou no PC, e sempre com confirmação no PC. |
| T7 | Command injection no agente | Crítico | O cliente nunca fornece executável, args, cwd ou env: só `profile_id`. Nenhum campo do protocolo chega a um shell por interpolação. |
| T8 | Terminal injection **para o PC** (input malicioso) | Crítico (inerente) | Aceito por design. Controlado por: a sessão ser opt-in (perfil remoto), grant `write` por sessão, arm com biometria, kill switch no PC e audit. Não prometer allowlist de comandos: em um PTY o input é um fluxo de teclas, e a filtragem é contornável. |
| T9 | Saída maliciosa **para o celular** (escape sequences, OSC 52 clipboard, OSC 8 links, título) | Alto | O celular recebe texto + estilos já interpretados pelo emulador do agente; nunca VT bruto. OSC 52/8 descartados. Links nunca abrem sem toque explícito. Texto de notificação sanitizado. |
| T10 | Saída maliciosa **para o agente** (um programa imitando o prompt do Claude ou os marcadores OSC 633) | Alto | Atenções vindas de adaptador autenticado (hook com token por sessão) valem mais que heurística. A UI marca a origem ("detectado por heurística — confirme na tela"). Marcadores de shell integration com nonce por sessão, como o `VSCODE_NONCE` do VS Code **[FATO]**. |
| T11 | WebSocket hijacking / CSRF / DNS rebinding | Médio | Sem cookies. Checar `Origin` e rejeitar qualquer origem de navegador. `Host` em allowlist **[FATO, OWASP / RFC 6455 §10.2: Origin não é autenticação]**. O listener do HTTP hook (loopback) exige header com token da sessão. |
| T12 | Escalada de privilégio | Alto | O agente roda como usuário comum. Se detectar token elevado (Admin), recusa grants de escrita remota e avisa. Sem Windows Service. |
| T13 | Acesso cruzado entre sessões | Alto | Autorização checada **em cada mensagem**: `(device, session, ação)` contra os grants. Nunca "autenticado = tudo". |
| T14 | Vazamento de código / secrets | Alto | Política de minimização (seção 11 da proposta, aqui na 7.3). Redação best-effort em contexto/atenção/push. Nada da tela persiste no celular. `FLAG_SECURE` opcional. |
| T15 | Comando destrutivo acidental | Alto | Aprovação estruturada (`attention.respond`) em vez de teclas. Pré-condição `expect`. `session.terminate`/kill com step-up. |
| T16 | Audit log adulterado | Médio (PC comprometido fora de escopo) | Append-only lógico; exportável. Hash encadeado é **[proposta]** para depois. |
| T17 | Hook do Claude Code usado como vetor | Médio | O endpoint aceita só loopback + token por sessão, injetado no ambiente do PTY. Uma decisão remota de permissão entra no audit. |

---

## 7. Modelo de dados

### 7.1 Entidades (agente)

```text
Agent        { agent_id, epoch (novo a cada start), cert (chave no cofre do SO), version }
Device       { device_id, name, pubkey, created_at, last_seen_at, revoked_at?, grants_default }
Grant        { device_id, session_id | "*", perms: {read, write, create, terminate}, armed_until? }
Profile      { profile_id, name, shell, args, cwd_policy, env_allow[] }   // definido só no PC
Session      { session_id (ULID), profile_id, name, workspace?, cwd, pid?, status, created_at,
               ended_at?, exit_code?, end_reason?: exited|killed|agent_restart }
SessionStatus = starting | prompt | running | waiting | exited | lost
               // waiting carrega {source: adapter|heuristic, confidence}
Attention    { attention_id, session_id, kind: permission|question|idle|error|finished,
               source, title, detail (redigido, ≤1 KB), options[], destructive: bool,
               created_at, resolved_at?, resolved_by? }
Context      { session_id, ver, cwd, title, running_command?,
               last_command?{text, exit_code?, started_at, ended_at, source},
               last_result? (≤ 1 KB, redigido),          // substitui lastOutput 32 KB
               tool?{kind:"claude-code", state, last_tool?, files_touched[≤10], prompt_hint?},
               summary?{text ≤ 4 KB, source: heuristic|adapter|llm, model?},
               updated_at }
Event        { epoch, seq, ts, session_id?, kind, payload }
AuditEntry   { id, ts, device_id?, session_id?, action, outcome, detail_meta }
               // metadados por padrão; conteúdo do input só se o usuário ativar
Screen (memória) { ver, cols, rows, grid, scrollback (≤ 5 000 linhas), cursor }
```

**Mudanças em relação à proposta:**

- `lastOutput` de 32 KB sai do contexto. A saída é consultada na tela, sob
  demanda.
- `recentEvents` vira o próprio Event Log.
- `objective`/`currentTask` só existem via adaptador ou LLM, com `source`.
- `status` ganha `prompt`/`lost` e perde a pretensão de saber "waiting" sem
  fonte.

### 7.2 Persistência (SQLite)

| Dado | Onde | Retenção |
|---|---|---|
| Devices, Grants, Profiles | SQLite | Até revogar |
| Chave privada do agente/TLS | **Cofre do SO** (DPAPI/Credential Manager; Keychain; Secret Service) via crate `keyring` — nunca no SQLite | Permanente |
| Session (metadados), Context (último) | SQLite | 7 dias após o fim |
| Event Log | SQLite | 24 h **ou** 10 000 eventos (o que vier primeiro) |
| Attention | SQLite | 7 dias |
| Audit | SQLite | 90 dias, exportável |
| Tela/scrollback | **Só memória** | Vida da sessão |
| Saída bruta do PTY | **Nunca persistida** | — |
| Input digitado | **Nunca persistido** (só metadados no audit) | — |

- **Configuração do banco:** WAL + `synchronous=NORMAL`; migrações
  versionadas embutidas no binário; `PRAGMA user_version` checado no
  start.
- **Recuperação após crash:** sessões que estavam `running` viram `lost`
  (`end_reason: agent_restart`); a época muda; clientes recebem snapshot.
- **Criptografia do banco (SQLCipher):** desnecessária no MVP se o banco
  não guarda conteúdo de tela nem secrets. O perímetro é a conta do usuário
  no SO. Reavaliar se o resumo por LLM passar a ser persistido.

### 7.3 Política de minimização de dados

| Categoria | Regra |
|---|---|
| **Fica no PC, sempre** | Saída bruta do PTY; scrollback completo; variáveis de ambiente; arquivos; transcript do Claude Code (`transcript_path` nunca é lido pelo agente no MVP); chaves privadas. |
| **Pode chegar ao celular** | Lista de sessões; status; contexto limitado (7.1); atenções redigidas; **tela visível e histórico paginado, só da sessão aberta pelo usuário e sob demanda**. |
| **Nunca persistido (em lugar nenhum)** | Saída bruta; input digitado; conteúdo de tela no celular (só memória, descartado ao sair da sessão/app). |
| **Pode ser resumido (opcional, opt-in)** | Contexto/último resultado, por LLM **local** por padrão. LLM externo só com opt-in explícito por sessão e após redação. |
| **Push (FCM/UnifiedPush)** | Só `{agent_id, attention_id}` opaco. O conteúdo é buscado pelo túnel ao abrir. **[FATO]** O payload do FCM passa pelos servidores do Google (limite de 4 KB). |

---

## 8. Roadmap reorganizado

O princípio: provar primeiro os riscos técnicos, ter segurança antes da
rede e o celular por último.

| Fase | Entrega | Critério de pronto |
|---|---|---|
| **M0 — Spikes** (descartáveis) | (a) ConPTY via `portable-pty` + emulador VT (`alacritty_terminal` ou `vt100` — escolher no spike, verificar licença) rodando pwsh, cmd e `claude`; (b) `Pseudoterminal` no VS Code exibindo esse PTY, com o teste de OSC 633 (M3); (c) HTTP hook do Claude Code → endpoint local, medindo o **timeout** máximo de um `PermissionRequest` esperando decisão humana (**UNVERIFIED hoje**). | Relatório com medições; decisão emulador VT; ADR-0001 |
| **M1 — Spec** | `docs/protocol.md` (TRCP/1), fixtures JSON de conformidade, threat model aprovado | Revisado |
| **M2 — Agente local** | Session host + Event Log + Screen Sync + SQLite, **só IPC local** (named pipe / unix socket com ACL do usuário) | Testes de integração com PTY real no Windows |
| **M3 — CLI `trc`** | `list`, `attach`, `send`, `resume`, sobre o IPC | CLI controla o Claude Code localmente |
| **M4 — Extensão VS Code** | Profile provider "Terminal remoto", Pseudoterminal ⇄ sessão, indicador remoto, comandos pair/revoke/kill switch | Sessão sobrevive a fechar e reabrir o VS Code |
| **M5 — Contexto** | Shell integration própria (pwsh, bash, zsh; cmd via heurística de prompt), adaptador Claude Code (hooks), redação | Atenção "permissão" chega estruturada |
| **M6 — Rede segura** | Listener TLS no IP do Tailscale, pairing QR, auth por chave, grants, audit, rate limit. **Primeira vez que o agente escuta na rede.** | Suíte de testes de segurança (T1–T17) + revisão |
| **M7 — Android** | App em primeiro plano: lista, contexto, tela, input com step-up, aprovação estruturada | Uso real por 1 semana |
| **M8 — Notificações** | Push opaco (FCM ou UnifiedPush) | Atenção → push → abre → responde |
| Depois | Resumo por LLM local, múltiplos PCs, relay E2E, JetBrains, WSL/SSH | — |

---

## 9. Decisões irreversíveis (acertar agora)

1. **O agente é dono do PTY** (modelo B). Todo o resto depende disso.
2. **Identificador de subprotocolo e regras de evolução** (`trcp.v1`;
   ignorar campos desconhecidos). Depois de existir um app instalado em
   celulares, mudar isso custa caro.
3. **Semântica de sincronização:** Event Log global `(epoch, seq)` + Screen
   Sync por versão/ack. Não enviar VT bruto ao cliente.
4. **Garantias de comando:** at-most-once, `cmd.id` de idempotência e sem
   retry automático de input.
5. **Modelo de identidade:** chave por dispositivo não exportável + TLS
   fixado + channel binding. A autenticação **não** depende do Tailscale
   (o que mantém a porta aberta para relay/Headscale/WireGuard puro).
6. **Sessões opt-in:** só terminais abertos pelo perfil remoto são
   acessíveis. Isso define a superfície de ataque e a promessa ao usuário.
7. **Padrões de privacidade da seção 7.3.** Relaxar depois é fácil;
   endurecer depois quebra expectativas e dados já persistidos.
8. **Fonte da verdade dos tipos do protocolo:** tipos Rust (`serde`) →
   JSON Schema gerado (`schemars`) + fixtures JSON como suíte de
   conformidade para TS e Kotlin.
9. **Repositório público e licença.** O código pode ser público; a
   segurança não pode depender de sigilo. Escolher a licença antes do
   primeiro PR externo.

## 10. Decisões que podemos adiar

- Framework mobile. Para Android-only, a recomendação é **nativo Kotlin +
  Compose**, porque os requisitos pesados são todos APIs de plataforma:
  Keystore + `BiometricPrompt`/`CryptoObject`, tipos de foreground service,
  FCM/UnifiedPush e pinning TLS com channel binding (OkHttp/Conscrypt).
  Com Screen Sync o app **não precisa de emulador de terminal** (renderiza
  linhas com spans), o que tira do Flutter/RN a vantagem de reaproveitar
  xterm.js. Flutter só ganha se o iOS entrar logo; RN ficaria preso a
  WebView para qualquer coisa de terminal. Como o protocolo é o contrato,
  a escolha é reversível.
- CBOR/MessagePack (medir antes).
- FCM vs UnifiedPush (fase M8).
- Resumo por LLM e qual modelo.
- Relay próprio E2E; Headscale; WireGuard puro.
- Múltiplos usuários, JetBrains, WSL/SSH, arquivos, Git, processos.
- Separação *ptyhost* × front de rede.
- SQLCipher.
- Hash encadeado no audit.

---

## 11. Plano de implementação

**Estrutura** (substitui `apps/agent` + `packages/protocol`):

```text
vscode-remote/
├── Cargo.toml                 # workspace
├── crates/
│   ├── trcp/                  # tipos do protocolo, serde, schemars — sem I/O
│   ├── trcd-core/             # session host, emulador VT, event log, context engine
│   ├── trcd/                  # binário: IPC, listener TLS, SQLite, auth
│   └── trc/                   # CLI
├── extensions/vscode/         # TypeScript, sem dependência nativa
├── android/                   # Gradle (M7)
├── spec/
│   ├── protocol.md
│   ├── schema/                # JSON Schema gerado a partir de crates/trcp
│   └── fixtures/              # mensagens válidas/inválidas: conformidade para Rust, TS e Kotlin
└── docs/
    ├── adr/
    ├── architecture.md
    ├── security.md            # threat model (seção 6)
    └── privacy.md             # política (seção 7.3)
```

**Sequência concreta:**

1. `docs/adr/0001-agente-dono-do-pty.md`: registra a decisão 9.1 e as
   alternativas A/B/C.
2. Spikes M0 num diretório `spikes/` (fora do workspace, descartável),
   respondendo às três perguntas abertas: emulador VT, OSC 633 no
   Pseudoterminal e timeout do hook.
3. `spec/protocol.md`: TRCP/1 da seção 5, agora com os números medidos.
4. `crates/trcp/src/lib.rs`: envelope, `Event`, `Command`, `Screen`,
   `ErrorCode`, com testes de roundtrip contra `spec/fixtures/`.
   **É o primeiro código de produção.**
5. `crates/trcd-core`: `Session` (PTY + emulador) → `EventLog` (epoch/seq,
   retenção, snapshot atômico) → `ScreenSync` (diff por versão
   confirmada). Testes com PTY real no Windows no CI.
6. `crates/trcd`: IPC local, SQLite com migrações. **Sem listener de rede.**
7. `crates/trc`: CLI.
8. `extensions/vscode`.
9. Contexto/adaptadores.
10. Rede + segurança (M6).
11. Android.
12. Push.

---

## 12. Perguntas em aberto (decisão humana)

**Decididas por Sr. Garioli em 2026-09-26:**

- **Pergunta 1** — produto para **terminais genéricos**, com dados só na
  rede do usuário. Confirma o modelo B.
- **Pergunta 2** — **só sessões opt-in** (perfil "Terminal remoto").
- **Pergunta 3** — **arm por sessão com biometria** por alguns minutos;
  aprovações destrutivas pedem biometria de novo.

Seguem abertas: 4 (push), 5 (SSH/WSL) e 6 (licença).

1. **Posicionamento frente ao Remote Control oficial do Claude Code:** o
   produto existe para terminais genéricos com dados só na rede do usuário
   — ou o foco é só o Claude Code? Isso define se vale construir o session
   host.
2. **Sessões opt-in** (só terminais abertos pelo perfil "Terminal remoto")
   **vs.** observar também os terminais comuns (read-only, por comando, via
   shell integration, com as limitações C1).
3. **Política padrão de escrita:** arm por sessão com biometria (X min),
   biometria a cada envio, ou só aprovação estruturada no MVP (sem teclado
   livre).
4. **Push:** FCM (Google vê metadados; exige credencial de conta de serviço
   no PC) vs. UnifiedPush/ntfy (sem Google; o usuário instala um
   distribuidor).
5. **Escopo de Remote-SSH/WSL** no primeiro ano.
6. **Licença** do repositório público.

---

## Conclusão

> **"Se eu fosse começar esse projeto amanhã, esta seria a arquitetura que eu
> usaria."**

Um **agente Rust por usuário, dono dos PTYs**, com emulador VT por sessão,
que:

- publica um **Event Log global `(epoch, seq)`** de estado/contexto/atenções
  e um **Screen Sync por versão** (modelo mosh);
- é acessado por uma **extensão VS Code fina** (Pseudoterminal + perfil
  "Terminal remoto"), por um **CLI** e por um **app Android nativo**;
- tem autenticação própria (TLS 1.3 fixado no pairing por QR + chave de
  dispositivo no Keystore + channel binding + grants por sessão + step-up
  biométrico);
- usa o Tailscale só como transporte;
- detecta estado das ferramentas de IA por **adaptadores estruturados**
  (hooks do Claude Code), com heurística como fallback rotulado.

**Mudanças em relação à proposta original:**

| Proposta original | Recomendado |
|---|---|
| Extensão observa terminais do VS Code | **Agente é dono do PTY**; extensão é view |
| Sessões morrem com o VS Code | Sobrevivem (processo de usuário no logon) |
| `terminal.output` incremental + replay | **Screen Sync por estado** + histórico paginado |
| Sequência por sessão | **Log global `(epoch, seq)`** + snapshot atômico |
| Retry/ack indefinidos | At-most-once, `cmd.id`, `expect`, `cmd.status` |
| "Esperando input" por heurística | **Adaptador Claude Code via hooks**; heurística rotulada |
| `lastOutput` 32 KB no contexto | `last_result` ≤ 1 KB redigido; tela sob demanda |
| stdout/stderr separados | Removido (impossível em PTY) |
| Tailscale como segurança | Tailscale como transporte; **auth de aplicação** |
| Código de pairing digitado | QR 128 bits + confirmação no PC |
| Celular cria terminal com parâmetros | Só `profile_id` definido no PC |
| Auth nos itens 12–14 | Nenhuma porta de rede antes da fase M6 |
| WS persistente no celular | WS em primeiro plano + push opaco |

---

## Anexo A — Fontes primárias verificadas em 2026-09-26

**VS Code**

- `vscode.d.ts` (branch main): https://github.com/microsoft/vscode/blob/main/src/vscode-dts/vscode.d.ts
  - `TerminalShellExecution.read()` e o evento de fim com `exitCode`.
  - `sendText`, `ExtensionTerminalOptions`/`Pseudoterminal` (estável desde
    1.39) e `shellIntegrationNonce` (1.104).
- `vscode.proposed.terminalDataWriteEvent.d.ts`: nota de "não promover a
  stable".
- Política de APIs *proposed*: https://code.visualstudio.com/api/advanced-topics/using-proposed-api
- Shell integration (shells suportados; cmd sem suporte; OSC 633/133):
  https://code.visualstudio.com/docs/terminal/shell-integration
  - O código-fonte também injeta em `powershell.exe` 5.1.
- Release notes:
  - v1_61: descarte dos processos ao fechar; revive.
  - v1_54: reconexão no reload.
  - v1_93: shell integration estável.
- `extHostExtensionService.ts`: limite de 5 s no `deactivate`.
- node-pty sem API pública para extensões: issue #84439.
- Exigência de rebuild nativo por ABI: https://code.visualstudio.com/api/advanced-topics/remote-extensions

**Claude Code**

- Hooks: https://code.claude.com/docs/en/hooks
  - `Notification` e `notification_type`, `PermissionRequest` com decisão
    e HTTP hooks.
- Remote Control: https://code.claude.com/docs/en/remote-control
- Modo headless / `stream-json`: https://code.claude.com/docs/en/headless

**Tailscale**

- Serve e headers de identidade: https://tailscale.com/kb/1312/serve
- Funnel: https://tailscale.com/kb/1223/funnel
- Device approval: https://tailscale.com/kb/1099/device-approval
- Tailnet Lock: https://tailscale.com/kb/1226/tailnet-lock
- Planos e preços: https://tailscale.com/pricing
- tsnet (só Go): https://tailscale.com/kb/1244/tsnet
- libtailscale (C, sem binding oficial para Rust): https://github.com/tailscale/libtailscale

**Android**

- Um VPN ativo por vez: https://developer.android.com/develop/connectivity/vpn
- Doze: https://developer.android.com/training/monitoring-device-state/doze-standby
- Timeout de foreground service: https://developer.android.com/develop/background-work/services/fgs/timeout
- Tipos de foreground service obrigatórios (14): https://developer.android.com/about/versions/14/changes/fgs-types-required
- Keystore: https://developer.android.com/privacy-and-security/keystore
- FCM (limite de 4 KB): https://firebase.google.com/docs/cloud-messaging/customize-messages/set-message-type
- UnifiedPush: https://unifiedpush.org/
- Termux `terminal-emulator`/`terminal-view` (Apache-2.0):
  https://github.com/termux/termux-app

**WebSocket**

- OWASP WebSocket Security Cheat Sheet
- RFC 6455 §10.2

**Mosh (SSP)**

- Winstein & Balakrishnan, "Mosh: An Interactive Remote Shell for Mobile
  Clients", USENIX ATC 2012.
  - Citado de memória, sem ter sido reaberto hoje: **[verificar]**.

**Não verificado — resolver no spike M0:**

- Timeout máximo de um hook esperando decisão humana.
- Se o Claude Code usa tela alternativa.
- Se o VS Code interpreta OSC 633 vindo de um `Pseudoterminal`.
- Licenças exatas de `alacritty_terminal`/`vt100`/`portable-pty`.

## Anexo B — Comparação de transporte

| Opção | NAT/CGNAT (comum em operadoras móveis e ISPs no Brasil) | Esforço | Lock-in | Veredito |
|---|---|---|---|---|
| **Tailscale** | Resolve (NAT traversal + DERP) | Mínimo | Baixo, se a auth for própria | **MVP** |
| WireGuard puro | Exige porta aberta/IP público no PC; falha sob CGNAT | Médio | Nenhum | Suportar depois como "modo avançado" |
| Headscale | Igual ao Tailscale; sem Serve/Funnel **[FATO]** | Médio (servidor próprio) | Nenhum | Alternativa self-hosted |
| VPN própria | — | Alto | — | Não |
| Conexão direta (porta pública) | — | Baixo | — | **Não** (superfície pública) |
| Relay próprio E2E | Resolve | Médio (VPS) | Nenhum | Futuro, para quem não usa Tailscale. O desenho de auth da seção 5.3 já permite um relay "cano burro". |

Restrição do Android **[FATO]**: só um VPN ativo por usuário/perfil. Quem usa
VPN corporativa no celular não consegue ter o Tailscale ativo ao mesmo
tempo. É uma limitação a declarar no produto; o relay futuro resolve.
