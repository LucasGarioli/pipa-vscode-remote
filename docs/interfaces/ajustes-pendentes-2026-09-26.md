# Ajustes de interface pendentes (2026-09-26)

Status: **proposta para aprovação de Sr. Garioli.** Nada aqui foi aplicado
às interfaces aprovadas (`android.md`, `vscode.md`, `textos.md`,
`fluxos.md`, `visao.md`); este arquivo só junta, numa lista única, os
ajustes de tela e de texto que as entregas de planejamento pediram.

## Resumo

- **36 ajustes** (AJ-01 a AJ-36), sem repetição.
- **21 são correção óbvia**: consequência direta de uma decisão já tomada
  ou texto que contradiz o comportamento aprovado.
- **15 pedem decisão**: 13 de Sr. Garioli e 2 de P5 (segurança, Fable),
  que valem a pena conhecer, mas não precisam de resposta dele agora
  (AJ-22, AJ-32).

Pedem decisão de Sr. Garioli: AJ-03, AJ-04, AJ-07, AJ-08, AJ-10, AJ-11,
AJ-15, AJ-16, AJ-18, AJ-19, AJ-25, AJ-33, AJ-34.

## Como ler

- **Tela:** arquivo de interface e seção afetados.
- **Proposta:** o que mudar. Textos em PT-BR, com a chave de catálogo
  sugerida; o EN entra junto, em `prototipo/textos.catalogo.json`, quando
  o ajuste for aprovado. O nome final da chave é de quem mantém
  `docs/interfaces/`.
- **Origem:** documento e item que pediram o ajuste.
- **Precisa de decisão?** "Não" = correção óbvia. "Sim" = opções, com a
  recomendação marcada.
- Aplicar um ajuste aprovado = editar o catálogo, regenerar `textos.md` e
  o protótipo (`prototipo/ferramentas/build.py`, `gen_textos.py`) e
  editar a seção indicada. O protótipo hoje usa
  `BRIDGE = 'ponte.gariolilabs.com'`; ele passa a mostrar o campo
  "Servidor" junto com AJ-02.

