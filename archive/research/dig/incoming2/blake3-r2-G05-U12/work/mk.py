
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

import json,os,sys
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig')); import add_cell
base=dict(hash="blake3-r2",row_i=None,row_j=None,source="our workflow: scan-once-wave2",own_test=True,date="2026-10-12",lever=False,gain_bits=None)
D="research/dig/incoming2/blake3-r2-G05-U12/work/"
recs={
"blake3-r2|DOOR.d37|DOOR|D1":dict(object="DOOR d37 fresh CV / prior block per context (mode lever)",question="RELABEL test: ledger arithmetic with all measured levers stacked: what does a fresh CV (one 430-op prior block) per context/member/block cost at the stacked ledger?",labels=["Z"],status="COMPUTED",
 number="Penalty bits (exact arithmetic, log2(1+added/N)), per context / per member / per block. Base 58.6197: 0.0067 / 0.0524 / 0.1029 (reproduces the record). Stacked, if the saving is in context COUNT: unchanged 0.0067 / 0.0524 / 0.1029 for pkgB3T 57.2365, omega 57.0055, B3W 56.7927. Stacked, if the saving is per-context WORK (upper bound): 0.0173 / 0.1328 / 0.2544 (57.2365); 0.0203 / 0.1547 / 0.2944 (57.0055); 0.0235 / 0.1778 / 0.3361 (56.7927). So the cost is 0.0067 to 0.0235 bit per context, 0.05 to 0.18 per member, 0.10 to 0.34 per block. No measured lever (LEVERS.md blake3 section, B3W/omega/tail stack) is found that uses CV freedom, so it buys back 0.",
 evidence=D+"d37_ledger.py, "+D+"d37_ledger.out",
 notes="universe cell blake3-r2|DOOR.d37|DOOR|D1. Door 37 stays KILL as standalone; the RELABEL test is now an own_test record. Check first: base penalty 0.0067 reproduced. Basis: pure arithmetic on recorded numbers (N 190440978718867836423, 2046750299405671 contexts, 430 ops per unit) from gridwave6/b3_layerxtech_mode_cost/RESULT.md; stacked scores 57.2365, 57.0055, 56.7927 are our HANDOFF/LEVERS values; how the stacked saving splits between context count and per-context work is NOT known to us, hence the bracket. No program of another participant was run. Not tested: a lever that needs a fresh CV (none identified), so 'no lever buys it back' is by search of the LEVERS list, not by proof.",gain_basis="T"),
"blake3-r2|DOOR.d38|DOOR|D1":dict(object="DOOR d38 parent/CV separability bias at 2 rounds",question="RELABEL test: RELAX 2/4 word-level model plus separability bias test at N=2^24",labels=["Z"],status="SAMPLED",
 number="RELAX 2 and RELAX 4 rerun (exhaustive over all 2^16 parent message patterns): model C minimum 7 word conditions (224 bits), 65535 patterns at the min, output byte-identical to the earlier gridwave6 run (cmp). Strict RELAX 0: 8 conditions (256 bits). Separability at N=2^24: T1 XOR max |P-1/2| 0.000338 (2.77 sigma, bit 223); T2 add max 0.000349 (2.86 sigma), P(word==0) max 0; T3 64 word cells x 2^18 quads worst 0.00384, flagged 0, confirmed 0; T4 1024 bit cells x 2^16 quads worst 0.00978, flagged 0, confirmed 0. Largest bias 0.00034 = 2^-11.5 (sampling noise, below the 2^-8 window), 0 usable biased bits.",
 evidence=D+"sep24.out, "+D+"summary_relax2.out, "+D+"summary_relax4.out, "+D+"c.log (code copied from research/gridwave6/b3_basextech_mode_join)",
 notes="universe cell blake3-r2|DOOR.d38|DOOR|D1. Known answer first: parent compress == organizer verifier blake3(rounds=2) 50/50, rounds=7 and the model rerun identical to reference. Kill criterion (>=7 conditions with relax, no separable bit) now holds at the tested sample size; the smoke run's 3.6 sigma max (0.0018 at 2^20) did not reappear at 2^24 (0.00034), consistent with noise. Sampled, not proved: bit-level cancellations inside a word are not in the word model; the 2^16 per-condition price is argued, not measured.",gain_basis="count"),
"blake3-r2|DOOR.d45|DOOR|D1":dict(object="DOOR d45 chaining-value route via 224-bit near-collision first block",question="No test given (low value). Own measurement: is matching 224 of 256 CV bits of a 2-round first block cheaper than generic?",labels=["Z"],status="LOCAL_ONLY",
 number="Toy widths only (k bits matched on words 1..7 of the 2-round CHUNK_START block CV, cv=IV, b=64, flags 1, N=2^22 random blocks): pairs/expected(uniform birthday) = 0.992 (k=32), 1.078 (k=36), 1.125 (k=40, 9 pairs), 0 seen vs 0.5 expected (k=44). No excess over generic. Generic price of a 224-bit match is 2^112 evaluations; the door's 2^64 is NOT reproduced by this measurement (2^64 is the generic price of a 128-bit match). Separately, word-model RELAX 2/4 minimum is 7 word conditions (224 bits) for a parent difference.",
 evidence=D+"d45_birthday.py, "+D+"d45.out",
 notes="universe cell blake3-r2|DOOR.d45|DOOR|D1. Known answer first: compress(flags=1) equals organizer verifier _compress 50/50. LOCAL_ONLY: toy k 32..44 and random (not structured) first blocks; a structured near-collision (e.g. message-difference trail with the 4-check structure) is not tested, so the claimed 2^64 stays unexplained rather than refuted; the only own number is generic 2^112. A full 256-bit collision of our root family costs ~2^57 but needs the root flags/length pins, which a non-final CHUNK_START block does not have.",gain_basis="count"),
}
for cid,r in recs.items():
    r=dict(base,**r); fn=cid.replace('|','_')+'.json'
    json.dump(r,open(fn,'w',encoding='utf-8'),indent=1)
    print(fn, add_cell.validate(json.load(open(fn,encoding='utf-8')), add_cell.load()))
