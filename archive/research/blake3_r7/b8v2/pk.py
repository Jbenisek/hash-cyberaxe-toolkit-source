import sys; sys.path.insert(0,'.')
import bsrho_b7 as B
st=B.step256()
print(st.qwords, B.packed_circuit(st.qwords)[1], B.packed_circuit([0]*8)[1], B.other_code(st), B.HANDLER_CODE+B.RECOVERY_CODE+B.SETUP_CODE)
