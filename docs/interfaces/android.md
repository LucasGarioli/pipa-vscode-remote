# Interfaces do app Android (P7)

Status: rascunho de planejamento, 2026-09-26.

- **Stack:** Kotlin + Jetpack Compose + Material 3, com o tema Pipa
  (`identidade-visual.md`).
- **Textos:** `textos.md`. Toda tela cita as chaves, e nenhum texto fica
  fixo no código.
- **Campos:** entre crases, os nomes do TRCP/1 (auditoria §5 e §7.1). Os
  itens `E#`/`P#` apontam para `exigencias-para-o-protocolo.md`.
- **Protótipo:** coluna "Celular Android" de `prototipo/index.html`. O
  seletor "Ir para" e os links `#<estado>` abrem cada tela.

## 0. Regras que valem para todas as telas

**Privacidade visível**

- **Nada da tela é gravado no celular.** Linhas do terminal, contexto e
  pedidos ficam só em memória, no `ViewModel`, e são descartados quando o app
  sai do primeiro plano por mais de 5 min ou quando o processo morre.
- O celular **guarda só** a lista de PCs pareados:
  - `{agent_id, agent_name, bridge, fingerprint}`, em DataStore cifrado;
  - a chave do aparelho, no Keystore.

  Pergunta Q2: guardar também a lista de terminais para abrir mais rápido?
  Padrão proposto: não.
- `FLAG_SECURE` ligado por padrão (pergunta Q3): sem print, sem gravação de
  tela e sem prévia em "Recentes". Desligável em "Aparelhos e segurança".
- **Notificações opacas:** "Algo pede sua atenção em LUCAS-PC". Nunca levam
  comando, nome de sessão nem saída (E24).

**Conexão**

- A conexão WebSocket existe **só em primeiro plano** (a auditoria recusa o
  foreground service).
- Com o app em segundo plano, só o push chega. Ao voltar, o app faz
  `resume{epoch, after_seq}` e mostra "Reconectando…" até o snapshot chegar.

**Permissões Android**

| Permissão | Quando é pedida |
|---|---|
| `INTERNET` | instalação |
| `CAMERA` | na hora de ler o QR (pedido em contexto; se negada, a aba "Digitar código" continua) |
| `POST_NOTIFICATIONS` (13+) | logo depois do primeiro pareamento, com explicação (`settings.notifications_help`) |
| `USE_BIOMETRIC` | instalação; é o `BiometricPrompt` que pede o toque |

**Biometria**

- `BiometricPrompt` com `CryptoObject` e
  `BIOMETRIC_STRONG | DEVICE_CREDENTIAL`, assinando o step-up (E6). A chave
  de escrita tem `setUserAuthenticationRequired(true)`.
- Sem biometria nem bloqueio de tela, o app **lê**, mas não escreve
  (`arm.no_biometric`).

**Acessibilidade (todas as telas)**

- **Alvo mínimo de 48 × 48 dp** (`minimumInteractiveComponentSize`). Os ícones
  da barra superior são `IconButton` de 48 dp.
- **Tudo em `sp`**, testado com fonte a 200 %. As barras usam
  `heightIn(min=…)`.
- **Contraste medido:** 0 reprovações nos dois temas
  (`identidade-visual.md` §8).
- **Estado com texto além de cor e ícone.** Os chips mono têm rótulo
  ("rodando", "falhou · exit 1").
- **TalkBack:**
  - cada item de lista é **um** nó (`Modifier.semantics(mergeDescendants = true)`),
    com rótulo por extenso (`sessions.item_a11y`);
  - as teclas especiais têm `contentDescription` próprio (`keys.*_a11y`);
  - mudanças de estado usam `liveRegion = Polite`, e erros de envio usam
    `Assertive`.
- **Contagens regressivas:**
  - são anunciadas só no início, aos 30 s e no fim; nunca a cada segundo;
  - a escrita tem prazo, mas é **estensível** sem perder o texto
    (WCAG 2.2.1).
- **Voltar do sistema** fecha folha ou diálogo antes de sair da tela.
  Não há gesto escondido.

**Estados padrão**

- **Carregando:**
  - `CircularProgressIndicator` com texto, depois de 300 ms;
  - abaixo de 1 s não mostra nada (limites de Nielsen: 0,1 / 1 / 10 s).
- **Erro:** o cartão diz o que aconteceu e o próximo passo.
- **Vazio:** explica como sair do vazio.
- **Offline:** faixa no topo, com o conteúdo antigo apagado (não gravado).

## 1. Boas-vindas

