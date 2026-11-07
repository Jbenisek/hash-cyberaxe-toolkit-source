// Independent implementation from the brief; no supplied counter is imported.
use std::collections::HashMap;
use std::time::Instant;

#[derive(Clone, Copy)]
struct Model {
    n: u32,
    y3: u32,
    y3p: u32,
    y11: u32,
    y11p: u32,
    delta: u32,
    mask: u32,
    value: u32,
    rotations: [u32; 4],
}
impl Model {
    fn modulus(self) -> u32 {
        1 << self.n
    }
    fn word(self, x: u32) -> u32 {
        x & (self.modulus() - 1)
    }
    fn add(self, x: u32, y: u32) -> u32 {
        self.word(x.wrapping_add(y))
    }
    fn sub(self, x: u32, y: u32) -> u32 {
        self.word(x.wrapping_sub(y))
    }
    fn ror(self, x: u32, r: u32) -> u32 {
        self.word((x >> r) | (x << (self.n - r)))
    }
    fn rol(self, x: u32, r: u32) -> u32 {
        self.ror(x, self.n - r)
    }
    fn pack(self, t: u32, s: u32, v: u32, z: u32) -> u32 {
        t | (s << self.n) | (v << (2 * self.n)) | (z << (3 * self.n))
    }
    fn beta_from_key(self, key: u32) -> u32 {
        let s = (key >> self.n) & (self.modulus() - 1);
        let z = (key >> (3 * self.n)) & (self.modulus() - 1);
        self.rol(z, self.rotations[3]) ^ s
    }
    fn class(self) -> Vec<u32> {
        (0..self.modulus())
            .filter(|&y4| self.add(self.y3, y4) & self.mask == self.value)
            .collect()
    }
    fn side1(self, d1: u32, b1: u32, a2: u32) -> u32 {
        let [_, r12, r8, r7] = self.rotations;
        let c1 = self.add(self.y11, d1);
        let c1p = self.add(self.y11p, d1);
        let b1p = b1 ^ self.ror(c1 ^ c1p, r12);
        let a2p = self.add(self.add(a2, self.sub(b1p, b1)), self.delta);
        let d2 = self.ror(d1 ^ a2, r8);
        let d2p = self.ror(d1 ^ a2p, r8);
        let c2 = self.add(c1, d2);
        let c2p = self.add(c1p, d2p);
        let b2 = self.ror(b1 ^ c2, r7);
        let b2p = self.ror(b1p ^ c2p, r7);
        self.pack(a2 ^ a2p, c2 ^ c2p, d2 ^ d2p, b2 ^ b2p)
    }
    fn side3(self, y4: u32, h1: u32, y9: u32, w8: u32) -> (u32, u32, u32) {
        let [r16, r12, r8, r7] = self.rotations;
        let e1 = self.add(self.y3, y4);
        let e1p = self.add(self.y3p, y4);
        let eta = self.ror(e1 ^ e1p, r16);
        let h1p = h1 ^ eta;
        let g1 = self.add(y9, h1);
        let g1p = self.add(y9, h1p);
        let f1 = self.ror(y4 ^ g1, r12);
        let f1p = self.ror(y4 ^ g1p, r12);
        let e2 = self.add(self.add(e1, f1), w8);
        let e2p = self.add(self.add(e1p, f1p), w8);
        let h2 = self.ror(h1 ^ e2, r8);
        let h2p = self.ror(h1p ^ e2p, r8);
        let g2 = self.add(g1, h2);
        let g2p = self.add(g1p, h2p);
        let f2 = self.ror(f1 ^ g2, r7);
        let f2p = self.ror(f1p ^ g2p, r7);
        (
            self.pack(g2 ^ g2p, e2 ^ e2p, f2 ^ f2p, h2 ^ h2p),
            f1 ^ f1p,
            eta,
        )
    }
}

// Alternative coordinates and equations, independently written from the
// differential identities, rather than calling side1/side3 above.
fn side1_changed(m: Model, c: u32, d: u32, b: u32) -> u32 {
    let cp = m.add(c, m.sub(m.y11p, m.y11));
    let beta = m.ror(c ^ cp, m.rotations[1]);
    let a = m.sub(c, m.y11) ^ m.rol(d, m.rotations[2]);
    let ap = m.add(m.add(a, m.sub(b ^ beta, b)), m.delta);
    let t = a ^ ap;
    let nu = m.ror(t, m.rotations[2]);
    let s = m.add(c, d) ^ m.add(cp, d ^ nu);
    m.pack(t, s, nu, m.ror(beta ^ s, m.rotations[3]))
}
fn side3_changed(m: Model, e: u32, g: u32, q: u32, h: u32) -> u32 {
    let y = m.sub(e, m.y3);
    let ep = m.add(e, m.sub(m.y3p, m.y3));
    let eta = m.ror(e ^ ep, m.rotations[0]);
    let gp = m.add(g, m.sub(h ^ eta, h));
    let f = m.ror(y ^ g, m.rotations[1]);
    let fp = m.ror(y ^ gp, m.rotations[1]);
    let qp = m.add(q, m.add(m.sub(ep, e), m.sub(fp, f)));
    let j = m.ror(h ^ q, m.rotations[2]);
    let jp = m.ror((h ^ eta) ^ qp, m.rotations[2]);
    let t = m.add(g, j) ^ m.add(gp, jp);
    m.pack(t, q ^ qp, m.ror((f ^ fp) ^ t, m.rotations[3]), j ^ jp)
}

