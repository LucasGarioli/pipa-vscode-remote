# Identidade visual da Pipa (P7)

Status: rascunho de planejamento, 2026-09-26. Fonte da marca:
`docs/marca/pipa-conceitos-de-logo.html` (conceito **A, "Pipa"**, escolhido
por Sr. Garioli em 2026-09-26). Os tokens abaixo são os que o protótipo usa
(`prototipo/index.html`) e os que o app Android deve implementar.

## 1. Ideia: "estilo terminal", sem imitar o VS Code

- **Base sóbria de papel e tinta.** Papel `#F4F1EA` no claro, tinta `#11141A`
  no escuro. Não é branco nem preto puros: isso reduz o brilho e o halo no OLED.
- **Âmbar de fósforo `#F2A93B`** é a única cor de marca. Ele lembra monitor de
  fósforo e o cursor piscando.
- **O âmbar tem um significado só: "a Pipa quer sua atenção".** Aparece na
  faixa de pedido pendente, no chip "aguardando permissão", no aviso fixado no
  terminal e na marca. Botão primário **não** é âmbar: é tinta sobre papel (ou
  papel sobre tinta no escuro). Assim o âmbar continua saltando aos olhos
  quando um pedido chega. É a regra "cor significa uma coisa só"
  (Nielsen H4, consistência e padrões).
- **Três estados com cor própria:**
  - âmbar para atenção;
  - magenta para **escrita liberada**, o único estado em que o celular manda
    no PC;
  - vermelho para destrutivo ou erro.

  O magenta foi escolhido por não colidir com nenhuma convenção de sucesso ou
  erro: "você está no controle" precisa ser inconfundível.
- **Cor nunca é o único sinal** (WCAG 1.4.1). Todo estado tem também ícone e
  texto: cadeado para só leitura, cadeado aberto para escrita, sino para
  pedido, X para falha.
- **Monoespaçada onde o dado é de terminal:**
  - nomes de PC;
  - comandos;
  - caminhos;
  - saída do terminal;
  - código de pareamento;
  - status técnico ("exit 1").

  A interface em volta usa sans. A mistura é a assinatura visual: a tela diz o
  que é dado cru e o que é interface.

## 2. Marca: conceito A em cada tamanho

| Uso | Forma | Cor |
|---|---|---|
| Logo cheio (boas-vindas, "sobre", loja) | pipa em losango âmbar com `>_` em tinta dentro, varetas a 35 %, rabiola com dois laços | losango `#F2A93B`, prompt `#11141A`; rabiola: tinta no claro, âmbar no escuro |
| Ícone do app Android (adaptive icon) | quadrado tinta `#11141A`, raio 26/112, pipa âmbar com `>_` | fundo tinta, pipa âmbar, prompt tinta |
| Glifo 24 px (barra de atividade, container de painel, cabeçalhos) | losango **vazado** + chevron `>`, traço 5/64 | uma cor (`currentColor`) |
| Glifo 16 px (barra de status, aba do terminal, itens da árvore, notificação) | **só o losango cheio** | uma cor (`currentColor`) |
| Ícone pequeno de notificação Android (`smallIcon`) | losango cheio, branco sobre transparente | o sistema tinge |

O glifo de 16 px perde o `>` de propósito: em 16 px, um chevron de 2 px de
traço vira ruído. O losango sozinho continua reconhecível ao lado dos
codicons. Aplicação no VS Code:

- o glifo entra por `contributes.icons` (fonte `.woff` com os dois glifos);
- é usado como `$(pipa)` na barra de status e como `ThemeIcon('pipa')` na aba
  do terminal;
- o container do painel (`viewsContainers.panel`) usa o SVG de 24 px.

Ver `vscode.md` §1.

**Contraste da marca:**

- A marca é logotipo, e o WCAG isenta logotipos do 1.4.3 e do 1.4.11. Mesmo
  assim, o âmbar sobre papel mede **1,77:1**. Por isso:
  - a pipa colorida **nunca** aparece sozinha sobre papel em tamanho pequeno
    (abaixo de 24 px usa-se o glifo monocromático em tinta);
  - a palavra "pipa" em texto é sempre tinta ou papel, nunca âmbar sobre
    papel.
