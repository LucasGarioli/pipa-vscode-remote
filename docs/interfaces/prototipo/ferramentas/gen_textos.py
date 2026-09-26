import catio
c = catio.load()
total = sum(len(s['itens']) for s in c['secoes'])
esc = lambda x: x.replace('|', '\\|').replace('\n', '<br>')
L = ['# Catálogo de textos (P7)', '',
     'Status: rascunho de planejamento, 2026-09-26. Gerado a partir de',
     '`prototipo/textos.catalogo.json`, que é a fonte única: toda string visível do',
     'protótipo sai de lá. Para mudar um texto, edite o JSON e gere de novo este',
     'arquivo e o protótipo.', '',
     f'Total: **{total} chaves** em {len(c["secoes"])} seções.', '',
     '## Regras', '',
     '- **Chaves estáveis.** A chave nunca muda quando o texto muda. No Android ela',
     '  vira `R.string.<chave com _ no lugar de .>`; na extensão vira a chave do',
     '  `package.nls.json` (textos do manifesto) ou do `l10n/bundle.l10n.json`',
     '  (textos em código, via `vscode.l10n.t`).',
     '- **Variáveis** entre chaves: `{pc}` nome do computador, `{device}` nome do',
     '  aparelho, `{session}` nome do terminal, `{n}` número, `{time}` hora ou',
     '  contagem regressiva, `{cmd}` comando, `{code}` código de confirmação,',
     '  `{bridge}` endereço do servidor (ponte), `{exit}` código de saída, `{tool}` ferramenta,',
     '  `{date}` data, `{when}` tempo relativo, `{ms}` latência, `{v}` versão, `{i}`',
     '  índice, `{keys}` teclas, `{name}` nome, `{cols}`/`{rows}` tamanho do terminal,',
     '  `{path}` pasta, `{known}` servidor dos outros computadores, `{source}` programa que',
     '  mandou um aviso, `{s}` segundos.',
     '- **Servidor, não ponte.** Nas telas, o servidor de retransmissão se chama',
     '  "servidor"; "ponte" e `trc-bridge` ficam nos documentos técnicos (AJ-34).',
     '- **Plurais**: chaves com `_one` / `_other` viram `plurals` no Android e',
     '  escolha por `n` na extensão.',
     '- **Tom**: frases curtas, verbo no começo dos botões, o objeto sempre nomeado',
     '  em confirmações ("Remover LUCAS-PC", nunca "Tem certeza?"). Nada de',
     '  jargão de protocolo na tela.',
     '- Chaves `*_a11y` são rótulos para TalkBack / leitor de tela, não aparecem',
     '  escritas.',
     '- Seção `proto.*` é só do protótipo; não vai para o produto.', '']
for s in c['secoes']:
    L += [f'## {s["titulo"]} (`{s["id"]}`)', '', '| Chave | PT-BR | EN |', '|---|---|---|']
    for k, (pt, en) in s['itens'].items():
        L.append(f'| `{k}` | {esc(pt)} | {esc(en)} |')
    L.append('')
open(r'E:/Projetos DEV/vscode-remote/docs/interfaces/textos.md', 'w', encoding='utf-8', newline='\n').write('\n'.join(L))
print('ok', total)
