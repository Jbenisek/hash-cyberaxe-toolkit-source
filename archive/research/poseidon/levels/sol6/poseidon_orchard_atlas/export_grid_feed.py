"""Consolidate CSVs and exact JSON into a schema-labeled, lossless grid feed."""
from pathlib import Path
import csv,json
from poseidon_core import parameters
B=Path(__file__).resolve().parent;D=B/'data';rc,m,mi=parameters()
def records(path):
    with path.open() as f:return list(csv.DictReader(f))
feed={'schema_version':1,'instance':'Orchard P128Pow5T3, RF8/RP56','proposal_commit':'01f736268b7086d97f38837d343d63a81bf31649','round_indexing':'0-based; source-before-i -> target-after-j','scope':'CSV records preserve strings for lossless numeric import; exact field values remain hex/text. Native, sampled, toy and source facts have separate evidence labels.','tables':{},'certificates':{}}
for p in sorted(D.glob('*.csv')):feed['tables'][p.stem]=records(p)
for p in sorted(D.glob('*.json')):
    if p.name not in ('atlas_feed.json','stage_graph.json'):feed['certificates'][p.stem]=json.loads(p.read_text())
(D/'atlas_feed.json').write_text(json.dumps(feed,indent=2)+'\n')
for row in records(D/'round_cards.csv'):
    i=int(row['round_index'])
    (B/'round_cards'/f'round_{i:02d}.json').write_text(json.dumps(row,indent=2)+'\n')
nodes=[];edges=[]
for boundary in range(65):
 for j in range(3):
    nodes.append({'id':f's{boundary}_{j}','type':'state','boundary':boundary,'lane':j,'input_role':('free_message' if j<2 else 'fixed_capacity') if boundary==0 else 'derived_internal','output_role':'digest' if boundary==64 and j==0 else 'internal'})
for i in range(64):
    full=i<4 or i>=60
    pre=[]
    for j in range(3):
        a=f'a{i}_{j}';nodes.append({'id':a,'type':'add_constant','round':i,'lane':j,'constant_hex':f'{rc[i][j]:064x}'})
        edges.append({'source':f's{i}_{j}','target':a,'kind':'add_constant'})
        if full or j==0:
            b=f'b{i}_{j}';nodes.append({'id':b,'type':'power5','round':i,'lane':j})
            edges.append({'source':a,'target':b,'kind':'nonlinear_power5'});pre.append(b)
        else:pre.append(a)
    for j in range(3):
        for k in range(3):edges.append({'source':pre[k],'target':f's{i+1}_{j}','kind':'linear_MDS_term','coefficient_hex':f'{m[j][k]:064x}'})
graph={'schema_version':1,'kind':'exact equation dependency graph, not necessary finite-change graph','nodes':nodes,'edges':edges,'node_count':len(nodes),'edge_count':len(edges)}
(D/'stage_graph.json').write_text(json.dumps(graph,indent=2)+'\n')
assert (len(nodes),len(edges))==(467,848)
print('grid JSON tables',len(feed['tables']),'stage graph',len(nodes),'nodes',len(edges),'edges')
