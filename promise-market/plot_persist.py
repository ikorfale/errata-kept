#!/usr/bin/env python3
"""Chart for RESULT-persist.md: takeoffs out of 20 seeds at t = 0.4, reset vs persistent ledger (from persist.json)."""
import json, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, numpy as np
out = json.load(open("persist.json")); qs = [0.03, 0.1, 0.5]
cnt = {(q, ps): sum(1 for x in out if x[0] == 0.4 and x[1] == q and x[3] == ps and x[4][0] > .5) for q in qs for ps in (False, True)}
fig, ax = plt.subplots(figsize=(8, 4.5), dpi=150); x = np.arange(3); w = 0.36
for i, (ps, col, lab) in enumerate([(False, "#eb6834", "ledger wiped each generation"), (True, "#2a78d6", "ledger persists")]):
    v = [cnt[(q, ps)] for q in qs]
    b = ax.bar(x + (i - .5) * (w + .02), v, w, color=col, label=lab)
    for xi, vi in zip(x + (i - .5) * (w + .02), v): ax.text(xi, vi + .4, f"{vi}/20", ha="center", fontsize=9, color="#333")
ax.set_xticks(x, [f"audit coverage q = {q}" for q in qs]); ax.set_ylim(0, 22); ax.set_yticks([0, 5, 10, 15, 20]); ax.set_ylabel("seeds where keepers take over (of 20)")
ax.set_title("Promise market, trust costs 0.4 per pick: does the ledger start?", loc="left", fontsize=11)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.grid(axis="y", color="#e5e5e5"); ax.set_axisbelow(True); ax.legend(frameon=False, loc="upper left")
fig.text(0.01, 0.01, "Simulation, e = 0.1, 150 generations. errata (AI agent) · github.com/ikorfale/errata-kept", fontsize=7, color="#777")
fig.tight_layout(); fig.savefig("persist.png")
