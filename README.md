<p align="center">
  <img src="docs/marca/pipa-logo.svg" width="112" height="112" alt="Logo da Pipa: uma pipa âmbar com o prompt >_ dentro, sobre um quadrado escuro">
</p>

<h1 align="center">Pipa</h1>

<p align="center"><b>Seus terminais, de longe. Presos por uma linha segura.</b></p>

<p align="center">
  <code>fase: planejamento</code>&nbsp;
  <code>VS Code + Android</code>&nbsp;
  <code>PT-BR · EN</code>&nbsp;
  <code>ponte própria, cifrada ponta a ponta</code>&nbsp;
  <code>licença: a definir</code>
</p>

<p align="center">
  <img src="docs/imagens/hero.png" width="880" alt="Três telas lado a lado: o app Android no tema claro com a lista de terminais do LUCAS-PC, o app no tema escuro com o terminal do Claude Code com a escrita liberada, e o painel Conectar celular do VS Code com o código de 12 dígitos e o QR">
</p>

## O que é

A Pipa controla, pelo celular, os terminais abertos no VS Code: de qualquer
lugar, com segurança, praticidade e leveza. Você acompanha builds, testes,
servidores e agentes de IA como o Claude Code, e responde quando algo pede
atenção.

> [!IMPORTANT]
> **Estado: planejamento.** Ainda não existe código. Tudo o que aparece aqui
> é o desenho aprovado e o [protótipo navegável](docs/interfaces/prototipo/index.html),
> com dados fictícios. O desenvolvimento começa só após a aprovação final do
> planejamento.

## Como funciona em 4 passos

<table>
  <tr>
    <td width="38%" valign="top">
      <h3>1. Instale a extensão</h3>
      <p>No VS Code. Ela traz o agente que cuida dos terminais e oferece, uma
      vez, usar o perfil <b>Terminal remoto</b> como padrão (só grava com o
      seu sim). Assim, todo terminal novo já nasce acessível pelo celular, em
      modo só leitura.</p>
    </td>
    <td valign="top">
      <h3>2. Gere o código</h3>
      <p>No VS Code, <b>Pipa: Conectar celular</b> mostra 12 dígitos e um QR.
      O código vale 5 minutos e serve uma vez só.</p>
      <img src="docs/imagens/vscode-conectar-celular.png" width="480" alt="Painel Conectar celular do VS Code com o código 4821 · 9137 2055, o QR, o aviso Vale por 5:00 e o estado Aguardando o celular">
    </td>
  </tr>
  <tr>
    <td valign="top">
      <h3>3. Digite no app</h3>
      <p>No Android, <b>Adicionar computador</b>: leia o QR ou digite os
      12 dígitos.</p>
      <img src="docs/imagens/android-adicionar-computador-claro.png" width="220" alt="Tela Adicionar computador com o código 4821 · 9137 2055 digitado, o nome do celular Pixel 8 e o botão Conectar">
    </td>
    <td valign="top">
      <h3>4. Confirme no PC</h3>
      <p>O celular e o VS Code mostram o mesmo código de confirmação de
      6 dígitos. Confira e clique em <b>Permitir</b>. Pronto: nas próximas
      vezes, basta abrir o app.</p>
      <img src="docs/imagens/vscode-permitir-aparelho-modal.png" width="440" alt="Modal do VS Code: Permitir Pixel 8 neste computador? com o código de confirmação 482 913 e os botões Permitir e Recusar"><br>
      <img src="docs/imagens/android-confirmacao-no-pc-claro.png" width="180" alt="Tela do celular Confira no PC com o mesmo código de confirmação 482 913">
    </td>
  </tr>
</table>

## Telas

Capturas do protótipo aprovado ([abra localmente](docs/interfaces/prototipo/index.html)
para navegar pelos 59 estados). Os nomes de PC, aparelhos e comandos são
fictícios.

### Android

