# Interfaces da extensão VS Code (P7)

Status: rascunho de planejamento, 2026-09-26.

## Regras deste documento

- **Só API estável.** Cada superfície cita a API e a linha do `vscode.d.ts`
  estável conferido. O arquivo foi baixado do branch `main` de
  microsoft/vscode em 2026-09-26 e não tem nenhum `@proposed`. As
  contribuições do `package.json` foram conferidas na página
  "Contribution Points" da documentação oficial (vscode-docs).
- **Nada de sobreposição inventada no terminal.** Não há decoração, banner
  nem overlay desenhado dentro do terminal: escrever faixas pelo
  `onDidWrite` corromperia TUIs como o Claude Code. O estado remoto aparece
  em quatro lugares:
  - no **nome** da aba;
  - no **ícone** da aba;
  - na **barra de status**;
  - na **árvore** do painel.
- **Tema:**
  - A UI nativa (barra de status, QuickPick, modal, árvore, notificações)
    herda o tema do editor automaticamente.
  - A única webview, o painel "Conectar celular", usa só variáveis
    `--vscode-*`.
  - A extensão não define cor própria, exceto o `ThemeColor` do ícone da aba,
    que também é do tema.
- **Textos** vêm de `textos.md`, com as chaves `vsc.*`:
  - em código, por `vscode.l10n.t`;
  - no manifesto, por `package.nls.json` / `package.nls.pt-br.json`.

O protótipo simula tudo isso na coluna "VS Code" (`prototipo/index.html`).
Atalhos: `#vs_pair`, `#vs_modal`, `#vs_armed`, `#vs_menu`, `#vs_tree`,
`#vs_revoke`, `#vs_cut`, `#vs_agent_off`.

## 1. Glifo da Pipa

- **Propósito:** reconhecer a Pipa em 16 px no meio dos codicons.
- **API:**
  - `contributes.icons` com uma fonte `.woff` própria com dois glifos:
    - `pipa`: losango cheio (16 px);
    - `pipa-outline`: losango vazado + `>` (24 px).
  - O glifo vira `$(pipa)` em textos que aceitam ícone e
    `new ThemeIcon('pipa')` (`vscode.d.ts` 940).
  - Para o container do painel, `viewsContainers.panel[].icon` aponta para
    `media/pipa-24.svg`, monocromático, 24 × 24, como a documentação pede.
- **Estado:** a cor sempre vem do tema (`currentColor`).

## 2. Item da barra de status

**API:**

- `window.createStatusBarItem('pipa.status', StatusBarAlignment.Right, 100)`
  (11641).
- `backgroundColor = new ThemeColor('statusBarItem.warningBackground')`
  (7622). O `vscode.d.ts` só aceita as cores `errorBackground` e
  `warningBackground`.
- `accessibilityInformation` (7637), `command = 'pipa.menu'`.
- `tooltip` é um `MarkdownString` com `supportThemeIcons` (3030).

**Propósito:** mostrar de relance se algum celular vê ou controla este PC. É a
heurística H1 de Nielsen, visibilidade do estado do sistema.

| Estado | Texto | Fundo | Tooltip (`textos.md`) |
|---|---|---|---|
| Agente ligado, nenhum celular | `$(pipa) Pipa` | padrão | `vsc.status_tooltip` |
| 1 celular conectado (só leitura) | `$(pipa) Pipa · 1 celular` | padrão | `vsc.status_tooltip` |
| N celulares | `$(pipa) Pipa · {n} celulares` | padrão | idem |
| **Escrita liberada** | `$(pipa) Pixel 8 no controle` | **warning** | `vsc.status_armed_tooltip` (sessão e horário de fim) |
| Pareamento esperando resposta | `$(pipa) Confirmar Pixel 8` | warning | abre o modal de novo |
| Acesso cortado | `$(circle-slash) Acesso remoto cortado` | padrão | `vsc.status_cut_tooltip` |
| Agente parado | `$(pipa) Pipa parada` | warning | `vsc.status_agent_off_tooltip`; o clique inicia o agente |

