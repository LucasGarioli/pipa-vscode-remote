# Segurança da Pipa — threat model, criptografia e revisão (P5)

Entrega **P5** do planejamento (`docs/plans/00-mapa-do-planejamento.md`).
Estado: **escrita em 2026-09-26/27, aguarda revisão.** Autor: agente Fable
5.1 (effort max), despachado de sessão Opus com autorização explícita de
Sr. Garioli (desvio registrado no mapa). Só documento: nenhum código,
spike ou teste executável foi produzido.

Este documento é normativo para o que a spec TRCP/1 (`spec/trcp-1.md`) e
a spec da ponte (`spec/bridge.md`) deixaram para P5, e consolida o threat
model de todo o produto. Ele **não edita** a spec TRCP/1: as mudanças que
propõe estão em §16 ("Revisão da spec TRCP/1") como achados numerados,
com o texto de cada correção pequena e inequívoca ("patch proposto").

Convenções: DEVE / NÃO DEVE / DEVERIA / PODE como na spec. Fatos externos
**[FATO]** com fonte oficial; **[INFERÊNCIA]** quando é dedução minha;
decisões técnicas desta entrega **SD-n**; decisões que ficam com Sr.
Garioli **DS-n** (§17); achados da revisão da spec **F-nn** (§16). Textos
de programa e nomes de API em `código`.

## 0. Sumário executivo

1. **Pareamento**: SPAKE2 conforme a RFC 9382, suíte
   `SPAKE2-P256-SHA256-HKDF-HMAC`, com o segredo de 8 dígitos como senha,
   identidades explícitas, confirmação explícita nos dois sentidos e um
   payload cifrado (AEAD) que troca as chaves públicas e o nome do
   aparelho. O código de confirmação de 6 dígitos (SAS) sai da chave de
   sessão do SPAKE2 **e** das chaves públicas trocadas. A crate `spake2`
   fica de fora (SD-1): ela implementa só Ed25519, no formato do
   python-spake2, sem os vetores da RFC; a decisão é um módulo próprio de
   ~150 linhas sobre `p256`, gravado pelos vetores da RFC 9382 e revisado
   antes de qualquer outro código de M6.
2. **Sessão**: TLS 1.3 **mútuo**, só TLS 1.3, certificados autoassinados
   fixados pelo hash do `SubjectPublicKeyInfo`, sem cadeia, sem datas,
   sem SNI, sem tickets, sem 0-RTT. Autenticação da sessão **só pelo
   TLS mútuo** (SD-2): `auth.proof` e `hello.nonce` saem da rev 0; o
   `tls-exporter` (RFC 9266) fica documentado como reserva.
3. **Chaves do celular**: **duas** (SD-4): `K_tls` (sem autenticação de
   usuário, para toda conexão) e `K_stepup` (autenticação a cada uso,
   `BIOMETRIC_STRONG | DEVICE_CREDENTIAL`). Consequência verificada: com
   `DEVICE_CREDENTIAL` permitido, o Keystore **não** invalida a chave em
   nova biometria; o residual de T1 é "quem sabe o PIN do celular libera
   escrita", e o texto das telas precisa dizer isso. Recuperação após
   invalidação = parear de novo (SD-5). `minSdk` recomendado 30 (DS-5).
4. **Chave do PC**: P-256 no Gerenciador de Credenciais (via `keyring`,
   persistência local, blob ≤ 2 560 bytes), nunca com escopo de máquina.
5. **Step-up**: formato fechado (§8): ECDSA P-256/SHA-256 sobre
   `"trcp-stepup-v1" ‖ nonce ‖ SHA-256(campos canônicos)`, com o
   `purpose` como primeiro campo.
6. **Revogação e corte**: AJ-22 resolvido pela opção (a): o agente
   completa o TLS com chave revogada e fecha com 4403, com guardas
   (SD-3); 4410 é ponta a ponta e a ponte não sabe do corte.
7. **Perfil local**: pipe `\\.\pipe\pipa-trcd-<SID>`, primeira instância
   exclusiva, DACL só do usuário, `PIPE_REJECT_REMOTE_CLIENTS`, e prova do
   servidor por cookie de arquivo, porque a documentação não dá ao cliente
   um jeito de identificar o servidor pelo handle. EX1: origem autenticada
   pelo caminho do executável do chamador, com aprovação na primeira
   chamada (AJ-32 opção (a)).
8. **Hook do Claude Code**: o hook HTTP do ADR-0008 é inseguro em PC com
   mais de um usuário (a URL não interpola variáveis; porta fixa pode ser
   ocupada por outro usuário local, que então recebe a entrada da
   ferramenta e o token e pode responder `allow`). Recomendação: hook de
   **comando** (`trc hook`) pelo pipe (DS-3).
9. **Auditoria**: `pipa.audit.input` sai (DP3 (a)); a spec ainda o cita
   em oito lugares (F-01, o achado de maior severidade).
10. **Cadeia de suprimento**: `cargo-deny` + `cargo-vet` + `cargo audit`
    no CI, `--locked`, SBOM, `cosign` sem chave, VSIX assinado pelo
    Marketplace, Play App Signing.

## 1. Escopo, princípios e fontes

- Cobre: agente `trcd` (Windows), extensão VS Code, app Android, ponte
  `trc-bridge`, adaptador de hooks do Claude Code e entrada local de
  avisos (EX1), push FCM, releases.
- Fora do escopo declarado (aceito como limite do produto): malware
  rodando **como o mesmo usuário** no PC (T17 da auditoria: ele já lê o
  PTY e o cofre do usuário); celular com root ou bootloader destravado;
  ataques físicos ao hardware seguro; falhas do próprio Windows, Android
  ou Google.
- Princípios (proposta §6; ADR-0004, 0005, 0012): a ponte é adversário de
  rede; nenhum terceiro além do Google (push) e do provedor de hospedagem
  da ponte; o celular guarda o mínimo; falhar fechado; segredo nunca em
  texto claro em configuração; nenhuma alegação sem fonte.
- Fontes primárias consultadas em 2026-09-27 estão listadas em §19; cada
  **[FATO]** aponta para uma delas.

## 2. Ativos e fronteiras de confiança

| Ativo | Onde vive | Quem pode usar | Perda significa |
|---|---|---|---|
| Chave privada do agente (`K_agent`, P-256) | Gerenciador de Credenciais do usuário do PC | `trcd` como o usuário | quem a tiver se passa pelo PC para celulares pareados (lê nada sem a chave do celular; engana o celular) |
| Registro de aparelhos `{fingerprint, name, state, at}` | disco do agente | `trcd` | alterado, autoriza um celular estranho (mesmo usuário: fora do escopo) |
| Chave de inscrição da ponte | cofre do agente; arquivo `keys.toml` na ponte | `trcd`; ponte | uso indevido de capacidade da ponte (`bridge.md` B3.5) |
| `K_tls` do celular | Android Keystore (StrongBox/TEE), sem autenticação de usuário | o app, com o aparelho desbloqueado | quem controla o celular desbloqueado lê terminais até a revogação |
| `K_stepup` do celular | Android Keystore, autenticação a cada uso | o app, após biometria ou PIN | quem sabe o PIN ou tem biometria cadastrada libera escrita |
| Segredo de 8 dígitos | tela do PC / QR, por 5 min | quem vê a tela | corrida de pareamento (§4.5), detectada pelo SAS |
| Chave de sessão SPAKE2 e SAS | memória, durante o pareamento | agente e celular | — (efêmeros) |
| Token de push do celular | disco do agente; memória da ponte no envio | agente; ponte | spam de push (bateria); sem conteúdo |
| Conteúdo dos terminais, pedidos, contexto | memória do agente; TLS ponta a ponta | dono do PC; celulares pareados, projetado | vazamento de segredos do trabalho |
| Cookie do perfil local | arquivo do usuário, DACL só dele | processos do usuário | outro usuário local se passar pelo agente (§10) |
| Token de hook por sessão (`PIPA_HOOK_TOKEN`) | ambiente do PTY | processos naquele terminal | processo de outro terminal forja eventos (§11) |
| Binários e pacotes assinados | GitHub Releases, Marketplace, Play | usuários | troca por binário hostil (§14) |

Fronteiras: (1) PC ↔ ponte (WSS público, metadados); (2) ponte ↔
celular (idem); (3) agente ↔ celular (TLS mútuo, conteúdo); (4) agente ↔
processos locais (pipe, mesmo usuário); (5) agente ↔ Claude Code (hook);
(6) ponte ↔ FCM (HTTPS, token e ids); (7) FCM ↔ celular (Google).

## 3. Atacantes e threat model

### 3.1 Atacantes

| Id | Atacante | Capacidades assumidas |
|---|---|---|
| A1 | Rede | lê, altera, injeta e bloqueia tráfego em qualquer fronteira; controla DNS e Wi-Fi público; não quebra TLS |
| A2 | Ponte hostil ou comprometida | tudo de A1 mais: escolhe a quem liga cada conexão, forja mensagens de controle, vê IPs, `agent_id`, horários e volumes, e retém tudo |
| A3 | App Android malicioso ou adulterado | fala TRCP e TRCB como quiser; sem pareamento válido não tem chave; com pareamento (celular do próprio dono adulterado) tem as permissões do aparelho |
| A4 | Processo local no PC como **outro** usuário | cria pipes e portas antes do agente; conecta ao pipe se a DACL deixar; não lê arquivos do usuário |
| A5 | Processo local no PC como o **mesmo** usuário | fora do escopo (T17); listado para deixar explícito o que não protegemos |
| A6 | Quem tem o celular **desbloqueado** e não sabe o PIN (celular emprestado, largado aberto) | usa o app: lê terminais; não libera escrita; não remove o próprio acesso sem ver a tela |
| A7 | Quem tem o celular **bloqueado** | nada, salvo falhas do Android; `FLAG_SECURE` cobre a tela |
| A8 | Ex-autorizado (chave de inscrição revogada, ou celular revogado) | conhece `agent_id`, endereço da ponte e, talvez, ainda tem o app pareado |
| A9 | Quem vê a tela do PC no pareamento (ombro, gravação, compartilhamento de tela) | conhece os 12 dígitos por 5 min |
| A10 | Cadeia de suprimento | crate hostil, comprometimento do CI ou da conta de publicação |

### 3.2 STRIDE por componente

Cada linha: ameaça → controle → residual → referência. "spec" =
`trcp-1.md`; "ponte" = `bridge.md`.

**Agente `trcd` (PC)**

| Tipo | Ameaça | Controle | Residual / referência |
|---|---|---|---|
| S | Celular estranho se passa por pareado | TLS mútuo; chave desconhecida recusada no TLS (§5.6) | — |
| S | PC falso engana o celular (A2 liga o celular a outro agente) | celular fixa o SPKI do agente (§5.1) | — |
| T | Comando alterado em trânsito | TLS 1.3 (AEAD) ponta a ponta | — |
| T | Reprodução de comando ou step-up | `cmd.id` de uso único (spec §10.2); nonce de step-up de uso único preso à conexão (R6.14) | — |
| R | "Não fui eu" | audit no PC com aparelho e hora (§13); step-up assinado (§8) | audit sem cadeia de integridade no MVP |
| I | Bytes crus, títulos, links, área de transferência | projeção por destinatário (spec §8.2, §16 PV1–PV11; P6) | redação de P6 |
| I | Segredos em log | proibição em §13; reasons sem conteúdo (R13.4) | — |
| D | Celular pareado inunda o agente | limites §14 da spec; 4429; buffers fixos (§12) | um pareado hostil ainda gasta CPU até revogar |
| E | Escrita sem presença do dono do celular | step-up com `K_stepup` a cada `grant.arm`, `attention.respond` perigoso e `terminate` (§8) | T1: quem sabe o PIN (§6.3) |
| E | Criar terminal com shell arbitrário | `create` fora do MVP; perfis só do PC (R6.4; ADR-0002) | — |

**Extensão VS Code**

| Tipo | Ameaça | Controle | Residual / referência |
|---|---|---|---|
| S | Extensão fala com um agente falso (pipe ocupado por A4) | prova do servidor por cookie; primeira instância exclusiva; DACL (§10) | A5 |
| S | Processo local se passa pela extensão | DACL só do usuário; identidade por executável para EX1 (§10.3) | A5 |
| I | Chave de inscrição em `settings.json` ou `SecretStorage` | proibido (ponte B3.3); vai direto ao agente | — |
| E | Confirmar pareamento sem a pessoa | modal só na UI da extensão; `pair.confirm` local; 60 s | UI de outra extensão hostil = A5 |

**App Android**

| Tipo | Ameaça | Controle | Residual / referência |
|---|---|---|---|
| S | App conecta a ponte falsa (DNS, Wi-Fi) | WebPKI na ponte; mesmo assim TLS mútuo fixado impede conteúdo (ponte B2.2) | negação de serviço |
| T | Tela alterada em trânsito | TLS ponta a ponta | — |
| I | Captura de tela, miniaturas de apps recentes | `FLAG_SECURE` (ADR; Q3) | — |
| I | Backup ou migração leva as chaves | Keystore não exporta; após restauração, parear de novo (§6.6) | — |
| I | Chaves de outros aparelhos | PV5 | — |
| D | Push em massa (spam) para gastar bateria | token só conhecido pelo agente e pela ponte privada; conteúdo opaco; app só busca pelo túnel | ponte hostil pode enviar pushes até revogar a inscrição |
| E | A6 libera escrita | `K_stepup` exige biometria ou PIN a cada uso | A6 que sabe o PIN = T1 |
| E | A6 remove o acesso e apaga rastros | `device.forget` sem step-up (D-6) é o lado seguro: retira acesso, não o concede; audit fica no PC | — |