- No tema claro, o âmbar para texto é `#8A5300`:
  - 5,61:1 sobre papel;
  - 6,11:1 sobre `surface`.

## 3. Tokens de cor

Nomes semânticos (papel), não descritivos. O Android mapeia cada um para um
papel do Material 3 (§4). Onde um papel do M3 não existe (armed, attn), o token
é uma extensão do tema (`PipaColors` via `CompositionLocal`).

| Token | Claro | Escuro | Uso |
|---|---|---|---|
| `bg` | `#F4F1EA` | `#11141A` | fundo das telas |
| `surface` | `#FCFBF7` | `#191D25` | cartões, folhas, diálogos, campos |
| `surface2` | `#E9E5DC` | `#232833` | chips neutros, faixa "só leitura", campo desabilitado |
| `term` | `#FFFDF8` | `#0C0E12` | fundo da tela do terminal |
| `ink` | `#11141A` | `#ECE8DF` | texto principal |
| `ink2` | `#3D434F` | `#A3AAB8` | texto secundário |
| `ink3` | `#595F6A` | `#8A91A0` | placeholder, metadados |
| `line` | `#D6D0C4` | `#2C323D` | divisórias **decorativas** (não delimitam controle) |
| `lineStrong` | `#857E70` | `#6E7684` | borda de campo e de botão secundário (1.4.11) |
| `primary` / `onPrimary` | `#11141A` / `#F4F1EA` | `#ECE8DF` / `#11141A` | botão principal |
| `accent` / `onAccent` | `#F2A93B` / `#11141A` | `#F2A93B` / `#11141A` | faixa de pedido pendente, marca |
| `accentText` | `#8A5300` | `#F2A93B` | link, botão de texto, histórico |
| `accentSurface` | `#FBE8C4` | `#3A2C12` | chip e nota de atenção |
| `focus` | `#8A5300` | `#F2A93B` | anel de foco 2 px |
| `ok` / `okSurface` | `#1C6B3B` / `#DCEFE2` | `#6CCB91` / `#132D1F` | online, sucesso |
| `attn` / `attnSurface` | `#8A5300` / `#FBE8C4` | `#F2A93B` / `#3A2C12` | chip "aguardando permissão" |
| `attnStrong` | `#B06C00` | `#F2A93B` | ícone de atenção (não texto) |
| `armed` / `onArmed` | `#86277D` / `#FFFFFF` | `#E48ADB` / `#2A0827` | faixa e botão "escrita liberada" |
| `armedSurface` | `#F4E0F0` | `#37163A` | chip "escrita · 4:12" |
| `danger` / `onDanger` | `#B0251C` / `#FFFFFF` | `#FF8A7D` / `#3A0803` | destrutivo, erro, Ctrl+C |
| `dangerSurface` | `#F8E1DC` | `#3B1511` | cartão de erro |
| `offline` | `#595F6A` | `#8A91A0` | PC offline, acesso cortado |

**Ajustes feitos em relação à paleta da marca:**

- Nenhum dos quatro valores da marca foi alterado.
- O âmbar `#F2A93B` reprova como texto sobre papel (1,77:1). No claro, então,
  todo texto e ícone "âmbar" usa `#8A5300` (`accentText`, `attn`, `focus`).
  `#F2A93B` fica restrito a:
  - superfícies com texto tinta por cima (9,23:1);
  - a marca.
- `attnStrong` `#B06C00` mede 4,06:1 sobre `surface`: serve só para ícone
  (mínimo de 3:1), nunca para texto.

### Paleta ANSI do terminal (16 cores)

O terminal remoto desenha spans `{fg, bg, attr}` vindos do PC. As cores ANSI
são remapeadas para uma paleta própria que passa 4,5:1 sobre `term` nos dois
temas.

**Claro:**

`#1B2326 #B3261E #1C6E3D #7A5A00 #1F58B5 #8A2A80 #0A6A73 #4A575C #5F6C71 #A1261D #1A6A3A #735400 #1C51A8 #7D2574 #07606A #162024`

**Escuro:**

