cd "$(dirname "$0")/.."
nice -n 19 python3 -B - <<'PY'
import resource, json, sys, subprocess
def rss(cmd):
    r = subprocess.run(["/usr/bin/time", "-f", "%M"] + cmd, capture_output=True, text=True)
    return int(r.stderr.strip().split("\n")[-1]) / 1024.0
gen = rss(["python3", "-B", "ext/gen_only.py", "pkg/blake3/experiments"])
bare = rss(["python3", "-B", "-c", "pass"])
json.dump({"gen_mb": gen, "bare_mb": bare}, open("ext/pygen_rss.json", "w")); print(gen, bare)
PY