fn run(label: &str, m: Model) -> u64 {
    let start = Instant::now();
    let n = m.modulus();
    let ys = m.class();
    let mut hist: HashMap<u32, u64> = HashMap::new();
    for d in 0..n {
        for b in 0..n {
            for a in 0..n {
                *hist.entry(m.side1(d, b, a)).or_insert(0) += 1;
            }
        }
    }
    let n1 = (n as u64).pow(3);
    assert_eq!(hist.values().sum::<u64>(), n1);
    for (&key, &count) in &hist {
        let t = key & (n - 1);
        let s = (key >> m.n) & (n - 1);
        let beta = m.beta_from_key(key);
        let computed = side1_carry_count(
            m.n,
            m.y11,
            m.sub(m.y11p, m.y11),
            m.delta,
            beta,
            t,
            s,
            m.rotations[1],
            m.rotations[2],
        );
        assert_eq!(
            computed, count as u128,
            "side-1 carry DP failed: key={key:08x}"
        );
    }
    println!(
        "{label}: side1_inputs={n1}, distinct_vectors={}, class_size={}",
        hist.len(),
        ys.len()
    );
    // Check a bijective reparameterization on the ENTIRE side-1 domain.
    let mut alt: HashMap<u32, u64> = HashMap::new();
    for c in 0..n {
        for d in 0..n {
            for b in 0..n {
                *alt.entry(side1_changed(m, c, d, b)).or_insert(0) += 1;
            }
        }
    }
    assert_eq!(hist, alt);
    drop(alt);
    let mut hits = 0u64;
    let mut nonzero = 0u64;
    let mut parts: HashMap<u32, u64> = HashMap::new();
    let mut matched_vectors: HashMap<u32, u64> = HashMap::new();
    for &y in &ys {
        for h in 0..n {
            for z in 0..n {
                for w in 0..n {
                    let (key, psi, eta) = m.side3(y, h, z, w);
                    if let Some(&weight) = hist.get(&key) {
                        *matched_vectors.entry(key).or_insert(0) += 1;
                        hits += weight;
                        nonzero += 1;
                        let t = key & (n - 1);
                        let s = (key >> m.n) & (n - 1);
                        let beta = m.beta_from_key(key);
                        // The brief's ROR(...,1) is the DIFFERENCE between its
                        // rotations 8 and 7; it must be adjusted for a scaled model.
                        let gap = m.rotations[2] - m.rotations[3];
                        assert_eq!(psi, t ^ m.ror(t, gap));
                        assert_eq!(s ^ m.ror(s, gap), beta ^ m.ror(eta, gap));
                        *parts.entry(beta).or_insert(0) += weight;
                    }
                }
            }
        }
    }
    let mut hits_alt = 0u64;
    let mut parts_alt: HashMap<u32, u64> = HashMap::new();
    for &y in &ys {
        let e = m.add(m.y3, y);
        for g in 0..n {
            for q in 0..n {
                for h in 0..n {
                    let key = side3_changed(m, e, g, q, h);
                    if let Some(&weight) = hist.get(&key) {
                        hits_alt += weight;
                        *parts_alt.entry(m.beta_from_key(key)).or_insert(0) += weight;
                    }
                }
            }
        }
    }
    assert_eq!(hits, hits_alt);
    assert_eq!(parts, parts_alt);
    let e = m.add(m.y3, ys[0]);
    let eta = m.ror(e ^ m.add(m.y3p, ys[0]), m.rotations[0]);
    for (&key, &actual) in &matched_vectors {
        let t = key & (n - 1);
        let s = (key >> m.n) & (n - 1);
        let computed = side3_carry_count(
            m.n,
            m.y3,
            m.sub(m.y3p, m.y3),
            m.mask,
            m.value,
            eta,
            t,
            s,
            m.rotations[1],
            m.rotations[2],
            m.rotations[3],
        );
        assert_eq!(
            computed, actual as u128,
            "side3 counter failed: key={key:08x}"
        );
    }
    let n3 = ys.len() as u64 * n1;
    let denom = n1 as u128 * n3 as u128;
    let rnum = (hits as u128) << (4 * m.n);
    let divisor = gcd(rnum, denom);
    let mut sorted: Vec<_> = parts.into_iter().collect();
    sorted.sort();
    println!("{label}: side3_inputs={n3}, matching_side3_inputs={nonzero}, matching_pairs={hits}, probability={hits}/{denom}, R={}/{}, parts={sorted:x?}, elapsed_s={:.3}",rnum/divisor,denom/divisor,start.elapsed().as_secs_f64());
    hits
}
fn gcd(mut a: u128, mut b: u128) -> u128 {
    while b != 0 {
        let r = a % b;
        a = b;
        b = r;
    }
    a
}

