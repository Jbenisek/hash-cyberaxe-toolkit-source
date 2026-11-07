**Lemma N.** For a trial of 6.1 put beta = b1 XOR b1' and eps = c2 XOR c2',
both taken from E1, and

    n = eps XOR ROL(beta XOR eps, 1) XOR eta.

Let D3 and D6 be the XOR differences between A and B of digest words 3 and
6, which are the second and the fourth word of R. Then n = D3 XOR ROL(D6, 8)
for every trial. In particular R = 0 implies n = 0.

Proof. Digest word 3 is Z[3] XOR Z[11], the a output of E3 and the c output
of E1, so D3 = (e2 XOR e2') XOR eps. Digest word 6 is Z[6] XOR Z[14], the b
output of E1 and the d output of E3, so D6 = (b2 XOR b2') XOR (h2 XOR h2').
In E1, b2 = ROR(b1 XOR c2, 7), so b2 XOR b2' = ROR(beta XOR eps, 7). In E3,
h2 = ROR(h1 XOR e2, 8), and h1 XOR h1' = eta for every Y4 in the class
(Lemma T), so h2 XOR h2' = ROR(eta XOR e2 XOR e2', 8). Rotating D6 left by 8
gives ROL(D6, 8) = ROL(beta XOR eps, 1) XOR eta XOR (e2 XOR e2'). The XOR
with D3 cancels e2 XOR e2' and leaves n. QED.

A trial *passes the E1 test* when n = 0. The word n needs the first seven
assignments of E1 for both messages and nothing of E3: for a trial of 6.1
the eta of E3 is the constant of the class.