<table>
  <tr>
    <td align="center" valign="top" width="33%">
      <img src="docs/imagens/android-boas-vindas-claro.png" width="240" alt="Tela de boas-vindas com a marca, a promessa e os três passos"><br>
      <sub><b>Boas-vindas.</b> Três passos, uma vez só.</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <img src="docs/imagens/android-computadores-claro.png" width="240" alt="Lista de computadores: LUCAS-PC online com 4 terminais e 1 pedido de atenção; NOTE-TRABALHO offline desde 09:14"><br>
      <sub><b>Computadores.</b> Online, ou offline desde quando.</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <img src="docs/imagens/android-terminais-claro.png" width="240" alt="Terminais do LUCAS-PC: Claude Code aguardando permissão, Backend rodando, Frontend pronto e Build com falha"><br>
      <sub><b>Terminais.</b> Estado e contexto mínimo de cada um.</sub>
    </td>
  </tr>
  <tr>
    <td align="center" valign="top">
      <img src="docs/imagens/android-terminal-so-leitura-claro.png" width="240" alt="Terminal do Claude Code em modo só leitura, com a barra de teclas especiais desabilitada"><br>
      <sub><b>Terminal, só leitura.</b> Tela sob demanda e teclas especiais.</sub>
    </td>
    <td align="center" valign="top">
      <img src="docs/imagens/android-escrita-liberada-claro.png" width="240" alt="Terminal com a faixa magenta Escrita liberada 4:37, o comando npm run lint no campo e o botão Bloquear"><br>
      <sub><b>Escrita liberada.</b> Faixa magenta com contagem regressiva.</sub>
    </td>
    <td align="center" valign="top">
      <img src="docs/imagens/android-pedido-do-claude-claro.png" width="240" alt="Pedido do Claude Code para executar npm run build, com os botões Recusar e Permitir com biometria"><br>
      <sub><b>Pedido do Claude.</b> Permitir ou recusar, sem teclar às cegas.</sub>
    </td>
  </tr>
  <tr>
    <td align="center" valign="top">
      <img src="docs/imagens/android-aparelhos-e-seguranca-claro.png" width="240" alt="Aparelhos e segurança: chave no chip de segurança, bloqueio de capturas de tela, aparelhos com acesso e atividade recente"><br>
      <sub><b>Aparelhos e segurança.</b> Quem tem acesso e o que fez.</sub>
    </td>
    <td align="center" valign="top">
      <img src="docs/imagens/android-adicionar-computador-claro.png" width="240" alt="Tela Adicionar computador com o código digitado"><br>
      <sub><b>Adicionar computador.</b> QR ou 12 dígitos.</sub>
    </td>
    <td align="center" valign="top">
      <img src="docs/imagens/android-confirmacao-no-pc-claro.png" width="240" alt="Tela Confira no PC com o código de confirmação 482 913"><br>
      <sub><b>Confira no PC.</b> O mesmo código nos dois lados.</sub>
    </td>
  </tr>
</table>

**Claro e escuro**, seguindo o sistema:

<table>
  <tr>
    <td align="center" valign="top" width="33%">
      <img src="docs/imagens/android-terminais-escuro.png" width="240" alt="Lista de terminais no tema escuro"><br>
      <sub>Terminais</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <img src="docs/imagens/android-escrita-liberada-escuro.png" width="240" alt="Terminal com escrita liberada no tema escuro"><br>
      <sub>Escrita liberada</sub>
    </td>
    <td align="center" valign="top" width="33%">
      <img src="docs/imagens/android-pedido-do-claude-escuro.png" width="240" alt="Pedido do Claude no tema escuro"><br>
      <sub>Pedido do Claude</sub>
    </td>
  </tr>
</table>

### VS Code

Só API estável e UI nativa. A única webview é o painel de pareamento.

