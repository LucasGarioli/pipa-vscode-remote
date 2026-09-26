# ADR-0004 — Ponte própria (`trc-bridge`) e pareamento por código de 12 dígitos

## Status

Aceita · 2026-09-26 · decidido por Sr. Garioli.

Registro da decisão: `proposta-conexao-por-codigo-2026-09-26.md`,
cabeçalho ("aprovada como direção por Sr. Garioli em 2026-09-26"); ponte
padrão decidida por Sr. Garioli em 2026-09-26, depois da primeira versão
deste ADR (`README.md` desta pasta, "Decididos depois da primeira versão",
item 4); a parte
criptográfica depende da revisão de segurança dedicada (P5, Fable max)
antes de qualquer código (proposta §8, "Revisão").

**Atualizado em 2026-09-26 (mais tarde no mesmo dia):** Sr. Garioli
substituiu a ponte padrão pública por uma **ponte privada**: "Servidor só
pra mim e pra quem eu autorizar. Outros usam servidores próprios deles ou
raspberry deles." (`README.md` desta pasta, item 5, que substitui o
item 4). O núcleo deste ADR (ponte própria, código de 12 dígitos, TLS
fixado) não mudou; mudou só quem pode usar `ponte.gariolilabs.com`.

## Contexto

- O pedido de Sr. Garioli: instalar o plugin, gerar um código estilo
  AnyDesk, digitar o código no app e pronto; tunelamento por segurança;
  sem terceiros (proposta §1).
- **[FATO]** A perfuração de NAT falha quando os dois lados estão atrás de
  NATs "não bem-comportados", e um relay é obrigatório nesses casos (RFC
  8656). Com CGNAT, redirecionamento de porta e P2P deixam de funcionar
  (proposta §3).
- **[FATO, medido no PC]** A rede de casa tem NAT duplo, com forte indício
  de CGNAT, e não tem IPv6 global (proposta §3).
- **[INFERÊNCIA]** Para o celular achar o PC só com um código, de qualquer
  rede, algum ponto alcançável precisa fazer a ponte; "sem terceiros"
  passa a significar uma ponte própria que não consegue ler nada
  (proposta §3).

## Decisão

**Topologia**

- Agente e celular fazem só conexões de **saída** até a ponte
  `trc-bridge`; nenhuma porta aberta no PC (proposta §4).
- A ponte é **burra por construção:** associa o ID do computador a uma
  conexão e copia bytes; sem disco, sem banco, sem chaves de sessão;
  binário Rust único (proposta §4, §4.1).
- **MVP sempre via ponte**, sem perfuração de NAT; conexão direta na mesma
  Wi-Fi e perfuração de NAT ficam como otimizações futuras, sem mudar o
  protocolo (proposta §4).
- Só PCs com a **chave de inscrição da ponte**, gerada na instalação da
  ponte, se registram nela (proposta §7).
- **Ponte privada, sem ponte pública** (decidido por Sr. Garioli,
  2026-09-26; substitui a "ponte padrão" decidida mais cedo no mesmo dia):
  - `ponte.gariolilabs.com` é **privada**: serve só Sr. Garioli e quem
    ele autorizar, com uma chave de inscrição emitida por ele. Formato,
    emissão e revogação dessa chave ficam para P4 (Fable).
  - **Não há ponte pública padrão.** Os demais usuários hospedam a
    própria ponte, com o mesmo binário `trc-bridge`, num servidor ou VPS
    ou num Raspberry. **[FATO, proposta §3 e §4.1]** Raspberry em casa
    atrás de CGNAT só funciona com IP público da operadora; sem ele, é
    preciso um VPS.
  - A extensão **pede o endereço da ponte na primeira vez**
    (`pipa.bridge`, `interfaces/vscode.md` §10); no uso de Sr. Garioli, o
    endereço vem pré-preenchido ou configurado.
  - O QR leva o endereço da ponte; o código digitado de 12 dígitos
    **não** leva. O app precisa, então, de um campo "Servidor" no fluxo
    de adicionar computador (ajuste de interface pendente,
    `interfaces/ajustes-pendentes-2026-09-26.md`).
  - Em qualquer caso a ponte não vê o conteúdo, só bytes cifrados
    (proposta §4, §7).

**Código**

- 12 dígitos numéricos, exibidos `4821 · 9137 2055`: os **4 primeiros**
  são o número de encontro, que a ponte usa só para juntar as pontas; os
  **8 restantes** são o segredo, que nunca sai dos aparelhos e só alimenta
  o PAKE (proposta §5).
- Validade de 5 min, uso único; um código errado invalida o código de
  forma visível (proposta §5, §7; `interfaces/README.md` decisão 7).
- O QR leva o mesmo código e o endereço da ponte (proposta §5;
  `interfaces/vscode.md` §4).

**Criptografia**