**Ponte `trc-bridge`** — detalhada em §3.4 e em `bridge.md` §7.3.

**Adaptador de hooks e entrada de avisos (EX1)**

| Tipo | Ameaça | Controle | Residual / referência |
|---|---|---|---|
| S | Processo forja um pedido de permissão do Claude Code | token por sessão no ambiente do PTY (ADR-0008); pipe só do usuário; identidade por executável | A5 |
| S | A4 ocupa a porta do hook HTTP e responde `allow` | **não há controle possível com hook HTTP**; recomendação de hook de comando (§11, DS-3) | — se DS-3 aprovada |
| I | Entrada da ferramenta (comandos, conteúdo de arquivos) vai para quem ocupou a porta | idem | idem |
| T | Aviso EX1 com texto enganoso ("aprove agora") | avisos são projetados como texto, nunca como pedido com botões `allow` (privacy §6.3 AV-*); `destructive` para heurística (§8, tabela) | engenharia social |
| D | Chamador local inunda avisos | limite por origem autenticada (NFR-60; PA-12) e global | — |

**Push (FCM)**

| Tipo | Ameaça | Controle | Residual / referência |
|---|---|---|---|
| I | Google vê o conteúdo | payload só `{agent_id, attention_id}` (R10.46) | Google vê hora e frequência |
| I | Operador da ponte vê token e hora | só em memória; sem log (ponte B8.4) | metadado para o operador |
| S | Push forjado | app trata push só como "vá buscar"; tudo vem pelo túnel (R10.47) | — |
| I | Credencial do FCM vaza de um PC | agente nunca a tem (ponte B8.1) | — |

**Cadeia de suprimento** — §14.

### 3.3 Ameaças herdadas da auditoria (T1–T17)

| T | Resumo | Onde fica |
|---|---|---|
| T1 | Biometria nova cadastrada por terceiro que sabe o PIN | §6.3: com `DEVICE_CREDENTIAL` a invalidação não se aplica; residual explícito; opção "só biometria" (DS-4) |
| T2 | Celular roubado desbloqueado | A6: leitura até revogar; escrita exige `K_stepup`; kill switch e revogação no PC (§9) |
| T3, T4 | Rede/tailnet (obsoletas: transporte trocado pela ponte) | §3.4 |
| T5 | Replay de comandos | `cmd.id`, nonce de step-up (spec §10.2, R6.14) |
| T6 | Injeção de sequências VT do celular | `input.send` só texto e teclas nomeadas; agente valida (spec §10.6) |
| T7 | Shell arbitrário | `create` fora do MVP (R6.4) |
| T8 | Bytes crus / OSC para o celular | PV1, PV7 |
| T9 | Ponte lê conteúdo | TLS mútuo ponta a ponta (§5) |
| T10 | Adivinhar código de pareamento | §4.5 |
| T11 | Hook forjado por processo local | §11 (token + identidade); DS-3 |
| T12 | Extensão hostil no VS Code | A5, fora do escopo; mitigação parcial: perfil local só faz o que a UI faz |
| T13 | Autorização só no handshake | R6.1 (a cada mensagem) |
| T14 | Log com segredos | §13; R13.4; PV10 |
| T15 | Dependência vulnerável | §14 |
| T16 | Push com conteúdo | R10.46 |
| T17 | Malware do mesmo usuário | fora do escopo (declarado) |

### 3.4 Ponte hostil ou comprometida (A2)

| Id | Ameaça | Controle | Residual |
|---|---|---|---|
| TB-1 | Ler ou alterar sessões | TLS 1.3 mútuo fixado; sem compressão; sem tickets | volume e horários |
| TB-2 | Ligar o celular a um agente falso (ou o agente a um celular falso) | fixação de SPKI nos dois lados; cliente TLS falso não tem `K_tls` | — |
| TB-3 | MITM no pareamento | SPAKE2: sem `secret8`, a ponte tem uma tentativa contra o celular e uma contra o agente por código (§4.5); confirmação explícita `cA`/`cB`; SAS compara chaves | 2 × 10^-8 por código |
| TB-4 | Ataque offline ao segredo a partir do tráfego do pareamento | propriedade do SPAKE2 (RFC 9382): o transcrito não permite testar senhas offline; Argon2id em `w` por precaução (§4.1) | — |
| TB-5 | Rebaixar a versão do TLS interno | só TLS 1.3 aceito pelos dois lados | — |
| TB-6 | Presença e padrões de uso | inerente ao papel de repassador; `since` desligável (ponte B5.3, B5.14); sem log por padrão | metadados |
| TB-7 | Negar serviço a um usuário | inerente; usuário troca de ponte (própria) | — |
| TB-8 | Enviar pushes falsos ou em excesso | app só busca pelo túnel; sem conteúdo; revogar inscrição | bateria |
| TB-9 | Forjar `linked` antes de ligar o par de verdade | o TLS mútuo falha; nada é revelado além do `ClientHello` (sem SNI) | — |

### 3.5 Celular perdido e ex-autorizado

- **Desbloqueado, PIN desconhecido (A6):** lê terminais dos PCs pareados
  até a revogação no PC (I6) ou o corte (I7); não libera escrita; pode
  `device.forget` (perde acesso). Mitigação de produto adiada: pedir
  desbloqueio ao abrir o app foi decidido negativamente (Q10, ADR-0003);
  não reaberto aqui. A pessoa que perde o celular revoga no PC ou corta o
  acesso remoto (fluxo aprovado I6/I7).
- **Desbloqueado, PIN conhecido:** libera escrita (T1); mesmas
  mitigações; o PC mostra "controlado remotamente por <aparelho>" e
  registra tudo no audit.
- **Bloqueado (A7):** nada.
- **Celular revogado (A8):** o TLS completa só para receber 4403 (§5.5);
  sabe presença do PC pela ponte (`bridge.md` B5.14); não recebe conteúdo.
- **Chave de inscrição revogada (A8):** o agente perde a ponte
  (`enroll_revoked`); os celulares dele veem "PC offline". Os pareamentos
  continuam válidos se ele apontar para outra ponte: a revogação de
  inscrição é sobre **capacidade da ponte**, não sobre os PCs dele.

## 4. Pareamento: SPAKE2 (RFC 9382)

### 4.1 Perfil escolhido

| Parâmetro | Valor | Fonte |
|---|---|---|
| Protocolo | SPAKE2, RFC 9382, com confirmação de chave explícita nos dois sentidos | **[FATO]** https://www.rfc-editor.org/rfc/rfc9382.html |
| Suíte | `SPAKE2-P256-SHA256-HKDF-HMAC` (P-256, SHA-256, HKDF, HMAC-SHA-256); pontos `M`, `N` da RFC §4; cofator `h` = 1 em P-256 | idem |
| Papéis | A = celular (quem reivindica), B = agente | — |
| Identidades | `idA` = `"pipa:phone"`; `idB` = `"pipa:agent:" ‖ agent_id` (26 caracteres ULID). **[FATO]** a RFC só permite identidade vazia "for applications in which identities are implicit. Otherwise, the protocol risks unknown key-share attacks" | RFC 9382 §3.3 |
| Senha `pw` | os 8 dígitos ASCII de `secret8` | — |
| `w` | `w = Argon2id(pw, salt, m = 64 MiB, t = 3, p = 1, 64 bytes)` lido como inteiro big-endian, `mod n` (ordem do grupo). `salt` = os 16 primeiros bytes de `SHA-256("trcp-pair-v1" ‖ code4)`. **[FATO]** a RFC define `w = MHF(pw) mod p` e diz que "The hashing algorithm SHOULD be an MHF" | RFC 9382 §3.2; Argon2: RFC 9106 |
| Transcrito `TT` | `len(idA)‖idA‖len(idB)‖idB‖len(pA)‖pA‖len(pB)‖pB‖len(K)‖K‖len(w)‖w`, com `len` de 8 bytes little-endian; `pA`, `pB`, `K` em SEC1 comprimido (33 bytes); `w` em 32 bytes big-endian | RFC 9382 §3.3 |
| Chaves | `Ke ‖ Ka = SHA-256(TT)` (16 + 16 bytes); `KcA ‖ KcB = HKDF-SHA-256(IKM = Ka, salt = vazio, info = "ConfirmationKeys" ‖ AAD, L = 32)`; `AAD = "trcp-pair-v1" ‖ code4` | RFC 9382 §3.3, §4 |
| Confirmação | `cA = HMAC-SHA-256(KcA, TT)`, `cB = HMAC-SHA-256(KcB, TT)` | idem |
| Chave do payload | `Kp = HKDF-SHA-256(IKM = Ke, salt = vazio, info = "trcp-pair-payload-v1", L = 32)`; AEAD ChaCha20-Poly1305 (RFC 8439); nonce de 12 bytes = 11 bytes zero ‖ contador por sentido (A: 0x01, 0x03; B: 0x02, 0x04) | HKDF: RFC 5869 |
| Vetores de teste | Apêndice B da RFC (só a suíte P-256; campos `A, B, w, x, y, pA, pB, K, TT, Hash(TT), Ke, Ka, KcA, KcB, cA, cB`) como fixtures do módulo | RFC 9382 App. B |

Por que Argon2id se o SPAKE2 já impede ataque offline: é a recomendação
da RFC (SHOULD), custa ~0,1–0,3 s uma vez por pareamento, e protege se
uma falha de implementação vazar algo do transcrito. Parâmetros modestos
porque a força real vem do protocolo, não da memória.

### 4.2 Mensagens dentro do encontro

Depois de `linked` (`bridge.md` B5.5) e antes de qualquer TLS. Formato
binário fixo (a ponte não lê): `ver(1) ‖ tipo(1) ‖ campos`, campos de
tamanho fixo ou prefixados por `u16` big-endian. Sem JSON: o transcrito
usa bytes exatos.

| Msg | Sentido | Conteúdo |
|---|---|---|
| PM1 | celular → agente | `0x01 0x01 ‖ pA(33)` |
| PM2 | agente → celular | `0x01 0x02 ‖ pB(33) ‖ agent_id(26) ‖ cB(32)` |
| PM3 | celular → agente | `0x01 0x03 ‖ cA(32) ‖ AEAD(Kp, n=…01, payload_A)` |
| PM4 | agente → celular | `0x01 0x04 ‖ AEAD(Kp, n=…02, payload_B)` |
| PM5 | agente → celular | `0x01 0x05 ‖ AEAD(Kp, n=…04, {result})` |

- `payload_A` (CBOR ou TLV, decidir em M6; campos): `device_name` (≤ 40
  caracteres depois de normalizar, §4.6), `spki_tls` (DER do
  `SubjectPublicKeyInfo` de `K_tls`), `spki_stepup` (idem de `K_stepup`),
  `app_version`, `caps` (lista de strings, reservada).
- `payload_B`: `agent_name` (≤ 63), `spki_agent`, `agent_version`,
  `bridge_hint` (host da ponte como o agente a conhece, para o app
  comparar com o que a pessoa digitou e avisar divergência; informativo).
- `result`: `"ok"`, `"rejected"`, `"confirm_timeout"`, `"cancelled"`.
- **SP4.1** O celular DEVE verificar `cB` antes de enviar PM3; `cB`
  inválido = `wrong_code` na tela do celular e fim (o agente nunca soube).
- **SP4.2** O agente DEVE verificar `cA` antes de decifrar `payload_A`;
  `cA` inválido = `pair.failed{code:"wrong_code"}` à extensão, invalidação
  do código na hora (R10.39) e Close. Só depois de `cA` válido e do
  payload aceito o agente emite `pair.claimed{device_name, sas}` (F-10).
- **SP4.3** Os dois lados DEVEM apagar `w`, `x`/`y`, `K`, `Ka`, `Ke`,
  `Kp` e o SAS da memória ao fim do pareamento (zeroização), guardando só
  `spki_*`, nomes e `fingerprint` (§5.1).
- **SP4.4** Prazos: PM1 em até 10 s após `linked`; PM2/PM3/PM4 em até 5 s
  cada; `pair.confirm` em 60 s (R10.38). Fora do prazo: `bridge_down` no
  celular e `confirm_timeout`/`cancelled` conforme o caso.
- **SP4.5** Pontos recebidos DEVEM ser validados (na curva, não
  identidade) antes do uso; ponto inválido = falha silenciosa como
  `wrong_code`.

### 4.3 Código de confirmação (SAS) de 6 dígitos

```
sas_bytes = HKDF-SHA-256(IKM = Ke, salt = vazio,
              info = "trcp-sas-v1" ‖ SHA-256(spki_tls ‖ spki_stepup ‖ spki_agent),
              L = 8)
sas = (u64_be(sas_bytes) mod 1_000_000), com zeros à esquerda, 6 dígitos
```

