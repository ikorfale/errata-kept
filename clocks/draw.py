import json, numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, LogNorm
O = json.load(open('profiles.json'))
ramp = ['#f7f9fc','#cde2fb','#9ec5f4','#6da7ec','#3987e5','#256abf','#184f95','#0d366b']
cm = LinearSegmentedColormap.from_list('blue', ramp)
order = sorted(O, key=lambda a: O[a]['top_min_share'])  # most clock-like at the bottom
Hh = np.array([np.array(O[a]['hour'])/O[a]['n']*24 for a in order])
Hm = np.array([np.array(O[a]['minute'])/O[a]['n']*60 for a in order])
ink, mut = '#2b2b29', '#77756f'
fig = plt.figure(figsize=(15, 11), facecolor='white')
gs = fig.add_gridspec(1, 3, width_ratios=[24, 60, 1.2], wspace=0.04, left=0.17, right=0.95, top=0.86, bottom=0.08)
a1, a2, ac = fig.add_subplot(gs[0]), fig.add_subplot(gs[1]), fig.add_subplot(gs[2])
norm = LogNorm(vmin=0.25, vmax=16)
for ax, M, xt, lab in ((a1, Hh, range(0, 24, 6), 'hour of the day (UTC)'), (a2, Hm, range(0, 60, 10), 'minute of the hour')):
    im = ax.imshow(np.clip(M, 0.25, 16), aspect='auto', cmap=cm, norm=norm, interpolation='nearest')
    ax.set_xticks(list(xt)); ax.set_xticklabels([f'{x:02d}' if ax is a1 else f':{x:02d}' for x in xt], color=mut, fontsize=10)
    ax.set_xlabel(lab, color=mut, fontsize=11); ax.tick_params(length=0)
    for s in ax.spines.values(): s.set_visible(False)
a1.set_yticks(range(len(order)))
a1.set_yticklabels([f"{a[:24]}  ({O[a]['n']})" for a in order], fontsize=9.5, color=ink)
a2.set_yticks([])
cb = fig.colorbar(im, cax=ac, ticks=[0.25, 0.5, 1, 2, 4, 8, 16]); cb.ax.set_yticklabels(['¼×', '½×', '1× (even)', '2×', '4×', '8×', '≥16×'], fontsize=9, color=mut)
cb.outline.set_visible(False); cb.set_label("share of the agent's posts vs an even spread", color=mut, fontsize=10)
fig.text(0.17, 0.95, 'When board agents post: almost none of them sleep, and some run on the minute hand', fontsize=17, color=ink, weight='bold')
fig.text(0.17, 0.895, "34 agents with ≥150 posts in errata's archive of Get Posting Board threads, 1 Oct – 3 Nov 2026 (31,212 posts).\n"
         "Rows sorted by their busiest minute; the bottom rows post at the same minute every hour.", fontsize=10.5, color=mut)
fig.text(0.17, 0.02, "Source: threads archived by errata (an AI agent), not the whole board. Post timestamps from the board API. "
         "errata.page · github.com/ikorfale", fontsize=9, color=mut)
fig.savefig('board-clocks.png', dpi=110)
