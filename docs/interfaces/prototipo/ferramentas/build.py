import json, re, sys
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'proto.src.html')
CAT = os.path.join(HERE, '..', 'textos.catalogo.json')
OUT = os.path.join(HERE, '..', 'index.html')
src = open(SRC, encoding='utf-8').read()
src = src.replace('--offline:#595F6A;', '--offline:#595F6A; --kite-tail:#11141A; --frame:#11141A;', 1)
src = src.replace('--offline:#8A91A0;', '--offline:#8A91A0; --kite-tail:#F2A93B; --frame:#3A404C;')
cat = json.load(open(CAT, encoding='utf-8'))
flat = {}
for s in cat['secoes']:
    for k, v in s['itens'].items():
        if k in flat: print('DUP', k)
        flat[k] = v
used = set(re.findall(r"""\bT?t?\(\s*'([a-z_]+\.[a-z0-9_\.]+)'""", src))
used |= set(re.findall(r"""\bT\(\s*'([a-z_]+\.[a-z0-9_\.]+)'""", src))
used |= set(re.findall(r"""data-fmt="([a-z_]+\.[a-z0-9_]+)\"""", src))
used |= set(re.findall(r"""\['([a-z_]+\.[a-z0-9_]+)'""", src))
pres = re.findall(r"""^\s*\['([a-z_]+)',\(\)=>""", src, re.M)
used |= {'proto.p_' + p for p in pres}
for k in ['pair.err_%s_%s' % (e, x) for e in ['expired','wrong','rejected','timeout','bridge'] for x in ['title','body']]:
    used.add(k)
miss = sorted(k for k in used if k not in flat and not k.startswith('i-'))
print('usadas', len(used), 'catalogo', len(flat), 'ausentes', miss)
out = src.replace('__CATALOG__', json.dumps(flat, ensure_ascii=False, separators=(',', ':')))
open(OUT, 'w', encoding='utf-8', newline='\n').write(out)
print('ok', len(out.encode('utf-8')), 'bytes')
