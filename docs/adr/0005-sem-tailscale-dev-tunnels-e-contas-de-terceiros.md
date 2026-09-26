# ADR-0005 — Sem Tailscale, Microsoft Dev Tunnels, VS Code tunnels ou contas de terceiros

## Status

Aceita · 2026-09-26 · decidido por Sr. Garioli.

Registro da decisão: pedido "sem terceiros" (proposta §1); aprovação da
proposta como direção (cabeçalho da proposta); `visao.md`, "O que não faz
(no MVP)": "Não depende de Tailscale, Microsoft Dev Tunnels ou contas de
terceiros".

## Contexto

A auditoria desenhou o transporte sobre Tailscale (listener TLS no IP
100.x, pairing por QR com endpoint do tailnet), com a autenticação de
aplicação independente dele (auditoria §4.2, §5.7, §9 item 5, Anexo B).
Sr. Garioli pediu depois: conexão por código, tunelamento por segurança,
**sem terceiros**, talvez usando o túnel já presente no VS Code (proposta
§1). A rede de casa tem forte indício de CGNAT (proposta §3), então algum
relay é inevitável (ADR-0004).

## Decisão

- O produto **não depende** de Tailscale, Microsoft Dev Tunnels, Remote
  Tunnels do VS Code (`code tunnel`) nem de qualquer conta de terceiro
  para funcionar (`visao.md`; proposta §2, §8).
- O transporte é a ponte própria com túnel cifrado ponta a ponta
  (ADR-0004).
- Removidos do desenho: Tailscale, bind no IP 100.x, a restrição de um VPN
  por vez no Android e o pairing com endpoint do tailnet (proposta §8).

## Alternativas consideradas e por que caíram

**Túnel do VS Code / Microsoft Dev Tunnels** (proposta §2, todos
**[FATO]**):

- Login obrigatório com conta GitHub ou Microsoft; uma porta privada só é
  acessível pela mesma conta; um app sem login precisaria de um token de
  cliente que **expira em 24 h** e só pode ser renovado pela identidade do
  dono.
- O TLS termina na borda da Microsoft, e o relay é dela.
- Limite de **5 GB/mês** por usuário.
- Serviço em *public preview*, "for adhoc testing and development, not for
  production workloads", sem SLA.
- A API para criar túneis (`workspace.openTunnel`) é *proposed* e não pode
  ir para o Marketplace.
- O Remote Tunnels (`code tunnel`) só conecta clientes VS Code, com a
  mesma conta nas duas pontas.

**Tailscale:**

- É um terceiro com conta própria, contra o pedido "sem terceiros"
  (proposta §1, §8). **[FATO]** conta Tailscale tomada ou nó do tailnet
  comprometido dão acesso de rede ao agente (auditoria §3 C4, §6 T3).
- Exigiria o Tailscale ligado no celular como pré-requisito externo
  (auditoria §13, "Praticidade").
- **[FATO]** O Android só permite um VPN ativo por usuário/perfil: quem usa
  VPN corporativa no celular não teria o Tailscale ao mesmo tempo
  (auditoria Anexo B).
- Observação justa: o Tailscale **resolve** o CGNAT (NAT traversal +
  DERP) e tinha lock-in baixo com auth própria (auditoria Anexo B). Não
  caiu por falha técnica; caiu pelo requisito de produto "sem terceiros".

**Headscale / WireGuard puro:** WireGuard puro exige porta aberta ou IP
público no PC e falha sob CGNAT; Headscale é servidor próprio, mas o
cliente continua sendo uma VPN no celular (auditoria Anexo B).
**[INFERÊNCIA]** a mesma restrição de um VPN por vez no Android se
aplicaria.

## Consequências

**Positivas**

- Nenhum login de terceiro; o fluxo é "instalar, ler um código, abrir o
  app" (`visao.md`, "Promessa").
- Nenhum TLS terminado fora dos aparelhos do usuário (ADR-0004).
- Convive com VPN corporativa no celular. **[INFERÊNCIA]** a ponte é uma
  conexão comum de app, não um VPN do Android.

**Negativas**

- O projeto passa a operar a própria ponte: hospedagem, disponibilidade e
  abuso ficam por conta dele (ADR-0006; proposta §7).
- Perde-se o NAT traversal pronto do Tailscale; o MVP vai sempre via ponte
  (proposta §4).
- Para usuários que não sejam Sr. Garioli, a ponte padrão
  `ponte.gariolilabs.com` é operada pela Garioli Labs e vê só metadados;
  quem quiser aponta para a própria ponte (decidido por Sr. Garioli,
  2026-09-26; ADR-0004). **[INFERÊNCIA]** a ponte padrão não exige conta
  nem login do usuário, então o requisito "sem contas de terceiros"
  continua valendo; como o PC obtém a chave de inscrição dela fica para
  P4.
- O push usa o FCM, do Google, que vê só IDs opacos (ADR-0014).
  **[INFERÊNCIA]** é a única dependência de serviço de terceiro no MVP;
  quem guarda a credencial de envio do FCM é ponto aberto (ADR-0014).

## Referências

- `docs/proposta-conexao-por-codigo-2026-09-26.md` §1, §2, §3, §8.
- `docs/auditoria-arquitetura-2026-09-26.md` cabeçalho, §3 C4, §4.2, §5.7,
  §6 T3, §9 item 5, §13, Anexo B.
- `docs/visao.md` "Promessa" e "O que não faz (no MVP)".
- `docs/interfaces/vscode.md` §10.