- O fundo "warning" fica reservado para os dois estados em que alguém de fora
  **pode agir** ou **espera resposta**. Assim ele não vira ruído.
- Leitor de tela: `accessibilityInformation.label` repete o texto por
  extenso ("Pipa: Pixel 8 pode digitar no terminal Claude Code até 14:37").
  Sem isso, o leitor lê o glifo.

## 3. Menu rápido (clique na barra de status)

**API:** `window.createQuickPick` (11502), com itens `QuickPickItem` com
`iconPath`/`$(…)` e `detail`.

**Itens, em ordem por estado:**

1. `$(unlock)` Retirar escrita de {device}: só quando há escrita liberada.
2. `$(device-mobile)` Conectar celular.
3. `$(shield)` Mostrar aparelhos: foca a árvore.
4. `$(circle-slash)` Cortar acesso remoto, com `detail` = `vsc.cmd_cut_detail`.
   Quando está cortado, o item vira `$(debug-restart)` Reativar acesso remoto.
5. `$(server)` Configurar servidor (`vsc.cmd_set_bridge`, AJ-26): pede o
   endereço e depois a chave de inscrição.
6. `$(gear)` Abrir configurações da Pipa.

**Kill switch sem confirmação, com desfazer.** Cortar é seguro e reversível:
ninguém perde trabalho. A notificação que aparece oferece o botão
**Reativar**. É o padrão "desfazer é melhor que confirmar": um diálogo
"tem certeza?" atrasaria justamente a ação de emergência.

## 4. Painel "Conectar celular" (webview)

**API:**

- `window.createWebviewPanel('pipa.pair', l10n.t('Conectar celular'), ViewColumn.Active, { enableScripts: true, localResourceRoots: [media] })`
  (11547).
- CSP restrita: `default-src 'none'; img-src ${webview.cspSource} data:; style-src ${webview.cspSource}; script-src 'nonce-…'`.
- O QR é gerado **na extensão**, sem rede, como SVG inline.
- A comunicação é só por `postMessage`.
- `retainContextWhenHidden` desligado: o código é regenerado se o painel
  voltar.

**Antes de abrir** (AJ-25, opção a): na primeira vez em que a pessoa roda
Conectar celular, sem `pipa.bridge` configurado, a extensão pede o servidor
numa `window.showInputBox` (`vsc.bridge_prompt`; validação
`vsc.bridge_invalid`; link `vsc.bridge_howto`) e, em seguida, a chave de
inscrição (AJ-26, `vsc.enroll_prompt`, `vsc.enroll_help`,
`vsc.enroll_invalid`). Só então abre o painel. A ponte só importa para
parear: perguntar na instalação pesaria para quem ainda só usa o terminal
local. No uso de Sr. Garioli, os dois já estão configurados.

**Por que webview:** a UI nativa não mostra QR nem um código de 12 dígitos
grande. É a única webview do produto.

**Conteúdo:**

- três passos numerados;
- o código `4821 · 9137 2055` em fonte do editor, 30 px, com dígitos
  tabulares;
- junto do código, na mesma fonte, o **servidor** (`vsc.pair_server_label`)
  com o botão **Copiar** (`vsc.pair_copy`, `vsc.pair_copied`): quem digita
  no celular precisa dos dois (AJ-27, `vsc.pair_step2`);
- o QR (150 px, fundo branco fixo, porque QR precisa de contraste
  claro/escuro verdadeiro);
- "Vale por 4:59 · uso único";
- botões Ocultar código e Gerar novo código;
- a faixa de estado;
- sem código na tela (expirou, errado, recusado), o rodapé mostra o
  servidor (`vsc.pair_bridge`).

**Estados:**

| Estado | Faixa (`role="status"`) | Ação |
|---|---|---|
| Aguardando | `vsc.pair_waiting` | contagem regressiva de 5 min |
| Celular leu o código | `vsc.pair_confirming` | abre o modal (§5) |
| Concluído | `vsc.pair_success` | o painel pode fechar |
| Expirou | `vsc.pair_expired` | o código some; botão Gerar novo |
| Código errado | `vsc.pair_wrong` | o código é invalidado; botão Gerar novo |
| Recusado | `vsc.pair_rejected` | botão Gerar novo |
| Servidor fora | `vsc.pair_bridge_down` | botão Gerar novo; link para a configuração |