fn possible_addition(a: u32, b: u32, c: u32) -> bool {
    possible_addition_n(a, b, c, 32)
}
fn possible_addition_n(a: u32, b: u32, c: u32, n: u32) -> bool {
    let mask = if n == 32 { u32::MAX } else { (1u32 << n) - 1 };
    let equal = !(a ^ b) & !(a ^ c);
    (a ^ b ^ c) & 1 == 0 && ((a ^ b ^ c) ^ (b << 1)) & (equal << 1) & mask == 0
}
fn candidate_t(beta: u32, s: u32) -> (u64, Vec<u32>) {
    let u = beta.rotate_left(12);
    let eta = 0x830303cfu32;
    let rho = (eta ^ s).rotate_right(8);
    let mut tested = 0u64;
    let mut survivors = Vec::new();
    fn visit(
        i: u32,
        nu: u32,
        u: u32,
        s: u32,
        eta: u32,
        rho: u32,
        tested: &mut u64,
        out: &mut Vec<u32>,
    ) {
        if i == 31 {
            *tested += 1;
            let t = nu.rotate_left(8);
            let x2 = (t ^ t.rotate_right(1)).rotate_left(12);
            if possible_addition(eta, 0, x2) && possible_addition(x2, rho, t) {
                out.push(t);
            }
            return;
        }
        let a = (u >> i) & 1;
        let b = (nu >> i) & 1;
        let c = (s >> i) & 1;
        if a == b && a == c {
            let next = ((u >> (i + 1)) ^ (s >> (i + 1)) ^ b) & 1;
            visit(i + 1, nu | (next << (i + 1)), u, s, eta, rho, tested, out);
        } else {
            visit(i + 1, nu, u, s, eta, rho, tested, out);
            visit(i + 1, nu | (1 << (i + 1)), u, s, eta, rho, tested, out);
        }
    }
    visit(0, (u ^ s) & 1, u, s, eta, rho, &mut tested, &mut survivors);
    (tested, survivors)
}

