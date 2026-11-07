import random
def toy_params(q, seed):
    rnd = random.Random(seed)
    while True:
        x = [rnd.randrange(q) for _ in range(3)]; y = [rnd.randrange(q) for _ in range(3)]
        if len(set(x)) == 3 and len(set(y)) == 3 and all((x[i]+y[j]) % q for i in range(3) for j in range(3)):
            break
    Mx = [[pow(x[i]+y[j], -1, q) for j in range(3)] for i in range(3)]
    RCx = [[rnd.randrange(q) for _ in range(3)] for _ in range(64)]
    return Mx, RCx, (1 << 65) % q