**Ocultar código:** troca os dígitos por `•••• · •••• ••••` e esconde o QR.
Serve para quem compartilha a tela numa chamada.

**Acessibilidade:**

- a contagem regressiva **não** é anunciada a cada segundo (`aria-live="off"`);
- mudanças de estado são anunciadas (`role="status"`);
- tempo fixo de 5 min, mas renovável sem perda (WCAG 2.2.1, "extend").

**Cores:** só `var(--vscode-foreground)`, `--vscode-descriptionForeground`,
`--vscode-button-*`, `--vscode-focusBorder`,
`--vscode-editorWidget-background`,
`--vscode-statusBarItem-warningBackground` e `--vscode-editor-font-family`.

## 5. Modal "Permitir aparelho?"

**API:**

- `window.showWarningMessage(l10n.t('Permitir “{0}” neste computador?', name), { modal: true, detail }, permitir, recusar)`
  (11342; `modal` 2182; `detail` 2188).
- `recusar` é um `MessageItem` com `isCloseAffordance: true` (2167). Assim, Esc
  ou fechar a janela **equivale a Recusar**, e o VS Code não cria um
  "Cancelar" extra.

**Propósito:** o PC dá a palavra final sobre quem entra. Isso cobre o caso de
alguém que fotografou o código.

**Conteúdo:** `vsc.allow_title` + `vsc.allow_detail`. O detalhe traz:

- o **código de confirmação** `482 913`, para comparar com o celular;
- o que o aparelho poderá fazer: ver em só leitura, escrever só com
  biometria ou PIN.

**Ações:**

- Permitir: pareia.
- Recusar / Esc: o celular vê `pair.err_rejected_*`.
- Sem resposta em 60 s: o celular vê `pair.err_timeout_*` e o painel oferece
  novo código.

**Por que modal:** é uma decisão de segurança, rara e com consequência. O
modal é o único controle nativo que exige resposta. A mesma regra deixa todo
o resto sem modal.

## 6. Terminal remoto: perfil, aba e estado

**API:**

- `contributes.terminal.profiles`:
  `[{ id: 'pipa.remote', title: '%vsc.term_profile%', icon: '$(pipa)' }]`.
- `window.registerTerminalProfileProvider('pipa.remote', provider)` (11828),
  que devolve `new TerminalProfile({ name, pty, iconPath: new ThemeIcon('pipa'), color: new ThemeColor('terminal.ansiYellow'), isTransient: true })`
  (8235, 8245; `ExtensionTerminalOptions` 12560; `iconPath`/`color` 12575–12582;
  `isTransient` 12593).
- O `Pseudoterminal` (12690–12770) é a view do PTY que vive no agente:
  - `onDidWrite` recebe a saída;
  - `handleInput` manda o teclado local;
  - `setDimensions` informa o tamanho;
  - `onDidClose` informa o fim;
  - `onDidChangeName` troca o nome da aba.

**Estado na aba:**

- **Ícone e cor fixos.** O glifo da Pipa em `terminal.ansiYellow` marca
  "este terminal é visível pelo celular". A cor só pode ser definida na
  criação; o `vscode.d.ts` não tem API para mudá-la depois. Por isso ela
  marca a *capacidade*, não o estado.
- **O nome muda com o estado.**
  - Normal: `Claude Code`.
  - Com escrita liberada: `Claude Code · Pixel 8 no controle`
    (`vsc.term_name_armed`), via `onDidChangeName`.
  - Ao desarmar, volta ao nome normal.
- **Barra de status**, atualizada também em `window.onDidChangeActiveTerminal`
  (11177). Quando o terminal ativo está com escrita liberada, o item mostra o
  estado warning (§2).
