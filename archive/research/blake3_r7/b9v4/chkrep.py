import json, re
d = json.load(open('organizer_report_b9v3.json'))
E = d['execution']
print(d['status'], E.get('status'), [k for k in E.keys()])
s = json.dumps(E)
print(set(re.findall(r'"(replay[a-z_]*|identical[a-z_]*|replayed[a-z_]*)": ([^,}]*)', s)))
for e in E['experiments']:
    print(e['id'], len(e['checked_trials']), sorted(k for k in e.keys() if k != 'checked_trials'))