**Propósito:** explicar em 10 segundos o que é e o próximo passo.

**Dados:** nenhum.

**Ações:**

- Adicionar computador (primário);
- Como a Pipa protege seus terminais (texto).

**Textos:**

- `welcome.title`, `welcome.body`;
- `welcome.steps_title`, `welcome.step1..3`;
- `welcome.cta`, `welcome.security_link`.

**Tela "Como a Pipa protege":** `welcome.security_1..4`, com ícone por item:

- começa só leitura;
- nada gravado;
- o PC decide quem entra;
- biometria para escrever.

**Acessibilidade:** o logo é decorativo (`contentDescription = null`), e o
título é `heading()`.

## 2. Adicionar computador

**Propósito:** parear com um código de 12 dígitos, lido do QR ou digitado.

**Abas:** "Ler QR" e "Digitar código".

- A aba inicial é Ler QR, mas **a câmera só é pedida ao abrir essa aba**.
- Se a câmera for negada, a aba mostra `add.qr_camera_denied` e um atalho
  para "Digitar código". O pareamento nunca depende da câmera.

**Campo do código:**

- Máscara `0000 · 0000 0000`, teclado numérico,
  `autofill = OneTimeCode`, colar aceito (ignora espaços e pontos).
- Contador vivo: "Faltam {n} dígitos" / "Código completo".
- **Botão "Conectar" desabilitado** até ter 12 dígitos
  (`aria-disabled`/`enabled=false` com o motivo em
  `semantics { stateDescription }`). É defesa nível 1: um código incompleto
  não pode ser enviado.

**Nome deste celular:**

- Campo com padrão = modelo (`Build.MODEL`), editável;
- aparece no PC ("Permitir “Pixel 8”?"), `add.name_help` (P2).

**Ponte:**

- mostra o endereço (`add.bridge_label`) e o link Alterar (vai para
  Configurações);
- se o QR trouxer uma ponte desconhecida, o app pergunta antes (P5).

**Textos:** `add.*`.

**Erros:** ver §4.

## 3. Pareamento em andamento

| Estado | Tela | Texto | Ação |
|---|---|---|---|
| Conectando à ponte | spinner central | `pair.connecting` + ponte | Voltar cancela |
| **Confira no PC** | código de confirmação em 40 sp mono (`482 913`) + "Esperando você clicar em Permitir no PC…" | `pair.verify_title`, `pair.verify_body`, `pair.verify_wait`, `pair.verify_mismatch_hint` | Cancelar |
| Concluído | ícone ok + "LUCAS-PC adicionado" | `pair.success_*` | Ver terminais |

- **Por que mostrar o código dos dois lados:** o PC só diz "Permitir" depois
  de comparar. Quem digitou o código errado **não** consegue um pareamento
  silencioso com o PC de outra pessoa. É defesa por verificação humana,
  barata e rara.
- **TalkBack:** o código é lido dígito a dígito (`pair.verify_code_a11y`,
  "Código 4 8 2 9 1 3").

## 4. Erros de pareamento

Cartão de erro acima do formulário. O campo **mantém** o que foi digitado,
exceto quando o código morreu.

| Código (P3) | Título / corpo | Próximo passo |
|---|---|---|
| `expired` | `pair.err_expired_*` | gerar novo código no VS Code; o campo é limpo |
| `wrong_code` | `pair.err_wrong_*` | o código foi invalidado por segurança; gerar outro |
| `rejected` | `pair.err_rejected_*` | alguém recusou no PC; conferir se é o PC certo |
| `confirm_timeout` | `pair.err_timeout_*` | o PC não respondeu em 60 s |
| ponte fora | `pair.err_bridge_*` | conferir a internet ou a ponte |

## 5. Computadores

**Propósito:** escolher o PC e ver de relance quem pede atenção.

**Dados por item:**

- `agent_name` (E1, mono);
- online / offline desde (E2);
- número de terminais e de pedidos abertos (E3).

**Ações:**

- tocar abre os terminais;
- atalhos na barra: Aparelhos e segurança, Configurações;
- "Adicionar computador".

**Estados:**

- sem PCs: volta à Boas-vindas;
- PC offline (`pcs.offline_since`, `pcs.offline_hint`);
- acesso cortado (`pcs.cut`);
- faixas globais no topo (§12).

**Textos:** `pcs.*`.

**TalkBack:** "LUCAS-PC, online, 4 terminais, 1 pedido de atenção".

## 6. Terminais de um computador

**Propósito:** saber o estado de cada terminal sem abrir nenhum.

**Dados por item:**

