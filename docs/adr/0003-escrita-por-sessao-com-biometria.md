# ADR-0003 — Escrita liberada por terminal, com prazo e biometria

## Status

Aceita · 2026-09-26 · decidido por Sr. Garioli.

Registro da decisão: auditoria §12, pergunta 3 ("arm por sessão com
biometria por alguns minutos; aprovações destrutivas pedem biometria de
novo"); durações e detalhes nas perguntas Q1, Q7, Q9 e Q10 de
`interfaces/README.md`, aceitas na "Aprovação (2026-09-26)"; mantida pela
proposta de conexão por código (§8, "Mantido: … arm por biometria").
Que o PIN/padrão do aparelho também vale foi decidido por Sr. Garioli em
2026-09-26, depois da primeira versão deste ADR (`README.md` desta pasta,
"Decididos depois da primeira versão", item 3). Neste ADR, "biometria"
quer dizer "biometria forte ou credencial do aparelho".

## Contexto

- O produto é, por definição, execução remota de comandos. O objetivo é
  que só o aparelho certo, na sessão certa, com intenção confirmada, possa
  escrever (auditoria §6, premissa).
- Ameaça principal: celular roubado desbloqueado (auditoria §6 T1).
- Três opções estavam na mesa: arm por sessão com biometria por X
  minutos, biometria a cada envio, ou só aprovação estruturada sem teclado
  livre (auditoria §12, pergunta 3).
- Todo terminal começa só leitura (ADR-0002).

## Decisão

- **Liberar escrita é por terminal e com prazo:** 1, 5 ou 15 min, padrão
  5, com teto configurável no PC (`pipa.write.maxMinutes`) e escrita
  desligável no PC (`pipa.write.enabled`) (`interfaces/README.md` decisão 1
  e Q7; `interfaces/android.md` §8; `interfaces/vscode.md` §10).
- **Prova de presença pelo Android:** `BiometricPrompt` com
  `CryptoObject`, assinando o step-up com uma chave P-256 do Android
  Keystore, não exportável (TEE/StrongBox), com
  `setUserAuthenticationRequired(true)` e
  `setInvalidatedByBiometricEnrollment(true)` (auditoria §6 T1, §4.2;
  `interfaces/android.md` §0 "Biometria").
- **Autenticadores aceitos: `BIOMETRIC_STRONG | DEVICE_CREDENTIAL`.** O
  PIN, o padrão ou a senha do aparelho também liberam a escrita (decidido
  por Sr. Garioli, 2026-09-26; configuração já citada na auditoria §6 T1
  e em `interfaces/android.md` §0; texto `arm.bio_use_pin`).
- **Uma chave ou duas no celular** (a do TLS mútuo e a de escrita) não é
  decidido aqui; segue para P5 (`README.md` desta pasta).
- **Biometria de novo, mesmo com escrita liberada,** para permitir um
  pedido destrutivo e para encerrar terminal (auditoria §12, pergunta 3;
  `interfaces/README.md` decisão 3; `interfaces/fluxos.md` F4;
  `interfaces/android.md` §9).
- **Recusar um pedido não pede biometria** (Q1). **Abrir o app não pede
  biometria** (Q10).
- **O PC vê quem está no controle:** aba renomeada, barra de status em
  warning, badge na árvore e notificação ao liberar, desligável
  (`pipa.notify.onArm`, Q9) (`interfaces/vscode.md` §2, §6, §7).
- Sem biometria nem bloqueio de tela no celular, o app lê mas não escreve
  (`interfaces/android.md` §0).

O formato do step-up (`step_up.challenge`, `grant.arm`/`grant.disarm`,
eventos `grant.armed`/`grant.disarmed`) é **proposta** das interfaces
(`interfaces/exigencias-para-o-protocolo.md` E4–E6, E9) e fica para a
especificação do protocolo (P3) e para a revisão de segurança (P5).

## Alternativas consideradas

| Alternativa | Por que caiu |
|---|---|
| Biometria a cada envio | Opção listada na auditoria §12 pergunta 3; não escolhida. **[INFERÊNCIA]** atrito alto para quem acompanha e responde várias vezes seguidas; `interfaces/README.md` Q7 diz que 5 min cobre "responder e acompanhar". |
| Só aprovação estruturada, sem teclado livre no MVP | Opção listada na auditoria §12 pergunta 3; não escolhida. A visão inclui enviar comandos e teclas especiais depois de liberar a escrita (`visao.md`, "O que faz"). |
| Escrita liberada por aparelho inteiro, sem prazo | **[INFERÊNCIA]** contraria o objetivo de limitar o dano de um toque errado "a um terminal e a poucos minutos" (`interfaces/android.md` §8). |
| Só biometria forte (`BIOMETRIC_STRONG`, sem PIN) | Rejeitada por Sr. Garioli (2026-09-26). **[INFERÊNCIA]** o motivo não foi registrado; aparelhos sem biometria forte cadastrada ficariam só leitura. |
| Allowlist de comandos | Em um PTY o input é um fluxo de teclas, e a filtragem é contornável (auditoria §6 T8). |

## Consequências

**Positivas**

- Celular roubado desbloqueado não escreve sem a biometria ou o PIN do
  dono (auditoria §6 T1).
- Quem não tem biometria cadastrada, mas tem bloqueio de tela, também pode
  escrever (`interfaces/android.md` §0).
- O dano de um toque errado fica limitado a um terminal e a poucos minutos
  (`interfaces/android.md` §8).
- O dono no PC sabe o tempo todo quem pode digitar (`interfaces/vscode.md`
  §2, §6).

**Negativas**

- Celular sem biometria nem bloqueio de tela fica só leitura
  (`interfaces/android.md` §0).
- **[INFERÊNCIA]** O prazo do arm é estado do agente (`Grant.armed_until`,
  auditoria §7.1), não um timeout da chave no Keystore: a chave com
  autenticação exigida só prova a presença no momento da assinatura.
- **[INFERÊNCIA]** Com `DEVICE_CREDENTIAL`, quem viu o dono digitar o PIN
  e pega o celular desbloqueado consegue liberar a escrita; a proteção
  contra T1 fica tão forte quanto o PIN do aparelho. As outras barreiras
  continuam: aviso no PC, prazo curto, kill switch e revogação
  (ADR-0013).
- Textos que dizem só "biometria" (por exemplo `pair.success_body` e
  `vsc.allow_detail`) ficam imprecisos; ver "Ajustes de interface
  pendentes" no `README.md` desta pasta.
- Trocar a biometria cadastrada invalida a chave, e o aparelho precisa
  refazer a chave de escrita (auditoria §6 T1,
  `setInvalidatedByBiometricEnrollment`). **[INFERÊNCIA]** o fluxo de
  recuperação não está desenhado.

## Referências

- `docs/auditoria-arquitetura-2026-09-26.md` §4.2, §6 (premissa, T1, T8),
  §7.1, §12 pergunta 3, §13.
- `docs/interfaces/README.md` decisões 1 e 3, Q1, Q7, Q9, Q10, "Aprovação".
- `docs/interfaces/android.md` §0, §8, §9.
- `docs/interfaces/vscode.md` §2, §6, §7, §10.
- `docs/interfaces/fluxos.md` F4.
- `docs/interfaces/exigencias-para-o-protocolo.md` E4, E5, E6, E9.
- `docs/proposta-conexao-por-codigo-2026-09-26.md` §8.
