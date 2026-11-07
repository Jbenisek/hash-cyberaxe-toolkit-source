**How r is counted (participant computation, not organizer-verified).** Write
tau, eps for the XOR differences between A and B of E1's a and c outputs and
beta for that of its first-half b. E1's a1 and d1 are the same for A and B, so its d and b
output differences are ROR(tau, 8) and ROR(beta XOR eps, 7), and E3's d and b
output differences are ROR(eta XOR eps', 8) and ROR(psi XOR tau', 7), where
eta, psi are the XOR differences of E3's first-half d and b and tau', eps'
those of its c and a outputs. So R = 0 holds exactly when tau' = tau, eps' =
eps, psi = tau XOR ROR(tau, 1) and eta = eps XOR ROL(beta XOR eps, 1). For Y4
in the class the left side of the last equation is the constant 830303cf.

1. *The betas.* beta is a function of d1 alone: with c1 = Y11 + d1 and DY11 =
   Y11' - Y11 = 0a08818b, beta = ROR(c1 XOR (c1 + DY11), 12). As in Lemma Q,
   the d1 with a given beta are those for which c1 has prescribed bits on the
   mask ROL(beta,12) AND 7fffffff; they are a share 2^-k of all d1, where k is
   the number of bits of the mask. Only finitely many words occur as beta, and
   they can be listed by increasing k.
2. *The outcomes of one beta.* An outcome is a pair (tau, eps). In E1, a2' =
   a2 + delta + (b1' - b1), and b1' - b1 = (b1 XOR beta) - b1 is a signed sum
   over the bits of beta. So tau = a2 XOR a2' is one of the XOR differences
   that an addition can show when its additive difference is delta plus such a
   signed sum. These words are enumerated by a depth-first search over the
   bits of tau, lowest first, with a carry automaton that keeps, for every
   carry, the number of sign choices on the lower bits of beta that lead to
   it; a branch ends when no sign choice is left. No bound is put on the
   weight of tau. For eps, the last equation above says eps XOR ROR(eps, 1) =
   beta XOR ROR(eta, 1). A word has the form eps XOR ROR(eps, 1) exactly when
   its weight is even, and then for exactly two words eps, each the complement
   of the other. So a beta for which beta XOR ROR(eta, 1) has odd weight
   contributes nothing, and every other beta has two candidates for eps.
