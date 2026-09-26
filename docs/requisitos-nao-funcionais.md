# Requisitos não funcionais (P8)

Status: **rascunho para revisão**, 2026-09-26. Entrega P8 de
`docs/plans/00-mapa-do-planejamento.md`. Planejamento: nada aqui foi
medido. Este documento fixa **metas, condições e método**; as medições
acontecem nas fases M0 a M8, com o método descrito aqui.

- Dono: P8 (requisitos não funcionais).
- Entradas: auditoria §13 (leveza), proposta de conexão por código §4.1
  (latência com ponte), spec TRCP/1 (§3, §8, §9, §14, §17, §19),
  ADR-0001 a ADR-0014, interfaces aprovadas, `docs/exigencias-externas.md`
  (EX1).
- Não muda a spec, os ADRs nem as telas. Onde um número daqui pede mudança
  em outro documento, o item vai para §7 (pontos em aberto) ou §6
  (decisões pendentes).

## Sumário

0. Sobre este documento
1. Referência de medição: hardware, redes, cargas, estatística,
   ferramentas
2. Contas explícitas (estimativas)
3. Requisitos (NFR-01 a NFR-61)
4. Validação dos números da spec, linha a linha
5. Decisão do histórico (scrollback)
6. Decisões pendentes (Sr. Garioli)
7. Pontos em aberto
8. Quadro-resumo dos NFRs
9. Referências

## 0. Sobre este documento

### 0.1 Rótulos

- **[FATO]**: conferido em 2026-09-26 em fonte oficial; o link está ao
  lado ou em §9.
- **[INFERÊNCIA]**: conclusão a partir de fatos. "Validar no Mx" quando
  precisa de prova antes de virar critério.
- **[ESTIMATIVA]**: conta feita aqui, com as premissas escritas. Não é
  medição. A fase indicada mede o valor real e substitui a estimativa.
- **[PROPOSTA]**: meta nova deste documento, sem origem anterior; entra
  em vigor quando a revisão aprovar.

### 0.2 Como ler um NFR

Cada requisito tem os mesmos campos:

- **Meta**: o número, com a unidade.
- **Condição**: hardware (§1.1), rede (§1.2) e carga (§1.3) em que a meta
  vale. Fora da condição, a meta não se aplica.
- **Método**: como medir e com qual ferramenta (§1.5).
- **Aprovação**: estatística e janela (§1.4). Passa quando **todas** as
  execuções exigidas passam, não a média delas.
- **Fase**: onde é medido pela primeira vez e onde vira teste de
  regressão (fases da auditoria §8: M0 spikes, M1 spec, M2 agente local,
  M3 CLI, M4 extensão, M5 contexto, M6 rede e ponte, M7 Android, M8
  push).
- **Origem**: de onde veio o número.

### 0.3 Precedência

Mesma da spec (§0.1 dela): telas aprovadas, depois ADRs, depois a spec,
depois este documento, depois auditoria e proposta. Os números da spec
marcados **[P8]** passam a ter o veredito de §4 daqui; os marcados
**fixo** na spec não mudam aqui.

## 1. Referência de medição

### 1.1 Hardware de referência

