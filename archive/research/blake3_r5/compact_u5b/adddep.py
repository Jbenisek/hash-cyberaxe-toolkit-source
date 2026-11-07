import json, shutil
f = 'dependencies.json'
shutil.copy(f, f + '.bak_pre616')
d = json.load(open(f))
if not any(x['submissionId'].startswith('616120b2') for x in d):
    d.append({"submissionId": "616120b2-f777-44a8-bbd2-44f20c56224a",
              "rationale": "TheTradoor's entry for blake3 round 7 (125.18448). Credited for the convention this entry adopts: gate instructions priced and encoded at 5 bytes each, which lets the straight-line step fit in 2^20. Re-implemented here from the text of that entry (no file of it was used or run).",
              "evidence": "proof.md Section 3 (instruction encoding) and restrictions."})
json.dump(d, open(f, 'w'), indent=2)
print(len(d))
