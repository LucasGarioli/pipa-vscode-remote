<p align="center">
  <img src="docs/marca/pipa-logo.svg" width="112" height="112" alt="Logo do Pipa: uma pipa âmbar com o prompt >_">
</p>

<h1 align="center">Pipa</h1>

<p align="center"><b>Seus terminais, de longe. Presos por uma linha segura.</b></p>

O Pipa permite controlar pelo celular os terminais abertos no VS Code, de
qualquer lugar, com segurança, praticidade e leveza.

1. Instale a extensão no VS Code.
2. Ela mostra um código de 12 dígitos para o seu computador.
3. Instale o app no Android e digite o código (ou leia o QR).
4. Confirme no PC. Pronto: nas próximas vezes, basta abrir o app.

> **Estado: planejamento.** Ainda não existe código. O desenvolvimento
> começa só após a aprovação final do planejamento.

## Como funciona

```text
 PC                                  Ponte (sua)                   Celular
┌─────────────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│ VS Code + extensão Pipa │       │ repassa só bytes │       │ App Android     │
│          │              │ saída │ cifrados; não lê │ saída │                 │
│ agente (dono dos        ├──────►│ nada, não guarda ◄───────┤ digita o código │
│ terminais)              │       │ nada             │       │ uma única vez   │
└─────────────────────────┘       └──────────────────┘       └─────────────────┘
        └──────────── túnel cifrado ponta a ponta PC ⇄ celular ─────────────┘
```

- **Agente próprio, dono dos terminais.** Os terminais do perfil
  "Terminal remoto" (o padrão do VS Code) rodam num agente leve em Rust.
  - A extensão só os exibe.
  - As sessões sobrevivem ao fechamento do VS Code.
- **Nenhuma porta aberta no PC e nenhum terceiro no caminho.**
  - O PC e o celular se conectam, por saída, a uma ponte sua (Raspberry,
    VPS ou nuvem).
  - A ponte só repassa dados cifrados de ponta a ponta.
- **Contexto mínimo no celular.**
  - Estado de cada terminal e um resumo curto do que está acontecendo.
  - Tela sob demanda; o celular não guarda o conteúdo.
- **Seguro por padrão.**
  - Tudo é só leitura.
  - Para escrever, você libera um terminal por 1, 5 ou 15 minutos com a
    digital.
  - Aprovações destrutivas pedem a digital de novo.
  - No PC, um botão corta todo o acesso na hora.
- **Feito para agentes de IA.** Pedidos de permissão do Claude Code chegam
  como aprovações estruturadas, e não como teclas digitadas às cegas.

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
- [Interfaces](docs/interfaces/README.md):
  - [fluxos](docs/interfaces/fluxos.md)
  - [VS Code](docs/interfaces/vscode.md)
  - [Android](docs/interfaces/android.md)
  - [identidade visual](docs/interfaces/identidade-visual.md)
  - [textos PT-BR/EN](docs/interfaces/textos.md)
  - [protótipo navegável](docs/interfaces/prototipo/index.html): abra o
    arquivo localmente no navegador.
- [Conceitos de logo](docs/marca/pipa-conceitos-de-logo.html)

## Plataformas

- Extensão VS Code (Windows primeiro; Linux e macOS depois).
- App Android. iOS fica fora do escopo inicial.
- Idiomas: português (Brasil) e inglês.
