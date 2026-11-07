# door 23 RELABEL test: rehash the SOLCLOUD_13 candidate pairs (read as data) with the organizer verifier reference.

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import zipfile,json,sys,struct
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/hash-smash'))
from verifier import blake3 as ref
# validate reference first: 7-round empty vector and 1-round/2-round self consistency
assert ref.blake3(b'',7).hex().startswith('af1349b9f5f9a1a6a0404dea36dcc949'),ref.blake3(b'',7).hex()
z=zipfile.ZipFile(_hca_public_path_text('__HCA_WORKSPACE__/SOL6Cloud\\SOLCLOUD_13\\SOLCLOUD_13_RESEARCH.zip'))
d=json.loads(z.read('SOLCLOUD_13_RESEARCH/tree/tree_certificate.json'))
res={}
for sect in ('oneblock_twoblock_candidates','forward_generated_candidates'):
    for e in d[sect]:
        r=int(e['rounds']); A=bytes.fromhex(e['message_A_hex']); B=bytes.fromhex(e['message_B_hex'])
        hA=ref.blake3(A,r); hB=ref.blake3(B,r)
        wA=struct.unpack('<8I',hA[:32]); wB=struct.unpack('<8I',hB[:32])
        diffw=[i for i in range(8) if wA[i]!=wB[i]]
        key=(sect,r)
        s=res.setdefault(key,dict(n=0,collide=0,lenA_B=set(),digest_matches_cert=0,diffwords=[],bits=[]))
        s['n']+=1; s['collide']+= (hA==hB); s['lenA_B'].add((len(A),len(B)))
        s['digest_matches_cert']+= (hA.hex()==e['digest_A'] and hB.hex()==e['digest_B']) if len(e['digest_A'])==64 else (hA.hex().startswith(e['digest_A'][:8]) )
        s['diffwords'].append(len(diffw)); s['bits'].append(bin(int.from_bytes(hA[:32],'big')^int.from_bytes(hB[:32],'big')).count('1'))
        s.setdefault('equal_cert_flag',0); s['equal_cert_flag']+= bool(e['equal_digest'])
for k,s in res.items():
    print(k,'pairs',s['n'],'collisions',s['collide'],'lens',sorted(s['lenA_B']),'certDigestMatch',s['digest_matches_cert'],'cert_equal_digest_flag',s['equal_cert_flag'],
      'diff words min/max',min(s['diffwords']),max(s['diffwords']),'diff bits min/mean/max',min(s['bits']),sum(s['bits'])/len(s['bits']),max(s['bits']))