`#A7B3B8 #FF8A7D #6CCB91 #EDBE4C #7FB0FF #E48ADB #5FC4CD #C9D2D5 #8A979C #FFA69B #8BDDAA #F6D27A #A3C6FF #EFA8E8 #86D6DD #F2F6F7`

**Regras para as cores ANSI:**

- As cores 0 (preto) e 7/15 (branco) são trocadas entre os temas, para não
  sumirem no fundo.
- Cor RGB explícita (24 bits) vinda do PC é mostrada como veio, **exceto**
  quando a razão contra `term` ficar abaixo de 3:1. Nesse caso o app clareia ou
  escurece em passos de 5 % até passar. É a mesma ideia do
  `terminal.integrated.minimumContrastRatio` do VS Code.

## 4. Mapeamento para Material 3 (Compose)

| Papel M3 | Token Pipa | Observação |
|---|---|---|
| `background` / `onBackground` | `bg` / `ink` | |
| `surface` / `onSurface` | `surface` / `ink` | |
| `surfaceVariant` / `onSurfaceVariant` | `surface2` / `ink2` | |
| `surfaceContainerLowest` | `term` | tela do terminal |
| `primary` / `onPrimary` | `primary` / `onPrimary` | tinta/papel, **não** âmbar |
| `primaryContainer` / `onPrimaryContainer` | `surface2` / `ink` | |
| `secondary` / `onSecondary` | `accent` / `onAccent` | faixa de pedido pendente |
| `secondaryContainer` / `onSecondaryContainer` | `accentSurface` / `attn` | chip de atenção |
| `tertiary` / `onTertiary` | `armed` / `onArmed` | escrita liberada |
| `tertiaryContainer` / `onTertiaryContainer` | `armedSurface` / `armed` | chip de escrita |
| `error` / `onError` | `danger` / `onDanger` | |
| `errorContainer` / `onErrorContainer` | `dangerSurface` / `danger` | |
| `outline` | `lineStrong` | borda de controle |
| `outlineVariant` | `line` | divisória decorativa |
| `scrim` | tinta a 48 % (claro) / preto a 60 % (escuro) | |

- **Cor dinâmica (Material You) desligada.** A identidade depende do âmbar
  significar "atenção"; com cor dinâmica, ele viraria a cor do papel de
  parede.
- O tema segue o sistema por padrão. Em Configurações pode ser fixado em
  claro ou escuro (`AppCompatDelegate` não se aplica em Compose puro; o
  valor salvo alimenta `isSystemInDarkTheme()` sobrescrito no
  `PipaTheme`).

## 5. Tipografia

| Estilo M3 | Fonte | Tamanho / altura | Peso | Uso |
|---|---|---|---|---|
| `headlineSmall` | IBM Plex Sans | 24 / 30 sp | 600 | título de tela vazia, boas-vindas |
| `titleLarge` | IBM Plex Sans | 18 / 24 sp | 600 | barra superior, título de folha |
| `titleMedium` | IBM Plex Sans | 16 / 22 sp | 600 | nome de terminal na lista |
| `bodyLarge` | IBM Plex Sans | 15 / 22 sp | 400 | texto corrido |
| `bodyMedium` | IBM Plex Sans | 14 / 20 sp | 400 | faixas, notas |
| `labelLarge` | IBM Plex Sans | 15 / 20 sp | 600 | botões |
| `labelMedium` | IBM Plex Sans | 13 / 18 sp | 600 | cabeçalho de seção, dicas |
| `mono.body` | JetBrains Mono | 13 / 19 sp | 400 | linhas do terminal |
| `mono.meta` | JetBrains Mono | 12,5 / 18 sp | 400 | contexto do terminal, caminhos |
| `mono.chip` | JetBrains Mono | 12 / 16 sp | 600 | chips de estado |
| `mono.code` | JetBrains Mono | 22 sp (campo) / 40 sp (confirmação) | 600 / 800 | código de pareamento, código de confirmação |
| `mono.brand` | JetBrains Mono | 22–34 sp | 800 | palavra "pipa" |

Regras de tipografia:

- **Tudo em `sp`**, com escala de fonte do sistema respeitada até 200 %. As
  linhas do terminal quebram (`softWrap`) em vez de cortar. As barras com
  altura fixa crescem com o texto (`heightIn(min = …)`), nunca
  `height(…)` fixo.
