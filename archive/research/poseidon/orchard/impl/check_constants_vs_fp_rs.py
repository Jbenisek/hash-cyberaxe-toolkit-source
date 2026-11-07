"""Cross-check the organizer JSON constants/MDS against halo2_poseidon-0.2.0 fp.rs (fetched fresh, sha256 b19d4e50...)."""
import re, hashlib, os
from poseidon_ref import RC, MDS, P
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'upstream', 'fp.rs'), 'rb').read()
print('fp.rs sha256', hashlib.sha256(src).hexdigest())
txt = src.decode()
rc_part = txt[txt.index('ROUND_CONSTANTS'):txt.index('MDS')]
mds_part = txt[txt.index('pub(crate) const MDS'):]
mds_part = mds_part[:mds_part.index('MDS_INV')] if 'MDS_INV' in mds_part else mds_part
def elems(part):
    out = []
    for blk in re.findall(r'from_raw\(\[(.*?)\]\)', part, re.S):
        l = [int(x.replace('_', ''), 16) for x in re.findall(r'0x[0-9a-fA-F_]+', blk)]
        assert len(l) == 4
        out.append(sum(v << (64 * i) for i, v in enumerate(l)))
    return out
rc = elems(rc_part); m = elems(mds_part)
assert len(rc) == 192 and len(m) == 9, (len(rc), len(m))
print('round constants equal JSON:', [tuple(rc[3*i:3*i+3]) for i in range(64)] == [tuple(r) for r in RC])
print('MDS equal JSON:', [tuple(m[3*i:3*i+3]) for i in range(3)] == [tuple(r) for r in MDS])
