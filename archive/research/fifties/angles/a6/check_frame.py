'A6: recompute one frame table in Python (gen_frames.lane, checked against ctr_lane) and compare with the GPU record.'
import struct, sys
import gen_frames as G
H = G.H
M64 = (1 << 64) - 1

def mix(z):
    z = (z + 0x9E3779B97F4A7C15) & M64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return z ^ (z >> 31)

frames, out, idx = sys.argv[1], sys.argv[2], int(sys.argv[3])
with open(frames, "rb") as f:
    f.seek(24 * idx); key = struct.unpack("<6I", f.read(24))
with open(out, "rb") as f:
    f.seek(44 * idx); rec = struct.unpack("<4Q3I", f.read(44))
print("probe", " ".join("%08x/%d" % G.lane(key, H.ctr_c1(t)) for t in range(7)))
sw1 = sw2 = sf1 = sf2 = nz = np_ = nj = 0
for j in range(H.CTR_MEMBERS):
    c1 = H.ctr_c1(j)
    w, ra = G.lane(key, c1)
    x = (c1 << 32) | w
    sw1 += mix(x); sw2 += mix(x ^ 0xA5A5A5A5C3C3C3C3)
    if ra:
        sf1 += mix(c1 + 0x1234567); sf2 += mix(c1 ^ 0x7777000088880000)
    nz += w == 0; np_ += ra; nj += (w == 0) and ra
mine = (sw1 & M64, sw2 & M64, sf1 & M64, sf2 & M64, nz, np_, nj)
print("python", mine)
print("gpu   ", rec)
print("MATCH" if mine == rec else "MISMATCH")
