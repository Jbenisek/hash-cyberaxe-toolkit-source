
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

L = _hca_public_path_text('__HCA_WORKSPACE__/research/launch')
s = open(L + r"\submit_pareto_pos_b3r7c.sh", encoding="utf-8", newline="").read().replace("\r\n", "\n")


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("# Staged 10-15 in slot pos_b3r7c (pareto/blake3 r7, Lemma 2 v2 rebuild of 8fbecd8a (B3R7b, refuted)): time_log2 125.29113 (filed 125.29018 (8fbecd8a)). DO NOT RUN without the owner's go.",
    "# Staged 10-16 in slot pos_b3r7d (pareto/blake3 r7, first-collision Section 4 over the filed B3R7c): time_log2 125.26917 (filed 125.29113 (a2e94df7)). DO NOT RUN without the owner's go.")
rep("# THE SUBMIT of B3R7c: the same program and ledger as the filed entry, Section 4 (Lemma 2) replaced by Lemma 2 v2 (no premise besides H1, H2 withdrawn, Chernoff tail certified in exact arithmetic),\n# Section 9 answers the findings of the rulings by id (1cd0dd3b and the entry's own ruling where there is one).\n# First dependency 1cd0dd3b (see dependencies.json for the full credited list).",
    "# THE SUBMIT of B3R7d: the same program, step and ledger as the filed B3R7c, Section 4 (Lemma 2) rewritten as a first-collision proof (no premise besides H1), B and Tp re-planned.\n# First dependency a2e94df7 (B3R7c; see dependencies.json for the full credited list).")
rep("05494d7891533522c156f3406460a2aeb015d2c02333d3b1ebcf4db4a8c7c3d3", "523d13b53cd1a9397194dfe22589410ddf398c15391e7aea92fdd319b66b7c7d")
rep("(1cd0dd3b first)", "(a2e94df7 first)")
rep('startswith("1cd0dd3b"), "first dependency must be 1cd0dd3b"', 'startswith("a2e94df7"), "first dependency must be a2e94df7"')
rep("| B3R7c | ${SUB:-none} | $TL (Lemma 2 v2; filed 125.29018 (8fbecd8a)) | validating |", "| B3R7d | ${SUB:-none} | $TL (first-collision Section 4; filed 125.29113 (a2e94df7)) | validating |")
rep("pos_b3r7c", "pos_b3r7d", 6)
open(L + r"\submit_pareto_pos_b3r7d.sh", "w", encoding="utf-8", newline="\n").write(s)
print("ok")