| Elemento | Campo |
|---|---|
| Nome | `Session.name` |
| Chip de estado | `Session.status` + `open_attentions`: `status.waiting_permission` (âmbar), `status.running`, `status.prompt`, `status.exited_ok`, `status.exited_err` com `exit_code`, `status.lost` |
| Contexto (mono, 1 linha) | `Context.tool{kind, last_tool}` → "Claude Code · Bash · npm run build"; ou `running_command` → "executando: npm run dev"; ou `last_command{text, exit_code}` → "último: npm test · exit 0"; ou `ended_at` |
| Chip "escrita · 4:12" | `Grant.armed_until` / `remaining_ms` (E5) |

**Organização:**

- a faixa âmbar "1 pedido esperando sua resposta" + Responder fica no topo;
- depois vêm as seções "Abertos" e "Encerrados".
- A nota fixa "Todo terminal começa só leitura" deixa a regra visível sem
  precisar aprender.

**Ações:**

- tocar abre o terminal (permissão `read`);
- não há criar terminal no MVP. `session.create` existe no protocolo, mas
  os terminais nascem no VS Code (visão, "O que faz").

**Estados:**

- vazio (`sessions.empty_*`);
- PC offline (faixa + texto `global.pc_offline_empty`);
- acesso cortado (tela própria, `global.cut_*`);
- reconectando (faixa).

## 7. Terminal

**Propósito:** ver a tela ao vivo e, quando liberado, digitar.

**Dados:**

- `screen{cols, rows, lines[].spans{text, fg, bg, attr}}` via `screen.sub`;
- histórico via `screen.history{before_line, count=200}`.

**Layout, de cima para baixo:**

1. **Barra superior:**
   - nome da sessão;
   - `LUCAS-PC · 120×32 (VS Code)`;
   - menu ⋮ → "Encerrar terminal…" (§9).
2. **Faixa de modo**, sempre visível:
   - **Só leitura** (`surface2`, cadeado): "Você vê a tela. Para digitar,
     libere a escrita." + botão **Liberar escrita**.
   - **Escrita liberada** (magenta, cadeado aberto): "Escrita liberada ·
     4:59" + "O PC mostra que este celular está no controle." + botão
     **Bloquear**.
3. **Tela do terminal:**
   - `JetBrains Mono` 13 sp, cores ANSI remapeadas;
   - quebra de linha (não rola na horizontal);
   - selecionável para copiar, sem gravar;
   - "Carregar 200 linhas anteriores" no topo;
   - "Início do histórico guardado no PC" quando `reached_start` (E13).
4. **Pedido fixado** (se houver): "Claude pede permissão · npm run build" +
   **Ver pedido**.
5. **Campo de envio + Enviar:**
   - desabilitado em só leitura, com o motivo embaixo
     (`session.send_disabled_reason`);
   - "Enviar manda o texto e um Enter".
6. **Teclas especiais**, grade 6 × 2:
   - `Esc Tab ← ↑ ↓ →` / `Enter` … `Ctrl+C`;
   - Ctrl+C fica longe do Enter, com borda vermelha;
   - sem escrita liberada, as teclas ficam desabilitadas e dizem por quê.

**Ações e permissões:**

| Ação | Comando | Permissão |
|---|---|---|
| Ver | `screen.sub`/`unsub` | read |
| Histórico | `screen.history` | read |
| Enviar texto | `input.send{data, expect.screen_ver}` | write + escrita liberada |
| Tecla especial | `input.send{keys:[…], expect}` | idem |
| Liberar escrita | `grant.arm` + step-up (E5, E6) | write |
| Encerrar | `session.terminate` + step-up | terminate |

**Estados de envio** (`statusline`, TalkBack `Assertive` nos erros). O texto
digitado **nunca** se perde:

| Resultado | Texto |
|---|---|
| enviando | `session.sending` |
| ok | `session.sent` (o campo limpa) |
| `stale` | `session.err_stale`: nada foi enviado; o texto fica |
| conexão caiu | `session.err_uncertain` → `cmd.status` → `uncertain_ok` / `uncertain_no` |
| `not_armed` | `session.err_not_armed`: o texto fica |
| `too_large` | `session.err_too_large` |

**Estados da tela:**

- encerrado (`session.exited_banner`, sem campo de envio);
- perdido (`session.lost_banner`);
- reconectando (faixa; a tela congela esmaecida, com a hora da última
  atualização).

**TalkBack:**

- a tela é um nó `log`, "Tela do terminal Claude Code, 14 linhas visíveis";
- o leitor não recebe cada frame: quem usa TalkBack navega pelas linhas;
- não há `liveRegion` na tela (ruído).