| Id | O quê | Descrição | Uso |
|---|---|---|---|
| PC-R1 | PC principal | A máquina de desenvolvimento de Sr. Garioli: Windows 11 Home, build 10.0.26200 (dado do ambiente desta sessão). CPU, RAM, disco, plano de energia e antivírus **registrados no relatório do M0**. Na tomada, plano "Equilibrado". | Todas as metas do agente e da extensão |
| PC-R2 | PC fraco simulado | O mesmo PC-R1 com o agente preso a **um núcleo**: `start /affinity 1 trcd.exe` (**[FATO]** `start` aceita `/affinity`, https://learn.microsoft.com/windows-server/administration/windows-commands/start). | Verifica que as metas de CPU não dependem de muitos núcleos |
| A-R1 | Celular principal | O aparelho de Sr. Garioli. Modelo, versão do Android e RAM **registrados no relatório do M7**. | Latência, abrir o app, bateria, dados |
| A-R2 | Celular de entrada | Emulador Android com 2 GB de RAM e 2 núcleos, na menor versão do Android que o app suportar (minSdk ainda não definido, §7 PA-9). | Memória e fluidez no piso |
| A-R3 | Medidor de energia (opcional) | Pixel 6 ou mais novo, único com o Power Profiler (**[FATO]**, ver §1.5). Depende da decisão DP-5. | Energia em mW, só informativa |
| B-BR | Ponte no Brasil | VPS de 1 vCPU e 1 GB em São Paulo, Linux. | Metas "ponte no Brasil" |
| B-US | Ponte nos EUA | GCE e2-micro, Linux. **[FATO]** e2-micro: 2 vCPUs visíveis, fração de 0,25 vCPU sustentada (cada vCPU a 12,5 % do tempo), rajada de ~30 s a 100 %, 1 GB de RAM, saída de até 1 Gbps (https://docs.cloud.google.com/compute/docs/general-purpose-machines). Grátis só em us-west1, us-central1 e us-east1 (https://docs.cloud.google.com/free/docs/free-cloud-features). | Metas "ponte nos EUA" e capacidade da ponte |

- **[INFERÊNCIA]** Entre as três regiões grátis, us-east1 (Carolina do
  Sul) deve ter o menor RTT até o Brasil. Validar no M6 medindo o RTT
  real de casa e do 4G até uma VM de teste em cada região, antes de
  escolher (a escolha da hospedagem é do M6, ADR-0006).
- Enquanto B-BR e B-US não existem (antes do M6), as metas de rede são
  medidas com uma ponte local e o atraso simulado de §1.2.

### 1.2 Redes de referência

| Id | Nome | Como se obtém |
|---|---|---|
| N0 | Ideal | Tudo na mesma rede local, sem modelagem. Serve para isolar o custo do software. |
| N1 | Wi-Fi de casa | A rede real de Sr. Garioli (NAT duplo, indício de CGNAT, proposta §3), celular no Wi-Fi. |
| N2 | 4G | Celular no 4G da operadora dele, Wi-Fi desligado. |
| N3 | Rede ruim | +300 ms de RTT e **5 % de perda em cada sentido** na perna do celular. |
| N4 | EUA simulado | +250 ms de RTT na perna da ponte, sem perda. Só até existir B-US. |
| N5 | Queda | Perda de 100 % por 10 s e por 60 s (buraco negro), e troca Wi-Fi↔4G. |

Ferramentas para N3 a N5:

- **Linux (`tc netem`)**, no computador que faz o papel de celular no
  harness (§1.5) ou na própria ponte. **[FATO]** sintaxe
  `delay TEMPO [VARIAÇÃO] … loss PORCENTAGEM`
  (https://man7.org/linux/man-pages/man8/tc-netem.8.html). Exemplo a
  conferir no M6, só na saída de uma interface:

  ```text
  tc qdisc add dev eth0 root netem delay 150ms 20ms loss 5%
  ```

  A entrada recebe o mesmo por uma interface `ifb`, para os dois
  sentidos somarem os 300 ms.
- **Windows (clumsy)**, no PC, para atrasar ou perder pacotes do agente.
  **[FATO]** clumsy tem atraso, descarte, estrangulamento, duplicação,
  reordenação e adulteração de pacotes, e usa o WinDivert
  (https://jagt.github.io/clumsy/).
- **Emulador Android**, para testes de tela com rede lenta. **[FATO]**
  `-netdelay min:max` e `-netspeed up:down`
  (https://developer.android.com/studio/run/emulator-commandline).
- N5 no aparelho real: modo avião por 10 s e por 60 s; troca Wi-Fi↔4G
  desligando o Wi-Fi com a tela aberta.

### 1.3 Cargas de referência

Cada carga é um script determinístico, descrito aqui e escrito em P9
(fixture de medição, não código de produto).

| Id | Nome | O que faz |
|---|---|---|
| C0 | Agente vazio | Agente rodando, nenhuma sessão, extensão conectada, ligado à ponte (a partir do M6). |
| C1 | Prompt parado | Sessões de `pwsh` paradas no prompt, 120 × 32. |
| C2 | Claude trabalhando | Script que imita a tela do Claude Code trabalhando: 1 linha de spinner reescrita a cada 100 ms, 1 linha de cronômetro a cada 1 s, e um bloco de 10 linhas novas por minuto. Uma rodada com o Claude Code real confere o script. |
| C3 | Log contínuo | 20 linhas por segundo, 80 caracteres, 2 cores por linha (imita `npm run dev`). |
| C4 | Rajada de texto | `type` (cmd) ou `Get-Content -Raw` de um arquivo de 100 MB de texto em linhas de 80 colunas. |
| C5 | TUI densa | Tela cheia 120 × 32 redesenhada a 30 Hz, 8 trocas de cor por linha (imita `htop`/`btop` e animações coloridas). |

Tamanho padrão: **120 × 32** (o exemplo da spec §9.3). As metas por
sessão valem nesse tamanho; outros tamanhos são reportados, não
aprovados (§2.1 mostra a proporção).

### 1.4 Regras estatísticas

- **Aquecimento:** descartar os primeiros 2 min de cada execução (cache,
  JIT do app, conexões).
- **Amostras de memória e CPU:** 1 por segundo. Critério sobre o p95 das
  amostras da janela, mais um teto no máximo.
- **CPU:** tempo de processador consumido (`TotalProcessorTime`) na
  janela, dividido pelo tempo de relógio. "1 núcleo" = 100 %.
- **Latência:** p50, p95 e p99, mais o máximo.
  - p95 só com **N ≥ 200** amostras; p99 só com **N ≥ 1 000**.
  - Redes reais (N1, N2): **3 execuções** em horários diferentes
    (manhã, tarde, noite); passa se passar em cada uma.
- **Relatório:** data, commit, hardware, rede, carga, N, percentis, e o
  arquivo bruto das amostras. Sem relatório, a meta conta como não
  medida.
- **Regressão (a partir do M2):** as metas de memória e CPU do agente
  viram teste automático com margem de 20 % acima da meta, para absorver
  a variação de máquina de CI. A meta exata vale no PC-R1 a cada
  release.

### 1.5 Ferramentas

| Onde | Ferramenta | Para quê | Fonte |
|---|---|---|---|
| Windows | `Get-Process trcd` → `PrivateMemorySize64`, `WorkingSet64`, `TotalProcessorTime` | Memória e CPU do agente, amostradas por script | https://learn.microsoft.com/powershell/module/microsoft.powershell.management/get-process |
| Windows | Contadores de desempenho (`typeperf "\Process(trcd)\Private Bytes"` e `% Processor Time`) | Mesma medida, sem script próprio | https://learn.microsoft.com/windows-server/administration/windows-commands/typeperf |
| Windows | WPR + WPA (ETW) | Trocas de contexto, despertares, CPU exata por thread, pilhas | https://learn.microsoft.com/windows-hardware/test/wpt/windows-performance-recorder |
| Windows | Typometer | Latência tecla → caractere na tela do VS Code, por captura de tela | https://pavelfatin.com/typometer/ |
| Windows | `powercfg /a`, `powercfg /sleepstudy`, PsShutdown `-d` | Estados de sono do PC e forçar o sono | https://learn.microsoft.com/windows-hardware/design/device-experiences/powercfg-command-line-options, https://learn.microsoft.com/sysinternals/downloads/psshutdown |
| VS Code | "Developer: Show Running Extensions" (tempo de ativação) e "Developer: Open Process Explorer" (memória do extension host) | Ativação e memória da extensão | **[INFERÊNCIA — validar no M4]**: comandos conhecidos, citados em https://github.com/microsoft/vscode/issues/174255; não achei página oficial que os descreva |
| Agente | Instrumentação própria (spans com relógio monotônico, só em build de medição) | Decompor a latência dentro do agente (NFR-22) | P9 define |
| Harness | Cliente de medição do perfil remoto (`trc-bench`, a especificar em P9), rodando em Linux com `netem` | Latência e dados com N ≥ 1 000, repetível | P9 define |
| Android | Macrobenchmark: `StartupTimingMetric` (TTID/TTFD), `FrameTimingMetric` (p50–p99 de `frameOverrunMs`), `PowerMetric` (Pixel 6+) | Abrir o app, fluidez, energia | https://developer.android.com/topic/performance/benchmarking/macrobenchmark-metrics |
| Android | `reportFullyDrawn()` | Marca o "pronto para uso" (TTFD) quando a lista ao vivo aparece | https://developer.android.com/topic/performance/vitals/launch-time |
| Android | Perfetto (trace de sistema e seções próprias `Trace.beginAsyncSection`) | Envio → frame aplicado → quadro na tela; CPU por processo | https://perfetto.dev/docs/ |
| Android | `adb shell dumpsys batterystats --reset` e `dumpsys batterystats <pacote>` | Wakelocks, jobs, rádio e CPU por app | https://developer.android.com/topic/performance/power/setup-battery-historian |
| Android | Power Profiler (Android Studio) | Energia por trilho (ODPM), só Pixel 6+ com Android 10+ | https://developer.android.com/studio/profile/power-profiler |
| Android | `dumpsys meminfo <pacote>` | PSS do app | https://developer.android.com/tools/dumpsys |
| Android | `TrafficStats.getUidRxBytes/getUidTxBytes` e `dumpsys netstats detail` | Bytes do app por janela | https://developer.android.com/reference/android/net/TrafficStats |
| Android | `adb shell dumpsys deviceidle force-idle` e `am set-inactive <pacote> true` | Forçar Doze e App Standby | https://developer.android.com/training/monitoring-device-state/doze-standby |
| Android | `bundletool get-size total --apks=…` e APK Analyzer | Tamanho de download | https://developer.android.com/tools/bundletool |
| Ponte | `/proc/<pid>/status` (`VmRSS`), `ss -tmi` (memória por socket), contadores próprios de bytes por conexão | Memória e tráfego da ponte | páginas de manual do Linux |
| Todos | Vídeo a 240 quadros/s com as duas telas no quadro | Latência "vidro a vidro" (toque → eco), sem sincronizar relógios; resolução ~4 ms | — |

**[FATO]** o Battery Historian não é mais mantido; a documentação
recomenda trace de sistema, a métrica de energia do Macrobenchmark ou o
Power Profiler
(https://developer.android.com/topic/performance/power/setup-battery-historian).
Por isso ele só aparece aqui como leitor do `bugreport`, nunca como
critério.

**Relógios entre aparelhos.** Latências que começam num aparelho e
terminam em outro (NFR-33, NFR-61) exigem o mesmo relógio. Método:
celular ligado por USB ao PC só para medir (o tráfego do app continua no
Wi-Fi ou 4G), diferença de relógio estimada por troca de carimbos via
`adb` repetida 20 vezes, com o erro reportado; aceitar a execução só se
o erro for ≤ 5 ms. Alternativa sem relógio: vídeo a 240 quadros/s.

## 2. Contas explícitas (estimativas)

Todas as contas desta seção são **[ESTIMATIVA]**. As premissas estão
escritas para que a medição de cada fase possa trocá-las pelo valor
real.

### 2.1 Memória do histórico por sessão

Premissa: o emulador guarda cada célula da grade como uma estrutura de
**24 bytes** (4 do caractere, 4 da cor de frente, 4 da cor de fundo,
2 de atributos, 2 de alinhamento e 8 de um ponteiro para dados extras).
**[INFERÊNCIA — validar no M0]** é a ordem de grandeza de
`alacritty_terminal`; o M0 mede `size_of` da célula do emulador escolhido
(`alacritty_terminal` ou `vt100`). Premissa 2: o histórico guarda linhas
na largura cheia, como a grade.

Fórmula: `bytes = linhas × colunas × 24`.

| Linhas | 80 col. | 120 col. | 200 col. |
|---|---|---|---|
| 1 000 | 1,92 MB | 2,88 MB | 4,80 MB |
| 2 000 | **3,84 MB** | **5,76 MB** | 9,60 MB |
| 5 000 | 9,60 MB | 14,40 MB | 24,00 MB |

- Grade visível 120 × 32: `120 × 32 × 24 = 92 160 B` ≈ 0,09 MB.
- Buffers do PTY: duas threads por sessão (**[FATO]** a Microsoft
  recomenda uma thread por canal do pseudoconsole para evitar deadlock,
  https://learn.microsoft.com/windows/console/creating-a-pseudoconsole-session),
  com ~64 KB cada ≈ 0,13 MB.
- Estrutura da sessão, contexto e sobras: ~0,1 MB.

Conclusão: com 2 000 linhas em largura cheia, a meta de **5 MB por
sessão só cabe até ~104 colunas** (`5 000 000 / (2 000 × 24)`). A 120
colunas, 2 000 linhas passam da meta em ~1 MB. 5 000 linhas (auditoria
§7.1) não cabem em nenhuma largura comum. Decisão em §5.

Alternativa compacta (se o emulador deixar copiar as linhas que saem do
topo para um depósito próprio): texto UTF-8 + corridas de atributo.

- Linha típica: 60 B de texto + 3 corridas × 12 B + 24 B de vetor + 16 B
  de cabeçalho ≈ **136 B**. 2 000 linhas ≈ 0,27 MB; 5 000 ≈ 0,68 MB.
- Linha densa (120 caracteres, 60 trocas de cor): ≈ 1 KB. 5 000 linhas
  ≈ 5 MB.

### 2.2 Memória base do agente

- Cache de página do SQLite: **[FATO]** o padrão é `-2000`, "limited to
  2048000 bytes of memory" (https://www.sqlite.org/pragma.html). É 10 %
  da meta de 20 MB; o agente PODE baixar o cache (ex.: `-512`) porque o
  banco é pequeno.
- Event Log: 10 000 eventos (retenção da spec) × ~400 B ≈ **4 MB** se
  ficar todo em memória. Por isso o log mora no SQLite e só a cauda fica
  em memória (§7 PA-6).
- Resultados para `cmd.status`: 256 por principal × 9 principais (8
  aparelhos + `local`) × ~200 B ≈ **0,46 MB**.
- Runtime assíncrono, TLS, pipe local e conexão com a ponte: alguns MB.
  **[INFERÊNCIA]** um runtime de poucas threads cabe; muitas threads de
  trabalho somam pilha comprometida. Medir no M0.
- Soma estimada: **6 a 12 MB** com C0, abaixo dos 20 MB da meta.

### 2.3 Memória por conexão remota no agente e na ponte

- Estado de Screen Sync por assinatura: o agente precisa da versão
  confirmada e das até W = 4 em voo (R9.14–R9.16).
  - Guardando a grade inteira por versão: `5 × 92 160 B` ≈ 0,46 MB por
    assinatura; 2 assinaturas × 8 conexões ≈ 7,4 MB.
  - Guardando só um hash de 8 B por linha por versão:
    `5 × 32 × 8 = 1 280 B` por assinatura. O conteúdo das linhas trocadas
    sai da grade atual. **Recomendação para o M2**, não muda o
    protocolo.
- Buffers de WebSocket: **[FATO]** o `tungstenite` usa por padrão
  128 KiB de leitura, 128 KiB de escrita, fila de escrita sem limite e
  mensagem de até 64 MiB
  (https://docs.rs/tungstenite/latest/tungstenite/protocol/struct.WebSocketConfig.html).
  Sem configurar, são ~256 KiB por conexão e um teto de mensagem 256
  vezes maior que o da spec. Ajustar para 16–32 KiB e `max_message` =
  256 KB (§7 PA-7).
- TLS (rustls): ~2 registros de 16 KB em trânsito por sentido.
- Meta resultante: **≤ 512 KB por conexão remota no agente** e
  **≤ 64 KB por conexão ociosa na ponte** (NFR-07, NFR-15).

### 2.4 Tamanho das mensagens de tela

Contagem de bytes do JSON da spec (§9.3), com ids de 26 caracteres:

| Mensagem | Conta | Bytes |
|---|---|---|
| Envelope de frame, sem linhas | `v, t, k, s, id, ts, p{ver, base, cols, rows, size_src, alt, top, hgen, cursor, scroll}` | ~230 |
| Linha simples (60 caracteres, 1 trecho) | `{"i":30,"spans":[{"text":"…","fg":2,"a":1}]}` | ~100 |
| Linha densa (120 caracteres, 8 trechos) | 120 + 8 × 22 + 16 | ~310 |
| Linha adversária (120 células, cor RGB em cada uma) | 120 × ~42 | ~5 000 |
| `screen.ack` | `v, t, k, s, id, ts, p{ver}` | ~110 |

Sobrecarga de transporte por mensagem pequena: WebSocket interno (2–8 B),
TLS interno (5 B de cabeçalho + 1 B de tipo + 16 B de etiqueta AES-GCM,
**[FATO]** RFC 8446 §5.2), WebSocket externo até a ponte (2–14 B), TLS
externo (22 B), TCP/IP (~52 B por pacote). Total ≈ **110 B**.

Frames resultantes:

| Frame | Bytes |
|---|---|
| Diff de 1 linha (spinner) | 230 + 100 ≈ **330** |
| Completo, texto simples (32 linhas × 100 B) | ≈ **3,4 KB** |
| Completo, TUI densa (32 × 310 B) | ≈ **10,1 KB** |
| Completo, adversário (32 × 5 000 B) | ≈ **160 KB** (cabe em 256 KB a 120 × 32; não cabe a 300 × 80) |

### 2.5 Dados móveis por minuto de tela aberta

Premissas: fps efetivo = `min(20, W / RTT)` (R9.16–R9.17); um ack por
frame (R9.20 permite acumular; o cenário é o pior simples); ping a cada
20 s sem tráfego (R3.10).

| Carga | Conta | Por minuto |
|---|---|---|
| C1, terminal aberto e parado | ping + pong + ACKs TCP ≈ 370 B a cada 20 s, nas duas camadas (interna e da ponte) | ≈ **2 KB** |
| Lista de terminais aberta, sem terminal | ~30 eventos/min × ~300 B + pings | ≈ **10 KB** |
| C2, Claude trabalhando | 10 frames/s × (430 + 110) B descendo + 10 acks/s × 220 B subindo ≈ 7,6 KB/s | ≈ **0,46 MB** |
| C3, log contínuo | 20 frames/s × 440 B + 20 acks × 220 B ≈ 13 KB/s | ≈ **0,8 MB** |
| C4, rajada de texto (ponte BR, 20 fps) | 20 × (3,4 KB + 110 B) + acks ≈ 75 KB/s | ≈ **4,5 MB** |
| C5, TUI densa (ponte BR, 20 fps) | 20 × (10,1 KB + 110 B) + acks ≈ 209 KB/s | ≈ **12,5 MB** |
| C5 com ponte nos EUA (RTT ~300 ms → ~13 fps) | 13 × 10,2 KB + acks | ≈ **8 MB** |
| Adversário 120 × 32 a 20 fps | 20 × 160 KB = 3,2 MB/s | ≈ **190 MB** |

- O pior caso sem teto de bytes é caro em dados móveis. Com um teto de
  **64 KB/s por assinatura** no agente (DP-3), C5 e o adversário ficam
  em ≈ **3,9 MB/min**. **[INFERÊNCIA]** o teto não muda o protocolo: a
  spec fixa só o máximo de frames (R9.17); mandar menos é permitido.
- Sem compressão (D-15, R3.9): **[INFERÊNCIA]** texto JSON comprime 3–5
  vezes; a economia não paga o risco de vazamento por tamanho. Os
  orçamentos acima já são sem compressão.

### 2.6 Orçamento de latência: enviar → eco

Caminho: toque em Enviar → celular → ponte → agente → PTY → shell ecoa
→ emulador → frame → ponte → celular → quadro na tela.

| Trecho | Estimativa |
|---|---|
| App: montar JSON, cifrar, escrever no socket | ≤ 10 ms |
| Rede: 1 RTT do caminho inteiro (celular↔ponte↔agente) | ver abaixo |
| Ponte: repasse, 2 vezes | ≤ 2 ms |
| Agente: validar, autorizar, escrever no PTY | ≤ 2 ms |
| ConPTY + shell ecoando | 5–30 ms **[INFERÊNCIA — validar no M0]** |
| Emulador + diff + JSON | ≤ 3 ms |
| Coalescência | 0 ms se a primeira mudança depois de ≥ 50 ms parado sai na hora (borda de subida); até 50 ms se esperar o tique |
| App: aplicar frame e desenhar | 1–2 quadros (16–33 ms) |
| **Soma sem a rede** | **≈ 35–130 ms** |

RTT do caminho inteiro **[INFERÊNCIA — validar no M0/M6]**:

| Cenário | Celular↔ponte | Ponte↔PC | Caminho | Enviar→eco típico |
|---|---|---|---|---|
| Ponte BR, Wi-Fi | ~20 ms | ~20 ms | ~40 ms | ~75–170 ms |
| Ponte BR, 4G | ~40–80 ms | ~20 ms | ~60–100 ms | ~95–230 ms |
| Ponte EUA, Wi-Fi | ~120 ms | ~120 ms | ~240 ms | ~275–370 ms |
| Ponte EUA, 4G | ~160–200 ms | ~120 ms | ~280–320 ms | ~315–450 ms |

Consequências:

- 150 ms p95 com ponte no Brasil é alcançável no Wi-Fi e apertado no 4G
  (DP-2).
- 400 ms p95 com ponte nos EUA é alcançável no Wi-Fi e apertado no 4G
  (DP-2).
- A coalescência precisa de **borda de subida**: a primeira mudança
  depois de um período parado sai sem esperar o tique de 50 ms (§7
  PA-13).

### 2.7 Tempo de abrir o app até a lista ao vivo

Viagens de ida e volta até a lista de terminais aparecer (modo
permanente da ponte, ADR-0006):

- até a ponte: TCP (1) + TLS 1.3 externo (1) + Upgrade WebSocket (1) = 3
  RTT celular↔ponte;
- encontro com o agente já registrado na ponte (P4): ~1 RTT ponte↔PC;
- ponta a ponta: TLS 1.3 mútuo (1) + Upgrade WebSocket interno (1) +
  `hello` (1) + `auth` (1) + `resume` e snapshot (1) = **5 RTT do
  caminho**.

| Cenário | Conta | Rede |
|---|---|---|
| Ponte BR, Wi-Fi | 3 × 20 + 20 + 5 × 40 | ≈ 0,28 s |
| Ponte BR, 4G | 3 × 60 + 20 + 5 × 80 | ≈ 0,60 s |
| Ponte EUA, Wi-Fi | 3 × 120 + 120 + 5 × 240 | ≈ 1,68 s |
| Ponte EUA, 4G | 3 × 180 + 120 + 5 × 300 | ≈ 2,16 s |

Somam-se a assinatura com a chave do Keystore (dezenas a centenas de ms;
**[INFERÊNCIA — validar no M7]**: chaves em StrongBox são mais lentas que
no TEE) e a partida do app, que pode correr em paralelo com a rede.
Com ponte nos EUA, os 5 RTT ponta a ponta dominam (§7 PA-11).

A lista de **computadores** não espera nada disso: os nomes vêm do
armazenamento local (`{agent_id, agent_name, bridge, fingerprint}`,
ADR-0012) e o estado online vem da presença na ponte (P4), ~3–4 RTT
celular↔ponte.

### 2.8 Saída de dados da ponte e custo

- Tudo que a ponte recebe ela reenvia: saída ≈ entrada.
- Uso típico estimado de uma pessoa: 1 h por dia de terminal aberto em C2
  = 7,6 KB/s × 3 600 s ≈ 27 MB por dia ≈ **0,82 GB por mês**.
- **[FATO]** o free tier do GCE dá 1 GB/mês de saída da América do Norte
  para todos os destinos, exceto China e Austrália
  (https://docs.cloud.google.com/free/docs/free-cloud-features). A
  proposta §4.1 registra US$ 0,19/GiB depois disso (Premium) e o IPv4 a
  US$ 0,005/h.
- 2 h por dia ≈ 1,6 GB/mês ≈ 0,6 GB acima do grátis ≈ US$ 0,11 a mais.
  Horas de C5 sem teto de bytes (12,5 MB/min = 0,75 GB/h) estouram o
  grátis numa única tarde: outro motivo para DP-3.

### 2.9 Taxa de `stale` esperada

Modelo **[INFERÊNCIA — modelo de Poisson, medir no M7]**: a tela muda com
taxa λ (mudanças visíveis por segundo); o envio é recusado se houver
mudança entre o frame que a pessoa viu e a chegada do envio no agente,
janela T ≈ RTT do caminho + idade do frame mostrado (≤ 50 ms).

`P(stale) ≈ 1 − e^(−λ·T)`

| Tela | λ | Ponte BR (T ≈ 0,1 s) | Ponte EUA (T ≈ 0,35 s) |
|---|---|---|---|
| Prompt parado (C1) | ~0 | ~0 % | ~0 % |
| Só um cronômetro por segundo | 1 | ~10 % | ~30 % |
| Claude trabalhando (C2) | 10 | ~63 % | ~97 % |
| Log contínuo (C3) | 20 | ~86 % | ~100 % |

Consequência: com o Claude Code trabalhando, enviar texto quase sempre dá
`stale` (a spec já prevê, §10.5 e §19.2 item 1). Ctrl+C e Esc são isentos
(R10.15) e as aprovações estruturadas vindas do adaptador não passam pela
precondição de tela (R10.29 vale só para pedido fora do adaptador).
Decisão em DP-6.

### 2.10 Vazão com perda (rede N3)

**[INFERÊNCIA — modelo de Mathis et al., 1997, citado de memória]**:
vazão TCP ≈ `(MSS / RTT) × (1,22 / √p)`. Com MSS = 1 400 B, RTT = 0,3 s
e p = 0,05: `4 667 × 5,46` ≈ **25 KB/s**.

- Frames com W = 4 deixam no máximo ~4 × 10 KB pendentes por assinatura:
  bem abaixo do teto de 1 MB por 30 s (R8.20). Em N3 o agente não deveria
  fechar conexões com 4429 por lentidão.
- Latência de um envio em N3: ~10 % das trocas perdem um pacote
  (`1 − 0,95²`) e pagam uma retransmissão (≥ 200 ms no Linux, ~RTT +
  variação). p95 ≈ RTT + 1 retransmissão ≈ 0,6–0,8 s; p99 com duas ≈
  1,5 s. Base de NFR-40.

## 3. Requisitos

### 3.1 Agente (`trcd`)

**NFR-01 — Agente ocioso: memória**

- Meta: **Private Bytes ≤ 20 MB** (p95 das amostras) e máximo ≤ 24 MB.
  Working Set reportado, sem critério.
- Condição: PC-R1, carga C0, 10 min depois do aquecimento.
- Método: `Get-Process trcd` a 1 Hz (`PrivateMemorySize64`,
  `WorkingSet64`); conferência com `typeperf "\Process(trcd)\Private
  Bytes"`.
- Aprovação: p95 e máximo na janela de 10 min, 3 execuções.
- Fase: M0 (medida indicativa no spike), M2 (teste de regressão), M6
  (de novo, com a conexão à ponte).
- Origem: auditoria §13 ("≤ 20 MB RSS"). **Ajuste deste documento:** no
  Windows não existe RSS; o Working Set pode ser aparado pelo sistema a
  qualquer momento e daria número bom sem o agente ser leve. **[FATO]**
  `PrivateMemorySize64` equivale ao contador Private Bytes, a memória que
  não pode ser compartilhada com outros processos
  (https://learn.microsoft.com/dotnet/api/system.diagnostics.process.privatememorysize64).

**NFR-02 — Agente: memória por sessão**

- Meta: acréscimo de **Private Bytes ≤ 5 MB por sessão**, com o histórico
  cheio no teto definido em §5.
- Condição: PC-R1, sessões 120 × 32 com o histórico cheio (script que
  imprime linhas até o teto), 0 a 16 sessões.
- Método: abrir 0, 2, 4, 8 e 16 sessões; em cada ponto, Private Bytes do
  `trcd` (média de 60 s). Inclinação por regressão linear = custo por
  sessão. O `conhost` do ConPTY e o shell são processos à parte:
  **[INFERÊNCIA — validar no M0]** o ConPTY roda num processo de host
  próprio; o M0 mede e reporta a memória dele por sessão, sem entrar
  nesta meta (não é código nosso).
- Aprovação: inclinação ≤ 5 MB e nenhum ponto acima de
  `NFR-01 + n × 5 MB`.
- Fase: M0 (célula do emulador, §2.1), M2 (regressão).
- Origem: auditoria §13; ADR-0007 ("meta de ≤ 5 MB por sessão, ainda não
  medida").

**NFR-03 — Agente ocioso: CPU**

- Meta: **≤ 0,1 % de um núcleo** em média (≤ 0,6 s de CPU a cada
  10 min) e **≤ 2 despertares por segundo**, em média.
- Condição: PC-R1 e PC-R2; C0 e, separado, C1 com 8 sessões (meta com 8
  sessões: ≤ 0,2 %).
- Método: diferença de `TotalProcessorTime` em 10 min; despertares e
  trocas de contexto por WPR (perfil de CPU) e WPA.
- Aprovação: 3 execuções de 10 min.
- Fase: M0 (indicativa), M2 (regressão), M6 (com a ponte).
- Origem: auditoria §13 ("~0 % CPU, só eventos, sem polling"); o número
  é **[PROPOSTA]**.

**NFR-04 — Agente em uso: CPU**

- Meta: **≤ 2 % de um núcleo** em média.
- Condição: PC-R1, 4 sessões: 1 em C2 com o celular assistindo
  (assinatura ativa), 3 em C1. Ponte local (N0).
- Método: `TotalProcessorTime` numa janela de 5 min; WPR se passar.
- Aprovação: 3 execuções; também em PC-R2 com meta de 4 %.
- Fase: M2 (sem celular: assinatura feita pela CLI), M6 (com o harness
  remoto), M7 (com o app).
- Origem: auditoria §13.

**NFR-05 — Agente sob rajada de saída**

- Meta:
  - a memória não passa de `NFR-01 + NFR-02` durante a rajada (sem fila
    que cresça com a saída);
  - frames ao celular ≤ 20/s e bytes ≤ o teto de DP-3;
  - a CPU volta ao nível de NFR-04 em ≤ 1 s depois do fim da saída.
- Condição: PC-R1, C4 (100 MB) numa sessão assinada pelo celular.
- Método: amostras de 1 Hz durante e depois; contadores de frames e
  bytes por assinatura no agente (build de medição).
- Aprovação: 3 execuções.
- Fase: M2 (CLI), M6 (harness remoto).
- Origem: auditoria §13 ("tráfego limitado pela coalescência, não pelo
  volume"); ADR-0007.

**NFR-06 — Tamanho de instalação**

- Meta: `trcd.exe` ≤ 15 MB; VSIX por plataforma (com o agente dentro)
  ≤ 15 MB; binário da ponte ≤ 15 MB.
- Condição: build de release, sem símbolos.
- Método: tamanho dos arquivos; conteúdo do VSIX listado.
- Aprovação: a cada release.
- Fase: M2 (agente), M4 (VSIX), M6 (ponte).
- Origem: **[PROPOSTA]**; auditoria §13 ("a extensão traz o binário do
  agente, VSIX por plataforma"); proposta §4 ("binário Rust de poucos
  MB").

**NFR-07 — Agente: memória por conexão remota**

- Meta: **≤ 512 KB** de Private Bytes por conexão remota com 2
  assinaturas ativas.
- Condição: PC-R1, 0, 4 e 8 conexões do harness, cada uma com 2
  assinaturas em C2.
- Método: inclinação de Private Bytes contra o número de conexões.
- Aprovação: inclinação ≤ 512 KB.
- Fase: M6.
- Origem: **[PROPOSTA]**, conta de §2.3.

### 3.2 Extensão do VS Code

**NFR-08 — Ativação**

- Meta: ativação por `onStartupFinished`; `activate()` **≤ 100 ms p95**,
  sem esperar o agente subir (o agente sobe destacado, auditoria §4.3).
- Condição: PC-R1, VS Code sem outras extensões ativas, 20 aberturas.
- Método: "Developer: Show Running Extensions" (tempo de ativação), 20
  aberturas; conferência com um carimbo no início e no fim do
  `activate()` em build de medição.
- Aprovação: p95 das 20 aberturas.
- Fase: M4.
- Origem: auditoria §13 ("ativação `onStartupFinished`"). **[FATO]**
  `onStartupFinished` ativa a extensão "some time after VS Code starts
  up" e "will not slow down VS Code startup"
  (https://code.visualstudio.com/api/references/activation-events). O
  número é **[PROPOSTA]**.

**NFR-09 — Memória da extensão**

- Meta: acréscimo **≤ 10 MB** na memória do extension host com 8
  terminais do perfil ligados; **nenhum módulo nativo** no VSIX.
- Condição: PC-R1, mesma pasta aberta, com e sem a extensão.
- Método: "Developer: Open Process Explorer", memória do extension host
  com e sem a Pipa (A/B, 5 rodadas cada); listagem do VSIX sem arquivos
  `.node`.
- Aprovação: diferença das médias ≤ 10 MB.
- Fase: M4.
- Origem: auditoria §13 ("sem módulo nativo; só ponte IPC ⇄
  Pseudoterminal"); número **[PROPOSTA]**.

**NFR-10 — Terminal local passando pelo agente**

Com o perfil "Terminal remoto" como padrão (ADR-0002), **todo** terminal
do VS Code passa pela extensão, pelo pipe e pelo agente. Leveza aqui é
não deixar o terminal do dia a dia mais lento.

- Meta:
  - tecla → caractere no terminal do VS Code: **acréscimo ≤ 10 ms p95**
    sobre o terminal nativo com o mesmo shell;
  - abrir um terminal até o prompt aparecer: **acréscimo ≤ 150 ms p95**
    sobre o nativo.
- Condição: PC-R1, `pwsh`, C1, agente já rodando.
- Método: Typometer, 200 teclas por perfil; abertura com vídeo ou
  carimbo do primeiro `onDidWrite` depois do `open`, 30 aberturas por
  perfil.
- Aprovação: diferença dos p95.
- Fase: M0 (indicativa, com o spike de `Pseudoterminal`), M4.
- Origem: **[PROPOSTA]** derivada do ADR-0002 e do ADR-0001.

**NFR-11 — Vazão local**

- Meta: C4 termina no terminal do VS Code via agente em **≤ 1,5 × o
  tempo** do terminal nativo.
- Condição: PC-R1, mesmo arquivo, mesmo shell, janela do mesmo tamanho.
- Método: cronômetro do comando (`Measure-Command`), 5 rodadas por
  perfil.
- Aprovação: razão das medianas.
- Fase: M4.
- Origem: **[PROPOSTA]**; R9.27–R9.29 (canal bruto local).

### 3.3 App Android

**NFR-12 — Tamanho do app**

- Meta: download ≤ **10 MB** por aparelho; APK universal ≤ 25 MB.
- Condição: build de release, R8 ligado.
- Método: `bundletool get-size total` sobre o conjunto de APKs; APK
  Analyzer para achar o que pesa. **[FATO]** `get-size total` estima o
  tamanho de download "as they would be served compressed over the wire"
  (https://developer.android.com/tools/bundletool).
- Aprovação: a cada release.
- Fase: M7.
- Origem: **[PROPOSTA]**. Leitor de QR é o maior risco de tamanho (§7
  PA-10).

**NFR-13 — Memória do app**

- Meta: PSS total **≤ 150 MB** com um terminal aberto e 2 000 linhas de
  histórico carregadas; sem crescimento acima de 1 MB a cada 10 min em
  uso contínuo.
- Condição: A-R1 e A-R2, C3 por 30 min.
- Método: `dumpsys meminfo <pacote>` a cada minuto.
- Aprovação: máximo da janela e inclinação.
- Fase: M7.
- Origem: **[PROPOSTA]**. **[INFERÊNCIA]** apps Compose simples ficam na
  casa de 60–100 MB de PSS; validar no M7.

**NFR-14 — Fluidez**

- Meta: `frameOverrunMs` **p95 ≤ 0** e **p99 ≤ 16 ms** ao rolar o
  histórico e ao receber frames a 20 fps.
- Condição: A-R1 e A-R2, C3 e C5.
- Método: Macrobenchmark com `FrameTimingMetric`
  (**[FATO]** entrega p50, p90, p95 e p99 de `frameOverrunMs`; positivo =
  quadro perdido).
- Aprovação: 10 iterações por cenário.
- Fase: M7.
- Origem: **[PROPOSTA]**.

### 3.4 Ponte (`trc-bridge`)

**NFR-15 — Ponte: memória**

- Meta: processo ocioso ≤ 15 MB de RSS; **≤ 64 KB por conexão ociosa** e
  ≤ 256 KB por conexão com tráfego.
- Condição: B-US (ou VM Linux equivalente), 0, 100 e 1 000 agentes
  registrados, e 0 a 50 pares ativos em C2.
- Método: `VmRSS` de `/proc/<pid>/status` a 1 Hz; `ss -tmi` para a
  memória dos sockets; inclinação contra o número de conexões.
- Aprovação: inclinação e máximo.
- Fase: M6.
- Origem: **[PROPOSTA]**, conta de §2.3; proposta §4 ("binário Rust de
  poucos MB").

**NFR-16 — Ponte: capacidade num e2-micro**

- Meta (dimensionamento de DP-4, opção recomendada, medido a 10 vezes
  a carga esperada):
  - **1 000 agentes registrados** ociosos e **50 pares ativos** em C2 ao
    mesmo tempo;
  - CPU média ≤ 20 % do tempo de CPU da VM, abaixo dos 25 % sustentados
    do e2-micro, sem depender da rajada;
  - memória total da VM ≤ 700 MB;
  - reinício da ponte: os 1 000 agentes se registram de novo em ≤ 60 s,
    com espera aleatória.
- Condição: B-US, gerador de carga que abre conexões reais (P9).
- Método: `mpstat`/`top` da VM, contadores da ponte, relógio do
  gerador.
- Aprovação: 30 min em regime + 3 reinícios.
- Fase: M6.
- Origem: **[PROPOSTA]**. Fato de base: e2-micro com 0,25 vCPU
  sustentada, rajada de ~30 s e 1 GB (§1.1).

**NFR-17 — Ponte: atraso de repasse**

- Meta: **p99 ≤ 2 ms** entre receber um registro de uma ponta e
  escrevê-lo na outra.
- Condição: carga de NFR-16.
- Método: histograma interno da ponte (carimbo na leitura e na escrita);
  conferência por `tcpdump` nas duas pernas.
- Aprovação: 30 min em regime.
- Fase: M6.
- Origem: **[PROPOSTA]**; a ponte "só repassa bytes" (ADR-0004).

**NFR-18 — Ponte: saída de dados**

- Meta: acompanhamento, não aprovação: saída mensal da ponte padrão
  medida e comparada com a estimativa de §2.8; alerta acima de 1 GB/mês.
- Método: contadores de bytes da ponte e faturamento do provedor.
- Fase: M6 em diante.
- Origem: proposta §4.1 e ADR-0006 (custo), §2.8.

### 3.5 Latência

**NFR-20 — Enviar → eco, ponte no Brasil**

- Meta: **p95 ≤ 150 ms** no Wi-Fi (N1). No 4G (N2), ver DP-2
  (recomendação: p95 ≤ 250 ms).
- Condição: B-BR, C1, `pwsh`, escrita liberada.
- Método:
  - harness (`trc-bench`) com N ≥ 1 000: `input.send` com um marcador
    único; o tempo vai do envio até o primeiro frame aplicado que contém
    o marcador (um relógio só);
  - app real (A-R1) com N ≥ 200: seções Perfetto do toque em Enviar até
    o quadro desenhado que mostra o marcador;
  - 30 amostras vidro a vidro em vídeo, para conferir o app.
- Aprovação: p95 em cada uma das 3 execuções, nas redes da meta.
- Fase: M6 (harness, com ponte local e depois B-BR), M7 (app).
- Origem: auditoria §13 ("≤ 150 ms p95", escrita para "mesma cidade,
  Tailscale direto") e proposta §4.1 (mantém 150 ms com a ponte no
  Brasil). **[INFERÊNCIA]** a ponte acrescenta um salto que a auditoria
  não tinha; conta em §2.6.

**NFR-21 — Enviar → eco, ponte nos EUA**

- Meta: **p95 ≤ 400 ms** no Wi-Fi (N1). No 4G, ver DP-2 (recomendação:
  p95 ≤ 500 ms).
- Condição, método e aprovação: como NFR-20, com B-US (ou N4 antes de
  existir B-US).
- Fase: M6, M7.
- Origem: proposta §4.1 ("≤ 400 ms p95 do envio à atualização da tela");
  ADR-0004 e ADR-0006.

**NFR-22 — Contribuição do agente**

- Meta: do byte lido do PTY até o frame escrito no socket: **p95 ≤ 5 ms
  quando a tela estava parada havia ≥ 50 ms** (borda de subida) e
  **p95 ≤ 55 ms** em rajada.
- Condição: PC-R1, C1 (eco de tecla) e C3.
- Método: instrumentação do agente (spans), N ≥ 1 000.
- Aprovação: p95 por cenário.
- Fase: M2 (via CLI), M6.
- Origem: **[PROPOSTA]**, necessária para NFR-20 (§2.6, §7 PA-13).

**NFR-23 — Abrir o app → lista de computadores**

- Meta: TTID **≤ 1,0 s p50 e ≤ 1,5 s p95** em partida a frio, com os
  nomes dos PCs já na tela (vêm do armazenamento local); estado online
  em ≤ 1,0 s depois disso com ponte no Brasil, ≤ 1,5 s nos EUA.
- Condição: A-R1 (meta) e A-R2 (reportado), ponte em modo permanente.
- Método: Macrobenchmark `StartupTimingMetric`, 20 iterações; o estado
  online marcado com seção Perfetto.
- Aprovação: p50 e p95 das iterações.
- Fase: M7.
- Origem: **[PROPOSTA]**. **[FATO]** o Android vitals considera
  excessiva a partida a frio de 5 s ou mais, a morna de 2 s e a quente
  de 1,5 s (https://developer.android.com/google/play/vitals/launch-time);
  a meta fica bem abaixo.

**NFR-24 — Abrir o app → terminais ao vivo**

- Meta, até a lista de terminais preenchida pelo snapshot
  (`reportFullyDrawn`):

  | Partida | Ponte BR | Ponte EUA |
  |---|---|---|
  | A frio, tocando no PC | p95 ≤ 2,0 s | p95 ≤ 3,5 s |
  | Volta do segundo plano (conexão fechada, F2) | p95 ≤ 1,2 s | p95 ≤ 3,0 s |

- Condição: A-R1, N1 e N2, ponte em modo permanente. No modo sob demanda
  (ADR-0006) a meta não vale (§7 PA-8).
- Método: Macrobenchmark (TTFD com `reportFullyDrawn()` chamado ao
  aplicar o snapshot), 20 iterações por rede.
- Aprovação: p95 por rede.
- Fase: M7.
- Origem: **[PROPOSTA]**, contas de §2.7.

**NFR-25 — Reconexão e resume**

- Meta: com a rede disponível de novo (troca Wi-Fi↔4G ou volta do modo
  avião), a tela volta ao vivo (primeiro frame aplicado) em **p95 ≤ 3 s**
  com ponte no Brasil e **≤ 4 s** nos EUA, contados do aviso de rede
  disponível do sistema.
- Condição: A-R1, N5, terminal aberto em C2.
- Método: seções Perfetto do aviso de rede (callback de conectividade)
  até o frame; 50 trocas.
- Aprovação: p95.
- Fase: M7 (harness com N5 no M6).
- Origem: **[PROPOSTA]**. Depende de o app reconectar na hora quando a
  rede muda, não só pela espera exponencial (§7 PA-4).

**NFR-26 — Pareamento**

- Meta, sem contar o tempo da pessoa:
  - código digitado ou QR lido → modal "Permitir?" no PC: **p95 ≤ 3 s**;
  - "Permitir" no PC → PC na lista do celular: **p95 ≤ 2 s**.
- Condição: A-R1, N1 e N2, B-BR e B-US.
- Método: carimbos no app e na extensão (`pair.claimed`, `pair.done`),
  relógios sincronizados por `adb` (§1.5); 20 pareamentos por cenário.
- Aprovação: p95.
- Fase: M6 (harness), M7.
- Origem: **[PROPOSTA]**. **[INFERÊNCIA — validar no M7]** gerar a chave
  P-256 no StrongBox pode levar mais de um segundo; o app pode gerá-la
  enquanto a pessoa digita o código.

**NFR-27 — Taxa de `stale` (medição, sem aprovação)**

- Meta: nenhuma aprovação; medir e reportar a fração de `input.send` com
  texto que volta `stale`, por carga (C1, C2, C3) e por ponte.
- Gatilho: se a taxa em C2 passar de 20 %, o resultado vai para a
  decisão de P7 sobre §19.2 item 1 da spec (DP-6).
- Método: harness com espera de 0 a 3 s entre o frame e o envio
  (imitando uma pessoa), N ≥ 500 por cenário; no app, contadores em
  build de medição.
- Fase: M6 (harness), M7 (uso real).
- Origem: spec §17 e §19.2 item 1 ("P8 mede"); estimativa em §2.9.

### 3.6 Bateria e dados móveis

**NFR-30 — Conexão só em primeiro plano**

- Meta: ao sair do primeiro plano, **nenhuma conexão aberta em ≤ 5 s**;
  nada reconecta em segundo plano sem push.
- Condição: A-R1, terminal aberto em C2, 20 saídas (Home, trocar de app,
  apagar a tela).
- Método: o agente registra `device.disconnected` (evento local, §8.9 da
  spec) com a hora; o app registra o `ON_STOP`; diferença com relógios
  sincronizados. `dumpsys netstats detail` confirma zero bytes do app
  depois disso.
- Aprovação: 20 de 20.
- Fase: M7.
- Origem: ADR-0012 ("WebSocket só com o app em primeiro plano"); fluxo
  F2 passo 5; auditoria §13. O prazo de 5 s é **[PROPOSTA]**.

**NFR-31 — Segundo plano: custo zero**

- Meta: em 8 h em segundo plano sem pedidos de atenção, o app tem **0
  wakelocks, 0 jobs, 0 alarmes e 0 bytes de rede** atribuídos a ele (o
  FCM roda no Google Play services, fora do app).
- Condição: A-R1, app pareado e com push registrado (a partir do M8),
  aparelho parado na mesa, fora da tomada.
- Método: `dumpsys batterystats --reset` antes; `dumpsys batterystats
  <pacote>` e `dumpsys netstats detail` depois; uma rodada extra com Doze
  forçado (`dumpsys deviceidle force-idle`) e App Standby
  (`am set-inactive <pacote> true`).
- Aprovação: 2 noites.
- Fase: M7, repetido no M8.
- Origem: auditoria §13 ("Celular em segundo plano: nenhuma conexão
  aberta; só push opaco"); ADR-0012. **[FATO]** o Doze suspende o acesso
  à rede e ignora wakelocks; o App Standby libera rede para apps ociosos
  "about once a day"
  (https://developer.android.com/training/monitoring-device-state/doze-standby).

**NFR-32 — Custo por push**

- Meta: cada push resulta numa **notificação visível em ≤ 10 s** depois
  de chegar ao app (100 %); rede usada pelo app por push **≤ 30 KB** e
  **≤ 10 s**.
- Condição: A-R1 em Doze forçado e fora dele; N1, N2, N3.
- Método: logcat do `onMessageReceived` e do `notify`; `TrafficStats`
  por janela; 50 pushes por cenário.
- Aprovação: 100 % dentro de 10 s; p95 dos bytes.
- Fase: M8.
- Origem: ADR-0014; **[FATO]** o `onMessageReceived` deve tratar a
  mensagem em até 10 s, e trabalho mais longo vai para o WorkManager
  (https://firebase.google.com/docs/cloud-messaging/android/receive-messages);
  **[FATO]** se as mensagens de prioridade alta não geram notificação
  visível, o FCM pode rebaixá-las, olhando 7 dias de comportamento
  (https://firebase.google.com/docs/cloud-messaging/android/message-priority).
  Consequência para R10.47 em §7 PA-3.

**NFR-33 — Push de ponta a ponta**

- Meta: pedido aberto no agente → notificação visível no celular: **p50
  ≤ 5 s, p95 ≤ 15 s**, com o aparelho em Doze.
- Condição: A-R1, Doze forçado, N1 e N2.
- Método: hora do `attention.opened` no agente e do `notify` no app,
  relógios sincronizados por `adb`; 50 pedidos.
- Aprovação: p50 e p95.
- Fase: M8.
- Origem: **[PROPOSTA]**. **[FATO]** o FCM tenta entregar a mensagem de
  prioridade alta na hora e pode acordar o aparelho; a de prioridade
  normal pode esperar o fim do Doze (link de NFR-32). **[INFERÊNCIA]** a
  entrega depende dos servidores do Google e não é garantida; a meta
  mede, não promete.

**NFR-34 — Dados por minuto de tela aberta**

- Meta (soma dos dois sentidos, medida no app):

  | Tela | Meta |
  |---|---|
  | Terminal aberto e parado (C1) | ≤ 10 KB/min |
  | Lista de terminais, sem terminal aberto | ≤ 30 KB/min |
  | Claude trabalhando (C2) | ≤ 1 MB/min p95 |
  | Log contínuo (C3) | ≤ 1,5 MB/min p95 |
  | Pior caso (C4, C5, adversário) | ≤ 4 MB/min com o teto de DP-3; sem ele, só reportado |

- Condição: A-R1, N1 e N2, ponte BR e EUA.
- Método: `TrafficStats` por janela de 1 min em build de medição;
  conferência com os contadores da ponte; harness para os piores casos.
- Aprovação: p95 das janelas de 1 min, 30 min por carga.
- Fase: M6 (harness), M7.
- Origem: pedido deste P8 (orçamento de dados); auditoria §13 (`cat` de
  100 MB limitado pela coalescência); contas de §2.5.

**NFR-35 — CPU e energia em primeiro plano**

- Meta: CPU do processo do app **≤ 5 %** de um núcleo com C1 e **≤ 15 %**
  com C3; energia só reportada.
- Condição: A-R1, tela aberta 10 min por carga.
- Método: CPU por processo no trace do Perfetto; energia com o Power
  Profiler ou `PowerMetric` se houver A-R3 (DP-5).
- Aprovação: média da janela de 10 min.
- Fase: M7.
- Origem: **[PROPOSTA]**. A energia em mW só vira meta depois de uma
  linha de base medida (DP-5).

### 3.7 Robustez

**NFR-40 — Rede ruim (N3: +300 ms de RTT, 5 % de perda)**

- Meta:
  - enviar → eco: **p95 ≤ 1 000 ms, p99 ≤ 2 000 ms**;
  - **0** quedas por falso "conexão morta" em 30 min (R3.10: 45 s);
  - **0** envios aplicados duas vezes; todo envio incerto se resolve por
    `cmd.status` (R10.1–R10.6);
  - a tela converge para o estado do PC em ≤ 2 s depois que a saída
    para;
  - no fim, o estado de lista do cliente é igual a um snapshot novo.
- Condição: harness com `netem` (M6) e app no emulador com
  `-netdelay`/perda (M7); C2.
- Método: N ≥ 1 000 envios; comparação automática do estado final.
- Aprovação: todas as condições em 3 execuções.
- Fase: M6, M7.
- Origem: pedido deste P8 (perda 5 %, 300 ms); ADR-0011; conta de §2.10.

**NFR-41 — Troca Wi-Fi ↔ 4G**

- Meta: em 50 trocas com envios em andamento: 0 envio duplicado, 0 envio
  sem resposta final (chegou / não chegou), escrita liberada mantida
  (R6.11) e tela ao vivo dentro de NFR-25.
- Condição: A-R1, N5, terminal com escrita liberada, um envio por
  segundo durante a troca.
- Método: log do app e audit do agente comparados.
- Aprovação: 50 de 50.
- Fase: M7.
- Origem: fluxo X9 (interfaces); ADR-0011; spec D-3.

**NFR-42 — PC dormindo**

- Meta:
  - o celular mostra "offline desde…" em **≤ 60 s p95** depois de o PC
    dormir;
  - ao acordar, o agente está de novo na ponte em **≤ 10 s** depois de a
    rede voltar, e o celular em primeiro plano volta ao vivo em ≤ 15 s;
  - **0 sessões perdidas** em 50 ciclos de sono (o sono não mata PTYs).
- Condição: PC-R1 (estados de sono registrados com `powercfg /a`), B-BR,
  celular aberto na lista.
- Método: sono forçado com PsShutdown `-d` e acordar por timer; horas do
  agente, da ponte e do app; `powercfg /sleepstudy` se o PC usar Modern
  Standby.
- Aprovação: p95 e contagem em 50 ciclos.
- Fase: M6 (agente e ponte), M7 (app).
- Origem: auditoria §3 M4 e §4.3 ("o agente não impede o sono; no resume
  reata"); fluxo X8. A detecção depende da presença na ponte (P4).
  Números **[PROPOSTA]**.

**NFR-43 — Queda do agente**

- Meta: depois de `taskkill /F` no agente, com reinício automático:
  época nova, sessões marcadas `lost`, clientes com snapshot em **≤ 3 s**
  depois de o agente voltar; banco íntegro (`PRAGMA integrity_check` =
  ok) em 100 quedas.
- Condição: PC-R1, 8 sessões, extensão e harness ligados.
- Método: script de 100 quedas; verificação automática.
- Aprovação: 100 de 100.
- Fase: M2 (local), M6 (remoto).
- Origem: auditoria §4.3 e §7.2; spec R8.5 e R8.27.

**NFR-44 — Conexão morta em silêncio**

- Meta: com perda de 100 % sem aviso (N5, 60 s), o cliente mostra
  "Reconectando…" em **≤ 45 s** e o agente libera os recursos da conexão
  em ≤ 45 s.
- Condição: harness e app; B-BR.
- Método: `netem loss 100%` ou modo avião sem desligar o Wi-Fi do PC.
- Aprovação: 20 de 20.
- Fase: M6, M7.
- Origem: spec R3.10.

**NFR-45 — Isolamento de contrapressão**

- Meta: um aparelho que para de confirmar frames não afeta os outros:
  NFR-20 continua valendo para os demais; a memória do agente não cresce
  por causa dele.
- Condição: harness com 3 clientes, um deles congelado.
- Método: latência dos outros dois e Private Bytes do agente, 10 min.
- Aprovação: p95 dos outros dentro de NFR-20 + 10 %.
- Fase: M6.
- Origem: spec §9.7 e R8.19–R8.21; ADR-0007.

### 3.8 Escala

**NFR-50 — 64 sessões**

- Meta, com 64 sessões abertas (teto da spec):
  - memória: `NFR-01 + 64 × NFR-02` (linear, ≤ 340 MB no teto com
    histórico cheio);
  - CPU ociosa (C1) ≤ 0,5 % de um núcleo;
  - snapshot em partes (R8.12), cada parte ≤ 256 KB; `resume` até a
    lista completa ≤ 200 ms a mais que com 4 sessões (N0);
  - a 65ª sessão recebe `rate_limited` e nada quebra.
- Condição: PC-R1, sessões com `cmd.exe` (shell leve, para isolar o
  custo do agente).
- Método: script de abertura; Private Bytes, CPU, tempo de `resume` pelo
  harness.
- Aprovação: 3 execuções.
- Fase: M2, M6.
- Origem: spec §14 ("Sessões abertas por agente: 64"); pedido deste P8.
  **[INFERÊNCIA]** 64 shells reais (`pwsh`) custam muito mais que o
  agente; o teto é do protocolo, não um uso esperado.

**NFR-51 — 8 conexões remotas**

- Meta, com 8 conexões (teto da spec), cada uma com 2 assinaturas em C3:
  - CPU do agente ≤ 25 % de um núcleo;
  - memória por conexão dentro de NFR-07;
  - latência de um cliente dentro de NFR-20 + 20 %;
  - a 9ª conexão recebe 4429 `limit`, sem afetar as 8.
- Condição: PC-R1, harness com 8 clientes, B-BR.
- Método: como NFR-04 e NFR-20.
- Aprovação: 3 execuções de 10 min.
- Fase: M6.
- Origem: spec §14 ("8 no total, 1 por aparelho").

### 3.9 Entrada local de avisos (EX1)

Exigência externa EX1 (`docs/exigencias-externas.md`): o agente expõe uma
entrada local para outros programas do PC mandarem avisos curtos ao
celular (primeiro cliente: claude-hadouken). O desenho é de P3, P5, P6 e
P7; aqui ficam os limites e as latências.

**NFR-60 — Limite de taxa por origem**

- Meta **[PROPOSTA]**:
  - por origem: **6 avisos por minuto**, rajada de **3**;
  - no agente todo, somando as origens: **30 por minuto**;
  - acima do limite, a chamada é recusada na hora com "tente depois de
    N ms", sem fila;
  - a chamada local responde em **p99 ≤ 5 ms** (confirma o recebimento;
    não espera a entrega ao celular);
  - uma origem estourando o limite não atrasa as outras nem o Event Log.
- Por que esses números: **[INFERÊNCIA]** alertas de consumo e de tarefa
  terminada acontecem algumas vezes por hora; 6 por minuto sobra para o
  uso normal e impede que um programa com defeito vire uma chuva de
  notificações (cada aviso com o celular em segundo plano vira um push, e
  push de prioridade alta sem notificação visível pode ser rebaixado,
  NFR-32).
- Condição: PC-R1, agente em C1.
- Método: fixture que dispara 1 000 avisos em 10 s de uma origem e 1 por
  segundo de outra; contagem de aceitos e recusados; Private Bytes do
  agente (acréscimo ≤ 100 KB no fim); latência da chamada local.
- Aprovação: aceitos ≤ `3 + 6 × minutos`; a outra origem com 100 %
  aceitos; p99 da chamada.
- Fase: a fase em que EX1 for implementada (P9 decide); o teste de
  limite entra na suíte do agente.
- Origem: EX1 ("Limite de taxa: P3 §14 + P8"). O limite "por origem"
  depende de a origem ser autenticada (P5, §7 PA-12).

**NFR-61 — Latência aviso local → notificação no celular**

- Meta **[PROPOSTA]**:

  | Estado do celular | Meta |
  |---|---|
  | App em primeiro plano (conexão aberta) | aviso visível no app: p95 ≤ 1 s (ponte BR), ≤ 1,5 s (EUA) |
  | App em segundo plano (push FCM) | notificação visível: p50 ≤ 5 s, p95 ≤ 15 s, com Doze forçado (mesma de NFR-33) |
  | Celular offline | entregue em ≤ 5 s depois que o app volta a conectar, dentro da validade que P3/P6 definirem |

- Condição: A-R1, N1 e N2, B-BR e B-US.
- Método: o programa de teste chama a entrada local e registra a hora no
  PC; o app registra a hora em que mostra o aviso (primeiro plano) ou do
  `notify` (segundo plano); relógios sincronizados por `adb` (§1.5); 50
  avisos por estado. Conferência com vídeo em 10 deles.
- Aprovação: p50 e p95 por estado.
- Fase: junto de NFR-60; a parte de push só a partir do M8.
- Origem: EX1; ADR-0014 (push opaco); **[INFERÊNCIA]** da própria EX1: o
  aviso vira um tipo de atenção no Event Log, entregue pelo mesmo push
  `{agent_id, attention_id}`.

## 4. Validação dos números da spec, linha a linha

Vereditos: **Manter**, **Ajustar** (com o valor proposto) ou **Validar
no Mx** (sem base para decidir antes da medição). Nenhum veredito muda a
spec: P3 aplica na revisão.

### 4.1 Tabela da spec §14

| Item (§14) | Spec | Veredito | Por quê |
|---|---|---|---|
| Mensagem remontada | 256 KB | **Manter** | Frame típico 3–10 KB, adversário 120 × 32 ~160 KB, página de histórico típica ~30 KB (§2.4). Falta regra para frame ou página acima do limite (§7 PA-1). |
| `input.send.data` | 4096 B, fixo | Fixo | Tela aprovada. |
| `input.send.keys` | 16 | **Manter** | Com 16 teclas por envio, o app agrupa toques repetidos de seta sem estourar a taxa de envios. |
| Comandos por aparelho | 30/s, rajada 30 | **Manter** | Uma pessoa não passa de ~5 comandos/s; paginar o histórico é 1 comando por página. Acks não são comandos (`t: ack`). |
| `input.send` por aparelho | 10/s | **Manter** | "Enviar" fica abaixo de 2/s; setas repetidas vão agrupadas em `keys`. |
| `step_up.challenge` | 10/min | **Manter** | Cada desafio pede biometria, que leva segundos. |
| Frames por assinatura | 20/s | **Manter** | 50 ms entre frames basta para ler terminal e acompanhar spinner de 10 Hz. Somar um teto de bytes por assinatura (DP-3). |
| Janela W | 4 | **Manter; validar no M6** | fps efetivo = `min(20, 4 / RTT)`: ~20 fps com ponte no Brasil, ~13 fps nos EUA (RTT ~0,3 s). Menos fps nos EUA também é menos dados e bateria. Subir para 8 só se o M6 mostrar tela visivelmente atrasada. |
| Assinaturas por conexão | 2 | **Manter** | Com hashes por linha (§2.3), cada assinatura custa ~1 KB de estado. |
| `screen.history.count` | 200, fixo | Fixo | Tela aprovada. Página densa pode passar de 256 KB (§7 PA-1). |
| Histórico por sessão | 2 000 linhas | **Ajustar**: "até 2 000 linhas **e** até 4,5 MB por sessão" | A 120 colunas, 2 000 linhas em largura cheia são ~5,8 MB (§2.1). Decisão em §5 e DP-1. |
| Ping / conexão morta | 20 s / 45 s | **Manter** | Custa ~2 KB/min (§2.5). **[FATO]** a RFC 5382 pede que NATs não expirem TCP parado antes de 2 h 4 min (REQ-5, https://www.rfc-editor.org/rfc/rfc5382); **[INFERÊNCIA]** operadoras móveis nem sempre cumprem, e 20 s cobre com folga. 45 s tolera retransmissões em N3. |
| Prazo de `hello` / `auth` | 10 s / 10 s | **Manter** | Em N3, handshake + assinatura no Keystore cabem em poucos segundos (§2.7, §2.10). |
| Espera de reconexão | 1 s a 30 s, fixo | Fixo | Ver §7 PA-4 (reconectar na hora quando a rede muda). |
| Tentativa com acesso cortado | 60 s | **Manter** | ~10 KB por tentativa (dois handshakes TLS), só em primeiro plano. |
| Retenção do log | 24 h ou 10 000 | **Manter** | A ~50 eventos/min, 10 000 cobrem ~3,3 h; depois disso o `resume` usa snapshot, que é pequeno. Guardar no SQLite, não em memória (§7 PA-6). |
| Resultados para `cmd.status` | 256 por principal | **Manter** | ~0,46 MB no total (§2.2). |
| Nonce de step-up | 60 s | **Manter** | Biometria humana leva 2–10 s. |
| Bytes pendentes | 1 MB por 30 s | **Manter** | Com W = 4, o pendente normal fica em dezenas de KB mesmo em N3 (§2.10); 1 MB só aparece com defeito ou cliente parado. |
| Sessões abertas | 64 | **Manter como teto** | Memória linear (NFR-50). |
| Sessões encerradas no snapshot | 20 | **Manter o número**; ver memória em §7 PA-5 | 20 × 60 min × até 5 MB = até 100 MB retidos. |
| `subject.value` / `detail` | 1 KB / 1 KB | **Manter** | Não entra no push (opaco). |
| `options` por pedido | 8 | **Manter** | — |
| Texto de contexto | 256 caracteres | **Manter** | — |
| Conexões remotas | 8, 1 por aparelho | **Manter** | ≤ 512 KB cada (NFR-07); CPU em NFR-51. |
| `pty.output` | 64 KB | **Manter** | Canal local; o xterm do VS Code consome em blocos. |
| `cols` / `rows` | 1000 / 500 | **Validar no M0** | Grade visível no teto: `1000 × 500 × 24 B` = 12 MB, sozinha acima de 2 × a meta por sessão. As metas por sessão valem em 120 × 32. P3 pode baixar o teto (ex.: 500 × 200) se o M0 confirmar o custo (§7 PA-14). |
| `activity.recent.limit` | 50 | **Manter** | Local. |
| Tela depois do fim | 60 min | **Manter o prazo**; teto de memória em §7 PA-5 | — |
| Validade do código | 5 min, fixo | Fixo | — |
| Prazo para Permitir | 60 s | **Manter** | Conflito de texto já registrado na spec §19.2 item 5. |

### 4.2 Outros números e decisões da spec marcados para P8

| Onde | Spec | Veredito | Por quê |
|---|---|---|---|
| R3.9 / D-15 | Sem compressão | **Manter** | O orçamento de dados de NFR-34 cabe sem compressão; o risco de vazamento por tamanho fica fora. |
| R3.11 / E23 | RTT medido pelo cliente com Ping/Pong | **Validar no M0** | **[FATO]** a interface `WebSocket` do OkHttp não tem método para mandar Ping (só `send`, `close`, `cancel`, `queueSize`, `request`; https://github.com/square/okhttp/blob/master/okhttp/src/commonJvmAndroid/kotlin/okhttp3/WebSocket.kt). Ver §7 PA-2 e PA-15. |
| D-1 / R10.15 | Ctrl+C e Esc isentos da precondição | **Manter** | Pela conta de §2.9, sem a isenção o Ctrl+C falharia ~63–97 % das vezes com o Claude Code trabalhando. |
| D-8 / R10.2 | 256 resultados por contagem | **Manter** | Custo de memória desprezível. |
| D-12 / R8.12 | Snapshot em partes | **Manter** | 64 sessões × ~600 B ≈ 40 KB: uma parte basta no caso comum. |
| R8.17 | 20 encerradas | ver 4.1 | — |
| R9.1 | 2 000 linhas | ver §5 | — |
| R9.26 | 60 min | ver 4.1 | — |
| §17 | Latência 150 / 400 ms p95 | **Manter no Wi-Fi; decidir o 4G** (DP-2) | §2.6. |
| §19.2 item 1 | Taxa de `stale` | **Medir** (NFR-27) + DP-6 | §2.9. |
| §19.2 item 20 | Histórico 2 000 × 5 000 | **2 000 com teto de bytes** (§5) | — |
| §19.2 item 26 | 20 encerradas e por quanto tempo | **Manter 20 e 60 min, com teto de memória** (§7 PA-5, dono P6) | — |

## 5. Decisão do histórico (scrollback)

Fontes: auditoria §7.1 (até 5 000 linhas), auditoria §13 (~2 000 linhas,
para caber em ≤ 5 MB por sessão), spec R9.1 e §14 (2 000 linhas [P8]),
spec §19.2 item 20, ADR-0007.

Conta (§2.1, **[ESTIMATIVA]** com célula de 24 B): 2 000 linhas custam
3,84 MB a 80 colunas e **5,76 MB a 120 colunas**; 5 000 linhas custam
9,6 a 14,4 MB. Portanto:

- **5 000 linhas estão descartadas** com armazenamento em largura cheia:
  passam da meta de 5 MB por sessão em qualquer largura comum.
- **2 000 linhas fixas não cabem** a 120 colunas, que é o tamanho de
  referência da própria spec.

**Proposta deste P8 (recomendação da DP-1):** histórico de **até 2 000
linhas e até 4,5 MB por sessão**, o que vier primeiro. O que passa sai
pelas linhas mais antigas.

| Largura | Linhas guardadas (4,5 MB / (colunas × 24 B), no máximo 2 000) |
|---|---|
| 80 | 2 000 |
| 120 | ~1 560 |
| 160 | ~1 170 |
| 200 | ~940 |

- Compatível com a spec: R9.1 já diz "até 2 000 linhas"; o fim do
  histórico já tem texto aprovado ("Início do histórico guardado no PC",
  `reached_start`, E13).
- Os 0,5 MB restantes da meta de 5 MB cobrem grade visível, buffers do
  PTY e a sessão (§2.1).
- **Validar no M0:** o tamanho real da célula do emulador escolhido e se
  ele deixa guardar o histórico em formato compacto (§2.1, ~136 B por
  linha). Se deixar, o M0 pode propor subir para 5 000 linhas dentro dos
  mesmos 4,5 MB, o que exige nova aprovação (é o número que a pessoa
  sente).

## 6. Decisões pendentes (Sr. Garioli)

**DP-1 — Tamanho do histórico no PC**

- A. 2 000 linhas fixas (spec atual). Simples; passa de 5 MB por sessão
  a partir de ~105 colunas.
- B. **Até 2 000 linhas e até 4,5 MB por sessão** (§5). Leveza
  garantida; em terminais largos guarda menos linhas (~1 560 a 120
  colunas).
- C. Histórico compacto de até 5 000 linhas. Mais histórico, mais código
  no agente; depende do emulador (M0).
- **Recomendação: B agora; o M0 avalia C.**

**DP-2 — Meta de latência no 4G**

A auditoria escreveu 150 ms p95 para "mesma cidade, Tailscale direto";
com a ponte há um salto a mais, e o 4G acrescenta 40–80 ms que não
controlamos (§2.6).

- A. Mesma meta em qualquer rede: 150 ms (ponte BR) e 400 ms (EUA).
  Risco de reprovar por causa da operadora.
- B. **Wi-Fi: 150 / 400 ms p95; 4G: 250 / 500 ms p95.**
- C. Metas só de p50.
- **Recomendação: B.** O celular manda o texto composto no campo, não
  tecla por tecla (proposta §4.1), então 250 ms no 4G ainda é imediato
  para quem aperta Enviar.

**DP-3 — Teto de dados por terminal aberto**

Hoje só existe o teto de 20 frames/s. Uma tela colorida que redesenha
sem parar gasta ~12,5 MB por minuto, e um programa com uma cor por
célula pode passar de 100 MB por minuto (§2.5).

- A. Só o teto de frames (como está).
- B. **Teto de 64 KB/s por terminal assistido, no agente**: pior caso
  ~4 MB por minuto; telas muito agitadas atualizam menos vezes por
  segundo. Não muda o protocolo (mandar menos frames já é permitido).
- C. Modo "economia de dados" escolhido no app. Exige tela, texto e
  campo novo no protocolo.
- **Recomendação: B**, com o número validado no M6/M7.

**DP-4 — Tamanho da ponte padrão (`ponte.gariolilabs.com`)**

O ADR-0004 deixa para P4 como terceiros entram na ponte padrão; o
dimensionamento depende disso.

- A. Só Sr. Garioli (≤ 10 PCs).
- B. **Uso pessoal e grupo pequeno: até 100 PCs registrados e 20 pares
  ativos**, medido a 10 vezes isso num e2-micro (NFR-16).
- C. Ponte pública (centenas ou milhares de PCs): exige outro plano de
  hospedagem e custo.
- **Recomendação: B.** Cabe no e2-micro com folga pela estimativa e não
  fecha a porta para C.

**DP-5 — Aparelhos de referência no Android**

- A. **O celular de Sr. Garioli (A-R1) + emulador de entrada (A-R2).**
  Sem compra; a bateria é medida por `batterystats` (wakelocks, rádio,
  CPU), sem mW.
- B. A + um Pixel 6 ou mais novo, para medir energia em mW (Power
  Profiler e `PowerMetric` só funcionam nele).
- C. B + um aparelho físico de entrada.
- **Recomendação: A no MVP.** As metas que importam para bateria (nada
  em segundo plano, NFR-30 e NFR-31) não precisam de mW.

**DP-6 — Enviar texto enquanto o Claude Code trabalha**

Pela conta de §2.9, com o spinner rodando quase todo envio de texto volta
"A tela mudou antes do envio" (60–100 %). Ctrl+C, Esc e as aprovações
vindas do adaptador funcionam.

- A. **Aceitar no MVP e medir no uso real** (NFR-27). O texto não se
  perde (fluxo X10).
- B. Botão "Enviar mesmo assim" depois de um `stale`. Tela e texto novos
  (P7), revisão de segurança (P5).
- C. Afrouxar a precondição (ex.: ignorar mudanças numa linha de status).
  Muda a spec e a segurança do envio.
- **Recomendação: A**, com o gatilho de NFR-27 (acima de 20 % em C2, a
  decisão volta com os números medidos).

## 7. Pontos em aberto

Conflitos e lacunas achados nesta entrega, com o dono. Nenhum foi
resolvido aqui.

| # | Ponto | Dono |
|---|---|---|
| PA-1 | A spec não diz o que fazer quando um frame completo ou uma página de `screen.history` passa do limite de mensagem (256 KB): com R3.8, o agente fecharia a própria conexão com 1009. Casos reais: tela grande e densa (300 × 80 com muitas cores) e 200 linhas coloridas célula a célula (§2.4). Opções: frame em partes (como o snapshot) ou página com menos linhas (`first_line` já permite). | P3 |
| PA-2 | O texto `settings.bridge_ok` diz "alcançável · {ms} ms" (tempo da **ponte**), mas o Ping/Pong de R3.11 corre dentro do TLS ponta a ponta e mede celular ↔ **agente**. Qual número a tela mostra? | P4, P7 |
| PA-3 | R10.47: ao receber o push, o app conecta, faz `resume` e só então decide a notificação; o push de limpeza cancela. **[FATO]** o `onMessageReceived` tem ~10 s, e push de prioridade alta que não gera notificação visível pode ser rebaixado (NFR-32). Com ponte nos EUA e rede ruim, buscar antes de notificar pode estourar 10 s, e o push de limpeza é, por definição, um push sem notificação. Proposta a avaliar: mostrar a notificação genérica na hora (o texto já é opaco) e buscar depois; push de limpeza com prioridade normal. | M8, P4, P5 |
| PA-4 | §13.5 fixa a espera de reconexão em 1 s a 30 s. NFR-25 pede reconectar na hora quando o sistema avisa que há rede nova (reiniciando a espera). Confirmar que isso é permitido. | P3, P7 |
| PA-5 | Sessões encerradas guardam tela e histórico por 60 min, até 20 delas (R8.17, R9.26): até 100 MB de memória depois de uso intenso, fora das metas de leveza. Proposta: as encerradas entram num teto conjunto (ex.: 16 MB), liberando as mais antigas primeiro. | P6, P3 |
| PA-6 | O Event Log de 10 000 eventos custaria ~4 MB se ficasse todo em memória, 20 % da meta ociosa (§2.2). O log deve morar no SQLite com só a cauda em memória. Não muda a spec; registro para o M2. | M2 |
| PA-7 | O `tungstenite`, por padrão, usa 256 KiB de buffers por conexão, fila de escrita sem limite e mensagem de até 64 MiB (§2.3). Agente e ponte precisam configurar buffers menores e `max_message` = 256 KB. Toca segurança (memória sob ataque). | P4, P5, M6 |
| PA-8 | O modo "sob demanda" da ponte (ADR-0006: até ~5 s para conectar, reconexão a cada 60 min) não cabe nas metas de abrir o app (NFR-23, NFR-24), que valem para o modo permanente. P4 define a meta do modo sob demanda. | P4 |
| PA-9 | O `minSdk` do app não está definido; ele fixa o A-R2 e muda o que as metas de partida e bateria significam. | P9, M7 |
| PA-10 | Tamanho do APK (NFR-12): um leitor de QR embutido pesa alguns MB por arquitetura. **[INFERÊNCIA — verificar]** o leitor de código do Google Play services não pede a permissão de câmera, o que mudaria o fluxo aprovado da permissão `CAMERA` (interfaces, android §0). | P7, M7 |
| PA-11 | Com ponte nos EUA, os ~5 RTT ponta a ponta até a lista ao vivo dominam o tempo de abrir o app (§2.7). Reduzir viagens (ex.: juntar etapas do handshake) é decisão de P4/P5. | P4, P5 |
| PA-12 | EX1: o limite "por origem" (NFR-60) só vale se a origem for autenticada; sem isso, qualquer processo se passa por outra origem e só o limite global protege. | P5 |
| PA-13 | NFR-20 e NFR-22 exigem coalescência com borda de subida (a primeira mudança depois de um período parado sai na hora). A spec fixa só o teto de 20/s (R9.17), o que não conflita. Registro para o M2. | M2 |
| PA-14 | `cols` ≤ 1000 e `rows` ≤ 500: a grade visível no teto custa ~12 MB (§4.1). P3 pode baixar o teto depois do M0. | P3, M0 |
| PA-15 | R3.10 exige que o cliente mande Ping a cada 20 s sem tráfego e R3.11 mede o RTT com ele. **[FATO]** o OkHttp manda pings automáticos (intervalo configurável), mas não expõe Ping manual nem o RTT. Como o WebSocket interno corre sobre TLS aninhado (spec §19.2 item 17), a biblioteca ainda está em aberto; se nenhuma expuser Ping/Pong, medir o RTT exige mensagem TRCP própria (mudança de spec). | M0, P3 |

## 8. Quadro-resumo dos NFRs

| Id | Requisito | Meta principal | Fase |
|---|---|---|---|
| NFR-01 | Agente ocioso: memória | Private Bytes ≤ 20 MB | M0, M2, M6 |
| NFR-02 | Agente: por sessão | ≤ 5 MB, histórico cheio | M0, M2 |
| NFR-03 | Agente ocioso: CPU | ≤ 0,1 % de um núcleo, ≤ 2 despertares/s | M0, M2, M6 |
| NFR-04 | Agente em uso: CPU | ≤ 2 % (4 sessões + 1 celular) | M2, M6, M7 |
| NFR-05 | Agente sob rajada | memória limitada, frames ≤ 20/s | M2, M6 |
| NFR-06 | Tamanho de instalação | agente, VSIX e ponte ≤ 15 MB | M2, M4, M6 |
| NFR-07 | Agente: por conexão remota | ≤ 512 KB | M6 |
| NFR-08 | Extensão: ativação | `onStartupFinished`, ≤ 100 ms p95 | M4 |
| NFR-09 | Extensão: memória | ≤ 10 MB a mais, sem módulo nativo | M4 |
| NFR-10 | Terminal local via agente | +10 ms tecla, +150 ms abrir (p95) | M0, M4 |
| NFR-11 | Vazão local | ≤ 1,5 × o nativo | M4 |
| NFR-12 | Tamanho do app | download ≤ 10 MB | M7 |
| NFR-13 | Memória do app | PSS ≤ 150 MB, sem vazamento | M7 |
| NFR-14 | Fluidez | `frameOverrunMs` p95 ≤ 0 | M7 |
| NFR-15 | Ponte: memória | ≤ 64 KB por conexão ociosa | M6 |
| NFR-16 | Ponte: capacidade (e2-micro) | 1 000 agentes + 50 pares, CPU ≤ 20 % | M6 |
| NFR-17 | Ponte: repasse | p99 ≤ 2 ms | M6 |
| NFR-18 | Ponte: saída de dados | acompanhamento, alerta > 1 GB/mês | M6+ |
| NFR-20 | Enviar → eco, ponte BR | p95 ≤ 150 ms Wi-Fi (4G: DP-2) | M6, M7 |
| NFR-21 | Enviar → eco, ponte EUA | p95 ≤ 400 ms Wi-Fi (4G: DP-2) | M6, M7 |
| NFR-22 | Contribuição do agente | p95 ≤ 5 ms parado, ≤ 55 ms rajada | M2, M6 |
| NFR-23 | Abrir → computadores | TTID p95 ≤ 1,5 s | M7 |
| NFR-24 | Abrir → terminais ao vivo | p95 ≤ 2,0 s BR / 3,5 s EUA | M7 |
| NFR-25 | Reconexão | p95 ≤ 3 s BR / 4 s EUA | M6, M7 |
| NFR-26 | Pareamento | p95 ≤ 3 s até o modal; ≤ 2 s depois | M6, M7 |
| NFR-27 | Taxa de `stale` | medição; gatilho 20 % em C2 | M6, M7 |
| NFR-30 | Só em primeiro plano | sem conexão ≤ 5 s depois de sair | M7 |
| NFR-31 | Segundo plano | 8 h com 0 wakelock, 0 job, 0 byte | M7, M8 |
| NFR-32 | Custo por push | notificação ≤ 10 s (100 %), ≤ 30 KB | M8 |
| NFR-33 | Push de ponta a ponta | p50 ≤ 5 s, p95 ≤ 15 s em Doze | M8 |
| NFR-34 | Dados por minuto | C1 ≤ 10 KB; C2 ≤ 1 MB; pior ≤ 4 MB (DP-3) | M6, M7 |
| NFR-35 | CPU do app | ≤ 5 % (C1), ≤ 15 % (C3) | M7 |
| NFR-40 | Rede ruim (N3) | p95 ≤ 1 s, 0 duplicados | M6, M7 |
| NFR-41 | Wi-Fi ↔ 4G | 0 duplicado, 0 sem resposta | M7 |
| NFR-42 | PC dormindo | offline ≤ 60 s; de volta ≤ 10 s; 0 sessões perdidas | M6, M7 |
| NFR-43 | Queda do agente | snapshot ≤ 3 s; banco íntegro | M2, M6 |
| NFR-44 | Conexão morta em silêncio | detectada ≤ 45 s | M6, M7 |
| NFR-45 | Contrapressão isolada | outros dentro de NFR-20 + 10 % | M6 |
| NFR-50 | 64 sessões | memória linear, CPU ≤ 0,5 % | M2, M6 |
| NFR-51 | 8 conexões remotas | CPU ≤ 25 %, latência + 20 % | M6 |
| NFR-60 | EX1: limite por origem | 6/min, rajada 3; global 30/min | fase da EX1 |
| NFR-61 | EX1: aviso → celular | 1 s em primeiro plano; p95 ≤ 15 s por push | fase da EX1, M8 |

## 9. Referências

Externas, conferidas em 2026-09-26:

- Android, Doze e App Standby (restrições e comandos `adb`):
  https://developer.android.com/training/monitoring-device-state/doze-standby
- Android, App Standby Buckets:
  https://developer.android.com/topic/performance/appstandby
- FCM, prioridade de mensagens (Doze, rebaixamento, 7 dias):
  https://firebase.google.com/docs/cloud-messaging/android/message-priority
- FCM, receber mensagens (janela de 10 s, WorkManager):
  https://firebase.google.com/docs/cloud-messaging/android/receive-messages
- FCM, tipos de mensagem (4096 bytes):
  https://firebase.google.com/docs/cloud-messaging/customize-messages/set-message-type
- Android, tempo de partida (TTID, TTFD, `reportFullyDrawn`):
  https://developer.android.com/topic/performance/vitals/launch-time
- Android vitals, limites de partida (5 s / 2 s / 1,5 s):
  https://developer.android.com/google/play/vitals/launch-time
- Macrobenchmark, métricas:
  https://developer.android.com/topic/performance/benchmarking/macrobenchmark-metrics
- Power Profiler (ODPM, Pixel 6+):
  https://developer.android.com/studio/profile/power-profiler
- Battery Historian (não mantido) e `batterystats`:
  https://developer.android.com/topic/performance/power/setup-battery-historian
- `bundletool get-size total`: https://developer.android.com/tools/bundletool
- Emulador, `-netdelay` e `-netspeed`:
  https://developer.android.com/studio/run/emulator-commandline
- GCE, tipos de máquina E2 compartilhados (e2-micro):
  https://docs.cloud.google.com/compute/docs/general-purpose-machines
- GCE, free tier: https://docs.cloud.google.com/free/docs/free-cloud-features
- Windows, pseudoconsole (threads por canal):
  https://learn.microsoft.com/windows/console/creating-a-pseudoconsole-session
- .NET, `Process.PrivateMemorySize64` (= Private Bytes):
  https://learn.microsoft.com/dotnet/api/system.diagnostics.process.privatememorysize64
- Windows Performance Recorder (ETW):
  https://learn.microsoft.com/windows-hardware/test/wpt/windows-performance-recorder
- VS Code, eventos de ativação (`onStartupFinished`):
  https://code.visualstudio.com/api/references/activation-events
- SQLite, `PRAGMA cache_size`: https://www.sqlite.org/pragma.html
- `tungstenite`, `WebSocketConfig`:
  https://docs.rs/tungstenite/latest/tungstenite/protocol/struct.WebSocketConfig.html
- OkHttp, interface `WebSocket`:
  https://github.com/square/okhttp/blob/master/okhttp/src/commonJvmAndroid/kotlin/okhttp3/WebSocket.kt
- RFC 5382, NAT para TCP (REQ-5): https://www.rfc-editor.org/rfc/rfc5382
- RFC 8446, TLS 1.3 (§5.2, registro): https://www.rfc-editor.org/rfc/rfc8446
- `tc netem`: https://man7.org/linux/man-pages/man8/tc-netem.8.html
- clumsy: https://jagt.github.io/clumsy/
- Typometer: https://pavelfatin.com/typometer/

Citado de memória, sem reabrir hoje: Mathis, Semke, Mahdavi e Ott, "The
Macroscopic Behavior of the TCP Congestion Avoidance Algorithm", ACM
CCR, 1997 (§2.10). **[verificar]**

Internas:

- `docs/auditoria-arquitetura-2026-09-26.md` §3 (A8, M4), §4.3, §5.6,
  §7.1, §7.2, §8, §13
- `docs/proposta-conexao-por-codigo-2026-09-26.md` §3, §4, §4.1
- `docs/spec/trcp-1.md` §3, §5, §8, §9, §10.5, §13.5, §14, §17, §19
- `docs/adr/0001`, `0002`, `0004`, `0006`, `0007`, `0011`, `0012`, `0014`
- `docs/interfaces/android.md` §0, §5–§7; `fluxos.md` F2, F7;
  `textos.md` (`settings.bridge_ok`)
- `docs/exigencias-externas.md` EX1
- `docs/plans/00-mapa-do-planejamento.md`
