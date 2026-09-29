# Exigências do produto registradas depois das decisões

Exigências de Sr. Garioli que chegaram depois das ADRs e que podem reabrir
decisões já aceitas. Cada uma diz o que pede, o que conflita e quem
desenha a resposta. Status inicial: **registrada, aguarda desenho**
(planejamento em pausa por ordem dele).

## PR1 — Funcionar em terminais já iniciados, não só nos novos

- **Origem:** Sr. Garioli, 2026-09-29: "O Pipa precisa funcionar em
  terminais que já foram iniciados, não só os novos."
- **O que pede:** terminais que já estavam abertos no VS Code antes da
  Pipa (ou abertos fora do perfil "Terminal remoto") também aparecem e
  funcionam no celular.
- **Conflita com:**
  - ADR-0001 (o agente é dono dos PTYs; só ele lê e escreve neles);
  - ADR-0002 (só sessões do perfil "Terminal remoto" existem para o
    celular; recusa do perfil padrão = nenhum terminal comum aparece);
  - telas aprovadas que dizem "só terminais do Terminal remoto"
    (`sessions.empty_body_not_default` e afins).
- **Fatos já verificados na auditoria (§3, §12), que limitam o desenho:**
  - [FATO] `window.onDidWriteTerminalData` (ler a saída de qualquer
    terminal) é API **proposta** e não será promovida; extensão na
    Marketplace não pode usá-la.
  - [FATO] `TerminalShellExecution.read()` (API estável, VS Code 1.93)
    lê a saída **por comando**, só a partir da inscrição e só com shell
    integration ativa; o cmd.exe não tem shell integration. Não há
    histórico do que já estava na tela antes da inscrição.
  - [FATO] `Terminal.sendText()` (estável) escreve em qualquer terminal.
- **Caminhos a avaliar no desenho (nenhum escolhido):**
  1. **Modo parcial nos terminais comuns:** lista todos os terminais;
     nos que não são do agente, mostra a saída comando a comando via
     shell integration (sem a tela inteira, sem TUI como o Claude Code)
     e escreve via `sendText()`, com os mesmos portões de escrita
     (biometria ou PIN, armado por sessão).
  2. **"Trazer para a Pipa":** um comando que reabre o terminal comum
     dentro do agente (mesmo cwd e shell). Não preserva o processo em
     execução.
  3. **Combinação de 1 e 2:** parcial por padrão, com "Trazer para a
     Pipa" quando a pessoa quiser a tela completa.
  4. Ler a tela inteira de um terminal que o agente não criou exige API
     proposta ou anexar ao ConPTY de outro processo; [INFERÊNCIA] não é
     viável numa extensão publicada. A confirmar em spike M0.
- **Quem desenha:** ADR nova (reabre 0001/0002), com spike M0 para medir
  o que a shell integration entrega em pwsh, bash e cmd e para o Claude
  Code rodando num terminal comum; ajuste de telas (P7) e da spec TRCP/1
  (tipo de sessão "parcial"); revisão de segurança (escrita via
  `sendText()` num terminal que o agente não controla).
- **Decisão pendente de Sr. Garioli:** qual caminho (1, 2 ou 3), quando
  o desenho for retomado.
