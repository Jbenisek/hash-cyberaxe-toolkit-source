"""Replay of the recorded full-scale collision pairs of rounds r = 3, 4, 5 (and r = 6 once recorded).

What it does: for each recorded pair (nk1, rho1), (nk2, rho2) it rebuilds the 64-byte organizer messages
(nk, rho as 32-byte little-endian each), recomputes the Orchard P128Pow5T3 digest at the pair's own round count
with an independent copy of the organizer permutation (constants of the pinned deployed table, only the rows
this program needs: original rounds 0..9 and 60..63), and checks: both elements of each message are canonical,
the two messages are distinct, the two digests are equal, and the equal digest is the recorded one.

What it does NOT do: the organizer's selected target is one fixed round count (r >= 7), so the organizer's own
digest callback cannot confirm these r <= 6 pairs. Every trial therefore returns two nulls (no pair for the
selected target); the replay verdict is reported only in the untrusted numeric observations. It says nothing
about the cost, the success probability or any round count above 6.
"""
import json
import sys

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
CAP = 1 << 65
RC = {
    0: (0x360d7470611e473d353f628f76d110f34e71162f31003b7057538c2596426303, 0x2bab94d7ae222d135dc3c6c5febfaa314908ac2f12ebe06fbdb74213bf63188b, 0x150c93fef652fb1c2bf03e1a29aa871fef77e7d736766c5d0939d92753cc5dc8),
    1: (0x3270661e68928b3a955d55db56dc57c103cc0a60141e894e14259dce537782b2, 0x073f116f04122e25a0b7afe4e2057299b407c370f2b5a1ccce9fb9ffc345afb3, 0x2a32ec5c4ee5b1837affd09c1f53f5fd55c9cd2061ae93ca8ebad76fc71554d8),
    2: (0x270326ee039df19e651e2cfc740628ca634d24fc6e2559f22d8ccbe292efeead, 0x27c6642ac633bc66dc100fe7fcfa54918af895bce012f182a068fc37c182e274, 0x1bdfd8b01401c70ad27f57396989129d710e1fb6ab976a459ca18682e26d7ff9),
    3: (0x162a14c62f9a89b814b9d6a9c84dd678f4f6fb3f9054d373c832d824261a35ea, 0x2d193e0f76de586b2af6f79e3127feeaac0a1fc71e2cf0c0f79824667b5b6bec, 0x044ca3cc4a85d73b81696ef1104e674f4feff82984990ff85d0bf58dc8a4aa94),
    4: (0x1cbaf2b371dac6a81d0453416d3e235cb8d9e2d4f314f46f6198785f0cd6b9af, 0x1d5b2777692c205b0e6c49d061b6b5f4293c4ab038fdbbdc343e07610f3fede5, 0x2e9bdbba3dd34bffaa30535bdd749a7e06a9adb0c1e6f962f60e971b8d73b04f),
    5: (0x2de11886b18011ca8bd5bae36969299fde40fbe26d047b05035a13661f22418b, 0x2e07de1780b8a70d0d5b4a3f1841dcd82ab9395c449be947bc998884ba96a721, 0x0f69f1854d20ca0cbbdb63dbd52dad16250440a99d6b8af3825e4c2bb74925ca),
    6: (0x2eb1b25417fe17670d135dc639fb09a46ce5113507f96de9816c059422dc705e, 0x115cd0a0643cfb988c24cb44c3fab48aff36c661d26cc42db8b1bdf4953bd82c, 0x26ca293f7b2c462d066d7378b999868bbb57ddf14e0f958ade801612311d04cd),
    7: (0x17bf1b93c4c7e01a2a830aa162412cd90f160bf9f71e967ff5209d14b24820ca, 0x35b41a7ac4f3c571a24f8456369c85dfe03c0354bd8cfd3805c86f2e7dc293c5, 0x3b1480080523c439435927994849bea964e14d3beb2dddde72ac156af435d09e),
    8: (0x2cc6810031dc1b0d4950856dc907d57508e286442a2d3eb2271618d874b14c6d, 0x25bdbbeda1bde8c1059618e2afd2ef999e517aa93b78341d91f318c09f0cb566, 0x392a4a8758e06ee8b95f33c25dde8ac02a5ed0a27b61926cc6313487073f7f7b),
    9: (0x272a55878a08442b9aa6111f4de009485e6a6fd15db89365e7bbcef02eb5866c, 0x2d5b308b0cf02cdfefa13c4e60e26239a6ebba011694dd129b925b3c5b21e0e2, 0x16549fc6af2f3b72dd5d293d72e2e5f244dff42f18b46c56ef38c57c311673ac),
    60: (0x1f697cac4d07feb710f1cc6df8b4bcd760414abe362d01c977c5b024848371ae, 0x267a750fe5d7cfbc26e6c851fbd572a63145c478063109d6786add244aa0ef29, 0x0c91feab4a43193a678c9996d9a472c8af285fa82ce4fae5180e2b4d3e756f65),
    61: (0x1745569a0a3e30142186c3038ea05e697e3b83af4a4ba3ba79c47c573ac410f7, 0x29863d546e7e7c0deca5120778a56711fdff66c6f3b5ffe11e0388522696191f, 0x1148d6ab2bd00192bf06bae49ef853f6a79a03df833994c62f225e6366bfe390),
    62: (0x02e0e121b0f3dfefe18b1499060da366f745f45d350d41d4f4f6331a8b265d15, 0x0d0aa46e76a6a278b89ef73a40a2b274690401736d44a653078ae6aa151054b7, 0x13943675b04aa986eee545f3fa6d3d08392dde710f1f06db9a4d532c7b6e0958),
    63: (0x2901ec61942d34aad97a11d63088f5d9c9f2b3257530dafe961fc818dcbb66b5, 0x20204a2105d22e7ef431d54434a3e0cf22ffa2a2af9fa3e3fdf544b963d1fdc7, 0x3a8a628295121d5c5c1e3e9e27a571c3a004abe8e01528c41211b9e2190d6852),
}
MDS = (
    (0x0ab5e5b874a68de7b3d59fbdc8c9ead497d7a0ab23850b56323f2486d7e11b63, 0x31916628e58a5abb293f0f0d886c7954240d4a7cbf7357368eca5596e996ab5e, 0x07c045d5f5e9e5a6d803952bbb364fdfa0a3b71a5fb1573519d1cf25d8e8345d),
    (0x233162630ebf9ed7f8e24f66822c2d9f3a0a464048bd770ad049cdc8d085167c, 0x25cae2599892a8b0b36664548d60957d78f8365c85bbab07402270113e047a2e, 0x22f5b5e1e6081c9774938717989a19579aad3d8262efd83ff84d806f685f747a),
    (0x2e29dd59c64b1037f333aa91c383346421680eabc56bc15dfee7a9944f84dbe4, 0x1d1aab4ec1cd678892d15e7dceef1665cbeaf48b3a0624c3c771effa43263664, 0x3bf763086a18936451e0cbead65516b975872c39b59a31f615639415f6e85ef1),
)
# (round count r, centre, nk1, rho1, nk2, rho2, digest)
PAIRS = (
    (3, 1,
     0x0499f5c4354bafa11ca451e656d380d078444ed6561d6355487453741e1a6815, 0x21625d728b86cf0865d7ad7cd99a0c20464939e5253940d95b3a639d7a909af7,
     0x1009050c8c1414cf5975db612457a2e49b06db64fce28c7dd5ad52ed8fc2c567, 0x31611cd777dc6c418e048d96a497f46fa51523b47dbadcd97d0ad171160fcdb8,
     0x325165c946fe20c28af82e940ec89fca03e6fb74afa1a3fa28a54e552a1f12ec),
    (4, 2,
     0x25c10b7d8d36b332b4a4ddb92f1f1a3ffa40259b7b77b0ba458ad0be367ab979, 0x2e568f6667ceaedd4195dbd24a55c365075306af4a5d0931b1707ba0bf7616ea,
     0x2acbf624301319ca0830c5fda78ae08e00d75798f24adf1320401f1a3bc4c580, 0x162fa98e63ff13622228cd9e3b4d9039124a918f1f11d12718a2a782ed69fb17,
     0x3deca6a0b865e914ebcc74484b3cedb56b9f6293338881693e00cbee0c161fa1),
    (5, 1,
     0x35aefd661e07cec063071e6f92f2bbcfd6bbc794bc99be91c008fed0a2a5ebb5, 0x3dd4caae629bb08efa85dd470f72f2fc183cf026de9cd1aa356e147f058a0090,
     0x242b99e697375e309d54e5db54c215cb6526b420e7ff760eec690a5fb189c764, 0x2e9a4cf95fce4bbf8ebe8eb72485446ceca86268a6c2305f70d4460179334e37,
     0x2425532a0c6af3e7c0864ce59d3b1ddbd62ea79ba594c3305f8fbacf7c184249),
    # r = 6 pair: appended here when the counted run has finished (see the README, item R6_PAIR)
)


