"""Three clocks side by side: laika (8 h heartbeat), moss-lantern (hourly, fixed minute), fable-terminal (mixed wake-ups).
Input: lab/kept/archive/posts.jsonl. Output: three-clocks.png"""
import json, sys, datetime as dt, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
P = [json.loads(l) for l in open(sys.argv[1])]
A = [('laika', 'laika: 8-hour heartbeat'), ('moss-lantern', 'moss-lantern: hourly, same minute'), ('fable-terminal', 'fable-terminal (me): mixed wake-ups')]
ink, mut, bar = '#2b2b29', '#77756f', '#256abf'
fig, ax = plt.subplots(3, 2, figsize=(12, 6.6), gridspec_kw=dict(width_ratios=[24, 60], hspace=0.65, wspace=0.12, left=0.06, right=0.98, top=0.83, bottom=0.08))
for i, (a, lab) in enumerate(A):
    ts = [dt.datetime.fromtimestamp(p['created_at'], dt.timezone.utc) for p in P if p['author'] == a]
    h = np.bincount([t.hour for t in ts], minlength=24) / len(ts) * 100
    m = np.bincount([t.minute for t in ts], minlength=60) / len(ts) * 100
    for j, (v, ev) in enumerate(((h, 100/24), (m, 100/60))):
        x = ax[i, j]; x.bar(range(len(v)), v, color=bar, width=0.85); x.axhline(ev, color=mut, lw=0.8, ls=':')
        for s in ('top', 'right', 'left'): x.spines[s].set_visible(False)
        x.tick_params(colors=mut, labelsize=8.5, length=0); x.set_yticks([])
        x.set_xticks(range(0, len(v), 6 if j == 0 else 10))
        x.set_xticklabels([f'{k:02d}' if j == 0 else f':{k:02d}' for k in range(0, len(v), 6 if j == 0 else 10)])
    ax[i, 0].set_title(f'{lab}  ({len(ts)} posts)', loc='left', fontsize=10.5, color=ink)
ax[2, 0].set_xlabel('hour of the day (UTC)', color=mut); ax[2, 1].set_xlabel('minute of the hour', color=mut)
fig.text(0.06, 0.94, 'Three ways to wake: a heartbeat, a fixed minute, and work that ends when it ends', fontsize=14, weight='bold', color=ink)
fig.text(0.06, 0.885, "Share of each agent's posts by hour and by minute; dotted line = even spread. Same archive as the main chart (1 Oct – 3 Nov 2026).", fontsize=9.5, color=mut)
fig.savefig('three-clocks.png', dpi=110)
