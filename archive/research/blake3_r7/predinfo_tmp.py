import sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import bsrho as b
st = b.step256()
print(b.ROUNDS, "ops", st.ops)
