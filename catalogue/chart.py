"""Chart for the catalogue-effect result: per listed thread, replies 48h before vs 48h after the catalogue post, treated
(filled) against the mean of its matched controls (hollow, same colour), plus new voices. Reads effect_rows.json."""
import json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
rows = json.load(open('lab/catalogue/effect_rows.json'))
fig, ax = plt.subplots(1, 2, figsize=(11, 5), dpi=150, gridspec_kw={'width_ratios': [3, 2]})
a = ax[0]
for x in rows:
    a.plot([0, 1], [x['pre'] + 1, x['post'] + 1], color='#b2182b', lw=1, alpha=.6)
    a.plot([0, 1], [x['pre'] + 1, max(0, x['pre'] + x['ctrl_diff']) + 1], color='#4d4d4d', lw=1, alpha=.5, ls='--')
a.plot([], [], color='#b2182b', lw=1.5, label='listed thread')
a.plot([], [], color='#4d4d4d', lw=1.5, ls='--', label='mean of its matched controls')
a.set_yscale('log'); a.set_xticks([0, 1]); a.set_xticklabels(['48 h before\nthe catalogue', '48 h after'])
a.set_ylabel('replies in the window (+1, log scale)'); a.set_xlim(-.2, 1.2); a.legend(frameon=False, loc='lower center', bbox_to_anchor=(0.5, -0.28), ncol=2)
a.set_title('Replies: 27 threads listed in the weekly library catalogue, W40-W43', fontsize=10, loc='left')
b = ax[1]
tr = sum(x['newv'] for x in rows) / len(rows); ct = sum(x['ctrl_newv'] for x in rows) / len(rows)
b.bar([0, 1], [tr, ct], color=['#b2182b', '#9e9e9e'], width=.6)
b.set_xticks([0, 1]); b.set_xticklabels(['listed threads', 'matched controls']); b.set_ylabel('new authors per thread, 48 h after')
for i, v in enumerate([tr, ct]): b.text(i, v + .02, f'{v:.2f}', ha='center', fontsize=10)
b.set_title('New voices: authors new to the thread', fontsize=10, loc='left')
for s in ('top', 'right'): a.spines[s].set_visible(False); b.spines[s].set_visible(False)
fig.text(0.01, 0.01, 'errata, 08.11.2026 · lab/catalogue/effect.py on the full board archive 01.10-03.11 · controls: never listed, same age and pre-window bins', fontsize=7, color='#666')
plt.tight_layout(rect=(0, 0.04, 1, 1)); plt.savefig('media/catalogue-effect.png'); print('saved media/catalogue-effect.png')
