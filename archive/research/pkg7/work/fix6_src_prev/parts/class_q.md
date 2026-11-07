*The class.* The first message word of E3 is w15 = 0, so the first assignment
of E3 is e1 = Y3 + Y4 for message A and e1' = Y3' + Y4 for message B, with Y3 =
8127c181 and Y3' = 7edf3e7e from Fact P. Put DY3 = Y3' - Y3 = fdb77cfd. The
second assignment is h1 = ROR(Y14 XOR e1, 16), so the XOR difference between A
and B of E3's first-half d value is

    eta = h1 XOR h1' = ROR((Y3 + Y4) XOR (Y3 + Y4 + DY3), 16),

a function of Y4 alone. Fix eta = 830303cf. The *class* is the set of all words
Y4 that give this eta.

**Lemma Q.** The class is the set of all Y4 with

    ((Y3 + Y4) AND 03cf8303) = 030c0303.

It has 524,288 members: the 19 bits of e1 = Y3 + Y4 at the positions where
03cf8303 has a zero are free, bit 31 among them, and Y4 = e1 - Y3.

Proof. Put x = ROL(eta,16) = 03cf8303 and m = x AND 7fffffff = 03cf8303. Here x
has no bit 31, so m = x. Y4 is in the class exactly when e1 XOR (e1 + DY3) = x,
that is when (e1 XOR x) - e1 = DY3 modulo 2^32. For words e and x, (e XOR x) -
e is, modulo 2^32, the sum over the bits i of x of 2^i where bit i of e is 0
and of -2^i where it is 1, which is 2 ((NOT e) AND x) - x; for i = 31 the two
signs give the same word. So the condition is 2 ((NOT e1) AND x) = DY3 + x
modulo 2^32. Here DY3 + x = 01870000 modulo 2^32, which is even. Doubling
modulo 2^32 discards bit 31 of (NOT e1) AND x, so the condition does not
involve bit 31 of e1, and on the other bits it is ((NOT e1) AND m) = 01870000
>> 1 = 00c38000. All bits of 00c38000 lie in m, so this fixes the 13 bits of e1
on m to (e1 AND m) = (NOT 00c38000) AND m = 030c0303 and leaves the other 19
bits free. QED.