struct Factor {
    vars: Vec<u32>,
    allowed: u32,
    ones: Vec<u32>,
}
fn factor(vars: &[u32], pred: impl Fn(u32) -> bool) -> Factor {
    let mut unique = vars.to_vec();
    unique.sort();
    unique.dedup();
    let mut allowed = 0u32;
    let mut ones = vec![0u32; unique.len()];
    for assignment in 0..(1u32 << unique.len()) {
        let mut word = 0u32;
        for (i, &v) in unique.iter().enumerate() {
            word |= ((assignment >> i) & 1) << v;
        }
        if pred(word) {
            allowed |= 1 << assignment;
            for i in 0..unique.len() {
                if assignment & (1 << i) != 0 {
                    ones[i] |= 1 << assignment;
                }
            }
        }
    }
    Factor {
        vars: unique,
        allowed,
        ones,
    }
}
fn candidate_t_csp(beta: u32, s: u32) -> Vec<u32> {
    let u = beta.rotate_left(12);
    let eta = 0x830303cfu32;
    let rho = (eta ^ s).rotate_right(8);
    let mut fs = Vec::new();
    // A necessary consequence of the side-1 signed-difference equation.
    // beta - 2*(b&beta) + delta is always divisible by this power of two.
    let delta = 0xfffffff8u32;
    let zeros = beta
        .wrapping_add(delta)
        .trailing_zeros()
        .min(beta.trailing_zeros().saturating_add(1))
        .min(32);
    let forced_zero = if zeros == 32 {
        u32::MAX
    } else {
        (1u32 << zeros) - 1
    };
    let low_value = beta.wrapping_add(delta) & 1;
    let mut a4_low = 0u32;
    for a in 0..32u32 {
        for b in 0..32u32 {
            let ap = a
                .wrapping_add((b ^ (beta & 31)).wrapping_sub(b))
                .wrapping_add(delta)
                & 31;
            a4_low |= 1 << (a ^ ap);
        }
    }
    fs.push(factor(&[0, 1, 2, 3, 4], |t| a4_low & (1 << (t & 31)) != 0));
    fs.push(factor(&[8], |t| ((t >> 8) ^ u ^ s) & 1 == 0));
    for i in 0..31 {
        let v = (i + 8) % 32;
        let w = (i + 9) % 32;
        fs.push(factor(&[v, w], |t| {
            let a = (u >> i) & 1;
            let b = (t >> v) & 1;
            let c = (s >> i) & 1;
            !(a == b && a == c) || (((u >> (i + 1)) ^ (t >> w) ^ (s >> (i + 1))) & 1) == b
        }));
    }
    let q = |t: u32, i: u32| ((t >> ((i + 20) % 32)) ^ (t >> ((i + 21) % 32))) & 1;
    fs.push(factor(&[20, 21], |t| q(t, 0) == eta & 1));
    fs.push(factor(&[0, 20, 21], |t| (q(t, 0) ^ rho ^ t) & 1 == 0));
    for i in 0..31 {
        let v = (i + 20) % 32;
        let w = (i + 21) % 32;
        let z = (i + 22) % 32;
        if (eta >> i) & 1 == 0 {
            fs.push(factor(&[v, w, z], |t| {
                q(t, i) != 0 || q(t, i + 1) == ((eta >> (i + 1)) & 1)
            }));
        }
        fs.push(factor(&[v, w, z, i, i + 1], |t| {
            let a = q(t, i);
            let b = (rho >> i) & 1;
            let c = (t >> i) & 1;
            !(a == b && a == c)
                || (q(t, i + 1) ^ ((rho >> (i + 1)) & 1) ^ ((t >> (i + 1)) & 1)) == b
        }));
    }
    let mut degree = [0u32; 32];
    for f in &fs {
        for &v in &f.vars {
            degree[v as usize] += 1;
        }
    }
    fn visit(
        fs: &[Factor],
        degree: &[u32; 32],
        mut known: u32,
        mut value: u32,
        out: &mut Vec<u32>,
    ) {
        loop {
            let before = known;
            for f in fs {
                let mut allowed = f.allowed;
                for (j, &v) in f.vars.iter().enumerate() {
                    if known & (1 << v) != 0 {
                        allowed &= if value & (1 << v) != 0 {
                            f.ones[j]
                        } else {
                            !f.ones[j]
                        };
                    }
                }
                if allowed == 0 {
                    return;
                }
                for (j, &v) in f.vars.iter().enumerate() {
                    if known & (1 << v) == 0 {
                        let has_one = allowed & f.ones[j] != 0;
                        let has_zero = allowed & !f.ones[j] != 0;
                        if !has_one || !has_zero {
                            known |= 1 << v;
                            if has_one {
                                value |= 1 << v;
                            }
                        }
                    }
                }
            }
            if known == before {
                break;
            }
        }
        if known == u32::MAX {
            out.push(value);
            return;
        }
        let v = (0..32)
            .filter(|&i| known & (1 << i) == 0)
            .max_by_key(|&i| degree[i as usize])
            .unwrap();
        visit(fs, degree, known | (1 << v), value, out);
        visit(fs, degree, known | (1 << v), value | (1 << v), out);
    }
    let mut answer = Vec::new();
    visit(&fs, &degree, forced_zero | 1, low_value, &mut answer);
    answer
}

fn all_beta_distribution() -> Vec<(u32, u64)> {
    fn visit(i: u32, carry: u32, u: u32, weight: u64, out: &mut Vec<(u32, u64)>) {
        let ki = (0x0a08818bu32 >> i) & 1;
        let u = u | ((ki ^ carry) << i);
        if i == 31 {
            out.push((u.rotate_right(12), weight * 2));
        } else if ki == carry {
            visit(i + 1, ki, u, weight * 2, out);
        } else {
            visit(i + 1, 0, u, weight, out);
            visit(i + 1, 1, u, weight, out);
        }
    }
    let mut out = Vec::new();
    visit(0, 0, 0, 1, &mut out);
    assert_eq!(out.iter().map(|x| x.1).sum::<u64>(), 1u64 << 32);
    out
}
fn s_words(beta: u32) -> [u32; 2] {
    let rhs = beta ^ 0x830303cfu32.rotate_right(1);
    assert_eq!(rhs.count_ones() % 2, 0);
    let mut s = 0u32;
    let mut bit = 0u32;
    for i in 0..31 {
        bit ^= (rhs >> i) & 1;
        s |= bit << (i + 1);
    }
    [s, !s]
}

