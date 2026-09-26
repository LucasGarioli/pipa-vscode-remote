import json, sys

def lum(h):
    h = h.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

def cr(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)

T = {
 'light': {
  'bg': '#F4F1EA', 'surface': '#FCFBF7', 'surface2': '#E9E5DC', 'term': '#FFFDF8',
  'ink': '#11141A', 'ink2': '#3D434F', 'ink3': '#595F6A',
  'line': '#D6D0C4', 'lineStrong': '#857E70',
  'accent': '#F2A93B', 'onAccent': '#11141A', 'accentText': '#8A5300', 'accentSurface': '#FBE8C4', 'focus': '#8A5300',
  'ok': '#1C6B3B', 'okSurface': '#DCEFE2',
  'attn': '#8A5300', 'attnSurface': '#FBE8C4', 'attnStrong': '#B06C00',
  'armed': '#86277D', 'onArmed': '#FFFFFF', 'armedSurface': '#F4E0F0',
  'danger': '#B0251C', 'onDanger': '#FFFFFF', 'dangerSurface': '#F8E1DC',
  'offline': '#595F6A',
 },
 'dark': {
  'bg': '#11141A', 'surface': '#191D25', 'surface2': '#232833', 'term': '#0C0E12',
  'ink': '#ECE8DF', 'ink2': '#A3AAB8', 'ink3': '#8A91A0',
  'line': '#2C323D', 'lineStrong': '#6E7684',
  'accent': '#F2A93B', 'onAccent': '#11141A', 'accentText': '#F2A93B', 'accentSurface': '#3A2C12', 'focus': '#F2A93B',
  'ok': '#6CCB91', 'okSurface': '#132D1F',
  'attn': '#F2A93B', 'attnSurface': '#3A2C12', 'attnStrong': '#F2A93B',
  'armed': '#E48ADB', 'onArmed': '#2A0827', 'armedSurface': '#37163A',
  'danger': '#FF8A7D', 'onDanger': '#3A0803', 'dangerSurface': '#3B1511',
  'offline': '#8A91A0',
 },
}

ANSI = {
 'light': ['#1B2326','#B3261E','#1C6E3D','#7A5A00','#1F58B5','#8A2A80','#0A6A73','#4A575C',
           '#5F6C71','#A1261D','#1A6A3A','#735400','#1C51A8','#7D2574','#07606A','#162024'],
 'dark':  ['#A7B3B8','#FF8A7D','#6CCB91','#EDBE4C','#7FB0FF','#E48ADB','#5FC4CD','#C9D2D5',
           '#8A979C','#FFA69B','#8BDDAA','#F6D27A','#A3C6FF','#EFA8E8','#86D6DD','#F2F6F7'],
}

# (fg, bg, min, kind)
PAIRS = [
 ('ink','bg',4.5,'texto'),('ink','surface',4.5,'texto'),('ink','surface2',4.5,'texto'),('ink','term',4.5,'texto terminal'),
 ('ink2','bg',4.5,'texto secundário'),('ink2','surface',4.5,'texto secundário'),('ink2','surface2',4.5,'texto secundário'),
 ('ink3','surface',4.5,'placeholder / meta'),('ink3','bg',4.5,'placeholder / meta'),
 ('lineStrong','surface',3,'borda de campo (1.4.11)'),('lineStrong','bg',3,'borda de campo (1.4.11)'),
 ('accentText','surface',4.5,'link / texto de acento'),('accentText','bg',4.5,'link / texto de acento'),
 ('onAccent','accent',4.5,'rótulo botão primário'),('accentText','accentSurface',4.5,'chip de acento'),
 ('focus','bg',3,'anel de foco (1.4.11)'),('focus','surface',3,'anel de foco (1.4.11)'),
 ('ink','accentSurface',4.5,'texto em cartão de atenção'),
 ('ok','surface',4.5,'status online'),('ok','okSurface',4.5,'chip ok'),
 ('attn','attnSurface',4.5,'chip atenção'),('attn','surface',4.5,'texto atenção'),('attnStrong','surface',3,'ícone/faixa atenção (1.4.11)'),
 ('armed','surface',4.5,'texto escrita liberada'),('onArmed','armed',4.5,'faixa escrita liberada'),('armed','armedSurface',4.5,'chip escrita'),
 ('danger','surface',4.5,'texto perigo'),('onDanger','danger',4.5,'botão destrutivo'),('ink2','accentSurface',4.5,'texto secundário em cartão de atenção'),('ink2','armedSurface',4.5,'texto secundário em faixa de escrita'),('danger','dangerSurface',4.5,'banner erro'),
 ('offline','surface',4.5,'status offline'),
]

out = {}
fail = 0
for theme, t in T.items():
    rows = []
    for fg, bg, mn, kind in PAIRS:
        v = cr(t[fg], t[bg])
        ok = v >= mn
        fail += (not ok)
        rows.append((fg, t[fg], bg, t[bg], round(v, 2), mn, kind, ok))
    for i, c in enumerate(ANSI[theme]):
        v = cr(c, t['term'])
        ok = v >= 4.5
        fail += (not ok)
        rows.append((f'ansi{i}', c, 'term', t['term'], round(v, 2), 4.5, 'cor ANSI no terminal', ok))
    out[theme] = rows

if '--md' in sys.argv:
    for theme, rows in out.items():
        print(f'\n#### Tema {"claro" if theme=="light" else "escuro"}\n')
        print('| Primeiro plano | Fundo | Razão medida | Mínimo | Uso | Resultado |')
        print('|---|---|---|---|---|---|')
        for fg, fgc, bg, bgc, v, mn, kind, ok in rows:
            print(f'| `{fg}` {fgc} | `{bg}` {bgc} | **{str(v).replace(".", ",")}:1** | {str(mn).replace(".", ",")}:1 | {kind} | {"passa" if ok else "FALHA"} |')
else:
    for theme, rows in out.items():
        for r in rows:
            if not r[-1] or '-v' in sys.argv:
                print(theme, r)
    print('falhas:', fail)