- **Notificação** ao liberar escrita:
  - `window.showInformationMessage(l10n.t('Pixel 8 liberou a escrita em “Claude Code” por 5 min.'), l10n.t('Retirar escrita'))`,
    sem modal;
  - é desligável pela configuração `pipa.notify.onArm`, ligada por padrão
    (pergunta Q9).

**Perfil padrão:** a visão pede que novos terminais nasçam no perfil remoto.
O caminho estável é a configuração do usuário
`terminal.integrated.defaultProfile.windows`. A extensão **pergunta uma vez**
e só grava com consentimento (AJ-28):

- notificação `vsc.default_profile_offer`, com os botões
  `vsc.default_profile_accept` ("Usar como padrão") e
  `vsc.default_profile_decline` ("Não");
- depois de um não, a extensão não pergunta de novo e aponta o comando
  **Usar o Terminal remoto como padrão** (`pipa.useAsDefault`, §9, AJ-29);
  o celular mostra o vazio próprio (`sessions.empty_body_not_default`,
  `android.md` §6).

Ver os itens não verificados.

## 7. Painel "Pipa" (árvore)

**API:**

- `contributes.viewsContainers.panel: [{ id: 'pipa', title: 'Pipa', icon: 'media/pipa-24.svg' }]`.
- `contributes.views.pipa: [{ id: 'pipa.devices', name: '%vsc.tree_title%' }]`.
- `window.createTreeView('pipa.devices', { treeDataProvider, showCollapseAll: false })`
  (11703; 11862).
- `TreeView.badge: ViewBadge` (12118, 12203) com o número de aparelhos com
  escrita liberada, para aparecer mesmo com o painel fechado.
- `TreeItem.contextValue` (12374) e `accessibilityInformation` (12381).
- `contributes.menus`:
  - `view/title`: Conectar celular (`$(add)`), Cortar/Reativar
    (`$(circle-slash)` / `$(debug-restart)`);
  - `view/item/context` com `group: 'inline'`: Revogar (`$(trash)`) quando
    `viewItem == device`, e Retirar escrita (`$(lock)`) quando
    `viewItem == session.armed`;
  - `view/item/context` no nó `viewItem == thisPc`: Renomear este
    computador (`pipa.renamePc`, AJ-30).
- `contributes.viewsWelcome` para `pipa.devices` quando não há aparelhos:
  `vsc.tree_welcome_text` + `[Conectar celular](command:pipa.pair)`.

**Estrutura:**

- Este computador · LUCAS-PC — `agente ligado` | `acesso cortado` [renomear]
- Aparelhos
  - Pixel 8 — `conectado agora` [revogar]
  - Galaxy Tab S9 — `visto há 3 dias` [revogar]
- Terminais remotos
  - Claude Code — `Pixel 8 no controle até 14:37` [retirar escrita]
  - Backend — `só leitura`
- Atividade recente, com as últimas 10 do audit, só metadados:
  - 14:31 Pixel 8 · Permitiu um pedido em Claude Code

**Por que painel e não barra lateral:** o painel fica ao lado da aba
Terminal, onde está a atenção de quem usa terminais remotos. Não disputa
espaço com o Explorer.

## 8. Revogar aparelho

**API:** `window.showWarningMessage(title, { modal: true, detail }, revogar)`,
com "Cancelar" automático.

- **Texto:** `vsc.revoke_title` ("Revogar “Pixel 8”?") + `vsc.revoke_detail`.
  O título **nomeia o aparelho**. Uma confirmação genérica ("Tem certeza?")
  seria respondida no reflexo.
- **Depois:** notificação `vsc.revoked_toast`. O celular recebe 4403 e mostra
  a tela "Este celular foi removido".
- **Por que confirmar aqui e não no corte:** revogar é **irreversível** para
  aquele aparelho (exige novo pareamento). Cortar é reversível com um clique.

## 9. Comandos (paleta)

`contributes.commands`, todos com `category: "Pipa"`:

