# ADR-0006 — Hospedagem da ponte adiada para M6; a ponte suporta modo permanente e sob demanda

## Status

Aceita · 2026-09-26 · decidido por Sr. Garioli.

Registro da decisão: cabeçalho da proposta ("hospedagem da ponte decidida
na fase M6") e proposta §4.1, "Decisão da hospedagem adiada para a fase
M6". Endereço da ponte padrão decidido por Sr. Garioli em 2026-09-26
(`README.md` desta pasta, "Decididos depois da primeira versão", item 4).

**Atualizado em 2026-09-26 (mais tarde no mesmo dia):** a ponte padrão
pública foi substituída por ponte privada de Sr. Garioli; os demais
usuários hospedam a própria ponte (`README.md` desta pasta, item 5;
ADR-0004). A hospedagem que este ADR adia é só a de
`ponte.gariolilabs.com`.

## Contexto

- A ponte só é necessária na fase M6 (rede segura); antes disso o agente
  só escuta IPC local (proposta §4.1; auditoria §3 C5, §8).
- Opções levantadas, com custo (proposta §4.1):

| Opção | Custo | Situação |
|---|---|---|
| Raspberry Pi em casa | Zero | Exige IP público, porta redirecionada e DNS; **bloqueada** pelo indício de CGNAT até a operadora liberar IP público |
| VPS mínimo | ~US$ 4–6/mês | O provedor só vê bytes cifrados, IPs e horários |
| GCE e2-micro (Always Free, regiões dos EUA) | **~US$ 3,65/mês**: **[FATO]** IPv4 em uso a US$ 0,005/h, free tier do IP de 1 h/mês; saída para a América do Sul 1 GB grátis, depois US$ 0,19/GiB | **[INFERÊNCIA]** ida e volta Brasil↔EUA↔Brasil ≈ 0,25–0,35 s por comando |
| Cloud Run com conexão 24 h | **~US$ 43–61/mês**: **[FATO]** instância com WebSocket aberto é cobrada como ativa; timeout máximo de 60 min | **Descartado** |
| Cloud Run sob demanda (o PC consulta periodicamente se há chamada e só então abre o WebSocket) | **[INFERÊNCIA]** perto de zero em uso pessoal; preço Tier 2 de São Paulo não confirmado | Até ~5 s para conectar; reconexão a cada 60 min; mais complexo |
| Os dois (várias pontes) | — | O app aceita mais de uma ponte |

## Decisão

- **Onde hospedar fica para M6.** A escolha não bloqueia o planejamento
  nem M0–M5 (proposta §4.1).
- Duas exigências valem desde já (proposta §4.1):
  - a ponte é **um binário único**, que roda em Raspberry, e2-micro, VPS
    ou contêiner;
  - o protocolo da ponte suporta **dois modos:** conexão permanente e
    "acordar sob demanda" (consulta periódica do agente).
- **Cloud Run com conexão 24/7 está descartado** por custo (proposta
  §4.1).
- Ação imediata e grátis: perguntar à operadora sobre IP público (proposta
  §4.1).
- **O endereço já está decidido; o lugar, não.** `ponte.gariolilabs.com`
  é a ponte **privada** de Sr. Garioli e de quem ele autorizar (decidido
  por Sr. Garioli, 2026-09-26; ADR-0004). **[INFERÊNCIA]** o nome DNS
  isola a escolha de hospedagem: o domínio pode apontar para Raspberry,
  e2-micro, VPS ou Cloud Run sem mudar a configuração dos clientes.
- **Não há ponte pública.** Os demais usuários rodam o mesmo binário no
  servidor, VPS ou Raspberry deles e configuram o endereço na extensão na
  primeira vez (ADR-0004). As duas exigências acima (binário único, dois
  modos) valem também para essas pontes.

## Alternativas consideradas

| Alternativa | Por que caiu |
|---|---|
| Decidir a hospedagem agora | Sem necessidade antes de M6; depende da resposta da operadora sobre IP público (proposta §4.1). |
| Cloud Run 24/7 | ~US$ 43–61/mês (proposta §4.1). |
| Ponte só em modo permanente | Impediria a opção sob demanda de custo perto de zero (proposta §4.1). |
| Ponte pública para qualquer usuário | Substituída por ponte privada em 2026-09-26 (ADR-0004). |

## Consequências

**Positivas**

- A escolha fica reversível: o mesmo binário roda em qualquer destino
  (proposta §4.1).
- O custo pode ficar entre zero e ~US$ 6/mês, conforme a opção (proposta
  §4.1).
- **[INFERÊNCIA]** Com a ponte privada, a carga é de uso pessoal e de um
  grupo pequeno autorizado; o dimensionamento cabe com folga no e2-micro
  ou num Raspberry (`requisitos-nao-funcionais.md` DP-4, NFR-16).

**Negativas**

- O protocolo da ponte (P4) precisa especificar os dois modos, o que custa
  mais desenho do que um só (proposta §4.1; mapa P4).
- Modo sob demanda: até ~5 s para conectar e reconexão a cada 60 min
  (proposta §4.1).
- A meta de latência depende de onde a ponte fica: 150 ms p95 com ponte no
  Brasil, ≤ 400 ms p95 do envio à atualização da tela com ponte nos EUA
  (proposta §4.1; auditoria §13).
- **[RECOMENDAÇÃO, não decisão]** Se a operadora liberar IP público, a
  ponte fica no Raspberry; senão, vai para um VPS, e o Raspberry fica em
  casa para acordar o PC por Wake-on-LAN (proposta §4.1).
- Quem hospeda a própria ponte precisa de instruções de instalação do
  `trc-bridge` (servidor, VPS, Raspberry), incluindo o aviso de CGNAT; é
  documentação a escrever junto com P4/M6.

## Referências

- `docs/proposta-conexao-por-codigo-2026-09-26.md` cabeçalho, §3, §4.1,
  §8.
- `docs/auditoria-arquitetura-2026-09-26.md` §3 C5, §8, §13.
- `docs/plans/00-mapa-do-planejamento.md` P4.
- `docs/requisitos-nao-funcionais.md` DP-4, NFR-16.