Fontes varridas: `docs/adr/README.md` ("Ajustes de interface
pendentes" e item 5 dos decididos); `docs/spec/trcp-1.md` §19.2, itens
1–10, 23, 24, 27, 29, 30 e 31; `docs/privacy.md` §15, PA1, PA6 e PA13;
`docs/requisitos-nao-funcionais.md` §7, PA-2, PA-4 e PA-10;
`docs/exigencias-externas.md` EX1; decisão de 2026-09-26 sobre a ponte
privada (`docs/adr/0004-…`).

---

## A. App Android (`android.md`)

### §1 Boas-vindas

**AJ-01 — Passos da Boas-vindas sem o servidor**

- **Tela:** `android.md` §1; `textos.md` `welcome.step1`,
  `welcome.step3`.
- **Problema:** os três passos supõem uma ponte já configurada; sem ponte
  pública, quem digita o código também precisa do servidor.
- **Proposta:**
  - `welcome.step1` = "Instale a extensão Pipa no VS Code e configure o
    servidor.";
  - `welcome.step3` = "Leia o QR ou digite aqui o código de 12 dígitos e
    o servidor.".
- **Origem:** decisão de 2026-09-26, ponte privada (ADR-0004; ADR README
  item 5).
- **Precisa de decisão?** Não. A palavra "servidor" depende de AJ-34.

### §2 Adicionar computador

**AJ-02 — Campo "Servidor" ao adicionar computador**

- **Tela:** `android.md` §2 (bloco "Ponte"); `textos.md` `add.bridge_*`.
- **Problema:** o código digitado de 12 dígitos não carrega o endereço da
  ponte, e não existe mais uma ponte padrão para o app usar. Hoje a tela
  só mostra o endereço e um link "Alterar" que leva às Configurações.
- **Proposta:**
  - na aba "Digitar código", um campo **Servidor** acima do código,
    editável no próprio formulário (sai o link para Configurações);
  - pré-preenchido com o servidor do último computador adicionado; vazio
    no primeiro;
  - "Conectar" fica desabilitado até ter servidor **e** 12 dígitos, com o
    motivo em `stateDescription` (mesma regra do código);
  - na aba "Ler QR", o servidor vem do QR e aparece no mesmo campo, para
    a pessoa ver onde vai conectar;
  - o celular não precisa da chave de inscrição (proposta §7: só PCs se
    registram); se P4 exigir, volta como ajuste novo.
  - Textos:
    - `add.server_label` = "Servidor";
    - `add.server_placeholder` = "ex.: ponte.seudominio.com";
    - `add.server_help` = "O endereço aparece no VS Code, no painel
      Conectar celular. O QR já traz o servidor.";
    - `add.server_missing` = "Informe o servidor.";
    - saem `add.bridge_label`, `add.bridge_change` e `add.bridge_help`.
- **Origem:** decisão de 2026-09-26 (ADR-0004; ADR README item 5).
- **Precisa de decisão?** Não: é consequência da decisão. O rótulo
  depende de AJ-34.

**AJ-03 — QR que traz um servidor desconhecido**

- **Tela:** `android.md` §2 ("se o QR trouxer uma ponte desconhecida, o
  app pergunta antes"); `exigencias-para-o-protocolo.md` P5.
- **Problema:** sem ponte padrão, no primeiro pareamento **todo**
  servidor é desconhecido; a regra atual faria a pergunta aparecer sempre.
- **Opções:**
  - (a) perguntar sempre que o servidor não estiver na lista do app,
    inclusive no primeiro computador;
  - (b) **[RECOMENDADA]** no primeiro computador, só mostrar o servidor no
    campo (AJ-02), sem diálogo; perguntar quando o app já tem computadores
    e o QR traz um servidor diferente de todos eles;
  - (c) nunca perguntar; só mostrar.
- **Por que (b):** a ponte não lê nada (TLS ponta a ponta, PAKE), então um
  QR com servidor trocado arrisca disponibilidade e metadados, não
  conteúdo; o diálogo só tem valor quando há um "normal" para comparar.
- **Textos de (b):**
  - `add.server_new_title` = "Usar outro servidor?";
  - `add.server_new_body` = "Este QR usa {bridge}. Seus outros
    computadores usam {known}. Continue só se foi você quem configurou
    esse servidor.";
  - `add.server_new_yes` = "Usar {bridge}";
  - `add.server_new_no` = "Cancelar".
- **Origem:** decisão de 2026-09-26; exigências P5.
- **Precisa de decisão?** Sim.

**AJ-04 — Leitor de QR: embutido ou do Google Play services**

- **Tela:** `android.md` §0 (tabela de permissões, `CAMERA`) e §2 (aba
  "Ler QR", `add.qr_camera_*`).
- **Problema:** um leitor embutido pesa alguns MB por arquitetura, contra
  a meta de download ≤ 10 MB (NFR-12). **[INFERÊNCIA — verificar]** o
  leitor de código do Google Play services não pede a permissão
  `CAMERA`, mas abre a própria tela do Google, fora do desenho aprovado.
- **Opções:**
  - (a) **[RECOMENDADA, depois de verificar em M7]** leitor do Google Play
    services: sai `CAMERA` da tabela; a aba "Ler QR" vira um botão que abre
    o leitor; `add.qr_camera_denied` e `add.qr_camera_a11y` dão lugar a
    `add.qr_unavailable` = "Não foi possível abrir o leitor de QR. Digite
    o código e o servidor.";
  - (b) leitor embutido, como aprovado: o visor fica dentro do app e o
    APK cresce.
- **Por que (a):** o push já exige Google Play services (FCM, ADR-0014),
  então não entra dependência nova; uma permissão a menos e APK menor.
- **Origem:** `requisitos-nao-funcionais.md` §7 PA-10.
- **Precisa de decisão?** Sim.

### §4 Erros de pareamento

**AJ-05 — "2 minutos" no erro de confirmação**

- **Tela:** `android.md` §4; `textos.md` `pair.err_timeout_body`.
- **Problema:** o texto diz "em 2 minutos"; a própria tabela de §4, o
  fluxo X4, ADR-0004 e a spec usam 60 s.
- **Proposta:** `pair.err_timeout_body` = "Ninguém confirmou em {pc} em
  60 segundos. Gere um novo código quando estiver perto do PC."
- **Origem:** `trcp-1.md` §19.2 item 5.
- **Precisa de decisão?** Não.

### §6 Terminais de um computador

**AJ-06 — Estado vazio depois de um "não" ao perfil padrão**

- **Tela:** `android.md` §6 (Estados, vazio); `textos.md`
  `sessions.empty_body`.
- **Problema:** o texto diz que o terminal "já nasce no perfil Terminal
  remoto", o que é falso quando a pessoa recusou o perfil padrão.
- **Proposta:**
  - `sessions.empty_body_not_default` = "Só os terminais do perfil
    Terminal remoto aparecem aqui. No VS Code, abra um pelo menu do + ou
    rode Pipa: Usar o Terminal remoto como padrão.";
  - o app escolhe o texto por `agent.remote_profile_default` (spec §11.7,
    AD1): `true` → `sessions.empty_body`; `false` ou `null` → a variante
    nova.
- **Origem:** ADR README, ajustes do item 1; `trcp-1.md` §19.2 item 29.
- **Precisa de decisão?** Não.

**AJ-07 — Onde o aviso de outro programa (EX1) aparece no app**

- **Tela:** `android.md` §5 e §6.
- **Problema:** nenhuma tela mostra os avisos da entrada local (primeiro
  cliente: claude-hadouken).
- **Opções:**
  - (a) **[RECOMENDADA]** seção **Avisos** no topo da tela "Terminais de
    um computador", acima de "Abertos", com um cartão por aviso (origem,
    título, texto curto, hora) e Dispensar; na lista "Computadores", a
    contagem de avisos ao lado da de pedidos;
  - (b) tela própria "Avisos", aberta por um ícone na barra de
    "Computadores";
  - (c) misturar com os pedidos de atenção (faixa âmbar).
- **Por que (a):** o aviso é de um PC, então fica com o PC, sem navegação
  nova; e não usa o âmbar, que é só de pedido (decisão de desenho 2).
- **Textos de (a):**
  - `notices.title` = "Avisos";
  - `notices.from` = "{origem} · {time}";
  - `notices.dismiss` = "Dispensar";
  - `notices.dismiss_all` = "Dispensar todos";
  - `pcs.notices_one` = "1 aviso"; `pcs.notices_other` = "{n} avisos".
- **Origem:** `exigencias-externas.md` EX1 ("onde o aviso aparece no
  app"); `privacy.md` §15 PA13.
- **Precisa de decisão?** Sim.

**AJ-08 — Como silenciar uma origem de avisos**

- **Tela:** `android.md` §6 (cartão do aviso) e §12.
- **Problema:** EX1 pede que a pessoa possa silenciar uma origem; nenhuma
  tela prevê isso.
- **Opções:**
  - (a) **[RECOMENDADA]** no celular: menu do cartão → "Silenciar avisos
    de {origem}"; o pedido vai ao agente, que deixa de mandar push dessa
    origem para este celular; a lista "Avisos silenciados", com Reativar,
    fica em "Aparelhos e segurança";
  - (b) só no PC, numa configuração ou na árvore da Pipa no VS Code;
  - (c) nos dois lugares.
- **Por que (a):** a pessoa quer silenciar no momento em que o aviso
  incomoda, no celular; guardar no agente evita push inútil e não grava
  nada novo no celular. Exige um comando no TRCP (P3).
- **Textos de (a):**
  - `notices.mute` = "Silenciar avisos de {origem}";
  - `notices.muted_toast` = "Avisos de {origem} silenciados neste
    celular.";
  - `devices.muted_title` = "Avisos silenciados";
  - `devices.muted_unmute` = "Reativar";
  - `devices.muted_empty` = "Nenhuma origem silenciada.".
- **Origem:** `exigencias-externas.md` EX1; `privacy.md` §15 PA13.
- **Precisa de decisão?** Sim.

### §7 Terminal

**AJ-09 — Tamanho quando nenhum terminal do VS Code está ligado**

- **Tela:** `android.md` §7 (barra superior); `textos.md`
  `session.size_desktop`.
- **Problema:** com `size_src: "agent"`, o sufixo "(VS Code)" é falso.
- **Proposta:** `session.size_agent` = "{cols}×{rows} (último tamanho)".
- **Origem:** `trcp-1.md` §19.2 item 9 (R9.3).
- **Precisa de decisão?** Não.

**AJ-10 — Colar texto com várias linhas no campo de envio**

- **Tela:** `android.md` §7 (campo de envio, estados de envio).
- **Problema:** a spec só aceita uma linha por envio (D-22: um envio nunca
  executa dois comandos); a tela não diz o que acontece ao colar várias
  linhas.
- **Opções:**
  - (a) **[RECOMENDADA]** não enviar e avisar, mantendo o texto:
    `session.err_multiline` = "O texto tem várias linhas. Envie uma linha
    por vez.";
  - (b) trocar as quebras de linha por espaços, sozinho, antes de enviar.
- **Por que (a):** (b) muda em silêncio o que a pessoa vai executar; (a)
  segue a regra "o texto digitado nunca se perde".
- **Origem:** `trcp-1.md` §19.2 item 27 (D-22, R10.18).
- **Precisa de decisão?** Sim.

**AJ-11 — O que a tela mostra ao perder a rede**

- **Tela:** `android.md` §0 ("Offline: … conteúdo antigo apagado") e §7
  ("reconectando: a tela congela esmaecida"); `fluxos.md` X7 ("a tela
  antiga é descartada").
- **Problema:** as telas aprovadas se contradizem, e a spec (PV2) diz que
  a tela some "ao sair do app ou perder a rede", contra os 5 min fora do
  primeiro plano de §0.
- **Opções:**
  - (a) **[RECOMENDADA]** reconectando ou sem internet: a tela fica
    congelada e esmaecida, com a hora da última atualização, só em
    memória; é descartada depois de 5 min fora do primeiro plano ou quando
    o processo morre; §0 "Offline" e X7 passam a dizer isso, e P3 ajusta
    PV2;
  - (b) descartar a tela na hora em que a rede cai, como X7 e PV2;
  - (c) descartar só depois de N segundos sem rede.
- **Por que (a):** nada é gravado em nenhum caso (ADR-0012 trata de
  persistência); apagar a tela a cada oscilação de 4G atrapalha o uso sem
  ganho de privacidade.
- **Origem:** `privacy.md` §15 PA1.
- **Precisa de decisão?** Sim.

### §8 Liberar escrita

**AJ-12 — Outro aparelho no controle (`busy`)**

- **Tela:** `android.md` §8 (Estados); `textos.md` (chave nova).
- **Problema:** `busy` não tem texto aprovado.
- **Proposta:** `arm.busy` = "{device} está no controle deste terminal
  até {time}."
- **Origem:** `trcp-1.md` §19.2 item 2.
- **Precisa de decisão?** Não.

### §10 Pedido de atenção

**AJ-13 — "O Claude continuou" afirma demais**

- **Tela:** `android.md` §10 (estados finais); `textos.md`
  `attn.done_allowed`.
- **Problema:** o `ok` garante que a decisão foi entregue ao adaptador,
  não que o Claude continuou.
- **Proposta:** `attn.done_allowed` = "Permitido. A resposta foi entregue
  ao Claude."
- **Origem:** `trcp-1.md` §19.2 item 24.
- **Precisa de decisão?** Não.

**AJ-14 — Pedidos sem opções: o que vai no rodapé**

- **Tela:** `android.md` §10 (Ações, fixas no rodapé).
- **Problema:** para `question`, `idle`, `finished` e `error` não há
  Permitir/Recusar, e a tela não diz o que aparece; o adaptador do MVP
  não responde perguntas do Claude Code.
- **Proposta:**
  - rodapé com **Abrir terminal** como botão primário, sem Permitir nem
    Recusar;
  - para `question`, a nota `attn.answer_in_terminal` = "A Pipa ainda
    não responde perguntas por aqui. Abra o terminal e responda lá."
- **Origem:** `trcp-1.md` §19.2 itens 7 e 23.
- **Precisa de decisão?** Não.

### §11 Notificações

**AJ-15 — Nome do PC na tela de bloqueio**

- **Tela:** `android.md` §11 (canal `pipa_attention`,
  `VISIBILITY_PUBLIC`).
- **Problema:** a notificação mostra o nome do PC com o celular bloqueado;
  o nome padrão é o hostname, que costuma ter o nome da pessoa
  ("LUCAS-PC").
- **Opções:**
  - (a) manter `VISIBILITY_PUBLIC` com o nome do PC;
  - (b) **[RECOMENDADA]** `VISIBILITY_PRIVATE` com versão pública
    `notif.attn_unknown` ("Algo pede sua atenção num computador"); o nome
    aparece depois de desbloquear;
  - (c) `VISIBILITY_SECRET`: nada na tela de bloqueio.
- **Por que (b):** o aviso continua visível e útil bloqueado, sem expor o
  nome; o texto já existe no catálogo.
- **Origem:** `privacy.md` §15 PA6.
- **Precisa de decisão?** Sim.

**AJ-16 — Notificação dos avisos de outros programas (EX1)**

- **Tela:** `android.md` §11.
- **Problema:** o único texto de notificação é `notif.attn` ("Algo pede
  sua atenção em {pc}"), que não descreve um alerta de consumo; mostrar o
  título do aviso muda tela e visibilidade.
- **Opções:**
  - (a) reusar `notif.attn`;
  - (b) **[RECOMENDADA]** texto opaco próprio, num canal próprio de
    importância padrão (a pessoa pode desligar só esse canal no
    Android):
    - `notif.notice` = "Novo aviso em {pc}";
    - `notif.channel_notices` = "Avisos de programas";
    - `notif.channel_notices_desc` = "Avisos curtos de programas do seu
      PC, como alertas de consumo.";
  - (c) mostrar o título do aviso, buscado pelo túnel (nunca pelo push),
    só com o celular desbloqueado.
- **Por que (b):** mantém o push opaco (ADR-0014) e separa o que é pedido
  do que é informação.
- **Origem:** `privacy.md` §15 PA13; EX1.
- **Precisa de decisão?** Sim.

### §12 Aparelhos e segurança

**AJ-17 — Textos de audit que faltam**

- **Tela:** `android.md` §12 (Atividade recente); `vscode.md` §7
  (Atividade recente); `textos.md` `audit.*`.
- **Problema:** faltam os textos das entradas `terminated` e `forgotten`.
- **Proposta:**
  - `audit.terminated` = "Encerrou {session}";
  - `audit.forgotten` = "Removeu o PC deste celular".
- **Origem:** `trcp-1.md` §19.2 item 8.
- **Precisa de decisão?** Não.

### §13 Configurações

**AJ-18 — Onde o servidor fica no app**

- **Tela:** `android.md` §13 (item "Ponte") e §12; `textos.md`
  `settings.bridge*`.
- **Problema:** as Configurações têm uma ponte só, global; mas cada PC
  guarda a própria (`{agent_id, agent_name, bridge, fingerprint}`,
  `android.md` §0), e sem ponte padrão PCs diferentes podem estar em
  servidores diferentes.
- **Opções:**
  - (a) **[RECOMENDADA]** sai o item "Ponte" das Configurações; o servidor
    de cada PC aparece no bloco do PC em "Aparelhos e segurança", com o
    estado (AJ-19); trocar de servidor = remover e adicionar o PC de
    novo, porque o pareamento é com aquele servidor;
  - (b) Configurações ganham "Servidor para novos computadores" e cada PC
    mostra o seu em "Aparelhos e segurança";
  - (c) manter como está.
- **Por que (a):** o campo de AJ-02 já cobre "novos computadores"; uma
  ponte global que não vale para os PCs já pareados confunde.
- **Textos de (a):** `devices.server` = "Servidor: {bridge}"; saem
  `settings.bridge`, `settings.bridge_ok`, `settings.bridge_err` e
  `settings.bridge_help` (o texto de ajuda vai para `add.server_help`).
- **Origem:** decisão de 2026-09-26; `privacy.md` §3.2 (preferência
  "ponte").
- **Precisa de decisão?** Sim.

**AJ-19 — Que número de latência mostrar**

- **Tela:** `android.md` §13 (ou §12, se AJ-18 for aprovado);
  `textos.md` `settings.bridge_ok`.
- **Problema:** "alcançável · {ms} ms" fala da **ponte**, mas o Ping/Pong
  da spec (R3.11) corre dentro do TLS e mede celular ↔ **PC**.
- **Opções:**
  - (a) **[RECOMENDADA]** mostrar o que se mede: no bloco do PC,
    `devices.pc_rtt` = "{pc} responde em {ms} ms"; o servidor mostra só
    "alcançável" / "sem resposta", sem ms;
  - (b) medir a ponte à parte, com um ping fora do túnel (P4 precisa
    prever);
  - (c) manter o texto e medir o PC (o número fica com o rótulo errado).
- **Por que (a):** não pede nada novo ao protocolo, e o tempo até o PC é
  o que a pessoa sente.
- **Origem:** `requisitos-nao-funcionais.md` §7 PA-2 (exigências E23).
- **Precisa de decisão?** Sim.

### §14 Estados globais

**AJ-20 — Autenticação recusada (4401) e parada depois de três falhas**

- **Tela:** `android.md` §14 (linha nova).
- **Problema:** o fechamento 4401 e a parada das tentativas depois de três
  falhas seguidas (R13.5) não têm tela nem texto.
- **Proposta:** tela cheia, sem nova tentativa automática:
  - `global.auth_failed_title` = "{pc} recusou este celular";
  - `global.auth_failed_body` = "O PC recusou a conexão três vezes
    seguidas. Isso não é problema de rede. Confira no VS Code se este
    celular ainda aparece em Aparelhos; se não aparecer, adicione de
    novo.";
  - ações: Tentar de novo; Adicionar de novo (`global.revoked_readd`).
- **Origem:** `trcp-1.md` §19.2 item 3 (R13.5).
- **Precisa de decisão?** Não.

**AJ-21 — Celular mais novo que o PC (4426)**

- **Tela:** `android.md` §14 (Versões incompatíveis).
- **Problema:** `global.outdated` só cobre o PC mais novo.
- **Proposta:** `global.outdated_pc` = "Atualize a extensão Pipa em {pc}:
  este celular usa uma versão mais nova do protocolo." Sem botão de loja.
- **Origem:** `trcp-1.md` §19.2 item 4 (R5.12).
- **Precisa de decisão?** Não.

**AJ-22 — Revogado, se P5 recusar no próprio TLS**

- **Tela:** `android.md` §14 (Aparelho revogado, `global.revoked_*`).
- **Problema:** a tela de revogado depende de o agente completar o TLS e
  mandar 4403 (D-21, R6.3); se P5 preferir recusar no próprio TLS, o
  celular não distingue revogação de falha de rede.
- **Opções (decisão de P5, não de Sr. Garioli):**
  - (a) **[RECOMENDADA pela spec, D-21]** completar o TLS e mandar 4403:
    a tela aprovada fica como está;
  - (b) recusar no TLS: a tela de revogado não aparece, e a de AJ-20
    passa a dizer também "pode ter sido removido no PC".
- **Origem:** `trcp-1.md` §19.2 item 10.
- **Precisa de decisão?** Sim (P5).

**AJ-23 — Reconectar na hora quando chega rede nova**

- **Tela:** `android.md` §14 (Reconectando).
- **Problema:** a tela fixa a espera em "1 a 30 s"; NFR-25 pede reconectar
  na hora quando o Android avisa que há rede nova.
- **Proposta:** na linha Reconectando, "espera de 1 a 30 s, que recomeça
  na hora quando o Android avisa rede nova". Texto `global.reconnecting`
  não muda. P3 confirma que a spec permite (§13.5).
- **Origem:** `requisitos-nao-funcionais.md` §7 PA-4.
- **Precisa de decisão?** Não.

**AJ-24 — Códigos de erro sem texto**

- **Tela:** `android.md` §7, §8 e §14; `textos.md` (chaves novas).
- **Problema:** `rate_limited`, `step_up_invalid` e `internal` não têm
  texto.
- **Proposta:**
  - `global.err_rate_limited` = "Muitos pedidos seguidos. Espere {s} s e
    tente de novo.";
  - `arm.err_step_up_invalid` = "A confirmação venceu. Confirme de
    novo.";
  - `global.err_internal` = "O PC teve um erro e nada foi feito. Tente de
    novo."
- **Origem:** `trcp-1.md` §19.2 item 30.
- **Precisa de decisão?** Não.

---

## B. Extensão VS Code (`vscode.md`)

**AJ-25 — `pipa.bridge` sem padrão e pedido do endereço na primeira vez**

- **Tela:** `vscode.md` §10 (`pipa.bridge`, padrão
  `ponte.gariolilabs.com`) e §4; `textos.md` `vsc.set_bridge`.
- **Problema:** não há ponte pública; o padrão atual levaria qualquer
  usuário a uma ponte privada que o recusa.
- **Proposta comum a todas as opções:**
  - `pipa.bridge` passa a ter padrão vazio; no uso de Sr. Garioli, o
    valor `ponte.gariolilabs.com` fica nas configurações de usuário dele;
  - `vsc.set_bridge` = "Endereço da ponte (servidor) usada para parear e
    conectar celulares. Não há servidor público: use o seu ou um que lhe
    foi autorizado.";
  - caixa de entrada com `vsc.bridge_prompt` = "Endereço do servidor da
    Pipa (ex.: ponte.seudominio.com)", `vsc.bridge_invalid` = "Endereço
    inválido. Use um nome como ponte.seudominio.com." e o link
    `vsc.bridge_howto` = "Como instalar um servidor".
- **Opções (quando pedir):**
  - (a) **[RECOMENDADA]** na primeira vez em que a pessoa roda "Conectar
    celular", antes de abrir o painel;
  - (b) logo depois de instalar a extensão, junto com a pergunta do perfil
    padrão;
  - (c) nunca perguntar: só a configuração e o aviso "Ponte fora" do
    painel.
- **Por que (a):** a ponte só importa para parear; perguntar na
  instalação pesa para quem ainda só usa o terminal local (M0–M5).
- **Origem:** decisão de 2026-09-26 (ADR-0004; ADR README item 5).
- **Precisa de decisão?** Sim.

**AJ-26 — Chave de inscrição da ponte**

- **Tela:** `vscode.md` §3 (menu rápido), §9 (comandos), §10.
- **Problema:** para registrar o PC numa ponte é preciso a chave de
  inscrição emitida por quem opera a ponte; nenhuma tela a pede.
- **Proposta:**
  - comando `pipa.setBridge`, `vsc.cmd_set_bridge` = "Configurar
    servidor", que pede o endereço (AJ-25) e depois a chave;
  - `vsc.enroll_prompt` = "Chave de inscrição do servidor {bridge}";
  - `vsc.enroll_help` = "Quem opera o servidor gera essa chave. Ela fica
    no cofre do sistema, não nas configurações.";
  - `vsc.enroll_invalid` = "O servidor recusou a chave. Peça uma nova a
    quem opera o servidor.";
  - a chave fica no `SecretStorage` da extensão ou no cofre do agente
    (DPAPI), nunca em `settings.json`.
- **Origem:** decisão de 2026-09-26; ADR README ponto em aberto 3.
- **Precisa de decisão?** Não. O formato da chave, a emissão e a
  revogação são de P4 (Fable); a tela segue o que P4 fechar.

**AJ-27 — Painel "Conectar celular" deixa claro o servidor**

- **Tela:** `vscode.md` §4 (conteúdo); `textos.md` `vsc.pair_step2`,
  `vsc.pair_bridge`.
- **Problema:** quem digita o código no celular precisa também do
  servidor, e o painel só mostra "Ponte: {bridge}" no rodapé.
- **Proposta:**
  - `vsc.pair_step2` = "Leia o QR. Se preferir digitar, informe o código
    e o servidor {bridge}.";
  - o servidor fica ao lado do código, na mesma fonte, com botão Copiar.
- **Origem:** decisão de 2026-09-26.
- **Precisa de decisão?** Não.

**AJ-28 — Notificação que oferece o perfil padrão**

- **Tela:** `vscode.md` §6; `textos.md` (chaves novas).
- **Problema:** `vscode.md` §6 descreve a notificação, mas não há textos;
  e §6 diz só "a extensão pergunta uma vez", sem o que acontece depois de
  um "não".
- **Proposta:**
  - `vsc.default_profile_offer` = "Usar o Terminal remoto (Pipa) como
    padrão nos novos terminais? Só os terminais desse perfil aparecem no
    celular.";
  - `vsc.default_profile_accept` = "Usar como padrão";
  - `vsc.default_profile_decline` = "Não";
  - em §6: "Depois de um não, a extensão não pergunta de novo e aponta o
    comando Usar o Terminal remoto como padrão (AJ-29)."
- **Origem:** ADR README, ajustes do item 1 (ADR-0002).
- **Precisa de decisão?** Não.

**AJ-29 — Comando "Usar o Terminal remoto como padrão"**

- **Tela:** `vscode.md` §9; `textos.md` (chave nova).
- **Problema:** a lista de comandos não tem o comando decidido.
- **Proposta:** comando `pipa.useAsDefault`, `vsc.cmd_use_as_default` =
  "Usar o Terminal remoto como padrão".
- **Origem:** ADR README, ajustes do item 1 (ADR-0002).
- **Precisa de decisão?** Não.

**AJ-30 — Renomear o PC**

- **Tela:** `vscode.md` §7 (nó "Este computador") e §9.
- **Problema:** Q11 decidiu "hostname, editável" e o protocolo tem
  `agent.rename`, mas não há comando nem configuração.
- **Proposta:**
  - comando `pipa.renamePc`, `vsc.cmd_rename_pc` = "Renomear este
    computador", também no menu do nó "Este computador";
  - `vsc.rename_prompt` = "Nome deste computador no celular";
  - `vsc.rename_help` = "Evite o seu nome completo: ele pode aparecer nas
    notificações." (ver AJ-15).
- **Origem:** `trcp-1.md` §19.2 item 6; interfaces Q11.
- **Precisa de decisão?** Não.

**AJ-31 — Tirar `pipa.audit.input` do MVP**

- **Tela:** `vscode.md` §10; `textos.md` `vsc.set_audit_input`.
- **Problema:** a opção grava o texto digitado no PC, contra ADR-0012 e
  contra `devices.audit_note` ("O texto digitado não é registrado").
- **Proposta:** sai a linha `pipa.audit.input` de §10 e a chave
  `vsc.set_audit_input`; `devices.audit_note` fica como está (passa a ser
  verdade sem exceção).
- **Origem:** `privacy.md` §14 DP3, **decidida por Sr. Garioli em
  2026-09-26: opção (a)**; `trcp-1.md` §19.2 item 31.
- **Precisa de decisão?** Não.

**AJ-32 — Autorizar um programa a mandar avisos (EX1)**

- **Tela:** `vscode.md` §7 (árvore) e §11; `textos.md` (chaves novas).
- **Problema:** se P5 decidir que o agente guarda uma lista de origens
  autorizadas, a pessoa precisa aprovar cada programa novo; nenhuma tela
  faz isso.
- **Opções (depende de P5):**
  - (a) **[RECOMENDADA, se P5 adotar a lista]** na primeira chamada de um
    programa novo, notificação `vsc.notice_origin_ask` = "{origem} quer
    mandar avisos para os seus celulares. Permitir?", com Permitir /
    Recusar, e o nó "Origens de aviso" na árvore, com Remover;
  - (b) autorização só por arquivo de configuração, sem tela;
  - (c) sem lista (qualquer processo local pode mandar), se P5 aceitar.
- **Origem:** `privacy.md` §15 PA14; EX1 ("autenticação de quem
  chama").
- **Precisa de decisão?** Sim (P5).

---

## C. Textos em várias telas (`textos.md`)

**AJ-33 — "Biometria" ou "biometria ou PIN"**

- **Tela:** `textos.md` `welcome.body`, `welcome.security_4`,
  `pair.success_body`, `vsc.allow_detail`, `vsc.set_write`; botão
  "Liberar com biometria" (`android.md` §8) e "Permitir com biometria"
  (§10).
- **Problema:** liberar escrita aceita PIN ou padrão do aparelho
  (ADR-0003), mas os textos falam só de biometria.
- **Opções:**
  - (a) **[RECOMENDADA]** "biometria ou PIN" nos textos explicativos e nos
    botões ("Liberar com biometria ou PIN");
  - (b) "desbloqueio do aparelho" em todos;
  - (c) manter "biometria"; o `BiometricPrompt` já oferece "Usar PIN".
- **Por que (a):** quem não tem biometria cadastrada, só PIN, entende que
  pode usar a Pipa; "desbloqueio do aparelho" é preciso, mas menos claro.
- **Origem:** ADR README, ajustes do item 3.
- **Precisa de decisão?** Sim.

**AJ-34 — "Ponte" ou "Servidor" nas telas**

- **Tela:** `textos.md` (todas as chaves com "ponte": `pair.connecting`,
  `pair.err_bridge_*`, `global.bridge_down`, `vsc.pair_bridge*`,
  `vsc.set_bridge`, `welcome.security_1`); glossário do `README.md`.
- **Problema:** as telas dizem "ponte"; agora a pessoa instala e digita o
  endereço desse servidor, e Sr. Garioli o chama de "servidor".
- **Opções:**
  - (a) **[RECOMENDADA]** "servidor" em todas as telas; "ponte" e
    `trc-bridge` ficam nos documentos técnicos e no glossário ("Servidor
    (ponte)");
  - (b) manter "ponte" nas telas e usar "Ponte" também no campo novo;
  - (c) "servidor" só no campo novo e nas instruções; "ponte" no resto.
- **Por que (a):** um termo só, e o que a pessoa conhece quando instala
  um programa num VPS ou num Raspberry.
- **Origem:** decisão de 2026-09-26 (texto de Sr. Garioli: "Servidor só
  pra mim…").
- **Precisa de decisão?** Sim.

---

## D. Fluxos (`fluxos.md`)

**AJ-35 — F1 e X6 com o servidor e a chave**

- **Tela:** `fluxos.md` F1 (passos 1, 3 e 4, e o diagrama) e X6.
- **Problema:** F1 supõe a ponte padrão; não há o passo de configurar o
  servidor nem de digitar o servidor no celular.
- **Proposta:**
  - F1 passo 1: "…a extensão pede o servidor e a chave de inscrição na
    primeira vez que a pessoa roda Conectar celular (AJ-25, AJ-26); no uso
    de Sr. Garioli, já vêm configurados";
  - F1 passo 4: "lê o QR (o servidor vem junto) ou digita o servidor e os
    12 dígitos";
  - X6: "Servidor fora do ar ou endereço errado" → "cartão com o
    endereço; conferir o servidor no campo".
- **Origem:** decisão de 2026-09-26.
- **Precisa de decisão?** Não.

---

## E. Visão (`visao.md`)

**AJ-36 — "O que faz" e "O que não faz"**

- **Tela:** `visao.md` "O que faz" e "O que não faz (no MVP)".
- **Problema:** "Mostra no celular todos os terminais abertos no VS Code"
  é falso depois de um "não" ao perfil padrão; e a visão não diz que não
  há servidor público.
- **Proposta:**
  - "Mostra no celular os terminais abertos pelo perfil Terminal remoto
    (o padrão, se você aceitar), com estado e contexto mínimo.";
  - em "O que não faz": "Não oferece servidor público: cada pessoa usa a
    própria ponte (servidor, VPS ou Raspberry); a da Garioli Labs é
    privada."
- **Origem:** ADR README, ajustes do item 1; decisão de 2026-09-26.
- **Precisa de decisão?** Não.

---

## Itens das fontes que não geram ajuste

- `trcp-1.md` §19.2 item 1 (envio com `stale` enquanto o Claude Code
  trabalha): `requisitos-nao-funcionais.md` DP-6 foi **decidida** por Sr.
  Garioli em 2026-09-26, opção A (aceitar no MVP e medir); nenhuma tela
  muda agora.
- ADR README, item 2 (push FCM opaco): as telas já tratam push opaco
  (`notif.*`).
- `privacy.md` PA1 entra aqui só pela parte de tela (AJ-11); o ajuste de
  PV2 na spec é de P3.