## 8. Liberar escrita

**Propósito:** dar escrita **a um terminal**, por pouco tempo, com prova de
presença.

**Folha inferior:**

- título `arm.title` ("Liberar escrita em Claude Code") e `arm.body`;
- seletor **1 / 5 / 15 min** (`radiogroup`; padrão 5; limitado por
  `policy.arm_max_min`, E4, pergunta Q7);
- botão **Liberar com biometria**, que abre o `BiometricPrompt` com
  `arm.bio_title`/`arm.bio_subtitle` ("Claude Code em LUCAS-PC · 5 min").

**Depois:**

- snackbar `arm.done`;
- a faixa fica magenta com a contagem;
- o chip "escrita · 4:59" aparece na lista;
- no PC, a aba é renomeada e surge a notificação.

**Fim da escrita:**

- aos 30 s do fim, snackbar `arm.expiring` + **Estender** (volta à folha);
- ao expirar, `arm.expired`, e o texto não enviado fica no campo;
- retirada pelo PC: `arm.disarmed_by_pc`.

**Estados:**

- sem biometria nem bloqueio (`arm.no_biometric` + atalho para as
  configurações do Android);
- escrita desativada no PC (`arm.policy_off`).

**Por que por terminal e com prazo:** o dano de um toque errado fica limitado
a um terminal e a poucos minutos. O PC vê o tempo todo quem está no controle.

## 9. Encerrar terminal

- Diálogo que **nomeia o terminal**: `terminate.title` ("Encerrar Backend?")
  e `terminate.body`.
- O corpo explica o sinal de interrupção e o kill em 5 s, e diz que não pode
  ser desfeito.
- O botão vermelho **Encerrar com biometria** faz o step-up e
  `session.terminate{signal:"int"}`. Depois de 5 s, o agente manda `kill`.

## 10. Pedido de atenção (aprovação)

**Propósito:** responder a um pedido do Claude Code sem ler o terminal
inteiro.

**Dados:**

- `Attention{kind, title, subject (E10), detail, options[].role (E7), destructive, requires_step_up (E9), source, created_at}`;
- a sessão, o PC e a pasta (`cwd`).

**Layout:**

1. Título: `attn.title_permission`, "Claude pede permissão" (os outros
   `kind` têm títulos próprios).
2. Fonte:
   - ✓ "Informado pelo Claude Code" (`source=adapter`);
   - ou o aviso âmbar "Detectado pela tela. Confira o terminal antes de
     responder." (`heuristic`). Um pedido adivinhado pela tela nunca parece
     tão confiável quanto um estruturado.
3. "Para executar o comando:" + **caixa mono** com o comando (selecionável).
4. `Claude Code · LUCAS-PC · ~/projetos/api · há 12 s`.
5. Nota:
   - destrutivo: nota vermelha `attn.destructive_note`;
   - sem escrita liberada: nota neutra `attn.need_bio_note`.

   A nota avisa **antes** que haverá biometria.
6. Ações, fixas no rodapé:
   - **Recusar** (secundário) e **Permitir** (primário), do mesmo tamanho,
     lado a lado;
   - "Abrir terminal" como texto.
   - Destrutivo: Permitir fica vermelho, "Permitir com biometria".

**Regras:**

- **Destrutivo exige biometria sempre**, mesmo com escrita liberada.
- **Recusar não pede biometria** (pergunta Q1): recusar é o lado seguro.
- **Uma resposta só:** `attention.respond` nunca é reenviado sozinho.
  Enquanto envia, os botões somem e aparece "Enviando resposta…".

**Estados finais** (os botões somem e aparece um cartão):

| Estado | Texto |
|---|---|
| Permitido | `attn.done_allowed` |
| Recusado | `attn.done_denied` |
| Respondido no PC / outro aparelho (`already_resolved`, E8) | `attn.stale_pc` / `attn.stale_other` |
| Claude parou de esperar | `attn.expired` |
| Terminal terminou | `attn.session_ended` |

- **Por que travar o pedido velho:** responder a um pedido que já mudou é o
  erro mais caro deste produto. O agente recusa (`already_resolved`) e a tela
  nem oferece o botão (defesa nível 1 + 3).
- **Vários pedidos:** `attn.counter` "1 de 3" + "Próximo pedido".
- **TalkBack:** o comando é lido como texto; Permitir diz "Permitir: npm run
  build em Claude Code".

## 11. Notificações

Canal `pipa_attention`:

