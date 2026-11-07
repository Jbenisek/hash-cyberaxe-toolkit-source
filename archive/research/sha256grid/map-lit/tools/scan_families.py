
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

import json, re, sys, os, collections
R = _hca_public_path_text('__HCA_WORKSPACE__/research/rivals')
boards = {
    "r31": os.path.join(R, "boards_sha256-r31-exploratory.json"),
    "r32": os.path.join(R, "boards_sha256-r32-exploratory.json"),
    "r37": os.path.join(R, "boards_sha256-r37-exploratory_live.json"),
    "r38": os.path.join(R, "boards_sha256-r38-exploratory_live.json"),
}
# family tag -> regex (case-insensitive)
fam = collections.OrderedDict([
    ("generic_birthday", r"birthday|distinguished[- ]point|van oorschot|pollard|\brho\b|radix|hash[- ]table birthday|tabulation"),
    ("grouped_partial_eval", r"grouped|round[- ]skip|partial[- ]evaluation|partial-charge|early key|pre-last-round key|last four rounds"),
    ("two_block_char", r"two-block|first[- ]block|second[- ]block|chaining value|\bCV1\b"),
    ("published_char_as_text", r"public algorithm text|published characteristic|characteristic as public"),
    ("own_char_search_SAT", r"\bSAT\b|\bSMT\b|\bSTP\b|cryptominisat|kissat|\bz3\b|\bMILP\b|cadical|route search|characteristic search|trail search"),
    ("starting_point_solver", r"starting point|starting solution|start solution|Step-1 solution|dense part|dense-part"),
    ("multi_start_union", r"many starting|starting points|eight-tuple|2\^18 Step-1|variants of the Step-1|A0-variant|S-variant|dense-part variants|222 classes|variant famil|valid tuples|TAB2|exact union"),
    ("condition_relaxation", r"relax|necessary condition|misprint|weakest condition|not necessary"),
    ("neutral_bits", r"neutral bit|neutral word|neutral"),
    ("boomerang_tunnel", r"boomerang|tunnel|auxiliary (path|differential)|amplif"),
    ("message_modification", r"message modification|advanced message|modif(y|ication) of message"),
    ("near_collision_multiblock", r"near[- ]collision|three-block|3-block|multi[- ]block|multiblock"),
    ("mitm", r"meet-in-the-middle|\bMITM\b|meet in the middle"),
    ("table_lookup_precomp", r"lookup table|row-16 table|x-indexed table|fibre|fiber|bucket|bitmap|precomputed (table|record)"),
    ("early_abort_staged", r"early[- ]abort|staged|stage[- ]?1[67]|decision-DAG"),
    ("bitslice_swar", r"bit-slic|bitslic|SWAR|\d+-lane|guard-bit|lanes per"),
    ("gpu", r"\bGPU\b|CUDA|graphics card|RTX"),
    ("sfs_or_freestart", r"semi-free-start|free-start|\bSFS\b"),
    ("accounting_instr_price", r"retired instruction|callgrind|per-form|instruction price|CPU-second|CPU-s\b|valgrind"),
    ("register_machine", r"64 registers|register-machine|registers resident|liveness"),
    ("replay_stored_pair", r"replay|stored pair|retained collision|prespecified collision|fixed-witness|fixed witness"),
    ("success_prob_engineering", r"Bernstein|Cauchy|second moment|cap-stop|success floor|Chebyshev|Paley"),
])
rx = {k: re.compile(v, re.I) for k, v in fam.items()}
out_rows = []
counts = {b: collections.Counter() for b in boards}
users = {b: collections.defaultdict(set) for b in boards}
for b, p in boards.items():
    d = json.load(open(p, encoding="utf-8"))
    for s in d["submissions"]:
        note = s.get("note") or ""
        tags = [k for k in fam if rx[k].search(note)]
        sc = s.get("officialScore")
        out_rows.append((b, s["id"][:8], s.get("solverUsername"), s.get("status"), sc, tags))
        for t in tags:
            counts[b][t] += 1
            users[b][t].add(s["id"][:8])
mode = sys.argv[1] if len(sys.argv) > 1 else "counts"
if mode == "counts":
    print("family".ljust(26), *[b.rjust(5) for b in boards])
    for k in fam:
        print(k.ljust(26), *[str(counts[b][k]).rjust(5) for b in boards])
    print("entries:", {b: sum(1 for r in out_rows if r[0] == b) for b in boards})
elif mode == "tsv":
    outp = sys.argv[2]
    with open(outp, "w", encoding="utf-8", newline="") as f:
        f.write("# COMPUTED 2026-10-10 by scan_families.py: keyword tags over each public note (noisy; a tag means the words appear, not that the technique is central)\n")
        f.write("board\tid8\tuser\tstatus\tofficial\ttags\n")
        for r in sorted(out_rows, key=lambda r: (r[0], r[4] if isinstance(r[4], (int, float)) else 1e9)):
            f.write("\t".join([r[0], r[1], str(r[2]), str(r[3]), str(r[4]), ",".join(r[5])]) + "\n")
    print("wrote", outp, len(out_rows))
    print("family".ljust(26), *[b.rjust(5) for b in boards])
    for k in fam:
        print(k.ljust(26), *[str(counts[b][k]).rjust(5) for b in boards])
elif mode == "ids":
    fams = sys.argv[2].split(",")
    for b in boards:
        for k in fams:
            ids = [r for r in out_rows if r[0] == b and k in r[5]]
            ids.sort(key=lambda r: (r[4] if isinstance(r[4], (int, float)) else 1e9))
            print(b, k, len(ids), " ".join(f"{r[1]}({r[2]},{r[3]},{r[4]})" for r in ids[:40]))
elif mode == "snip":
    # print context snippets for a regex in selected boards
    pat = re.compile(sys.argv[2], re.I)
    bsel = sys.argv[3].split(",")
    width = int(sys.argv[4]) if len(sys.argv) > 4 else 160
    for b, p in boards.items():
        if b not in bsel:
            continue
        d = json.load(open(p, encoding="utf-8"))
        for s in d["submissions"]:
            note = s.get("note") or ""
            for m in list(pat.finditer(note))[:3]:
                a = max(0, m.start() - width); z = min(len(note), m.end() + width)
                txt = re.sub(r"\s+", " ", note[a:z])
                print(f"[{b} {s['id'][:8]} {s.get('solverUsername')} {s.get('status')} {s.get('officialScore')}] ...{txt}...")
