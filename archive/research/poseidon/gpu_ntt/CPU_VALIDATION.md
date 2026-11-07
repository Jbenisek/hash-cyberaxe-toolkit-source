# CPU reference validation (D184)

The reference driver uses `boost::multiprecision::cpp_int` for the canonical
Pallas integer and independently checks 128 random field pairs.  It checks
canonical add, subtraction, multiplication, squaring, and the Montgomery
conversion; it also checks the polynomial remainder and Newton inverse
identity.

Recorded run (seed `0xd184cafe`):

```text
CPU_BIGINT_FIELD=PASS POLY_MOD=PASS NEWTON_INV=PASS
poly_product_deg=6 inverse_len=8 remainder_deg=0 power_deg=2
ops(add=2804 sub=2417 mul=29060 sqr=77312)
```

The final power is the requested exponent `(p-1)/2`, reduced modulo the
monic test polynomial `g=1+2X+X^3`; the reported operation totals include its
field operations and the preceding checks.