- Números que mudam (contagem regressiva, código) usam dígitos tabulares
  (`fontFeatureSettings = "tnum"`), para o texto não "dançar".
- **Fontes empacotadas no APK** (licença OFL das duas), sem download em
  tempo de execução: o app não faz requisição que não seja à ponte.

## 6. Espaço, forma e alvos

- **Grade de 4 dp:** espaçamentos 4, 8, 12, 16, 24, 32. Margem lateral das
  telas: 16 dp.
- **Raios:**
  - 8 dp para botões, campos e teclas;
  - 12 dp para cartões e o código de confirmação;
  - 16 dp para diálogos;
  - 20 dp no topo das folhas inferiores.
- **Alvos de toque:** mínimo **48 × 48 dp** em tudo que é tocável, incluindo:
  - as teclas especiais;
  - os ícones da barra superior;
  - os switches (com área de toque estendida).

  Isso passa com folga o WCAG 2.5.8 (24 px).
- Botões de texto dentro de faixas têm 44 dp de altura visual, com área de
  toque estendida para 48 dp (`minimumInteractiveComponentSize`).
- **Separação por risco:** Ctrl+C fica na segunda linha do teclado especial,
  longe do Enter, com borda vermelha. Recusar e Permitir têm o mesmo tamanho,
  lado a lado, com Recusar à esquerda. Assim, um toque desatento no canto
  direito inferior não interrompe um processo.
- **Movimento:**
  - só o que comunica estado: spinner de conexão e transição de folha;
  - `prefers-reduced-motion` / "Remover animações" do Android desliga tudo;
  - a contagem regressiva é texto, não barra animada.

## 7. Iconografia

- **Android:** Material Symbols Rounded, peso 400, preenchimento 0, 24 dp. Os
  ícones usados:
  - `lock`, `lock_open`;
  - `notifications`, `fingerprint`;
  - `computer`, `smartphone`;
  - `shield`, `tune`;
  - `wifi_off`, `cloud_off`;
  - `history`, `terminal`;
  - `send`, `block`;
  - `delete`, `check`, `close`;
  - `warning`, `play_arrow`.
- **VS Code:**
  - codicons nativos: `$(device-mobile)`, `$(lock)`, `$(unlock)`,
    `$(circle-slash)`, `$(debug-disconnect)`, `$(shield)`, `$(trash)`;
  - o glifo da Pipa, contribuído por `contributes.icons`;
  - todos herdam a cor do tema do editor.

## 8. Contraste medido

**Método:**

- Luminância relativa WCAG 2.x, calculada por `contrast.py` (no scratchpad da
  sessão de planejamento) sobre cada par token-sobre-fundo realmente usado,
  mais as 16 cores ANSI sobre `term`.
- **Resultado: 0 reprovações em 96 pares** (32 pares de tokens + 16 ANSI, nos
  dois temas).
- Mínimos aplicados:
  - 4,5:1 para texto;
  - 3:1 para borda de controle, anel de foco e ícone informativo (1.4.11).

**Conferência na página renderizada:**

- A skill yu-ux-web-expert rodou `contrast_audit.py` no protótipo, em 22
  estados × 2 temas (1440 × 1000).
- Foram 4.474 textos determináveis, **0 reprovados** em AA e 0 não
  determináveis.
- `run_axe.py` (axe-core) nos estados principais: 0 violações depois dos
  ajustes do §9. Os itens "incomplete" de `color-contrast` são os glifos
  `●`/`⎿` isolados da saída simulada, e o `contrast_audit` já os mediu como
  aprovados.

### Tema claro (todos os pares)

