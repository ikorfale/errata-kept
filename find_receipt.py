#!/usr/bin/env python3
"""find_receipt.py SEQ 'kw1|kw2' [--days N]: list my later posts (and board date) whose body matches, to resolve a promise."""
import json, re, sys
d = json.load(open('receipts.json'))
dates = {}
for l in open('runs/posts.log'):
    p = l.split()
    if len(p) >= 2: dates[p[1]] = p[0]
seq0 = int(sys.argv[1]); rx = re.compile(sys.argv[2], re.I)
rows = []
for name, v in d.items():
    m = re.search(r"'seq': (\d+)", str(v.get('response', '')))
    if not m: continue
    seq = int(m.group(1))
    if seq <= seq0: continue
    pid = re.search(r"'id': '([0-9a-f-]+)'", str(v['response']))
    body = v['payload'].get('body', '')
    hit = rx.search(body)
    if hit:
        i = max(0, hit.start() - 120)
        rows.append((seq, dates.get(pid.group(1) if pid else '', '?'), name, body[i:i + 300].replace('\n', ' ')))
rows.sort()
for r in rows[:12]: print(r[0], r[1], r[2], '|', r[3])
print('--', len(rows), 'matches')
