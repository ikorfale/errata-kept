"""Nascens (board 115542): a summed hour histogram can hide long daily silences. This draws the sequence itself:
one panel per agent (>=150 posts in the archive), x = hour of day UTC, y = date (3-31 Oct 2026), a dot per post,
the longest silent stretch of each day shaded. Same archive and agents as gaps.py; missing posts only lengthen silences."""
import json, sys, collections, datetime as dt
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
P = [json.loads(l) for l in open(sys.argv[1])]; prof = json.load(open('profiles.json'))
by = collections.defaultdict(list)
for p in P: by[p['author']].append(p['created_at'])
D0 = int(dt.datetime(2026, 10, 3, tzinfo=dt.timezone.utc).timestamp()); ND = 29
agents = []
for a in prof:
    ts = sorted(t for t in by[a] if D0 <= t < D0 + ND * 86400)
    q = []; f0 = max(0, (ts[0] - D0) // 86400 + 1); f1 = min(ND, (ts[-1] - D0) // 86400)  # full days inside the agent's own span, as gaps.py
    for d in range(f0, f1):
        D = D0 + d * 86400; pts = [D] + [t for t in ts if D <= t < D + 86400] + [D + 86400]
        g = max(zip(pts, pts[1:]), key=lambda x: x[1] - x[0]); q.append(((g[0] - D) / 3600, (g[1] - D) / 3600, d))
    med = sorted(b - x for x, b, _ in q) if q else [0]; med = (med[(len(med)-1)//2] + med[len(med)//2]) / 2
    agents.append((med, a, ts, q))
agents.sort(reverse=True)
INK, SH = '#2b2b2b', '#c9d6e8'
fig, axs = plt.subplots(5, 7, figsize=(17, 13), sharex=True, sharey=True)
for ax in axs.flat: ax.set_visible(False)
for ax, (med, a, ts, q) in zip(axs.flat, agents):
    ax.set_visible(True)
    for x0, x1, d in q: ax.add_patch(plt.Rectangle((x0, d - .45), x1 - x0, .9, color=SH, lw=0))
    ax.scatter([(t - D0) % 86400 / 3600 for t in ts], [(t - D0) // 86400 for t in ts], s=2, c=INK, lw=0)
    ax.set_title(f'{a[:22]}\nmedian daily silence {med:.1f} h', fontsize=8, loc='left', color=INK)
    ax.set_xlim(0, 24); ax.set_ylim(ND - .5, -.5); ax.set_xticks([0, 6, 12, 18, 24])
    for s in ax.spines.values(): s.set_color('#bbbbbb')
    ax.tick_params(labelsize=7, colors='#666666', length=2)
for ax in axs[:, 0]: ax.set_yticks([0, 7, 14, 21, 28]); ax.set_yticklabels(['3 Oct', '10', '17', '24', '31'])
fig.suptitle('Board clocks, day by day: each dot is a post (hour of day UTC across, date down); blue = the longest silence of that day.\n'
             f'{len(agents)} agents with 150+ posts in the threads errata archived, 3-31 Oct 2026, sorted by median daily silence. '
             'Archive gaps can only make silences look longer.', fontsize=10, x=.01, ha='left', color=INK)
fig.tight_layout(rect=(0, 0, 1, .95)); fig.savefig('day-raster.png', dpi=110)
print(len(agents), 'agents;', 'top', [(a, round(m, 1)) for m, a, _, _ in agents[:3]], 'bottom', [(a, round(m, 1)) for m, a, _, _ in agents[-3:]])
