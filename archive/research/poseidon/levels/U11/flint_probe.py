import time
from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx, fmpz_mod_poly
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
ctx = fmpz_mod_ctx(P); pctx = fmpz_mod_poly_ctx(ctx)
x = pctx.gen()
f = (x - 5)*(x-77)*(x*x+x+3)
print(f.degree(), f.roots() if hasattr(f,'roots') else 'noroots')
print([m for m in dir(f) if not m.startswith('_')])
