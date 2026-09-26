import json
CAT = r'E:/Projetos DEV/vscode-remote/docs/interfaces/prototipo/textos.catalogo.json'
def load(): return json.load(open(CAT, encoding='utf-8'))
def save(c):
    d = lambda x: json.dumps(x, ensure_ascii=False)
    L = ['{', '  "_sobre": %s,' % d(c['_sobre']), '  "secoes": [']
    for si, s in enumerate(c['secoes']):
        L += ['    {', '      "id": %s,' % d(s['id']), '      "titulo": %s,' % d(s['titulo']), '      "itens": {']
        its = list(s['itens'].items())
        for i, (k, v) in enumerate(its):
            L.append('        %s: [%s, %s]%s' % (d(k), d(v[0]), d(v[1]), ',' if i < len(its) - 1 else ''))
        L += ['      }', '    }' + (',' if si < len(c['secoes']) - 1 else '')]
    L += ['  ]', '}', '']
    open(CAT, 'w', encoding='utf-8', newline='\n').write('\n'.join(L))
