# Checks that research/endgame/endgame_map.html carries the SHA-256 grid (markup, JS call, embedded data) and writes the
# page script to page_script.js here for a node --check syntax pass. Prints only facts about the SHA-256 grid.
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(HERE, '..', '..', 'endgame', 'endgame_map.html')
s = open(PAGE, encoding='utf-8').read()
for m in ('id="s-hgrids"', 'id="hgrids"', 'href="#s-hgrids"', 'drawGrids(DATA.hgrids||[]'):
    print('%-28s %s' % (m, 'present' if s.count(m) == 1 else 'COUNT %d' % s.count(m)))
a = s.index('const DATA=') + len('const DATA=')
b = s.index(';\nconst NS=', a)
data = json.loads(s[a:b])
hg = data.get('hgrids') or []
print('hgrids grids:', len(hg), [g['title'] for g in hg])
for g in hg:
    marks = {}
    for c in g['cells']:
        marks[c['m']] = marks.get(c['m'], 0) + 1
    print('rows %d cols %s cells %d marks %s' % (len(g['rows']), g['cols'], len(g['cells']), marks))
    x = [c for c in g['cells'] if c['r'].startswith('F08') and c['c'] == 'r37'][0]
    print('sample F08 x r37 text=%r dead=%s why[:90]=%r' % (x['t'], x['d'], x['why'][:90]))
i = s.index('<script>') + len('<script>')
j = s.index('</script>', i)
open(os.path.join(HERE, 'page_script.js'), 'w', encoding='utf-8').write(s[i:j])
print('script chars', j - i)