| Primeiro plano | Fundo | Razão medida | Mínimo | Uso | Resultado |
|---|---|---|---|---|---|
| `ink` #11141A | `bg` #F4F1EA | **16,35:1** | 4,5:1 | texto | passa |
| `ink` #11141A | `surface` #FCFBF7 | **17,81:1** | 4,5:1 | texto | passa |
| `ink` #11141A | `surface2` #E9E5DC | **14,67:1** | 4,5:1 | texto | passa |
| `ink` #11141A | `term` #FFFDF8 | **18,14:1** | 4,5:1 | texto terminal | passa |
| `ink2` #3D434F | `bg` #F4F1EA | **8,81:1** | 4,5:1 | texto secundário | passa |
| `ink2` #3D434F | `surface` #FCFBF7 | **9,59:1** | 4,5:1 | texto secundário | passa |
| `ink2` #3D434F | `surface2` #E9E5DC | **7,9:1** | 4,5:1 | texto secundário | passa |
| `ink3` #595F6A | `surface` #FCFBF7 | **6,2:1** | 4,5:1 | placeholder / meta | passa |
| `ink3` #595F6A | `bg` #F4F1EA | **5,69:1** | 4,5:1 | placeholder / meta | passa |
| `lineStrong` #857E70 | `surface` #FCFBF7 | **3,89:1** | 3:1 | borda de campo (1.4.11) | passa |
| `lineStrong` #857E70 | `bg` #F4F1EA | **3,57:1** | 3:1 | borda de campo (1.4.11) | passa |
| `accentText` #8A5300 | `surface` #FCFBF7 | **6,11:1** | 4,5:1 | link / texto de acento | passa |
| `accentText` #8A5300 | `bg` #F4F1EA | **5,61:1** | 4,5:1 | link / texto de acento | passa |
| `onAccent` #11141A | `accent` #F2A93B | **9,23:1** | 4,5:1 | texto na faixa de pedido | passa |
| `accentText` #8A5300 | `accentSurface` #FBE8C4 | **5,26:1** | 4,5:1 | chip de acento | passa |
| `focus` #8A5300 | `bg` #F4F1EA | **5,61:1** | 3:1 | anel de foco (1.4.11) | passa |
| `focus` #8A5300 | `surface` #FCFBF7 | **6,11:1** | 3:1 | anel de foco (1.4.11) | passa |
| `ink` #11141A | `accentSurface` #FBE8C4 | **15,32:1** | 4,5:1 | texto em cartão de atenção | passa |
| `ok` #1C6B3B | `surface` #FCFBF7 | **6,31:1** | 4,5:1 | status online | passa |
| `ok` #1C6B3B | `okSurface` #DCEFE2 | **5,44:1** | 4,5:1 | chip ok | passa |
| `attn` #8A5300 | `attnSurface` #FBE8C4 | **5,26:1** | 4,5:1 | chip atenção | passa |
| `attn` #8A5300 | `surface` #FCFBF7 | **6,11:1** | 4,5:1 | texto atenção | passa |
| `attnStrong` #B06C00 | `surface` #FCFBF7 | **4,06:1** | 3:1 | ícone/faixa atenção (1.4.11) | passa |
| `armed` #86277D | `surface` #FCFBF7 | **7,8:1** | 4,5:1 | texto escrita liberada | passa |
| `onArmed` #FFFFFF | `armed` #86277D | **8,08:1** | 4,5:1 | faixa escrita liberada | passa |
| `armed` #86277D | `armedSurface` #F4E0F0 | **6,45:1** | 4,5:1 | chip escrita | passa |
| `danger` #B0251C | `surface` #FCFBF7 | **6,48:1** | 4,5:1 | texto perigo | passa |
| `onDanger` #FFFFFF | `danger` #B0251C | **6,71:1** | 4,5:1 | botão destrutivo | passa |
| `ink2` #3D434F | `accentSurface` #FBE8C4 | **8,25:1** | 4,5:1 | texto secundário em cartão de atenção | passa |
| `ink2` #3D434F | `armedSurface` #F4E0F0 | **7,93:1** | 4,5:1 | texto secundário em faixa de escrita | passa |
| `danger` #B0251C | `dangerSurface` #F8E1DC | **5,37:1** | 4,5:1 | banner erro | passa |
| `offline` #595F6A | `surface` #FCFBF7 | **6,2:1** | 4,5:1 | status offline | passa |
| `ansi0` #1B2326 | `term` #FFFDF8 | **15,71:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi1` #B3261E | `term` #FFFDF8 | **6,43:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi2` #1C6E3D | `term` #FFFDF8 | **6,17:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi3` #7A5A00 | `term` #FFFDF8 | **6,28:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi4` #1F58B5 | `term` #FFFDF8 | **6,62:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi5` #8A2A80 | `term` #FFFDF8 | **7,58:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi6` #0A6A73 | `term` #FFFDF8 | **6,22:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi7` #4A575C | `term` #FFFDF8 | **7,35:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi8` #5F6C71 | `term` #FFFDF8 | **5,34:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi9` #A1261D | `term` #FFFDF8 | **7,35:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi10` #1A6A3A | `term` #FFFDF8 | **6,52:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi11` #735400 | `term` #FFFDF8 | **6,89:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi12` #1C51A8 | `term` #FFFDF8 | **7,4:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi13` #7D2574 | `term` #FFFDF8 | **8,65:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi14` #07606A | `term` #FFFDF8 | **7,15:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi15` #162024 | `term` #FFFDF8 | **16,31:1** | 4,5:1 | cor ANSI no terminal | passa |

