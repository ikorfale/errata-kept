"""Timer-series candidate flag for Kept (#676): for each agent with >=150 archived posts, the modal gap between posts
(gaps > 20 min, binned at 2% width on a log scale) and the share of all gaps within +-3% of it. A drifting timer
(period not a divisor of 24 h) still shows one period here, unlike a minute-of-hour or hour-of-day cut. A flag, never a verdict."""
import json, sys, collections, math, statistics as st
P = [json.loads(l) for l in open(sys.argv[1])]; prof = json.load(open('profiles.json'))
by = collections.defaultdict(list)
for p in P: by[p['author']].append(p['created_at'])
rows = []
for a in prof:
    ts = sorted(by[a]); g = [(y - x) / 60 for x, y in zip(ts, ts[1:])]
    big = [x for x in g if x > 20]
    if not big: continue
    c = collections.Counter(round(math.log(x) / math.log(1.02)) for x in big)
    k = max(c, key=lambda b: sum(c[b + i] for i in (-1, 0, 1)))
    T = 1.02 ** k; T = st.median([x for x in big if abs(x / T - 1) <= .05]); near = sum(abs(x / T - 1) <= .03 for x in g)
    rows.append((near / len(g), a, T, len(g), (1440 / T) % 1))
rows.sort(reverse=True)
print('agent                     gaps  modal_period_min  share_of_all_gaps_within_3%  periods_per_day_fraction')
for s, a, T, n, fr in rows: print(f'{a[:24]:24} {n:5}  {T:7.1f}  {s:5.2f}  {fr:4.2f}')
print('flag (share >= 0.30):', sum(r[0] >= .30 for r in rows), 'of', len(rows))
