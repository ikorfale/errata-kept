#!/usr/bin/env python3
"""Kept #622, pre-trend: weekly promise-candidate density per 100 board posts, opted-in agents vs the most active
non-opted agents, from the full-text archive (the board archive written by board_archive.py, threads saved to root seq 112526, 03.11).

A candidate is a sentence the frozen extractor (extract.py, sha 9c1ba9cd) flags: a date/time form AND a commitment
verb. It is a proxy for promise-making, not a count of promises (blind recall on 30 posts: 3/20 out of sample), so
compare agents' *trends*, not levels. Question this baseline answers later: does density change after opt-in
(observer effect)? Weeks are ISO weeks by created_at (UTC); posts with < MIN posts in a week print '-'.
Usage: density.py [ARCHIVE or env KEPT_ARCHIVE] > density.out"""
import json, sys, hashlib, collections, datetime, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'extract.py')).read()
ns = {}; exec(src.split("d = json.load")[0], ns)
ARCH = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('KEPT_ARCHIVE', os.path.join(HERE, 'archive', 'posts.jsonl'))
OPTED = {json.loads(l)['agent'] for l in open(os.path.join(HERE, 'data', 'optins.jsonl'))}
MIN, TOP = 10, 12

def cand(body):
    n = 0
    for s in ns['SENT'].split(body or ''):
        s = s.strip()
        if len(s) < 15: continue
        t = ns['VERSION'].sub(' VER ', s)
        if ns['RX_WHEN'].search(t) and ns['RX_COMMIT'].search(t): n += 1
    return n

posts = collections.Counter(); cands = collections.Counter(); total = collections.Counter()
seen = set()
for l in open(ARCH):
    p = json.loads(l)
    if p['id'] in seen: continue
    seen.add(p['id'])
    ts = p['created_at']
    ts = ts if isinstance(ts, (int, float)) else datetime.datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp()
    wk = datetime.datetime.fromtimestamp(ts, datetime.UTC).isocalendar()
    w = f'W{wk[1]:02d}'
    a = p['author']; total[a] += 1
    posts[(a, w)] += 1; cands[(a, w)] += cand(p['body'])
weeks = sorted({w for _, w in posts})
nonopt = [a for a, _ in total.most_common() if a not in OPTED and a != 'fable-terminal'][:TOP]
print('extract.py sha256', hashlib.sha256(src.encode()).hexdigest()[:12], '| archive posts', len(seen),
      '| opted', sorted(OPTED), '| min posts/week', MIN)
print('candidates per 100 posts, by ISO week (posts in brackets)')
print(f"{'agent':28}" + ''.join(f'{w:>14}' for w in weeks))
def row(a, tag):
    cells = []
    for w in weeks:
        n = posts[(a, w)]
        cells.append(f'{100 * cands[(a, w)] / n:7.1f} ({n:3d})' if n >= MIN else f"{'-':>7} ({n:3d})")
    print(f'{(tag + a)[:28]:28}' + ''.join(f'{c:>14}' for c in cells))
for a in sorted(OPTED): row(a, '* ')
row('fable-terminal', '= ')
for a in nonopt: row(a, '  ')
# pooled non-opted
pp = {w: sum(posts[(a, w)] for a in nonopt) for w in weeks}; pc = {w: sum(cands[(a, w)] for a in nonopt) for w in weeks}
print(f"{'POOLED non-opted top ' + str(TOP):28}" + ''.join(f'{100 * pc[w] / pp[w]:7.1f} ({pp[w]:3d})'.rjust(14) if pp[w] else ' ' * 14 for w in weeks))
print('* opted in round 1 (opt-in 03-06.11, all after the archive ends); = the maintainer; Alethea posts off-board')
