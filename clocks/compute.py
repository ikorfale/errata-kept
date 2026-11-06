"""Agent circadian portraits: when each board agent posts (hour of UTC day, minute of hour).
Input: lab/kept/archive/posts.jsonl (threads archived by errata, up to root seq 112526). Output: profiles.json, summary."""
import json, math, collections, datetime as dt, sys
P = [json.loads(l) for l in open(sys.argv[1])]
by = collections.defaultdict(list)
for p in P: by[p['author']].append(p['created_at'])
def H(c):  # normalised entropy 0..1
    n = sum(c); return -sum(x/n*math.log(x/n) for x in c if x)/math.log(len(c))
out = {}
for a, ts in by.items():
    if len(ts) < 150 or a == 'Anonymous': continue
    h = [0]*24; m = [0]*60; days = set()
    for t in ts:
        d = dt.datetime.fromtimestamp(t, dt.timezone.utc); h[d.hour] += 1; m[d.minute] += 1; days.add(d.date())
    sh = sorted(h); quiet = sum(1 for x in h if x == 0)
    # longest run of empty-or-near-empty hours (<1% of posts), circular: a 'sleep'
    thr = 0.01*len(ts); run = best = 0
    for x in h+h:
        run = run+1 if x < thr else 0; best = max(best, min(run, 24))
    out[a] = {'n': len(ts), 'days': len(days), 'hour': h, 'minute': m, 'H_hour': round(H(h), 3), 'H_min': round(H(m), 3),
              'sleep_h': best, 'top_min_share': round(max(m)/len(ts), 3), 'top_min': m.index(max(m))}
json.dump(out, open('profiles.json', 'w'))
print(f'posts {len(P)} | agents >=150 posts {len(out)} | span', dt.datetime.fromtimestamp(min(p["created_at"] for p in P), dt.timezone.utc).date(), '-', dt.datetime.fromtimestamp(max(p["created_at"] for p in P), dt.timezone.utc).date())
for a, o in sorted(out.items(), key=lambda x: -x[1]['n']):
    print(f"{a[:26]:26} n={o['n']:5} days={o['days']:3} H_hour={o['H_hour']:.3f} sleep={o['sleep_h']:2}h H_min={o['H_min']:.3f} top_min=:{o['top_min']:02} {o['top_min_share']:.3f}")
