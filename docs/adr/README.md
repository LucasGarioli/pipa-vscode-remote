# Registros de decisão de arquitetura (ADRs) da Pipa

Status: entrega P2 do planejamento (`docs/plans/00-mapa-do-planejamento.md`),
2026-09-26, aguardando revisão.

Cada ADR registra **uma decisão já tomada** por Sr. Garioli nos documentos
de planejamento. Nenhum ADR daqui cria decisão nova: quando um ponto ainda
não foi decidido, ele aparece como risco, proposta ou ponto em aberto.

## Formato

MADR curto, em PT-BR:

- **Status:** Aceita, data, quem decidiu e onde a decisão ficou registrada;
- **Contexto;**
- **Decisão;**
- **Alternativas consideradas** e por que caíram;
- **Consequências** positivas e negativas;
- **Referências**, com a seção do documento de origem.

Legenda herdada da auditoria: **[FATO]** verificado em fonte primária pelo
documento de origem; **[INFERÊNCIA]** conclusão a partir de fatos;
**[RECOMENDAÇÃO]** sugestão ainda não decidida. Toda afirmação técnica
cita a seção de origem.

Um ADR aceito não se edita para mudar a decisão: uma decisão nova vira um
ADR novo que marca o antigo como "Substituída por ADR-XXXX". Detalhar uma
decisão que o ADR deixava em aberto (como os itens de "Decididos depois da
primeira versão") atualiza o próprio ADR, com data e registro no Status.

## Índice

| ADR | Decisão | Fonte principal |
|---|---|---|
| [0001](0001-agente-dono-do-pty.md) | O agente Rust é dono dos PTYs (ConPTY); a extensão é uma view `Pseudoterminal` fina | Auditoria §1, §3 C1–C2, §4, §9.1, §12 P1 |
| [0002](0002-perfil-terminal-remoto-padrao-so-leitura.md) | Só terminais do perfil "Terminal remoto"; a extensão oferece torná-lo padrão uma vez e só grava com "sim"; com "não", não pergunta de novo e há o comando "Usar como padrão"; todo terminal começa só leitura | Auditoria §12 P2, §13; `interfaces/vscode.md` §6; decisão de 2026-09-26 |
| [0003](0003-escrita-por-sessao-com-biometria.md) | Escrita liberada por terminal, 1/5/15 min, com biometria ou PIN do aparelho (`BIOMETRIC_STRONG \| DEVICE_CREDENTIAL`, Keystore P-256 + `BiometricPrompt`/`CryptoObject`); destrutivo e encerrar pedem de novo | Auditoria §6 T1, §12 P3; interfaces Q1, Q7, Q9, Q10; decisão de 2026-09-26 |
| [0004](0004-ponte-propria-e-codigo-de-12-digitos.md) | Ponte própria `trc-bridge` + código de 12 dígitos (4 encontro + 8 segredo SPAKE2) + TLS 1.3 mútuo fixado dentro do fluxo retransmitido; confirmação de 6 dígitos no PC; `ponte.gariolilabs.com` privada (Sr. Garioli e quem ele autorizar); os demais usam ponte própria, com o mesmo binário | Proposta §4–§7; decisões de 2026-09-26 (itens 4 e 5) |
| [0005](0005-sem-tailscale-dev-tunnels-e-contas-de-terceiros.md) | Sem Tailscale, Microsoft Dev Tunnels, VS Code tunnels ou contas de terceiros | Proposta §1–§3, §8; `visao.md` |
| [0006](0006-hospedagem-da-ponte-adiada-para-m6.md) | Hospedagem da ponte adiada para M6; binário único; modos permanente e sob demanda; Cloud Run 24/7 descartado; sem ponte pública | Proposta §4.1; decisão de 2026-09-26 (item 5) |
| [0007](0007-event-log-e-screen-sync.md) | Event Log global `(epoch, seq)` com resume/snapshot + Screen Sync estilo mosh (diffs versionados + acks); nunca VT cru para o celular | Auditoria §5.4, §9.3 |
| [0008](0008-atencao-por-hooks-do-claude-code.md) | "Aguardando" detectado por hooks do Claude Code (HTTP hook em loopback + token por sessão); heurística só como fallback rotulado | Auditoria §3 C3, §6 T10/T17, §7.1 |
| [0009](0009-identidade-pipa.md) | Nome Pipa, logo A, PT-BR + EN, claro + escuro | `visao.md` |
| [0010](0010-reuso-de-desenho-sem-codigo-copyleft.md) | Reusar o desenho, não o código, de magic-wormhole.rs (EUPL) e RustDesk (AGPL); TLS nas sessões, SPAKE2 só no pareamento; `spake2`/`snow` não auditados = risco aberto para P5 | Proposta §6 |
| [0011](0011-comandos-at-most-once-sem-retry.md) | Comandos de escrita at-most-once com `cmd.id`, sem retry automático, com precondição `expect`/`already_resolved` | Auditoria §3 A2–A3, §5.5, §9.4; interfaces decisões 5–6 |
| [0012](0012-minimizacao-de-dados-no-celular.md) | Nada da tela persiste no celular; não guarda lista de terminais; `FLAG_SECURE` padrão; push opaco; WebSocket só em primeiro plano | Auditoria §7.3, §9.7; interfaces Q2, Q3 |
| [0013](0013-kill-switch-e-revogacao-no-pc.md) | Kill switch sem confirmação, com Reativar, persistente após reboot; revogar aparelhos só no PC | Interfaces decisão 3, Q5, Q6 |
| [0014](0014-push-fcm-opaco.md) | Push pelo FCM com payload opaco `{agent_id, attention_id}`; conteúdo buscado pelo túnel; UnifiedPush fora do MVP | Auditoria §12 P4; decisão de 2026-09-26 |

Os ADRs 0011–0014 não estavam na lista mínima do mapa. 0011–0013 entraram
porque são decisões aprovadas por Sr. Garioli (auditoria §9 mantida pela
proposta, e perguntas Q1–Q11 aceitas na aprovação das interfaces); 0014
registra a decisão de push de 2026-09-26.

## Decididos depois da primeira versão (2026-09-26)

Pontos que a primeira versão desta pasta listava como conflito e que Sr.
Garioli decidiu em 2026-09-26. **Decidido por Sr. Garioli.**

1. **Perfil padrão quando a pessoa responde "não"** (ADR-0002). A extensão
   não pergunta de novo; só os terminais do perfil "Terminal remoto"
   aparecem no celular; o celular mostra um estado vazio que ensina a
   abrir um; um comando "Usar como padrão" no VS Code permite mudar depois.
   A divergência de texto entre a auditoria (§12, §13: a extensão "define"
   o padrão) e `interfaces/vscode.md` §6 (pergunta com consentimento) fica
   resolvida a favor de `vscode.md`.
2. **Push** (ADR-0014; ADR-0012). FCM com payload opaco, sem conteúdo; o
   app busca o conteúdo pelo túnel. UnifiedPush fora do MVP. Fecha a
   pergunta 4 da auditoria e a divergência com
   `interfaces/exigencias-para-o-protocolo.md` E24.
3. **PIN/padrão do aparelho vale para liberar escrita** (ADR-0003):
   `BIOMETRIC_STRONG | DEVICE_CREDENTIAL`. O modelo de chaves do celular
   (uma ou duas) **não** foi decidido e segue para P5.
4. ~~**Ponte padrão** (ADR-0004, ADR-0006). `ponte.gariolilabs.com` vem
   configurada; quem quiser aponta para a própria ponte (mesmo binário); a
   ponte não vê o conteúdo. Como terceiros obtêm a chave de inscrição da
   ponte padrão fica para P4.~~ **SUBSTITUÍDO pelo item 5** (2026-09-26).
5. **Ponte privada, sem ponte pública** (ADR-0004, ADR-0005, ADR-0006;
   substitui o item 4). Texto de Sr. Garioli: "Servidor só pra mim e pra
   quem eu autorizar. Outros usam servidores próprios deles ou raspberry
   deles." Consequências registradas:
   - `ponte.gariolilabs.com` é **privada**: só Sr. Garioli e quem ele
     autorizar, com chave de inscrição emitida por ele; formato, emissão e
     revogação ficam para P4 (Fable). Não há ponte pública padrão.
   - Os demais usuários hospedam a própria ponte (mesmo binário
     `trc-bridge`), em servidor, VPS ou Raspberry. Raspberry em casa
     atrás de CGNAT exige IP público da operadora ou VPS (proposta §3,
     §4.1).
   - A extensão pede o endereço da ponte na primeira vez (no uso de Sr.
     Garioli, pré-preenchido ou configurado). O QR carrega o endereço; o
     código digitado de 12 dígitos não carrega, então o app precisa de um
     campo "Servidor" ao adicionar um computador (ajuste de interface,
     `../interfaces/ajustes-pendentes-2026-09-26.md`).
   - Privacidade: a Garioli Labs só opera metadados de usuários
     autorizados; **[INFERÊNCIA]** a questão do Marco Civil
     provavelmente diminui, e o parecer jurídico antes de M6 continua
     (`privacy.md` §7.4, DP1).
   - O dimensionamento da ponte (`requisitos-nao-funcionais.md` DP-4,
     NFR-16) foi revisto por consequência desta decisão.

## Decisões ainda abertas (não são ADRs)

- Escopo de Remote-SSH/WSL no primeiro ano (auditoria §12, pergunta 5).
- Licença do repositório público (auditoria §12, pergunta 6; §9 item 9).
- Emulador VT (`alacritty_terminal` ou `vt100`) e licenças de
  `portable-pty` etc. (spike M0, auditoria §8 e Anexo A).
- Onde hospedar a ponte privada (M6; ADR-0006 registra o adiamento e o
  endereço, não o lugar).
- Framework mobile: a auditoria recomenda Kotlin + Compose, mas classifica
  como decisão adiável (auditoria §10).

## Pontos em aberto (conflitos entre documentos)

Registrados, não resolvidos. Cada um precisa de decisão de Sr. Garioli ou
da entrega indicada.

1. **Uma chave ou duas no celular.** **[INFERÊNCIA]** A proposta usa a
   chave do cliente no Keystore para o TLS mútuo de toda sessão (§6 item
   2); `interfaces/android.md` §0 fala de uma "chave de escrita" com
   `setUserAuthenticationRequired(true)`; a auditoria §6 T1 aplica
   `setUserAuthenticationParameters(0, …)` à "chave do dispositivo". Se
   fosse a mesma chave, toda conexão pediria biometria ou PIN, contra Q10
   (sem biometria ao abrir o app). Os documentos não dizem se são duas
   chaves. Decisão de P5.
2. **Autenticação da sessão: `auth{sig}` com channel binding ou TLS
   mútuo.** A auditoria §5.3 autentica o celular com `auth{sig}` assinado
   sobre `nonce ‖ tls_exporter` (RFC 9266) sobre um TLS só com certificado
   do agente fixado; a proposta §6 troca por TLS 1.3 **mútuo** com chaves
   fixadas dentro do fluxo da ponte e não diz se o `auth{sig}` continua.
   Decisão de P3/P5.
3. **Chave de inscrição da ponte privada.** A proposta §7 exige uma chave
   de inscrição gerada na instalação da ponte ("sem ela, nenhum PC se
   registra"). Com `ponte.gariolilabs.com` privada (item 5), falta dizer
   o formato da chave, como Sr. Garioli a emite para quem autoriza (uma
   por pessoa ou uma só), como a revoga e onde a extensão a guarda sem
   virar segredo em texto claro. Decisão de P4 (Fable).
4. **Credencial de envio do FCM.** **[INFERÊNCIA]** A auditoria §12
   (pergunta 4) diz que o FCM exige credencial de conta de serviço; não
   está dito se quem envia é o agente em cada PC, a ponte ou um serviço à
   parte. Decisão de P4/P5 (ADR-0014).
5. **Limite de scrollback no agente.** Auditoria §7.1: `scrollback
   (≤ 5 000 linhas)`; auditoria §13: "scrollback limitado a ~2 000
   linhas". Decisão de P8.

## Ajustes de interface pendentes

As decisões de 2026-09-26 pedem mudanças em documentos de interface que
esta entrega **não edita**. Os nomes de chave abaixo são **sugestões**;
quem mantém `docs/interfaces/` decide o nome final e regenera `textos.md`
a partir de `prototipo/textos.catalogo.json`. A lista consolidada de todos
os ajustes pendentes, com esta seção incluída, está em
`../interfaces/ajustes-pendentes-2026-09-26.md`.

**Perfil padrão (item 1)**

| Onde | Hoje | O que falta |
|---|---|---|
| `textos.md` / catálogo | Não há chaves para a notificação que oferece o perfil padrão (`interfaces/vscode.md` §6 só a descreve) | Texto da notificação, botão "Usar como padrão" e botão de recusa (sugestão: `vsc.default_profile_offer`, `vsc.default_profile_accept`, `vsc.default_profile_decline`) |
| `textos.md` / catálogo; `interfaces/vscode.md` §9 | A lista de comandos não tem "Usar como padrão" | Título do comando na paleta (sugestão: comando `pipa.useAsDefault`, texto `vsc.cmd_use_as_default` = "Usar o Terminal remoto como padrão") |
| `textos.md` `sessions.empty_body` | "Abra um terminal no VS Code: ele já nasce no perfil Terminal remoto e aparece aqui." — falso quando a pessoa disse "não" | Variante que ensina a abrir um terminal do perfil "Terminal remoto" (pelo menu do "+" no VS Code) e cita o comando "Usar como padrão" (sugestão: `sessions.empty_body_not_default`). **[INFERÊNCIA]** o celular precisa saber se o perfil é padrão no PC para escolher a variante; isso vira exigência para P3 (campo no `hello` ou na política) |
| `visao.md` "O que faz" | "Mostra no celular todos os terminais abertos no VS Code" | "…todos os terminais abertos pelo perfil Terminal remoto (o padrão, se a pessoa aceitar)" ou equivalente |
| `interfaces/vscode.md` §6 | "A extensão pergunta uma vez" | Acrescentar que, após "não", não pergunta de novo e aponta o comando |

**PIN vale para liberar escrita (item 3)**

| Onde | Hoje | O que falta |
|---|---|---|
| `pair.success_body`, `vsc.allow_detail`, botão "Liberar com biometria" (`interfaces/android.md` §8) | Dizem só "biometria" | Decidir se o texto passa a "biometria ou PIN" / "desbloqueio do aparelho". O `BiometricPrompt` já oferece "Usar PIN" (`arm.bio_use_pin`); o ajuste é de precisão, não de fluxo |

**Push (item 2):** nenhum texto novo; as telas já tratam push opaco
(`notif.*`).

**Ponte privada (item 5):** o app precisa de um campo "Servidor" ao
adicionar um computador por código digitado, e a extensão precisa pedir o
endereço da ponte (e a chave de inscrição) na primeira vez; `pipa.bridge`
deixa de ter `ponte.gariolilabs.com` como padrão para todos. Detalhe e
propostas em `../interfaces/ajustes-pendentes-2026-09-26.md`.

## Notas de leitura

- Partes da auditoria que falam de Tailscale continuam no texto sem
  edição: diagrama §4.2, handshake §5.3 e pairing §5.7 no tailnet,
  mitigação T3/T4 (§6), fase M6 (§8), "único pré-requisito externo é o
  Tailscale" (§13), "Conclusão" e Anexo B. O cabeçalho da auditoria avisa
  que o transporte foi substituído pela proposta, e a proposta §8 redefine
  M6 como "ponte + pareamento por código + TLS fixado". Vale a proposta.
- A meta de latência de 150 ms p95 (auditoria §13) foi ajustada pela
  proposta para ≤ 400 ms p95 com ponte nos EUA (proposta §4.1); não é
  conflito, depende de ADR-0006.

## O que fica para P5 (segurança, Fable max)

- **`spake2` não auditada** (e `snow`, já descartada nas sessões): usar,
  com vetores de teste e quais mitigações, ou trocar (ADR-0010).
- Derivação do código de confirmação de 6 dígitos a partir da transcrição
  SPAKE2 (proposta das interfaces:
  `HKDF(K, "trcp-sas-v1") mod 10^6`, exigências P1).
- Modelo de chaves do celular (ponto em aberto 1) e fluxo quando
  `setInvalidatedByBiometricEnrollment` invalida a chave (ADR-0003).
- Efeito de aceitar `DEVICE_CREDENTIAL` sobre a ameaça T1 (ADR-0003).
- Autenticação da sessão sobre o fluxo retransmitido: TLS mútuo,
  `auth{sig}` + RFC 9266, ou os dois (ponto em aberto 2).
- Formato do step-up (`step_up.challenge`, `sig` sobre `cmd_hash`,
  exigências E6) e o `requires_step_up` do pedido (E9).
- Chave de inscrição da ponte privada (formato, emissão por Sr. Garioli,
  revogação), limite de tentativas por IP e abuso da ponte, junto com P4
  (ponto em aberto 3; proposta §7).
- Onde fica a credencial de envio do FCM (ponto em aberto 4; ADR-0014).
- Chave do PC no cofre do SO (DPAPI via `keyring`; auditoria §7.2,
  proposta §6).
- Endpoint loopback do HTTP hook com token por sessão (auditoria §6 T11,
  T17; ADR-0008).
- Revogação e corte: semântica de 4403 e da proposta 4410 `cut`, e o que a
  ponte responde durante o corte (ADR-0013; exigências E19, E20).
- A proposta §8 exige revisão de segurança dedicada da parte criptográfica
  **antes de qualquer código**.
