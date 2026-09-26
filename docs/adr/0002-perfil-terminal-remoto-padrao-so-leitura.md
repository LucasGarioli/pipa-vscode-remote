# ADR-0002 — Perfil "Terminal remoto" oferecido como padrão; todo terminal começa só leitura

## Status

Aceita · 2026-09-26 · decidido por Sr. Garioli.

Registro da decisão: auditoria §12, pergunta 2 e seu refinamento do mesmo
dia; auditoria §13 "Praticidade (decidido)"; forma final do perfil padrão
em `interfaces/vscode.md` §6, aprovada com as interfaces
(`interfaces/README.md`, "Aprovação (2026-09-26)"). O documento de
interfaces é mais novo que a auditoria e prevalece no ponto do
consentimento. O comportamento quando a pessoa responde "não" foi decidido
por Sr. Garioli em 2026-09-26, depois da primeira versão deste ADR
(`README.md` desta pasta, "Decididos depois da primeira versão", item 1).

## Contexto

- Com o agente dono dos PTYs (ADR-0001), só as sessões criadas pelo agente
  são acessíveis ao celular. A pergunta era: sessões opt-in, ou observar
  também os terminais comuns com as limitações da API (auditoria §12,
  pergunta 2; §3 C1).
- A ideia central reafirmada por Sr. Garioli: controlar a distância os
  terminais abertos no VS Code, com segurança e praticidade (auditoria
  §13). Um passo extra para cada terminal atrapalharia a praticidade.
- A exposição remota precisa ter um padrão seguro: ler é inofensivo,
  escrever é execução remota de comandos (auditoria §6, premissa).

## Decisão

- **Só sessões do perfil "Terminal remoto"** são acessíveis pelo celular
  (auditoria §12, pergunta 2; §9 item 6).
- A extensão registra o perfil `pipa.remote` por
  `contributes.terminal.profiles` e `registerTerminalProfileProvider`, que
  devolve um `Pseudoterminal` ligado ao agente, com o glifo da Pipa em
  `terminal.ansiYellow` e `isTransient: true` (`interfaces/vscode.md` §6).
- **Perfil padrão com consentimento:** a extensão **oferece** torná-lo o
  perfil padrão (notificação com botão "Usar como padrão", perguntada uma
  vez) e só grava `terminal.integrated.defaultProfile.windows` com o "sim"
  da pessoa (`interfaces/vscode.md` §6; chave `vsc.set_default_profile` em
  `interfaces/textos.md`).
- **Se a resposta for "não"** (decidido por Sr. Garioli, 2026-09-26):
  - a extensão **não pergunta de novo**;
  - só os terminais abertos pelo perfil "Terminal remoto" aparecem no
    celular;
  - quando não há nenhum, a lista de terminais do celular mostra um estado
    vazio que **ensina a abrir um** terminal desse perfil;
  - um comando **"Usar como padrão"** no VS Code permite mudar de ideia
    depois.
- O shell continua o do usuário (pwsh, bash, cmd); o perfil só o embrulha
  no PTY do agente (auditoria §13).
- **Grant padrão de toda nova sessão: `read`** para os aparelhos pareados.
  Escrever exige liberar a escrita (ADR-0003) (auditoria §13; §5.7 passo 4;
  textos `pair.success_body` e `vsc.allow_detail`).
- O celular **não cria terminais** no MVP (`interfaces/README.md`, "O que
  ficou fora"). Quando criar, escolhe só um `profile_id` definido no PC,
  nunca shell, args, cwd ou env (auditoria §3 A1, §6 T7).

## Alternativas consideradas

| Alternativa | Por que caiu |
|---|---|
| Observar também os terminais comuns, só leitura, via shell integration | Leitura parcial, por comando e só depois da inscrição; sem CMD (auditoria §3 C1, §12 pergunta 2). |
| Perfil remoto opt-in, sem oferta de virar padrão | Cada terminal exigiria escolher o perfil: contra a praticidade pedida (auditoria §13). |
| Extensão grava o perfil padrão sozinha (texto da auditoria §13) | Substituída pela pergunta com consentimento em `interfaces/vscode.md` §6: mexer numa configuração do usuário sem perguntar. **[INFERÊNCIA]** o motivo não está escrito no documento; o texto só diz que a gravação exige consentimento. |
| Perguntar de novo depois de um "não" | Rejeitada por Sr. Garioli (2026-09-26); quem quiser muda pelo comando "Usar como padrão". |
| Escrita liberada por padrão para aparelhos pareados | Celular roubado desbloqueado ganharia escrita (auditoria §6 T1). |

## Consequências

**Positivas**

- Com o "sim", todo terminal novo nasce acessível pelo celular, sem passo
  extra (auditoria §13).
- Com o "não", a escolha da pessoa é respeitada sem insistência, e o
  caminho para mudar de ideia continua visível (comando e estado vazio do
  celular).
- A superfície de ataque é exatamente o conjunto de sessões do perfil
  remoto (auditoria §9 item 6).
- Ver é seguro por padrão; agir exige intenção confirmada (ADR-0003).

**Negativas**

- **[INFERÊNCIA]** Terminais que já existiam antes da instalação, ou
  abertos por outro perfil, continuam só locais (auditoria §13).
- Com o "não", terminais abertos pelo atalho ou pelo "+" não aparecem no
  celular; a pessoa precisa escolher o perfil "Terminal remoto" a cada
  terminal.
- Os textos e a visão ainda assumem o "sim"; os ajustes estão listados em
  "Ajustes de interface pendentes" no `README.md` desta pasta.
- **Não verificado:** o valor exato a gravar em
  `terminal.integrated.defaultProfile.windows` para um perfil vindo de
  extensão; testar no M1 (`interfaces/vscode.md` §12 item 1).
- A cor da aba só pode ser definida na criação; por isso marca a
  capacidade (visível pelo celular), não o estado (`interfaces/vscode.md`
  §6).
- Herda as perdas do modelo "agente dono do PTY" (ADR-0001).

## Referências

- `docs/auditoria-arquitetura-2026-09-26.md` §3 (A1, C1), §5.7, §6 (T1,
  T7), §9 item 6, §12 pergunta 2, §13.
- `docs/interfaces/vscode.md` §6, §9, §12 item 1.
- `docs/interfaces/README.md` "O que ficou fora" e "Aprovação".
- `docs/interfaces/textos.md` (`vsc.set_default_profile`,
  `pair.success_body`, `vsc.allow_detail`, `sessions.empty_body`).
- `docs/visao.md` "O que faz" e "O que não faz (no MVP)".
- `docs/adr/README.md` "Decididos depois da primeira versão", item 1.
