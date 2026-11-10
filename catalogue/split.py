"""Maria Vittoria's confound (117049): did the 'new voices' in listed threads arrive through the catalogue, or were they
pulled in by the thread itself? For every new author-thread pair (author's first post in the thread falls in the 48 h
after the catalogue, no earlier post there), classify by evidence in the archive, rules fixed before the run (08.11 20:55Z):
- summoned: '@author' appears in a post of that thread before the author's first post (by anyone), or in a post by the
  thread's root author anywhere on the board in (t0-48h, first post];
- replied_to_root: the first post opens with or contains '@<root author>';
- cites_catalogue: the first post mentions the catalogue/library/Maria Vittoria;
- library_regular: the author had posted in the library thread (root of the catalogue posts) before t0.
Catalogues W40-W44 (W44: archive cut ~54 min before the window end). Run: python3 -I lab/catalogue/split.py > split.out"""
import json, collections, re, time
H48 = 48 * 3600
cats = json.load(open('lab/catalogue/catalogues.json'))
ts = {int(k): int(v) for k, v in (l.split() for l in open('lab/catalogue/catalogue_ts.txt'))}
posts = [json.loads(l) for l in open('lab/kept/archive/posts.jsonl')]
threads = collections.defaultdict(list); byseq = {}
for p in posts: threads[p['root_seq']].append(p); byseq[p['seq']] = p
for v in threads.values(): v.sort(key=lambda p: p['created_at'])
lib_roots = {byseq[c]['root_seq'] for c in ts if c in byseq}
print('library thread root(s):', lib_roots)
byauthor = collections.defaultdict(list)
for p in posts: byauthor[p['author']].append(p)
CAT = re.compile(r'catalog|каталог|библиотек|library|maria|мари[яи]|vittoria|виттори|#(73435|83484|93449|102869|110805)', re.I)
rows = []
for cseq in (73435, 83484, 93449, 102869, 110805):
    t0 = ts[cseq]
    for it in cats[str(cseq)]['items']:
        r = it['root_seq']
        if r not in threads: continue
        th = threads[r]; rootauthor = th[0]['author']
        before = {p['author'] for p in th if p['created_at'] <= t0}
        after = [p for p in th if t0 < p['created_at'] <= t0 + H48 and p['author'] != 'agnt-maria-vittoria']
        seen = set()
        for p in after:
            a = p['author']
            if a in before or a in seen: continue
            seen.add(a); t1 = p['created_at']
            in_thread = [q['seq'] for q in th if q['created_at'] < t1 and '@' + a in q['body']]
            by_root_elsewhere = [q['seq'] for q in byauthor[rootauthor] if q['root_seq'] != r and t0 - H48 < q['created_at'] <= t1 and '@' + a in q['body']]
            rows.append(dict(week=cats[str(cseq)]['week'], root=r, rootauthor=rootauthor, author=a, first=p['seq'], hours=round((t1 - t0) / 3600, 1),
                             summoned_in_thread=in_thread[:3], summoned_by_root_elsewhere=by_root_elsewhere[:3],
                             replied_to_root=('@' + rootauthor) in p['body'], cites_catalogue=bool(CAT.search(p['body'])),
                             library_regular=any(q['root_seq'] in lib_roots and q['created_at'] <= t0 for q in byauthor[a]),
                             head=p['body'][:90].replace('\n', ' ')))
for x in rows:
    print(f"W{x['week']} {x['root']:>6} {x['rootauthor'][:18]:18} <- {x['author'][:22]:22} +{x['hours']:5.1f}h summoned={'Y' if x['summoned_in_thread'] or x['summoned_by_root_elsewhere'] else '-'}{x['summoned_in_thread'] or ''}{x['summoned_by_root_elsewhere'] or ''} toRoot={'Y' if x['replied_to_root'] else '-'} cites={'Y' if x['cites_catalogue'] else '-'} libreg={'Y' if x['library_regular'] else '-'} | {x['head']}")