fn side1_carry_count(
    n: u32,
    y11: u32,
    d11: u32,
    delta: u32,
    beta: u32,
    t: u32,
    s: u32,
    r12: u32,
    r8: u32,
) -> u128 {
    let mask = if n == 32 { u32::MAX } else { (1u32 << n) - 1 };
    let ror = |x: u32, r: u32| ((x >> r) | (x << (n - r))) & mask;
    let u = ror(beta, n - r12);
    let nu = ror(t, r8);
    let p = u ^ nu ^ s;
    if p & 1 != 0 || (d11 ^ u) & 1 != 0 {
        return 0;
    }
    let mut cmask = 0u32;
    let mut cvalue = 0u32;
    for i in 0..n - 1 {
        let ki = (d11 >> i) & 1;
        let ci = ((d11 ^ u) >> i) & 1;
        let next = ((d11 ^ u) >> (i + 1)) & 1;
        if ki == ci {
            if next != ki {
                return 0;
            }
        } else {
            cmask |= 1 << i;
            cvalue |= next << i;
        }
    }
    let difference = beta.wrapping_add(delta).wrapping_sub(t) & mask;
    if difference & 1 != 0 {
        return 0;
    }
    let k = difference >> 1;
    let boundary_mask = t & ((1 << r8) - 1);
    let mut answer = 0u128;
    for boundary in 0..(1u32 << r8) {
        if boundary & !boundary_mask != 0 {
            continue;
        }
        let states = 1usize << (r8 + 3);
        let mut dp = vec![0u128; states];
        let mut next = vec![0u128; states];
        dp[(boundary as usize) << 3] = 1;
        let mut active = vec![(boundary as usize) << 3];
        let mut next_active = Vec::new();
        for i in 0..n {
            for &state in &active {
                let weight = dp[state];
                let history = (state >> 3) as u32;
                let carry = ((state >> 2) & 1) as i32;
                let borrow = ((state >> 1) & 1) as i32;
                let sign_carry = -((state & 1) as i32);
                for cb in 0..=1i32 {
                    if cmask & (1 << i) != 0 && cb != ((cvalue >> i) & 1) as i32 {
                        continue;
                    }
                    let subtract = cb - ((y11 >> i) & 1) as i32 - borrow;
                    let next_borrow = if subtract < 0 { 1usize } else { 0 };
                    let a = (subtract & 1) ^ ((history & 1) as i32);
                    for db in 0..=1i32 {
                        if i >= n - r8
                            && boundary_mask & (1 << (i - (n - r8))) != 0
                            && db != ((boundary >> (i - (n - r8))) & 1) as i32
                        {
                            continue;
                        }
                        let sum = cb + db + carry;
                        let cp = carry ^ (((p >> i) & 1) as i32);
                        let sump =
                            (cb ^ (((u >> i) & 1) as i32)) + (db ^ (((nu >> i) & 1) as i32)) + cp;
                        if ((sum ^ sump) & 1) != ((s >> i) & 1) as i32 {
                            continue;
                        }
                        if i < n - 1 && ((sum >> 1) ^ (sump >> 1)) != ((p >> (i + 1)) & 1) as i32 {
                            continue;
                        }
                        let history_next = (history >> 1) | ((db as u32) << (r8 - 1));
                        // b's bit 31 (or n-1) is unconstrained by a signed
                        // difference after division by 2 modulo 2^(n-1).
                        if i == n - 1 {
                            answer += weight * 2;
                            continue;
                        }
                        let active = (beta >> i) & 1;
                        for bb in 0..=active as i32 {
                            let q = bb - a * (((t >> i) & 1) as i32) + sign_carry;
                            let adjusted = q - ((k >> i) & 1) as i32;
                            if adjusted & 1 != 0 {
                                continue;
                            }
                            let sc = adjusted / 2;
                            assert!(sc == 0 || sc == -1);
                            let index = ((history_next as usize) << 3)
                                | (((sum >> 1) as usize) << 2)
                                | (next_borrow << 1)
                                | ((-sc) as usize);
                            if next[index] == 0 {
                                next_active.push(index);
                            }
                            next[index] += weight * (if active == 0 { 2 } else { 1 });
                        }
                    }
                }
            }
            for &state in &active {
                dp[state] = 0;
            }
            std::mem::swap(&mut dp, &mut next);
            std::mem::swap(&mut active, &mut next_active);
            next_active.clear();
        }
    }
    answer
}

