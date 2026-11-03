#!/usr/bin/env python3
"""Kept: run the frozen rules (exec'd verbatim from extract.py) on one agent's archived board posts.
Usage: per_agent.py AUTHOR [OUT]. Input archive/posts.jsonl. Output one line per candidate sentence."""
import json, sys, hashlib
src = open('extract.py').read(); print('rules sha256', hashlib.sha256(src.encode()).hexdigest()[:12])
ns = {}; exec(src.split("d = json.load")[0], ns)
who = sys.argv[1]; out = sys.argv[2] if len(sys.argv) > 2 else f'data_{who}_candidates.jsonl'
posts = [json.loads(l) for l in open('archive/posts.jsonl')]; posts = [p for p in posts if p['author'] == who]
rows = []
for p in posts:
    for s in ns['SENT'].split(p['body'] or ''):
        s = s.strip()
        if len(s) < 15: continue
        t = ns['VERSION'].sub(' VER ', s)
        if ns['RX_WHEN'].search(t) and ns['RX_COMMIT'].search(t):
            rows.append({'seq': p['seq'], 'root_seq': p['root_seq'], 'post': p['id'], 'created': p['created_at'], 'sentence': s[:600]})
with open(out, 'w') as f:
    for r in rows: f.write(json.dumps(r, ensure_ascii=False) + '\n')
print(who, 'posts', len(posts), 'seq', min(p['seq'] for p in posts), '-', max(p['seq'] for p in posts), 'candidates', len(rows), 'in posts', len({r['seq'] for r in rows}))
