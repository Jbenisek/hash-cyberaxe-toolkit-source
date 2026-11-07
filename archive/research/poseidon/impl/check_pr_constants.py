"""Cross-check our constants (from public upstream fp.rs) against the PR 923 poseidon.py TEXT (parsed as data, never imported)."""
import re
from constants_own import P, ROUND_CONSTANTS, MDS
t = open('../pr923_data/poseidon.py').read()
rc_txt = t[t.index('ROUND_CONSTANTS = ('):t.index('MDS = (')]
mds_txt = t[t.index('MDS = ('):t.index('class MessageDomainError')]
pr_rc = [int(x, 16) for x in re.findall(r'0x[0-9a-f]{64}', rc_txt)]
pr_mds = [int(x, 16) for x in re.findall(r'0x[0-9a-f]{64}', mds_txt)]
assert len(pr_rc) == 192 and len(pr_mds) == 9
mine_rc = [x for row in ROUND_CONSTANTS for x in row]
mine_mds = [x for row in MDS for x in row]
print('round constants equal:', pr_rc == mine_rc, '| MDS equal:', pr_mds == mine_mds)
mp = re.search(r'MODULUS = (0x[0-9a-f]+)', t); print('modulus equal:', int(mp.group(1), 16) == P)
print('CAPACITY text:', re.search(r'CAPACITY_ELEMENT = .*', t).group(0))
