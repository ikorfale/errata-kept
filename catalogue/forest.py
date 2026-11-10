"""Forest chart of the catalogue effect on new voices (per listed thread, 48 h after, minus matched controls, 95% CI),
one row per run, parsed from the .out files so the chart cannot disagree with them.
Run from the repo root: python3 catalogue/forest.py [final_w45_out]  (default effect_w45.out, the 41-of-48-hour snapshot)."""
import re, sys, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
D = 'catalogue/'
FINAL = sys.argv[1] if len(sys.argv) > 1 else D + 'effect_w45.out'
ROWS = [('W40–W43, 27 listed threads (8 Nov)', D + 'effect.out', 'EFFECT on new voices'),
        ('W44 added, 32 threads', D + 'effect_w44.out', 'EFFECT on new voices'),
        ('Minus the 4 newcomers summoned by name', D + 'split.out', 'summoned removed'),
        ('Minus summoned and 2 sweeping agents', D + 'split.out', 'sweepers also removed'),
        ('W40–W45, 38 threads' + ('' if 'final' in FINAL else ' (41 of 48 h)'), FINAL, 'EFFECT on new voices'),
        ('W40–W45, finer activity bins', FINAL.replace('.out', '_finebins.out'), 'EFFECT on new voices')]
PAT = re.compile(r'([+-−]?\d\.\d\d) per thread,? (?:95% )?CI \[([+-−]?\d\.\d\d), ([+-−]?\d\.\d\d)\]')
def grab(f, key):
    for l in open(f):
        if key in l:
            m = PAT.search(l.replace('−', '-'))
            if m: return tuple(float(x) for x in m.groups())
    raise SystemExit(f'no "{key}" with a CI in {f}')
vals = [grab(f, k) for _, f, k in ROWS]
INK, MUTED, RED, GRID = '#1f1f1f', '#6b6b6b', '#b2182b', '#d9d9d9'
fig, ax = plt.subplots(figsize=(10, 5.2), dpi=150); y = list(range(len(ROWS)))[::-1]
ax.axvline(0, color=MUTED, lw=1, ls='--', zorder=1)
for yi, (lab, _, _), (p, lo, hi) in zip(y, ROWS, vals):
    ax.plot([lo, hi], [yi, yi], color=RED, lw=2.5, solid_capstyle='round', zorder=2)
    ax.plot([p], [yi], 'o', color=RED, ms=9, mec='white', mew=1.5, zorder=3)
    ax.text(hi + 0.04, yi, f'{p:+.2f}  [{lo:+.2f}, {hi:+.2f}]', va='center', fontsize=10, color=INK)
ax.set_yticks(y); ax.set_yticklabels([r[0] for r in ROWS], fontsize=10.5, color=INK)
ax.set_xlim(-0.25, 1.6); ax.set_xlabel('new voices per listed thread, 48 h after the catalogue, minus matched controls (95% CI)', fontsize=10, color=INK)
for s in ('top', 'right'): ax.spines[s].set_visible(False)
for s in ('left', 'bottom'): ax.spines[s].set_color(GRID)
ax.tick_params(colors=MUTED, labelcolor=INK); ax.grid(axis='x', color=GRID, lw=0.6, zorder=0)
ax.set_title('Does a weekly library catalogue bring new readers to a thread?', loc='left', fontsize=13, color=INK, pad=14)
fig.text(0.01, 0.01, 'errata · catalogue/effect.py, split.py, forest.py · controls: never listed, same age and prior-activity bins; sources: the .out files named in the article', fontsize=7.5, color=MUTED)
fig.tight_layout(rect=(0, 0.04, 1, 1)); out = D + 'library-catalogue-thread-effect.png'; fig.savefig(out); print(out, [f'{p:+.2f} [{lo:+.2f},{hi:+.2f}]' for p, lo, hi in vals])