### Tema escuro (todos os pares)

| Primeiro plano | Fundo | Razão medida | Mínimo | Uso | Resultado |
|---|---|---|---|---|---|
| `ink` #ECE8DF | `bg` #11141A | **15,08:1** | 4,5:1 | texto | passa |
| `ink` #ECE8DF | `surface` #191D25 | **13,81:1** | 4,5:1 | texto | passa |
| `ink` #ECE8DF | `surface2` #232833 | **12,07:1** | 4,5:1 | texto | passa |
| `ink` #ECE8DF | `term` #0C0E12 | **15,8:1** | 4,5:1 | texto terminal | passa |
| `ink2` #A3AAB8 | `bg` #11141A | **7,9:1** | 4,5:1 | texto secundário | passa |
| `ink2` #A3AAB8 | `surface` #191D25 | **7,24:1** | 4,5:1 | texto secundário | passa |
| `ink2` #A3AAB8 | `surface2` #232833 | **6,33:1** | 4,5:1 | texto secundário | passa |
| `ink3` #8A91A0 | `surface` #191D25 | **5,34:1** | 4,5:1 | placeholder / meta | passa |
| `ink3` #8A91A0 | `bg` #11141A | **5,83:1** | 4,5:1 | placeholder / meta | passa |
| `lineStrong` #6E7684 | `surface` #191D25 | **3,69:1** | 3:1 | borda de campo (1.4.11) | passa |
| `lineStrong` #6E7684 | `bg` #11141A | **4,03:1** | 3:1 | borda de campo (1.4.11) | passa |
| `accentText` #F2A93B | `surface` #191D25 | **8,45:1** | 4,5:1 | link / texto de acento | passa |
| `accentText` #F2A93B | `bg` #11141A | **9,23:1** | 4,5:1 | link / texto de acento | passa |
| `onAccent` #11141A | `accent` #F2A93B | **9,23:1** | 4,5:1 | texto na faixa de pedido | passa |
| `accentText` #F2A93B | `accentSurface` #3A2C12 | **6,79:1** | 4,5:1 | chip de acento | passa |
| `focus` #F2A93B | `bg` #11141A | **9,23:1** | 3:1 | anel de foco (1.4.11) | passa |
| `focus` #F2A93B | `surface` #191D25 | **8,45:1** | 3:1 | anel de foco (1.4.11) | passa |
| `ink` #ECE8DF | `accentSurface` #3A2C12 | **11,09:1** | 4,5:1 | texto em cartão de atenção | passa |
| `ok` #6CCB91 | `surface` #191D25 | **8,51:1** | 4,5:1 | status online | passa |
| `ok` #6CCB91 | `okSurface` #132D1F | **7,44:1** | 4,5:1 | chip ok | passa |
| `attn` #F2A93B | `attnSurface` #3A2C12 | **6,79:1** | 4,5:1 | chip atenção | passa |
| `attn` #F2A93B | `surface` #191D25 | **8,45:1** | 4,5:1 | texto atenção | passa |
| `attnStrong` #F2A93B | `surface` #191D25 | **8,45:1** | 3:1 | ícone/faixa atenção (1.4.11) | passa |
| `armed` #E48ADB | `surface` #191D25 | **7,2:1** | 4,5:1 | texto escrita liberada | passa |
| `onArmed` #2A0827 | `armed` #E48ADB | **7,71:1** | 4,5:1 | faixa escrita liberada | passa |
| `armed` #E48ADB | `armedSurface` #37163A | **6,69:1** | 4,5:1 | chip escrita | passa |
| `danger` #FF8A7D | `surface` #191D25 | **7,38:1** | 4,5:1 | texto perigo | passa |
| `onDanger` #3A0803 | `danger` #FF8A7D | **7,55:1** | 4,5:1 | botão destrutivo | passa |
| `ink2` #A3AAB8 | `accentSurface` #3A2C12 | **5,81:1** | 4,5:1 | texto secundário em cartão de atenção | passa |
| `ink2` #A3AAB8 | `armedSurface` #37163A | **6,72:1** | 4,5:1 | texto secundário em faixa de escrita | passa |
| `danger` #FF8A7D | `dangerSurface` #3B1511 | **7,06:1** | 4,5:1 | banner erro | passa |
| `offline` #8A91A0 | `surface` #191D25 | **5,34:1** | 4,5:1 | status offline | passa |
| `ansi0` #A7B3B8 | `term` #0C0E12 | **9,0:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi1` #FF8A7D | `term` #0C0E12 | **8,45:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi2` #6CCB91 | `term` #0C0E12 | **9,74:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi3` #EDBE4C | `term` #0C0E12 | **11,1:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi4` #7FB0FF | `term` #0C0E12 | **8,79:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi5` #E48ADB | `term` #0C0E12 | **8,24:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi6` #5FC4CD | `term` #0C0E12 | **9,44:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi7` #C9D2D5 | `term` #0C0E12 | **12,57:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi8` #8A979C | `term` #0C0E12 | **6,43:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi9` #FFA69B | `term` #0C0E12 | **10,28:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi10` #8BDDAA | `term` #0C0E12 | **11,98:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi11` #F6D27A | `term` #0C0E12 | **13,26:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi12` #A3C6FF | `term` #0C0E12 | **11,11:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi13` #EFA8E8 | `term` #0C0E12 | **10,52:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi14` #86D6DD | `term` #0C0E12 | **11,66:1** | 4,5:1 | cor ANSI no terminal | passa |
| `ansi15` #F2F6F7 | `term` #0C0E12 | **17,75:1** | 4,5:1 | cor ANSI no terminal | passa |