- **SP4.6** O agente e o celular calculam o SAS independentemente depois
  de PM3/PM4. O agente o mostra no modal (`pair.claimed.sas`, R10.38); o
  celular o mostra na tela de espera (fluxo aprovado X3/X4). A pessoa
  compara e confirma no PC.
- Para que serve, já que o SPAKE2 autentica: contra **A9** (código
  visto). Quem viu os 12 dígitos e reivindica antes do celular legítimo
  completa o SPAKE2 com sucesso; o SAS na tela do PC será então o do
  intruso, e o celular legítimo (que recebeu `claimed` da ponte e não
  tem SAS, ou que completou outra corrida) não o exibe igual: a pessoa
  recusa. O `device_name` no modal ajuda, mas é escolhido pelo intruso;
  o SAS não. Refinamento sobre a proposta das interfaces
  (`HKDF(K, "trcp-sas-v1") mod 10^6`): deriva de `Ke` (chave de sessão da
  RFC, não do ponto bruto) e compromete as chaves públicas trocadas, para
  que o SAS também prove que as chaves fixadas são as do aparelho na mão.
- Viés: `2^64 mod 10^6` é desprezível (< 10^-13 por dígito).

### 4.4 Implementação: decisão sobre a crate (SD-1)

Fatos verificados em 2026-09-27:

