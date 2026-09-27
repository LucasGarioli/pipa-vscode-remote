# Ponte `trc-bridge` — especificação TRCB/1

Entrega **P4** do planejamento (`docs/plans/00-mapa-do-planejamento.md`).
Estado: **escrita em 2026-09-26/27, aguarda revisão.** Autor: agente Fable
5.1 (effort max), despachado de sessão Opus com autorização explícita de
Sr. Garioli (desvio registrado no mapa).

Esta spec é **normativa** para o binário `trc-bridge` e para os dois
clientes dele: o agente `trcd` no PC e o app Android. Ela cobre o que a
proposta (`docs/proposta-conexao-por-codigo-2026-09-26.md` §3, §4.1, §7),
os ADRs 0004, 0005, 0006 e 0014 e a spec TRCP/1 (`trcp-1.md` §3.1, §17)
deixaram para P4. A criptografia que corre **dentro** do fluxo repassado
(SPAKE2, TLS 1.3 mútuo, chaves, step-up) é de **P5**, `docs/security.md`.

Convenções: DEVE / NÃO DEVE / DEVERIA / PODE como em `trcp-1.md`. Regras
numeradas `B<seção>.<n>`. Fatos externos marcados **[FATO]** com fonte;
inferências marcadas **[INFERÊNCIA]**; números a validar em M6 marcados
**[P4]**; os já fixados por tela ou texto aprovado, "fixo".

## 0. Sumário executivo

- A ponte é um **repassador cego**: encontra duas conexões de saída (uma do
  PC, uma do celular) e copia bytes de uma para a outra. Ela nunca recebe
  chave, segredo de pareamento, código de confirmação nem conteúdo TRCP.
  Tudo isso corre dentro do TLS 1.3 mútuo ponta a ponta (P5).
- Nome do protocolo externo: **TRCB/1**, subprotocolo WebSocket
  `trcb.v1`. Mensagens de controle em JSON (frames de texto); fluxo
  repassado em frames binários opacos.
- **Encontro por código**: o PC pede à ponte um número de encontro de 4
  dígitos; os outros 8 dígitos do código de 12 são segredo do PC e do
  celular, e a ponte nunca os vê. Validade 5 min (fixo), uma única
  reivindicação.
- **Chave de inscrição** `pipa-enroll-v1.<id>.<segredo>`: só agentes com
  chave válida se registram e abrem encontros; celulares não precisam de
  chave. Sr. Garioli emite uma chave por pessoa na ponte privada; quem
  hospeda a própria ponte emite as suas.
- **Dois modos** no mesmo binário: **permanente** (VM, VPS, Raspberry;
  agente mantém um canal de controle aberto) e **sob demanda** (Cloud Run
  com zero instâncias ociosas; agente consulta a ponte a cada poucos
  segundos). A escolha muda só a latência de "chamar o PC" e a meta de
  abrir o app (§6.4).
- **Sem disco por padrão**: nada de registro de acesso, salvo a opção
  desligada por padrão que a decisão DP1 (c) pediu (§9).
- **Push**: a ponte privada envia o push FCM em nome dos agentes, com
  credencial só na ponte; agente nunca guarda credencial do FCM. Pontes
  próprias de terceiros ficam **sem push no MVP** (decisão pendente de
  Sr. Garioli, `security.md` §17 DS-1).

## 1. Papéis, ativos e o que cada um vê

| Papel | Quem | O que faz | O que vê |
|---|---|---|---|
| Agente | `trcd` no PC | Registra-se na ponte com a chave de inscrição; abre encontros; atende chamadas | Tudo do próprio PC |
| Celular | app Android | Reivindica um encontro (pareamento) ou chama um agente pelo `agent_id` | Só o que o TRCP projeta (P6) |
| Ponte | `trc-bridge` | Autentica agentes pela chave de inscrição; aloca números de encontro; liga pares de conexões; copia bytes | IPs, horários, `agent_id`, `key_id`, número de encontro, volume de bytes, duração |
| Operador | Sr. Garioli (ponte privada) ou quem hospeda | Emite e revoga chaves de inscrição; opera o binário | O que a ponte vê, mais o rótulo de cada chave |

- **B1.1** A ponte NÃO DEVE interpretar, guardar em disco nem alterar os
  frames binários repassados. Ela PODE contá-los e medir tempo.
- **B1.2** Nada derivado do segredo de 8 dígitos, das chaves TLS, do
  SPAKE2 ou do código de confirmação chega à ponte. Os clientes DEVEM
  tratar a ponte como adversário de rede (P5, `security.md` §3.4).
- **B1.3** Ativos que a ponte protege: (a) disponibilidade do encontro e
  do repasse para agentes inscritos; (b) confidencialidade dos metadados
  que vê (IP, horários, `agent_id`) perante terceiros; (c) a lista de
  chaves de inscrição. Ativos que a ponte **não** tem como comprometer
  sozinha: conteúdo das sessões, autenticação dos aparelhos, escrita no
  PC (P5 garante ponta a ponta).

## 2. Transporte externo

- **B2.1** Clientes conectam **de saída** à ponte por **WSS** (TLS sobre
  TCP, HTTP/1.1 Upgrade para WebSocket, RFC 6455). Nenhum cliente aceita
  conexão de entrada.
- **B2.2** O certificado externo da ponte é público (WebPKI: Let's
  Encrypt ou o certificado gerido da plataforma). Os clientes validam
  como qualquer cliente HTTPS: cadeia, nome, validade. O TLS externo
  protege só os metadados de controle; a segurança das sessões não
  depende dele (P5).
- **B2.3** Modos de terminação TLS: (a) **própria**, com `rustls` e
  certificado em disco (`--tls-cert`, `--tls-key`; renovação por ACME é
  externa, ex.: `certbot` ou Caddy); (b) **atrás de proxy**
  (`--behind-proxy`): a ponte fala WS em claro só em `127.0.0.1` ou na
  rede privada da plataforma (Cloud Run termina TLS; Caddy ou nginx no
  Raspberry). Em (b) a ponte lê o IP do cliente de `X-Forwarded-For`
  **só** quando `--trusted-proxy <cidr>` inclui o endereço do peer;
  senão, usa o IP do peer.
