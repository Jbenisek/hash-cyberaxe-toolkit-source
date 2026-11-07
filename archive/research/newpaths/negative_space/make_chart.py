"""Turn records.csv (ours) and records_others.csv (other teams) into a simple local dot chart: method_map.html.
Run: python -B make_chart.py   then open method_map.html in a browser."""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
rows = []
for path, who in ((os.path.join(HERE, "records.csv"), "ours"),
                  (os.path.join(HERE, "..", "negative_space_others", "records_others.csv"), "others")):
    if not os.path.exists(path):
        continue
    for r in csv.DictReader(open(path, encoding="utf-8")):
        try:
            cost = float(r.get("cost") or "")
        except ValueError:
            cost = None
        rows.append({"who": who, "id": r.get("id", ""), "name": (r.get("name") or "")[:90],
                     "free": r.get("free", ""), "part": r.get("part", ""), "layer": r.get("layer", ""),
                     "tech": r.get("tech", ""), "res": r.get("res", ""), "goal": r.get("goal", ""),
                     "status": r.get("status", ""), "cost": cost, "team": r.get("team/entry", "")})

html = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Method Map</title><style>
:root{--bg:#fafaf7;--fg:#222;--muted:#777;--grid:#ddd;--alive:#1a9a50;--dead:#c0392b;--open:#d68910;--na:#888}
@media (prefers-color-scheme:dark){:root{--bg:#16181c;--fg:#e8e8e8;--muted:#999;--grid:#333}}
body{margin:0;padding:16px;background:var(--bg);color:var(--fg);font:14px system-ui,sans-serif}
h1{font-size:20px;margin:0 0 8px}.bar{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:8px}
svg{width:100%;height:auto;display:block}#tip{position:fixed;pointer-events:none;background:var(--bg);border:1px solid var(--grid);
padding:6px 8px;border-radius:6px;max-width:320px;display:none;font-size:12px}.lg span{margin-right:12px}
.dot-alive{fill:var(--alive)}.dot-dead{fill:var(--dead)}.dot-open{fill:var(--open)}.dot-n\\/a{fill:var(--na)}
</style></head><body><h1>Method Map</h1>
<div class="bar"><label>Group by <select id="ax"><option>tech</option><option>free</option><option>part</option><option>layer</option>
<option>res</option><option>goal</option></select></label><label><input type="checkbox" id="oth" checked> other teams (hollow)</label>
<span class="lg"><span style="color:var(--alive)">&#9679; alive</span><span style="color:var(--dead)">&#9679; dead</span>
<span style="color:var(--open)">&#9679; open</span><span style="color:var(--na)">&#9679; n/a</span></span></div>
<div style="color:var(--muted);font-size:12px">Each dot is one method. Up is costlier (log2 of the work); the dashed line is the
generic 128. Dots without a cost sit in the band at the very top; dots are spread a little so overlaps show.</div><svg id="c"></svg><div id="tip"></div>
<script>const D=__DATA__;
const svg=document.getElementById('c'),tip=document.getElementById('tip');
function draw(){const ax=document.getElementById('ax').value,oth=document.getElementById('oth').checked;
const rows=D.filter(r=>oth||r.who==='ours');const cats=[...new Set(rows.map(r=>r[ax]||'-'))].sort();
const W=Math.max(640,cats.length*90),H=560,L=50,B=110,T=60;svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
const cs=rows.map(r=>r.cost).filter(c=>c!==null&&isFinite(c)),hi=Math.min(Math.max(...cs,130),520),lo=Math.max(Math.min(...cs,0),0);
const y=c=>T+(H-B-T)*(1-((Math.min(c===null?hi:c,hi))-lo)/(hi-lo||1));const x=i=>L+(W-L-20)*(i+0.5)/cats.length;
let s='';for(let v=Math.ceil(lo/32)*32;v<=hi;v+=32)s+=`<line x1="${L}" x2="${W-10}" y1="${y(v)}" y2="${y(v)}" stroke="var(--grid)"/><text x="${L-6}" y="${y(v)+4}" text-anchor="end" font-size="11" fill="var(--muted)">${v}</text>`;
s+=`<line x1="${L}" x2="${W-10}" y1="${y(128)}" y2="${y(128)}" stroke="var(--muted)" stroke-dasharray="5 4"/>`;
cats.forEach((c,i)=>s+=`<text transform="translate(${x(i)},${H-B+14}) rotate(35)" font-size="11" fill="var(--fg)">${c}</text>`);
rows.forEach((r,k)=>{const i=cats.indexOf(r[ax]||'-');const jx=x(i)+((k*37)%60-30),jy=(r.cost===null?8+((k*53)%40):y(r.cost)+((k*29)%11-5));
const cl='dot-'+(r.status||'n/a');s+=r.who==='ours'?`<circle class="${cl}" cx="${jx}" cy="${jy}" r="5" data-k="${k}" opacity="0.85"/>`
:`<circle cx="${jx}" cy="${jy}" r="5" fill="none" stroke-width="1.6" style="stroke:var(--${r.status==='n/a'?'na':(r.status||'na')})" data-k="${k}"/>`;});
svg.innerHTML=s;svg.querySelectorAll('circle').forEach(el=>{const r=rows[+el.dataset.k];
el.onmousemove=e=>{tip.style.display='block';tip.style.left=(e.clientX+12)+'px';tip.style.top=(e.clientY+12)+'px';
tip.innerHTML=`<b>${r.name}</b><br>${r.who==='others'?(r.team||'other team')+'<br>':''}status: ${r.status}; cost: ${r.cost===null?'-':r.cost}<br>${ax}: ${r[ax]||'-'}`;};
el.onmouseleave=()=>tip.style.display='none';el.onclick=el.onmousemove;});}
document.getElementById('ax').onchange=draw;document.getElementById('oth').onchange=draw;draw();
</script></body></html>"""
out = os.path.join(HERE, "method_map.html")
open(out, "w", encoding="utf-8").write(html.replace("__DATA__", json.dumps(rows)))
print(f"{out}: {len(rows)} dots ({sum(r['who']=='ours' for r in rows)} ours, {sum(r['who']=='others' for r in rows)} others)")