fn projection_count(
    n: u32,
    y3: u32,
    classmask: u32,
    classvalue: u32,
    ymask: u32,
    yvalue: u32,
) -> u128 {
    let mut dp = [1u128, 0];
    for i in 0..n {
        let mut next = [0u128; 2];
        for carry in 0..2usize {
            for y in 0..2u32 {
                if ymask & (1 << i) != 0 && y != ((yvalue >> i) & 1) {
                    continue;
                }
                let sum = y + ((y3 >> i) & 1) + carry as u32;
                if classmask & (1 << i) != 0 && (sum & 1) != ((classvalue >> i) & 1) {
                    continue;
                }
                next[(sum >> 1) as usize] += dp[carry];
            }
        }
        dp = next;
    }
    dp[0] + dp[1]
}
fn restricted_addition_count(
    n: u32,
    a: u32,
    b: u32,
    s: u32,
    xmask: u32,
    xvalue: u32,
    ymask: u32,
    yvalue: u32,
) -> u128 {
    let mut dp = [0u128; 4];
    dp[0] = 1;
    for i in 0..n {
        let mut next = [0u128; 4];
        for state in 0..4usize {
            if dp[state] == 0 {
                continue;
            }
            for x in 0..2u32 {
                for y in 0..2u32 {
                    if xmask & (1 << i) != 0 && x != ((xvalue >> i) & 1) {
                        continue;
                    }
                    if ymask & (1 << i) != 0 && y != ((yvalue >> i) & 1) {
                        continue;
                    }
                    let sum = x + y + (state & 1) as u32;
                    let sump =
                        (x ^ ((a >> i) & 1)) + (y ^ ((b >> i) & 1)) + ((state >> 1) & 1) as u32;
                    if ((sum ^ sump) & 1) != ((s >> i) & 1) {
                        continue;
                    }
                    next[((sum >> 1) | ((sump >> 1) << 1)) as usize] += dp[state];
                }
            }
        }
        dp = next;
    }
    dp.iter().sum()
}
fn side3_carry_count(
    n: u32,
    y3: u32,
    d3: u32,
    classmask: u32,
    classvalue: u32,
    eta: u32,
    t: u32,
    s: u32,
    r12: u32,
    r8: u32,
    r7: u32,
) -> u128 {
    let mask = if n == 32 { u32::MAX } else { (1u32 << n) - 1 };
    let low = mask >> 1;
    let ror = |x: u32, r: u32| ((x >> r) | (x << (n - r))) & mask;
    let psi = t ^ ror(t, r8 - r7);
    let x2 = ror(psi, n - r12);
    let rho = ror(eta ^ s, r8);
    if !possible_addition_n(eta, 0, x2, n) || !possible_addition_n(x2, rho, t, n) {
        return 0;
    }
    let kh = eta.wrapping_sub(x2) & mask;
    let ke = s.wrapping_sub(d3).wrapping_sub(psi) & mask;
    if (kh | ke) & 1 != 0 {
        return 0;
    }
    let hm = eta & low;
    let em = s & low;
    let zm = hm & em;
    let jmask = ror(zm, r8);
    let multiplier = 1u128 << (n - (hm | em).count_ones());
    let mut ys = Vec::new();
    let mut sub = x2;
    loop {
        let count = projection_count(n, y3, classmask, classvalue, x2, sub);
        if count > 0 {
            ys.push((sub, count));
        }
        if sub == 0 {
            break;
        }
        sub = (sub - 1) & x2;
    }
    let mut answer = 0u128;
    let mut gsub = x2;
    loop {
        let hvalue = ((kh >> 1).wrapping_add(gsub)) & low;
        if hvalue & !hm == 0 {
            for &(ysub, ycount) in &ys {
                let fmasked = ror(ysub ^ gsub, r12) & psi;
                let evalue = ((ke >> 1).wrapping_add(fmasked)) & low;
                if evalue & !em != 0 {
                    continue;
                }
                let jvalue = ror((hvalue ^ evalue) & zm, r8);
                let count = restricted_addition_count(n, x2, rho, t, x2, gsub, jmask, jvalue);
                answer += count * ycount * multiplier;
            }
        }
        if gsub == 0 {
            break;
        }
        gsub = (gsub - 1) & x2;
    }
    answer
}

fn check_side3_small() {
    let mut checked = 0u64;
    for d3 in [0, 1, 3, 7, 15] {
        for y3 in [0, 5] {
            let m = Model {
                n: 4,
                y3,
                y3p: (y3 + d3) & 15,
                y11: 0,
                y11p: 3,
                delta: 2,
                mask: 15,
                value: 0,
                rotations: [2, 3, 2, 1],
            };
            let y = m.sub(0, y3);
            let eta = m.ror(d3, 2);
            let mut counts = HashMap::new();
            for h in 0..16 {
                for z in 0..16 {
                    for w in 0..16 {
                        let (key, _, _) = m.side3(y, h, z, w);
                        *counts.entry(key).or_insert(0u64) += 1;
                    }
                }
            }
            for t in 0..16 {
                for s in 0..16 {
                    let key = m.pack(t, s, m.ror(t, 2), m.ror(eta ^ s, 2));
                    let actual = *counts.get(&key).unwrap_or(&0);
                    let counted = side3_carry_count(4, y3, d3, 15, 0, eta, t, s, 3, 2, 1);
                    assert_eq!(
                        counted, actual as u128,
                        "side3 DP failed d3={d3:x},y3={y3:x},t={t:x},s={s:x}"
                    );
                    checked += 1;
                }
            }
        }
    }
    println!("side3 carry counter: {checked} exact 4-bit (model,t,s) cases passed");
}