- **Pareamento, uma vez:** SPAKE2 sobre o segredo de 8 dígitos gera uma
  chave temporária; protegidos por ela, os dois trocam e fixam as chaves
  permanentes: P-256 no Android Keystore (não exportável) e a chave do PC
  no cofre do Windows (DPAPI) (proposta §6 item 1).
- **Confirmação no PC:** os dois lados mostram um código de confirmação de
  6 dígitos derivado da troca; o PC **compara** (não digita) e decide em
  modal "Permitir “<aparelho>” neste computador?", com 60 s de prazo
  (proposta §5, §6 item 1; `interfaces/README.md` Q4;
  `interfaces/vscode.md` §5).
- **Sessões seguintes:** TLS 1.3 mútuo com chaves fixadas, rodando
  **dentro** do fluxo repassado pela ponte (rustls no PC; SSLEngine ou
  Conscrypt no Android); a ponte vê só registros TLS (proposta §6
  item 2).
- Nas próximas vezes o celular já conhece o PC, sem código (proposta §5).

## Alternativas consideradas

| Alternativa | Por que caiu |
|---|---|
| Tailscale como transporte (desenho original da auditoria) | Terceiro e com conta; ver ADR-0005 (proposta §8, "Removido"). |
| Túnel do VS Code / Microsoft Dev Tunnels | Terceiro, login obrigatório, API proposta; ver ADR-0005 (proposta §2). |
| Conexão direta com porta pública ou WireGuard puro | Falha sob CGNAT e expõe superfície pública (auditoria Anexo B; proposta §3). |
| QR com segredo de 128 bits e fallback `7F4K-92MX` com 5 tentativas (auditoria §5.7) | Substituído pelo código numérico de 12 dígitos com PAKE e tentativa única (proposta §5; cabeçalho da auditoria). |
| Noise `IK` nas sessões | **[FATO]** `snow` não passou por auditoria independente, e o Noise exige PSK de 256 bits, não senha curta (§15.1 da especificação). Registrada e não adotada (proposta §6). |
| Perfuração de NAT no MVP | Complexidade sem necessidade: o tráfego de terminal é pequeno (Screen Sync coalescido) (proposta §4). |
| Ponte pública padrão `ponte.gariolilabs.com` para qualquer usuário (decidida e substituída em 2026-09-26) | Sr. Garioli preferiu servir só a si e a quem autorizar; os demais usam ponte própria. |

## Consequências

**Positivas**

- Funciona atrás de CGNAT dos dois lados (proposta §4).
- **[INFERÊNCIA]** Um atacante de rede tem uma tentativa por código, com 1
  chance em 100 milhões; não há ataque offline, nem para quem controla a
  ponte; a confirmação no PC é uma segunda barreira (proposta §5, com
  citação do magic-wormhole).
- A ponte comprometida só vê IPs, horários e tamanhos (proposta §7).
- A autenticação não depende da rede (auditoria §9 item 5).
- **[INFERÊNCIA]** Com a ponte privada, a Garioli Labs só opera metadados
  de usuários que Sr. Garioli autorizou, nunca de desconhecidos.

**Negativas**

- Existe um servidor a operar e a hospedar (ADR-0006).
- **[INFERÊNCIA]** Para Sr. Garioli e quem ele autorizar, a Garioli Labs
  vê os metadados de uso (IPs, horários, tamanhos), nunca o conteúdo.
- Quem não foi autorizado precisa subir a própria ponte antes do primeiro
  pareamento: um passo a mais na instalação, e hospedagem, atualização e
  disponibilidade por conta dessa pessoa.
- Metadados de uso (quando o terminal é usado) ficam visíveis para a ponte:
  aceito e declarado (proposta §7).
- Latência maior se a ponte ficar fora do Brasil: meta de ≤ 400 ms p95 com
  ponte nos EUA, contra 150 ms p95 no Brasil (proposta §4.1).
- **[FATO]** `spake2` declara no README que não passou por auditoria
  independente (proposta §6). Risco aberto para P5 (ver ADR-0010).
- A derivação do código de confirmação
  (`HKDF(K, "trcp-sas-v1") mod 10^6`), o formato de erros de pareamento e
  o conteúdo do QR são **propostas** das interfaces
  (`interfaces/exigencias-para-o-protocolo.md` P1, P3, P5), não decisões.

## Referências

- `docs/proposta-conexao-por-codigo-2026-09-26.md` §1, §3, §4, §4.1, §5,
  §6, §7, §8.
- `docs/auditoria-arquitetura-2026-09-26.md` cabeçalho, §5.7, §9 item 5,
  Anexo B.
- `docs/interfaces/README.md` decisão 7, Q4.
- `docs/interfaces/vscode.md` §4, §5.
- `docs/interfaces/exigencias-para-o-protocolo.md` §2 (P1–P5).
- `docs/interfaces/ajustes-pendentes-2026-09-26.md` (campo "Servidor").