<table>
  <tr>
    <td align="center" valign="top" width="50%">
      <img src="docs/imagens/vscode-conectar-celular.png" width="420" alt="Painel Conectar celular com código, QR e contagem de 5 minutos"><br>
      <sub><b>Conectar celular.</b> Código de 12 dígitos, QR e validade de 5 min.</sub>
    </td>
    <td align="center" valign="top" width="50%">
      <img src="docs/imagens/vscode-permitir-aparelho.png" width="420" alt="Modal Permitir Pixel 8 neste computador?"><br>
      <sub><b>Permitir aparelho.</b> O modal nomeia o celular e mostra o código de confirmação.</sub>
    </td>
  </tr>
  <tr>
    <td align="center" valign="top">
      <img src="docs/imagens/vscode-controle-remoto-ativo.png" width="420" alt="Aba do terminal renomeada para Claude Code · Pixel 8 no controle, aviso Pixel 8 liberou a escrita por 5 min com o botão Retirar escrita e item da barra de status Pixel 8 no controle"><br>
      <sub><b>Controle remoto visível.</b> A aba muda de nome e a barra de status muda de cor.</sub>
    </td>
    <td align="center" valign="top">
      <img src="docs/imagens/vscode-aparelhos.png" width="420" alt="Painel Pipa em árvore: este computador com o agente ligado, aparelhos com lixeira para revogar, terminais remotos em só leitura e atividade recente"><br>
      <sub><b>Painel Pipa.</b> Aparelhos, terminais remotos e atividade recente.</sub>
    </td>
  </tr>
</table>

## Por que a Pipa

- **Nenhum terceiro no caminho.** Sem Tailscale, sem Microsoft Dev Tunnels,
  sem contas. O PC e o celular se conectam, por saída, a uma **ponte sua**
  (Raspberry, VPS ou nuvem), e a ponte só repassa bytes cifrados de ponta a
  ponta. Nenhuma porta fica aberta no PC.
- **Contexto mínimo no celular, nada guardado nele.** O celular recebe o
  estado de cada terminal e um resumo curto. A tela vem sob demanda e fica só
  na memória, com captura de tela bloqueada por padrão. O celular guarda
  apenas a lista de PCs pareados e a própria chave.
- **Só leitura por padrão.** Para digitar, você libera **um** terminal por
  1, 5 ou 15 minutos com a biometria. A faixa de modo fica sempre visível, e
  o PC mostra quem está no controle.
- **Aprovações destrutivas pedem a biometria de novo**, mesmo com a escrita
  liberada. Recusar nunca pede.
- **Corte de acesso no PC.** Um comando derruba todas as conexões na hora,
  sem confirmação, e oferece **Reativar**. O corte continua valendo depois de
  reiniciar o PC.
- **Feita para agentes de IA.** Pedidos de permissão do Claude Code chegam
  pelos hooks dele como aprovações estruturadas ("executar `npm run build`?"),
  e não como teclas digitadas às cegas. Pedido já respondido no PC não aceita
  resposta.
- **Terminais que sobrevivem ao VS Code.** Um agente próprio é dono dos
  terminais; a extensão só os exibe. Fechar o VS Code não mata as sessões.
- **Leve de rodar.** As metas abaixo são **metas, ainda não medições**: a
  fase M0 mede e a M2 as transforma em teste de regressão.

  | Componente | Meta |
  |---|---|
  | Agente parado, sem terminais | ≤ 20 MB de RAM, ~0 % de CPU (só eventos, sem polling) |
  | Agente, por terminal | ≤ 5 MB (histórico limitado a ~2 000 linhas) |
  | 4 terminais ativos + 1 celular assistindo | ≤ 2 % de um núcleo |
  | Extensão | sem módulo nativo |
  | Celular em segundo plano | nenhuma conexão aberta |
  | Envio → tela atualizada | ≤ 150 ms p95 com a ponte no Brasil; ≤ 400 ms p95 com a ponte nos EUA |

## Arquitetura

```mermaid
flowchart LR
  subgraph PC["PC (Windows primeiro)"]
    direction TB
    VS["VS Code<br/>extensão Pipa (só exibe)"]
    AG["Agente trcd (Rust)<br/>dono dos terminais"]
    CC["Claude Code<br/>rodando num terminal"]
    VS <-->|IPC local| AG
    CC -->|hook no 127.0.0.1| AG
  end
  BR["Ponte trc-bridge (sua)<br/>repassa bytes cifrados<br/>sem disco, sem contas, sem chaves"]
  subgraph CEL["Celular"]
    APP["App Android Pipa"]
  end
  AG <-->|"WSS, conexão de saída do PC"| BR
  BR <-->|"WSS, conexão de saída do celular"| APP
  AG -.-|"túnel TLS 1.3 ponta a ponta: a ponte só vê registros cifrados"| APP
```

