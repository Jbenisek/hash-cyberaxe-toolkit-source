// Runs the page's own drawGrids() on DATA.hgrids with a minimal DOM stub; prints table shape and the X-reason list size.
const fs = require('fs');
const s = fs.readFileSync(process.argv[2], 'utf8');
const data = JSON.parse(s.slice(s.indexOf('const DATA=') + 11, s.indexOf(';\nconst NS=')));
const hdef = s.match(/function h\(tag,text,cls\)\{[^\n]*\}/)[0];
const gcode = s.slice(s.indexOf('const GCL='), s.indexOf('drawGrids(DATA.grids'));
function El(tag) {
  return { tag, children: [], className: '', textContent: '', style: {},
    appendChild(c) { this.children.push(c); return c; } };
}
global.document = { createElement: El, createElementNS: (ns, t) => El(t),
  createTextNode: t => ({ tag: '#text', textContent: String(t), children: [] }) };
global.tip = { style: {} };
global.tipAt = function () {};
const run = new Function('data', 'El', hdef + '\n' + gcode + '\nconst host=El("div");drawGrids(data.hgrids||[],host,"missing");return host;');
const host = run(data, El);
const card = host.children[0];
const walk = (e, f) => { f(e); (e.children || []).forEach(c => walk(c, f)); };
let tds = [], ths = [], lis = 0, texts = {};
walk(card, e => { if (e.tag === 'td') { tds.push(e); texts[e.textContent] = (texts[e.textContent] || 0) + 1; }
  if (e.tag === 'th') ths.push(e); if (e.tag === 'li') lis++; });
console.log('cards', host.children.length, 'title', card.children[0].textContent);
console.log('th', ths.length, 'td', tds.length, 'X-reason items', lis);
console.log('td classes', JSON.stringify(tds.reduce((a, t) => (a[t.className || '(none)'] = (a[t.className || '(none)'] || 0) + 1, a), {})));
console.log('header', ths.slice(0, 7).map(t => t.textContent).join(' | '));
console.log('last line', card.children[card.children.length - 1].textContent);