- **B2.4** Versões TLS externas: TLS 1.3 preferida; TLS 1.2 aceita com as
  suítes padrão do `rustls` (só AEAD com sigilo futuro; **[FATO]** o
  `rustls` não implementa RC4, 3DES, suítes sem sigilo futuro nem
  renegociação, https://docs.rs/rustls/latest/rustls/manual/_04_features/index.html).
- **B2.5** Subprotocolo: o cliente DEVE oferecer `trcb.v1` em
  `Sec-WebSocket-Protocol`; a ponte DEVE selecioná-lo. Sem ele: HTTP 400.
- **B2.6** Pedido com cabeçalho `Origin`: HTTP 403, pelo mesmo motivo de
  R3.4 (nenhum cliente é navegador).
- **B2.7** Extensões WebSocket: NÃO DEVEM ser negociadas (nem
  `permessage-deflate`, RFC 7692). Estende D-15/R3.9 à camada externa.
- **B2.8** Caminhos, todos sob `/v1/`:

| Caminho | Método | Quem | Para quê |
|---|---|---|---|
| `/v1/health` | GET | qualquer um | `200 {"ok":true,"v":1}`; sem versão detalhada, sem contagens |
| `/v1/agent` | Upgrade | agente | canal de controle (modo permanente) |
| `/v1/agent/poll` | POST | agente | consulta curta (modo sob demanda) |
| `/v1/agent/accept?call=<call_id>` | Upgrade | agente | conexão de dados para atender uma chamada |
| `/v1/pair/<code4>` | Upgrade | celular | reivindicar um encontro |
| `/v1/connect/<agent_id>` | Upgrade | celular | chamar um agente pareado |

Qualquer outro caminho: 404 sem corpo. Métodos fora da tabela: 405.

- **B2.9** Frames: nas conexões de **controle** (`/v1/agent`) só frames de
  texto com um objeto JSON `{"t":<tipo>, ...}` por frame. Nas conexões de
  **dados** (`accept`, `pair`, `connect`) a ponte envia um único frame de
  texto `{"t":"linked"}` (ou um Close) e, dali em diante, só frames
  **binários** passam, nos dois sentidos. Frame de texto depois de
  `linked`, ou binário antes: Close 4400.
- **B2.10** O conteúdo dos frames binários é o fluxo TLS ponta a ponta
  (P5). Os clientes DEVERIAM mandar um registro TLS por frame.
  **[FATO]** um registro TLS 1.3 cifrado tem no máximo 2^14 + 256 bytes
  (RFC 8446 §5.2), logo cabe no teto de frame de §7.

## 3. Registro do agente e chave de inscrição

### 3.1 Formato da chave

```
pipa-enroll-v1.<key_id>.<secret>
key_id : 8 caracteres base32 Crockford minúsculos (40 bits aleatórios)
secret : 32 bytes aleatórios em base64url sem padding (43 caracteres)
```

- **B3.1** A chave inteira tem 67 caracteres, sem espaços, copiável de
  uma linha. O prefixo `pipa-enroll-v1` permite detectar colagem no lugar
  errado (ex.: no campo de código) e futuras versões.
- **B3.2** `key_id` identifica a chave nos registros e na interface;
  `secret` nunca é mostrado depois da emissão e nunca sai do PC ou da
  ponte. A extensão mostra só `key_id` (`vscode.md` §7, AJ-25/AJ-26).
- **B3.3** No PC, a chave fica **no cofre do agente** (DPAPI de usuário,
  `security.md` §7), gravada pelo comando local `bridge.enroll{key}`
  (I11). A extensão NÃO DEVE persistir a chave: nem `settings.json`, nem
  `SecretStorage` além do trânsito até o agente. Depois de `bridge.enroll`
  a extensão descarta o texto.

### 3.2 Emissão, escopo, revogação e rotação

- **B3.4** Uma chave por **pessoa** (PA11): o operador emite com rótulo
  (`trc-bridge key new --label "Fulano" --max-agents 3`) e entrega por
  canal que ele escolher (mensagem pessoal). O rótulo é dado pessoal do
  operador (nome que ele deu); entra em `privacy.md` §3.3 como registro
  do operador da ponte privada (linha nova, a cargo de P6).
- **B3.5** Escopo da chave: `max_agents` PCs registrados ao mesmo tempo
  (padrão 3 **[P4]**), `expires_at` opcional. Um PC a mais recebe Close
  4429 `{"code":"limit","what":"agents"}`.
- **B3.6** Revogação é imediata: `trc-bridge key revoke <key_id>` (ou
  edição do arquivo de chaves + `SIGHUP`) DEVE (a) recusar novos
  registros; (b) fechar os canais de controle dos agentes dessa chave com
  Close 4403 `{"code":"enroll_revoked"}`; (c) fechar as conexões de dados
  desses agentes com Close 1001 `{"code":"peer_gone"}`; (d) apagar os
  encontros abertos por eles.
- **B3.7** Rotação: `key rotate <key_id> --grace 7d` cria `secret` novo
  para o mesmo `key_id`; o antigo vale até o fim da carência. Na
  carência, o registro com o segredo antigo devolve
  `registered{key_rotated:true}` para o agente avisar a pessoa
  (`vscode.md`: aviso novo, a cargo de P7; não bloqueia).
- **B3.8** Onde a ponte guarda as chaves: arquivo de configuração
  `keys.toml` (modo 0600, dono do processo), recarregável. Cada linha
  `key_id`, `secret`, `label`, `max_agents`, `created_at`, `expires_at?`,
  `revoked_at?`. **[INFERÊNCIA]** a verificação por HMAC exige o segredo
  em claro na ponte; uma chave vazada permite só **usar capacidade de
  repasse** (registrar agentes falsos), nunca acessar um PC ou um celular
  (P5). Por isso não se justifica esquema assimétrico no MVP. Em Cloud
  Run o arquivo vem do Secret Manager montado como volume; em VM ou
  Raspberry, `/etc/trc-bridge/keys.toml`.
- **B3.9** Quem hospeda a própria ponte usa o mesmo mecanismo:
  `trc-bridge init` gera a primeira chave e imprime uma vez ("sem ela,
  nenhum PC se registra", proposta §7).

### 3.3 Prova de posse (desafio-resposta)

A ponte nunca recebe o `secret`; recebe uma prova.

```
proof = base64url( HMAC-SHA-256( secret,
          "trcb-enroll-v1" ‖ 0x00 ‖ nonce ‖ 0x00 ‖ agent_id ‖ 0x00 ‖ ctx ) )
nonce : 32 bytes aleatórios da ponte, em base64url (decodificados na HMAC)
ctx   : "agent" no canal de controle; "poll" na consulta sob demanda
```

- **B3.10** Canal de controle (`/v1/agent`): a ponte envia
  `{"t":"challenge","nonce":…}` logo após o Upgrade; o agente responde em
  até 5 s **[P4]** com
  `{"t":"register","agent_id":…,"key_id":…,"proof":…,"mode":"permanent","presence_since":true}`;
  a ponte confere em tempo constante e responde
  `{"t":"registered","keepalive_s":25,"accept_timeout_s":10,"max_pending":4,"key_rotated":false}`
  ou fecha: 4401 `{"code":"enroll"}` (chave desconhecida, prova errada,
  vencida), 4403 `{"code":"enroll_revoked"}` (só quando `key_id` existe,
  está revogada **e** a prova bate com o segredo revogado: não revela
  nada a quem não tinha a chave), 4429 `limit`.
- **B3.11** Consulta sob demanda (`POST /v1/agent/poll`, corpo JSON
  `{agent_id, key_id, nonce, proof}`): sem `nonce` válido a ponte
  responde `401 {"nonce":…}`; com prova válida responde
  `200 {"calls":[{"call_id":…,"kind":"session"|"pair"}], "next_nonce":…, "interval_s":4, "key_rotated":false}`.
  O `nonce` é **sem estado**: `HMAC(bridge_secret, expiry ‖ agent_id)`
  com validade de 60 s, para sobreviver a reinício e a escala a zero.
  Uma consulta é uma requisição HTTP curta, sem Upgrade.
- **B3.12** `agent_id` é o ULID do agente (R7.2). A ponte NÃO DEVE
  permitir dois registros simultâneos do mesmo `agent_id`: o segundo
  substitui o primeiro (Close 4409 `{"code":"replaced"}` no antigo), pois
  um PC reinstalado ou reiniciado é o caso comum.

## 4. Encontro por código (pareamento)

### 4.1 Divisão do código

```
código de 12 dígitos = code4 ‖ secret8
code4   : número de encontro, alocado pela ponte (0000–9999)
secret8 : segredo do PC e do celular; entra só no SPAKE2 (P5)
```

- **B4.1** O agente pede `{"t":"pair.open"}` pelo canal de controle (ou
  na consulta sob demanda: `{"pair_open":true}` no corpo). A ponte aloca
  um `code4` **aleatório entre os livres**, com validade de **5 min
  (fixo)**, e responde `{"t":"pair.opened","code4":"4821","expires_at":…}`.
  O agente sorteia `secret8` com CSPRNG, monta o código e o devolve à
  extensão em `pair.start.data.code` (R10.38 e §10.6.8 do TRCP).
- **B4.2** Colisão não existe por construção: só a ponte aloca, e só entre
  livres. Se os 10 000 números estiverem ocupados, `pair.open` recebe
  `{"t":"error","code":"busy"}` e o agente responde `pair.failed{code:
  "busy"}` à extensão (R10.37 já tem o texto). Como só agentes inscritos
  abrem números (§3), esgotar o espaço não é ataque externo; é falha
  operacional e entra nas métricas de §10.
- **B4.3** Um número aberto por agente (R10.37) e no máximo 5 por chave
  de inscrição **[P4]**. `pair.renew` = fechar o número atual e abrir
  outro; `pair.cancel` fecha. Vencido, o número volta ao conjunto livre
  depois de uma quarentena de 10 min **[P4]**, para que um celular
  atrasado receba `expired`, não um encontro alheio.

### 4.2 Reivindicação pelo celular

- **B4.4** O celular abre `GET /v1/pair/<code4>` (Upgrade). Estados:
  - número aberto e ainda não reivindicado: a ponte marca **reivindicado**
    (uso único), envia ao agente `{"t":"call","call_id":…,"kind":"pair"}`
    (ou o enfileira para a próxima consulta, §6) e espera o `accept`;
  - número em quarentena (venceu há menos de 10 min): Close 4404
    `{"code":"expired"}`;
  - número nunca aberto ou já reciclado: Close 4404 `{"code":"unknown"}`;
  - número já reivindicado nesta validade: Close 4409
    `{"code":"claimed"}`;
  - agente não atendeu no prazo: Close 4408 `{"code":"accept_timeout"}`.
- **B4.5** Mapeamento para os códigos de `pair.failed` que o celular
  mostra (exigências P3, R10.39): `expired` → `expired`; `unknown` →
  `wrong_code` (texto de código incorreto); `claimed` → texto novo
  `pair.err_claimed` ("Este código já foi usado. Gere outro no
  computador."), a cargo de P7; `accept_timeout` e qualquer falha de
  transporte com a ponte → `bridge_down`. O agente, por sua vez, só
  responde `wrong_code` à extensão depois de a confirmação SPAKE2 falhar
  (P5): a ponte não sabe se o segredo estava certo.
- **B4.6** Depois de `linked` nos dois lados, o pareamento inteiro
  (SPAKE2, troca de chaves, código de confirmação de 6 dígitos, nome do
  aparelho) corre em frames binários que a ponte não lê
  (`security.md` §4). Quando o agente fecha a conexão (sucesso, recusa,
  `wrong_code`, `confirm_timeout`, `cancelled`), a ponte fecha a do
  celular com Close 1000 se o agente fechou com 1000, e 1001
  `{"code":"peer_gone"}` nos demais casos. O motivo detalhado já chegou
  ao celular por dentro do túnel.

### 4.3 Uso único e adivinhação

- **B4.7** Uma reivindicação por número por validade. A segunda recebe
  `claimed`. **Consequência aceita (residual):** quem adivinha um
  `code4` aberto antes do celular legítimo ocupa o encontro; o agente
  vê o SPAKE2 falhar (probabilidade 1 − 10^-8 de o intruso não ter
  `secret8`), responde `pair.failed{code:"wrong_code"}` e a pessoa gera
  outro código (R10.39, tentativa única). Não há como o intruso chegar ao
  PC: `security.md` §4.5.
- **B4.8** Limites que tornam a varredura cara (§7): 10 reivindicações
  por minuto e 60 por hora por IP **[P4]**; 3 reivindicações
  inválidas seguidas para o mesmo agente em 10 min fazem o agente
  **pausar o pareamento por 10 min** e avisar a extensão
  (`pair.failed{code:"busy"}` com `data{reason:"abuse"}`; texto a cargo de
  P7). **[INFERÊNCIA]** varrer os 10 000 números de um único IP leva
  ~17 h no limite horário; uma botnet consegue, e por isso o dano é
  limitado a atrapalhar um pareamento, nunca a completar um.
- **B4.9** Enumeração: `4404 unknown` versus `4404 expired` versus
  `4409 claimed` revela se um número está ou esteve aberto. Isso é
  inerente a um número de 4 dígitos que serve só de rota, e não expõe
  segredo algum. Os limites de B4.8 valem igualmente para respostas 4404.

## 5. Chamada e repasse

### 5.1 Chamada

- **B5.1** O celular abre `GET /v1/connect/<agent_id>` (Upgrade). Se o
  agente está registrado (modo permanente) ou consultou nos últimos
  `2 × interval_s` (modo sob demanda), a ponte cria `call_id` (16 bytes
  aleatórios, base64url), envia `{"t":"call","call_id":…,"kind":"session"}`
  ao agente e espera o `accept` por `accept_timeout_s` (10 s permanente;
  `pending_wait_s` = 15 s sob demanda **[P4]**). O celular vê a espera
  como "conectando".
- **B5.2** `call_id` é de uso único, vale só por esse prazo e só para o
  `agent_id` chamado. `accept` com `call_id` desconhecido, vencido ou já
  usado: Close 4404 `{"code":"no_call"}`.
- **B5.3** Agente ausente: Close 4404 `{"code":"agent_offline","since":
  <ms desde a época, opcional>}`. `since` é a hora em que o último
  registro terminou (ou a última consulta, no modo sob demanda), vinda
  só da memória: depois de reiniciar a ponte ele fica ausente e o app
  mostra "offline" sem hora. O agente PODE desligar `since` com
  `presence_since:false` no registro. Decisão de privacidade em §5.4.
- **B5.4** Cada agente atende no máximo `max_pending` = 4 chamadas
  simultâneas ainda não aceitas **[P4]** e 8 conexões de dados ligadas
  (espelha "8 conexões remotas por agente" de `trcp-1.md` §14). Acima:
  Close 4429 `{"code":"limit","what":"calls"}` para o celular.
- **B5.5** O agente atende abrindo `GET /v1/agent/accept?call=<call_id>`
  (Upgrade). A ponte liga as duas conexões, envia `{"t":"linked"}` para
  ambas e passa ao repasse. Quem recebe `linked` só então começa o TLS
  ponta a ponta (o celular como cliente TLS, o agente como servidor;
  `security.md` §5).

### 5.2 Repasse

- **B5.6** Depois de `linked`, a ponte copia cada frame binário recebido
  de um lado para o outro, **preservando os limites de frame** e sem
  agrupar. Frames de controle WebSocket (Ping, Pong, Close) não
  atravessam: a ponte responde Ping com Pong localmente e trata Close
  como fim do par.
- **B5.7** Fim do par: quando um lado fecha (Close, erro, TCP caiu), a
  ponte fecha o outro com o **mesmo código** se ele for 1000 ou 1001 e
  com 1001 `{"code":"peer_gone"}` nos demais casos. A ponte NÃO DEVE
  repassar reasons: os motivos TRCP (4403, 4410, 4409...) já viajam
  dentro do TLS, ponta a ponta (`trcp-1.md` §13.3).
- **B5.8** Contrapressão: cada sentido tem um buffer de saída de no máximo
  256 KiB **[P4]**. Cheio, a ponte para de ler do lado rápido (sem
  descartar frames). Se o lado lento não drena nada por 30 s **[P4]**, a
  ponte fecha o par: 4429 `{"code":"slow"}` para o lento, 1001
  `peer_gone` para o outro.
- **B5.9** A ponte NÃO DEVE registrar em disco nem em log de operação o
  conteúdo dos frames, e NÃO DEVE guardar frames além do buffer de
  contrapressão.
- **B5.10** Conexão de dados sem `linked` em 15 s (celular esperando o
  agente) recebe o Close de B5.1/B4.4; conexão de dados que ficou
  60 s **[P4]** sem nenhum frame em qualquer sentido é fechada com 1001
  `{"code":"idle"}`. **[INFERÊNCIA]** com o Ping TRCP a cada 20 s dentro
  do túnel (R3.10) um par vivo nunca fica 60 s calado; o teto só apanha
  pares mortos.

### 5.3 Códigos de fechamento da ponte

| Código | Reason | Quando |
|---|---|---|
| 1000 | — | Fim normal iniciado por um lado (repassado) |
| 1001 | `{"code":"peer_gone"}` / `{"code":"idle"}` / `{"code":"restart"}` | O outro lado caiu; ociosa; ponte reiniciando |
| 4400 | `{"code":"protocol"}` | Frame do tipo errado, JSON inválido, mensagem de controle fora de ordem |
| 4401 | `{"code":"enroll"}` | Chave de inscrição desconhecida, prova inválida ou fora do prazo |
| 4403 | `{"code":"enroll_revoked"}` | Chave revogada (prova bateu com o segredo revogado) |
| 4404 | `{"code":"agent_offline","since":…}` / `expired` / `unknown` / `no_call` | Agente ausente; número vencido; número nunca aberto; `call_id` inválido |
| 4408 | `{"code":"accept_timeout"}` | Agente não atendeu no prazo |
| 4409 | `{"code":"claimed"}` / `{"code":"replaced"}` | Número já reivindicado; registro substituído |
| 4429 | `{"code":"limit","what":…,"retry_ms":…}` / `{"code":"slow"}` / `{"code":"rate","retry_ms":…}` | Teto de agentes, chamadas ou conexões; lento; limite por IP |

- **B5.11** Reason: objeto JSON UTF-8 de até 123 bytes, `code`
  obrigatório (mesma regra de R13.2/R13.3). Nunca leva `agent_id` de
  terceiros, IP nem chave.
- **B5.12** O celular trata 4404 `agent_offline` como "PC offline pela
  ponte" (§13.5 do TRCP, E2), 4429 como espera de `retry_ms`, 1001 e
  falhas de transporte como `global.reconnecting`, e nunca reconecta
  sozinho depois de 4404 `expired`/`unknown`/`claimed` (fim do
  pareamento). O agente trata 4401 e 4403 como "chave de inscrição
  inválida/revogada" e avisa a extensão (`vsc.bridge_key_*`, textos de
  AJ-25/AJ-26 a completar em P7).

### 5.4 Presença ("offline desde 14:02", E2)

- **B5.13** Não há consulta de presença separada: a tentativa de chamada
  **é** a consulta (PA9 de `privacy.md` §15: o pedido não identifica o
  celular; a ponte vê só IP e `agent_id`). Um celular que só quer a lista
  de PCs online chama cada `agent_id` pareado e fecha com 1000 logo após
  `linked`, sem completar o TLS, ou mantém a conexão para uso. O app
  DEVERIA reaproveitar a mesma conexão para a sessão.
- **B5.14** **Vazamento residual aceito:** quem conhece um `agent_id`
  (um celular pareado, inclusive depois de revogado) pode saber se o PC
  está online e desde quando saiu. `agent_id` é um ULID com 80 bits
  aleatórios (R7.1), então não é enumerável; a revogação já orienta a
  pessoa a tratar aquele celular como hostil; e a ponte, por definição,
  já sabe a presença. Quem quiser esconder o `since` usa
  `presence_since:false`. Registro em `security.md` §3 (ameaça TB-6).
- **B5.15** PA-2 (`requisitos-nao-funcionais.md` §7): o texto
  `settings.bridge_ok` "alcançável · {ms} ms" mostra o tempo de ida e
  volta de um `GET /v1/health` medido pelo app, que é o tempo até a
  **ponte**. O Ping/Pong do TRCP (R3.11) mede até o agente e não aparece
  nessa tela.

## 6. Modos: permanente e sob demanda

### 6.1 Permanente

- **B6.1** O agente mantém o canal `/v1/agent` aberto. A ponte envia Ping
  a cada `keepalive_s` = 25 s **[P4]** e considera o agente ausente sem
  Pong em 10 s **[P4]**; o agente reconecta com espera exponencial de 1 s
  a 30 s com variação aleatória e mantém a mesma política de sobrevivência
  ao suspender/retomar o PC.
- **B6.2** Onde roda: VM pequena (**[FATO]** o nível gratuito do Google
  Cloud inclui "1 non-preemptible `e2-micro` VM instance per month" em
  `us-west1`, `us-central1` ou `us-east1`, com 30 GB de disco padrão e
  1 GB de saída por mês,
  https://docs.cloud.google.com/free/docs/free-cloud-features), VPS de
  qualquer provedor, ou Raspberry com IP público (CGNAT exige IP da
  operadora ou um VPS na frente; proposta §3, §4.1).
- **B6.3** Custo dominante: o tempo com sessões abertas não custa nada a
  mais numa VM; a latência de "chamar o PC" é ~1 RTT ponte↔PC.

### 6.2 Sob demanda (Cloud Run, zero instâncias ociosas)

- **B6.4** O agente **não** mantém canal aberto: faz `POST /v1/agent/poll`
  a cada `interval_s` (4 s por padrão **[P4]**; 2 s enquanto o PC tem
  pedido de atenção aberto, 15 s quando o PC está ocioso há mais de 30
  min, sempre obedecendo o `interval_s` devolvido pela ponte). Cada
  consulta é uma requisição HTTP de poucos milissegundos.
- **B6.5** Chamada pendente: a ponte segura a conexão do celular por
  `pending_wait_s` = 15 s e entrega `call` na próxima consulta; o agente
  abre `accept`; o par fica ligado enquanto a sessão durar. **[FATO]**
  "A Cloud Run instance that has any open WebSocket connection is
  considered active, so CPU is allocated and the service is billed as
  instance-based billing"
  (https://docs.cloud.google.com/run/docs/triggering/websockets): a
  instância só custa enquanto há sessão ou pareamento aberto.
- **B6.6** Configuração de referência: `--max-instances=1`,
  `--min-instances=0`, `--concurrency=1000`, `--timeout=3600`, 1 vCPU,
  256 MiB, `--session-affinity`. **[FATO]** o tempo limite de requisição
  "is set by default to 5 minutes (300 seconds) and can be extended up to
  60 minutes (3600 seconds)"
  (https://docs.cloud.google.com/run/docs/configuring/request-timeout);
  "WebSockets clients connecting to Cloud Run should handle reconnecting
  to the server if the request times out" (página de WebSockets acima).
  Logo, no modo sob demanda **toda conexão de dados cai a cada 60 min**:
  o celular reconecta e faz `resume` (TRCP §8); o agente fecha e reabre
  o `accept` só quando chamado de novo.
- **B6.7** Estado só em memória, e a instância pode sumir a qualquer
  momento. Por isso: (a) nonces de consulta são sem estado (B3.11);
  (b) números de encontro vivem só enquanto o agente os renova (o agente
  reenvia `pair_open:{code4}` em cada consulta enquanto o código está na
  tela; se a instância morreu, a ponte reabre o **mesmo** `code4` se
  livre, ou responde `pair.reopen_failed` e o agente manda `pair.renew`
  à extensão); (c) `since` de presença se perde (B5.3).
- **B6.8** `--max-instances=1` não é garantia: **[FATO]** "this maximum
  setting can be exceeded for a brief period due to circumstances such as
  traffic spikes"
  (https://docs.cloud.google.com/run/docs/configuring/max-instances), e a
  afinidade de sessão "is *best effort*"
  (https://docs.cloud.google.com/run/docs/configuring/session-affinity).
  Se o celular e a consulta do agente caírem em instâncias diferentes, a
  chamada não é entregue e o celular recebe 4404 `agent_offline` após
  `pending_wait_s`; o app tenta de novo em 15 s (`global.reconnecting`).
  Aceito como degradação rara em ponte de poucos usuários.
- **B6.9** Estimativa de custo **[INFERÊNCIA a partir de números
  oficiais]** com os valores da página de preços conferidos em
  2026-09-27 (https://cloud.google.com/run/pricing — mudam com o tempo):
  nível gratuito mensal de 2 milhões de requisições, 180 000 vCPU-s e
  360 000 GiB-s; além dele, US$ 0,000024 por vCPU-s, US$ 0,0000025 por
  GiB-s e US$ 0,40 por milhão de requisições. Consultas a cada 4 s ≈
  650 000 requisições/mês (dentro do gratuito); sessões abertas ≈ 3 600
  vCPU-s por hora, ou seja, ~50 h/mês de sessão dentro do gratuito e
  ≈ US$ 0,09 por hora além disso.

### 6.3 O que muda para os clientes

| Aspecto | Permanente | Sob demanda |
|---|---|---|
| Latência ponte→PC ao chamar | ~1 RTT | até `interval_s` + 1 RTT (p95 ≤ 5 s com 4 s) |
| Conexão de dados | dura o que a sessão durar | cai a cada 60 min (Cloud Run); `resume` |
| Presença `since` | conhecida enquanto a ponte viver | só a última consulta em memória |
| Pareamento | igual | igual; o agente renova o número a cada consulta |
| Push (FCM) | a ponte envia na hora | a ponte envia na hora (o agente entrega o pedido de push na consulta) |

- **B6.10** O celular não sabe nem precisa saber o modo. O agente escolhe
  por configuração (`pipa.bridge.mode`, padrão `auto`: tenta o canal de
  controle e cai para consulta se a ponte responder `registered{mode:
  "poll"}`, o que a ponte faz quando roda com `--mode on-demand`).

### 6.4 Metas (PA-8)

- **B6.11** Modo permanente: as metas de abrir o app de
  `requisitos-nao-funcionais.md` (NFR-23, NFR-24) valem sem mudança. Modo
  sob demanda: do toque em "conectar" até `linked`, p95 ≤ 10 s e p50 ≤ 5
  s **[P4]**, medidos em M6 com `interval_s` = 4 s; de `linked` até a
  lista ao vivo valem as mesmas metas do modo permanente (o restante do
  caminho é igual).
- **B6.12** PA-11 (~5 RTT até a lista ao vivo): a ponte não acrescenta
  viagem depois de `linked`; juntar etapas do handshake é assunto do TRCP
  e do TLS (P5 §5.7 registra que o TLS 1.3 mútuo custa 1 RTT e o Upgrade
  mais 1; sem 0-RTT por decisão).

## 7. Abusos e limites

### 7.1 Tabela de limites

| Item | Valor | Ao passar |
|---|---|---|
| Linha de pedido + cabeçalhos do Upgrade | 8 KiB **[P4]** | 431 e fecha |
| Tempo até completar o Upgrade | 5 s **[P4]** | fecha TCP |
| Conexão de controle sem `register` válido | 5 s **[P4]** | 4401 |
| Conexão de dados sem `linked` | 15 s | 4404/4408 conforme o caso |
| Conexão ligada sem nenhum frame | 60 s **[P4]** | 1001 `idle` |
| Frame binário (payload) e mensagem | 64 KiB / 64 KiB **[P4]** | 1009 nos dois lados do par |
| Frame de texto de controle | 4 KiB **[P4]** | 4400 |
| Buffer de saída por sentido | 256 KiB; 30 s sem drenar **[P4]** | 4429 `slow` |
| Conexões simultâneas por IP | 8 **[P4]** | 4429 `rate` |
| Novas conexões por IP | 30/min **[P4]** | 4429 `rate` |
| Reivindicações de encontro por IP | 10/min, 60/h **[P4]** | 4429 `rate`; conta também as 4404 |
| Chamadas `connect` por IP | 20/min **[P4]** | 4429 `rate` |
| Consultas `poll` por agente | 1 por `interval_s/2` **[P4]** | 429 com `interval_s` maior |
| Agentes por chave de inscrição | `max_agents` (3) | 4429 `limit` |
| Encontros abertos por agente / por chave | 1 / 5 **[P4]** | `error busy` |
| Chamadas pendentes por agente | 4 **[P4]** | 4429 `limit` |
| Conexões de dados ligadas por agente | 8 **[P4]** | 4429 `limit` |
| Conexões totais | 1 000 **[P4]**, configurável | 4429 `limit` com `retry_ms` |
| Ping da ponte / Pong esperado | 25 s / 10 s **[P4]** | fecha 1001 |

- **B7.1** Limites por IP contam IPv4 por endereço e IPv6 por /64
  **[P4]**. Atrás de proxy, valem sobre o IP de `X-Forwarded-For` só
  com `--trusted-proxy` (B2.3).
- **B7.2** Toda resposta de limite DEVE ser barata: a ponte decide antes
  de alocar buffers e responde com Close curto. Nada de espera artificial
  que prenda recursos (evita transformar o limite em vetor de exaustão).

### 7.2 Configuração explícita do `tungstenite` (PA-7)

**[FATO]** os padrões do `tungstenite` 0.30 são `read_buffer_size` =
128 KiB, `write_buffer_size` = 128 KiB, `max_write_buffer_size` =
ilimitado, `max_message_size` = 64 MiB, `max_frame_size` = 16 MiB
(https://docs.rs/tungstenite/latest/tungstenite/protocol/struct.WebSocketConfig.html).

- **B7.3** A ponte DEVE configurar, por conexão: `max_message_size` =
  `max_frame_size` = 64 KiB; `read_buffer_size` = 16 KiB;
  `write_buffer_size` = 0 (escreve cada frame na hora; a coalescência
  fica com o TCP); `max_write_buffer_size` = 256 KiB (o buffer de B5.8;
  ao estourar, a escrita falha e a ponte aplica 4429 `slow`);
  `accept_unmasked_frames` = false.
- **B7.4** O agente e o app configuram as **suas** camadas WebSocket
  internas (dentro do TLS) com `max_message_size` = 256 KiB (`trcp-1.md`
  §14) e frames externos de até 64 KiB; `security.md` §12 repete a regra
  para o agente. Memória por par no pior caso: 2 × (256 KiB + 16 KiB) +
  frames em voo ≈ 0,6 MiB; 100 pares ≈ 60 MiB, dentro dos 256 MiB da
  configuração de B6.6.

### 7.3 Catálogo de abusos

| Abuso | Controle | Residual |
|---|---|---|
| Força bruta do encontro (`code4`) | espaço de 10^4 é só rota; uso único; limites por IP (B4.8); pausa do agente; o segredo de 8 dígitos nunca chega à ponte | atrapalhar um pareamento (B4.7) |
| Adivinhar `secret8` | nunca passa pela ponte; uma tentativa SPAKE2 por código (P5 §4.5) | 10^-8 por código |
| Enumerar agentes | `agent_id` com 80 bits aleatórios; sem listagem | conhecer `agent_id` = ver presença (B5.14) |
| Enumerar chaves de inscrição | prova HMAC com nonce; 4401 genérico; 4403 só com prova válida | — |
| Registrar agentes falsos com chave vazada | `max_agents`; revogação imediata; rotação | uso de capacidade até revogar |
| Exaustão de conexões / memória | tetos por IP e globais; buffers pequenos e fixos; nenhuma alocação antes do Upgrade válido | DDoS volumétrico (fora do escopo; plataforma) |
| Slowloris (cabeçalhos lentos, Upgrade nunca completa) | 5 s para o Upgrade; 8 KiB de cabeçalhos; sem retenção de pedidos parciais | — |
| Leitor lento (segura o par) | contrapressão limitada + 30 s | — |
| Amplificação | a ponte nunca envia mais bytes do que recebe, exceto frames de controle de poucas dezenas de bytes; só TCP | — |
| Ponte falsa (DNS ou proxy hostil) | WebPKI no externo; e, mesmo com a ponte falsa, TLS mútuo fixado impede ler ou falar com o PC (P5) | negação de serviço; metadados |
| Operador curioso | não há conteúdo; sem log por padrão (§9); `since` desligável | metadados de §1 |
| Reprodução de `register`/`poll` | nonce de uso único de 32 bytes (canal) ou com validade de 60 s e preso ao `agent_id` (poll) | — |
| Sequestro de `call_id` | 16 bytes aleatórios, uso único, 30 s; o par ligado a um agente falso não completa o TLS mútuo | — |

## 8. Push (FCM) — quem envia e onde fica a credencial

Resolve o ponto em aberto 4 do `adr/README.md`, o item 15 de
`trcp-1.md` §19.2 e PA8 de `privacy.md` §15, junto com `security.md`
§3.2 (push) e §17 (DS-1).

- **B8.1** **A ponte envia**; o agente **nunca** guarda credencial do
  FCM. Motivo: a alternativa distribuiria uma credencial de conta de
  serviço do Google em cada PC de usuário (PS-1..PS-3 de `privacy.md`),
  onde vazaria. **[FATO]** a API HTTP v1 do FCM é autorizada com "a
  short-lived OAuth 2.0 access token" obtido de credenciais de conta de
  serviço, escopo `https://www.googleapis.com/auth/firebase.messaging`
  (https://firebase.google.com/docs/cloud-messaging/auth-server), e o
  papel IAM necessário é "Firebase Cloud Messaging API Admin"
  (`roles/firebasecloudmessaging.admin`,
  https://firebase.google.com/docs/projects/iam/roles-predefined-product).
- **B8.2** Onde fica a credencial: em Cloud Run, **nenhum arquivo de
  chave**: a ponte usa a identidade de serviço da própria instância
  (conta de serviço dedicada, só com o papel acima). **[FATO]** a
  documentação recomenda conta de serviço gerida pelo usuário com
  permissões mínimas e o código obtém credenciais por Application Default
  Credentials, sem arquivo
  (https://docs.cloud.google.com/run/docs/securing/service-identity). Em
  VM/VPS/Raspberry: arquivo JSON da conta de serviço em
  `/etc/trc-bridge/fcm.json`, modo 0600, rotação a cada 90 dias
  **[P4]**, ou Workload Identity Federation quando houver.
- **B8.3** Fluxo: o agente manda pela conexão de controle (ou no corpo
  da consulta) `{"t":"push","token":…,"attention_id":…,"priority":
  "high"|"normal","ttl_s":120}`; a ponte monta a mensagem **só de dados**
  `{agent_id, attention_id}` (R10.46, ADR-0014) e chama o FCM. **[FATO]**
  "Maximum payload for both message types is 4096 bytes"
  (https://firebase.google.com/docs/cloud-messaging/customize-messages/set-message-type);
  o nosso tem menos de 100 bytes.
- **B8.4** Privacidade (BR-1/BR-2 de `privacy.md` §8.2): token e hora
  ficam **só em memória** durante a chamada ao FCM; nunca em log, nem no
  registro de acesso de §9. Erros do FCM viram só contador. O agente
  recebe `{"t":"push.result","attention_id":…,"ok":bool,"unregistered":
  bool}`: com `unregistered`, o agente apaga o token (R10.45).
- **B8.5** Pontes de terceiros: o token FCM do app é do projeto Firebase
  da Pipa; só credenciais **desse** projeto enviam para ele. Uma ponte
  própria não tem como enviar push para o app publicado. Opções e
  recomendação em `security.md` §17 **DS-1** (decisão de Sr. Garioli).
  Até lá: pontes com `--fcm` desligado respondem `push.result{ok:false,
  reason:"no_push"}` e o agente informa a extensão uma vez.
- **B8.6** PA-3 (`requisitos-nao-funcionais.md` §7): o push de pedido vai
  com prioridade alta e `ttl_s` 120; o push de limpeza com prioridade
  normal e `ttl_s` 60. O que o app faz ao receber (mostrar a notificação
  genérica na hora e depois corrigir) é proposta para R10.47 em
  `security.md` §16 (F-07).

## 9. Registro de acesso (opcional, desligado por padrão — DP1 (c))

**[FATO]** Lei 12.965/2014 (Marco Civil), art. 15: "O provedor de
aplicações de internet constituído na forma de pessoa jurídica deverá
manter os respectivos registros de acesso a aplicações de internet, sob
sigilo, pelo prazo de 6 (seis) meses"; art. 5º VIII define esses
registros como "o conjunto de informações referentes à data e hora de uso
de uma determinada aplicação de internet a partir de um determinado
endereço IP"; art. 10 §1º condiciona a disponibilização a ordem judicial
(https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2014/lei/l12965.htm;
texto conferido no espelho da Câmara,
https://www2.camara.leg.br/legin/fed/lei/2014/lei-12965-23-abril-2014-778630-publicacaooriginal-143980-pl.html).
Se o parecer antes de M6 disser que o art. 15 alcança a ponte privada, o
desenho abaixo já atende; senão, fica desligado.

- **B9.1** `--access-log <dir>` liga o registro. Desligado, a ponte não
  abre arquivo algum além da configuração (ADR-0004 "sem disco").
- **B9.2** Conteúdo por linha (JSON Lines, UTF-8):
  `{"ts":<RFC 3339 UTC>,"ip":<endereço>,"ev":"register"|"poll"|"pair_claim"|"connect"|"accept"|"close","role":"agent"|"phone","rid":<agent_id ou code4>}`.
  Exatamente o conjunto de DP1 (b): data e hora, IP, evento de conexão e
  ID de roteamento. **Nunca**: portas, `key_id`, rótulos, tokens de push,
  volume de bytes por par, reasons, cabeçalhos.
- **B9.3** Rotação diária; arquivos com modo 0600; expurgo automático
  após **180 dias** (o prazo legal de 6 meses, contado com folga de
  calendário); a ponte recusa iniciar se o diretório for legível por
  outros.
- **B9.4** Cifra: cada arquivo do dia é cifrado no fechamento com uma
  chave pública do operador (`age` ou equivalente, chave privada fora da
  ponte). A ponte só escreve; ler exige a chave privada. Assim um
  comprometimento da ponte não expõe o histórico.
- **B9.5** Log de operação (erros, reinícios) é separado, não contém IP
  nem ids em nível `info`, e vai para stdout/journal. Nível `debug` só
  em laboratório.

## 10. Operação

- **B10.1** Instalação: um único binário estático `trc-bridge`
  (Linux x86-64 e aarch64 para Raspberry; container OCI para Cloud Run),
  assinado com `cosign` sem chave (identidade OIDC do GitHub Actions) e
  com `SHA256SUMS` (`security.md` §14). `trc-bridge init` gera o arquivo
  de configuração e a primeira chave de inscrição.
- **B10.2** Cloud Run: `gcloud run deploy trc-bridge --image … --region
  <região> --max-instances 1 --min-instances 0 --concurrency 1000
  --timeout 3600 --cpu 1 --memory 256Mi --session-affinity
  --service-account trc-bridge@… --set-secrets /etc/trc-bridge/keys.toml=…`
  e `--args --behind-proxy --mode on-demand`. A região depende de DP4
  (`privacy.md` §14): `southamerica-east1` mantém os metadados no Brasil.
- **B10.3** VM/VPS/Raspberry: unidade `systemd` com usuário próprio,
  `ProtectSystem=strict`, `NoNewPrivileges=yes`, diretório de estado só
  se `--access-log`; TLS própria (B2.3 a) ou Caddy na frente (b).
- **B10.4** Atualização: **drenagem** ao receber `SIGTERM`: para de
  aceitar Upgrades (responde 503), fecha canais de controle com 1001
  `{"code":"restart"}` (agentes reconectam e caem na instância nova), dá
  30 s **[P4]** aos pares ligados e então os fecha com 1001 `restart`
  (celulares fazem `resume`). Em Cloud Run a revisão antiga e a nova
  coexistem brevemente (B6.8).
- **B10.5** Observabilidade sem conteúdo: contadores em memória expostos
  em `GET /v1/metrics` só para `127.0.0.1` ou com `--metrics-token`:
  conexões por tipo, pares ligados, bytes repassados (total, não por
  par), rejeições por código, chamadas sem resposta, consultas por
  segundo, falhas de push (contagem). Sem IP, sem `agent_id`, sem
  `key_id`.
- **B10.6** `GET /v1/health` responde 200 enquanto a ponte aceita novas
  conexões e 503 durante a drenagem.

## 11. Fixtures de conformidade (em prosa)

Cada fixture nomeia o cenário, a entrada e o resultado esperado; M6 as
implementa como testes de integração do `trc-bridge` com clientes falsos.

| # | Cenário | Esperado |
|---|---|---|
| BX-01 | `GET /v1/agent` sem `trcb.v1` | 400; sem alocação |
| BX-02 | Upgrade com `Origin` | 403 |
| BX-03 | `register` com prova de chave inexistente | 4401 `enroll`, em tempo indistinguível do caso de chave existente e prova errada (medir: diferença < 5 ms p95) |
| BX-04 | `register` com chave revogada e prova válida para o segredo revogado | 4403 `enroll_revoked` |
| BX-05 | `register` com chave revogada e prova inválida | 4401 `enroll` |
| BX-06 | Quarto agente da mesma chave com `max_agents` = 3 | 4429 `limit` `what:"agents"` |
| BX-07 | Segundo `register` do mesmo `agent_id` | o primeiro recebe 4409 `replaced`; o segundo fica registrado |
| BX-08 | `pair.open` duas vezes pelo mesmo agente | segundo recebe `error busy` |
| BX-09 | `pair.open` aloca sempre número livre | 10 000 aberturas em agentes distintos nunca repetem; a 10 001ª recebe `busy` |
| BX-10 | `GET /v1/pair/4821` com número aberto | agente recebe `call{kind:"pair"}`; após `accept`, ambos recebem `linked` |
| BX-11 | Segunda reivindicação do mesmo número | 4409 `claimed` |
| BX-12 | Reivindicação 4 min 59 s após abrir / 5 min 01 s | ligada / 4404 `expired` |
| BX-13 | Reivindicação 11 min após vencer | 4404 `unknown` |
| BX-14 | 11ª reivindicação do mesmo IP em 1 min | 4429 `rate` com `retry_ms` |
| BX-15 | Frame de texto depois de `linked` | 4400 para quem enviou, 1001 `peer_gone` para o outro |
| BX-16 | Frame binário de 64 KiB + 1 | 1009 para quem enviou, 1001 `peer_gone` para o outro |
| BX-17 | Leitor que não drena por 31 s | 4429 `slow` para o lento, 1001 `peer_gone` para o outro; memória da ponte não cresce além de 256 KiB por sentido |
| BX-18 | `connect` para agente registrado que não atende em 10 s | 4408 `accept_timeout`; `call_id` fica inutilizável |
| BX-19 | `connect` para `agent_id` desconhecido | 4404 `agent_offline` sem `since` |
| BX-20 | `connect` após o agente sair há 90 s | 4404 `agent_offline` com `since` ≈ agora − 90 s; com `presence_since:false`, sem `since` |
| BX-21 | `accept` com `call_id` já usado | 4404 `no_call` |
| BX-22 | Modo sob demanda: `connect` seguido de `poll` em 3 s | resposta da consulta traz `call`; par ligado em < 5 s |
| BX-23 | Modo sob demanda: `poll` com `nonce` de 61 s | 401 com `nonce` novo; nenhuma chamada entregue |
| BX-24 | Ping da ponte sem Pong por 10 s | 1001; agente marcado ausente |
| BX-25 | `SIGTERM` com um par ligado | `/v1/health` 503; controle fecha 1001 `restart`; par fecha após 30 s com 1001 `restart` |
| BX-26 | Ponte sem `--access-log` roda 1 h com tráfego | nenhum arquivo criado ou modificado fora de stdout |
| BX-27 | Ponte com `--access-log` | linhas só com `ts, ip, ev, role, rid`; arquivo 0600; nenhum token, `key_id` ou reason |
| BX-28 | Chave revogada com agente registrado e par ligado | controle 4403 `enroll_revoked`; par 1001 `peer_gone`; encontro aberto some |
| BX-29 | `push` com `--fcm` desligado | `push.result{ok:false, reason:"no_push"}` |
| BX-30 | `push` com token que o FCM diz `UNREGISTERED` | `push.result{ok:false, unregistered:true}`; nada em log |
| BX-31 | Cabeçalhos de 8 KiB + 1 ou Upgrade que demora 6 s | 431 / TCP fechado; sem alocação de buffers |
| BX-32 | `--behind-proxy` sem `--trusted-proxy` e `X-Forwarded-For` presente | o cabeçalho é ignorado; limites contam o IP do peer |

## 12. Versionamento

- **B12.1** `trcb.v1` muda de forma compatível por campos opcionais novos
  em mensagens de controle e por códigos novos de reason; mudança
  incompatível vira `trcb.v2`, e a ponte aceita as duas por pelo menos 6
  meses (mesma política de R15.4).
- **B12.2** O TRCP e o TLS internos evoluem sem tocar na ponte: ela não
  os lê.

## 13. Rastreabilidade dos pontos de P4

| Ponto (documento + id) | Onde ficou |
|---|---|
| `adr/README.md` ponto em aberto 3 (chave de inscrição: formato, emissão, revogação, guarda) | §3 |
| `adr/README.md` ponto em aberto 4 (credencial do FCM) | §8 (com `security.md` §3.2 e §17 DS-1) |
| `adr/README.md` "O que fica para P5": limite de tentativas por IP e abuso da ponte | §4.3, §7 |
| ADR-0004 (formato, emissão e revogação da chave → P4) | §3 |
| ADR-0006 (modos permanente e sob demanda; hospedagem em M6) | §6, §10 |
| ADR-0014 (quem envia o push; credencial) | §8 |
| Proposta §7 (ameaças da ponte: comprometida, código visto, adivinhação, estranhos, DoS, metadados) | §7.3, §5.4, `security.md` §3.4 |
| `trcp-1.md` §3.1 item 1 (formato e modos em P4) | §2, §6 |
| `trcp-1.md` §6.8 e §19.2 item 14 (a ponte precisa saber do corte?) | Não: B5.7; o agente segue registrado durante o corte e entrega 4410 dentro do TLS (`security.md` §9) |
| `trcp-1.md` §10.6.8, R10.39, R10.40 (lado do celular; QR; validação da ponte) | §4.2, B4.5; QR `pipa://pair?c=…&b=…&v=1`: `b` é o host da ponte que o app valida por WebPKI (B2.2) |
| `trcp-1.md` §17 linha P4 (presença E2; corte E20; ponte privada; QR; push) | §5.4, B5.7, §3, §4, §8 |
| `trcp-1.md` §19.2 item 5 (texto "2 minutos") | não é da ponte; `security.md` §16 F-06 |
| `trcp-1.md` §19.2 item 15 (push: quem envia, credencial, limpeza) | §8 |
| `trcp-1.md` §13.5 linha 1 ("PC offline pela ponte", E2) | B5.3, B5.12 |
| `exigencias-para-o-protocolo.md` E2, E20, E24, P5, I11 | §5.4; B5.7; §8; B4.5 e §13 (QR); B3.3 |
| `privacy.md` PA4 (ponte sem disco × registros de acesso) | §9 |
| `privacy.md` PA8 (quem envia o push) | §8, B8.4 |
| `privacy.md` PA9 (consulta de presença identifica o celular?) | B5.13 |
| `privacy.md` PA11 (chave por pessoa vira identificador) | B3.4 (linha nova em `privacy.md` §3.3 a cargo de P6) |
| `privacy.md` §8.2 e DP1 (c) | §8, §9 |
| `requisitos-nao-funcionais.md` PA-2 (o que a tela de RTT mostra) | B5.15 |
| `requisitos-nao-funcionais.md` PA-3 (push e `onMessageReceived`) | B8.6 e `security.md` F-07 |
| `requisitos-nao-funcionais.md` PA-7 (`tungstenite`) | §7.2 |
| `requisitos-nao-funcionais.md` PA-8 (meta do modo sob demanda) | §6.4 |
| `requisitos-nao-funcionais.md` PA-11 (viagens até a lista) | B6.12 |
| `interfaces/vscode.md` §7 e AJ-25/AJ-26 (tela da chave de inscrição segue P4) | §3.1–3.2: a tela mostra `key_id`, estado (válida, rotacionada, revogada) e nunca o segredo |
| `interfaces/android.md` §2 / AJ (campo Servidor; QR com outro servidor) | B4.5, §13 (QR) |

Textos e telas novos que esta spec pede a P7 (pequenos): `pair.err_claimed`
(B4.5), aviso de chave rotacionada (B3.7), aviso de pausa por abuso
(B4.8), estados da chave de inscrição na árvore (AJ-25/AJ-26). Nenhum
muda um fluxo aprovado.