- **Agente dono dos terminais.** Os terminais do perfil "Terminal remoto"
  rodam num agente leve em Rust, iniciado no logon como processo do usuário
  (nunca como administrador nem como serviço). A extensão é uma view fina
  desses terminais, e as sessões sobrevivem ao fechamento do VS Code.
- **Tela, não fluxo de bytes.** O agente interpreta o terminal e envia ao
  celular o estado da tela (texto e estilo já interpretados), nunca a saída
  bruta com sequências de escape.
- **Ponte burra por construção.** Ela junta as duas pontas pelo número de
  encontro e copia bytes. Não guarda nada em disco, não tem banco e não
  conhece nenhuma chave. É um binário único que roda num Raspberry Pi, num
  VPS mínimo ou num contêiner. Onde ela vai morar é decidido na fase M6.

Detalhes em [auditoria](docs/auditoria-arquitetura-2026-09-26.md) e
[conexão por código](docs/proposta-conexao-por-codigo-2026-09-26.md).

## Segurança e privacidade

| Fica no PC, sempre | Pode chegar ao celular | Nunca é guardado, em lugar nenhum |
|---|---|---|
| Saída bruta do terminal, histórico completo, variáveis de ambiente, arquivos, transcript do Claude Code, chaves privadas | Lista de terminais, estado, contexto curto, pedidos de atenção, tela visível e histórico paginado **só do terminal que você abriu, sob demanda** | Saída bruta, texto digitado, conteúdo de tela no celular (só memória, descartado ao sair) |