- **[FATO]** `spake2` 0.4.0 (RustCrypto/PAKEs): "Only `Ed25519Group` is
  implemented", compatível com o python-spake2, e "This crate has never
  received an independent third party audit for security and
  correctness. USE AT YOUR OWN RISK!"
  (https://docs.rs/spake2/latest/spake2/;
  https://github.com/RustCrypto/PAKEs). Não há grupo P-256 nem menção à
  RFC 9382; o transcrito do python-spake2 não é o da RFC.
- **[FATO]** `p256` (RustCrypto/elliptic-curves): "The elliptic curve
  arithmetic contained in this crate has never been independently
  audited!" (https://github.com/RustCrypto/elliptic-curves).
- **[FATO]** CPace (alternativa balanceada mais recente) está em
  `draft-irtf-cfrg-cpace-21`, "Sent to the RFC Editor", sem número de
  RFC (https://datatracker.ietf.org/doc/draft-irtf-cfrg-cpace/). Sem
  crate auditada.
- **[FATO]** o `rustls` recomenda o provedor `rustls-aws-lc-rs`
  (https://github.com/rustls/rustls/blob/main/README.md);
  **[INFERÊNCIA]** o `aws-lc-rs` não expõe aritmética de pontos genérica
  (soma e multiplicação por escalar de pontos arbitrários), que o SPAKE2
  exige; confirmar em M0.

**Decisão SD-1:** módulo próprio `trc-pake` (~150 linhas) implementando
exatamente §4.1 sobre `p256` (`arithmetic`), `sha2`, `hkdf`, `hmac`,
`argon2`, `chacha20poly1305`. Motivos: (a) nenhuma opção é auditada; entre
as não auditadas, a que segue a RFC tem vetores publicados e transcrito
com identidades; (b) P-256 é a mesma curva do TLS e do Keystore, um só
conjunto de primitivas; (c) o Android calcula o mesmo perfil com
`java.security`/BouncyCastle sem depender de porte do python-spake2.
Mitigações obrigatórias: (1) vetores do Apêndice B da RFC como fixtures
que **falham a build**; (2) testes negativos (ponto fora da curva,
identidade, `cA` errado, `w` errado, transcrito com identidade trocada);
(3) fuzz dos decodificadores PM1–PM5; (4) revisão Fable max do módulo e
dos testes **antes** de M6 continuar (proposta §8); (5) reavaliar em cada
release se surgiu implementação auditada (RFC 9382 ou CPace publicado) e
trocar por trás da mesma interface `Pake`. Riscos residuais: canal
lateral de tempo nas primitivas do `p256` (o segredo vive 5 min e uma
única execução; aceito).

### 4.5 Entropia, tentativas e corrida

- `secret8`: 10^8 ≈ 2^26,6. Só ataque **online**, uma tentativa SPAKE2
  por código (R10.39, `wrong_code` invalida). A2 tem duas tentativas por
  código (uma contra cada lado, §3.4 TB-3): 2 × 10^-8. Códigos duram 5
  min e a pessoa gera outro depois de cada falha: em uso normal, a
  chance acumulada é desprezível; um atacante que force falhas
  repetidas é visível (a extensão mostra `wrong_code`, e o agente pausa
  o pareamento após 3 falhas em 10 min, `bridge.md` B4.8).
- SAS: 10^6. Contra A9 na corrida, o intruso não escolhe o SAS (depende
  de `Ke` e das chaves), então a chance de coincidir com o do celular
  legítimo é 10^-6; e a pessoa ainda vê o nome do aparelho.
- Griefing: reivindicar o número antes do celular legítimo (sem saber
  `secret8`) apenas faz o pareamento falhar; residual aceito
  (`bridge.md` B4.7–B4.8).
- Ponte hostil que sabe `code4` (sempre sabe) mas não `secret8`: TB-3.

### 4.6 Validação de `device_name` e `agent_name`

- **SP4.7** Ao receber `payload_A`, o agente DEVE: normalizar Unicode
  (NFC), remover caracteres de controle e de formatação (categorias `Cc`,
  `Cf`), colapsar espaços, aparar as pontas, cortar em **40** caracteres
  (spec §14) e exigir pelo menos 1 caractere visível; nome vazio depois
  disso vira `"Celular"`. O mesmo vale para `agent_name` no celular (63).
  O texto nunca é interpretado (sem Markdown, sem links).

### 4.7 QR e endereço da ponte

- `pipa://pair?c=482191372055&b=ponte.gariolilabs.com&v=1` (exigências
  P5): `c` = 12 dígitos; `b` = host[:porta] da ponte; `v` = 1. O app
  valida a ponte só pelo WebPKI (`bridge.md` B2.2) e mostra `b` no campo
  Servidor (AJ-02/AJ-03). O código digitado não carrega `b`; a pessoa
  informa o servidor. Nenhum segredo além de `c`, que já está na tela.
- **SP4.8** O app DEVE tratar `v` desconhecido como "atualize o app" e
  recusar `b` com esquema, caminho ou credenciais embutidas.

## 5. Sessão: TLS 1.3 mútuo com chaves fixadas

### 5.1 Certificados e fixação

- **SP5.1** Cada lado tem um certificado X.509 **autoassinado** sobre uma
  chave EC P-256 (ECDSA com SHA-256), gerado uma vez: o agente na
  instalação (`rcgen`), o celular no primeiro uso (chave `K_tls` do
  Keystore, certificado autoassinado gerado pelo app). Validade nominal
  de 100 anos; **as datas são ignoradas** pelos verificadores. `CN` fixo
  (`pipa-agent`, `pipa-phone`), sem SAN significativo.
- **SP5.2** `fingerprint` = `SHA-256(SubjectPublicKeyInfo em DER)`,
  exibido em base64url sem padding quando aparece em tela. É o que o
  celular guarda por PC (`{agent_id, agent_name, bridge, fingerprint}`,
  ADR-0012) e o que o agente guarda por aparelho (registro §6.3 da spec).
- **SP5.3** Verificação = **igualdade exata** do fingerprint do
  certificado apresentado com o fixado. Sem cadeia (intermediários
  presentes = falha), sem OCSP/CRL, sem nome de host, sem datas, sem
  restrições de uso. Por que X.509 e não chave pública crua (RFC 7250):
  **[FATO]** o `rustls` suporta "RFC7250 raw public keys for TLS1.3"
  (https://docs.rs/rustls/latest/rustls/manual/_04_features/index.html),
  mas **[INFERÊNCIA]** o Conscrypt/Android não; confirmar em M0. Se M0
  confirmar suporte nos dois lados, trocar para RPK é mudança local.
- **SP5.4** Rotação de `K_agent` ou `K_tls` no MVP = parear de novo. Um
  comando `agent.rekey`/`device.rekey` assinado pela chave antiga é
  evolução atrás de capacidade (fora do MVP).

### 5.2 Parâmetros

| Item | Valor | Fonte / motivo |
|---|---|---|
| Versão | **só TLS 1.3** nos dois lados (RFC 8446). **[FATO]** "In Android 10 and higher, TLS 1.3 is enabled by default for all TLS connections" (https://developer.android.com/about/versions/10/behavior-changes-all) | elimina rebaixamento; exige `minSdk` ≥ 29 (DS-5 pede 30) |
| Papéis TLS | agente = servidor; celular = cliente | espelha o Upgrade (o agente aceita `/trcp`) |
| Autenticação | mútua e **obrigatória**: o servidor exige certificado do cliente | R3.2 |
| Suítes | as três do TLS 1.3 (`AES_128_GCM_SHA256`, `AES_256_GCM_SHA384`, `CHACHA20_POLY1305_SHA256`); **[FATO]** no Android "The TLS 1.3 cipher suites cannot be customized" (mesma página) | — |
| Grupos | X25519 preferido, `secp256r1` aceito | ambos comuns; medir em M0 |
| Assinatura | `ecdsa_secp256r1_sha256` apenas | as chaves são P-256 |
| SNI | não enviado; se a pilha exigir um nome, `agent.pipa.invalid` (TLD reservado, RFC 6761), ignorado pelo verificador | a ponte não vê nomes |
| ALPN | `trcp/1` | detecta cliente errado cedo |
| Resumo de sessão | **desligado** nos dois lados (sem tickets, sem cache): `rustls` com `send_tls13_tickets = 0`; Android `Conscrypt.setUseSessionTickets(engine, false)` (**[FATO]** o método existe, https://github.com/google/conscrypt/blob/master/common/src/main/java/org/conscrypt/Conscrypt.java) | um handshake completo por conexão é barato (§5.7) e evita estado ligado a chaves |
| 0-RTT | nunca. **[FATO]** "0-RTT mode isn't supported" no Android 10 (página acima); `rustls` `max_early_data_size` = 0 | — |
| Autenticação pós-handshake, renegociação | não usadas (o `rustls` não implementa renegociação, **[FATO]** lista de não-recursos) | — |
| Compressão | inexistente no TLS 1.3; proibida no WebSocket (R3.9; ponte B2.7) | — |
| Registro | ≤ 2^14 bytes de texto claro por registro (**[FATO]** RFC 8446 §5.1); um registro por frame externo de 64 KiB (ponte B2.10) | — |

### 5.3 Verificadores

**Agente (`rustls` 0.23.x; API conferida na versão 0.23.45)**

- `ServerConfig` só com `TLS13`, provedor `aws-lc-rs`,
  `with_client_cert_verifier(Arc<PinnedClientVerifier>)`,
  `with_single_cert(vec![cert_agent], key_agent)`, `alpn_protocols =
  ["trcp/1"]`, `send_tls13_tickets = 0`.
- **[FATO]** `rustls::server::danger::ClientCertVerifier` exige
  `verify_client_cert(end_entity, intermediates, now)`,
  `verify_tls12_signature`, `verify_tls13_signature`,
  `supported_verify_schemes`, `root_hint_subjects`, e oferece
  `client_auth_mandatory()` e `offer_client_auth()` (padrão `true`)
  (https://docs.rs/rustls/latest/rustls/server/danger/trait.ClientCertVerifier.html).
  Implementação: `intermediates` não vazio → erro; extrai o SPKI de
  `end_entity`; `fingerprint` no registro em estado `active` ou
  `revoked` (para 4403, §5.5) → `ClientCertVerified::assertion()`;
  senão → `CertificateError::UnknownIssuer` (o TLS falha com alerta
  genérico). `verify_tls13_signature` delega a
  `rustls::crypto::verify_tls13_signature` com os algoritmos do
  provedor; `verify_tls12_signature` devolve erro (nunca chamado com só
  TLS 1.3); `supported_verify_schemes` = `[ECDSA_NISTP256_SHA256]`;
  `root_hint_subjects` = `&[]`; `client_auth_mandatory` = `true`.
- O estado do aparelho (`active`/`revoked`/`forgotten`, corte, política)
  **não** é decidido no verificador: ele só reconhece a chave. O TRCP
  decide depois do Upgrade (§6.3 da spec), para que 4403/4410 possam ser
  enviados.

**Celular (Conscrypt/`javax.net.ssl`, dentro do túnel)**

- `SSLContext.getInstance("TLSv1.3")` com `KeyManager` que devolve
  `[cert_phone]` e a `PrivateKey` de `K_tls` do `AndroidKeyStore`, e
  `X509TrustManager` cujo `checkServerTrusted` exige cadeia de tamanho 1
  e `SHA-256(SPKI) == fingerprint` do PC; `checkClientTrusted` lança
  sempre; `getAcceptedIssuers` vazio. `SSLEngine` em modo cliente,
  `setEnabledProtocols(["TLSv1.3"])`, sem
  `endpointIdentificationAlgorithm`, ALPN `trcp/1`, tickets desligados.
- **[INFERÊNCIA]** assinar o `CertificateVerify` com chave do
  `AndroidKeyStore` via `KeyManager` funciona no Conscrypt do sistema;
  omitir SNI exige `SSLParameters.setServerNames(emptyList())`; e a pilha
  "TLS sobre frames binários de WebSocket" exige dirigir o `SSLEngine` à
  mão (spec §19.2 item 17). Os três são itens do spike M0.

### 5.4 Autenticação da sessão: só TLS mútuo (SD-2)

Fecha o ponto em aberto 2 do `adr/README.md` e R5.7/§19.2 item 11.

- **[FATO]** no TLS 1.3 o `CertificateVerify` do cliente é "A signature
  over the entire handshake using the private key corresponding to the
  public key in the Certificate message" (RFC 8446 §4.4.3): a prova de
  posse de `K_tls` já está ligada a **este** handshake, com **este**
  servidor (cujo certificado está no transcrito). Um `auth{sig}` sobre
  `nonce ‖ tls_exporter` provaria a mesma posse da mesma chave, no mesmo
  canal: redundante.
- **[FATO]** o `tls-exporter` da RFC 9266 usa o rótulo
  `EXPORTER-Channel-Binding`, contexto vazio e 32 bytes, e "is always
  true for TLS 1.3" (https://www.rfc-editor.org/rfc/rfc9266.html); está
  disponível nos dois lados (`rustls`
  `ConnectionCommon::export_keying_material(output, label, context)`,
  https://docs.rs/rustls/latest/rustls/struct.ConnectionCommon.html;
  Conscrypt `exportKeyingMaterial(engine, label, context, length)`).
- **Decisão SD-2:** rev 0 autentica **só pelo TLS mútuo**. `auth.p` é
  `{}` nos dois perfis; `hello.nonce` sai; um futuro `proof` (por exemplo,
  para ligar uma segunda chave, ou se um dia o cliente TLS for uma pilha
  sem certificado de cliente) entra atrás da capacidade `auth-proof`,
  com `sig_K_stepup("trcp-auth-v1" ‖ exporter32)`. Patch em F-03.

### 5.5 Chave revogada: completar o TLS e fechar com 4403 (SD-3)

Resolve AJ-22 e §19.2 item 10 pela opção **(a)** (D-21, R6.3): a tela
aprovada de revogado (`global.revoked_*`) depende disso, e o custo é um
handshake por tentativa.

- **SP5.5** O verificador aceita fingerprints em estado `revoked`
  enquanto o registro mínimo `{fingerprint, state, at}` existir
  (retenção: P6, proposta 90 dias). Depois do Upgrade, sem processar
  `hello`, o agente envia Close 4403 `{"code":"revoked","at":…}` e fecha.
- **SP5.6** Guardas: (1) no máximo **uma** conexão em andamento por
  fingerprint revogado; (2) no máximo **uma** tentativa por 60 s por
  fingerprint revogado (a spec §13.5 já manda o app **nunca** reconectar
  após 4403; tentativas além disso são app adulterado ou bug); (3) acima
  de 10 tentativas por hora, o agente passa a recusar **no TLS** por 1 h
  (o app hostil deixa de ver a tela, o que não importa); (4) nada além
  do Upgrade e do Close: sem `hello`, sem `limits`, sem log de tela; (5)
  o audit registra a tentativa uma vez por hora, não uma por tentativa.
- **SP5.7** `forgotten` (D-6): igual, com `{"code":"forgotten"}`; o app
  já apagou a chave, então isso só ocorre numa corrida.
- Custo: **[INFERÊNCIA]** um handshake TLS 1.3 com ECDSA P-256 custa da
  ordem de 1 ms de CPU no PC; com a guarda (2) é irrelevante.

### 5.6 Chave desconhecida

- **SP5.8** Fingerprint fora do registro → o handshake falha antes do
  Upgrade, com alerta TLS genérico. O celular vê "não foi possível
  conectar" (tela de reconexão) e nada mais: um app com chave nova não
  distingue "PC desconhece" de "rede caiu". É o comportamento desejado
  (spec §6.1).

### 5.7 Custo em viagens (PA-11)

Depois de `linked`: 1 RTT do handshake TLS 1.3 (sem 0-RTT, por decisão)
+ 1 RTT do Upgrade + `hello`/`auth` (a spec pode encadear `hello` e
`auth` na mesma viagem, o que já faz). Juntar o Upgrade ao primeiro voo
TLS não é possível sem 0-RTT, e 0-RTT não vale o risco de repetição.
Fica registrado: a ponte não acrescenta viagem; o restante é do TRCP.

## 6. Chaves do celular

### 6.1 Duas chaves (SD-4)

Fecha o ponto em aberto 1 do `adr/README.md` e §19.2 item 13.

| Chave | Uso | Autenticação de usuário | Invalidação |
|---|---|---|---|
| `K_tls` | certificado de cliente do TLS mútuo (toda conexão) | **não** (Q10: nada de biometria ao abrir o app) | só ao remover o PC (F6), desinstalar ou restaurar o aparelho |
| `K_stepup` | assinar step-up (§8) | **sim, a cada uso**, `BIOMETRIC_STRONG \| DEVICE_CREDENTIAL` (decisão 3) | pelo Keystore (§6.3) |

Motivo: uma chave só teria de escolher entre pedir biometria a cada
conexão (contra Q10) ou não pedir nunca (sem step-up). Duas chaves dão
cada garantia a quem precisa dela. As duas nascem no primeiro uso do
app, e as duas chaves públicas vão ao agente dentro do SPAKE2
(`payload_A`, §4.2), ligadas ao mesmo `device_id`.

### 6.2 Parâmetros do Keystore

Fonte dos parâmetros: Javadoc de `KeyGenParameterSpec.Builder`
(https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec.Builder,
texto conferido no fonte AOSP) e o guia do Keystore
(https://developer.android.com/privacy-and-security/keystore).

| Parâmetro | `K_tls` | `K_stepup` |
|---|---|---|
| Algoritmo | EC P-256 (`KEY_ALGORITHM_EC`, `secp256r1`), `PURPOSE_SIGN`, digest `SHA-256` | idem |
| `setIsStrongBoxBacked(true)` | sim; em `StrongBoxUnavailableException`, refaz sem StrongBox (TEE). **[FATO]** StrongBox suporta "ECDSA, ECDH P-256" (guia do Keystore) | idem |
| `setUserAuthenticationRequired` | `false` | `true` |
| `setUserAuthenticationParameters(timeout, type)` | — | `(0, AUTH_BIOMETRIC_STRONG \| AUTH_DEVICE_CREDENTIAL)`. **[FATO]** `timeout` "0 if user authentication must take place for every use of the key" |
| `setInvalidatedByBiometricEnrollment` | — | `true` (padrão), **sem efeito** enquanto `AUTH_DEVICE_CREDENTIAL` estiver presente (§6.3) |
| `setUnlockedDeviceRequired` | `false` (o app só roda desbloqueado; **[FATO]** a Javadoc traz avisos de defeitos até o Android 14) | `false` |
| Atestado | opcional, fora do MVP (o agente não valida atestado; **[FATO]** existe e prova "Your key is in hardware that Google believes to be secure", https://developer.android.com/privacy-and-security/security-key-attestation) | idem |

- **SP6.1** Uso de `K_stepup`: `BiometricPrompt.authenticate(promptInfo,
  CryptoObject(signature))` com
  `setAllowedAuthenticators(BIOMETRIC_STRONG | DEVICE_CREDENTIAL)`, sem
  `setNegativeButtonText` (**[FATO]** "incompatible with device
  credential authentication and must NOT be set"), e
  `setConfirmationRequired(true)` (padrão) para biometria passiva. A
  assinatura é iniciada antes do prompt e concluída no
  `onAuthenticationSucceeded` com o `CryptoObject` devolvido.
- **[FATO]** "Crypto-based authentication is not supported for device
  credential prior to API 30" e "`BIOMETRIC_STRONG | DEVICE_CREDENTIAL`
  is unsupported on API 28-29" (Javadoc do `androidx.biometric`,
  https://github.com/androidx/androidx/blob/androidx-main/biometric/biometric/src/main/java/androidx/biometric/BiometricPrompt.java).
  Daí DS-5 (`minSdk` = 30).
- **[FATO]** "Key material never enters the application process" e, com
  hardware seguro, "its key material is never exposed outside of secure
  hardware" (guia do Keystore): nem o app lê `K_tls`/`K_stepup`.

### 6.3 Efeito de aceitar `DEVICE_CREDENTIAL` sobre T1

**[FATO]** Javadoc de `setUserAuthenticationRequired`: a chave "is also
irreversibly invalidated once a new biometric is enrolled or once no
more biometrics are enrolled, unless `setInvalidatedByBiometricEnrollment
(boolean)` is used to allow validity after enrollment, **or
`KeyProperties.AUTH_DEVICE_CREDENTIAL` is specified**"; e "keys that are
valid for biometric authentication only are irreversibly invalidated
when a new biometric is enrolled".

Consequências:

1. Com a decisão 3 (PIN ou padrão valem), `K_stepup` **não** é
   invalidada por biometria nova. A proteção contra T1 que o ADR-0003
   atribuía a `setInvalidatedByBiometricEnrollment` **não existe nesse
   modo**; e não faria diferença: quem sabe o PIN não precisa cadastrar
   biometria.
2. Residual de T1 = "quem sabe o PIN/padrão do celular e o tem em mãos
   libera escrita nos PCs pareados". Mitigações que valem: o PC mostra e
   nomeia o aparelho no controle (`vsc.term_name_armed`), o audit
   registra, o prazo de escrita é curto (1/5/15 min), revogação e corte
   no PC. Textos: `pair.success_body`, `vsc.allow_detail` e o botão
   "Liberar com biometria" devem dizer "biometria ou PIN" (ajuste já
   pendente em `adr/README.md` "PIN vale para liberar escrita").
3. Opção para quem quiser mais: um ajuste no app, "Só biometria", que
   recria `K_stepup` com `AUTH_BIOMETRIC_STRONG` apenas e
   `setInvalidatedByBiometricEnrollment(true)`; aí T1 volta a ser
   coberto e o PIN deixa de valer para aquele celular. Padrão
   desligado, por ser a decisão 3. **DS-4** (§17).
4. Invalidação que **sempre** vale, nos dois modos: **[FATO]** "once the
   secure lock screen is disabled (reconfigured to None, Swipe or other
   mode which does not authenticate the user) or when the secure lock
   screen is forcibly reset". Cobre o ataque "desliga o bloqueio e usa":
   sem bloqueio, `K_stepup` morre.

### 6.4 Recuperação quando `K_stepup` é invalidada (SD-5)

Fecha o item do `adr/README.md` "fluxo quando
`setInvalidatedByBiometricEnrollment` invalida a chave" (ADR-0003).

- Sintoma: `KeyPermanentlyInvalidatedException` ao iniciar a assinatura.
  `K_tls` continua válida: o app segue lendo.
- **MVP:** o app mostra "Confirme este celular de novo no computador" e
  leva ao fluxo de adicionar computador; o pareamento novo substitui as
  duas chaves no agente (mesmo `device_id` se `fingerprint` de `K_tls`
  coincidir, senão aparelho novo). Custa 12 dígitos; acontece raramente
  (bloqueio de tela removido ou redefinido; ou "Só biometria" com
  biometria nova).
- **Pós-MVP:** `device.rekey_stepup{spki_stepup}` pela sessão TLS
  (autenticada por `K_tls`), com aprovação no PC ("Pixel 8 trocou a
  chave de biometria. Permitir?"). Fica atrás de capacidade; não muda a
  rev 0.
- Recomendação a Sr. Garioli: aceitar o MVP assim (**DS-6**).

### 6.5 `minSdk` (DS-5)

Recomendação: **30** (Android 11). Motivos verificados: `CryptoObject` com
`DEVICE_CREDENTIAL` só a partir de 30 (§6.2); TLS 1.3 padrão desde 29;
`setUserAuthenticationParameters` é da API 30 (Javadoc citada). Abaixo
de 30 seria preciso um modo degradado (só biometria) por versão, que
duplica testes de segurança. PA-9 de `requisitos-nao-funcionais.md`
pedia o número; a decisão de mercado é de Sr. Garioli (§17).

### 6.6 Backup, transferência e root

- **[INFERÊNCIA]** chaves do Keystore não entram em backup nem migram
  para outro aparelho (o material não sai do hardware, §6.2); após
  restaurar ou trocar de celular, o app não encontra as chaves e
  orienta a parear de novo. Os dados de pareamento (nomes, `bridge`,
  `fingerprint`) podem ser excluídos do backup do app
  (`android:allowBackup="false"` ou regras de exclusão) para não deixar
  um app restaurado "meio pareado". Definir em M7.
- Root/bootloader destravado: fora do escopo; nenhuma detecção de root
  no MVP (falsos positivos e falsa sensação).

## 7. Chave e segredos do PC

- **SP7.1** `K_agent` (PKCS#8 DER, ~140 bytes), a chave de inscrição da
  ponte (67 caracteres) e nada mais ficam no **Gerenciador de
  Credenciais do Windows** como credenciais genéricas, via `keyring`
  (v4.2.0) com o store `windows-native-keyring-store`, persistência
  **Local** (não Enterprise). **[FATO]** o store oferece "Session",
  "Local" e "Enterprise", com Enterprise por padrão
  (https://docs.rs/windows-native-keyring-store/latest/windows_native_keyring_store/);
  **[FATO]** `CredentialBlobSize` "cannot be larger than
  `CRED_MAX_CREDENTIAL_BLOB_SIZE` (5*512) bytes" e `CRED_PERSIST_ENTERPRISE`
  é visível "to logon sessions for this user on other computers"
  (https://learn.microsoft.com/windows/win32/api/wincred/ns-wincred-credentialw).
  Local evita que a chave do PC viaje com perfil móvel.
- **SP7.2** Se a extensão ou o agente precisarem cifrar algo fora do
  Gerenciador (por exemplo, o cookie do perfil local, §10), usam DPAPI
  com `CryptProtectData` **sem** `CRYPTPROTECT_LOCAL_MACHINE` (**[FATO]**
  com essa flag "Any user on the computer ... can ... decrypt the data",
  https://learn.microsoft.com/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata)
  e com `CRYPTPROTECT_UI_FORBIDDEN`. **[FATO]** "a user with a roaming
  profile can decrypt the data from another computer": aceitável (mesmo
  usuário).
- **SP7.3** O registro de aparelhos, a política, o audit e o Event Log
  ficam em SQLite na pasta de dados do usuário (`%LOCALAPPDATA%\Pipa\`),
  com a DACL padrão do perfil. Não são segredos; a integridade contra
  A5 está fora do escopo.
- **SP7.4** Tokens de push ficam no mesmo SQLite; são quase-segredos:
  nunca em log; apagados por R10.45; entregues à ponte só no momento do
  push (`bridge.md` B8.3).
- **SP7.5** Pós-MVP: chave do agente em CNG/TPM (`NCryptCreatePersistedKey`
  com o provedor de plataforma), não exportável; exige que o `rustls`
  assine por `SigningKey` própria. Spike, não MVP.
- **SP7.6** O agente NÃO DEVE gravar segredos em `settings.json`,
  variáveis de ambiente persistentes, registro do Windows ou logs; a
  extensão NÃO DEVE persistir a chave de inscrição (`bridge.md` B3.3).

## 8. Step-up: formato exato

Fecha R6.13 ("canonização, hash e algoritmo") e §19.2 item 12; atende E6
e E9.

```
purpose  ∈ {"arm", "respond", "terminate"}
f(x)     = len(x) como u16 big-endian ‖ UTF-8(x)
canon    = f(purpose) ‖ f(s) ‖ f(c1) [‖ f(c2)]
   arm       : c1 = minutes (decimal ASCII, ex.: "5")
   respond   : c1 = attention_id ; c2 = option_id
   terminate : c1 = signal (ex.: "int")
msg      = "trcp-stepup-v1" ‖ nonce_bytes(32) ‖ SHA-256(canon)
sig      = ECDSA(K_stepup, P-256, SHA-256) sobre msg, codificada em DER
step_up  = {"nonce": <base64url do nonce>, "sig": <base64url do DER, sem padding>}
```

- **SP8.1** `nonce_bytes` são os 32 bytes decodificados de
  `step_up.challenge.nonce`. O agente refaz `msg` a partir do comando
  recebido (não confia em nada assinado além do que o comando traz) e
  verifica com o `spki_stepup` do aparelho. Falha, nonce vencido, já
  usado, de outra conexão, de outro `purpose` ou de outro `s` →
  `step_up_invalid` (R6.15).
- **SP8.2** `purpose` entra como **primeiro campo** de `canon`: assim a
  mesma assinatura não serve para outro fim mesmo se um dia o nonce for
  reaproveitado por defeito. Isso respeita a forma de R6.13
  (`"trcp-stepup-v1" ‖ nonce ‖ H(campos decisivos)`); F-09 propõe o
  texto.
- **SP8.3** Assinatura DER com `r`, `s` de até 33 bytes cada (70–72
  bytes); base64url de até 96 caracteres. O agente aceita `s` alto ou
  baixo (maleabilidade não importa: o nonce é de uso único) e rejeita DER
  malformado. Verificação com o mesmo provedor criptográfico do TLS.
- **SP8.4** O celular assina **depois** de mostrar à pessoa o que está
  assinando: "Liberar escrita em <sessão> por <n> min", "Permitir/Recusar
  <pedido>", "Encerrar <sessão>". O texto vem da tela aprovada; o
  `CryptoObject` garante que a assinatura só existe após a autenticação.
- **SP8.5** `requires_step_up` (E9) é calculado pelo agente: `true` para
  `grant.arm`, `session.terminate`, e para `attention.respond` quando o
  pedido tem `destructive: true` e a opção escolhida tem `role: allow`
  (recusar nunca exige step-up). Projetado por aparelho (R8.6).
- **SP8.6** Vetores de teste (M3): um por `purpose`, com chave fixa,
  nonce fixo e `sig` esperada verificável; mais um negativo por regra de
  R6.15.
- Regra de `destructive` (item 33, M5) — quem marca é o **adaptador no
  PC**, nunca o celular:

| Fonte do pedido | `destructive` |
|---|---|
| Hook `PermissionRequest` com ferramenta `Bash`, `Write`, `Edit`, `MultiEdit`, `NotebookEdit`, qualquer `mcp__*` ou nome desconhecido | `true` |
| Hook `PermissionRequest` com `Read`, `Glob`, `Grep`, `WebSearch`, `WebFetch` | `false` |
| `Notification` de `permission_prompt` sem detalhe da ferramenta | `true` |
| `question`, `idle`, `finished`, `error` sem opção `allow` | `false` |
| Qualquer pedido com `source: "heuristic"` | `true` |
| `subject.truncated` **ou `subject.redacted`** (PA7) | `true` (F-02) |

## 9. Revogação, esquecimento e corte

| Evento | Quem | Efeito no agente | O que o celular vê | A ponte |
|---|---|---|---|---|
| `device.revoke` (I6) | dono do PC | R6.2: fecha 4403 `revoked`, retira escritas, invalida nonces, apaga token de push, audit; registro vira `revoked` com `at` | `global.revoked_*`; nunca reconecta; ao tentar, TLS completa e recebe 4403 (SD-3) | não sabe |
| `device.forget` (E18) | o próprio celular | idem com `forgotten`; o app apaga `K_tls`, `K_stepup` e os dados do PC | tela de removido | não sabe |
| `remote.cut` (I7) | dono do PC | R6.21: estado `cut` em disco, 4410 a todos, retira escritas, cancela pareamento; **o agente continua registrado na ponte** para poder entregar 4410 | `global.cut_*`; tenta a cada 60 s | não sabe (§19.2 item 14 fechado: desnecessário) |
| `remote.restore` | dono do PC | volta a `on` | reconecta sozinho | — |
| Revogação da chave de inscrição | operador da ponte | agente perde a ponte (`enroll_revoked`), avisa a extensão | "PC offline" | executa (`bridge.md` B3.6) |

- **SP9.1** 4410 durante o corte segue as mesmas guardas de SD-3 (uma
  tentativa por aparelho por 60 s; o app já se limita a isso, §13.5).
  F-11 propõe o texto.
- **SP9.2** Revogar **não** é cortar: cortar preserva os pareamentos;
  revogar apaga um. "Revogar todos" não existe como comando; é cortar e
  revogar um a um (telas aprovadas).
- **SP9.3** Ao revogar, o agente também descarta assinaturas de tela,
  janela de frames e resultados de `cmd.status` daquele aparelho.

## 10. Perfil local: pipe, squatting e EX1

### 10.1 Nome e criação

- **SP10.1** Nome: `\\.\pipe\pipa-trcd-<SID do usuário em texto>` (por
  exemplo `\\.\pipe\pipa-trcd-S-1-5-21-…-1001`). **[FATO]** o nome pode
  ter até 256 caracteres (https://learn.microsoft.com/windows/win32/api/namedpipeapi/nf-namedpipeapi-createnamedpipew).
  O SID no nome evita colisão entre usuários; **não** é proteção.
- **SP10.2** Criação: `CreateNamedPipeW(nome, PIPE_ACCESS_DUPLEX |
  FILE_FLAG_OVERLAPPED | FILE_FLAG_FIRST_PIPE_INSTANCE, PIPE_TYPE_BYTE |
  PIPE_READMODE_BYTE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS,
  PIPE_UNLIMITED_INSTANCES, 64 KiB, 64 KiB, 0, &sa)` na **primeira**
  instância; as demais sem `FILE_FLAG_FIRST_PIPE_INSTANCE`. **[FATO]**
  com essa flag "creation of the first instance succeeds, but creation
  of the next instance fails with ERROR_ACCESS_DENIED" (mesma página).
  Se a primeira criação falhar com `ERROR_ACCESS_DENIED`, **outro
  processo já tem o nome**: o agente NÃO DEVE usar outro nome; registra
  o evento, avisa a extensão (`vsc.local_pipe_taken`, texto novo, P7) e
  tenta de novo a cada 10 s.
- **SP10.3** DACL explícita (sem herança): `ALLOW <SID do usuário>
  FILE_GENERIC_READ | FILE_GENERIC_WRITE | SYNCHRONIZE`; `ALLOW SYSTEM
  GENERIC_ALL`; nenhuma ACE para Everyone, Anonymous, Users ou
  Administrators. **[FATO]** a DACL padrão daria "read access to members
  of the Everyone group and the anonymous account" (mesma página), por
  isso é obrigatória a explícita. **[FATO]** `FILE_GENERIC_WRITE`
  inclui `FILE_CREATE_PIPE_INSTANCE` (https://learn.microsoft.com/windows/win32/ipc/named-pipe-security-and-access-rights):
  como o agente e os clientes são o mesmo usuário, não dá para negar a
  criação de instâncias aos clientes sem negá-la ao agente; um processo
  do mesmo usuário criar instâncias é A5, fora do escopo.
- **SP10.4** `PIPE_REJECT_REMOTE_CLIENTS` (R3.5) e o SID de logon
  (**[FATO]** "To prevent remote users or users on a different terminal
  services session from accessing a named pipe, use the logon SID on
  the DACL", mesma página): o MVP usa o SID do usuário; restringir à
  sessão de logon (SID de logon) é endurecimento opcional que impediria
  usar o mesmo agente de outra sessão RDP do mesmo usuário; fica fora.

### 10.2 Cliente: quem é o servidor?

- **[FATO]** `GetNamedPipeServerProcessId` exige "This handle must be
  created by the CreateNamedPipe function"
  (https://learn.microsoft.com/windows/win32/api/winbase/nf-winbase-getnamedpipeserverprocessid):
  a documentação **não** dá ao cliente um meio de identificar o servidor
  pelo handle. Por isso a prova é na aplicação.
- **SP10.5 Prova do servidor por cookie.** Ao iniciar, o agente grava 32
  bytes aleatórios em `%LOCALAPPDATA%\Pipa\trcd\local.cookie` (arquivo
  criado com DACL só do usuário e SYSTEM, sobrescrito a cada início). O
  cliente lê o cookie (mesmo usuário lê; A4 não) e, no `hello` do
  perfil local, envia `p.nonce` (32 bytes, base64url); o agente responde
  no seu `hello` com `p.local_proof = base64url(HMAC-SHA-256(cookie,
  "trcp-local-v1" ‖ nonce))`. O cliente verifica antes do `auth`;
  prova ausente ou errada → o cliente fecha com 4401 e mostra
  `vsc.local_pipe_untrusted` (texto novo, P7). Um squatter de outro
  usuário (A4) recebe só `hello` do cliente (nome e versão) e nada mais.
  Patch em F-04 (altera §3.2, R5.8 e o `hello` local).
- **SP10.6 Nível de personificação.** **[FATO]** o cliente controla a
  personificação por `SECURITY_SQOS_PRESENT` em `CreateFile`, e
  "SECURITY_IMPERSONATION ... is the default behavior if no other flags
  are specified along with the SECURITY_SQOS_PRESENT flag"
  (https://learn.microsoft.com/windows/win32/api/fileapi/nf-fileapi-createfilew);
  "The SecurityImpersonation level is the default for named pipe, RPC,
  and DDE servers" (https://learn.microsoft.com/windows/win32/secauthz/impersonation-levels).
  O `trc` (CLI Rust) abre o pipe com `SECURITY_SQOS_PRESENT |
  SECURITY_IDENTIFICATION`: um servidor falso pode no máximo identificar
  o chamador. **[INFERÊNCIA]** o `net.connect` do Node não expõe essas
  flags; se o libuv abrir sem SQOS, a extensão NÃO DEVE conectar
  diretamente e usa `trc proxy` (stdio ↔ pipe) ou um addon nativo
  mínimo. Item do spike M0/M4, junto com o item de §3.2 da spec
  (WebSocket sobre pipe no Node).
- **SP10.7** O servidor identifica o cliente pela DACL (só o usuário
  entra) e, para EX1, pelo processo: `GetNamedPipeClientProcessId(hPipe)`
  (**[FATO]** handle "must be created by the CreateNamedPipe function",
  https://learn.microsoft.com/windows/win32/api/winbase/nf-winbase-getnamedpipeclientprocessid,
  que é o caso do servidor) → `OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)`
  → `QueryFullProcessImageNameW` = caminho do executável. Enquanto o
  cliente mantém o handle, o PID não é reutilizado.

### 10.3 Chamadores locais (EX1): autenticação e origem (AJ-32 → (a))

Fecha a linha "Autenticação de quem chama" de `exigencias-externas.md`
EX1, PA14 de `privacy.md`, PA-12 de `requisitos-nao-funcionais.md` e o
`origin` de `privacy.md` §6.3.

- **SP10.8** Autenticação de camada OS: só processos **do usuário**
  entram (DACL). Isso é o que EX1 pede contra "nenhum processo qualquer";
  o que sobra (A5) está fora do escopo.
- **SP10.9** Identidade de origem: `{origin, exe_path}`, com `origin` o
  nome curto que o chamador declara (≤ 32 caracteres, privacy §6.3) e
  `exe_path` o caminho obtido em SP10.7. A primeira chamada de um par
  `{origin, exe_path}` novo abre a notificação `vsc.notice_origin_ask`
  ("{origem} quer mandar avisos para os seus celulares. Permitir?") com
  Permitir/Recusar, e o nó "Origens de aviso" na árvore com Remover
  (AJ-32 opção (a)). Enquanto não aprovado: `forbidden`, no máximo um
  prompt por origem a cada 10 min. Recusado: silêncio por 24 h, sem
  prompt.
- **SP10.10** O agente preenche `origin` nos avisos a partir da lista
  aprovada, nunca do texto do chamador (privacy §6.3). Limites por
  origem (NFR-60) contam por par aprovado; chamadores não aprovados só
  encontram o limite global (PA-12).
- **SP10.11** `trc hook` (§11) é origem pré-aprovada na instalação
  (`origin` = `claude-code`, `exe_path` = o `trc.exe` instalado), pois
  quem instalou a Pipa pediu exatamente isso.
- Dado novo no PC: a lista de origens `{origin, exe_path, first_seen,
  state}` entra em `privacy.md` §3.3 (linha nova, P6).

## 11. Hook do Claude Code (ADR-0008)

### 11.1 Fatos

- **[FATO]** hooks HTTP: `{"type":"http","url":…,"headers":{…},
  "allowedEnvVars":[…],"timeout":…}`; "Only variables listed in
  `allowedEnvVars` are resolved" e a interpolação `$VAR` vale para
  **headers**; o campo `url` **não** interpola variáveis. Hooks de
  comando recebem o JSON pela entrada padrão e respondem pela saída
  padrão. `PermissionRequest` decide com
  `{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"|"deny",…}}}`;
  "Exit code 0 with no output means the hook has no decision to report,
  so the tool call continues through the normal permission flow"
  (https://code.claude.com/docs/en/hooks).
- Hooks moram em `~/.claude/settings.json` (usuário), `.claude/settings.json`
  (projeto, versionado), `.claude/settings.local.json`, plugins e
  frontmatter (mesma página).

### 11.2 Análise do hook HTTP em `127.0.0.1:<porta>`

- Como a URL não interpola variáveis, a porta é **fixa** na
  configuração. Em Windows, qualquer usuário local pode escutar numa
  porta livre de `127.0.0.1`; quem escutar primeiro recebe os POSTs do
  Claude Code do **nosso** usuário. O corpo traz `tool_input` (comando
  `Bash` inteiro, conteúdo de `Write`, etc.) e o cabeçalho traz o token.
  Pior: em `PermissionRequest`, o ocupante responde `allow` e aprova a
  ferramenta em nosso lugar. Não há autenticação do servidor em HTTP em
  claro, e o cliente (Claude Code) não é nosso: **não existe mitigação
  do nosso lado** para PC com mais de um usuário local (A4).
- Em PC de um usuário só, o risco se reduz a A5 (fora do escopo), e o
  hook HTTP seria aceitável com: porta fixa alta reservada, token por
  sessão no header via `allowedEnvVars`, e o agente recusar iniciar o
  recurso se não conseguir a porta (aviso "porta ocupada"). Mas o agente
  não sabe distinguir "ocupada por mim de outra sessão" de "ocupada por
  A4".

### 11.3 Recomendação (DS-3): hook de comando pelo pipe

```json
{"hooks":{"PermissionRequest":[{"hooks":[{"type":"command",
  "command":"\"C:\\Program Files\\Pipa\\trc.exe\" hook","timeout":300}]}],
 "Notification":[{"hooks":[{"type":"command",
  "command":"\"C:\\Program Files\\Pipa\\trc.exe\" hook","timeout":10}]}],
 "Stop":[{"hooks":[{"type":"command",
  "command":"\"C:\\Program Files\\Pipa\\trc.exe\" hook","timeout":10}]}]}}
```

- `trc hook` lê o JSON, abre o pipe com SQOS de identificação, verifica
  o servidor (cookie, SP10.5), envia `{event, PIPA_HOOK_TOKEN}` e:
  para `Notification`/`Stop` sai com 0 sem saída; para
  `PermissionRequest` espera a decisão vinda do celular (ou do PC) até
  o `timeout` e devolve `allow`/`deny` **só** se houve decisão pelo
  celular com step-up válido quando exigido; senão sai com 0 sem saída
  (fluxo normal do Claude Code). Sem agente: sai com 0 sem saída em
  < 100 ms.
- O token por sessão continua (ADR-0008): o agente o injeta no ambiente
  do PTY que cria; `trc hook` herda o ambiente do Claude Code e o lê
  (T11/T17: um processo em **outro** terminal não tem esse token; um
  processo no mesmo terminal é A5).
- Configuração em `~/.claude/settings.json`, gravada pela extensão com
  consentimento e mostrada em texto antes; nunca em `.claude/` do
  projeto (um repositório hostil já pode instalar hooks próprios; não é
  nosso problema resolver, mas não devemos ensinar a colocar hooks em
  projeto).
- Consequência: supersede a parte "HTTP hook" do ADR-0008 (novo ADR, a
  cargo de quem mantém `docs/adr/`); mantém o adaptador, os eventos e
  a heurística rotulada. Se Sr. Garioli mantiver HTTP, o texto de
  instalação DEVE avisar "só em PC de um usuário" e o agente DEVE
  implementar os cuidados de §11.2.
- **[INFERÊNCIA]** a interação entre o diálogo de permissão no PC e a
  decisão pelo celular (quem responde primeiro) depende de como o Claude
  Code trata um hook `PermissionRequest` pendente; validar em M5.

## 12. Limites de memória e transporte no agente (PA-7)

- **SP12.1** O agente configura o `tungstenite` interno (dentro do TLS)
  com `max_message_size = 262144` (spec §14), `max_frame_size = 262144`,
  `read_buffer_size = 16 KiB`, `write_buffer_size = 0`,
  `max_write_buffer_size = 1 MiB` (o "1 MB por 30 s" de §14 vira 4429
  `slow`); e os frames **externos** para a ponte em 64 KiB
  (`bridge.md` §7.2). **[FATO]** os padrões da crate são 128 KiB /
  128 KiB / ilimitado / 64 MiB / 16 MiB
  (https://docs.rs/tungstenite/latest/tungstenite/protocol/struct.WebSocketConfig.html).
- **SP12.2** Antes de `auth.ok`, o agente aceita no máximo 16 KiB por
  mensagem e 3 mensagens (`hello`, `auth` e uma folga); o resto é 4400.
- **SP12.3** Sem compressão em nenhuma camada (R3.9, D-15 confirmada;
  ponte B2.7). F-08 registra a confirmação.
- **SP12.4** O `pty.output` e o `screen.history` já são limitados pela
  spec; o agente NÃO DEVE bufferizar mais de W janelas por assinatura
  (R9.x) nem reter frames para aparelho desconectado.

## 13. Auditoria e registros no PC

- **SP13.1** O audit (R6.25) registra: conexão e desconexão remotas,
  liberar e retirar escrita, `input.send` (**só** contagem de caracteres
  e de teclas), resposta a pedido, encerrar terminal, pareamento (início,
  `claimed`, resultado), revogação, esquecimento, corte, reativação,
  mudança de política, tentativa de aparelho revogado (uma por hora),
  origem EX1 aprovada/recusada/removida, chave de inscrição gravada
  (só `key_id`) e falha de prova do servidor local. **Nunca** o texto
  digitado: `pipa.audit.input` **não existe** (DP3 (a)). F-01 remove os
  restos da spec.
- **SP13.2** Retenção: proposta de P6 (90 dias), expurgo automático;
  `audit.list` remoto só do próprio aparelho e só metadados (R6.26);
  `activity.recent` local.
- **SP13.3** Integridade: append-only lógico no SQLite; cadeia de hash
  (cada linha com `SHA-256(linha anterior ‖ linha)`) fica para depois do
  MVP; contra A5 não há garantia de qualquer forma.
- **SP13.4** Logs de operação do agente: nível `info` sem conteúdo de
  tela, sem texto digitado, sem tokens, sem chaves, sem nomes de sessão
  (PV10); IPs não existem no agente (só a ponte os vê). `debug` só em
  laboratório e nunca por padrão em release.

## 14. Cadeia de suprimento e releases

| Controle | Ferramenta / prática | Fonte |
|---|---|---|
| Vulnerabilidades, crates não mantidas, yanked | `cargo-deny check advisories` no CI e `cargo audit` diário | **[FATO]** advisories "Checks advisory databases for crates with security vulnerabilities, or that have been marked as `Unmaintained`, or which have been yanked" (https://embarkstudios.github.io/cargo-deny/checks/index.html) |
| Licenças, duplicatas, fontes | `cargo-deny` `licenses`, `bans`, `sources` (só crates.io) | idem |
| Auditoria de código de dependências | `cargo vet` com importação das auditorias públicas (Mozilla, Google) e `exemptions` revisadas a cada release; o CI falha em crate não auditada | https://mozilla.github.io/cargo-vet/ |
| Reprodutibilidade | `Cargo.lock` versionado; `cargo build --locked`; MSRV fixa; `#![forbid(unsafe_code)]` fora dos crates de FFI (ConPTY, pipes) | — |
| Primitivas | TLS: `rustls` (**[FATO]** auditado pela Cure53 em 2020, https://jbp.io/2020/06/14/rustls-audit.html; relatório `TLS-01-report.pdf` em https://github.com/rustls/rustls/tree/main/audit) com `aws-lc-rs`; PAKE: módulo próprio sobre `p256` (SD-1, não auditado, mitigado) | — |
| SBOM | CycloneDX gerado no release e anexado | — |
| Assinatura dos binários (`trcd`, `trc`, `trc-bridge`, instalador) | `cosign sign-blob` sem chave com identidade OIDC do GitHub Actions, registro no Rekor; `SHA256SUMS` assinado; o instalador do Windows também com Authenticode quando houver certificado | **[FATO]** Fulcio emite certificados de curta duração ligados a identidade OIDC; Rekor registra (https://docs.sigstore.dev/cosign/signing/overview/) |
| Extensão VS Code | publicação pelo Marketplace; **[FATO]** "The Visual Studio Marketplace signs all extensions when they are published. VS Code verifies this signature when you install an extension" (https://code.visualstudio.com/docs/configure/extensions/extension-marketplace); publicação por identidade federada (Entra ID), não PAT | https://code.visualstudio.com/api/working-with-extensions/publishing-extension |
| APK | Play App Signing (**[FATO]** "Google manages and protects your app's signing key", https://support.google.com/googleplay/android-developer/answer/9842756); chave de upload fora do CI, em cofre; `google-services.json` não é segredo mas o projeto Firebase restringe remetentes por IAM | — |
| CI | permissões mínimas do `GITHUB_TOKEN`; ambientes protegidos para release; sem segredos de longa duração (OIDC para Sigstore e para o GCP) | — |
| Dependências Android | Gradle com `verification-metadata.xml` (checksums) | — |

## 15. Resposta a incidentes

| Cenário | Quem age | Ação | Tempo alvo |
|---|---|---|---|
| Celular perdido | dona/o do PC | revogar no PC (I6) ou cortar (I7); o app no celular perde acesso na próxima mensagem (R6.1) | minutos |
| PC comprometido (A5) | dona/o | tudo do PC está exposto por definição; reinstalar, gerar `K_agent` nova, parear de novo, trocar a chave de inscrição | — |
| Chave de inscrição vazada | operador | `key revoke` + `key new`; avisar a pessoa | minutos |
| Ponte comprometida | operador | rebuild da instância; rotação de todas as chaves de inscrição; comunicar metadados expostos (IPs, horários) aos usuários; nenhuma chave de sessão a trocar | horas |
| Credencial do FCM exposta | operador | revogar a chave da conta de serviço no GCP; pushes falsos só gastam bateria | horas |
| Vulnerabilidade no `rustls`/`p256`/`tungstenite` | equipe | `cargo audit` alerta; release de correção; a extensão avisa versão mínima (4426) | dias |
| Bug que envia conteúdo à ponte | equipe | correção urgente; comunicado; não há retenção na ponte por padrão (BR-*) | dia |
| Relato externo | equipe | `SECURITY.md` no repositório com contato e prazo de resposta (5 dias úteis) e divulgação coordenada (90 dias) | — |

## 16. Revisão da spec TRCP/1

Achados sobre `docs/spec/trcp-1.md` (revisão de segurança pedida em §17
da spec e em `adr/README.md`). Severidade: **Alta** (fere um princípio
ou uma decisão tomada), **Média** (fragiliza um controle ou deixa uma
regra de segurança aberta), **Baixa** (precisão, texto, consistência).
"Patch proposto" = texto pronto; quem mantém a spec aplica.

**F-01 — Alta — `audit_input` continua na spec, contra DP3 (a).**
Regras: §6.7/R6.17 (lista de `policy`), R6.20, R6.25, R6.26, `policy.set`
em §10.6.9, §16 (nota final e `devices.audit_note`), fixtures FX-32 e
FX-59, PV11 ("audit (90 dias proposto)" fica). Problema: `privacy.md` §14
DP3 decidiu remover `pipa.audit.input`; a spec ainda define o campo, um
comando que o liga e dois fixtures que o exercitam. Patch proposto:
- §6.7, primeira linha: `policy{write_enabled, arm_max_min,
  arm_choices_min}` (E4, I9), ligada às configurações
  `pipa.write.enabled` e `pipa.write.maxMinutes`.
- R6.20: "Toda mudança gera `policy.changed` no log." (apagar a segunda
  frase).
- R6.25: "... `input.send` (contagem de caracteres e teclas; **nunca o
  texto**), ...".
- R6.26: "... O texto digitado **nunca** sai do PC e **nunca é
  registrado** (E17; exigências §4; `privacy.md` DP3)."
- §10.6.9, linha `policy.set`: `{write_enabled?, arm_max_min?}`.
- §16, nota final: "O texto digitado nunca é registrado no PC: o texto
  `devices.audit_note` está correto." (e retirar o item correspondente
  de §19.2).
- FX-32 e FX-59: substituir por fixture "`policy.set{audit_input:true}`
  → `invalid`" (campo desconhecido) e por fixture de audit que confere
  a ausência de texto.

**F-02 — Média — assunto redigido não força `destructive` (PA7).**
Regra: R11.1. Problema: a pessoa pode aprovar sem step-up um comando do
qual só vê parte (`redacted: true`), exatamente o caso que R11.1 quis
cobrir com `truncated`. Patch proposto: "**R11.1** `subject.truncated:
true` **ou `subject.redacted: true`** DEVE vir com `destructive: true`:
o que a pessoa não vê inteiro exige biometria para permitir."

**F-03 — Média — `hello.nonce` e `auth.proof` sem uso (SD-2).**
Regras: §5.3 (tabela, linha `nonce`), R5.7, exemplo de `auth`, §13.3
(4401 "`proof` inválido"), §19.2 item 11. Problema: campo de segurança
definido sem semântica convida implementação divergente; com TLS mútuo
a prova é redundante (§5.4). Patch proposto:
- §5.3: apagar a linha `nonce` da tabela e o campo do exemplo.
- R5.7: "**R5.7** Em v1 rev 0, `auth.p` DEVE ser `{}` nos dois perfis: no
  perfil remoto, o TLS 1.3 mútuo com chaves fixadas já autentica o
  aparelho (`security.md` §5.4); no local, o ACL do pipe e a prova do
  servidor (R5.8). Uma prova adicional (`proof`) só entra atrás da
  capacidade `auth-proof`, com formato definido em `security.md`."
- Exemplo: `{"t":"auth","k":"auth","p":{}}`.
- §13.3, 4401: "`hello`/`auth` fora do prazo, `auth.p` diferente de `{}`
  (rev 0), prova do servidor local ausente ou errada (R5.8), perfil local
  por conexão remota".
- §19.2 item 11: marcar resolvido (SD-2).

**F-04 — Média — perfil local sem nome de pipe, sem anti-squatting e sem
prova do servidor (item 34).** Regras: §3.2, R3.5, R5.8. Patch proposto:
- §3.2, novo bloco depois de R3.5: "**R3.5a** O nome do pipe é
  `\\.\pipe\pipa-trcd-<SID do usuário>`. A primeira instância DEVE ser
  criada com `FILE_FLAG_FIRST_PIPE_INSTANCE`; se falhar com
  `ERROR_ACCESS_DENIED`, outro processo tem o nome e o agente NÃO DEVE
  usar outro nome: avisa e tenta de novo a cada 10 s. A DACL é
  explícita: só o SID do usuário e SYSTEM; nenhuma entrada para
  Everyone ou Anonymous (`security.md` §10.1)."
- "**R3.5b** O cliente local DEVE abrir o pipe com `SECURITY_SQOS_PRESENT
  | SECURITY_IDENTIFICATION` (ou por um processo auxiliar que o faça) e
  DEVE verificar o servidor pela prova de R5.8 antes de `auth`."
- R5.8: "**R5.8** No perfil local, o `hello` do cliente leva `p.nonce`
  (32 bytes em base64url) e o `hello` do agente responde
  `p.local_proof = base64url(HMAC-SHA-256(cookie, "trcp-local-v1" ‖
  nonce))`, com o cookie de `%LOCALAPPDATA%\Pipa\trcd\local.cookie`
  (`security.md` §10.2). Prova ausente ou errada: o cliente fecha com
  4401 e não envia `auth`. `auth.p` DEVE ser `{}`; a autenticação do
  cliente é o ACL do pipe."
- Fixture nova: "servidor local sem cookie válido → cliente fecha 4401
  antes de `auth`".
- Apagar o parágrafo "O nome do pipe, a proteção contra ... ficam para
  P5" e marcar §19.2 item 34 resolvido.

**F-05 — Média — completar TLS com chave revogada sem guardas (D-21,
R6.3, item 10).** Patch proposto, acrescentar a R6.3: "Guardas: uma
conexão em andamento e uma tentativa por 60 s por fingerprint revogado;
acima de 10 tentativas por hora o agente recusa no próprio TLS por 1 h;
nenhum processamento além do Upgrade e do Close; audit uma vez por hora
(`security.md` §5.5)." Marcar §19.2 item 10 resolvido: opção (a).

**F-06 — Baixa — "em 2 minutos" contra 60 s (item 5).** Regras: §14
(linha "Prazo para Permitir/Recusar no PC"), R10.38. Decisão: **60 s**
(exigências P3, fluxo X4; do ponto de vista de segurança, o menor prazo
reduz a janela em que um modal esquecido aceita um clique distraído).
Patch: texto `pair.err_timeout_body` passa a dizer "em 60 segundos"
(P7, catálogo); a spec só retira a nota "(texto diz 2 min, §19.2)" e
marca o item 5 resolvido.

**F-07 — Baixa — R10.47 e o prazo do `onMessageReceived` (PA-3).**
Problema: buscar pelo túnel antes de notificar pode passar de ~10 s com
ponte distante e rede ruim; push de limpeza sem notificação visível pode
ser rebaixado pelo sistema. Patch proposto para R10.47: "Ao receber um
push de pedido, o app **mostra na hora** a notificação genérica
(`notif.attn`, texto sem conteúdo), conecta pelo túnel, faz `resume` e
então **corrige**: pedido aberto → completa a notificação; resolvido →
cancela. Push de limpeza tem prioridade normal e o app só cancela se
conseguir confirmar pelo túnel." Toca `interfaces/android.md` §11 (P7) e
`bridge.md` B8.6; decisão de M8.

**F-08 — Baixa — R3.9 (compressão), confirmação e alcance.** Decisão de
P5: D-15 **confirmada**; patch: acrescentar a R3.9 "Vale também para a
conexão externa com a ponte (`bridge.md` B2.7). O TLS 1.3 não tem
compressão." e retirar "Revisar em P5".

**F-09 — Média — R6.13 sem canonização (item 12).** Patch proposto,
substituir a última linha de R6.13: "Canonização: `f(x) = len(x) em u16
big-endian ‖ UTF-8(x)`; `H = SHA-256(f(purpose) ‖ f(s) ‖ f(c1) [‖
f(c2)])` com `c1, c2` os campos da lista acima na ordem dada (`minutes` e
`signal` como texto decimal/ASCII); a mensagem assinada é
`"trcp-stepup-v1" ‖ nonce (32 bytes decodificados) ‖ H`; algoritmo
ECDSA P-256 com SHA-256, assinatura em DER, `sig` em base64url sem
padding (`security.md` §8)." Marcar item 12 resolvido.

**F-10 — Média — `pair.claimed` antes da confirmação SPAKE2; `device_name`
sem validação; `sas` sem derivação (R10.38, §14).** Patch proposto,
acrescentar a R10.38: "`pair.claimed` DEVE ser emitido só depois de a
confirmação SPAKE2 do celular ter sido verificada e do payload de
pareamento ter sido aceito (`security.md` §4.2). `device_name` é
normalizado (NFC, sem caracteres de controle, aparado) e cortado em 40
caracteres antes de chegar à extensão (`security.md` §4.6). `sas` é
derivado como em `security.md` §4.3." Na tabela de §14, linha
`device_name`: origem "`security.md` §4.6".

**F-11 — Média — 4410 durante o corte sem guarda (R6.22).** Patch:
acrescentar a R6.22 "com as mesmas guardas de R6.3 (uma tentativa por
aparelho por 60 s)". E fechar §19.2 item 14: "A ponte não precisa saber
do corte; o agente segue registrado (`bridge.md` B5.7)."

**F-12 — Baixa — D-3 e item 32 (escrita liberada sobrevive ao app sair de
primeiro plano).** Decisão de P5: **aceito**. A escrita liberada tem
prazo curto e pertence ao aparelho; o risco adicional de a conexão cair
é nenhum (sem conexão, nada é escrito), e exigir biometria a cada volta
ao primeiro plano quebraria o fluxo F3. Um ajuste opcional do app
"desarmar ao sair do app" pode existir (P7), sem mudança de spec. Marcar
item 32 resolvido.

**F-13 — Baixa — D-5 e item 25 (recusar bloqueado por `policy_off`).**
Recomendação de P5: **manter** D-5. Com a escrita desativada no PC, o
celular não deve influenciar o Claude Code nem para recusar: um "não"
remoto também muda o curso do trabalho de quem está no PC, e a política
é do PC. Decisão final de Sr. Garioli (**DS-2**).

**F-14 — Média — limites antes da autenticação e cabeçalhos do Upgrade.**
Regras: R3.3, §14. Patch proposto: linha nova em §14 "Pedido de Upgrade
(linha + cabeçalhos) | 8 KiB [P8] | esta spec | HTTP 431 e fecha" e
"Mensagem antes de `auth.ok` | 16 KiB e 3 mensagens [P8] | esta spec |
4400". Nota informativa para §3.1: "os frames externos até a ponte têm
64 KiB; uma mensagem TRCP de 256 KB atravessa em vários registros TLS
(`bridge.md` B2.10)".

**F-15 — Média — token de push como quase-segredo (R10.44, R10.45).**
Patch proposto, acrescentar a R10.45: "O token nunca aparece em log,
audit ou `msg`; é entregue à ponte só no momento de um push
(`bridge.md` B8.3) e apagado também quando a ponte responde
`unregistered`."

**F-16 — Baixa — §13.5 e os fechamentos da ponte.** Patch: acrescentar
após a tabela: "Os códigos de fechamento da **ponte** (4404
`agent_offline`, 4408, 4409 `claimed`, 4429 `rate`) e o que o app faz com
cada um estão em `bridge.md` §5.3 e B5.12."

Resumo: 1 Alta, 9 Médias, 6 Baixas. Nenhum achado exige mudar um fluxo
ou uma tela aprovada; F-04 e F-10 acrescentam textos pequenos (P7).

## 17. Decisões pendentes de Sr. Garioli

| Id | Decisão | Opções | Recomendação |
|---|---|---|---|
| **DS-1** | Push para quem hospeda a **própria ponte** (o token FCM do app só aceita remetentes do projeto Firebase da Pipa) | (a) sem push fora de `ponte.gariolilabs.com` no MVP; o app funciona aberto e informa a limitação ao configurar servidor próprio; (b) a Garioli Labs opera um repassador público só de push (`push.gariolilabs.com`), o que recria um serviço público (Marco Civil, abuso, custo); (c) build alternativa do app (F-Droid/APK) com projeto Firebase do próprio usuário; (d) UnifiedPush (ADR-0014 já o adia) | **(a)** agora, com **(d)** como caminho pós-MVP; nunca (b) |
| **DS-2** | D-5: recusar pedido também bloqueado por `policy_off` (§19.2 item 25) | (a) manter; (b) permitir recusar com a escrita desativada | **(a)** (F-13) |
| **DS-3** | Transporte do hook do Claude Code | (a) hook de **comando** `trc hook` pelo pipe (novo ADR que supersede a parte HTTP do ADR-0008); (b) manter HTTP com aviso "só em PC de um usuário" e as mitigações de §11.2 | **(a)** |
| **DS-4** | Ajuste "Só biometria" no app (recria `K_stepup` sem `DEVICE_CREDENTIAL`, com invalidação por biometria nova) e textos "biometria ou PIN" | (a) oferecer, padrão desligado (decisão 3 mantida); (b) não oferecer no MVP | **(a)**; se (b), pelo menos os textos mudam |
| **DS-5** | `minSdk` do app | (a) 30 (Android 11, 2020); (b) 29 com modo degradado (só biometria no step-up) em 29; (c) 26–28 (exige outra arquitetura de step-up) | **(a)** |
| **DS-6** | Recuperação quando `K_stepup` é invalidada | (a) parear de novo (MVP), `device.rekey_stepup` depois; (b) implementar `device.rekey_stepup` já no MVP (comando novo + modal no PC) | **(a)** |

Decisões técnicas tomadas nesta entrega, com veto possível: SD-1 (módulo
SPAKE2 próprio sobre `p256`, §4.4), SD-2 (só TLS mútuo, §5.4), SD-3
(4403 com guardas, §5.5), SD-4 (duas chaves, §6.1), SD-5 (re-parear,
§6.4). Nenhuma exige mudança de tela aprovada; SD-4 e §6.3 exigem os
ajustes de texto já pendentes ("biometria ou PIN").

## 18. Rastreabilidade dos pontos de P5 (e P4/P5)

| Ponto (documento + id) | Onde ficou |
|---|---|
| `adr/README.md` ponto em aberto 1 (uma ou duas chaves) | §6.1 SD-4 |
| `adr/README.md` ponto em aberto 2 (`auth{sig}` + RFC 9266 ou TLS mútuo) | §5.4 SD-2; F-03 |
| `adr/README.md` ponto em aberto 3 (chave de inscrição) | `bridge.md` §3 |
| `adr/README.md` ponto em aberto 4 (credencial do FCM) | `bridge.md` §8; §3.2 (push); DS-1 |
| `adr/README.md` P5: `spake2` não auditada | §4.4 SD-1 |
| `adr/README.md` P5: derivação do SAS | §4.3 |
| `adr/README.md` P5: modelo de chaves e fluxo de invalidação | §6.1, §6.4 SD-5, DS-6 |
| `adr/README.md` P5: efeito de `DEVICE_CREDENTIAL` sobre T1 | §6.3, DS-4 |
| `adr/README.md` P5: autenticação da sessão | §5.4 |
| `adr/README.md` P5: formato do step-up e `requires_step_up` | §8, SP8.5 |
| `adr/README.md` P5: chave de inscrição, limites por IP, abuso da ponte | `bridge.md` §3, §4.3, §7 |
| `adr/README.md` P5: credencial do FCM | `bridge.md` §8 |
| `adr/README.md` P5: chave do PC no cofre (DPAPI via `keyring`) | §7 |
| `adr/README.md` P5: endpoint loopback do hook (T11, T17) | §11, DS-3 |
| `adr/README.md` P5: 4403/4410 e a ponte no corte | §9, §5.5; `bridge.md` B5.7 |
| `adr/README.md` P5: revisão criptográfica antes do código | §4.4 (mitigação 4), §14 |
| ADR-0003 (T1 residual; recuperação após invalidação) | §6.3, §6.4 |
| ADR-0008 (hook HTTP em loopback com token) | §11 (recomenda superseder) |
| ADR-0010 (`spake2`/`snow` não auditadas) | §4.4 |
| ADR-0013 (kill switch persistente) | §9 |
| ADR-0014 (push opaco; credencial) | §3.2, `bridge.md` §8 |
| Auditoria §5.3 (`auth{sig}`), §6 T1–T17, §7.2 (chave no cofre) | §5.4; §3.3; §7 |
| Proposta §6 (plano criptográfico) e §8 (revisão antes do código) | §4, §5; §4.4 |
| `spec/trcp-1.md` §3.1 item 3 (TLS mútuo, P5) | §5 |
| `spec/trcp-1.md` §3.2 (pipe: nome, squatting, verificação) e §19.2 item 34 | §10, F-04 |
| `spec/trcp-1.md` R3.9 / D-15 (compressão) | SP12.3, F-08 |
| `spec/trcp-1.md` R5.7 / §19.2 item 11 (`auth.proof`, channel binding) | §5.4, F-03 |
| `spec/trcp-1.md` §6.1 (o que vem do TLS) | §5.3, §5.6 |
| `spec/trcp-1.md` R6.3 / D-21 / §19.2 item 10 / AJ-22 | §5.5 SD-3, F-05 |
| `spec/trcp-1.md` §6.6 (tipo da chave de step-up) e §19.2 item 13 | §6 |
| `spec/trcp-1.md` R6.13 / §19.2 item 12 / E6 | §8, F-09 |
| `spec/trcp-1.md` §6.7, R6.25, `audit_input` (DP3) | §13, F-01 |
| `spec/trcp-1.md` §6.8 / §19.2 item 14 (ponte e corte) | §9, F-11; `bridge.md` B5.7 |
| `spec/trcp-1.md` R10.38–R10.40 (SAS, `device_name`, QR, lado do celular) | §4.2, §4.3, §4.6, §4.7, F-10 |
| `spec/trcp-1.md` R10.44–R10.47 / §19.2 item 15 (push) | §3.2, F-07, F-15; `bridge.md` §8 |
| `spec/trcp-1.md` §11.7 `destructive` / R11.1 / §19.2 item 33 | §8 (tabela), F-02 |
| `spec/trcp-1.md` §14 `device_name` (P5 valida) | §4.6 |
| `spec/trcp-1.md` §17 linha P5 (todos os itens) | §4, §5, §6, §8, §10; F-01..F-16 |
| `spec/trcp-1.md` §19.1 D-1, D-2, D-4, D-7, D-9, D-11, D-16, D-20 (revisão P5) | Revisadas sem objeção: D-1 (parar e cancelar sem precondição não escrevem dados), D-2 (um aparelho no controle limita o dano), D-4 (desligar retira tudo), D-7 (`unknown` queima o id), D-9 (uma conexão por aparelho), D-11 (código e SAS fora do log), D-16 (`Origin` recusado), D-20 (push de limpeza igual; ver F-07) |
| `spec/trcp-1.md` §19.1 D-3 / §19.2 item 32 | F-12 |
| `spec/trcp-1.md` §19.1 D-5 / §19.2 item 25 | F-13, DS-2 |
| `spec/trcp-1.md` §19.1 D-6 | §3.2 (app), §9 |
| `spec/trcp-1.md` §19.1 D-13 | F-02 (estendida a `redacted`) |
| `spec/trcp-1.md` §19.1 D-15 | F-08 |
| `spec/trcp-1.md` §19.1 D-21 | SD-3 |
| `spec/trcp-1.md` §19.2 item 5 | F-06 |
| `privacy.md` PA7 (redigido não força `destructive`) | F-02 |
| `privacy.md` PA8 (quem envia o push) | `bridge.md` §8 |
| `privacy.md` PA14 (autenticação EX1; lista de origens) | §10.3 |
| `privacy.md` §6.3 `origin` "a partir da autenticação (P5)" | SP10.10 |
| `privacy.md` §8.2 e DP3 (a) | `bridge.md` B8.4; §13 |
| `privacy.md` PA4, PA9, PA11 | `bridge.md` §9, B5.13, B3.4 |
| `requisitos-nao-funcionais.md` PA-3 | F-07; `bridge.md` B8.6 |
| `requisitos-nao-funcionais.md` PA-7 | §12; `bridge.md` §7.2 |
| `requisitos-nao-funcionais.md` PA-9 (`minSdk`) | §6.5, DS-5 |
| `requisitos-nao-funcionais.md` PA-11 | §5.7; `bridge.md` B6.12 |
| `requisitos-nao-funcionais.md` PA-12 | SP10.10 |
| `requisitos-nao-funcionais.md` PA-2, PA-8 | `bridge.md` B5.15, §6.4 |
| `interfaces/ajustes-pendentes-2026-09-26.md` AJ-22 | §5.5 (opção a) |
| `interfaces/ajustes-pendentes-2026-09-26.md` AJ-32 | §10.3 (opção a) |
| `interfaces/exigencias-para-o-protocolo.md` E6, E9, P1, P2, P3, P5, I11 | §8; SP8.5; §4.3; §4.2; `bridge.md` B4.5; §4.7; §7 e `bridge.md` B3.3 |
| `exigencias-externas.md` EX1 (autenticação de quem chama) | §10.3 |
| `docs/plans/00-mapa-do-planejamento.md` P4, P5 | `bridge.md`; este documento |

Itens que esta entrega passa adiante: linhas novas em `privacy.md` §3.3
(rótulo da chave de inscrição; lista de origens EX1) para P6; textos
novos pequenos para P7 (`pair.err_claimed`, `vsc.local_pipe_taken`,
`vsc.local_pipe_untrusted`, `vsc.notice_origin_ask`, aviso de chave
rotacionada, aviso de pausa por abuso, "biometria ou PIN"); ADR novo
para DS-3 se aprovada; spikes M0 listados em §5.3 e SP10.6.

## 19. Fontes consultadas (2026-09-27)

- RFC 9382 (SPAKE2): https://www.rfc-editor.org/rfc/rfc9382.html
- RFC 8446 (TLS 1.3): https://www.rfc-editor.org/rfc/rfc8446.html
- RFC 9266 (`tls-exporter`): https://www.rfc-editor.org/rfc/rfc9266.html
- RFC 5869 (HKDF), RFC 2104 (HMAC), RFC 8439 (ChaCha20-Poly1305),
  RFC 9106 (Argon2), RFC 6455 (WebSocket), RFC 6761 (`.invalid`)
- `spake2` 0.4.0: https://docs.rs/spake2/latest/spake2/ e
  https://github.com/RustCrypto/PAKEs
- `p256`: https://github.com/RustCrypto/elliptic-curves
- CPace: https://datatracker.ietf.org/doc/draft-irtf-cfrg-cpace/
- `rustls` 0.23.45: https://docs.rs/rustls/latest/rustls/server/danger/trait.ClientCertVerifier.html,
  https://docs.rs/rustls/latest/rustls/client/danger/trait.ServerCertVerifier.html,
  https://docs.rs/rustls/latest/rustls/struct.ConnectionCommon.html,
  https://docs.rs/rustls/latest/rustls/manual/_04_features/index.html,
  https://github.com/rustls/rustls/blob/main/README.md,
  https://github.com/rustls/rustls/tree/main/audit,
  https://jbp.io/2020/06/14/rustls-audit.html
- `tungstenite` 0.30: https://docs.rs/tungstenite/latest/tungstenite/protocol/struct.WebSocketConfig.html
- Android: https://developer.android.com/privacy-and-security/keystore,
  https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec.Builder,
  https://github.com/androidx/androidx/blob/androidx-main/biometric/biometric/src/main/java/androidx/biometric/BiometricPrompt.java,
  https://developer.android.com/privacy-and-security/security-key-attestation,
  https://developer.android.com/about/versions/10/behavior-changes-all
- Conscrypt: https://github.com/google/conscrypt/blob/master/common/src/main/java/org/conscrypt/Conscrypt.java
- FCM: https://firebase.google.com/docs/cloud-messaging/auth-server,
  https://firebase.google.com/docs/cloud-messaging/customize-messages/set-message-type,
  https://firebase.google.com/docs/projects/iam/roles-predefined-product
- Cloud Run: https://docs.cloud.google.com/run/docs/triggering/websockets,
  https://docs.cloud.google.com/run/docs/configuring/request-timeout,
  https://docs.cloud.google.com/run/docs/configuring/max-instances,
  https://docs.cloud.google.com/run/docs/configuring/session-affinity,
  https://docs.cloud.google.com/run/docs/securing/service-identity,
  https://cloud.google.com/run/pricing,
  https://docs.cloud.google.com/free/docs/free-cloud-features
- Windows: https://learn.microsoft.com/windows/win32/api/namedpipeapi/nf-namedpipeapi-createnamedpipew,
  https://learn.microsoft.com/windows/win32/ipc/named-pipe-security-and-access-rights,
  https://learn.microsoft.com/windows/win32/api/fileapi/nf-fileapi-createfilew,
  https://learn.microsoft.com/windows/win32/secauthz/impersonation-levels,
  https://learn.microsoft.com/windows/win32/api/winbase/nf-winbase-getnamedpipeserverprocessid,
  https://learn.microsoft.com/windows/win32/api/winbase/nf-winbase-getnamedpipeclientprocessid,
  https://learn.microsoft.com/windows/win32/api/dpapi/nf-dpapi-cryptprotectdata,
  https://learn.microsoft.com/windows/win32/api/wincred/ns-wincred-credentialw
- `keyring` 4.2.0: https://docs.rs/keyring/latest/keyring/ e
  https://docs.rs/windows-native-keyring-store/latest/windows_native_keyring_store/
- Claude Code hooks: https://code.claude.com/docs/en/hooks
- Cadeia de suprimento: https://embarkstudios.github.io/cargo-deny/checks/index.html,
  https://mozilla.github.io/cargo-vet/, https://docs.sigstore.dev/cosign/signing/overview/,
  https://code.visualstudio.com/docs/configure/extensions/extension-marketplace,
  https://code.visualstudio.com/api/working-with-extensions/publishing-extension,
  https://support.google.com/googleplay/android-developer/answer/9842756
- Marco Civil (Lei 12.965/2014): https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2014/lei/l12965.htm
  (texto conferido em https://www2.camara.leg.br/legin/fed/lei/2014/lei-12965-23-abril-2014-778630-publicacaooriginal-143980-pl.html)
