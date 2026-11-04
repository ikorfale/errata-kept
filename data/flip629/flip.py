#!/usr/bin/env python3
"""#629 dated-flag stability on looktwin-feedback blind30: rows.py over three frozen reads (2,3,4),
plus a post-level check across all four reads (read1 = 03.11, same prompt and model, older reader code)."""
import json, collections, sys
R = [json.loads(l) for l in open(sys.argv[1])]
print('candidates', len(R), dict(collections.Counter(r['status'] for r in R)))
def flags(r): return [x.get('dated') if x else None for x in r['reads']]
anyd = [r for r in R if any(f is True for f in flags(r))]
alld = [r for r in anyd if all(f is True for f in flags(r))]
print('candidates dated in >=1 read', len(anyd), '| in all 3', len(alld), '| flipped', len(anyd) - len(alld))
for r in anyd:
    print(' ', r['seq'], r['status'], flags(r), '|', r['quote'][:90])
posts = collections.defaultdict(list)
for i in (1, 2, 3, 4):
    for l in open(f'data/flip629/read{i}.jsonl'):
        d = json.loads(l); posts[d['seq']].append(any(p.get('dated') for p in (d.get('promises') or [])))
flip = {s: v for s, v in posts.items() if len(set(v)) > 1}
print('posts', len(posts), '| with a dated promise in all 4 reads', sum(all(v) for v in posts.values()),
      '| in none', sum(not any(v) for v in posts.values()), '| post-level flip', len(flip), flip)
