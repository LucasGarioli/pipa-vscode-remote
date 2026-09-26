# ADR-0013 — Kill switch sem confirmação e persistente; revogação de aparelhos só no PC

## Status

Aceita · 2026-09-26 · decidido por Sr. Garioli.

Registro da decisão: perguntas Q5 e Q6 de `interfaces/README.md`, aceitas
na "Aprovação (2026-09-26)", e decisão de desenho 3 das mesmas interfaces;
kill switch já previsto na auditoria (§6 T1, T8; §13).

## Contexto

- O dono do PC precisa de um jeito imediato de tirar todo acesso remoto
  numa emergência (auditoria §13; §6 T8).
- Um celular roubado não pode expulsar o dono legítimo (Q6).
- Revogar um aparelho é irreversível para ele (exige novo pareamento);
  cortar o acesso é reversível (`interfaces/vscode.md` §8).

## Decisão

- **Kill switch "Cortar acesso remoto"** no PC, **sem confirmação**, com
  **Reativar** na notificação: desfazer é melhor que confirmar
  (`interfaces/README.md` decisão 3; `interfaces/vscode.md` §3).
- **O corte persiste** depois de reiniciar o PC (Q5).
- **Revogar aparelho** só no PC, com modal que nomeia o aparelho
  ("Revogar “Pixel 8”?"); o celular revogado perde a conexão
  imediatamente (auditoria §6 T1; `interfaces/vscode.md` §8).
- **O celular não revoga outros aparelhos** (Q6); pode só remover o
  próprio pareamento ("Remover LUCAS-PC deste celular")
  (`interfaces/exigencias-para-o-protocolo.md` E18).

Os códigos de fechamento (4403 revogado já na auditoria §5.6; 4410 `cut`
novo) e o comportamento da ponte durante o corte são **propostas** das
interfaces (`interfaces/exigencias-para-o-protocolo.md` E19, E20, I7) para
P3/P4.

## Alternativas consideradas

| Alternativa | Por que caiu |
|---|---|
| Kill switch com "Tem certeza?" | Atrasaria justamente a ação de emergência (`interfaces/vscode.md` §3). |
| Corte que volta sozinho no reboot | Quem cortou numa emergência não quer ver o acesso voltar sozinho (Q5). |
| Revogar outros aparelhos pelo celular | Um celular roubado poderia expulsar o dono (Q6). |

## Consequências

**Positivas**

- Uma ação, sem diálogo, derruba todos os celulares (`interfaces/vscode.md`
  §3).
- O ladrão de um celular não mexe nos outros aparelhos (Q6).

**Negativas**

- O estado de corte precisa ser persistido pelo agente
  (`interfaces/exigencias-para-o-protocolo.md` I7).
- Para revogar um aparelho perdido é preciso estar no PC (Q6).
  **[INFERÊNCIA]** longe do PC, a única defesa contra um celular roubado é
  a biometria de escrita (ADR-0003); o kill switch também exige o PC.

## Referências

- `docs/auditoria-arquitetura-2026-09-26.md` §5.6, §6 (T1, T8), §13.
- `docs/interfaces/README.md` decisão 3, Q5, Q6, "Aprovação".
- `docs/interfaces/vscode.md` §3, §8.
- `docs/interfaces/exigencias-para-o-protocolo.md` E18–E20, I7.
