# PROPOSTA — Conexão por código, sem terceiros

Data: 2026-09-26 · Status: **aprovada como direção** por Sr. Garioli em 2026-09-26 (hospedagem da ponte decidida na fase M6).
Substitui a parte de transporte da auditoria
(`auditoria-arquitetura-2026-09-26.md`): Tailscale, TLS no IP 100.x e
pairing por QR com endpoint do tailnet. O restante da auditoria continua
valendo: agente dono do PTY, Event Log + Screen Sync, grants, biometria e
minimização de dados.

Legenda: **[FATO]** verificado hoje em fonte primária · **[INFERÊNCIA]** ·
**[RECOMENDAÇÃO]**.

## 1. Pedido

> Usuário instala o plugin no VS Code, o plugin gera um código (estilo
> AnyDesk) para aquele computador. Instala o app no celular, entra com o
> código, e está rodando. Algo simples. Tunelamento, por segurança. Sem
> terceiros. Talvez usar o tunelamento já presente no VS Code.

## 2. Por que não o túnel do VS Code

**[FATO]** O port forwarding do VS Code usa o Microsoft Dev Tunnels. Os
problemas, um a um:

- **Login obrigatório.** É preciso entrar com conta GitHub ou Microsoft.
  Uma porta privada só é acessível pela mesma conta; um app sem login
  precisaria de um token de cliente que **expira em 24 h** e só pode ser
  renovado pela identidade do dono.
  (https://code.visualstudio.com/docs/debugtest/port-forwarding,
  https://learn.microsoft.com/azure/developer/dev-tunnels/security)
- **O TLS termina na borda da Microsoft,** e o relay é dela.
- **Limites de uso:** 5 GB/mês por usuário.
- **Serviço em preview, voltado a desenvolvimento.** Fica "for adhoc testing
  and development, not for production workloads", em *public preview*, sem
  SLA.
- **A API de extensão é proposta, não estável.** A API para criar túneis
  (`workspace.openTunnel`) é *proposed* e não pode ir para o Marketplace. O
  Remote Tunnels (`code tunnel`) só conecta clientes VS Code, com a mesma
  conta nas duas pontas. (https://code.visualstudio.com/docs/remote/tunnels)

**Conclusão:** é terceiro (Microsoft + GitHub), exige login e tem API
instável para extensões. **Descartado.**

## 3. O fato de rede que define o desenho

**[FATO]**

- A perfuração de NAT falha quando os dois lados estão atrás de NATs "não
  bem-comportados", e um relay é obrigatório nesses casos (RFC 8656;
  https://tailscale.com/blog/how-nat-traversal-works).
- Com CGNAT, redirecionamento de porta e P2P deixam de funcionar (NIC.br).

**[FATO, medido hoje no PC]** A rede de casa tem NAT duplo, com
`192.168.0.1` → `192.168.1.1` → `172.16.255.2`. Esse endereço privado já
dentro da operadora é forte indício de CGNAT; confirmar comparando o IP de
WAN do modem com o IP público. A rede também não tem IPv6 global (só
`fd81::`, ULA).

**[INFERÊNCIA]** Para o celular achar o PC só com um código, de qualquer
rede, **algum ponto com endereço alcançável** precisa fazer a ponte. O
AnyDesk e o RustDesk funcionam assim: servidor de ID/encontro + relay
(https://rustdesk.com/docs/en/self-host/). "Sem terceiros" passa a
significar **uma ponte sua que não consegue ler nada**, não "nenhum
servidor".

## 4. Arquitetura proposta

```text
 PC (casa, atrás de CGNAT)            PONTE (sua)                    Celular (4G/Wi-Fi)
┌──────────────────────┐        ┌─────────────────────┐        ┌──────────────────────┐
│ VS Code + extensão   │        │ trc-bridge (Rust)   │        │ App Android          │
│        │ IPC         │ saída  │ • encontro por ID   │ saída  │                      │
│ trcd (agente) ───────┼───────►│ • repasse de bytes  │◄───────┼── conecta ao ID do PC│
│  dono dos PTYs       │  WSS   │   CIFRADOS          │  WSS   │                      │
└──────────────────────┘        │ • sem contas, sem   │        └──────────────────────┘
                                │   disco, sem chaves │
                                └─────────────────────┘
        └────────── túnel cifrado ponta a ponta PC ⇄ celular (a ponte só vê bytes) ──────────┘
```

- **Nenhuma porta aberta no PC.** O agente e o celular fazem conexões de
  **saída** até a ponte, por isso o CGNAT dos dois lados deixa de importar.
  Só a ponte precisa ser alcançável.
- **A ponte é burra por construção:**
  - Associa "ID do computador" a uma conexão e copia bytes entre as duas
    pontas.
  - Não guarda nada em disco, não tem banco e não conhece nenhuma chave de
    sessão.
  - É um binário Rust de poucos MB, que roda num Raspberry Pi (ARM64) ou num
    VPS mínimo.
- **MVP sempre via ponte**, sem perfuração de NAT. O tráfego de terminal é
  pequeno (Screen Sync coalescido). Conexão direta na mesma rede Wi-Fi e
  perfuração de NAT ficam como otimizações futuras, sem mudar o protocolo.

### 4.1 Onde roda a ponte

| Opção | Requisito | Custo | Observação |
|---|---|---|---|
| **Raspberry Pi em casa** | IP público da operadora (pedir à operadora, às vezes modem em bridge) + porta redirecionada + nome DNS (subdomínio de `gariolilabs.com`, só DNS) | Zero | **Hoje há indício de CGNAT, o que bloqueia esta opção** até a operadora liberar IP público |
| **VPS mínimo** | Nenhum | ~US$ 4–6/mês | O provedor só vê bytes cifrados, IPs e horários |
| Google Compute Engine e2-micro (Always Free) | Região us-west1, us-central1 ou us-east1 (**[FATO]** southamerica-east1 fora do free tier) | **~US$ 3,65/mês**. **[FATO]** O IPv4 em uso custa US$ 0,005/h e o free tier do IP é de 1 h/mês. Saída para a América do Sul: 1 GB grátis, depois US$ 0,19/GiB (Premium) | Simples e sempre ligado. **[INFERÊNCIA]** Ida e volta Brasil↔EUA↔Brasil ≈ 0,25–0,35 s por comando |
| Google Cloud Run com conexão 24 h | — | **~US$ 43–61/mês**. **[FATO]** Instância com WebSocket aberto é cobrada como ativa; abaixo de 1 vCPU exige concorrência 1; timeout máximo de 60 min | **Descartado** |
| Google Cloud Run sob demanda (o PC consulta periodicamente se há chamada e só então abre o WebSocket) | max-instances=1 (**[FATO]** afinidade de sessão é *best effort*) | **[INFERÊNCIA]** Perto de zero em uso pessoal; o preço Tier 2 de São Paulo não foi confirmado | Até ~5 s para conectar; reconexão a cada 60 min; mais complexo |
| Os dois | — | — | O app aceita mais de uma ponte; se uma cair, usa a outra |

**Decisão da hospedagem adiada para a fase M6** (a ponte só é necessária
nela). Duas exigências valem desde já:

- **A ponte é um binário único**, que roda em qualquer lugar: Raspberry,
  e2-micro, VPS ou contêiner.
- **O protocolo da ponte suporta dois modos:** conexão permanente e
  "acordar sob demanda" (consulta periódica do agente).

Ação imediata e grátis: perguntar à operadora sobre IP público.

A meta de latência da auditoria (seção 13, 150 ms p95) vale para a ponte no
Brasil. Com ponte nos EUA, a meta passa a ser **≤ 400 ms p95 do envio à
atualização da tela**. O celular envia comandos compostos num campo de
texto, não tecla por tecla, então essa latência é aceitável.

**[RECOMENDAÇÃO]** Primeiro, perguntar à operadora sobre IP público. Se ela
liberar, a ponte fica no Raspberry. Se não liberar, a ponte vai para um VPS,
e o Raspberry fica em casa para uma função futura: **acordar o PC por
Wake-on-LAN** a pedido do celular, que resolve o PC dormindo.

## 5. O código (UX)

**No PC:**

- A extensão, no comando "Conectar celular", mostra:

  ```text
  Conectar celular
  Código:   4821 · 9137 2055        (vale 5 min, uso único)
  [QR]      (mesmo código + endereço da ponte)
  ```

**No celular:**

1. "Adicionar computador".
2. Digitar o código **ou** escanear o QR.
3. O PC mostra: *"Permitir 'Pixel 8' neste computador? [Permitir] [Recusar]"*.
4. Pronto. Nas próximas vezes basta abrir o app: o celular já conhece o PC,
   sem código.

**Formato:** 12 dígitos, só números, fáceis de digitar no teclado do
celular.

- Os **4 primeiros** são o "número de encontro". A ponte usa esse número só
  para juntar as duas pontas.
- Os **8 restantes** são o **segredo**. Ele **nunca sai dos aparelhos**; só
  alimenta a troca de chaves.

**Por que 8 dígitos bastam:**

- **[FATO]** A troca usa um PAKE (SPAKE2), o mesmo desenho do
  magic-wormhole: "the only way for a network attacker to learn the shared
  key is to perform a man-in-the-middle attack during the initial connection
  attempt, and to correctly guess the code".
  (https://magic-wormhole.readthedocs.io/en/latest/welcome.html)
- **[INFERÊNCIA]** Na prática:
  - O atacante tem **uma** tentativa por código, com 1 chance em 100
    milhões.
  - Um erro invalida o código de forma visível.
  - Não existe ataque offline, nem para quem controla a ponte.
  - A confirmação no PC é uma segunda barreira.

**Endereço da ponte:**

- O QR leva o endereço da ponte.
- Digitando o código, o app usa a ponte configurada nele (no uso pessoal, a
  sua, gravada na primeira instalação).

## 6. Criptografia

1. **Pareamento — só uma vez:**
   - SPAKE2 sobre o segredo de 8 dígitos gera uma chave forte temporária.
   - Protegidos por essa chave, os dois trocam e **fixam as chaves
     permanentes**:
     - o celular, uma chave P-256 no **Android Keystore**, não exportável;
     - o PC, a chave dele no cofre do Windows (DPAPI).
   - Os dois conferem os 6 dígitos de confirmação derivados da troca.
2. **Sessões seguintes:** **TLS 1.3 mútuo com chaves fixadas**, rodando
   *dentro* do fluxo repassado pela ponte:
   - rustls no PC; SSLEngine/Conscrypt no Android;
   - chave do cliente no Keystore;
   - a ponte vê só registros TLS.

**[FATO]** Tanto `spake2` quanto `snow` (Noise) declaram no README que não
passaram por auditoria independente. O Noise também não aceita senha curta
como PSK: a especificação exige 256 bits (§15.1).

**[RECOMENDAÇÃO]** Por isso a escolha é **TLS 1.3 para todas as sessões**
(biblioteca amplamente usada e revisada) e SPAKE2 **só no pareamento**,
com vetores de teste e revisão de segurança dedicada. A alternativa, Noise
`IK` nas sessões, fica registrada e não é adotada.

**[FATO]** As implementações de referência têm licença copyleft:
magic-wormhole.rs é EUPL e RustDesk é AGPL-3.0. **Reaproveitar o desenho,
não o código**, a menos que o produto seja open source compatível.

## 7. Ameaças novas (complementam a seção 6 da auditoria)

| Ameaça | Mitigação |
|---|---|
| Ponte comprometida ou provedor do VPS curioso | Só vê IPs, horários e tamanhos. Não consegue MITM no pareamento sem acertar o código na única tentativa, nem depois, porque as chaves estão fixadas. |
| Alguém vê o código na tela | Validade de 5 min, uso único e confirmação no PC. |
| Adivinhação do código | PAKE: uma tentativa online por código e invalidação visível. A ponte limita tentativas por IP. |
| Ponte usada por estranhos | O agente se registra com uma **chave de inscrição da ponte**, gerada na instalação da ponte. Sem ela, nenhum PC se registra. |
| Negação de serviço na ponte | Afeta só a disponibilidade, nunca a confidencialidade. Várias pontes são aceitas. |
| Metadados: quando você usa o terminal | Aceito e declarado. A ponte vê o padrão de uso, nunca o conteúdo. |

## 8. O que muda na auditoria

- **Removido:** Tailscale, bind no IP 100.x, restrição de um VPN por vez no
  Android, pairing com endpoint do tailnet.
- **Novo componente:** `crates/trc-bridge` (ponte).
- **Fase M6 (rede segura) passa a ser:** ponte + pareamento por código + TLS
  fixado.
- **Mantido:** agente dono do PTY, perfil padrão "Terminal remoto" só
  leitura, arm por biometria, Event Log + Screen Sync, minimização de dados.
- **Revisão:** a parte criptográfica (pareamento e TLS fixado) exige revisão
  de segurança dedicada, no Fable com effort máximo, antes de qualquer
  código.
