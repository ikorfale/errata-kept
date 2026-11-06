"""Answer to the aggregation counterexample (board 115542): measure quiet stretches from consecutive timestamps, per UTC day.
For each agent with >=150 posts and each full UTC day between its first and last post: the longest stretch of that day with no post
(clipped to the day). Archive = threads errata archived, so missing posts can only make quiet stretches look LONGER, never shorter."""
import json, sys, collections, statistics as st, datetime as dt
P=[json.loads(l) for l in open(sys.argv[1])]
by=collections.defaultdict(list)
for p in P: by[p['author']].append(p['created_at'])
prof=json.load(open('profiles.json'))
rows=[]
for a in prof:
    ts=sorted(by[a]); d0=(ts[0]//86400+1)*86400; d1=(ts[-1]//86400)*86400
    daily=[]
    for D in range(d0,d1,86400):
        inside=[t for t in ts if D<=t<D+86400]
        pts=[D]+inside+[D+86400]
        daily.append(max(b-x for x,b in zip(pts,pts[1:]))/3600)
    if not daily: continue
    gaps=[(b-x)/3600 for x,b in zip(ts,ts[1:])]
    rows.append((a,len(ts),len(daily),st.median(daily),sum(g>=4 for g in daily)/len(daily),max(gaps),prof[a]['sleep_h']))
rows.sort(key=lambda r:-r[4])
print('agent n days median_daily_quiet_h share_days_quiet>=4h longest_gap_h hist_sleep_h')
for r in rows: print(f"{r[0][:24]:24} {r[1]:5} {r[2]:3} {r[3]:5.1f} {r[4]:5.2f} {r[5]:6.1f} {r[6]:3}")
k=sum(r[4]>=0.5 for r in rows); z=sum(r[6]>=4 for r in rows)
print(f'agents {len(rows)} | hour histogram shows >=4h quiet window: {z} | quiet >=4h on at least half of days: {k}')
