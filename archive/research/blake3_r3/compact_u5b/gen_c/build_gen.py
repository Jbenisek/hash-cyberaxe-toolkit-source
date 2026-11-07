import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_r7 as build
H = os.path.dirname(os.path.abspath(__file__))
stack = int(sys.argv[1]) if len(sys.argv) > 1 else 4096
extra = sys.argv[2:]
ok = build.cc(os.path.join(H, "gen.c"), os.path.join(H, "gen.wasm"), ["run", "info_ptr", "code_ptr"], stack=stack, extra=["-Wall"] + extra)
sys.exit(0 if ok else 1)
