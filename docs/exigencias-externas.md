# Exigências externas

Exigências que vêm de outros produtos de Sr. Garioli e que a Pipa precisa
atender. Cada uma diz de onde veio, o que pede e quais entregas do
planejamento a absorvem. Status inicial de toda exigência: **registrada,
aguarda desenho** (nenhuma decisão de protocolo tomada aqui).

## EX1 — Entrada local de avisos (primeiro cliente: claude-hadouken)

- **Origem:** ordem de Sr. Garioli de 2026-09-26, recebida pela sessão do
  claude-hadouken. Referência do lado de lá: `Garioli-Labs/claude-hadouken`,
  commit `73937e9`, spec
  `docs/superpowers/specs/2026-09-25-leitor-de-consumo-design.md` §12.
- **Contexto:** o claude-hadouken v0.3.0 vai mandar alertas de consumo e
  avisos de tarefa terminada para a Pipa. A Pipa tem **prioridade sobre o
  WhatsApp** como destino (a pessoa escolhe Pipa, WhatsApp ou os dois;
  padrão: nenhum).
- **O que pede:** o agente da Pipa no PC expõe uma **entrada local de
  avisos** que outros programas locais podem chamar para mandar um aviso
  curto ao celular pelo canal cifrado da própria Pipa, sem serviço de
  terceiro no caminho além do push opaco já decidido (ADR-0014).
  O primeiro cliente é um plugin Node sem dependências.
- **Decisões a tomar:**

  | Tema | Onde é decidido |
  |---|---|
  | Transporte local (pipe nomeado no Windows / socket Unix) | P3 (spec TRCP/1, lado local, §3) |
  | Autenticação de quem chama, para que nenhum processo qualquer forje avisos | P5 (Fable) |
  | Esquema da mensagem: título, texto curto, severidade, origem; conteúdo mínimo, sem código, caminhos pessoais nem segredos | P3 + P6 |
  | Limite de taxa | P3 §14 + P8 |
  | Comportamento com o celular offline (fila, validade, descarte) | P3 (Event Log) + P6 (retenção) |
  | Onde o aviso aparece no app e como a pessoa silencia uma origem | P7 (interfaces): ajuste de tela para aprovação de Sr. Garioli |

- **Inferência:** o encaixe natural é um tipo de "atenção" sem sessão de
  terminal no Event Log, entregue pelo mesmo push opaco
  `{agent_id, attention_id}`. A confirmar no desenho.