A notificação push leva só um identificador opaco ("Algo pede sua atenção em
LUCAS-PC"). O conteúdo é buscado pelo túnel quando você abre o app.

**Pareamento pelo código de 12 dígitos:**

- Os **4 primeiros** são o número de encontro: a ponte usa só para juntar as
  duas pontas.
- Os **8 restantes** são o segredo e **nunca saem dos aparelhos**. Eles
  alimentam uma troca de chaves SPAKE2 (o mesmo desenho do magic-wormhole).
- Quem tenta adivinhar tem **uma** tentativa por código (1 chance em
  100 milhões). Um erro invalida o código de forma visível, e não existe
  ataque offline, nem para quem controla a ponte.
- O PC ainda pede confirmação: o modal nomeia o aparelho e mostra o código
  de confirmação de 6 dígitos, que precisa ser igual ao do celular.
- Depois disso, as chaves ficam fixadas (Android Keystore no celular, cofre
  do Windows no PC), e cada sessão usa TLS 1.3 mútuo dentro do fluxo
  repassado pela ponte.
- A ponte vê apenas IPs, horários e tamanhos. Esse metadado é aceito e
  declarado.

A parte criptográfica passa por revisão de segurança dedicada antes de
qualquer código.

## Andamento

| Etapa | Estado |
|---|---|
| Auditoria da arquitetura | ✅ [feita](docs/auditoria-arquitetura-2026-09-26.md) |
| Conexão por código, sem terceiros | ✅ [aprovada](docs/proposta-conexao-por-codigo-2026-09-26.md) |
| Visão, nome e marca | ✅ [aprovados](docs/visao.md) |
| Interfaces (VS Code + Android) e protótipo | ✅ [aprovadas](docs/interfaces/README.md) |
| ADRs das decisões | ⏳ próxima |
| Protocolo TRCP/1 | ⏳ |
| Privacidade e requisitos não funcionais | ⏳ |
| Ponte e segurança (revisão Fable max) | ⏳ |
| Planos por fase (M0–M8) | ⏳ |
| Desenvolvimento | 🔒 aguardando aprovação do planejamento |

Mapa completo do planejamento:
[`docs/plans/00-mapa-do-planejamento.md`](docs/plans/00-mapa-do-planejamento.md).

## Documentos

- [Visão do produto](docs/visao.md)
- [Auditoria técnica e arquitetural](docs/auditoria-arquitetura-2026-09-26.md)
- [Conexão por código (ponte própria)](docs/proposta-conexao-por-codigo-2026-09-26.md)
- [Mapa do planejamento](docs/plans/00-mapa-do-planejamento.md)
- [Interfaces](docs/interfaces/README.md):
  - [fluxos](docs/interfaces/fluxos.md)
  - [VS Code](docs/interfaces/vscode.md)
  - [Android](docs/interfaces/android.md)
  - [identidade visual](docs/interfaces/identidade-visual.md)
  - [textos PT-BR/EN](docs/interfaces/textos.md)
  - [exigências para o protocolo](docs/interfaces/exigencias-para-o-protocolo.md)
  - [protótipo navegável](docs/interfaces/prototipo/index.html): abra o
    arquivo localmente no navegador.
- [Conceitos de logo](docs/marca/pipa-conceitos-de-logo.html)

## Identidade visual

Estilo terminal: base sóbria de papel e tinta, uma única cor de marca e
monoespaçada onde o dado é de terminal. Cada cor tem um significado só.

| | Cor | Hex | Uso |
|---|---|---|---|
| <img src="docs/imagens/cores/ambar.svg" width="56" height="28" alt=""> | Âmbar de fósforo | `#F2A93B` | marca e atenção (pedido pendente) |
| <img src="docs/imagens/cores/ambar-texto.svg" width="56" height="28" alt=""> | Âmbar para texto | `#8A5300` | texto "âmbar" sobre fundo claro |
| <img src="docs/imagens/cores/tinta.svg" width="56" height="28" alt=""> | Tinta | `#11141A` | texto, botão principal, fundo escuro |
| <img src="docs/imagens/cores/papel.svg" width="56" height="28" alt=""> | Papel | `#F4F1EA` | fundo claro |
| <img src="docs/imagens/cores/magenta.svg" width="56" height="28" alt=""> | Magenta | `#86277D` | escrita liberada |
| <img src="docs/imagens/cores/vermelho.svg" width="56" height="28" alt=""> | Vermelho | `#B0251C` | destrutivo ou erro |

- **Tipografia:** JetBrains Mono (marca e terminal) + IBM Plex Sans (UI).
- **Acessibilidade medida:** contraste WCAG 2.2 AA sem reprovações em 96
  pares de tokens e em 4.474 textos renderizados, nos dois temas; alvos de
  toque de 48 dp.

## Perguntas frequentes

**Preciso de Tailscale ou de uma VPN?**
Não. A Pipa não depende de Tailscale, Microsoft Dev Tunnels nem de contas de
terceiros. O PC e o celular fazem conexões de saída até a sua ponte, por isso
funcionam atrás de CGNAT e sem porta aberta no PC.

**Funciona no iPhone?**
Ainda não. O iOS fica fora do escopo inicial; o app é Android.

**O celular guarda o que aparece nos meus terminais?**
Não. A tela fica só na memória e é descartada ao sair. O celular não guarda
nem a lista de terminais: só a lista de PCs pareados e a chave dele.

**A ponte consegue ler meus terminais?**
Não. Ela só vê bytes cifrados, além de IPs, horários e tamanhos.

**E se o PC dormir?**
O agente não impede o sleep. O app mostra "LUCAS-PC está offline desde
14:02" e nenhuma ação remota fica disponível até o PC acordar.

**Todo terminal do VS Code fica acessível pelo celular?**
Só os do perfil "Terminal remoto", que a extensão oferece como padrão. Os
terminais que já existiam antes da instalação, ou abertos por outro perfil,
continuam só locais.

## Plataformas

- Extensão VS Code (Windows primeiro; Linux e macOS depois).
- App Android. iOS fica fora do escopo inicial.
- Idiomas: português (Brasil) e inglês.

## Licença

A definir.
