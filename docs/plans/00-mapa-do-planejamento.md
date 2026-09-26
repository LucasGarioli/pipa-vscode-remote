# Mapa do planejamento

Início: 2026-09-26, com autorização de Sr. Garioli: "pode começar o
planejamento. Inclua interfaces no planejamento já também."

**Regra:** nenhuma linha de código de produto nem teste descartável antes
do sinal explícito de início do desenvolvimento. O planejamento produz só
documentos, protótipos visuais de interface e planos.

## Entregas

| # | Entrega | Arquivo(s) | Modelo · effort sugerido | Depende de |
|---|---|---|---|---|
| P1 | Glossário e visão do produto: nome, público, promessa, o que **não** faz | `docs/visao.md` | Opus · high | — |
| P2 | ADRs das decisões já tomadas (agente dono do PTY, perfil padrão só leitura, arm por biometria, ponte própria + código, sem Tailscale/Dev Tunnels) | `docs/adr/0001…0006` | Opus · high | P1 |
| P3 | Especificação do protocolo TRCP/1: envelope, handshake, Event Log, Screen Sync, comandos, erros, limites, versionamento + fixtures de conformidade descritas | `docs/spec/trcp-1.md` | Opus · xhigh | P2 |
| P4 | Especificação da ponte (`trc-bridge`): encontro por código, modos permanente e sob demanda, abusos, limites | `docs/spec/bridge.md` | **Fable · max** | P3 |
| P5 | Segurança: threat model consolidado, pareamento (SPAKE2), TLS fixado, chaves, biometria, revogação, auditoria; **revisão Fable max** | `docs/security.md` | **Fable · max** | P3, P4 |
| P6 | Privacidade: política de dados (o que fica no PC, o que chega ao celular, retenção) | `docs/privacy.md` | Opus · high | P3 |
| P7 | **Interfaces**: fluxos, telas e estados do VS Code e do Android, textos (UX writing), acessibilidade, **protótipo visual navegável** | `docs/interfaces/` | Opus · high (+ skill de UX) | P1, P5 (fluxo de pareamento) |
| P8 | Requisitos não funcionais: leveza, latência, bateria, com o método de medição | `docs/requisitos-nao-funcionais.md` | Opus · high | P3 |
| P9 | Planos por fase (M0 spikes → M8 push): tarefas, arquivos, testes, Definição de Pronto, modelo/effort por tarefa | `docs/plans/M0…M8.md` | Opus · xhigh; M6 **Fable · max** | P2–P8 |
| P10 | Quadro de andamento no README | `README.md` | Opus · high | P9 |

## Escopo das interfaces (P7)

**VS Code** (UI nativa sempre que possível; webview só para o QR):

- barra de status: agente on/off, nº de celulares conectados, sessão
  controlada remotamente;
- indicador no terminal "controlado remotamente por <aparelho>";
- comando e painel "Conectar celular": código de 12 dígitos + QR + contagem
  de 5 min;
- confirmação "Permitir <aparelho>?";
- lista de aparelhos com revogação;
- kill switch "Cortar acesso remoto";
- configurações: ponte, padrões de permissão.

**Android:**

- boas-vindas;
- adicionar computador (digitar código ou ler QR, esperar confirmação);
- lista de computadores (online/offline desde…);
- lista de sessões com estado e contexto;
- tela da sessão (terminal só leitura, campo de comando, teclas especiais:
  Ctrl+C, setas, Tab, Esc);
- liberar escrita com biometria (arm por X min, contagem visível);
- atenção/aprovação estruturada ("Claude pede permissão para…");
- histórico paginado;
- aparelhos e segurança;
- estados de erro: sem rede, PC dormindo, código expirado, revogado.

**Para cada tela:**

- objetivo;
- dados exibidos, com origem no protocolo (P3);
- ações e permissão exigida;
- estados vazio / carregando / erro / offline;
- textos;
- acessibilidade: contraste, alvo de toque ≥ 48 dp, TalkBack.

**Protótipo:** HTML navegável publicado como página privada para revisão.
Não é código de produto: é descartável e serve só para aprovar o desenho.

## Ordem e pontos de revisão

Reordenada em 2026-09-26 por ordem de Sr. Garioli: "Quero as interfaces
prontas primeiro". "Prontas" no planejamento significa desenho aprovado e
protótipo navegável; o código de interface espera o sinal de
desenvolvimento.

1. P1 (visão mínima: nome, promessa, público) → decisões de identidade
   visual — **feito** (`docs/visao.md`: Pipa, logo A)
2. **P7 — interfaces completas + protótipo → APROVADAS em 2026-09-26** (`docs/interfaces/README.md`)
3. P2 + P3 + P6 + P8, ajustados ao que as telas aprovadas exigem →
   revisão
4. P4 + P5 (Fable max) → revisão. Se a segurança exigir mudança em alguma
   tela (por exemplo, no pareamento), a tela volta para reaprovação.
5. P9 + P10 → **aprovação final do planejamento**; aguarda o sinal de
   desenvolvimento