- `pipa.pair`: Conectar celular;
- `pipa.menu`;
- `pipa.showDevices`;
- `pipa.cut`: Cortar acesso remoto;
- `pipa.restore`;
- `pipa.disarm`: Retirar escrita;
- `pipa.revoke`;
- `pipa.startAgent`;
- `pipa.setBridge`: Configurar servidor (`vsc.cmd_set_bridge`, AJ-26);
- `pipa.useAsDefault`: Usar o Terminal remoto como padrão
  (`vsc.cmd_use_as_default`, AJ-29);
- `pipa.renamePc`: Renomear este computador (`vsc.cmd_rename_pc`, AJ-30),
  com `window.showInputBox` (`vsc.rename_prompt`, `vsc.rename_help`); o
  agente aplica `agent.rename`;
- `pipa.openSettings`.

`pipa.restore` e `pipa.disarm` só aparecem quando fazem sentido
(`enablement` / `when` com chaves de contexto setadas por
`commands.executeCommand('setContext', …)`, 11023).

## 10. Configurações

`contributes.configuration`, com as descrições em `textos.md` (`vsc.set_*`):

| Chave | Tipo, padrão | Observação |
|---|---|---|
| `pipa.bridge` | string, vazio | escopo `machine`, para o workspace não mudar o servidor. Não há servidor público: fica vazio até a pessoa informar (AJ-25, §4); no uso de Sr. Garioli, `ponte.gariolilabs.com` fica nas configurações de usuário dele |
| `pipa.write.enabled` | boolean, `true` | escopo `machine`; desligado = celular só lê (`arm.policy_off`) |
| `pipa.write.maxMinutes` | number, `15`, enum 1/5/15 | teto das opções do celular |
| `pipa.notify.onArm` | boolean, `true` | notificação da §6 |

- **Escopo `machine`.** Uma pasta clonada não pode trazer um
  `.vscode/settings.json` que ligue a escrita ou troque a ponte.
- **Chave de inscrição** (AJ-26): nunca em `settings.json`; fica no
  `SecretStorage` da extensão ou no cofre do agente (DPAPI). O formato, a
  emissão e a revogação são de P4 (Fable); a tela segue o que P4 fechar.
- **Sem `pipa.audit.input`** (AJ-31; `privacy.md` §14 DP3, opção a): o texto
  digitado nunca é registrado, e `devices.audit_note` vale sem exceção.

## 11. Estados globais no VS Code

| Situação | Onde aparece |
|---|---|
| Agente parado | barra de status em warning "Pipa parada"; no painel, a lista de terminais mostra o texto e o botão Iniciar agente; terminais remotos não abrem |
| Servidor fora | faixa no painel de pareamento; tooltip da barra de status; nada bloqueia o uso local |
| Acesso cortado | barra de status `$(circle-slash)`; nó raiz da árvore; notificação com Reativar |
| Celular com escrita liberada | aba renomeada, barra warning, badge na árvore, notificação |

## 12. Itens não verificados (precisam de prova na implementação)

1. **Valor da configuração de perfil padrão para perfil de extensão.** O nome
   exato a gravar em `terminal.integrated.defaultProfile.windows` quando o
   perfil vem de `contributes.terminal.profiles` não foi confirmado. Na UI
   ele aparece pelo `title`. Testar no M1.
2. **Foco padrão do modal.** Não está documentado qual botão recebe o foco
   no `showWarningMessage` modal. O risco: Enter aceitar "Permitir" sem
   leitura. Mitigação já no desenho: o código de confirmação obriga a olhar
   o celular. Se o foco cair em Permitir, avaliar inverter a ordem.
3. **Modal com a janela do VS Code sem foco** (pessoa longe do PC). Não
   verificado se o Windows pisca a barra de tarefas. O celular mostra "Confira
   no PC", e o prazo de 60 s cobre a ida até o PC.
4. **`$(pipa)` em `QuickPickItem.label` e em `MarkdownString`** com ícone de
   fonte contribuída. A documentação diz que funciona em "labels que suportam
   ícones"; confirmar na barra de status e no tooltip.
5. **Contraste do `terminal.ansiYellow` no tema claro padrão (Light Modern)**,
   usado no ícone da aba. Depende do tema do usuário; não é controlável pela
   extensão.
