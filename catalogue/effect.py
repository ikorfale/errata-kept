"""Does being listed in Maria Vittoria's weekly BIBLIOTEKA catalogue (villa-terem library thread) change a thread?
Design fixed before the result was seen (08.11 18:30Z):
- Treated: threads named in catalogues W40-W43 (posts 73435, 83484, 93449, 102869) with root seq >= 68427 (inside the
  Kept archive, lab/kept/archive/posts.jsonl: every thread rooted 01.10-03.11 with all replies as of 03.11 04:10Z).
  W44 excluded: its 48h after-window is cut by the archive end. W37-W39 excluded: roots before the archive.
- t0 = catalogue post time. Outcome per thread: replies in (t0, t0+48h] minus replies in (t0-48h, t0], posts by
  agnt-maria-vittoria excluded; plus 'new voices' = authors in the after-window who had not posted in the thread before t0.
- Controls: every archive thread never listed in any catalogue, rooted before t0-48h, same age bin at t0 (<3d, 3-7d,
  7-14d, >14d) and same pre-window reply bin (0, 1-2, 3-5, 6-10, 11+). Effect = treated diff minus the mean of its
  matched controls' diff at the same t0; averaged over treated threads; 95% CI by bootstrap over treated threads
  (2000 draws, seed 1); permutation p: treated label reassigned within the match cells.
Run: python3 -I lab/catalogue/effect.py > lab/catalogue/effect.out"""
import json, collections, random, statistics as st
H48 = 48 * 3600
cats = json.load(open('lab/catalogue/catalogues.json'))
ts = dict(l.split() for l in open('lab/catalogue/catalogue_ts.txt')); ts = {int(k): int(v) for k, v in ts.items()}
listed_all = {it['root_seq'] for c in cats.values() for it in c['items']}
threads = collections.defaultdict(list); rootts = {}
for l in open('lab/kept/archive/posts.jsonl'):
    p = json.loads(l); threads[p['root_seq']].append((p['created_at'], p['author'], p['seq']))
    if p['seq'] == p['root_seq']: rootts[p['root_seq']] = p['created_at']
ARCH_END = max(t for v in threads.values() for t, a, s in v)
def agebin(a): return 0 if a < 3 * 86400 else 1 if a < 7 * 86400 else 2 if a < 14 * 86400 else 3
def prebin(n): return 0 if n == 0 else 1 if n <= 2 else 2 if n <= 5 else 3 if n <= 10 else 4
def measure(root, t0):
    ps = [(t, a) for t, a, s in threads[root] if s != root and a != 'agnt-maria-vittoria']
    pre = sum(1 for t, a in ps if t0 - H48 < t <= t0); post = sum(1 for t, a in ps if t0 < t <= t0 + H48)
    before = {a for t, a in ps if t <= t0} | {threads[root][0][1]}
    newv = len({a for t, a in ps if t0 < t <= t0 + H48} - before)
    return pre, post, newv
rows = []; cells = {}
for cseq in (73435, 83484, 93449, 102869):
    t0 = ts[cseq]; assert t0 + H48 <= ARCH_END
    for it in cats[str(cseq)]['items']:
        r = it['root_seq']
        if r not in threads: print('skip (before archive):', r); continue
        pre, post, newv = measure(r, t0); ab, pb = agebin(t0 - rootts[r]), prebin(pre)
        ctrl = []
        for cr, rt in rootts.items():
            if cr in listed_all or rt > t0 - H48 or agebin(t0 - rt) != ab: continue
            cp, cpo, cn = measure(cr, t0)
            if prebin(cp) == pb: ctrl.append((cpo - cp, cn, cpo))
        rows.append(dict(cat=cseq, week=cats[str(cseq)]['week'], root=r, author=it['author'], topic=it['topic'], age_d=round((t0 - rootts[r]) / 86400, 1), pre=pre, post=post, newv=newv, nctrl=len(ctrl), ctrl_diff=st.mean(d for d, n, p in ctrl) if ctrl else None, ctrl_newv=st.mean(n for d, n, p in ctrl) if ctrl else None, ctrl_post=st.mean(p for d, n, p in ctrl) if ctrl else None, ctrl=ctrl))
print(f'{"week":4} {"root":>6} {"author":24} {"topic":12} {"age_d":>5} {"pre":>3} {"post":>4} {"new":>3} | {"nctrl":>5} {"ctrl_diff":>9} {"ctrl_new":>8}')
for x in rows:
    cd = f"{x['ctrl_diff']:+9.2f}" if x['ctrl_diff'] is not None else '        -'
    cn = f"{x['ctrl_newv']:8.2f}" if x['ctrl_newv'] is not None else '       -'
    print(f"W{x['week']:<3} {x['root']:>6} {x['author']:24} {x['topic']:12} {x['age_d']:5.1f} {x['pre']:3d} {x['post']:4d} {x['newv']:3d} | {x['nctrl']:5d} {cd} {cn}")
ok = [x for x in rows if x['ctrl']]
eff = [x['post'] - x['pre'] - x['ctrl_diff'] for x in ok]; effn = [x['newv'] - x['ctrl_newv'] for x in ok]
print(f'\ntreated threads {len(rows)}, with >=1 matched control {len(ok)}; median controls per thread {st.median(x["nctrl"] for x in ok):.0f}')
print(f'treated: mean pre {st.mean(x["pre"] for x in ok):.2f}, mean post {st.mean(x["post"] for x in ok):.2f}, mean diff {st.mean(x["post"]-x["pre"] for x in ok):+.2f}; matched controls mean diff {st.mean(x["ctrl_diff"] for x in ok):+.2f}')
rng = random.Random(1)
def boot(v):
    ms = sorted(st.mean(rng.choices(v, k=len(v))) for _ in range(2000)); return ms[50], ms[1949]
lo, hi = boot(eff); print(f'EFFECT on replies (treated diff - matched control diff): {st.mean(eff):+.2f} per thread, 95% bootstrap CI [{lo:+.2f}, {hi:+.2f}]')
lo, hi = boot(effn); print(f'EFFECT on new voices in the 48h after: {st.mean(effn):+.2f} per thread, 95% CI [{lo:+.2f}, {hi:+.2f}] (treated {st.mean(x["newv"] for x in ok):.2f} vs controls {st.mean(x["ctrl_newv"] for x in ok):.2f})')
# permutation within cells: draw one control per treated thread at random, compute its 'effect' against the rest
perm = []
for _ in range(2000):
    s = 0
    for x in ok:
        d, n, p = rng.choice(x['ctrl']); s += d - x['ctrl_diff']
    perm.append(s / len(ok))
obs = st.mean(eff); pv = sum(1 for v in perm if v >= obs) / len(perm)
print(f'permutation (one random matched control per cell, 2000 draws): P(control mean >= observed {obs:+.2f}) = {pv:.3f}; perm sd {st.pstdev(perm):.2f}')
dead = [x for x in ok if x['pre'] == 0]
if dead:
    rev = sum(1 for x in dead if x['post'] > 0); crev = st.mean(sum(1 for d, n, p in x['ctrl'] if p > 0) / len(x['ctrl']) for x in dead)
    print(f'revival: {len(dead)} listed threads silent in the 48h before; {rev} got >=1 reply after ({rev/len(dead):.0%}); matched silent controls {crev:.0%}')
json.dump([{k: v for k, v in x.items() if k != 'ctrl'} for x in rows], open('lab/catalogue/effect_rows.json', 'w'), indent=0)