- nome `notif.channel_attn`, descrição `notif.channel_attn_desc`;
- importância alta;
- visibilidade `VISIBILITY_PUBLIC`, porque o texto já é opaco.

| Caso | Título | Texto |
|---|---|---|
| 1 pedido | Pipa | `notif.attn`: "Algo pede sua atenção em LUCAS-PC" |
| N pedidos no mesmo PC | Pipa | `notif.attn_many`: "{n} pedidos de atenção em NOTE-TRABALHO" |
| PC desconhecido para o app | Pipa | `notif.attn_unknown` |

- **Ícone pequeno:** glifo de 16 px da Pipa (losango).
- **Toque:** abre o app → biometria, se "Pedir biometria ao abrir" estiver
  ligado → `resume` → tela do pedido.
- **Sem ações na notificação** (nada de Permitir na tela de bloqueio): a
  decisão pede ver o comando.
- **Agrupamento** por PC (`setGroup(agent_id)`).
- Quando o pedido é resolvido em outro lugar, a notificação é **cancelada**:
  o app recebe `attention.resolved` na próxima conexão, ou um push
  data-only de limpeza.

## 12. Aparelhos e segurança

**Blocos:**

- **Este celular:**
  - nome;
  - "Pareado com LUCAS-PC em 26/09/2026";
  - onde a chave está: StrongBox ou TEE (`devices.key_*`, vem do
    `KeyInfo`).
- **Switches:**
  - Bloquear capturas de tela (`FLAG_SECURE`, ligado);
  - Pedir biometria ao abrir a Pipa (desligado, pergunta Q10).
- **Aparelhos com acesso a LUCAS-PC** (E16, só leitura): "este celular",
  "conectado agora", "visto há 3 dias". Nota `devices.revoke_on_pc`: revogar
  outro aparelho é no PC (pergunta Q6).
- **Atividade recente deste celular** (E17): hora + ação, só metadados, e a
  nota `devices.audit_note`.
- **Remover LUCAS-PC deste celular:**
  - botão com contorno vermelho;
  - diálogo que **nomeia o PC**: `devices.remove_confirm_title` e
    `devices.remove_confirm_cta` "Remover LUCAS-PC";
  - executa `device.forget` (E18) e volta à Boas-vindas, ou à lista, se
    houver outros PCs.

## 13. Configurações

| Item | Conteúdo |
|---|---|
| Ponte | endereço + "alcançável · 182 ms" / "sem resposta" (RTT, E23) + Alterar + `settings.bridge_help` |
| Idioma | Igual ao sistema / Português (Brasil) / English (`AppCompatDelegate.setApplicationLocales`, idioma por app do Android 13+) |
| Tema | Igual ao sistema / Claro / Escuro |
| Notificações | abre as configurações do canal no Android + `settings.notifications_help` |
| Aparelhos e segurança | atalho |
| Sobre | "Versão 0.1.0 · protocolo trcp.v1" |

## 14. Estados globais

| Estado | Detecção | Aparência | Texto | Ação |
|---|---|---|---|---|
| Sem internet | `ConnectivityManager` | faixa neutra no topo | `global.no_network` | nenhuma; volta sozinho |
| Ponte inalcançável | falha de conexão ao host | faixa vermelha clara | `global.bridge_down` | Tentar de novo |
| Reconectando | WS caiu | faixa neutra + spinner | `global.reconnecting` (tentativa n; backoff de 1 a 30 s) | Tentar de novo |
| PC offline / dormindo | ponte diz offline (E2) | faixa + lista vazia | `global.pc_offline`, `global.pc_offline_empty` | Tentar de novo |
| Acesso cortado no PC | close 4410 (E20) | tela com ícone "bloqueado" | `global.cut_*` | nenhuma: só o PC reativa |
| Aparelho revogado | close 4403 (E19) | tela cheia | `global.revoked_*` | Adicionar de novo / Tirar da lista |
| Versões incompatíveis | close 4426 (E21) | faixa vermelha | `global.outdated` | Abrir a loja |

## 15. O que **não** está nas telas do MVP, e por quê

- **Criar terminal pelo celular:** os terminais nascem no VS Code; manter um
  lugar só reduz a confusão sobre "de onde veio".
- **Teclado de terminal completo** (Ctrl+qualquer, F1–F12): cobre 95 % com
  Esc, Tab, setas, Enter e Ctrl+C; o resto fica para depois do uso real.
- **Redimensionar o terminal:** o tamanho é o do VS Code (auditoria, `resize`
  só em M1 sem view desktop).
- **Resposta rápida na notificação:** exige ver o comando.
- **Widget e Wear OS.**