fn check_side1_small() {
    let mut checked = 0u64;
    for d11 in [0, 1, 3, 7, 15] {
        for y11 in [0, 5] {
            let m = Model {
                n: 4,
                y3: 0,
                y3p: 1,
                y11,
                y11p: (y11 + d11) & 15,
                delta: 2,
                mask: 15,
                value: 0,
                rotations: [2, 3, 2, 1],
            };
            let mut counts = HashMap::new();
            for d in 0..16 {
                for b in 0..16 {
                    for a in 0..16 {
                        *counts.entry(m.side1(d, b, a)).or_insert(0u64) += 1;
                    }
                }
            }
            for beta in 0..16 {
                for t in 0..16 {
                    for s in 0..16 {
                        let key = m.pack(t, s, m.ror(t, 2), m.ror(beta ^ s, 1));
                        let actual = *counts.get(&key).unwrap_or(&0);
                        let counted = side1_carry_count(4, y11, d11, 2, beta, t, s, 3, 2);
                        assert_eq!(
                            counted, actual as u128,
                            "side1 DP failed d11={d11:x},y11={y11:x},beta={beta:x},t={t:x},s={s:x}"
                        );
                        checked += 1;
                    }
                }
            }
        }
    }
    println!("side1 carry counter: {checked} exact 4-bit (model,beta,t,s) cases passed");
}

