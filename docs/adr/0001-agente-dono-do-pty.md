# ADR-0001 — O agente Rust é dono dos PTYs; a extensão é uma view fina

## Status

Aceita · 2026-09-26 · decidido por Sr. Garioli.

Registro da decisão: auditoria §12, pergunta 1 ("terminais genéricos, com
dados só na rede do usuário. Confirma o modelo B"); mantida pela proposta
de conexão por código (cabeçalho e §8, "Mantido: agente dono do PTY").

## Contexto

A proposta inicial previa uma extensão do VS Code que observasse e
controlasse os terminais comuns do editor. Pela API estável isso não se
sustenta:

- **[FATO]** `window.onDidWriteTerminalData` é API *proposed*, e o próprio
  arquivo diz que não será promovida a estável por problemas de
  desempenho. APIs *proposed* não podem ser usadas em extensões publicadas
  (auditoria §1 item 1, §3 C1; Anexo A).
- **[FATO]** A única leitura estável, `TerminalShellExecution.read()`
  (1.93+), funciona por comando, exige shell integration, só entrega o que
  foi escrito depois da inscrição e não dá acesso ao scrollback. O
  `cmd.exe` não tem shell integration (auditoria §1 item 2, §3 C1).
- **[FATO]** Fechar a janela do VS Code descarta os processos de terminal;
  `persistentSessionReviveProcess` relança um processo novo, não preserva
  o antigo (auditoria §1 item 3, §3 C2).
- **[INFERÊNCIA]** Um Claude Code iniciado antes da inscrição da extensão
  aparece como uma única execução, cuja saída fica perdida até o fim
  (auditoria §3 C1).
- **[FATO]** O extension host morre com a janela, e `deactivate()` recebe no
  máximo 5 s (auditoria §2).

## Decisão

- Um agente Rust por usuário (`trcd`) é o **session host**: cria e possui os
  PTYs (ConPTY no Windows, `openpty` nos demais), mantém um emulador VT por
  sessão e é a fonte da verdade de sessões, contexto e eventos (auditoria
  §4.2, §4.3, §9 item 1).
- A extensão do VS Code é uma **view fina**: um `Pseudoterminal` ligado à
  sessão do agente por IPC local (named pipe com ACL do usuário), sem módulo
  nativo (auditoria §4.2, §13 tabela "Extensão";
  `interfaces/vscode.md` §6; `interfaces/exigencias-para-o-protocolo.md`
  §3 I10).
- O ID da sessão é do agente (ULID), e a view guarda esse ID (auditoria §3
  M5).
- O agente roda como processo de usuário iniciado no logon, instância
  única, nunca como Windows Service (auditoria §4.3 — recomendação da
  auditoria, coberta pela frase "o restante desta auditoria continua
  valendo" do cabeçalho da proposta).

## Alternativas consideradas

| Alternativa | Por que caiu |
|---|---|
| A. Extensão observa os terminais do VS Code (proposta original) | Captura parcial (por comando, depois da inscrição), sem CMD, sessões morrem ao fechar o VS Code, superfície de ataque = todo terminal (auditoria §4.1). |
| C. Só Claude Code (hooks, SDK ou o Remote Control oficial) | Não cobre terminais genéricos. **[FATO]** O Remote Control oficial passa pela API da Anthropic e o transcript fica nos servidores dela (auditoria §4.1). Sr. Garioli escolheu terminais genéricos com dados só na rede dele (§12, pergunta 1). |
| Agente como Windows Service | Roda na sessão 0; criar shells na sessão do usuário exige manipular tokens; um bug vira escalada de privilégio (auditoria §4.3). |

## Consequências

**Positivas**

- Captura total da saída, inclusive de CMD e de TUIs (auditoria §4.1).
- As sessões sobrevivem a fechar e reabrir o VS Code (auditoria §3 C2;
  critério de pronto de M4 na §8).
- Só é acessível remotamente o que foi aberto pelo perfil remoto: a
  superfície de ataque encolhe (auditoria §1, §4.1). Ver ADR-0002.
- JetBrains ou CLI depois exigem só uma nova view (auditoria §4.1).

**Negativas**

- Crash do agente mata os PTYs, que são filhos dele. Mitigações: agente
  sem pânico, sessões marcadas `lost` com motivo persistido, separação
  futura de um *ptyhost* mínimo (auditoria §4.3).
- Contribuições de ambiente de outras extensões
  (`environmentVariableCollection`, como a ativação de venv do Python) não
  se aplicam aos shells do agente (auditoria §3 M3).
- A shell integration nativa do VS Code só funciona se o fluxo trouxer
  OSC 633. **[INFERÊNCIA — validar em spike M0]** o agente pode injetar os
  próprios scripts de integração (auditoria §3 M3; Anexo A, "Não
  verificado").
- Conflito de tamanho entre a view do PC e o celular; o tamanho do PTY
  pertence à view desktop quando anexada (auditoria §3 M1).
- Custo médio: ConPTY + emulador VT (auditoria §4.1). A escolha do
  emulador (`alacritty_terminal` ou `vt100`) e a checagem de licenças ficam
  para o spike M0 (auditoria §8, Anexo A).

## Referências

- `docs/auditoria-arquitetura-2026-09-26.md` §1, §2, §3 (C1, C2, M1, M3,
  M5), §4.1–§4.3, §9 item 1, §12 pergunta 1, Anexo A.
- `docs/proposta-conexao-por-codigo-2026-09-26.md` cabeçalho e §8.
- `docs/interfaces/vscode.md` §6.
- `docs/interfaces/exigencias-para-o-protocolo.md` §3 (I10).
