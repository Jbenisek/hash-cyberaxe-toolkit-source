
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

import json,sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig'))
import add_cell
o=json.load(open('work/scan_m1415.out.json'))
ev="research/dig/incoming/blake3-r2-U13/work/scan_m1415.py; research/dig/incoming/blake3-r2-U13/work/scan_m1415.out.json; research/dig/incoming/blake3-r2-U13/work/b3lib.py; research/dig/incoming/blake3-r2-U13/work/validate_b3.py"
qtext={'Q1':'difference/condition count at this word','Q2':'necessity of each condition group (relax, recount outcome mass)','Q3':'degrees of freedom (exact over carries)','Q4':'alternative outcomes / carry patterns and whether they reach the same later differences'}
st={'Q1':'COMPUTED','Q2':'SAMPLED','Q3':'COMPUTED','Q4':'SAMPLED'}
for i in (14,15):
    w='m%d'%i; ww='w%d'%i; q2=o['Q2'][ww]
    pad = "bytes 56-59" if i==14 else "bytes 60-63 (B may use only the low 3 bytes of a 63-byte block)"
    num={
    'Q1':f"Difference: 0 bits ({ww} = 0 in both A and B in 0 of 20000 sampled blocks differ or are nonzero). Classification: padding word, a constant zero, not free, not pinned by X3/X7/X11/X15; the 55-byte length of block A forces {pad} to be zero, and the construction has no parameter for it. Constants X3/X7/X11/X15 hold in 2000/2000 builds with {ww}=0. No condition counted on it (0 bits).",
    'Q2':f"Relax {ww}=0: nonzero {ww} in B only, {q2['trials_B_only']} trials: lemma-H digest words 0,2,5,7 kept {q2['lemmaH_kept']}, mean digest words differing {q2['mean_digest_words_differ']}/8 (min {q2['min_digest_words_differ']}). Same nonzero value in both blocks: X3/X7/X11/X15 kept {q2['same_nonzero_both_blocks_consts_kept']}/{q2['trials_both']}, lemma H kept {q2['same_nonzero_both_lemmaH_kept']}/{q2['trials_both']} (A would also break the 55-byte padding rule). The zero is necessary for the construction as built; any change loses all sampled outcome mass.",
    'Q3':f"Degrees of freedom: 0. {ww} takes the single value 0 over 50000 builds of the 8-parameter construction; length 55 forces it. The whole block still has 8 free 32-bit parameters (256 bits) = 12 free words minus 128 bits of X3/X7/X11/X15; {ww} adds nothing and the word cannot be spent as freedom. Whether a longer message shape (more nonzero bytes in A) could make {ww} free with a re-derived inversion was not tested (different length changes the counter word n in the state).",
    'Q4':f"Alternative: B-only (w14,w15)=(dl,-dl mod 2^24), {o['Q4_alt']['trials']} trials: lemma H kept {o['Q4_alt']['lemmaH']}, mean digest words differing {o['Q4_alt']['mean_words_differ']}/8. No carry alternative for {ww}: no addition on it can absorb a difference because the only difference in the pair is in w4,w5 (the 75/32 carry effect lives there); {ww} must be zero and equal in A and B."}
    for q in ('Q1','Q2','Q3','Q4'):
        cid=f"blake3-r2|{w}|msgword|{q}"
        r=dict(hash='blake3-r2',row_i=None,row_j=None,object=f"message word {w} ({ww}): zero padding word, constant 0 in A and B",
          question=f"{q} {qtext[q]}",labels=['N','0'] if q in('Q1','Q3') else ['N'],status=st[q],number=num[q],source="our workflow: scan-once",own_test=True,
          evidence=ev,date="2026-10-12",lever=False,gain_bits=None,
          notes=f"Universe cell {cid}. Own b3lib construction (pkgB3U Sec 4) validated 3000/3000 first (U10 copy). Sampled window of the 8-parameter construction; U06 template adapted. No gain seen. Unit text says free/pinned/cancelling/forced; finding is a fourth class, padding zero.",
          topic=f"blake3-r2 msgword {w}")
        fn=f"{cid.replace('|','_')}.json"
        json.dump(r,open(fn,'w'),indent=1)
        add_cell.validate(json.load(open(fn)),add_cell.load()); print('ok',fn)