fn main() {
    check_side1_small();
    check_side3_small();
    let mut eta_counts: HashMap<u32, u64> = HashMap::new();
    let mut min_y = u32::MAX;
    let mut max_y = 0u32;
    let free: Vec<_> = (0..32).filter(|&i| (0x03cf8303u32 >> i) & 1 == 0).collect();
    for assignment in 0..(1u32 << free.len()) {
        let mut e = 0x030c0303u32;
        for (j, &i) in free.iter().enumerate() {
            e |= ((assignment >> j) & 1) << i;
        }
        let y = e.wrapping_sub(0x8127c181);
        assert_eq!(0x8127c181u32.wrapping_add(y) & 0x03cf8303, 0x030c0303);
        let ep = 0x7edf3e7eu32.wrapping_add(y);
        *eta_counts.entry((e ^ ep).rotate_right(16)).or_insert(0) += 1;
        min_y = min_y.min(y);
        max_y = max_y.max(y);
    }
    println!("32-bit exhaustive class check: free_bits={}, eta_counts={eta_counts:x?}, min_Y4={min_y:08x}, max_Y4={max_y:08x}",free.len());
    let args: Vec<_> = std::env::args().collect();
    if args.get(1).map(String::as_str) == Some("class-only") {
        return;
    }
    if args.get(1).map(String::as_str) == Some("all32") {
        use std::io::Write;
        let started = Instant::now();
        let mut output =
            std::io::BufWriter::new(std::fs::File::create("gpt_sol_parts_A.csv").unwrap());
        writeln!(output,"beta,s,c1_count,necessary_t,side1_positive_t,jointly_positive_t,matching_pairs,R_numerator,R_denominator").unwrap();
        let distribution = all_beta_distribution();
        let mut total = 0u128;
        let mut positive_betas = 0u64;
        let mut checked = 0u64;
        for &(beta, c1_count) in &distribution {
            if beta.count_ones() % 2 != 1 {
                continue;
            }
            let mut beta_total = 0u128;
            for s in s_words(beta) {
                let ts = candidate_t_csp(beta, s);
                if ts.is_empty() {
                    continue;
                }
                let mut weighted = 0u128;
                let mut lpositive = 0u64;
                let mut joint = 0u64;
                for &t in &ts {
                    let l = side1_carry_count(
                        32, 0x7af77f38, 0x0a08818b, 0xfffffff8, beta, t, s, 12, 8,
                    );
                    if l == 0 {
                        continue;
                    }
                    lpositive += 1;
                    let j = side3_carry_count(
                        32, 0x8127c181, 0xfdb77cfd, 0x03cf8303, 0x030c0303, 0x830303cf, t, s, 12,
                        8, 7,
                    );
                    if j > 0 {
                        joint += 1;
                        weighted += l.checked_mul(j).expect("product overflow");
                    }
                }
                if weighted > 0 {
                    let divisor = gcd(weighted, 1u128 << 83);
                    writeln!(
                        output,
                        "{beta:08x},{s:08x},{c1_count},{},{lpositive},{joint},{weighted},{},{}",
                        ts.len(),
                        weighted / divisor,
                        (1u128 << 83) / divisor
                    )
                    .unwrap();
                    output.flush().unwrap();
                    println!(
                        "NONZERO beta={beta:08x} s={s:08x} R={}/{}",
                        weighted / divisor,
                        (1u128 << 83) / divisor
                    );
                }
                beta_total += weighted;
            }
            if beta_total > 0 {
                positive_betas += 1;
            }
            total = total.checked_add(beta_total).expect("sum overflow");
            checked += 1;
            if checked % 1000 == 0 {
                println!(
                    "PROGRESS betas={checked}/66871 positive={positive_betas} elapsed_s={:.2}",
                    started.elapsed().as_secs_f64()
                );
            }
        }
        let divisor = gcd(total, 1u128 << 83);
        println!("FINAL feasible_betas={} parity_checked={checked} positive_betas={positive_betas} matching_pairs={total} R={}/{} elapsed_s={:.3}",distribution.len(),total/divisor,(1u128<<83)/divisor,started.elapsed().as_secs_f64());
        std::fs::write("gpt_sol_total_A.txt",format!("matching_pairs={total}\nR_numerator={}\nR_denominator={}\npositive_betas={positive_betas}\nparity_checked={checked}\nelapsed_seconds={:.3}\n",total/divisor,(1u128<<83)/divisor,started.elapsed().as_secs_f64())).unwrap();
        return;
    }
    if args.get(1).map(String::as_str) == Some("support32") {
        for (beta, s0) in [
            (0x18b0e098u32, 0x6e21be55u32),
            (0x18d0e098, 0x6e61be55),
            (0x18b1a098, 0x6e203e55),
            (0x18d1a098, 0x6e603e55),
        ] {
            for s in [s0, !s0] {
                let (tested, survivors) = candidate_t(beta, s);
                let mut csp = candidate_t_csp(beta, s);
                let mut reference: Vec<_> = survivors
                    .iter()
                    .copied()
                    .filter(|&t| {
                        side1_carry_count(32, 0x7af77f38, 0x0a08818b, 0xfffffff8, beta, t, s, 12, 8)
                            > 0
                    })
                    .collect();
                csp.retain(|&t| {
                    side1_carry_count(32, 0x7af77f38, 0x0a08818b, 0xfffffff8, beta, t, s, 12, 8) > 0
                });
                csp.sort();
                reference.sort();
                assert_eq!(csp, reference);
                let mut positive = 0u64;
                let mut lsum = 0u128;
                let mut weighted = 0u128;
                let mut jointly_positive = 0u64;
                for &t in &survivors {
                    let l = side1_carry_count(
                        32, 0x7af77f38, 0x0a08818b, 0xfffffff8, beta, t, s, 12, 8,
                    );
                    if l > 0 {
                        positive += 1;
                        lsum += l;
                        let j = side3_carry_count(
                            32, 0x8127c181, 0xfdb77cfd, 0x03cf8303, 0x030c0303, 0x830303cf, t, s,
                            12, 8, 7,
                        );
                        if j > 0 {
                            jointly_positive += 1;
                            weighted += l * j;
                        }
                    }
                }
                println!("32-bit necessary support: beta={beta:08x}, s={s:08x}, A5_feasible_t={tested}, A3_A5_A7_feasible_t={}, side1_positive_t={positive}, side1_inputs_in_these_paths={lsum}, sample={:08x?}",survivors.len(),&survivors[..survivors.len().min(8)]);
                println!("32-bit EXACT PART: beta={beta:08x} s={s:08x} jointly_positive_t={jointly_positive} matching_pairs={weighted}, R={}/2^83",weighted);
                if beta == 0x18b0e098 && s == 0x6e21be55 {
                    assert!(survivors.contains(&0x185020a0));
                }
            }
        }
        return;
    }
    if args.get(1).map(String::as_str) == Some("search-scaled") {
        for d3 in [1, 3, 7, 15, 31, 63, 127, 255] {
            for d11 in [1, 3, 7, 15] {
                for delta in [0, 2, 254, 8, 248] {
                    let label = format!("8-bit search D3={d3:02x} D11={d11:02x} delta={delta:02x}");
                    let hits = run(
                        &label,
                        Model {
                            n: 8,
                            y3: 0,
                            y3p: d3,
                            y11: 0,
                            y11p: d11,
                            delta,
                            mask: 255,
                            value: 0,
                            rotations: [4, 3, 2, 1],
                        },
                    );
                    if hits > 0 {
                        return;
                    }
                }
            }
        }
        return;
    }
    run(
        "4-bit identical-executions control",
        Model {
            n: 4,
            y3: 9,
            y3p: 9,
            y11: 7,
            y11p: 7,
            delta: 0,
            mask: 3,
            value: 1,
            rotations: [3, 2, 2, 1],
        },
    );
    run(
        "6-bit nontrivial",
        Model {
            n: 6,
            y3: 0x21,
            y3p: 0x1e,
            y11: 0x18,
            y11p: 0x23,
            delta: 0x38,
            mask: 0x0f,
            value: 3,
            rotations: [4, 3, 2, 1],
        },
    );
    run(
        "8-bit nontrivial",
        Model {
            n: 8,
            y3: 0x81,
            y3p: 0x7e,
            y11: 0x38,
            y11p: 0xc3,
            delta: 0xf8,
            mask: 0xcf,
            value: 3,
            rotations: [4, 3, 2, 1],
        },
    );
    run(
        "8-bit positive singleton",
        Model {
            n: 8,
            y3: 0,
            y3p: 0x0f,
            y11: 0,
            y11p: 3,
            delta: 0,
            mask: 255,
            value: 0,
            rotations: [4, 3, 2, 1],
        },
    );
    run(
        "8-bit four-member class delta=2",
        Model {
            n: 8,
            y3: 0,
            y3p: 0x0f,
            y11: 0,
            y11p: 3,
            delta: 2,
            mask: 0xcf,
            value: 0,
            rotations: [4, 3, 2, 1],
        },
    );
}