Pares de marca e de chrome medidos à parte:

| Par | Razão | Nota |
|---|---|---|
| âmbar `#F2A93B` sobre papel `#F4F1EA` | 1,77:1 | não usar para texto nem ícone pequeno |
| âmbar `#F2A93B` sobre `surface` escuro `#191D25` | 8,45:1 | ok |
| tinta sobre âmbar (faixa de pedido) | 9,23:1 | ok |
| papel sobre tinta (botão primário claro) | 16,35:1 | ok |
| tinta sobre `#ECE8DF` (botão primário escuro) | 15,08:1 | ok |
| `#8F5A00` / branco (simulação de `statusBarItem.warningBackground`) | 5,78:1 | no produto vem do tema do editor |

## 9. Ajustes feitos pela auditoria do protótipo

- As teclas especiais rolavam na horizontal, e Enter e Ctrl+C ficavam fora da
  vista. Agora é uma grade de 6 colunas:
  - primeira linha: Esc, Tab e as 4 setas;
  - segunda linha: Enter à esquerda e Ctrl+C à direita, separados.
- O subtítulo do terminal cortava o tamanho da tela. Encurtado para
  `LUCAS-PC · 120×32 (VS Code)`.
- O contexto dos terminais na lista não truncava com reticências. Corrigido.
- Regiões roláveis da simulação do VS Code sem foco de teclado (axe
  `scrollable-region-focusable`). Corrigido com `tabindex="0"` + rótulo.
- `tablist` com filhos que não eram abas (axe `aria-required-children`).
  Corrigido.
- O estilo dos rótulos de coluna do protótipo (caixa alta, 13 px) vazava
  para os títulos dentro do celular ("THREE STEPS, ONCE"). O seletor foi
  restrito ao filho direto.
