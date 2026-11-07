import difflib
t = open("proof_t8.md", encoding="utf-8").read()
i = t.index("## 4. Success probability"); j = t.index("## 5.")
old = t[i:j]
new = open("../../blake3_r4/b4f/sec4_t.md", encoding="utf-8").read()
oi = old.index("Lemma 2 (for"); ni = new.index("Lemma 2 (for")
for a, b in zip(old[:oi].split("\n"), new[:ni].split("\n")):
    if a != b:
        print("OLD:", a[:2500]); print("NEW:", b[:2500]); print()