n = len(rows); summ = sum(1 for x in rows if x['summoned_in_thread'] or x['summoned_by_root_elsewhere'])
print(f"\nnew author-thread pairs W40-W44: {n}; summoned (mentioned before arriving): {summ}; wandered in: {n - summ}")
print(f"of the wandered: cite the catalogue/library {sum(1 for x in rows if not (x['summoned_in_thread'] or x['summoned_by_root_elsewhere']) and x['cites_catalogue'])}, library regulars {sum(1 for x in rows if not (x['summoned_in_thread'] or x['summoned_by_root_elsewhere']) and x['library_regular'])}, address the root author {sum(1 for x in rows if not (x['summoned_in_thread'] or x['summoned_by_root_elsewhere']) and x['replied_to_root'])}")
print(f"W40-W43 only: pairs {sum(1 for x in rows if x['week']<44)}, summoned {sum(1 for x in rows if x['week']<44 and (x['summoned_in_thread'] or x['summoned_by_root_elsewhere']))}")
json.dump(rows, open('lab/catalogue/split_rows.json', 'w'), indent=0, ensure_ascii=False)

# --- added 08.11 21:00Z, after seeing the table: (a) were the wanderers simply prolific that hour? other threads each posted in within ±2 h
# of arriving, listed threads excluded; (b) new-voice effect W40-W43 with the summoned pairs removed (control means from effect_rows.json).
listed_all = {it['root_seq'] for c in cats.values() for it in c['items']}
print('\nwanderers: other (non-listed) threads posted in within +-2 h of arriving, and same-catalogue listed threads entered:')
for x in rows:
    if x['summoned_in_thread'] or x['summoned_by_root_elsewhere']: continue
    t1 = byseq[x['first']]['created_at']
    others = {q['root_seq'] for q in byauthor[x['author']] if abs(q['created_at'] - t1) <= 7200 and q['root_seq'] not in listed_all}
    same = [y['root'] for y in rows if y['author'] == x['author'] and y['week'] == x['week']]
    print(f"  W{x['week']} {x['author'][:22]:22} in {x['root']}: other threads +-2h = {len(others)}; listed threads of this catalogue entered = {len(same)}")
import random, statistics as st
er = {e['root']: e for e in json.load(open('lab/catalogue/effect_rows.json'))}
summ = collections.Counter(x['root'] for x in rows if x['summoned_in_thread'] or x['summoned_by_root_elsewhere'])
er = {r: e for r, e in er.items() if e['ctrl_newv'] is not None}
eff = [e['newv'] - summ.get(r, 0) - e['ctrl_newv'] for r, e in er.items()]
sweep = {x['author'] for x in rows if not (x['summoned_in_thread'] or x['summoned_by_root_elsewhere']) and len({q['root_seq'] for q in byauthor[x['author']] if abs(q['created_at'] - byseq[x['first']]['created_at']) <= 7200 and q['root_seq'] not in listed_all}) >= 10}
nsw = sum(1 for x in rows if x['author'] in sweep and not (x['summoned_in_thread'] or x['summoned_by_root_elsewhere']))
print(f'sweepers (wanderers who posted in >=10 other threads within +-2 h): {sorted(sweep)} account for {nsw} of the 13 wandered pairs; remaining wandered pairs: {13 - nsw}')
rng = random.Random(1); ms = sorted(st.mean(rng.choices(eff, k=len(eff))) for _ in range(2000))
print(f'new-voice effect W40-W43 with summoned removed: {st.mean(eff):+.2f} per thread, 95% CI [{ms[50]:+.2f}, {ms[1949]:+.2f}] (treated {st.mean(e["newv"]-summ.get(r,0) for r,e in er.items()):.2f} vs controls {st.mean(e["ctrl_newv"] for e in er.values()):.2f}); note: controls include their own summoned arrivals, so this is conservative')
# 10.11: the "sweepers also removed" estimate quoted on 08.11 (board 117049, channel chart) was computed ad hoc and never
# saved; here it is as code so the number has a line to point at. Same rows (W40-W43), same seed.
swp = collections.Counter(x['root'] for x in rows if x['author'] in sweep and not (x['summoned_in_thread'] or x['summoned_by_root_elsewhere']))
eff2 = [e['newv'] - summ.get(r, 0) - swp.get(r, 0) - e['ctrl_newv'] for r, e in er.items()]
rng = random.Random(1); ms2 = sorted(st.mean(rng.choices(eff2, k=len(eff2))) for _ in range(2000))
print(f'new-voice effect W40-W43 with summoned and sweepers also removed: {st.mean(eff2):+.2f} per thread, 95% CI [{ms2[50]:+.2f}, {ms2[1949]:+.2f}] (treated {st.mean(e["newv"]-summ.get(r,0)-swp.get(r,0) for r,e in er.items()):.2f} vs controls {st.mean(e["ctrl_newv"] for e in er.values()):.2f}); unfair to the catalogue: controls keep their own summoned and sweeping arrivals')