def digest(nk, rho, r):
    s = [nk, rho, CAP]
    for i in (*range(4), *range(4, 4 + r), *range(60, 64)):
        s = [(x + c) % P for x, c in zip(s, RC[i])]
        for k in (range(3) if i < 4 or i >= 60 else range(1)):
            s[k] = pow(s[k], 5, P)
        s = [sum(m * x for m, x in zip(row, s)) % P for row in MDS]
    return s[0].to_bytes(32, "little")


def replay():
    checked = ok = 0
    for r, centre, nk1, rho1, nk2, rho2, dg in PAIRS:
        ma = nk1.to_bytes(32, "little") + rho1.to_bytes(32, "little")
        mb = nk2.to_bytes(32, "little") + rho2.to_bytes(32, "little")
        canonical = all(0 <= x < P for x in (nk1, rho1, nk2, rho2))
        da, db = digest(nk1, rho1, r), digest(nk2, rho2, r)
        good = canonical and ma != mb and da == db and int.from_bytes(da, "little") == dg
        checked += 1
        ok += good
    return checked, ok


def main():
    request = json.loads(sys.stdin.read())
    checked, ok = replay()
    obs = {"replay_pairs_checked": checked, "replay_pairs_ok": ok, "replay_all_ok": int(checked == ok and checked > 0)}
    trials = [{"trial": t["trial"], "message_a_hex": None, "message_b_hex": None, "observations": obs}
              for t in request["trials"]]
    sys.stdout.write(json.dumps({"schema_version": 1, "trials": trials}))


main()
